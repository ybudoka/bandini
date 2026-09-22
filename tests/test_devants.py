"""Rien devant une porte, plus large — les obstacles se DEPLACENT (`app/devants.py`).

Retour de Martin (20 sept. 2026) : « deplace les obstacles pour eviter que ca soit
devant les portes des commerces et dans les missions ».

⚠️ Le juge d'a cote (`test_carte.test_rien_ne_se_tient_devant_une_porte_meme_peinte`) tient
le pas de porte : deux tuiles. Celui-ci tient ce qu'un joueur lit comme « devant » : trois
tuiles dans l'axe, une de chaque cote, et plus large encore devant un lieu de mission. Et il
tient l'autre moitie de la promesse : on DEPLACE, on ne re-tire pas la ville.
"""

from collections import Counter
from functools import lru_cache
from unittest import mock

import pytest

from app import autobus, carte, chantiers, devants, missions

GRAINES = [carte.GRAINE, 1, 2, 7]

#: Ce que le deplacement ne doit JAMAIS toucher : le sol, les rues, les portes, et tout ce
#: qui s'est pose apres le decor.
INTACT = ("sol", "voie", "portes", "devantures", "residences", "lampes", "rampes",
          "metro", "eboueurs", "paquets", "graffitis", "barrieres", "zones",
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
    # ⚠️ Les chantiers, sans leurs annexes : elles LISENT la ville finie (`chantiers.completer`).
    assert chantiers.sans_annexes(sans["chantiers"]) == chantiers.sans_annexes(avec["chantiers"]), \
        "les chantiers ont change : le deplacement touche a la ville"
    # ⚠️ Les listes dans lesquelles le jeu TIRE (`hash % longueur`) gardent leur longueur et leur
    # ordre : une entree de moins rebattrait tous les jours. Elles portent seulement un drapeau.
    for cle in ("entraves", "fermetures", "aqueducs"):
        assert [{k: v for k, v in o.items() if k != "ecartee"} for o in avec[cle]] == sans[cle], \
            f"« {cle} » n'a plus la meme longueur ou le meme ordre"

    # ⚠️ Les autobus : un arrêt qui collait la porte d'un lieu de mission GLISSE le long de sa voie,
    # son abri et son banc avec lui (`_deplacer_les_arrets`) — rien d'autre des lignes ne bouge.
    glisses = _glissements(sans, avec)
    abris_et_bancs = {(t, x, y) for g in glisses for t, x, y in g["partis"] | g["arrives"]}

    larges, _ = devants.devants(avec)
    avant = {(d["type"], d["x"], d["y"]) for d in sans["decor"]}
    apres = {(d["type"], d["x"], d["y"]) for d in avec["decor"]}
    partis, arrives = avant - apres - abris_et_bancs, apres - avant - abris_et_bancs
    assert {t for g in glisses for t in g["partis"]} <= avant - apres, "un abribus a glissé sans partir"
    assert {t for g in glisses for t in g["arrives"]} <= apres - avant, "un abribus a glissé sans arriver"
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


def _banc(ville: dict, rang: int) -> tuple[int, int] | None:
    """Le banc d'un arrêt : à côté de son abri, le long de la voie, et tourné comme lui."""
    a = autobus.detail(ville, rang)
    dx, dy = autobus.PAS[a["sens"]]
    ax, ay = a["abri"]
    bancs = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] == autobus.BANCS[a["sens"]]}
    return next((b for b in ((ax - dx, ay - dy), (ax + dx, ay + dy)) if b in bancs), None)


def _glissements(sans: dict, avec: dict) -> list[dict]:
    """Les arrêts qui ont glissé d'une ville à l'autre — et le juge de ce qu'un glissement a le droit
    de changer : rien des lignes que l'indice de CET arrêt, décalé d'autant de tuiles qu'il a glissé
    sur sa voie ; son nom ne change pas, ni sa flèche."""
    assert len(sans["autobus"]["arrets"]) == len(avec["autobus"]["arrets"])
    for cle in sans["autobus"]:
        if cle not in ("arrets", "lignes"):
            assert sans["autobus"][cle] == avec["autobus"][cle], f"« autobus.{cle} » a changé"
    glisses, decalages = [], {}
    for rang, (a, b) in enumerate(zip(sans["autobus"]["arrets"], avec["autobus"]["arrets"])):
        assert a["nom"] == b["nom"], f"l'arrêt {rang} a changé de nom : {a['nom']} -> {b['nom']}"
        if (a["x"], a["y"]) == (b["x"], b["y"]):
            continue
        da, db = autobus.detail(sans, rang), autobus.detail(avec, rang)
        assert da["sens"] == db["sens"], f"{a['nom']} a changé de voie"
        dx, dy = autobus.PAS[da["sens"]]
        k = (b["x"] - a["x"]) * dx + (b["y"] - a["y"]) * dy
        assert (b["x"], b["y"]) == (a["x"] + dx * k, a["y"] + dy * k), f"{a['nom']} a quitté sa voie"
        assert 1 <= abs(k) <= devants.PORTEE_D_UN_ARRET, f"{a['nom']} a glissé de {k} tuiles"
        ancien_banc, nouveau_banc = _banc(sans, rang), _banc(avec, rang)
        assert (ancien_banc is None) == (nouveau_banc is None), f"{a['nom']} a perdu ou gagné son banc"
        decalages[rang] = k
        glisses.append({
            "nom": a["nom"], "k": k, "avant": da, "apres": db,
            "partis": {(autobus.ABRIS[da["sens"]], *da["abri"])}
            | ({(autobus.BANCS[da["sens"]], *ancien_banc)} if ancien_banc else set()),
            "arrives": {(autobus.ABRIS[db["sens"]], *db["abri"])}
            | ({(autobus.BANCS[db["sens"]], *nouveau_banc)} if nouveau_banc else set()),
        })
    for ls, la in zip(sans["autobus"]["lignes"], avec["autobus"]["lignes"]):
        assert {k: v for k, v in ls.items() if k != "arrets"} == {k: v for k, v in la.items() if k != "arrets"}, \
            f"la ligne {ls['numero']} a changé de tracé"
        assert la["arrets"] == [[id_, i + decalages.get(id_, 0)] for id_, i in ls["arrets"]], \
            f"la ligne {ls['numero']} : un arrêt n'est plus à sa place dans la boucle"
    return glisses


