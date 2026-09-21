"""Rien devant une porte, plus large — les obstacles se DEPLACENT (`app/devants.py`).

Retour de Martin (20 sept. 2026) : « deplace les obstacles pour eviter que ca soit
devant les portes des commerces et dans les missions ».

⚠️ Le juge d'a cote (`test_carte.test_rien_ne_se_tient_devant_une_porte_meme_peinte`) tient
le pas de porte : deux tuiles. Celui-ci tient ce qu'un joueur lit comme « devant » : trois
tuiles dans l'axe, une de chaque cote, et plus large encore devant un lieu de mission. Et il
tient l'autre moitie de la promesse : on DEPLACE, on ne re-tire pas la ville.
"""

from functools import lru_cache
from unittest import mock

import pytest

from app import carte, devants

GRAINES = [carte.GRAINE, 1, 2, 7]

#: Ce que le deplacement ne doit JAMAIS toucher : le sol, les rues, les portes, et tout ce
#: qui s'est pose apres le decor.
INTACT = ("sol", "voie", "portes", "devantures", "residences", "lampes", "rampes", "autobus",
          "metro", "eboueurs", "chantiers", "paquets", "graffitis", "barrieres", "zones",
          "points_interet", "interieurs", "arrets", "intersections", "portes_garage")


@lru_cache(maxsize=None)
def _ville(graine: int, deplace: bool = True) -> dict:
    """La ville de cette graine, avec ou sans le deplacement (le temoin)."""
    if deplace:
        return carte.generer(graine=graine)
    with mock.patch.object(devants, "deplacer", lambda chantier, ville: None):
        return carte.generer(graine=graine)


def _bouche(ville: dict) -> list[str]:
    """Tout ce qui se tient devant une porte, et que ce module doit avoir ecarte."""
    larges, pas = devants.devants(ville)
    fl = ville["aqueduc"]["flaque"]

    def couvre(o: dict, rayon: int = 0) -> bool:
        return any((x, y) in larges
                   for x in range(o["x"] - rayon, o["x"] + o.get("l", 1) + rayon)
                   for y in range(o["y"] - rayon, o["y"] + o.get("h", 1) + rayon))

    trouves = [f"{d['type']} {d['x']},{d['y']}" for d in ville["decor"]
               if d["type"] in devants.DECOR_MOBILE and (d["x"], d["y"]) in larges]
    trouves += [f"kiosque {a['slug']} {a['x']},{a['y']}" for a in ville["ambulants"]
                if (a["x"], a["y"]) in larges or (a["x"], a["y"] + 1) in larges]
    trouves += [f"reclame {r['x']},{r['y']}" for r in ville["reclames"] if (r["x"], r["y"]) in larges]
    trouves += [f"scene {s['x']},{s['y']}" for s in ville["scenes"]
                if (s["x"], s["y"]) in larges
                or any((s["x"] + i, s["y"] + j) in pas for i in (-1, 0, 1) for j in (-1, 0, 1))]
    # ⚠️ Les evenements ECARTES (`ecartee`) ne comptent plus : le jeu passe au suivant.
    trouves += [f"{cle} {o['x']},{o['y']}" for cle in ("entraves", "fermetures", "nids_de_poule")
                for o in ville[cle] if couvre(o) and not o.get("ecartee")]
    trouves += [f"aqueduc {o['x']},{o['y']}" for o in ville["aqueducs"]
                if couvre(o, fl) and not o.get("ecartee")]
    return trouves


@pytest.mark.parametrize("graine", GRAINES)
def test_rien_de_ce_qui_bouche_ne_reste_devant_une_porte(graine):
    """⚠️ Mesure avant (16 a 40 objets par ville, quatre graines) : la scene d'un amuseur dont
    la foule tombe sur le seuil, un kiosque contre la porte du terminus, un BBQ, une caisse, un
    arbre — et, en jeu, la voie fermee du jour ou le bris d'aqueduc a trois tuiles de la porte du
    bar. Les deux tuiles reservees ne voyaient rien de tout ca."""
    restent = _bouche(_ville(graine))
    assert not restent, f"{len(restent)} devant une porte (graine {graine}) : {restent[:6]}"


@pytest.mark.parametrize("graine", GRAINES)
def test_le_temoin_a_bien_des_obstacles_devant_les_portes(graine):
    """Le juge du dessus ne vaut que si le temoin — la ville SANS le deplacement — en avait.
    Sans cette ligne, un juge qui ne regarde plus rien passerait au vert pour toujours."""
    assert len(_bouche(_ville(graine, deplace=False))) >= 8


