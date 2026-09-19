#!/usr/bin/env python3
"""Genere les sons manquants de `app/audio.py` — par le serveur MCP elevenlabs.

⚠️ Ce script N'APPELLE PAS l'API ElevenLabs lui-meme. Il parle au serveur MCP
`elevenlabs` exactement comme Claude Code le fait (JSON-RPC sur stdio) : une
seule integration a maintenir, une seule cle a poser, et le meme chemin que
celui qu'on utilise a la main depuis l'agent.

    uv run python scripts/audio_elevenlabs.py --essai     # ce qui serait genere
    uv run python scripts/audio_elevenlabs.py             # genere ce qui manque
    uv run python scripts/audio_elevenlabs.py --musiques   # les 15 musiques du jeu
    uv run python scripts/audio_elevenlabs.py --refaire coup pas
    uv run python scripts/audio_elevenlabs.py --refaire pas-2   # cette variante-la

⚠️ CHAQUE GENERATION COUTE DES CREDITS. Le script ne touche jamais a un
fichier deja present (sauf `--refaire`), et ne tourne jamais en CI.

La cle vit dans ~/.mcp-servers/elevenlabs/cle.txt (chmod 600) ou dans
ELEVENLABS_API_KEY. Le chemin du lanceur se change par BANDINI_MCP_ELEVENLABS.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from app import audio, interpretation  # noqa: E402

LANCEUR = Path(os.environ.get(
    "BANDINI_MCP_ELEVENLABS",
    Path.home() / ".mcp-servers" / "elevenlabs" / "run.sh",
)).expanduser()

#: Le format des voix des passants, des radios et des pubs, FINI (comme
#: `audio.FORMAT_HISTOIRE`) : une voix se genere en master, `finir_voix()` l'y ramene.
#: ⚠️ C'etait 22 kHz / 32 kbit/s, « une replique de deux mots n'a pas d'aigu a
#: perdre » — et Martin les a trouvees ETOUFFEES. Mesure : tout ce qui depasse
#: 8 kHz y etait coupe, alors que les masters v3 montent a 14. En 44 kHz /
#: 48 kbit/s, les passants pesent 1,5 fois plus (+200 Ko : bruitages et passants
#: a 1,41 Mo sur les 1,5 du budget de demarrage).
FORMAT = "mp3_44100_48"

#: ⚠️ Les BRUITAGES, eux, ne sont plus generes a leur taille finale. On
#: demande le meilleur master (`audio.FORMAT_MASTER`) et `finir()` le ramene
#: a la taille du jeu — voir la longue note de `app/audio.py` : en generant
#: directement en 22 kHz / 32 kbit/s on jetait tout l'aigu AVANT de pouvoir
#: le regarder, et on gardait en echange un tiers de silence.


class ClientMCP:
    """Un client MCP minuscule : poignee de main, puis des appels d'outils.

    ⚠️ stdin reste OUVERT tant qu'on n'a pas fini : un serveur MCP s'arrete sur
    l'EOF, et les dernieres reponses se perdraient.
    """

    def __init__(self, lanceur: Path) -> None:
        self.proc = subprocess.Popen(
            ["/bin/sh", str(lanceur)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        self.lignes: queue.Queue[str | None] = queue.Queue()
        threading.Thread(target=self._lire, daemon=True).start()
        self.identifiant = 0
        self._envoyer({"jsonrpc": "2.0", "id": self._suivant(), "method": "initialize",
                       "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                  "clientInfo": {"name": "bandini", "version": "1"}}})
        self._attendre(self.identifiant)
        self._envoyer({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _lire(self) -> None:
        for ligne in self.proc.stdout:
            self.lignes.put(ligne)
        self.lignes.put(None)

    def _suivant(self) -> int:
        self.identifiant += 1
        return self.identifiant

    def _envoyer(self, message: dict) -> None:
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def _attendre(self, identifiant: int, delai: float = 300.0) -> dict:
        while True:
            ligne = self.lignes.get(timeout=delai)
            if ligne is None:
                raise RuntimeError("le serveur MCP s'est arrete :\n" + self.proc.stderr.read()[-2000:])
            ligne = ligne.strip()
            if not ligne.startswith("{"):
                continue
            charge = json.loads(ligne)
            if charge.get("id") == identifiant:
                if "error" in charge:
                    raise RuntimeError(charge["error"].get("message", charge["error"]))
                return charge["result"]

    def appeler(self, outil: str, arguments: dict) -> dict:
        identifiant = self._suivant()
        self._envoyer({"jsonrpc": "2.0", "id": identifiant, "method": "tools/call",
                       "params": {"name": outil, "arguments": {"params": arguments}}})
        resultat = self._attendre(identifiant)
        texte = resultat["content"][0]["text"]
        # ⚠️ Un outil MCP qui REFUSE ne repond pas en JSON : il rend sa plainte
        # en clair, avec `isError`. Sans ce detour, le script mourait sur un
        # `JSONDecodeError` nu — et comme `--refaire` efface la cible AVANT
        # d'appeler, on se retrouvait sans le vieux son ni le neuf, sans savoir
        # pourquoi. (Vecu : `duration_seconds` a 0,4 s, le minimum est 0,5.)
        if resultat.get("isError"):
            return {"ok": False, "erreur": texte.strip()}
        try:
            return json.loads(texte)
        except json.JSONDecodeError:
            return {"ok": False, "erreur": texte.strip()[:400]}

    def fermer(self) -> None:
        self.proc.stdin.close()
        self.proc.terminate()
        self.proc.wait(timeout=10)


# --- La finition : du master ElevenLabs au fichier du jeu ---------------------------


def _sortie_ffmpeg(arguments: list[str]) -> str:
    """Lance ffmpeg et rend ce qu'il a dit. ⚠️ `volumedetect` ecrit sur la
    sortie d'ERREUR et au niveau `info` : un `-v error` de trop, et on mesure
    le silence."""
    fait = subprocess.run(["ffmpeg", "-hide_banner", "-y", *arguments],
                          capture_output=True, text=True)
    if fait.returncode != 0:
        raise RuntimeError("ffmpeg : " + fait.stderr.strip()[-400:])
    return fait.stderr


def _pic_dbfs(chemin: Path) -> float:
    sortie = _sortie_ffmpeg(["-i", str(chemin), "-af", "volumedetect", "-f", "null", "-"])
    trouve = re.search(r"max_volume: (-?[\d.]+) dB", sortie)
    if not trouve:
        raise RuntimeError(f"pas de pic mesurable dans {chemin.name}")
    return float(trouve.group(1))


def _a_du_calme(chemin: Path) -> bool:
    """Ce fichier contient-il un moment ou le son s'arrete ?

    ⚠️ C'est la condition pour pouvoir mesurer un plancher de bruit. Un
    buzzer de refus ou une auto qui passe remplissent TOUTE leur duree : leur
    « plancher », c'est leur son (mesure : 1 dB de RSB pour `erreur`, un
    fichier pourtant impeccable). Sans calme, pas de mesure — et surtout pas
    de verdict.
    """
    sortie = _sortie_ffmpeg(["-i", str(chemin), "-af",
                             "silencedetect=n=-40dB:d=0.05", "-f", "null", "-"])
    return "silence_start" in sortie


def _rsb_db(chemin: Path) -> float:
    """Le pic moins le plancher de bruit — ce qui reste de son une fois le
    souffle enleve. Rend l'infini quand la question ne se pose pas."""
    if not _a_du_calme(chemin):
        return float("inf")
    sortie = _sortie_ffmpeg(["-i", str(chemin), "-af",
                             "astats=measure_overall=Noise_floor+Peak_level:"
                             "measure_perchannel=0", "-f", "null", "-"])
    plancher = re.search(r"Noise floor dB: (-?[\d.]+)", sortie)
    pic = re.search(r"Peak level dB: (-?[\d.]+)", sortie)
    if not plancher or not pic:
        return float("inf")     # pas mesurable : on ne crie pas au loup
    return float(pic.group(1)) - float(plancher.group(1))


