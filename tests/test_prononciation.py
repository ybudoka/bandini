"""Le dictionnaire de prononciation des voix (22 sept. 2026).

Demande de Martin : « crée moi un dictionnaire pour mon jeu ». Les règles
(`app/prononciation.pls`) disent à ElevenLabs comment prononcer un mot sans
toucher au texte qu'on lit. Ce qui peut s'y perdre sans que personne l'entende :

- un lexique qu'ElevenLabs refuse (XML cassé, mauvais espace de noms) ;
- une règle morte (le mot a quitté toutes les répliques) ou en double (seule
  la première compte : la seconde ment en silence) ;
- une règle qui mord dans une balise de jeu (`[running]`) : v3 la lirait à voix haute ;
- un phonème qui n'est pas de l'IPA (un `g` ou un `r` tapé au clavier) ou qui a perdu sa
  lecture en clair (22 sept. 2026 : les règles passent de l'alias au phonème).
"""

import json
import re
import xml.etree.ElementTree as ET

import pytest

from app import audio, interpretation, prononciation

REGLES = prononciation.regles()
TEXTES = [interpretation.dit(v) for v in audio.toutes_les_voix()]


def test_le_lexique_est_un_pls_qu_elevenlabs_lit():
    racine = ET.parse(prononciation.FICHIER).getroot()
    assert racine.tag == f"{{{prononciation.ESPACE}}}lexicon"
    assert racine.get("version") == "1.0"
    assert racine.get("alphabet"), "l'attribut alphabet est exigé par le format, même sans phonème"
    assert racine.get("{http://www.w3.org/XML/1998/namespace}lang", "").startswith("fr")
    assert REGLES, "un dictionnaire sans règle"


#: L'IPA du français d'ici et de l'anglais qu'on y parle. ⚠️ Ni `g` ni `r` : le G de
#: l'IPA est `ɡ` (U+0261), et le R d'ici est `ʁ` — une touche du clavier glissée dans un
#: phonème est une faute de frappe, pas un son.
IPA = set("abdefhijklmnopstuvwyzøŋœɑɔəɛɡɪʁʃʊʒɲɥʏ") | {"\u0303", "ː", "ˈ", "ˌ", ".", " "}


def test_chaque_regle_est_un_phoneme_complet():
    """⚠️ Des phonèmes IPA, plus des alias (Martin, 22 sept. 2026 : « ça marche bien »,
    après « Deux piastres. » → pjɑs en v3). Un lexème = un grapheme puis un phonème, et
    rien d'autre : un alias à côté laisserait ElevenLabs choisir."""
    racine = ET.parse(prononciation.FICHIER).getroot()
    for lexeme in racine.findall(f"{{{prononciation.ESPACE}}}lexeme"):
        enfants = [e.tag.split("}")[1] for e in lexeme]
        assert enfants == ["grapheme", "phoneme"], f"un lexème = un grapheme puis un phonème : {enfants}"
    for mot, phoneme in REGLES:
        assert mot and mot.strip() == mot, f"grapheme vide ou avec des blancs : {mot!r}"
        assert phoneme and phoneme.strip() == phoneme, f"phonème vide ou avec des blancs pour « {mot} »"
        etrangers = sorted(set(phoneme) - IPA)
        assert not etrangers, f"« {mot} » → /{phoneme}/ : {etrangers} n'est pas de l'IPA d'ici"


def test_chaque_phoneme_se_lit_en_clair():
    """Personne ici ne relit l'IPA d'un coup d'œil : chaque règle garde, juste après elle,
    le commentaire `<!-- dit : piasses -->`. Sans lui, une règle qui sonne mal ne se
    retrouve plus dans le fichier."""
    sans = [mot for mot, lecture in prononciation.lectures().items() if not lecture]
    assert not sans, f"règles sans « {prononciation.MARQUE_LECTURE} » : {sans}"