#: L'air d'un lieu de mission pour un abribus, écrit ici en toutes lettres : deux tuiles de côté
#: sans donneur (le devant de mission), trois pour un donneur, cinq pour deux, sept pour trois.
#: ⚠️ Pas relu dans `devants` : un juge qui relit la table qu'il juge ne rougit jamais.
AIR = {0: 2, 1: 3, 2: 5, 3: 7}


def _abribus_colles(ville: dict) -> list[str]:
    """Les arrêts dont l'abri ou le banc est dans l'air d'une porte de lieu de mission."""
    donneurs = Counter(p["ou"][6:] for p in missions.PERSONNAGES if p["ou"].startswith("porte:"))
    lieux = devants.lieux_de_mission(ville)
    portes = [p for p in ville["portes"] if p["lieu"] in lieux]
    colles = []
    for rang, arret in enumerate(ville["autobus"]["arrets"]):
        a = autobus.detail(ville, rang)
        for t in [tuple(a["abri"]), _banc(ville, rang)]:
            if t and any(1 <= t[1] - p["y"] <= 4 and abs(t[0] - p["x"]) <= AIR[donneurs[p["lieu"]]]
                         for p in portes):
                colles.append(arret["nom"])
                break
    return colles


@pytest.mark.parametrize("graine", GRAINES)
def test_aucun_abribus_ne_colle_la_porte_d_un_lieu_de_mission(graine):
    """Retour de Martin (22 sept. 2026, capture) : « trop de choses collé devant chez Ti-Paul,
    étale-les plus sur le pâté de maison ». La ligne 2 s'arrête devant le dépanneur, et son abribus
    prenait la place la plus proche de la porte : deux tuiles de côté, celle du donneur. Ti-Paul se
    rabattait entre l'édicule du métro et le guichet. Cinq arrêts étaient ainsi collés à un lieu de
    mission ; ils glissent le long de leur voie.

    ⚠️ Le terminus reste : son parvis (`autobus.PARVIS`) tient déjà son arrêt à distance du car de
    l'ouverture, et il n'a nulle part où glisser plus loin. Il est hors du devant de mission."""
    ville, temoin = _ville(graine), _ville(graine, deplace=False)
    restent = _abribus_colles(ville)
    assert all(nom.startswith("Terminus") for nom in restent), f"collés à un lieu de mission : {restent}"
    for nom in restent:
        rang = next(r for r, a in enumerate(ville["autobus"]["arrets"]) if a["nom"] == nom)
        assert ville["autobus"]["arrets"][rang] == temoin["autobus"]["arrets"][rang], f"{nom} a glissé à moitié"
        a = autobus.detail(ville, rang)
        assert not any(1 <= a["abri"][1] - p["y"] <= 4 and abs(a["abri"][0] - p["x"]) <= 2
                       for p in ville["portes"] if p["lieu"] == "terminus"), f"{nom} est devant le terminus"


@pytest.mark.parametrize("graine", GRAINES)
def test_le_temoin_a_bien_des_abribus_colles(graine):
    """Le juge du dessus ne vaut que si la ville SANS le glissement en avait : quatre au moins, sur
    chacune de ces graines (le dépanneur, le poste, le casse-croûte, l'hôpital)."""
    assert len([n for n in _abribus_colles(_ville(graine, deplace=False)) if not n.startswith("Terminus")]) >= 4


def test_devant_chez_ti_paul_l_arret_laisse_la_facade_aux_donneurs():
    """Le cas de la capture, sur la ville livrée : Ti-Paul et Xavier attendent au dépanneur, à deux
    et à quatre tuiles de la porte. L'abri et son banc se tiennent plus loin que six tuiles de côté —
    une tuile d'air après le second donneur —, sur le même trottoir, et l'arrêt porte encore le nom
    du dépanneur. Et ils ne se collent pas à un autre meuble : le premier glissement posait le banc
    contre un arbre du parc, et refaisait un peu plus loin le paquet qu'on défaisait."""
    ville = _ville(carte.GRAINE)
    porte = next(p for p in ville["portes"] if p["lieu"] == "depanneur")
    rang = next(r for r, a in enumerate(ville["autobus"]["arrets"]) if a["nom"] == "Dépanneur Chez Ti-Paul")
    a = autobus.detail(ville, rang)
    for t in (tuple(a["abri"]), _banc(ville, rang)):
        assert t[1] == porte["y"] + 1, f"{t} n'est plus sur la façade du dépanneur"
        assert abs(t[0] - porte["x"]) >= 6, f"{t} colle encore la porte du dépanneur ({porte['x']}, {porte['y']})"
    siens = {tuple(a["abri"]), _banc(ville, rang)}
    voisins = [d["type"] for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE and (d["x"], d["y"]) not in siens
               and any(max(abs(d["x"] - x), abs(d["y"] - y)) <= 1 for x, y in siens)]
    assert not voisins, f"l'arrêt du dépanneur se colle à {voisins}"


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
