"""Le catalogue des sons — et le fait que le jeu sonne meme sans les fichiers."""

import re
import shutil
import subprocess

import pytest

from app import audio

RACINE_JS = audio.RACINE_STATIQUE / "js"


@pytest.mark.parametrize("echantillon", audio.CATALOGUE, ids=lambda e: e["slug"])
def test_un_echantillon_est_generable(echantillon):
    """Les bornes sont celles d'ElevenLabs : hors d'elles, l'appel serait refuse."""
    assert echantillon["slug"] and re.fullmatch(r"[a-z_]+", echantillon["slug"])
    assert echantillon["nom"]
    assert echantillon["categorie"] in audio.CATEGORIES
    assert 0.5 <= echantillon["duree_s"] <= 30.0
    assert 0 < echantillon["volume"] <= 1.0
    assert 1 <= echantillon["variantes"] <= 4
    assert len(echantillon["prompt"]) >= 20, "une recette trop courte donne n'importe quoi"
    assert "no music" in echantillon["prompt"] or echantillon["categorie"] != "sfx", \
        "un bruitage avec de la musique dessous est inutilisable"


def test_les_slugs_sont_uniques():
    assert len(audio.SLUGS) == len(set(audio.SLUGS))


def test_le_catalogue_ne_declare_que_des_fichiers_presents():
    for echantillon in audio.exporter()["echantillons"]:
        for nom in echantillon["fichiers"]:
            chemin = audio.RACINE_STATIQUE / audio.DOSSIER / nom
            assert chemin.is_file(), nom
            assert chemin.stat().st_size > 500, f"{nom} est vide ou tronque"


def test_aucun_fichier_orphelin():
    assert audio.orphelins() == [], "des .mp3 que le catalogue ne reclame plus"


def test_le_poids_audio_reste_raisonnable():
    """Un telephone en 3G telecharge les BRUITAGES au demarrage : on se tient
    loin du megaoctet. Les radios, elles, n'arrivent qu'au tour de cle."""
    dossier = audio.RACINE_STATIQUE / audio.DOSSIER
    fichiers = list(dossier.glob("*.mp3")) if dossier.is_dir() else []
    bruitages = [f for f in fichiers if not f.name.startswith(("radio-", "histoire-"))]
    radios = [f for f in fichiers if f.name.startswith("radio-")]
    histoire = [f for f in fichiers if f.name.startswith("histoire-")]
    # ⚠️ Budget releve de 600 a 650 Ko le 13 sept. 2026 : les trois cris de
    # l'homme-sandwich (22 Ko) l'ont fait deborder de 6 Ko. On reste a un
    # tiers du megaoctet ; la prochaine fois, on compresse avant de relever.
    # Puis de 650 a 800 Ko le meme jour : seize bruitages d'armes (un par arme,
    # la gachette a vide, la casse, le degainage) — un son qu'on n'avait pas,
    # pas un son qu'on a laisse grossir. Puis a 850 : les six repliques de la
    # fille de la Brume (52 Ko). On reste sous le mega.
    assert sum(f.stat().st_size for f in bruitages) < 850_000
    for fichier in bruitages:
        assert fichier.stat().st_size < 80_000, fichier.name
    for fichier in radios:
        assert 100_000 < fichier.stat().st_size < 700_000, fichier.name
    # 5 stations de 45 s + l'ambiance de 60 s a 64 kbit/s : 2,3 Mo dans le
    # depot, mais une seule piste a la fois sur le fil, au tour de cle.
    assert sum(f.stat().st_size for f in radios) < 2_500_000
    # Les voix de l'histoire se chargent par mission : une replique reste legere.
    for fichier in histoire:
        assert fichier.stat().st_size < 150_000, fichier.name
    assert sum(f.stat().st_size for f in histoire) < 3_000_000


@pytest.mark.parametrize("radio", audio.RADIOS, ids=lambda r: r["slug"])
def test_une_station_est_generable(radio):
    assert radio["nom"] and radio["style"]
    assert "instrumental" in radio["prompt"] or "no vocals" in radio["prompt"], \
        "une voix chantee sous une sirene, c'est illisible"
    assert 20 <= radio["duree_s"] <= 90
    assert 0 < radio["volume"] <= 1