def _duree_s(chemin: Path) -> float:
    """⚠️ ffprobe rend `N/A` — pas une erreur, pas un zero — sur un fichier
    dont il ne sait rien dire (un wav vide, par exemple, ce qui arrive quand
    le rognage a tout mange). On le lit comme une duree nulle."""
    fait = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "csv=p=0", str(chemin)], capture_output=True, text=True)
    dit = fait.stdout.strip()
    try:
        return float(dit)
    except ValueError:
        return 0.0


def finir(master: Path, cible: Path, boucle: bool) -> dict:
    """Mono, normalise, rogne, encode. Rend ce qui a change, pour le dire.

    Quatre gestes, et l'ORDRE est la seule chose difficile ici :

    1. **mono** — le jeu place ses sons lui-meme (`StereoPanner`) ; un
       fichier deja large arrive a gauche quoi qu'on fasse. Et on ne peut
       juger un niveau qu'une fois les deux canaux melanges ;
    2. **normaliser au pic** (`PIC_VISE_DBFS`) — tous les fichiers partent
       alors du meme niveau, et c'est ce qui rend le `volume` du catalogue
       credible ;
    3. **rogner la queue** — SEULEMENT MAINTENANT. ⚠️ Rogner avant de
       normaliser, c'est ce que j'ai fait d'abord, et c'est faux : le seuil
       est un niveau ABSOLU (-45 dBFS), donc sur une generation sortie a
       -34 dB il tombe 11 dB sous le pic, c'est-a-dire en plein milieu du
       son. Mesure : un pas s'est fait rogner a 0,06 s, puis remonter de
       +37 dB — il ne restait que le souffle. Normalise d'abord, le seuil
       est toujours a 44 dB sous le pic, quelle que soit la generation ;
    4. **fondre et encoder** — 15 ms de fondu, sinon couper une decroissance
       fait un clic.

    ⚠️ Une BOUCLE saute 3 et le fondu de 4 : la couture est exactement ce que
    le rognage abime, et un fondu ferait un trou a chaque tour.
    """
    avant = master.stat().st_size
    with tempfile.TemporaryDirectory(prefix="bandini-finition-") as temporaire:
        dossier = Path(temporaire)

        mono = dossier / "mono.wav"
        _sortie_ffmpeg(["-i", str(master), "-af", "pan=mono|c0=0.5*c0+0.5*c1",
                        "-ar", "44100", "-ac", "1", str(mono)])
        gain = audio.PIC_VISE_DBFS - _pic_dbfs(mono)

        plein = dossier / "plein.wav"
        _sortie_ffmpeg(["-i", str(mono), "-af", f"volume={gain:.2f}dB", str(plein)])

        rogne = plein
        if not boucle:
            rogne = dossier / "rogne.wav"
            coupe = ("silenceremove=start_periods=1:start_threshold="
                     f"{audio.SEUIL_QUEUE_DBFS}dB:detection=peak:start_silence=")
            _sortie_ffmpeg(["-i", str(plein), "-af",
                            f"{coupe}0.005,areverse,{coupe}{audio.QUEUE_GARDEE_S},areverse",
                            str(rogne)])

        duree = _duree_s(rogne)
        if duree < audio.DUREE_PLANCHER_S:
            raise RuntimeError(f"il ne reste que {duree:.3f} s apres rognage — "
                               "master muet ou presque")

        filtres = [] if boucle else [
            f"afade=t=out:st={max(0.0, duree - audio.FONDU_S):.3f}:d={audio.FONDU_S}"]
        cible.parent.mkdir(parents=True, exist_ok=True)
        _sortie_ffmpeg(["-i", str(rogne), *(["-af", ",".join(filtres)] if filtres else []),
                        "-ar", "44100", "-ac", "1",
                        "-b:a", audio.DEBIT_BOUCLE if boucle else audio.DEBIT_BREF,
                        "-map_metadata", "-1", str(cible)])

    # ⚠️ On juge le fichier FINI, pas le gain qu'il a fallu. Un son sorti bas
    # mais propre est un bon son ; un son sorti bas ET bruyant, on vient d'en
    # remonter le souffle, et ca se REFAIT (`--refaire pas-2`) — ca ne se
    # repare pas. Une boucle est exemptee : son plancher, c'est son son.
    rsb = float("inf") if boucle else _rsb_db(cible)
    return {"avant": avant, "apres": cible.stat().st_size, "duree": duree, "gain": gain,
            "rsb": rsb, "souffle": rsb < audio.RSB_PLANCHER_DB}


