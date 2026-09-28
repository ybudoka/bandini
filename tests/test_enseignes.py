"""Les enseignes qui ouvrent pour vrai, côté ville (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md) :
le bingo, le Rialto, la salle de quilles et le lave-auto ont chacun une porte, une pièce et un comptoir qui
sert ; la baie du lave-auto est sur la chaussée devant sa porte ; et les poser ne déplace rien d'autre."""

import pytest
import villes

from app import carte, devantures, enseignes, magasins, missions

#: ⚠️ LA VILLE D'AVANT (27 sept. 2026) : ces juges jugent la construction de la ville — ils la comparent à
#: elle-même sans un module, ou lisent ses quartiers par un `_Chantier` neuf, dans SON repère. La carte du jeu
#: a descendu de 110 rangées sous la bande nord (`app/nord.py`) : on la génère sans elle, `nord=False`.


@pytest.fixture(scope="module")
def VILLE():
    """La ville du jeu, exportée — prise dans `villes`, plus bâtie à la collecte."""
    return villes.exporter()


SLUGS = [f["slug"] for f in enseignes.ENSEIGNES]


@pytest.mark.parametrize("slug", SLUGS)
def test_chacune_a_sa_porte_son_enseigne_et_un_comptoir_qui_sert(VILLE, slug):
    fiche = next(f for f in enseignes.ENSEIGNES if f["slug"] == slug)
    portes = [p for p in VILLE["portes"] if p["lieu"] == slug]
    assert len(portes) == 1, f"{slug} : {len(portes)} portes"
    porte = portes[0]
    assert porte["interieur"] == slug and porte["nom"] in (fiche["texte"], fiche.get("court"))
    assert VILLE["sol"][porte["y"]][porte["x"]] == "D"
    devanture = next(d for d in VILLE["devantures"] if d["y"] == porte["y"] and d["x"] <= porte["x"] < d["x"] + d["l"])
    assert devanture["texte"] == porte["nom"], devanture
    assert devantures.tient_en(devanture["texte"], devanture["l"])
    piece = VILLE["interieurs"][slug]
    points = [q for q in piece["points"] if q["type"] == "emplettes"]
    assert points, f"{slug} : aucun comptoir"
    for q in points:
        comptoir = magasins.COMPTOIRS[q["genre"]]
        assert comptoir["articles"] and comptoir.get("enseigne"), q
    point = next(q for q in VILLE["points_interet"] if q["slug"] == slug)
    assert (point["x"], point["y"]) == (porte["x"], porte["y"] + 1) and point["famille"] in carte.FAMILLES_DE_LIEU


def test_le_bingo_est_celui_que_la_ville_affichait_et_pas_dans_une_rue_cossue(VILLE):
    """La ville peignait déjà « BINGO » sur une façade sans pièce derrière : c'est elle qui ouvre."""
    porte = next(p for p in VILLE["portes"] if p["lieu"] == "bingo")
    devanture = next(d for d in VILLE["devantures"] if d["y"] == porte["y"] and d["x"] <= porte["x"] < d["x"] + d["l"])
    assert devanture.get("standing") != "+", devanture


def test_chaque_comptoir_d_enseigne_fait_jouer_ou_propose_quelque_chose():
    """Le bingo vend une carte, le Rialto un billet, le lave-auto dit son lavage, les quilles proposent la
    ligue du mardi — un défi du catalogue, joué debout au comptoir."""
    jeux = {g: c.get("joue") for g, c in magasins.COMPTOIRS.items() if c.get("enseigne")}
    assert jeux == {"bingo": "bingo", "rialto": "film", "quilles": None, "lave_auto": "lave_auto"}, jeux
    defi = next(d for d in missions.DEFIS if d["slug"] == "quilles")
    assert magasins.COMPTOIRS["quilles"]["defi"] == "quilles" and defi["epreuve"] == "quilles" and defi["a_pied"]


def test_la_baie_du_lave_auto_est_sur_la_chaussee_devant_sa_porte(VILLE):
    b = VILLE["lave_auto"]
    porte = next(p for p in VILLE["portes"] if p["lieu"] == "lave_auto")
    assert b["x"] <= porte["x"] < b["x"] + b["l"] and 0 < b["y"] - porte["y"] <= 5, (b, porte)
    for y in range(b["y"], b["y"] + b["h"]):
        for x in range(b["x"], b["x"] + b["l"]):
            assert carte.LEGENDE[VILLE["sol"][y][x]].get("route"), f"la baie mord sur « {VILLE['sol'][y][x]} » en {x, y}"


def test_les_enseignes_ne_deplacent_rien_d_autre(VILLE, monkeypatch):
    """⚠️ Posées sur la ville FINIE et sans dé, comme le dojo : la même ville sans elles est identique, hors
    de leurs portes (la pièce, le lieu, le nom), de leurs enseignes, des pièces reprises et des points
    ajoutés au bout. Et elles ne mordent sur aucune porte qui avait un lieu à elle."""
    # ⚠️ Les CONCESSIONNAIRES se posent après et ajoutent leur point au bout : neutralisés des DEUX côtés.
    from app import concessionnaires
    monkeypatch.setattr(concessionnaires, "poser_le_salon", lambda chantier, ville: None)
    avec = carte.generer(graine=VILLE["graine"], nord=False)
    monkeypatch.setattr(enseignes, "poser", lambda chantier, ville: [])
    sans = carte.generer(graine=VILLE["graine"], nord=False)  # ⚠️ sous le patch : pas `villes`
    for cle in ("sol", "decor", "paquets", "ambulants", "reclames", "scenes", "nids_de_poule", "barrieres",
                "metro", "autobus", "chantiers", "residences", "graffitis", "lampes", "fermetures"):
        assert avec[cle] == sans[cle], f"les enseignes deplacent « {cle} »"
    reprises = {(p["x"], p["y"]) for p in avec["portes"] if p["lieu"] in SLUGS}
    assert len(reprises) == len(SLUGS)
    for pa, ps in zip(avec["portes"], sans["portes"], strict=True):
        if (pa["x"], pa["y"]) in reprises:
            assert ps["interieur"] not in carte.INTERIEURS and not ps["interieur"].startswith("logement"), ps
        else:
            assert pa == ps
    for da, ds in zip(avec["devantures"], sans["devantures"], strict=True):
        if not any(da["y"] == y and da["x"] <= x < da["x"] + da["l"] for x, y in reprises):
            assert da == ds
    assert avec["points_interet"][:len(sans["points_interet"]) - 1] == sans["points_interet"][:-1], \
        "les points de la ville ont bouge"
    assert {q["slug"] for q in avec["points_interet"]} - {q["slug"] for q in sans["points_interet"]} == set(SLUGS)