def test_chaque_char_de_phase_1_a_une_station_qui_existe():
    """Enregistree ou procedurale — mais elle existe.

    ⚠️ Depuis M9, le camion et la remorqueuse ont une station ECRITE PAR UNE
    GRAINE (`musique.STATIONS`) plutot qu'un mp3 : c'est pour ca que le juge
    passe par `station_existe` et non par `radio_par_slug`. Un bouton RADIO
    qui ne trouve pas sa station reste un bouton qui ne fait rien.
    """
    from app import vehicules

    for vehicule in vehicules.de_phase(1):
        if vehicule["radio"]:
            assert audio.station_existe(vehicule["radio"]), vehicule["slug"]
    assert any(v["radio"] for v in vehicules.de_phase(1)), "aucun char n'a de radio"
    assert not audio.station_existe("une_station_qui_n_existe_pas")


def test_l_autobus_n_a_que_son_moteur():
    """Le plan de M9 le dit : « le camion a sa toune, l'autobus n'a que son
    moteur ». Un autobus de ville avec la radio dans la cabine, ca n'existe
    pas, et ca enleverait au camion ce qui le distingue."""
    from app import vehicules

    assert vehicules.par_slug("autobus")["radio"] is None
    assert vehicules.par_slug("camion")["radio"] == "station_camion"


def test_les_radios_ne_sont_pas_chargees_au_demarrage(paquet):
    """Les radios sont dans `radios`, jamais dans `echantillons` : sinon
    `chargerEchantillons()` telechargerait un mega de jazz avant la premiere
    image."""
    slugs = {e["slug"] for e in paquet["audio"]["echantillons"]}
    for radio in paquet["audio"]["radios"]:
        assert radio["slug"] not in slugs
        assert "fichier" in radio


def test_le_navigateur_ne_reclame_que_des_slugs_du_catalogue():
    """`Son.joue('x')` dans le JS doit correspondre a un son declare en Python."""
    source = (RACINE_JS / "son.js").read_text(encoding="utf-8")
    demandes = set(re.findall(r"joue\('([a-z_]+)'\)", source))
    assert demandes, "plus personne ne joue d'echantillon ?"
    assert demandes <= set(audio.SLUGS), demandes - set(audio.SLUGS)


def test_chaque_effet_garde_son_repli_synthetise():
    """⚠️ Le filet : un `joue(...)` sans `else` synthetise laisse un silence."""
    source = (RACINE_JS / "son.js").read_text(encoding="utf-8")
    bloc = source[source.index("const SFX = {"):source.index("// --- La musique")]
    for ligne in bloc.splitlines():
        if "joue(" not in ligne:
            continue
        assert re.search(r"if \(!joue\('[a-z_]+'\)\)\s*\S", ligne), ligne.strip()


def test_les_fichiers_sont_servis(client, paquet):
    audios = paquet["audio"]
    assert audios["echantillons"], "le paquet ne dit rien de l'audio"
    servis = 0
    for echantillon in audios["echantillons"]:
        for nom in echantillon["fichiers"]:
            reponse = client.get(f"/static/{audios['dossier']}/{nom}")
            assert reponse.status_code == 200, nom
            servis += 1
    assert servis >= len(audio.CATALOGUE), "des sons du catalogue ne sont pas servis"


def test_l_ambiance_et_les_voix_sont_declarees_a_part(paquet):
    """L'ambiance n'est pas une radio (elle joue a pied) et les voix ne sont
    pas des bruitages (elles ont un texte et une voix nommee)."""
    audios = paquet["audio"]
    assert len(audios["ambiances"]) >= 1
    for ambiance in audios["ambiances"]:
        assert ambiance["slug"] not in {r["slug"] for r in audios["radios"]}
        assert 0 < ambiance["volume"] <= 0.5, "la musique de fond doit rester sous la rumeur"
    assert len(audios["voix"]) >= 6
    genres = {v["genre"] for v in audios["voix"]}
    assert {"homme", "femme"} <= genres, "il faut des hommes ET des femmes qui parlent"
    assert "crieur" in genres, "l'homme-sandwich n'a rien a crier"
    for voix in audio.VOIX:
        assert 2 <= len(voix["texte"]) <= 40, "une replique de passant tient en quelques mots"
        assert voix["voix"] and not voix["voix"].startswith("__"), \
            f"{voix['slug']} : la voix ElevenLabs n'est pas nommee"


def test_le_choc_est_du_techno_maintenant():
    """Martin trouvait le punk trop hardcore pour la moto."""
    choc = audio.radio_par_slug("le_choc")
    assert choc["style"] == "techno" and "techno" in choc["prompt"]
    assert "punk" not in choc["prompt"]


