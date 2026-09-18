"""Les voix qui jouent, et qui finissent leurs phrases (16 sept. 2026).

Demande de Martin : « regénère toutes les voix en mettant des pauses dans le
texte et de l'émotion, et un léger temps mort à la fin pour éviter les fins
coupées ». Trois choses a tenir, et trois endroits ou elles se perdent :

- le JEU (`app/interpretation.py`) doit dire les memes mots que la boite ;
- le FICHIER doit finir sur un temps mort, au niveau des autres ;
- le JEU VIDEO ne doit pas passer a la ligne suivante pendant qu'on parle.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app import audio, interpretation

VOIX = audio.toutes_les_voix()
RACINE = Path(__file__).resolve().parent.parent


def test_chaque_voix_a_son_jeu_et_chaque_jeu_sa_voix():
    """⚠️ Une replique ajoutee sans son jeu sortirait PLATE a la prochaine
    generation, a cote de 83 qui respirent — et personne ne le verrait avant de
    l'entendre. Et un jeu dont le slug a disparu ne sert plus personne."""
    slugs = {v["slug"] for v in VOIX}
    sans_jeu = sorted(slugs - set(interpretation.JEU))
    assert not sans_jeu, f"ecris leur interpretation dans app/interpretation.py : {sans_jeu}"
    orphelins = sorted(set(interpretation.JEU) - slugs)
    assert not orphelins, f"ces jeux ne sont plus la voix de personne : {orphelins}"


@pytest.mark.parametrize("voix", VOIX, ids=lambda v: v["slug"])
def test_le_jeu_dit_exactement_les_mots_de_la_boite(voix):
    """⚠️ Le slug d'une replique d'histoire suit sa PLACE (`ti_guy-m1-3`) : une
    ligne inseree dans une mission decale toutes celles d'en dessous, et leur jeu
    se met a dire la phrase de la voisine. C'est ce juge-ci qui rougit."""
    dit = interpretation.dit(voix)
    assert interpretation.mots(dit) == interpretation.mots(voix["texte"]), (
        f"{voix['slug']} : la voix dirait « {dit} » sous « {voix['texte']} »")


def test_chaque_jeu_porte_une_emotion_de_ton():
    """⚠️ « Toujours de l'émotion ». Un soupir, un rire ou un cri (`CORPS`)
    disent comment le corps parle, pas ce qu'on ressent ; une replique qui ne
    porte qu'eux sort plate a cote des autres. Chaque jeu doit donc porter au
    moins une balise de TON, en plus de ses balises de corps."""
    sans_ton = []
    for slug, dit in interpretation.JEU.items():
        b = set(interpretation.balises(dit))
        if not (b & interpretation.TONS):
            sans_ton.append((slug, b))
    assert not sans_ton, f"ces jeux n'expriment aucun ton ({sans_ton})"


@pytest.mark.parametrize("voix", VOIX, ids=lambda v: v["slug"])
def test_les_balises_sont_celles_que_v3_comprend(voix):
    """Une balise inconnue se LIT a voix haute. Et `<break time>` est du v2 :
    v3 le prononce aussi, ou l'ignore — dans les deux cas, pas de pause."""
    dit = interpretation.dit(voix)
    inconnues = [b for b in interpretation.balises(dit) if b not in interpretation.BALISES]
    assert not inconnues, f"{voix['slug']} : balises inconnues {inconnues}"
    reste = re.sub(r"\[[^\[\]]*\]", "", dit)
    assert "[" not in reste and "]" not in reste, f"{voix['slug']} : un crochet orphelin"
    assert "<" not in dit, f"{voix['slug']} : pas de SSML, v3 ne le lit pas"


def test_le_script_envoie_le_jeu_avec_le_modele_qui_le_lit():
    """Le cablage : un jeu ecrit que le script n'envoie pas, ou envoie a v2 (qui
    lit les crochets a voix haute), ne vaut rien."""
    source = (RACINE / "scripts" / "audio_elevenlabs.py").read_text(encoding="utf-8")
    boucle = source[source.index("for ligne in voix:", source.index("def main")):]
    assert '"text": interpretation.dit(ligne)' in boucle
    assert '"model_id": interpretation.MODELE' in boucle
    assert "finir_voix(" in boucle, "sans la finition, pas de temps mort a la fin"
    assert interpretation.MODELE == "eleven_v3"


def test_les_voix_a_secher_sont_des_voix_du_jeu():
    """Un nom mal recopie ne secherait personne, et rien ne le dirait."""
    utilisees = {v["voix"] for v in VOIX}
    inconnues = sorted(interpretation.VOIX_A_SECHER - utilisees)
    assert not inconnues, f"ces voix a secher ne parlent nulle part : {inconnues}"