def _niveau_lufs(chemin: Path) -> float | None:
    """Le niveau integre. ⚠️ `None` sous 400 ms de son : la mesure travaille par
    blocs de 400 ms et rend -70 (« rien ») sur un « Salut! » trop bref."""
    trouves = re.findall(r"I:\s+(-?[\d.]+) LUFS", _sortie_ffmpeg(
        ["-i", str(chemin), "-af", "ebur128", "-f", "null", "-"]))
    if not trouves or float(trouves[-1]) <= -69.0:
        return None
    return float(trouves[-1])       # le dernier : le resume, pas un bloc


def _trous_s(chemin: Path, seuil_s: float = 1.2) -> list[float]:
    """Les silences de plus de `seuil_s` AU MILIEU de la replique — le temps
    mort de la fin n'en est pas un. C'est le piege mesure de v3 (voir
    `app/interpretation.py`) : « … » + `[sighs]` y a fait un trou de 2 s."""
    duree = _duree_s(chemin)
    # ⚠️ -35 dB, pas -40 : dans le trou de 2 s de l'essai, un soupir a -42 dB
    # coupait le silence en deux morceaux d'une seconde, et a -40 on ne voyait
    # rien. A -35, le soupir compte pour du silence — c'est ce qu'il est, a
    # l'oreille, entre deux phrases.
    sortie = _sortie_ffmpeg(["-i", str(chemin), "-af",
                             f"silencedetect=n=-35dB:d={seuil_s}", "-f", "null", "-"])
    fins = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", sortie)
    return [float(d) for fin, d in fins if float(fin) < duree - 0.05]


