"""Le caddie qu'on fouille puis qu'on pousse, la plaque de rue et les panneaux drôles : le catalogue et la
place des panneaux (docs/jalons/le-decor-les-betes-et-les-gens-repondent.md, deuxième vague, 2 oct. 2026).

Le navigateur ne garde aucun de ces nombres : on les juge ici. Ce qui se joue au bouton est dans
`test_caddie_et_panneaux_js.py`.
"""

import json

import pytest

import villes

from app import collectionner, definitions, devants, interactions, missions, panneaux, recherche, saisons


# --- Le caddie --------------------------------------------------------------------------------------


def test_le_caddie_ne_rend_que_de_la_monnaie_et_des_objets_droles():
    """Martin : « pas une carte de hockey ni une bebelle, qui ont leurs places ». La table ne tire que la
    monnaie et les canettes des bacs, ou un objet drôle qu'on laisse là."""
    c, f = interactions.CADDIE, interactions.FOUILLER
    tirees = {s for _, s in c["table"]}
    assert tirees == {"monnaie", "canettes", "drole"}
    assert all(isinstance(p, int) and p > 0 for p, _ in c["table"])
    assert all(s in f["trouvailles"] for s in tirees - {"drole"})
    # Aucun objet drôle ne porte le nom d'une pièce de collection : il se lit, il ne se range nulle part.
    noms = {b["nom"].upper() for fam in ("CARTES", "BEBELLES") for b in getattr(collectionner, fam, ())}
    assert c["droles"] and not any(n and n in d for d in c["droles"] for n in noms)
    # De la monnaie, pas un salaire : l'espérance d'une fouille de caddie reste celle d'un bac.
    total = sum(p for p, _ in c["table"])
    esperance = sum(p / total * sum(f["trouvailles"][s]["argent"]) / 2 for p, s in c["table"] if s != "drole")
    assert esperance <= 2.0
    assert c["debout"] != c["decors"][0]


def test_le_belier_tient_meme_au_sprint_dans_la_neige():
    """Seul un SPRINT le lance en bélier (`Caddies` lit `j.sprinte`) ; et ce sprint-là, l'hiver sans bottes
    (`saisons.JOUEUR["neige"]`), doit encore aller plus vite que `belier` — sinon, de janvier à mars, il ne
    bousculerait plus personne."""
    c, v = interactions.CADDIE, recherche.VITESSES
    assert c["belier"] < v["joueur_sprint"] * saisons.JOUEUR["neige"] * c["pousse_x"]
    assert c["pousse_x"] > 1, "poussé, il part devant : sinon on marcherait dans lui"
    assert c["belier"] < c["vitesse_max"]
    assert 0.9 < c["frottement"] < 1 and 0 <= c["rebond"] < 1
    # Ce qu'il fait à un char : de la tôle, pas une épave — un char en a cent fois plus.
    assert 0 < c["degats_char"] <= 5


# --- Les panneaux drôles -----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ville():
    return villes.exporter()


@pytest.fixture(scope="module")
def poses(ville):
    return panneaux.placer(ville)


def test_un_ou_deux_panneaux_par_district_et_tous_poses(poses):
    """Un ou deux par district habité — la baie n'est que de l'eau —, et aucun ne reste sans place."""
    par_district: dict[str, int] = {}
    for p in panneaux.PANNEAUX:
        par_district[p["district"]] = par_district.get(p["district"], 0) + 1
    assert set(par_district) == {"faubourg", "erables", "shop", "quais", "pointe", "canton", "friches", "gare"}
    assert all(1 <= n <= 2 for n in par_district.values()), par_district
    assert len(poses) == len(panneaux.PANNEAUX), "un panneau n'a pas trouvé de place"
    assert all(p["genre"] in panneaux.GENRES for p in panneaux.PANNEAUX)
    for p in panneaux.PANNEAUX:
        assert 2 <= len(p["lignes"]) <= 3, "une blague de panneau : un fait, puis la chute"
        assert all(ligne == ligne.upper() and ligne.strip() == ligne and ligne for ligne in p["lignes"])


def test_un_panneau_se_plante_au_bord_du_trottoir_loin_des_portes_et_du_decor(ville, poses):
    """Sur l'abord (ou l'herbe), contre un trottoir, dans son district et hors d'un territoire de gang ;
    jamais devant une porte, au coin d'un croisement, ni collé à un décor."""
    sol, decor = ville["sol"], {(d["x"], d["y"]) for d in ville["decor"]}
    portes = set(devants.portes(ville))
    zones = {z["slug"]: z for z in ville["zones"] if not z.get("gang")}
    gangs = [z for z in ville["zones"] if z.get("gang")]
    catalogue = {tuple(p["lignes"]): p for p in panneaux.PANNEAUX}
    for p in poses:
        x, y = p["x"], p["y"]
        z = zones[catalogue[tuple(p["lignes"])]["district"]]
        assert z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"], f"{p['lignes'][0]} hors de son district"
        assert sol[y][x] in panneaux.SOLS
        assert any(sol[y + dy][x + dx] == "." for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), "loin du trottoir"
        assert not any(g["x"] <= x < g["x"] + g["l"] and g["y"] <= y < g["y"] + g["h"] for g in gangs)
        r = panneaux.LOIN_DES_PORTES
        assert not any((x + dx, y + dy) in portes for dx in range(-r, r + 1) for dy in range(-r, r + 1)), "devant une porte"
        assert not any((x + dx, y + dy) in decor for dx in (-1, 0, 1) for dy in (-1, 0, 1)), "collé à un décor"
        for i in ville["intersections"]:
            assert not (i["x"] - 3 <= x < i["x"] + i["l"] + 3 and i["y"] - 3 <= y < i["y"] + i["h"] + 3), "au coin d'une rue"
    # Deux panneaux d'un même district ne se lisent pas l'un pour l'autre.
    for a in poses:
        for b in poses:
            if a is not b and catalogue[tuple(a["lignes"])]["district"] == catalogue[tuple(b["lignes"])]["district"]:
                assert max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"])) >= panneaux.ECART_TUILES


def test_les_panneaux_ne_touchent_pas_la_ville(ville, poses):
    """Sans dé, et sans rien ajouter à la carte : la même ville rend les mêmes places, et ni le décor ni
    la carte n'en savent rien — ils voyagent dans la SUITE du paquet."""
    assert panneaux.placer(villes.exporter()) == poses
    assert all(d["type"] not in ("panneau_drole", "panneau") for d in ville["decor"])
    assert "panneaux" in definitions.DANS_LA_SUITE
    exporte = panneaux.pour_le_navigateur(ville)
    assert json.loads(json.dumps(exporte)) == exporte
    assert [[x, y, panneaux.GENRES[g], lignes] for x, y, g, lignes in exporte] == \
        [[p["x"], p["y"], p["genre"], p["lignes"]] for p in poses]


def test_un_panneau_ne_ment_pas_sur_la_ville():
    """Ce qu'un panneau nomme existe : l'usine Prévost, le Dragon d'or, l'école La Mante, Sal."""
    textes = " ".join(ligne for p in panneaux.PANNEAUX for ligne in p["lignes"])
    noms = " ".join(p["nom"].upper() for p in missions.PERSONNAGES)
    assert "SAL" in noms and "PRÉVOST" in json.dumps(villes.exporter()["autobus"], ensure_ascii=False).upper()
    for mot in ("PRÉVOST", "DRAGON D’OR", "LA MANTE", "SAL"):
        assert mot in textes
