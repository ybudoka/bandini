"""Les missions mises en scène, 1re vague : le vocabulaire de plans et ses juges.

⚠️ Une scène est une LISTE DE PLANS dans `missions.py`, et `scenes.js` la joue sans
connaître aucune scène par son nom. Ces juges tiennent les deux bouts : le Python
n'écrit que des plans que le navigateur sait jouer, et le navigateur ne triche pas
en reconnaissant une scène.
"""

import re
from pathlib import Path

import pytest

from app import missions
from app.missions._commun import _l, _p, _r

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
        # ⚠️ Celles qu'elle écrit ET celles que le défaut lui bâtirait : c'est le
        # défaut qui portera la prochaine mission, et les cent de M16.
        ecrites = list(m["scenes"].items())
        defauts = [(partie, missions.scene_par_defaut(m, partie)) for partie in ("intro", "fin")]
        for partie, scene in ecrites + defauts:
            for plan in scene:
                for nom in (plan.get(cle) for cle in ("vers", "dans", "de")):
                    if not isinstance(nom, str) or ":" not in nom:
                        continue
                    forme, suite = nom.split(":", 1)
                    # `ruelle:garage:24` : la ruelle a vingt-quatre tuiles au moins.
                    if forme == "ruelle" and ":" in suite:
                        suite, tuiles = suite.split(":", 1)
                        assert tuiles.isdigit(), (m["slug"], partie, nom)
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
    """⚠️ `pendant` se compte APRÈS `echec`, et `renvoi` après `pendant` : insérées avant
    `fin`, elles renommaient les voix de fin et d'échec déjà générées — des mp3 payés
    devenus des 404."""
    for m in missions.CATALOGUE:
        n, attendus = 0, {}
        for partie in ("appel", "intro", "client", "fin", "echec"):
            for ligne in m["dialogue"].get(partie, []):
                n += 1
                attendus[(partie, ligne["texte"])] = f"{ligne['qui']}-{m['slug']}-{n}"
        for r in missions.repliques():
            if r["mission"] == m["slug"] and r["partie"] not in ("pendant", "renvoi"):
                assert r["slug"] == attendus[(r["partie"], r["texte"])], r


def test_une_replique_renvoi_s_accroche_a_un_objectif_qui_existe_et_se_dit_en_personne():
    """⚠️ Lulu, de jour, renvoie qui lui parle trop tôt (m50). Une réplique `renvoi` dont
    l'objectif n'existe pas ne se dirait jamais ; et on lui PARLE, donc elle ne passe pas au
    combiné."""
    fiche = _fiche("marco", [{"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE"}])
    fiche["dialogue"]["renvoi"] = [_r("marco", "Reviens ce soir.", 0)]
    missions._completer(fiche)
    assert missions.erreurs_de_mise_en_scene(fiche) == []
    fiche["dialogue"]["renvoi"] = [_r("marco", "Reviens ce soir.", 7)]
    assert any("renvoi accrochée à un objectif qui n'existe pas" in e for e in missions.erreurs_de_mise_en_scene(fiche))
    renvois = [r for r in missions.repliques() if r["partie"] == "renvoi"]
    assert [r["slug"] for r in renvois] == ["lulu-m50-8"], "m50 : Lulu dit d'attendre la nuit"
    assert not any(r["telephone"] for r in renvois)


def test_un_acteur_qui_marche_vers_le_joueur_s_arrete_a_distance_de_parole():
    """⚠️ Martin, 20 sept. 2026 : « Marco se déplace par-dessus le personnage principal dans
    l'animation du début ». Sans `pres`, `marcher vers joueur` va au pixel du joueur : l'acteur
    finit dessus. Rouge avant : m50 n'en passait pas, ni à l'intro ni à la fin."""
    for m in missions.CATALOGUE:
        for partie, scene in m["scenes"].items():
            for plan in scene:
                if plan["type"] == "marcher" and plan.get("vers") == "joueur":
                    assert plan.get("pres", 0) >= 14, (m["slug"], partie, "marche sur le joueur")
    nu = [{"type": "marcher", "acteur": "donneur", "vers": "joueur", "duree": 50}]
    assert any("sans `pres`" in e for e in missions.erreurs_de_scene(nu))
    assert missions.erreurs_de_scene([dict(nu[0], pres=22)]) == []


def test_l_echec_se_dit_au_combine():
    """On n'est jamais à côté du donneur quand on rate."""
    echecs = [r for r in missions.repliques() if r["partie"] == "echec"]
    assert echecs and all(r["telephone"] for r in echecs)


# --- Le bloc Lego : une mission qui n'apporte que ses données ---------------------------