def test_chaque_egalisation_corrige_une_voix_du_jeu():
    """Une cle mal recopiee laisserait sa voix au passe-haut des hommes, sans un mot."""
    utilisees = {v["voix"] for v in VOIX}
    inconnues = sorted(set(interpretation.EGALISATION) - utilisees)
    assert not inconnues, f"ces egalisations ne corrigent personne : {inconnues}"
    for filtre in interpretation.EGALISATION.values():
        assert filtre.startswith("highpass="), "le passe-haut d'abord : c'est la que « caverneux » vit"


def test_toutes_les_finitions_egalisent():
    """Les trois chemins qui fabriquent une voix : la generation, `--secher`, `--refinir`.
    Un seul qui oublie l'egalisation, et la voix redevient sourde a la prochaine passe."""
    source = (RACINE / "scripts" / "audio_elevenlabs.py").read_text(encoding="utf-8")
    appels = source.count("bilan = finir_voix(")
    assert appels == 3
    assert source.count("interpretation.egalisation(ligne)") == appels


def test_le_script_seche_avant_de_finir():
    """Le cablage, aux trois endroits ou une voix se fabrique : la generation,
    `--secher`, et `--refinir` — qui doit repartir du master SECHE."""
    source = (RACINE / "scripts" / "audio_elevenlabs.py").read_text(encoding="utf-8")
    boucle = source[source.index("for ligne in voix:", source.index("def main")):]
    assert "interpretation.a_secher(ligne)" in boucle and "secher(client, master" in boucle
    refinir = source[source.index("def refinir"):source.index("def secher_masters")]
    assert "-sec.wav" in refinir and "interpretation.MARQUE_SECHEE" in refinir
    assert '"elevenlabs_voice_isolation"' in source


# --- Les fichiers ------------------------------------------------------------------

ffmpeg_present = pytest.mark.skipif(
    shutil.which("ffprobe") is None or shutil.which("ffmpeg") is None,
    reason="ffmpeg n'est pas installe : ces juges mesurent des octets")

PRESENTES = [v for v in VOIX if audio.chemin_voix(v).is_file()]


def _ffmpeg(chemin, filtre):
    """⚠️ Les filtres de mesure ecrivent au niveau `info`, sur la sortie d'erreur."""
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(chemin), "-af", filtre,
                           "-f", "null", "-"], capture_output=True, text=True).stderr


def _duree_s(chemin):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(chemin)], capture_output=True, text=True).stdout)


@ffmpeg_present
@pytest.mark.parametrize("voix", [v for v in PRESENTES if interpretation.a_secher(v)], ids=lambda v: v["slug"])
def test_une_voix_qui_sonnait_dans_une_piece_a_ete_sechee(voix):
    """C'est le FICHIER qui le prouve (son etiquette `comment`) : une replique
    regeneree par un chemin qui oublie l'isolateur reviendrait dans sa piece, et
    la liste de `VOIX_A_SECHER` continuerait de le promettre."""
    tags = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=comment",
                           "-of", "default=nw=1:nk=1", str(audio.chemin_voix(voix))],
                          capture_output=True, text=True).stdout.strip()
    assert tags == interpretation.MARQUE_SECHEE, f"{voix['slug']} n'est pas passee par l'isolateur"


@ffmpeg_present
@pytest.mark.parametrize("voix", [v for v in PRESENTES if not v.get("histoire")], ids=lambda v: v["slug"])
def test_une_voix_de_la_rue_garde_ses_aigus(voix):
    """En 22 kHz, tout ce qui depasse 8 kHz etait coupe : les passants, les radios et
    les pubs sonnaient etouffes a cote de l'histoire, qui est en 44 kHz."""
    frequence = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                "stream=sample_rate", "-of", "csv=p=0", str(audio.chemin_voix(voix))],
                               capture_output=True, text=True).stdout.strip()
    assert frequence == "44100", f"{voix['slug']} : {frequence} Hz"


@ffmpeg_present
@pytest.mark.parametrize("voix", PRESENTES, ids=lambda v: v["slug"])
def test_une_voix_finit_sur_un_temps_mort(voix):
    """Mesure avant : les 19 repliques du narrateur finissaient a 10-47 ms du
    dernier son. Un navigateur qui enchaine sur `onended` coupe alors le souffle
    de la derniere syllabe."""
    sortie = _ffmpeg(audio.chemin_voix(voix), "areverse,silencedetect=n=-50dB:d=0.02")
    trouve = re.search(r"silence_start: -?0(?:\.0+)?\b.*?silence_duration: ([\d.]+)", sortie, re.S)
    queue = float(trouve.group(1)) if trouve else 0.0
    assert queue >= 0.8 * interpretation.TEMPS_MORT_S, (
        f"{voix['slug']} : {queue * 1000:.0f} ms de silence a la fin, "
        f"pour {interpretation.TEMPS_MORT_S * 1000:.0f} voulues")


