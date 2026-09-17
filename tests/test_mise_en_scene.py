"""Les missions mises en scène, 1re vague : le vocabulaire de plans et ses juges.

⚠️ Une scène est une LISTE DE PLANS dans `missions.py`, et `scenes.js` la joue sans
connaître aucune scène par son nom. Ces juges tiennent les deux bouts : le Python
n'écrit que des plans que le navigateur sait jouer, et le navigateur ne triche pas
en reconnaissant une scène.
"""

import re
from pathlib import Path

from app import missions

RACINE = Path(__file__).resolve().parent.parent
SCENES_JS = (RACINE / "static" / "js" / "scenes.js").read_text(encoding="utf-8")


def _types_du_navigateur() -> set[str]:
    bloc = SCENES_JS[SCENES_JS.index("const PLANS = {"):SCENES_JS.index("\n  return { jouer")]
    return set(re.findall(r"^    ([a-z_]+): \{$", bloc, re.M))


def test_le_navigateur_joue_exactement_les_types_du_catalogue():
    assert _types_du_navigateur() == set(missions.TYPES_PLANS), \
        "un type de plan que l'un connaît et pas l'autre : la scène sauterait ce plan en silence"


def test_l_ouverture_s_ecrit_dans_le_vocabulaire():
    assert missions.erreurs_de_scene(missions.SCENE_OUVERTURE) == []
    genres = {p["type"] for p in missions.SCENE_OUVERTURE}
    # La preuve que les plans suffisent : un car qui arrive et repart, quelqu'un qui
    # en descend et marche, la caméra, le noir, la narration, le titre, la musique.
    assert {"conduire", "sortir", "marcher", "camera", "coupe", "dire", "titre", "son"} <= genres


def test_le_juge_des_scenes_refuse_ce_qui_ne_se_joue_pas():
    mauvais = [
        ([{"type": "danser"}], "type inconnu"),
        ([{"type": "attendre", "duree": 10, "vers": "garage"}], "clés inconnues"),
        ([{"type": "geste", "acteur": "joueur", "geste": "saluer"}], "geste inconnu"),
        ([{"type": "conduire", "acteur": "car", "vers": "arret", "part": 10, "duree": 5}], "pas les deux"),
        ([{"type": "son", "sfx": "pas", "musique": "titre"}], "un seul"),
        ([{"type": "camera", "vers": "arret", "duree": 10, "courbe": "rebond"}], "courbe inconnue"),
        ([{"type": "titre", "monte": 10}], "sans texte"),
        ([{"type": "marcher", "vers": "quai", "duree": 10}], "sans acteur"),
        ([{"type": "attendre", "duree": -3}], "entier positif"),
        ([], "vide"),
    ]
    for scene, attendu in mauvais:
        erreurs = missions.erreurs_de_scene(scene)
        assert any(attendu in e for e in erreurs), (scene, erreurs)


def test_le_paquet_porte_les_scenes(paquet):
    assert paquet["scenes"]["ouverture"] == missions.SCENE_OUVERTURE
    assert set(paquet["types_plans"]) == set(missions.TYPES_PLANS)


def test_le_metteur_en_scene_ne_connait_aucune_scene_par_son_nom():
    """⚠️ Le juge qui aurait attrapé un `if (slug === 'ouverture')` : ni une scène, ni
    un lieu, ni un personnage, ni une mission ne se nomme dans `scenes.js`."""
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", SCENES_JS, flags=re.S)
    noms = {"ouverture", "terminus", "autobus", "garage", "narrateur"}
    noms |= {m["slug"] for m in missions.CATALOGUE} | {p["slug"] for p in missions.PERSONNAGES}
    for nom in sorted(noms):
        assert not re.search(rf"['\"]{re.escape(nom)}['\"]", code), f"scenes.js nomme « {nom} »"


def test_histoire_ne_joue_plus_l_ouverture_en_dur():
    histoire = (RACINE / "static" / "js" / "histoire.js").read_text(encoding="utf-8")
    assert "Scenes.jouer(" in histoire
    for reste in ("OUV_LOIN", "marcherVersLeQuai", "placerLeCar", "Vehicules.creer('autobus'"):
        assert reste not in histoire, f"l'ancienne ouverture traîne encore : {reste}"


def test_les_six_gestes_sont_dessines_dans_les_trois_faces():
    sprites = (RACINE / "static" / "js" / "sprites.js").read_text(encoding="utf-8")
    immobile = re.search(r"^      bas: \[\n        \[([^\]]+)\]", sprites, re.M).group(1)
    for geste in missions.GESTES:
        for face in ("bas", "haut", "cote"):
            m = re.search(rf"^      geste_{geste}_{face}: \[\[([^\]]+)\]\],$", sprites, re.M)
            assert m, f"geste_{geste}_{face} n'est pas dessiné"
            rangs = re.findall(r"'([^']*)'", m.group(1))
            assert len(rangs) == 16 and all(len(r) == 12 for r in rangs), (geste, face)
            if face == "bas":
                assert rangs != re.findall(r"'([^']*)'", immobile), f"{geste} : c'est la pose immobile"