@pytest.mark.parametrize("graine", GRAINES)
def test_la_ville_ne_bouge_que_ce_qui_bouchait(graine):
    """⚠️ La regle qui a coute vingt-six juges le jour ou une rangee de la trame a bouge : on
    ne re-tire pas la ville. Ici tout ce qui n'est pas un obstacle devant une porte est
    IDENTIQUE au temoin, et chaque objet qui a bouge est reparti a quelques tuiles de la."""
    sans, avec = _ville(graine, deplace=False), _ville(graine)
    for cle in INTACT:
        assert sans[cle] == avec[cle], f"« {cle} » a change : le deplacement touche a la ville"
    # ⚠️ Les listes dans lesquelles le jeu TIRE (`hash % longueur`) gardent leur longueur et leur
    # ordre : une entree de moins rebattrait tous les jours. Elles portent seulement un drapeau.
    for cle in ("entraves", "fermetures", "aqueducs"):
        assert [{k: v for k, v in o.items() if k != "ecartee"} for o in avec[cle]] == sans[cle], \
            f"« {cle} » n'a plus la meme longueur ou le meme ordre"

    larges, _ = devants.devants(avec)
    avant = {(d["type"], d["x"], d["y"]) for d in sans["decor"]}
    apres = {(d["type"], d["x"], d["y"]) for d in avec["decor"]}
    partis, arrives = avant - apres, apres - avant
    for type_, x, y in partis:
        assert type_ in devants.DECOR_MOBILE and (x, y) in larges, f"{type_} {x},{y} n'avait pas a partir"
    for type_, x, y in arrives:
        assert any(t == type_ and max(abs(x - px), abs(y - py)) <= devants.PORTEE
                   for t, px, py in partis), f"{type_} {x},{y} est arrive de nulle part"
    assert len(avec["decor"]) >= len(sans["decor"]) - 2, "le deplacement a vide la rue"

    # Les kiosques et leur reclame : aucun ne disparait sur ces graines, et leur lien tient.
    assert len(avec["ambulants"]) == len(sans["ambulants"])
    for a, b in zip(sans["ambulants"], avec["ambulants"]):
        assert a["slug"] == b["slug"]
        assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) <= 2 * devants.PORTEE_D_UN_KIOSQUE
    kiosques = {(a["x"], a["y"]) for a in avec["ambulants"]}
    for r in avec["reclames"]:
        assert (r["kiosque"]["x"], r["kiosque"]["y"]) in kiosques, "une reclame crie pour un kiosque qui n'y est plus"
    # Les scenes : quelques-unes de moins au pire, jamais plus.
    assert len(sans["scenes"]) - 3 <= len(avec["scenes"]) <= len(sans["scenes"])
    # Ce qu'on ecarte en laisse assez (`AQUEDUCS`, `NIDS_DE_POULE`), et n'ecarte que ce qui bouche.
    assert len([o for o in avec["aqueducs"] if not o.get("ecartee")]) >= carte.AQUEDUCS["par_ville"][0]
    assert len(avec["nids_de_poule"]) >= carte.NIDS_DE_POULE["par_ville"][0]
    assert [o for o in avec["entraves"] if not o.get("ecartee")]
    assert [o for o in avec["fermetures"] if not o.get("ecartee")]
    for cle in ("entraves", "fermetures"):
        for o in avec[cle]:
            touche = any((o["x"] + i, o["y"] + j) in larges for i in range(o["l"]) for j in range(o["h"]))
            assert bool(o.get("ecartee")) == touche, f"{cle} {o['x']},{o['y']} : ecartee = {o.get('ecartee')}, touche = {touche}"