def _fiche(donneur, objectifs, intro=2, fin=2):
    """Une fiche réduite à l'os : ce qui distingue une mission, et rien d'autre.
    Pas de `prerequis`, pas de `phase`, pas d'`echec`, pas de `donne`, pas de
    `scenes`."""
    return {
        "slug": "zz", "titre": "Un essai", "donneur": donneur, "recompense": 100,
        "objectifs": objectifs,
        "dialogue": {
            "appel": [_l(donneur, "Viens me voir.")],
            "intro": [_l(donneur, f"Intro {i}.") for i in range(1, intro + 1)],
            "pendant": [_p(donneur, "Ça avance?", 0)],
            "fin": [_l(donneur, f"Fin {i}.") for i in range(1, fin + 1)],
            "echec": [_l(donneur, "Une autre fois.")],
        },
    }


#: Les formes que le défaut doit couvrir — ce sont celles que les missions écrites
#: à la main ont fini par prendre. ⚠️ `marco` et `thibodeau` se tiennent dehors
#: (`porte:`), `bouchard` et `josee` dedans (`point:`).
FORMES = {
    "dehors, fin ailleurs": ("marco", [{"type": "aller", "lieu": "poste", "rayon": 4, "texte": "VA AU POSTE"}]),
    "dehors, fin chez lui": ("thibodeau", [{"type": "tuer", "groupe": "cravates", "n": 2, "ou": "donneur", "texte": "COGNE"},
                                           {"type": "retourner", "texte": "REVIENS"}]),
    "dedans, un lieu à montrer": ("bouchard", [{"type": "aller", "lieu": "poste", "rayon": 4, "texte": "VA AU POSTE"}]),
    "dedans, rien à montrer": ("josee", [{"type": "survivre", "secondes": 30, "texte": "TIENS LE COUP"}]),
    "une zone": ("josee", [{"type": "tuer", "groupe": "cravates", "n": 2, "ou": "zone:cravates", "texte": "VIDE LE COIN"}]),
    "une seule réplique": ("marco", [{"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE"}], 1, 1),
}


@pytest.mark.parametrize("forme", sorted(FORMES))
def test_une_mission_qui_n_apporte_que_ses_donnees_est_finie(forme):
    """⚠️ **LE BLOC LEGO** (demande de Martin, 20 sept. 2026). Un fichier de
    mission qui n'écrit que ce qui la distingue — son donneur, ses objectifs, ses
    répliques — reçoit tout le reste : ses clés par défaut ET ses deux scènes. Il
    doit passer le juge du catalogue sans qu'on lui ajoute une ligne."""
    fiche = _fiche(*FORMES[forme])
    manque = set(missions.DEFAUTS_DE_MISSION) - set(fiche)
    assert manque, "la fiche d'essai doit vraiment omettre les clés par défaut"
    missions._completer(fiche)
    assert missions.erreurs_de_mise_en_scene(fiche) == [], forme
    for cle, valeur in missions.DEFAUTS_DE_MISSION.items():
        if cle != "scenes":
            assert fiche[cle] == valeur, (forme, cle)
    for partie in ("intro", "fin"):
        assert fiche["scenes"][partie], (forme, partie)


@pytest.mark.parametrize("forme", sorted(FORMES))
def test_une_scene_par_defaut_montre_quelque_chose(forme):
    """Une scène par défaut n'est jamais une boîte de dialogue déguisée : il s'y
    passe toujours un geste, une caméra ou une coupe. Et **dedans, elle sort** —
    sinon on parlerait d'un lieu qu'on ne montre pas."""
    fiche = _fiche(*FORMES[forme])
    missions._completer(fiche)
    for partie in ("intro", "fin"):
        assert {p["type"] for p in fiche["scenes"][partie]} - {"dire"}, (forme, partie)
    if missions.dedans(FORMES[forme][0]):
        assert "coupe" in {p["type"] for p in fiche["scenes"]["intro"]}, forme


def test_le_catalogue_est_complete_a_l_import():
    """Personne, en aval — le paquet, le navigateur, les juges — n'a à savoir
    qu'une clé pouvait manquer."""
    for m in missions.CATALOGUE:
        for cle in ("prerequis", "phase", "echec", "donne", "scenes"):
            assert cle in m, (m["slug"], cle)
        assert set(m["scenes"]) == {"intro", "fin"}, m["slug"]


def test_chaque_mission_du_catalogue_a_aussi_des_scenes_par_defaut_jouables():
    """⚠️ Les missions écrivent les leurs ; le défaut doit quand même savoir les
    mettre en scène — c'est lui qui portera les cent de M16. Le banc les joue
    toutes les deux (`test_missions_en_scene_js`)."""
    for m in missions.CATALOGUE:
        for partie in ("intro", "fin"):
            assert missions.erreurs_de_scene(missions.scene_par_defaut(m, partie)) == [], (m["slug"], partie)
