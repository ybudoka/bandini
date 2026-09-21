"""Des garages où l'on entre : semer la police et repeindre (21 sept. 2026).

Demande de Martin : « il faut des portes de garage qu'on peut vraiment entrer. pour
permettre de semer la police en voiture. », puis « repeindre des voitures ».

Ici, la VILLE : les carrosseries posées sur la ville finie, le rideau, la baie sous le
toit où le char se cache, l'abord jusqu'à la rue, et ce que leur pose ne déplace pas.
Ce qui bouge (le seuil qui s'ouvre, le rideau qui tombe, le pistolet, la police qui
perd la trace) se juge au banc, dans `test_garages_ou_l_on_entre_js.py`.
"""

import pytest

from app import carte, devantures, devants, economie, vehicules

GRAINES = (carte.GRAINE, 1, 2, 7)


@pytest.fixture(scope="module", params=GRAINES)
def ville(request):
    return carte.generer(graine=request.param)


def _carrosseries(ville):
    return [p for p in ville["portes_garage"] if p.get("genre") == "carrosserie"]


def _roulable(sol, x, y):
    return carte.LEGENDE[sol[y][x]].get("solide", 0) == 0


def _district(ville, x, y):
    """Le district d'une tuile, relu dans les zones du paquet (pas dans le chantier)."""
    slugs = {d["slug"] for d in ville["districts"]}
    for z in ville["zones"]:
        if z.get("slug") in slugs and z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"]:
            return z["slug"]
    return None


def _abord(sol, x, y):
    """Les tuiles entre le rideau et la rue, colonne `x` : jusqu'a la premiere route."""
    tuiles = []
    for j in range(1, 8):
        fiche = carte.LEGENDE[sol[y + j][x]]
        if fiche.get("route") and not fiche.get("stationnement") and j > 1:
            return tuiles
        tuiles.append((x, y + j))
    return None


def test_une_carrosserie_par_district_et_toujours_au_faubourg(ville):
    """Une par district au plus, trois au moins dans la ville — et au Faubourg, ou
    l'on debarque : sans elle, la premiere poursuite de la partie n'a nulle part ou
    aller."""
    portes = _carrosseries(ville)
    assert len(portes) >= 3, f"{len(portes)} carrosseries : on ne seme la police nulle part"
    districts = [_district(ville, p["x"], p["y"]) for p in portes]
    assert len(set(districts)) == len(districts), f"deux carrosseries dans le meme district : {districts}"
    for p, d in zip(portes, districts):
        assert p["lieu"] == f"carrosserie_{d}", (p, d)
    assert "faubourg" in districts, districts
    # Le rideau de Ti-Guy reste le premier : des juges et le jeu le lisent la.
    assert ville["portes_garage"][0]["lieu"] == "garage"


def test_le_rideau_couvre_deux_tuiles_d_une_devanture_devenue_carrosserie(ville):
    sol = ville["sol"]
    for p in _carrosseries(ville):
        assert p["l"] == 2 and [sol[p["y"]][p["x"] + i] for i in range(2)] == ["G", "G"], p
        enseigne = next(d for d in ville["devantures"] if d["y"] == p["y"] and d["x"] <= p["x"] and p["x"] + 1 < d["x"] + d["l"])
        district = _district(ville, p["x"], p["y"])
        assert enseigne["texte"] == devantures.CARROSSERIES[district][0], enseigne
        assert enseigne["motifs"][p["x"] - enseigne["x"]:p["x"] - enseigne["x"] + 2] == "GG", enseigne
        # Pas de comptoir derriere : une porte qui s'ouvre sur un depanneur, sous une
        # enseigne de carrosserie, mentirait deux fois.
        assert not enseigne["porte"], enseigne
        assert enseigne.get("standing") != "+", f"une carrosserie dans un bloc cossu : {enseigne}"
        assert enseigne["genre"] == devantures.genre_index("industrie"), enseigne


def test_derriere_chaque_rideau_une_baie_sous_le_toit_ou_tient_l_autobus(ville):
    """La rangee du rideau et `baie` rangees de toit derriere : c'est la que le char se
    cache. Le plus long du parc doit y entrer tout entier, nez au mur du fond — sinon
    le rideau retombe sur son pare-chocs. Ti-Guy compris."""
    sol = ville["sol"]
    plus_long = max(v["longueur"] for v in vehicules.CATALOGUE if not v["eau"])
    for p in ville["portes_garage"]:
        assert p["baie"] >= 1, p
        assert (p["baie"] + 1) * carte.TUILE_PX >= plus_long, f"{p['lieu']} : {plus_long} px ne tiennent pas"
        for i in range(p["l"]):
            for k in range(1, p["baie"] + 1):
                glyphe = sol[p["y"] - k][p["x"] + i]
                assert carte.LEGENDE[glyphe].get("toit"), \
                    f"{p['lieu']} : « {glyphe} » en {p['x'] + i, p['y'] - k}, la baie n'est pas sous un toit"


