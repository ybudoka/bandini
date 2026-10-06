"""Les cartes de hockey (P4, des choses à collectionner, vague 1) : où elles dorment, ce qu'elles disent, ce
qu'elles pèsent — et la ville qui ne bouge pas d'un octet quand on les pose.

⚠️ Les règles sont écrites ICI en toutes lettres (le recoin, l'encaissement, l'écart, le chemin depuis la
planque) : un juge qui relirait `collectionner.RECOINS` changerait avec la constante qu'il garde.
"""

import gzip
import json
from collections import deque

import pytest

from app import carte, collectionner, nord

TERRES = ("faubourg", "erables", "shop", "quais", "pointe", "friches", "canton", "gare")


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def _district(ville, slug):
    return next(z for z in ville["zones"] if z["slug"] == slug and not z.get("gang"))


def _dans(r, x, y):
    return r["x"] <= x < r["x"] + r["l"] and r["y"] <= y < r["y"] + r["h"]


def test_quarante_cartes_cinq_par_district_des_numeros_qui_ne_bougent_pas():
    assert [c["numero"] for c in collectionner.CARTES] == list(range(1, 41))
    for d in TERRES:
        assert sum(1 for c in collectionner.CARTES if c["district"] == d) == 5, d
    assert set(collectionner.EQUIPES) == set(TERRES)
    # ⚠️ Des NUMÉROS qui sont des noms : la sauvegarde et le marché aux puces y tiennent.
    assert collectionner.CARTES[0]["nom"] == "GILLES « LA TOQUE » BOUCHARD"
    assert collectionner.CARTES[11]["nom"] == "GASTON OUELLET"


def test_une_carte_se_lit_dans_une_ligne_du_carnet():
    for c in collectionner.CARTES:
        assert c["position"] in collectionner.POSITIONS, c
        assert 1 <= len(c["dos"]) <= 2, c
        assert len(c["nom"]) <= 34, f"n° {c['numero']} : un nom trop long pour sa ligne ({len(c['nom'])})"
        for ligne in c["dos"]:
            assert len(ligne) <= 44 and ligne == ligne.upper(), f"n° {c['numero']} : « {ligne} »"


def test_les_paliers_finissent_a_l_album_complet():
    paliers = {int(k): v for k, v in collectionner.REGLE["paliers"].items()}
    assert max(paliers) == len(collectionner.CARTES), "le dernier palier n'est pas l'album complet"
    # Moins que les paquets cachés (50 $, 500 $ à dix, 1 500 $ aux vingt) : un album, pas une paie.
    assert collectionner.REGLE["prime"] <= 50 and max(paliers.values()) <= 1500


def test_chaque_carte_dort_dans_un_recoin_de_son_district(ville):
    sol = ville["sol"]
    places = ville["collections"]["cartes"]
    assert sorted(p["numero"] for p in places) == list(range(1, 41))
    fiches = {c["numero"]: c for c in collectionner.CARTES}
    pris = {(o["x"], o["y"]) for cle in ("decor", "paquets", "scenes", "ambulants", "reclames", "points_interet")
            for o in ville.get(cle) or []}
    cours = [z for z in ville["zones"] if z.get("gang")]
    for p in places:
        x, y = p["x"], p["y"]
        assert _dans(_district(ville, fiches[p["numero"]]["district"]), x, y), f"n° {p['numero']} hors de son district"
        # Une ruelle, une friche, de l'herbe ou un quai — jamais la rue, le trottoir ou la plage.
        assert sol[y][x] in "x;,Q", f"n° {p['numero']} sur « {sol[y][x]} »"
        assert (x, y) not in pris, f"n° {p['numero']} sur un décor, un paquet ou un lieu"
        # Jamais sur le pas d'une porte — la vraie, la condamnée, le garage : deux tuiles sous elle.
        assert not any(sol[y - k][x + dx] in "DdG" for k in (1, 2) for dx in (-1, 0, 1)), \
            f"n° {p['numero']} sur le pas d'une porte"
        assert not any(_dans(c, x, y) for c in cours), f"n° {p['numero']} dans une cour de gang"
        # Un RECOIN : trois murs au moins parmi ses huit voisines.
        murs = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dx or dy) and not carte.marchable(sol[y + dy][x + dx]))
        assert murs >= 3, f"n° {p['numero']} ({x},{y}) en terrain découvert ({murs} murs)"