def test_les_phonemes_vont_a_un_modele_qui_les_lit():
    """Le phonème dépend du modèle : eleven_v3 le lit, multilingual_v2 l'IGNORE (en
    silence — la voix dirait « piastres »). Changer de modèle, c'est revenir aux alias."""
    assert interpretation.MODELE == "eleven_v3"


def test_aucune_regle_en_double():
    """Seule la PREMIÈRE règle qui colle s'applique : une seconde ne ferait rien."""
    mots = [mot for mot, _ in REGLES]
    doubles = sorted({m for m in mots if mots.count(m) > 1})
    assert not doubles, f"règles en double : {doubles}"


RESERVE = prononciation.en_reserve()


@pytest.mark.parametrize("mot", [m for m, _ in REGLES if m not in RESERVE])
def test_chaque_regle_hors_reserve_touche_une_replique(mot):
    """Au-dessus de la réserve, une règle dont le mot n'est dans aucune réplique est
    une faute de frappe (« Prevost » ne corrigerait jamais « Prévost ») ou une règle
    morte : on la corrige, on la retire, ou on la descend dans la réserve."""
    assert any(mot in prononciation.touches(t) for t in TEXTES), (
        f"« {mot} » n'est dans aucune réplique dite (sensible à la casse) — "
        f"faute de frappe, ou à descendre sous « {prononciation.MARQUE_RESERVE} »")


def test_la_reserve_existe_et_ne_passe_pas_devant():
    """La réserve est la FIN du fichier : une règle dite qui la suivrait échapperait au
    juge ci-dessus. Et elle n'est pas vide — c'est elle qui sert les missions à venir."""
    lexemes = prononciation._lexemes()
    drapeaux = [reserve for _, _, _, reserve in lexemes]
    assert any(drapeaux), f"la marque « {prononciation.MARQUE_RESERVE} » manque"
    assert drapeaux == sorted(drapeaux), "une règle hors réserve après la marque"


def test_une_regle_courte_passe_avant_la_longue_qui_la_contient():
    """Seule la première règle qui colle s'applique : « Guy » avant « Ti-Guy » ferait
    dire « Ti-Gui » par hasard, et « Y a » avant … — l'ordre se tient ici."""
    mots = [m for m, _ in REGLES]
    for i, court in enumerate(mots):
        for long in mots[i + 1:]:
            assert not (court != long and re.search(prononciation._motif(court), long)), (
                f"« {long} » doit passer AVANT « {court} » : sinon « {court} » le mange")


def test_aucune_regle_ne_mord_dans_une_balise():
    for texte in TEXTES:
        for balise in interpretation.balises(texte):
            assert not prononciation.touches(balise), (
                f"[{balise}] serait réécrite par le dictionnaire : {prononciation.touches(balise)}")


def test_les_regles_prennent_des_mots_entiers():
    assert prononciation.entendu("Prenez donc la rue.") == "Prenez don la rue."
    assert prononciation.entendu("[running] Royal") == "[running] Royal"
    assert prononciation.entendu("l'inspectrice Roy.") == "l'inspectrice Roi."
    # une seule passe : une lecture n'est pas réécrite par une règle suivante
    assert prononciation.entendu("Astheure") == "Asteure"


def test_la_note_du_televersement_suit_le_lexique():
    """`prononciation.json` reste vide (`id: null`) tant que rien n'est téléversé — le
    script le remplit ; s'il désigne un dictionnaire, c'est un identifiant, pas du vide."""
    brut = json.loads(prononciation.TELEVERSE.read_text(encoding="utf-8"))
    assert set(brut) == {"empreinte", "id", "version_id"}
    if brut["id"] is None:
        pytest.skip("pas encore téléversé")
    note = prononciation.televerse()
    if note is None:
        pytest.skip("le lexique a changé depuis le dernier téléversement : le script en refera un")
    assert re.fullmatch(r"[A-Za-z0-9]+", note["id"])