def secher(client: ClientMCP, master: Path, dossier: Path) -> Path:
    """La voix seule du master, sans la piece (ElevenLabs Voice Isolator) :
    `<master>-sec.wav`, dans `dossier`. Voir `interpretation.VOIX_A_SECHER`.

    ⚠️ Sous `ISOLATION_MIN_S`, l'isolateur refuse : on envoie la replique
    allongee de silence, et on recoupe le retour a sa duree d'origine — il
    garde le minutage (mesure : 7,44 s envoyees, 7,43 rendues).
    """
    duree = _duree_s(master)
    cible = dossier / f"{master.stem}-sec.wav"
    with tempfile.TemporaryDirectory(prefix="bandini-sec-") as temporaire:
        envoi = master
        if duree < interpretation.ISOLATION_MIN_S + 0.1:
            envoi = Path(temporaire) / f"{master.stem}.wav"
            _sortie_ffmpeg(["-i", str(master), "-ac", "1", "-ar", "44100", "-af",
                            f"apad=whole_dur={interpretation.ISOLATION_MIN_S + 0.2}", str(envoi)])
        reponse = client.appeler("elevenlabs_voice_isolation",
                                 {"fichier": str(envoi), "output_dir": temporaire, "nom": "isolee"})
        if not reponse.get("ok"):
            raise RuntimeError(f"isolation : {reponse.get('erreur')}")
        _sortie_ffmpeg(["-i", reponse["fichier"], "-af", f"atrim=end={duree:.3f}",
                        "-ac", "1", "-ar", "44100", str(cible)])
    return cible


def finir_voix(master: Path, cible: Path, histoire: bool, marque: str | None = None,
               filtre: str | None = None) -> dict:
    """Mono, au niveau, un fondu sur la derniere syllabe, le temps mort, encode.

    ⚠️ L'ancien fichier n'est remplace qu'a la toute fin : une finition qui
    echoue laisse la replique qu'on avait, jamais un trou dans le jeu.
    `marque` va dans l'etiquette `comment` (`interpretation.MARQUE_SECHEE`) ;
    `filtre` est l'egalisation de la voix (`interpretation.egalisation`), posee
    AVANT de mesurer le niveau : on regle le volume de ce qu'on entendra.
    """
    frequence, debit = (audio.FORMAT_HISTOIRE if histoire else FORMAT).split("_")[1:]
    with tempfile.TemporaryDirectory(prefix="bandini-voix-") as temporaire:
        dossier = Path(temporaire)
        mono = dossier / "mono.wav"
        _sortie_ffmpeg(["-i", str(master), "-ac", "1", "-ar", "44100",
                        *(["-af", filtre] if filtre else []), str(mono)])
        duree = _duree_s(mono)
        if duree < audio.DUREE_PLANCHER_S:
            raise RuntimeError(f"{duree:.3f} s de voix — master muet")
        niveau = _niveau_lufs(mono)
        pic = _pic_dbfs(mono)
        gain = interpretation.LIMITE_DBFS + interpretation.LIMITEUR_MAX_DB - pic
        if niveau is not None:
            gain = min(gain, interpretation.NIVEAU_LUFS - niveau)
        # ⚠️ Rogner APRES le gain : le seuil est un niveau absolu, choisi sur des
        # fichiers deja normalises (voir `interpretation.SEUIL_SILENCE_DB`).
        # Et `stop_duration` a 0,02 : dans ffmpeg 8 c'est le DECLENCHEUR, et
        # `stop_silence` ce qu'on garde — mesure sur un signal synthetique, une
        # pause de 0,4 s reste entiere et une de 2 s tombe a 0,7. Avec
        # `stop_duration` a 0,75, la pause de 2 s gardait 1,5 s.
        seuil = f"{interpretation.SEUIL_SILENCE_DB}dB"
        bord = (f"silenceremove=start_periods=1:start_threshold={seuil}:"
                f"start_silence={interpretation.BORD_S}:detection=rms:window=0.02")
        rogne = dossier / "rogne.wav"
        _sortie_ffmpeg(["-i", str(mono), "-af",
                        f"volume={gain:.2f}dB,"
                        f"alimiter=limit={10 ** (interpretation.LIMITE_DBFS / 20):.4f}:attack=2:"
                        "release=50:level=0:latency=1,"
                        f"{bord},areverse,{bord},areverse,"
                        f"silenceremove=stop_periods=-1:stop_duration=0.02:stop_threshold={seuil}:"
                        f"stop_silence={interpretation.PAUSE_MAX_S}:detection=rms:window=0.02",
                        str(rogne)])
        duree = _duree_s(rogne)
        if duree < audio.DUREE_PLANCHER_S:
            raise RuntimeError(f"il ne reste que {duree:.3f} s apres rognage")
        fini = dossier / "fini.mp3"
        fondu = interpretation.FONDU_FIN_S
        # ⚠️ L'ENCODEUR DEPASSE LE PIC qu'on lui donne — mesure sur les 83 : de
        # -0,8 a +2,3 dB (`ti_guy-m1-2` vise a -1,9 dBFS est sorti a +0,4). On
        # remesure donc le fichier encode, et on le refait une fois, plus bas
        # de ce qu'il a depasse. Le rognage, lui, ne bouge pas : il est deja fait.
        # ⚠️ ET LE PIC DU MP3 NE SUIT PAS LE GAIN : sur `bouchard-m4-2`, -1 dB de
        # gain sort a -4,5 dBFS et -2 dB a -3,1 — l'encodeur tremble de 3 dB.
        # Corriger du depassement exact oscillait (« depasse encore apres trois
        # encodages ») : on descend du depassement, puis par quarts de dB.
        correction = 0.0
        for essai in range(12):
            _sortie_ffmpeg(["-i", str(rogne), "-af",
                            f"volume={correction:.2f}dB,"
                            f"afade=t=out:st={max(0.0, duree - fondu):.3f}:d={fondu},"
                            f"apad=pad_dur={interpretation.TEMPS_MORT_S}",
                            "-ar", frequence, "-ac", "1", "-b:a", f"{debit}k",
                            "-map_metadata", "-1",
                            *(["-metadata", f"comment={marque}"] if marque else []), str(fini)])
            depasse = _pic_dbfs(fini) - interpretation.PIC_MAX_DBFS
            if depasse <= 0.1:
                break
            correction -= depasse if essai == 0 else 0.25
        else:
            raise RuntimeError(f"le pic depasse encore de {depasse:.1f} dB apres douze encodages")
        gain += correction
        trous = _trous_s(fini)
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(fini), str(cible))
    return {"duree": _duree_s(cible), "gain": gain, "niveau": niveau, "trous": trous}