def test_deux_trouvailles_jamais_collees(ville):
    places = ville["collections"]["cartes"]
    for i, a in enumerate(places):
        for b in places[i + 1:]:
            assert max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"])) >= 10, (a, b)
        for q in ville["paquets"] + ville["frenesies"]:
            assert max(abs(a["x"] - q["x"]), abs(a["y"] - q["y"])) >= 6, f"n° {a['numero']} collée à {q}"


def test_chaque_carte_se_rejoint_a_pied_depuis_la_planque_toutes_barrieres_fermees(ville):
    """Le pire cas du juge des barrières : une carte n'attend ni une mission ni une heure."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    murs = set()
    for b in ville["barrieres"]:
        if "pieton" in b["arrete"] and not b["existant"]:
            for y in range(b["y"], b["y"] + b["h"]):
                for x in range(b["x"], b["x"] + b["l"]):
                    if x in (b["x"], b["x"] + b["l"] - 1) or y in (b["y"], b["y"] + b["h"] - 1):
                        murs.add((x, y))
    planque = next(p for p in ville["points_interet"] if p["slug"] == "planque")
    vus, file = {(planque["x"], planque["y"])}, deque([(planque["x"], planque["y"])])
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < L and 0 <= ny < H and (nx, ny) not in vus and (nx, ny) not in murs \
                    and carte.marchable(sol[ny][nx]):
                vus.add((nx, ny))
                file.append((nx, ny))
    for p in ville["collections"]["cartes"]:
        assert (p["x"], p["y"]) in vus, f"n° {p['numero']} ({p['x']},{p['y']}) ne se rejoint pas à pied"


def test_un_recoin_emmure_n_est_plus_choisi(ville):
    """⚠️ La carte livrée se rejoint déjà : on l'emmure (des murs autour, sur une copie du sol) — elle part."""
    p = next(q for q in ville["collections"]["cartes"] if q["numero"] == 1)
    sol = [list(r) for r in ville["sol"]]
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy:
                sol[p["y"] + dy][p["x"] + dx] = "B"
    v = dict(ville, sol=["".join(r) for r in sol])
    autre = next(q for q in collectionner.poser(v)["cartes"] if q["numero"] == 1)
    assert (autre["x"], autre["y"]) != (p["x"], p["y"]), "un recoin emmuré garde sa carte"


def test_la_pose_ne_tire_aucun_de_et_se_refait_a_l_identique(ville):
    v = json.loads(json.dumps({k: val for k, val in ville.items() if k != "collections"}))
    assert collectionner.poser(v) == collectionner.poser(json.loads(json.dumps(v))) == ville["collections"]


def test_les_cartes_ne_deplacent_rien(monkeypatch):
    """Posées en tout dernier et sans un dé : la ville avec elles est la ville sans elles, à l'octet."""
    vu = {}
    vraie = collectionner.poser

    def espion(v):
        vu["avant"] = json.dumps(v, sort_keys=True)
        out = vraie(v)
        vu["apres"] = json.dumps(v, sort_keys=True)
        return out

    monkeypatch.setattr(collectionner, "poser", espion)
    v = carte.generer()
    # ⚠️ Des booléens, pas deux chaînes de plusieurs Mo : pytest en calculerait le diff pendant des minutes.
    avant, apres = json.loads(vu["avant"]), json.loads(vu["apres"])
    touchees = sorted(k for k in set(avant) | set(apres) if avant.get(k) != apres.get(k))
    assert not touchees, f"poser les cartes a touché la ville : {touchees}"
    # ⚠️ Sauf la RÉGATE (i07, 1er oct. 2026), posée après elles : ses bouées sur l'eau autour de l'île, sa propre clé, et
    # rien d'autre ne change (`test_regate::test_la_ville_d_avant_est_la_meme_cle_par_cle`).
    sans = {k: val for k, val in v.items() if k not in ("collections", "regate")}
    derniere = json.dumps(sans, sort_keys=True) == vu["avant"]
    assert derniere, "les cartes ne se posent pas en dernier"