def test_la_rumeur_et_les_passages_existent():
    for slug in ("foule", "passage_auto", "passage_moto", "sonnette"):
        assert audio.par_slug(slug), slug
    assert audio.par_slug("foule")["boucle"] is True, "la rumeur doit boucler"
    assert audio.par_slug("passage_auto")["variantes"] >= 2


def test_les_voix_de_l_histoire_sont_declarees_par_mission(paquet):
    """Chaque replique de l'histoire est servie avec son personnage et sa
    mission, pour que le navigateur ne charge que celles de la mission en
    cours — jamais au demarrage."""
    histoire = paquet["audio"]["histoire"]
    assert len(histoire) >= 30
    assert {v["mission"] for v in histoire} == {"m1", "m2", "m3", "m4", "m5", "journal"}, \
        "les cinq missions, et le journal lu par le narrateur"
    assert all(v["qui"] and v["partie"] for v in histoire)
    assert any(v["telephone"] for v in histoire), "les appels sont marques : la voix vient du combine"
    assert all(v["fichier"] is None or v["fichier"].startswith("histoire-") for v in histoire)
    slugs = {v["slug"] for v in histoire} | {v["slug"] for v in paquet["audio"]["voix"]}
    assert len(slugs) == len(histoire) + len(paquet["audio"]["voix"]), "un slug de voix par replique"


# --- La finition : on juge les FICHIERS, pas l'intention -----------------------------
#
# ⚠️ Ces juges-la sont d'une autre nature que ceux du dessus. Les premiers
# verifient le CATALOGUE (une recette bien formee, un slug unique) ; ceux-ci
# ouvrent les octets et mesurent. C'est la seule facon d'attraper ce qui nous
# etait passe sous le nez pendant deux jours : des fichiers sans aigu, des
# pics qui vont de -34 dB a 0, un son large qu'aucun panoramique ne rattrape.
# Aucun ne remplace l'oreille de Martin — ils disent seulement que la chaine
# a bien tourne, pas que le son est le bon.


def _ffprobe(chemin, entrees):
    fait = subprocess.run(["ffprobe", "-v", "error", "-show_entries", entrees,
                           "-of", "default=nw=1:nk=1", str(chemin)],
                          capture_output=True, text=True)
    return fait.stdout.split()


def _pic_dbfs(chemin):
    """⚠️ `volumedetect` ecrit au niveau `info`, sur la sortie d'ERREUR : avec
    un `-v error` de trop on mesure un silence et tous les juges passent."""
    fait = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(chemin),
                           "-af", "volumedetect", "-f", "null", "-"],
                          capture_output=True, text=True)
    trouve = re.search(r"max_volume: (-?[\d.]+) dB", fait.stderr)
    assert trouve, f"pas de pic mesurable dans {chemin.name}"
    return float(trouve.group(1))


ffmpeg_present = pytest.mark.skipif(
    shutil.which("ffprobe") is None or shutil.which("ffmpeg") is None,
    reason="ffmpeg n'est pas installe : ces juges mesurent des octets")

#: Les fichiers de bruitage reellement presents, avec leur echantillon.
BRUITAGES = [(e, i) for e in audio.CATALOGUE for i in range(1, e["variantes"] + 1)
             if audio.chemin(e, i).is_file()]


@ffmpeg_present
@pytest.mark.parametrize("echantillon,indice", BRUITAGES,
                         ids=lambda x: x if isinstance(x, int) else x["slug"])
def test_un_bruitage_est_mono_et_en_44_khz(echantillon, indice):
    """⚠️ Mono n'est pas une economie, c'est une CORRECTION : `son.js` place
    ses sons avec un `StereoPanner`, et un fichier deja large arrive a gauche
    quoi qu'on lui demande. Deux des premiers fichiers etaient dans ce cas."""
    frequence, canaux = _ffprobe(audio.chemin(echantillon, indice),
                                 "stream=sample_rate,channels")
    assert int(canaux) == 1, "un son large ne se laisse pas placer"
    assert int(frequence) == 44100, "en 22 kHz il n'y a plus rien au-dessus de 11 kHz"


@ffmpeg_present
@pytest.mark.parametrize("echantillon,indice", BRUITAGES,
                         ids=lambda x: x if isinstance(x, int) else x["slug"])