def _demande(nom: str) -> tuple[str, int | None]:
    """« pas » -> tout le son ; « pas-2 » -> cette variante-la, seule.

    ⚠️ ElevenLabs ne rend pas deux fois la meme qualite : sur quatre pas, il
    en sort regulierement un beaucoup plus faible que les autres, qu'il faut
    remonter de 25 dB avec son souffle. Refaire les quatre pour en corriger
    un, c'est payer trois generations pour rien — et en abimer peut-etre une
    bonne au passage. D'ou l'indice. Aucun slug ne porte de chiffre
    (`test_un_echantillon_est_generable` l'exige), donc `nom-2` ne peut pas
    etre autre chose qu'une variante.
    """
    tete, _, queue = nom.rpartition("-")
    if tete and queue.isdigit():
        return tete, int(queue)
    return nom, None


def a_faire(refaire: list[str]) -> list[tuple[dict, int]]:
    if not refaire:
        return audio.manquants()
    connus = (set(audio.SLUGS)
              | {r["slug"] for r in audio.RADIOS + audio.AMBIANCES}
              | {m["slug"] for m in audio.MUSIQUES}
              | {v["slug"] for v in audio.toutes_les_voix()})
    demandes = [_demande(nom) for nom in refaire]
    # ⚠️ Le NOM entier d'abord : une replique d'histoire finit par un chiffre
    # (`ti_guy-m1-1`), et `_demande` la prend pour la variante 1 de `ti_guy-m1`
    # — qui n'existe pas. `--refaire ti_guy-m1-1` repondait « slug inconnu ».
    inconnus = [nom for nom, (slug, _) in zip(refaire, demandes)
                if nom not in connus and slug not in connus]
    if inconnus:
        raise SystemExit(f"slugs inconnus : {inconnus} (voir app/audio.py)")
    hors_bornes = [f"{slug}-{indice}" for slug, indice in demandes
                   if indice is not None and audio.par_slug(slug)
                   and not 1 <= indice <= audio.par_slug(slug)["variantes"]]
    if hors_bornes:
        raise SystemExit(f"variantes qui n'existent pas : {hors_bornes}")
    voulus = {(slug, indice) for slug, indice in demandes}
    return [(e, i) for e in audio.CATALOGUE
            for i in range(1, e["variantes"] + 1)
            if (e["slug"], i) in voulus or (e["slug"], None) in voulus]


def radios_a_faire(refaire: list[str]) -> list[dict]:
    if not refaire:
        return audio.radios_manquantes()
    return [r for r in audio.RADIOS + audio.AMBIANCES if r["slug"] in refaire]


def musiques_a_faire(refaire: list[str]) -> list[dict]:
    """Les pieces de `musique.py` a faire jouer par l'IA.

    ⚠️ Rien n'est jamais refait sans `--refaire <slug>` : une piece est deja
    payee, et une seconde generation ne donne PAS la meme — on perdrait celle
    que Martin a ecoutee et acceptee."""
    if not refaire:
        return audio.musiques_manquantes()
    return [m for m in audio.MUSIQUES if m["slug"] in refaire]


