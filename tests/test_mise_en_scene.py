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


# --- 2e vague : les cinq missions de la v1, mises en scène ------------------------------


def test_chaque_mission_est_finie():
    """Une mission, c'est trois choses : ses objectifs, ses répliques à chaque temps
    (intro, pendant, fin, échec) et ses scènes (intro, fin). Il en manque une, et
    elle n'est pas finie — ni les cinq de la v1, ni les cent de M16."""
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_mise_en_scene(m) == [], m["slug"]


def test_les_lieux_des_scenes_existent_dans_la_ville():
    from app import carte
    ville = carte.generer()
    lieux = {p["slug"] for p in ville["points_interet"]} | {p["lieu"] for p in ville["portes"] if p.get("lieu")}
    zones = {z["slug"] for z in ville["zones"]}
    for m in missions.CATALOGUE:
        for partie, scene in m["scenes"].items():
            for plan in scene:
                for nom in (plan.get(cle) for cle in ("vers", "dans", "de")):
                    if not isinstance(nom, str) or ":" not in nom:
                        continue
                    forme, suite = nom.split(":", 1)
                    if forme in ("porte", "ruelle"):
                        assert suite in lieux, (m["slug"], partie, nom)
                    elif forme == "zone":
                        assert suite in zones, (m["slug"], partie, nom)
                    elif forme == "chez":
                        assert missions.personnage(suite)["ou"], (m["slug"], partie, nom)


def test_le_juge_refuse_une_mission_pas_finie():
    import copy
    m4 = missions.par_slug("m4")
    sans_coupe = copy.deepcopy(m4)
    sans_coupe["scenes"]["fin"] = [{"type": "dire"}]
    assert any("personne ne va le voir" in e for e in missions.erreurs_de_mise_en_scene(sans_coupe))
    sans_pendant = copy.deepcopy(missions.par_slug("m1"))
    sans_pendant["dialogue"]["pendant"] = []
    assert any("pendant" in e for e in missions.erreurs_de_mise_en_scene(sans_pendant))
    ligne_oubliee = copy.deepcopy(m4)
    ligne_oubliee["scenes"]["intro"] = [p for p in ligne_oubliee["scenes"]["intro"] if p.get("repliques") != [2, 3]]
    assert any("toutes, une fois" in e for e in missions.erreurs_de_mise_en_scene(ligne_oubliee))
    acteur_inconnu = copy.deepcopy(m4)
    acteur_inconnu["scenes"]["intro"].append({"type": "geste", "acteur": "fantome", "geste": "hausser"})
    assert any("acteur inconnu" in e for e in missions.erreurs_de_mise_en_scene(acteur_inconnu))


def test_histoire_ne_nomme_aucune_mission():
    """⚠️ Le juge qui aurait attrapé le `if (m.slug === 'm1')` de `reussir()` : ce que
    fait une mission est dans ses données, jamais dans `histoire.js`."""
    histoire = (RACINE / "static" / "js" / "histoire.js").read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", histoire, flags=re.S)
    for m in missions.CATALOGUE:
        assert not re.search(rf"['\"]{m['slug']}['\"]", code), f"histoire.js nomme la mission {m['slug']}"


def test_les_voix_deja_payees_gardent_leur_slug():
    """⚠️ `pendant` se compte APRÈS `echec` : insérée avant `fin`, elle renommait les
    voix de fin et d'échec déjà générées — des mp3 payés devenus des 404."""
    for m in missions.CATALOGUE:
        n, attendus = 0, {}
        for partie in ("appel", "intro", "client", "fin", "echec"):
            for ligne in m["dialogue"].get(partie, []):
                n += 1
                attendus[(partie, ligne["texte"])] = f"{ligne['qui']}-{m['slug']}-{n}"
        for r in missions.repliques():
            if r["mission"] == m["slug"] and r["partie"] != "pendant":
                assert r["slug"] == attendus[(r["partie"], r["texte"])], r


def test_l_echec_se_dit_au_combine():
    """On n'est jamais à côté du donneur quand on rate."""
    echecs = [r for r in missions.repliques() if r["partie"] == "echec"]
    assert echecs and all(r["telephone"] for r in echecs)