@ffmpeg_present
@pytest.mark.parametrize("voix", PRESENTES, ids=lambda v: v["slug"])
def test_une_voix_est_au_niveau_des_autres(voix):
    """Mesure avant : de -32 a -15 LUFS, 17 dB d'ecart d'une replique a l'autre.

    ⚠️ Deux sorties honnetes : au niveau vise, OU arretee par le pic (un cri ne
    monte pas au niveau d'un murmure en ecretant). Et une replique trop breve
    pour etre mesuree (sous 400 ms de son) n'a que son pic a tenir.

    ⚠️ On mesure le niveau SANS le temps mort de la fin : la mesure travaille par
    blocs de 400 ms, et sur « Salut! » (0,5 s de voix) les 0,35 s de silence
    ajoutees tiraient le niveau a -21,4 pour une voix posee a -19,6.

    ⚠️ Le pic, lui, se mesure sur le fichier entier et avec 0,2 dB de marge
    seulement : l'encodeur depassait jusqu'a 2,3 dB, et c'est la finition qui
    remesure et reencode — ce juge-ci dit qu'elle l'a bien fait."""
    chemin = audio.chemin_voix(voix)
    pic = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", _ffmpeg(chemin, "ebur128=peak=sample"))[-1])
    assert pic <= interpretation.PIC_MAX_DBFS + 0.2, f"{voix['slug']} : pic a {pic:+.1f} dBFS"
    fin = _duree_s(chemin) - interpretation.TEMPS_MORT_S
    niveau = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", _ffmpeg(chemin, f"atrim=end={fin:.3f},ebur128"))[-1])
    if niveau <= -69:
        return
    au_niveau = abs(niveau - interpretation.NIVEAU_LUFS) <= 1.5
    # Arretee par le limiteur : il a travaille ses 6 dB, donc son pic est a la limite.
    arretee_par_le_pic = niveau < interpretation.NIVEAU_LUFS and pic >= interpretation.LIMITE_DBFS - 1.5
    assert au_niveau or arretee_par_le_pic, (
        f"{voix['slug']} : {niveau:.1f} LUFS (pic {pic:+.1f}) pour {interpretation.NIVEAU_LUFS} visés")


# --- Le jeu -------------------------------------------------------------------------

def test_une_ligne_attend_que_sa_voix_se_taise(banc):
    """⚠️ Le temps de LIRE une ligne (90 + 3 par caractere) la faisait passer a la
    suivante voix ou pas — et la suivante coupe la voix. Une replique qui
    respire est plus longue que ca : sans ce juge, les pauses coupaient tout."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        // ⚠️ Les QUATRE lignes de l'intro, dites d'un trait : parler a Ti-Guy joue
        // maintenant sa SCENE (`Scenes`), qui les dit en deux temps sous ses plans.
        // C'est l'attente de la voix qu'on juge ici, pas la scene.
        L.Histoire.dire(L.Histoire.courante() || L.B.defs.missions[0], 'intro', null);
        const c = L.B.cinema;
        if (!c) return null;
        // La voix de la premiere ligne joue, et elle est plus longue que le temps de lire.
        L.Son.Voix.enCours = { slug: c.lignes[0].slug };
        o.frame(c.duree + 120);
        const pendant = c.i;
        // Elle se tait : la ligne passe.
        L.Son.Voix.enCours = null;
        o.frame(3);
        const apres = c.i;
        // Sans voix du tout, le temps de lire suffit, comme avant.
        const sansVoix = c.duree;
        o.frame(sansVoix + 3);
        const lue = c.i;
        // Une voix qui ne dit jamais qu'elle s'est tue ne fige pas la scene.
        L.Son.Voix.enCours = { slug: c.lignes[c.i].slug };
        o.frame(c.duree + 900 + 3);
        const coincee = c.i;
        L.Son.Voix.enCours = null;
        return { pendant: pendant, apres: apres, lue: lue, coincee: coincee, lignes: c.lignes.length };
    }""")
    assert r is not None, "Ti-Guy ne parle pas : le banc n'a rien a juger"
    assert r["lignes"] >= 4
    assert r["pendant"] == 0, "la ligne est passee pendant que sa voix parlait"
    assert r["apres"] == 1, "la voix s'est tue et la ligne est restee"
    assert r["lue"] == 2, "sans voix, la ligne passe apres le temps de la lire"
    assert r["coincee"] == 3, "une voix muette pour le navigateur a fige la scene"