def refinir(voix: list[dict], masters: Path) -> int:
    """Rejoue `finir_voix()` sur des masters deja payes. ⚠️ C'est ce qui permet
    de regler un seuil, une pause ou un niveau et de le mesurer sur les 83
    repliques sans une seule generation — la premiere fois, on a regenere
    toute la serie pour changer trois nombres."""
    if not masters.is_dir():
        raise SystemExit("--refinir veut --masters DOSSIER (les masters d'une generation)")
    rates = 0
    for ligne in voix:
        nom = audio.nom_fichier_voix(ligne)
        # ⚠️ Une voix a secher se refinit depuis son master SECHE : repartir du
        # brut remettrait la piece autour d'elle sans que rien ne le dise.
        seche = interpretation.a_secher(ligne)
        master = masters / (f"{nom[:-4]}-sec.wav" if seche else nom)
        if not master.is_file():
            rates += 1
            print(f"  ✗ {nom:>40}  pas de {master.name} dans {masters}"
                  + (" (lance --secher)" if seche else ""))
            continue
        try:
            bilan = finir_voix(master, audio.chemin_voix(ligne), bool(ligne.get("histoire")),
                               interpretation.MARQUE_SECHEE if seche else None,
                               interpretation.egalisation(ligne))
        except (RuntimeError, OSError) as souci:
            rates += 1
            print(f"  ✗ {nom:>40}  {souci}")
            continue
        trous = f"  ⚠ trou de {max(bilan['trous']):.1f} s" if bilan["trous"] else ""
        print(f"  ✓ {nom:>40}  {bilan['duree']:5.2f} s  gain {bilan['gain']:+5.1f} dB{trous}")
    return 1 if rates else 0


def secher_masters(voix: list[dict], masters: Path) -> int:
    """Seche les masters deja payes des voix qui sonnent dans une piece, puis les
    finit. Ne regenere AUCUNE replique : le jeu que Martin a ecoute reste le meme.
    COUTE 1000 credits par minute envoyee a l'isolateur."""
    if not masters.is_dir():
        raise SystemExit("--secher veut --masters DOSSIER (les masters d'une generation)")
    if not LANCEUR.is_file():
        raise SystemExit(f"lanceur MCP introuvable : {LANCEUR}")
    client = ClientMCP(LANCEUR)
    rates = 0
    try:
        for ligne in voix:
            nom = audio.nom_fichier_voix(ligne)
            if not interpretation.a_secher(ligne):
                continue
            try:
                sec = secher(client, masters / nom, masters)
                bilan = finir_voix(sec, audio.chemin_voix(ligne), bool(ligne.get("histoire")),
                                   interpretation.MARQUE_SECHEE, interpretation.egalisation(ligne))
            except (RuntimeError, OSError) as souci:
                rates += 1
                print(f"  ✗ {nom:>40}  {souci}")
                continue
            print(f"  ✓ {nom:>40}  {bilan['duree']:5.2f} s  gain {bilan['gain']:+5.1f} dB  (sechee)")
    finally:
        client.fermer()
    return 1 if rates else 0