def test_devant_chaque_rideau_du_roulable_jusqu_a_la_rue_et_rien_de_pose(ville):
    sol = ville["sol"]
    for p in _carrosseries(ville):
        abord = set()
        for i in range(p["l"]):
            tuiles = _abord(sol, p["x"] + i, p["y"])
            assert tuiles is not None and len(tuiles) <= carte._Chantier.CARROSSERIE_ABORD, \
                f"{p['lieu']} : pas de rue devant la colonne {p['x'] + i}"
            abord |= set(tuiles)
        for x, y in sorted(abord):
            assert _roulable(sol, x, y), f"{p['lieu']} : l'abord est bouche en {x, y}"
            assert sol[y][x] != "_", f"{p['lieu']} : l'abord n'est pas pave en {x, y}"
        poses = [(cle, q) for cle in ("decor", "paquets", "ambulants", "scenes", "reclames")
                 for q in ville[cle] if (q["x"], q["y"]) in abord]
        assert not poses, f"{p['lieu']} : pose entre le rideau et la rue : {poses}"


def test_chaque_carrosserie_est_un_point_des_services_sur_la_carte(ville):
    points = {q["slug"]: q for q in ville["points_interet"]}
    for p in _carrosseries(ville):
        q = points.get(p["lieu"])
        assert q, f"{p['lieu']} n'est pas sur la carte"
        assert q["famille"] == "service" and q["type"] == "carrosserie", q
        assert (q["x"], q["y"]) == (p["x"], p["y"] + 1), q
        assert q["nom"] == devantures.CARROSSERIES[_district(ville, p["x"], p["y"])][1]


def test_les_carrosseries_ne_deplacent_rien_d_autre(ville, monkeypatch):
    """⚠️ Posees EN DERNIER et sans de, comme le rideau de Ti-Guy : la meme ville sans
    elles est identique, hors de leur rideau et de leur abord (et du nom sur le bandeau).
    Le devant des portes (`devants.deplacer`) est neutralise des DEUX cotes : il vient
    apres, et ecarter ce qui tombe devant une porte neuve est son travail."""
    monkeypatch.setattr(devants, "deplacer", lambda chantier, ville_: {})
    avec = carte.generer(graine=ville["graine"])
    monkeypatch.setattr(carte._Chantier, "poser_les_carrosseries", lambda self, ville_: [])
    sans = carte.generer(graine=ville["graine"])
    for cle in ("paquets", "ambulants", "reclames", "scenes", "nids_de_poule", "barrieres",
                "metro", "autobus", "chantiers", "portes", "residences", "graffitis", "lampes"):
        assert avec[cle] == sans[cle], f"les carrosseries deplacent « {cle} »"
    portes = _carrosseries(avec)
    assert portes, "le juge compare deux villes sans carrosserie"
    touchees = set()
    for p in portes:
        for i in range(p["l"]):
            touchees.add((p["x"] + i, p["y"]))
            touchees |= {(p["x"] + i, p["y"] + j) for j in range(1, 12)}
    for y, (a, b) in enumerate(zip(avec["sol"], sans["sol"])):
        for x, (ga, gb) in enumerate(zip(a, b)):
            assert ga == gb or (x, y) in touchees, f"la tuile {x, y} a change : {gb} -> {ga}"
    assert [d for d in avec["decor"] if (d["x"], d["y"]) not in touchees] == \
           [d for d in sans["decor"] if (d["x"], d["y"]) not in touchees], "le decor a bouge hors des abords"
    assert avec["points_interet"][:len(sans["points_interet"])] == sans["points_interet"], \
        "les points de la ville ont bouge : on n'en AJOUTE qu'au bout"
    renommees = {(p["x"], p["y"]) for p in portes}
    for da, ds in zip(avec["devantures"], sans["devantures"]):
        if any(da["y"] == y and da["x"] <= x < da["x"] + da["l"] for x, y in renommees):
            # Le rideau prend deux tuiles de VITRINE ou de mur : jamais la porte peinte, ni
            # une condamnee, ni des planches. La porte peinte, elle, redevient son mur : le
            # rideau est la porte, et une peinte ne double jamais une vraie.
            for i, (ma, ms) in enumerate(zip(da["motifs"], ds["motifs"])):
                assert ma == ms or (ma == "G" and ms in "WF") or (ms == "P" and ma in "WF"), \
                    f"« {ds['texte']} » : {ds['motifs']} -> {da['motifs']}"
            assert "P" not in da["motifs"], f"« {da['texte']} » garde une porte peinte a cote du rideau"
            continue
        assert da == ds, f"une devanture qui n'est pas une carrosserie a change : {ds} -> {da}"


def test_la_peinture_coute_plus_cher_a_chaque_etoile_sauf_chez_ti_guy():
    """Cinq etoiles effacees pour le prix d'une peinture rendraient la police
    decorative : la carrosserie prend un supplement par etoile. Chez Ti-Guy, c'est prix
    de famille, et son menu garde la peinture tout court."""
    assert economie.prix_carrosserie(0) == economie.REPEINTE
    prix = [economie.prix_carrosserie(e) for e in range(6)]
    assert all(b > a for a, b in zip(prix, prix[1:])), prix
    assert economie.exporter()["carrosserie"] == economie.CARROSSERIE
    assert economie.exporter()["repeinte"] == economie.REPEINTE