def test_un_bruitage_part_du_meme_niveau(echantillon, indice):
    """Tous au meme pic, pour que `volume` veuille dire quelque chose.

    ⚠️ La marge est celle de l'ENCODEUR, pas du reglage : `ffmpeg` normalise
    au sample pres, puis le mp3 rend un pic qui bouge — mesure sur les 32
    fichiers, il s'ecarte de -1,0 dBFS jusqu'a 1,0 dB dans les deux sens. La
    marge tient a 1,2 : l'ecart total est passe de **34,4 dB a 1,8 dB**, et
    c'est ca que le juge protege.
    """
    pic = _pic_dbfs(audio.chemin(echantillon, indice))
    assert abs(pic - audio.PIC_VISE_DBFS) <= 1.2, \
        f"{pic:+.1f} dBFS au lieu de {audio.PIC_VISE_DBFS:+.1f} : le melange ne tient plus"


@ffmpeg_present
@pytest.mark.parametrize("echantillon,indice",
                         [(e, i) for e, i in BRUITAGES if not e["boucle"]],
                         ids=lambda x: x if isinstance(x, int) else x["slug"])
def test_un_bruitage_bref_ne_finit_pas_par_du_vide(echantillon, indice):
    """On ne paie pas pour du silence. ⚠️ Les boucles sont exclues : c'est
    exactement leur couture qu'un rognage abimerait."""
    chemin = audio.chemin(echantillon, indice)
    fait = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(chemin), "-af",
                           f"silencedetect=n={audio.SEUIL_QUEUE_DBFS}dB:d=0.2",
                           "-f", "null", "-"], capture_output=True, text=True)
    duree = float(_ffprobe(chemin, "format=duration")[0])
    debuts = [float(m) for m in re.findall(r"silence_start: (-?[\d.]+)", fait.stderr)]
    fins = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", fait.stderr)]
    if debuts and len(debuts) > len(fins):      # un silence ouvert jusqu'au bout
        assert duree - debuts[-1] < 0.25, \
            f"{duree - debuts[-1]:.2f} s de rien a la fin de {chemin.name}"


@ffmpeg_present
def test_les_bruitages_ont_de_l_aigu():
    """Le defaut d'origine, en un juge : en 22 kHz / 32 kbit/s, il ne restait
    presque rien au-dessus de 8 kHz.

    On compare le pic du signal filtre a 8 kHz au pic du fichier entier.
    Mesure sur les cinq sons qui DOIVENT briller — anciens fichiers puis
    nouveaux : caisse -26 → -10, ramassage -23 → -7, tole -27 → -6, porte
    -32 → -10, clic -30 → -7 (la porte d'alors ; depuis qu'il y en a trois,
    c'est la porte du commerce qu'on juge — elle DOIT briller). Le seuil
    de -14 dB tombe entre les deux, avec
    au moins 4 dB de marge de chaque cote : il aurait refuse les anciens
    fichiers, il accepte ceux-ci.

    ⚠️ On ne juge QUE ces cinq-la. Un klaxon, une sirene, un moteur sont des
    sons graves : ils n'ont pas d'aigu a avoir, et leur en demander ferait
    tomber le juge sur des fichiers parfaits. ⚠️ La sonnette de velo est
    dehors elle aussi, pour la raison inverse : c'est le seul son que le
    22 kHz n'avait pas trop abime (-16 dB), donc il ne separe rien.
    """
    for slug in ("argent", "ramasse", "choc", "porte_commerce", "menu"):
        echantillon = audio.par_slug(slug)
        chemin = audio.chemin(echantillon, 1)
        if not chemin.is_file():
            pytest.skip(f"{slug} n'est pas genere")
        entier = _pic_dbfs(chemin)
        fait = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(chemin), "-af",
                               "highpass=f=8000:poles=2,volumedetect", "-f", "null", "-"],
                              capture_output=True, text=True)
        aigu = float(re.search(r"max_volume: (-?[\d.]+) dB", fait.stderr).group(1))
        assert aigu - entier > -14, \
            f"{slug} : rien au-dessus de 8 kHz ({aigu - entier:.0f} dB sous le pic)"


@ffmpeg_present
@pytest.mark.parametrize("echantillon,indice",
                         [(e, i) for e, i in BRUITAGES if not e["boucle"]],
                         ids=lambda x: x if isinstance(x, int) else x["slug"])
