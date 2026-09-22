"""Le dictionnaire de prononciation des voix (22 sept. 2026).

Demande de Martin : « crée moi un dictionnaire pour mon jeu ». Les règles
(`app/prononciation.pls`) disent à ElevenLabs comment prononcer un mot sans
toucher au texte qu'on lit. Ce qui peut s'y perdre sans que personne l'entende :

- un lexique qu'ElevenLabs refuse (XML cassé, mauvais espace de noms) ;
- une règle morte (le mot a quitté toutes les répliques) ou en double (seule
  la première compte : la seconde ment en silence) ;
- une règle qui mord dans une balise de jeu (`[running]`) : v3 la lirait à voix haute.
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


def test_chaque_regle_est_un_alias_complet():
    """⚠️ Des alias, pas des phonèmes : l'alias marche avec tous les modèles (le
    phonème IPA dépend du modèle), et il se relit sans connaître l'IPA."""
    racine = ET.parse(prononciation.FICHIER).getroot()
    for lexeme in racine.findall(f"{{{prononciation.ESPACE}}}lexeme"):
        enfants = [e.tag.split("}")[1] for e in lexeme]
        assert enfants == ["grapheme", "alias"], f"un lexème = un grapheme puis un alias : {enfants}"
    for mot, alias in REGLES:
        assert mot and mot.strip() == mot, f"grapheme vide ou avec des blancs : {mot!r}"
        assert alias and alias.strip() == alias, f"alias vide ou avec des blancs pour « {mot} »"
        assert alias != mot, f"« {mot} » se remplace par lui-même"


def test_aucune_regle_en_double():
    """Seule la PREMIÈRE règle qui colle s'applique : une seconde ne ferait rien."""
    mots = [mot for mot, _ in REGLES]
    doubles = sorted({m for m in mots if mots.count(m) > 1})
    assert not doubles, f"règles en double : {doubles}"


@pytest.mark.parametrize("mot", [m for m, _ in REGLES])
def test_chaque_regle_touche_au_moins_une_replique(mot):
    """Une règle dont le mot a quitté toutes les répliques est morte : on la
    retire, ou c'est la réplique qui a changé d'orthographe sans prévenir."""
    assert any(mot in prononciation.touches(t) for t in TEXTES), (
        f"« {mot} » n'est dans aucune réplique dite (sensible à la casse)")


def test_aucune_regle_ne_mord_dans_une_balise():
    for texte in TEXTES:
        for balise in interpretation.balises(texte):
            assert not prononciation.touches(balise), (
                f"[{balise}] serait réécrite par le dictionnaire : {prononciation.touches(balise)}")


def test_les_regles_prennent_des_mots_entiers():
    assert prononciation.entendu("Prenez donc la rue.") == "Prenez don la rue."
    assert prononciation.entendu("[running] Royal") == "[running] Royal"
    assert prononciation.entendu("l'inspectrice Roy.") == "l'inspectrice Roi."
    # une seule passe : un alias n'est pas réécrit par une règle suivante
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