def test_la_ville_d_avant_la_bande_nord_n_en_a_que_vingt_cinq():
    avant = carte.generer(nord=False)
    districts = {c["numero"]: c["district"] for c in collectionner.CARTES}
    assert sorted({districts[p["numero"]] for p in avant["collections"]["cartes"]}) == \
        sorted(set(TERRES) - {"friches", "canton", "gare"})
    assert len(avant["collections"]["cartes"]) == 25


def test_la_bande_nord_sait_les_decaler():
    assert "collections" in nord.DECALAGES


def test_elles_voyagent_a_part_hors_de_la_carte_et_des_definitions(paquets, client):
    defs = json.loads(paquets.definitions.corps)
    ville = json.loads(paquets.carte.corps)
    col = json.loads(paquets.collections.corps)
    assert "collections" not in ville, "les places des cartes pèsent sur la carte"
    assert defs["collections_empreinte"] == col["empreinte"] == paquets.collections.etag
    assert len(col["cartes"]["liste"]) == 40 and all("x" in c for c in col["cartes"]["liste"])
    r = client.get("/api/collections")
    assert r.status_code == 200 and r.headers["ETag"].strip('"') == paquets.collections.etag
    assert client.get("/api/collections", headers={"If-None-Match": r.headers["ETag"]}).status_code == 304
    # Leur plafond à elles : 8 249 bruts / 3 218 gzip à la mesure, sons compris (30 sept. 2026) ; puis 10 050 / 3 822
    # avec le catalogue de la planque qu'on décore (vague 2) ; 14 354 / 5 429 avec les douze bebelles, leurs dessins et
    # leurs places (vague 3). Relevé à 18 000 / 7 000 pour les sauts (vague 4) : ce paquet-ci arrive en arrière-plan,
    # après les définitions, et n'attend personne — c'est le plafond du dépôt, pas celui du premier écran.
    # Puis 16 987 / 5 964 avec les sauts (vague 4), et 17 872 / 6 348 avec le marché aux puces : relevé à 22 000 / 8 000.
    # Puis 23 947 / 8 533 avec les douze enseignes (vague 5 : leurs emblèmes, leurs lignes, leurs places — 3 790 / 1 430
    # à elles seules) : relevé à 26 000 / 9 500 (1er oct. 2026). Puis 26 336 avec le propriétaire qui sort (vague 6 :
    # qui sort de chaque commerce, ses huit répliques et ses deux séries de voix — 1,1 Ko) : relevé à 27 000 bruts.
    # Puis 28 002 avec la planque des comptoirs (6 oct. 2026, docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-
    # l-enseigne.md : le portrait, la pièce d'en arrière et ses six meubles, les étagères des collections — 9 769 gzip) :
    # relevé à 30 000 bruts et 11 000 gzip.
    assert paquets.collections.taille < 30_000
    assert len(gzip.compress(paquets.collections.corps, 6)) < 11_000


def test_leurs_sons_voyagent_avec_elles_pas_dans_les_definitions(paquets):
    """⚠️ Les définitions étaient au ras de leur plafond : les deux bruitages des cartes et leur lieu partent avec
    le catalogue (`audio.LIEUX_A_PART`), et le navigateur les remet au paquet à l'arrivée (`Son.Lieu.declarer`)."""
    defs = json.loads(paquets.definitions.corps)
    col = json.loads(paquets.collections.corps)
    slugs = {e["slug"] for e in defs["audio"]["echantillons"]}
    sons = ["carte_hockey", "orgue_arena", "bebelle", "reel_bebelles", "saut_reussi", "devisser"]
    assert not slugs & set(sons) and "collections" not in defs["audio"]["lieux"]
    assert col["sons"]["lieu"] == "collections"
    assert [e["slug"] for e in col["sons"]["echantillons"]] == sons
    assert all(e["fichiers"] for e in col["sons"]["echantillons"]), "un son des cartes sans son fichier"