def test_un_bruitage_bref_ne_souffle_pas(echantillon, indice):
    """Normaliser remonte le son ET son plancher. Si la generation etait
    bruyante, on l'entend maintenant.

    ⚠️ Le juge mesure le fichier FINI, jamais le gain qu'il a fallu — c'est
    l'erreur que le script faisait : `pas-2` demandait +29 dB et sortait avec
    le meilleur plancher des quatre variantes. Un son bas et propre est un
    bon son.

    ⚠️ On ne voit le souffle que quand le son S'ARRETE. Les boucles sont donc
    exclues (sur une sirene, le « plancher » mesure le son continu lui-meme :
    13 dB), et parmi les sons brefs, ceux qui remplissent toute leur duree
    aussi — mesure : le buzzer de refus et l'auto qui passe donnent 1 dB de
    RSB alors que leurs fichiers sont impeccables. Sans un moment de calme,
    pas de verdict.
    """
    chemin = audio.chemin(echantillon, indice)
    calme = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(chemin), "-af",
                            "silencedetect=n=-40dB:d=0.05", "-f", "null", "-"],
                           capture_output=True, text=True)
    if "silence_start" not in calme.stderr:
        pytest.skip("son continu : son plancher, c'est son son")
    fait = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(chemin), "-af",
                           "astats=measure_overall=Noise_floor+Peak_level:"
                           "measure_perchannel=0", "-f", "null", "-"],
                          capture_output=True, text=True)
    plancher = re.search(r"Noise floor dB: (-?[\d.]+)", fait.stderr)
    pic = re.search(r"Peak level dB: (-?[\d.]+)", fait.stderr)
    if not plancher or not pic:
        pytest.skip("plancher non mesurable sur ce fichier")
    rsb = float(pic.group(1)) - float(plancher.group(1))
    assert rsb >= audio.RSB_PLANCHER_DB, \
        f"{chemin.name} : {rsb:.0f} dB de rapport signal/bruit, ca souffle"


def test_la_reserve_ne_compte_pas_comme_un_orphelin():
    """Une generation ratee mais bonne se garde — sans etre chargee.

    ⚠️ Ce juge tient un INVARIANT, pas un comportement : `orphelins()` liste
    le dossier avec `iterdir()`, qui ne descend pas dans les sous-dossiers.
    C'est la seule chose qui laisse vivre `static/audio/reserve/`. Le jour ou
    quelqu'un passera a `rglob()` pour de bonnes raisons, ce juge tombera au
    lieu de laisser `test_aucun_fichier_orphelin` reclamer la suppression de
    toute la reserve.
    """
    reserve = audio.RACINE_STATIQUE / audio.DOSSIER / "reserve"
    if not reserve.is_dir():
        pytest.skip("pas de reserve pour l'instant")
    gardes = {f.name for f in reserve.glob("*.mp3")}
    assert gardes, "une reserve vide se supprime"
    assert not (gardes & set(audio.orphelins())), \
        "la reserve est reclamee comme orpheline : orphelins() descend-il dans les sous-dossiers ?"
    # ⚠️ Et le jeu ne la telecharge pas : rien dans ce qu'on exporte ne la nomme.
    declares = {nom for e in audio.exporter()["echantillons"] for nom in e["fichiers"]}
    assert not (gardes & declares)


def test_chaque_arme_a_son_effet_dans_le_navigateur():
    """`Son.SFX.arme(def)` joue `SFX[def.son]` : il faut donc une entree — avec
    son repli synthetise, juge plus haut — pour chaque `son` de `armes.py`, et
    les trois d'autour (a vide, casse, degainer) que `combat.js` appelle."""
    from app import armes

    source = (RACINE_JS / "son.js").read_text(encoding="utf-8")
    bloc = source[source.index("const SFX = {"):source.index("// --- Les voix")]
    effets = set(re.findall(r"^\s+([a-z_]+): function", bloc, re.M))
    for a in armes.CATALOGUE:
        assert a["son"] in effets, f"{a['slug']} : pas d'effet SFX.{a['son']} dans son.js"
    assert {"vide", "casse", "degainer", "arme", "jet"} <= effets


def test_la_fille_de_la_brume_a_plusieurs_repliques():
    """Martin (13 sept. 2026) : « la prostituée aussi doit parler, avec plusieurs
    dialogues différents ». Un genre a elle — une passante qu'on frole ne dit
    pas ca — et une voix qui n'est celle de personne d'autre."""
    brume = [v for v in audio.VOIX if v["genre"] == "brume"]
    assert len(brume) >= 5, "il lui faut plusieurs dialogues differents"
    assert len({v["texte"] for v in brume}) == len(brume), "deux repliques pareilles"
    assert all(v["voix"] == audio.VOIX_BRUME for v in brume)
    autres = {audio.VOIX_PAR_GENRE["homme"], audio.VOIX_PAR_GENRE["femme"], audio.VOIX_CRIEUR}
    assert audio.VOIX_BRUME not in autres, "sa voix doit se distinguer des passantes et du crieur"