@pytest.mark.parametrize("graine", GRAINES)
def test_ce_qu_on_deplace_ne_se_pose_pas_sur_autre_chose(graine):
    """Une tuile prise ne se reprend pas : ni deux decors sur la meme, ni un decor sur un kiosque,
    une scene, un quai d'autobus, une station de metro ou un bac d'eboueur."""
    ville = _ville(graine)
    tuiles = [(d["x"], d["y"]) for d in ville["decor"]]
    assert len(tuiles) == len(set(tuiles)), "deux decors sur la meme tuile"
    pose = set(tuiles)
    for couche in ("ambulants", "paquets"):
        assert not pose & {(o["x"], o["y"]) for o in ville[couche]}, f"un decor sur « {couche} »"
    assert not {(o["x"], o["y"]) for o in ville["ambulants"]} & {(o["x"], o["y"]) for o in ville["reclames"]}
    # ⚠️ Ce qu'ON A POSE (un decor arrive, un kiosque ou une reclame reparti) ne prend la tuile de
    # rien d'autre. La station de metro EST son edicule (un decor) : on ne juge donc que les
    # arrivees — comme sur un bac de la tournee. Et une reclame de la ville sans le deplacement
    # peut deja avoir un arbre sous les pieds (`reclames()` ne reserve pas sa tuile) : hors sujet.
    temoin = _ville(graine, deplace=False)
    vus = {(d["type"], d["x"], d["y"]) for d in temoin["decor"]}
    arrives = {(d["x"], d["y"]) for d in ville["decor"] if (d["type"], d["x"], d["y"]) not in vus}
    deja = {(o["x"], o["y"]) for couche in ("reclames", "ambulants", "paquets") for o in temoin[couche]}
    assert not arrives & deja, "un decor est arrive sur un kiosque, une reclame ou un paquet"
    assert not arrives & {(s["x"], s["y"]) for s in ville["metro"]["stations"]}
    assert not arrives & {(x, y) for _, x, y in (ville["eboueurs"] or {}).get("points", [])}
    deplaces = [o for couche in ("reclames", "ambulants")
                for o, b in zip(ville[couche], temoin[couche]) if (o["x"], o["y"]) != (b["x"], b["y"])]
    assert not {(o["x"], o["y"]) for o in deplaces} & pose, "un kiosque ou une reclame deplace sur un decor"
    # Un kiosque reste sur la SORTE de sol qui lui convient (le camion sur l'asphalte, la cabane sur
    # le quai) : `_places_ambulantes` en decide, le deplacement n'invente rien.
    for a, b in zip(temoin["ambulants"], ville["ambulants"]):
        assert ville["sol"][a["y"]][a["x"]] == ville["sol"][b["y"]][b["x"]], f"{b} a change de sol"


def test_le_deplacement_ne_tire_aucun_de():
    """⚠️ Aucun de : c'est ce qui fait qu'on peut le retirer sans deplacer une seule autre
    tuile, et qu'il donne la meme ville a chaque generation."""
    original = devants.deplacer

    def surveille(chantier, ville):
        with mock.patch.object(carte.Des, "suivant", side_effect=AssertionError("un de tire")), \
                mock.patch.object(carte.Des, "chance", side_effect=AssertionError("un de tire")), \
                mock.patch.object(carte.Des, "entier", side_effect=AssertionError("un de tire")):
            return original(chantier, ville)

    with mock.patch.object(devants, "deplacer", surveille):
        ville = carte.generer(graine=1)
    assert ville["devant"]


def test_les_lieux_des_missions_se_lisent_dans_les_missions():
    """Le devant d'un lieu de mission est plus large — et les lieux ne s'ecrivent pas ici : ils
    viennent des objectifs, des scenes et des personnages."""
    ville = _ville(carte.GRAINE)
    lieux = devants.lieux_de_mission(ville)
    # M1 va au garage et livre au garage ; Ti-Guy attend au terminus ; Thibodeau au kiosque ;
    # Bouchard mange au casse-croute (sa piece, lue par son `point:`).
    assert {"garage", "terminus", "kiosque", "casse_croute"} <= lieux
    assert lieux < {p["lieu"] for p in ville["portes"]} | lieux
    assert lieux <= {p["lieu"] for p in ville["portes"]}, "un lieu de mission sans porte dans la ville"


@pytest.mark.parametrize("graine", GRAINES)
def test_devant_un_lieu_de_mission_le_devant_est_plus_large(graine):
    """Deux tuiles de plus de chaque cote, une de plus devant : la ou le donneur attend et ou
    le char se livre. Rien de mobile n'y reste — pas meme a la limite de la fenetre ordinaire."""
    ville = _ville(graine)
    lieux = devants.lieux_de_mission(ville)
    zone = {(p["x"] + dx, p["y"] + dy) for p in ville["portes"] if p["lieu"] in lieux
            for dx, dy in devants.DEVANT_DE_MISSION}
    assert zone, "aucune porte de mission"
    restent = [d for d in ville["decor"] if d["type"] in devants.DECOR_MOBILE and (d["x"], d["y"]) in zone]
    assert not restent, f"devant un lieu de mission : {restent[:4]}"
    assert not [a for a in ville["ambulants"] if (a["x"], a["y"]) in zone], "un kiosque devant un lieu de mission"
    assert not [s for s in ville["scenes"] if (s["x"], s["y"]) in zone], "une scene devant un lieu de mission"


def test_la_ville_dit_quel_est_le_devant_d_une_porte():
    """Le jeu lit la fenetre dans la ville (`def.devant`) : il ne la recopie pas."""
    assert _ville(carte.GRAINE)["devant"] == {"cote": devants.DEVANT_COTE, "profondeur": devants.DEVANT_PROFONDEUR}
    assert set(devants.DEVANT) == {(dx, dy) for dy in (1, 2, 3) for dx in (-1, 0, 1)}