def main() -> int:
    argus = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argus.add_argument("--essai", action="store_true", help="dire quoi generer, sans rien depenser")
    argus.add_argument("--refaire", nargs="*", default=[], metavar="SLUG",
                       help="regenerer ces sons meme s'ils existent ; « pas » refait "
                            "les quatre variantes, « pas-2 » refait celle-la seule")
    argus.add_argument("--radios", action="store_true",
                       help="generer aussi les stations de radio (musique : CHER)")
    argus.add_argument("--musiques", action="store_true",
                       help="generer aussi les 15 musiques du jeu (menu, districts, "
                            "poursuite, bagarre, musicien de rue — musique : CHER)")
    argus.add_argument("--voix", action="store_true",
                       help="generer aussi les repliques des passants et de l'histoire (voix : au caractere)")
    argus.add_argument("--masters", metavar="DOSSIER",
                       help="garder les masters des voix dans ce dossier (hors du depot) : "
                            "la finition se rejoue alors sans repayer une generation")
    argus.add_argument("--secher", action="store_true",
                       help="avec --masters : passer les voix qui sonnent dans une piece par "
                            "l'isolateur ElevenLabs, puis les finir (1000 credits / minute)")
    argus.add_argument("--refinir", action="store_true",
                       help="avec --masters : rejouer la finition des voix depuis leurs masters, "
                            "sans rien generer (gratuit)")
    options = argus.parse_args()

    if os.environ.get("CI"):
        print("⚠️  Jamais en CI : la generation coute des credits.", file=sys.stderr)
        return 2

    travail = a_faire(options.refaire)
    radios = radios_a_faire(options.refaire) if (options.radios or options.refaire) else []
    radios = [r for r in radios if options.radios or r["slug"] in options.refaire]
    musiques = musiques_a_faire(options.refaire) if (options.musiques or options.refaire) else []
    musiques = [m for m in musiques if options.musiques or m["slug"] in options.refaire]
    # ⚠️ Trois cas SEPARES, jamais combinés. `--refaire <slug>` retire UNE voix
    # (et `--voix --refaire <slug>` doit faire pareil : le slug filtre, pas
    # `--voix`). L'ancien filtre court-circuitait sur `--voix` et gardait TOUTES
    # les voix : « refaire une » régénérait les 80 d'un coup, à crédits perdus.
    # Désormais le slug prime, et `--voix` ne sert qu'aux manquantes.
    if options.refaire:
        voix = [v for v in audio.toutes_les_voix() if v["slug"] in options.refaire]
    elif options.voix:
        voix = audio.voix_manquantes()
    else:
        voix = []
    if not travail and not radios and not musiques and not voix:
        print("Rien a generer : les", sum(e["variantes"] for e in audio.CATALOGUE),
              "fichiers sont la.")
        orphelins = audio.orphelins()
        if orphelins:
            print("Fichiers que le catalogue ne reclame plus :", ", ".join(orphelins))
        return 0

    if options.secher:
        return secher_masters(voix, Path(options.masters or ""))
    if options.refinir:
        return refinir(voix, Path(options.masters or ""))
    print(f"{len(travail) + len(radios) + len(musiques) + len(voix)} fichier(s) a generer "
          f"dans static/{audio.DOSSIER}/ :")
    for echantillon, indice in travail:
        print(f"  {audio.nom_fichier(echantillon, indice):>22}  "
              f"{echantillon['duree_s']:>4} s  {'boucle  ' if echantillon['boucle'] else '        '}"
              f"{echantillon['prompt'][:60]}…")
    for radio in radios:
        print(f"  {audio.nom_fichier_radio(radio):>22}  {radio['duree_s']:>4} s  MUSIQUE  "
              f"{radio['style']} — {radio['prompt'][:48]}…")
    for piece in musiques:
        print(f"  {audio.nom_fichier_musique(piece['slug']):>28}  {piece['duree_s']:>4} s  MUSIQUE  "
              f"{piece['prompt'][:52]}…")
    for ligne in voix:
        print(f"  {audio.nom_fichier_voix(ligne):>28}  {len(interpretation.dit(ligne)):>4} c  VOIX     "
              f"{ligne['voix'][:22]} — « {interpretation.dit(ligne)[:60]} »")
    if options.essai:
        print("\n(--essai : rien n'a ete genere)")
        return 0
    if not LANCEUR.is_file():
        raise SystemExit(f"lanceur MCP introuvable : {LANCEUR}")

    dossier = str(audio.RACINE_STATIQUE / audio.DOSSIER)
    client = ClientMCP(LANCEUR)
    faits, rates, faibles, a_ecouter = 0, [], [], []
    try:
        etat = client.appeler("elevenlabs_status", {})
        print("\nElevenLabs :", etat.get("cle", "?"), "·", etat.get("quota", etat.get("caracteres_restants", "?")))
        # ⚠️ Les masters ne vont PAS dans static/ : ils y resteraient. Ils
        # vivent le temps de la generation, et c'est `finir()` qui ecrit le
        # fichier du jeu.
        with tempfile.TemporaryDirectory(prefix="bandini-masters-") as masters:
            for echantillon, indice in travail:
                nom = audio.nom_fichier(echantillon, indice)
                cible = audio.chemin(echantillon, indice)
                if cible.exists():
                    cible.unlink()      # --refaire : le serveur n'ecrase jamais
                reponse = client.appeler("elevenlabs_sound_effect", {
                    "prompt": echantillon["prompt"],
                    "duration_seconds": echantillon["duree_s"],
                    "prompt_influence": echantillon["influence"],
                    "loop": echantillon["boucle"],
                    "output_format": audio.FORMAT_MASTER,
                    "output_dir": masters,
                    # ⚠️ Le serveur n'ecrase jamais : deux variantes du meme
                    # slug se marcheraient dessus sans l'indice dans le nom.
                    "nom": nom[:-4],
                })
                if not reponse.get("ok"):
                    rates.append((nom, reponse.get("erreur")))
                    print(f"  ✗ {nom:>16}  {reponse.get('erreur')}")
                    continue
                try:
                    bilan = finir(Path(reponse["fichier"]), cible, echantillon["boucle"])
                except (RuntimeError, OSError) as souci:
                    rates.append((nom, f"finition : {souci}"))
                    print(f"  ✗ {nom:>16}  finition : {souci}")
                    continue
                faits += 1
                rsb = "" if bilan["rsb"] == float("inf") else f"  RSB {bilan['rsb']:>4.0f} dB"
                print(f"  ✓ {nom:>18}  {bilan['apres']:>6} o  {bilan['duree']:>5.2f} s  "
                      f"gain {bilan['gain']:+5.1f} dB{rsb}"
                      f"{'  ⚠ ca souffle' if bilan['souffle'] else ''}")
                if bilan["souffle"]:
                    faibles.append(nom)
        # ⚠️ Une voix passe par un master, comme un bruitage : le niveau et le
        # temps mort de la fin se posent APRES la generation (voir
        # `app/interpretation.py`). Et on ne l'efface plus avant : c'est
        # `finir_voix()` qui la remplace, une fois la nouvelle prete.
        with (contextlib.nullcontext(options.masters) if options.masters
              else tempfile.TemporaryDirectory(prefix="bandini-masters-voix-")) as masters:
            for ligne in voix:
                nom = audio.nom_fichier_voix(ligne)
                cible = audio.chemin_voix(ligne)
                avant = _duree_s(cible) if cible.exists() else None
                reponse = client.appeler("elevenlabs_text_to_speech", {
                    "text": interpretation.dit(ligne),
                    "voice": ligne["voix"],
                    "model_id": interpretation.MODELE,
                    "language_code": "fr",
                    "stability": interpretation.STABILITE,
                    "output_format": audio.FORMAT_MASTER,
                    "output_dir": masters,
                    "nom": nom[:-4],
                })
                if not reponse.get("ok"):
                    rates.append((nom, reponse.get("erreur")))
                    print(f"  ✗ {nom:>40}  {reponse.get('erreur')}")
                    continue
                try:
                    # ⚠️ Secher AVANT de finir : le niveau et les pauses se
                    # mesurent sur la voix seule, pas sur la voix et sa piece.
                    master, marque = Path(reponse["fichier"]), None
                    if interpretation.a_secher(ligne):
                        master = secher(client, master, Path(masters))
                        marque = interpretation.MARQUE_SECHEE
                    bilan = finir_voix(master, cible, bool(ligne.get("histoire")), marque,
                                       interpretation.egalisation(ligne))
                except (RuntimeError, OSError) as souci:
                    rates.append((nom, f"finition : {souci}"))
                    print(f"  ✗ {nom:>40}  finition : {souci}")
                    continue
                faits += 1
                duree = "" if avant is None else f"{avant:5.2f} s -> "
                trous = f"  ⚠ trou de {max(bilan['trous']):.1f} s" if bilan["trous"] else ""
                print(f"  ✓ {nom:>40}  {duree}{bilan['duree']:5.2f} s  gain {bilan['gain']:+5.1f} dB{trous}")
                if bilan["trous"]:
                    a_ecouter.append(nom)
        # ⚠️ Les musiques du jeu passent par le MEME outil que les radios
        # (ElevenLabs Music) et par le meme format : une piece de district est
        # une boucle de fond, exactement comme une station. Et comme une
        # boucle, elle ne se rogne ni ne se fond — voir la note de `finir()` :
        # la couture est precisement ce qu'un rognage abime.
        for piece in musiques:
            nom = audio.nom_fichier_musique(piece["slug"])
            cible = audio.chemin_musique(piece["slug"])
            if cible.exists():
                cible.unlink()          # --refaire : le serveur n'ecrase jamais
            reponse = client.appeler("elevenlabs_music", {
                "prompt": piece["prompt"],
                "music_length_ms": piece["duree_s"] * 1000,
                "force_instrumental": True,
                "output_format": audio.FORMAT_RADIO,
                "output_dir": dossier,
                "nom": nom[:-4],
            })
            if reponse.get("ok"):
                faits += 1
                print(f"  ✓ {nom:>28}  {reponse['octets']:>7} octets")
            else:
                rates.append((nom, reponse.get("erreur")))
                print(f"  ✗ {nom:>28}  {reponse.get('erreur')}")
        for radio in radios:
            nom = audio.nom_fichier_radio(radio)
            cible = audio.chemin_radio(radio)
            if cible.exists():
                cible.unlink()
            reponse = client.appeler("elevenlabs_music", {
                "prompt": radio["prompt"],
                "music_length_ms": radio["duree_s"] * 1000,
                "force_instrumental": True,
                "output_format": audio.FORMAT_RADIO,
                "output_dir": dossier,
                "nom": nom[:-4],
            })
            if reponse.get("ok"):
                faits += 1
                print(f"  ✓ {nom:>22}  {reponse['octets']:>7} octets")
            else:
                rates.append((nom, reponse.get("erreur")))
                print(f"  ✗ {nom:>22}  {reponse.get('erreur')}")
    finally:
        client.fermer()

    print(f"\n{faits} son(s) generes, {len(rates)} en echec.")
    if faibles:
        print("⚠️  Du souffle sous le son (RSB sous "
              f"{audio.RSB_PLANCHER_DB:.0f} dB) — a refaire : {' '.join(faibles)}")
    if a_ecouter:
        print("⚠️  Un silence de plus d'une seconde au milieu de la replique — une "
              f"pause trop lourde, ou v3 qui a derape. A ecouter d'abord : {' '.join(a_ecouter)}")
    for nom, erreur in rates:
        print(f"  {nom} : {erreur}")
    if faits:
        print("\n⚠️  ECOUTE-LES avant de committer : personne d'autre ne peut juger un son.")
    return 1 if rates else 0


if __name__ == "__main__":
    sys.exit(main())
