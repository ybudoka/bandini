"""La patinoire du parc (P4, docs/jalons/la-patinoire-du-parc.md) : sa place au parc du Faubourg, et ce
qu'elle ne déplace pas.

⚠️ Les règles sont écrites ICI en toutes lettres (le parc du Faubourg, le gazon et l'allée, les portes sur
une allée, la ville d'à côté inchangée) : un juge qui relirait `patinoire.poser` changerait avec lui.
"""

import json

import pytest

from app import carte, patinoire
from tests import villes

#: Les couches qui prennent une tuile, et que la glace ne doit pas couvrir.
COUCHES = ("decor", "paquets", "scenes", "ambulants", "reclames", "points_interet")


@pytest.fixture(scope="module")
def avant_apres():
    """La ville du jeu, avec sa patinoire, et la même sans (`poser` rend None sans rien toucher) — bande nord
    comprise : les icônes, les cartes et le marché aux puces s'y placent APRÈS elle, sur la ville finie.
    ⚠️ La ville sans est générée ici, pas dans `villes` : le cache ne sait rien d'un patch."""
    avec = villes.generer()
    garde = patinoire.poser
    patinoire.poser = lambda chantier, ville: None
    try:
        sans = carte.generer()
    finally:
        patinoire.poser = garde
    return avec, sans


def test_la_patinoire_est_au_parc_du_faubourg_sur_le_gazon(avant_apres):
    ville, _ = avant_apres
    p = ville["patinoire"]
    assert p, "pas de patinoire"
    assert p["l"] >= 12 and p["h"] >= 4, f"une patinoire de {p['l']} × {p['h']} tuiles : trop petite pour patiner"
    tuiles = [(x, y) for y in range(p["y"], p["y"] + p["h"]) for x in range(p["x"], p["x"] + p["l"])]
    sols = {ville["sol"][y][x] for x, y in tuiles}
    assert sols <= {",", "g"}, f"la glace se pose sur autre chose que du gazon ou une allée : {sols}"
    districts = {z["district"] for z in ville["zones"]
                 if z["x"] <= p["x"] < z["x"] + z["l"] and z["y"] <= p["y"] < z["y"] + z["h"]}
    assert "faubourg" in districts, f"la patinoire n'est pas au Faubourg : {districts}"


def test_rien_sur_la_glace_ni_contre_ses_bandes(avant_apres):
    """Ni un arbre, ni un banc, ni un paquet sur la glace — ni collé contre une bande : on fait le tour."""
    ville, _ = avant_apres
    p = ville["patinoire"]
    x0, y0, x1, y1 = p["x"] - 1, p["y"] - 1, p["x"] + p["l"], p["y"] + p["h"]
    dessus = [(c, o.get("type"), o["x"], o["y"]) for c in COUCHES for o in ville.get(c) or []
              if x0 <= o["x"] <= x1 and y0 <= o["y"] <= y1
              and ville["sol"][o["y"]][o["x"]] in (",", "g")]
    assert dessus == [], f"sur la glace ou contre ses bandes : {dessus}"


def test_ses_portes_ouvrent_sur_une_allee(avant_apres):
    """On entre à pied par une porte des bandes, et une porte donne sur un chemin : une allée du parc ou le
    trottoir — jamais dans un buisson."""
    ville, _ = avant_apres
    p = ville["patinoire"]
    assert 1 <= len(p["portes"]) <= 2
    pas = {"nord": (0, -1), "sud": (0, 1), "ouest": (-1, 0), "est": (1, 0)}
    for porte in p["portes"]:
        dx, dy = pas[porte["cote"]]
        assert ville["sol"][porte["y"] + dy][porte["x"] + dx] in ("g", "."), porte
    assert any(ville["sol"][q["y"] + pas[q["cote"]][1]][q["x"] + pas[q["cote"]][0]] == "g" for q in p["portes"]), \
        "aucune porte sur une allée du parc"


def test_la_ville_est_la_meme_hors_de_la_clairiere(avant_apres):
    """Aucune tuile ne change, aucun dé n'est tiré : chaque clé de la ville est la même avec et sans la
    patinoire, sauf le décor DÉPLACÉ — même nombre, même ordre, mêmes sortes ; seules bougent les places
    de ce qui était sur la clairière, et chacun reste dans le parc, sur le gazon, à portée."""
    avec, sans = avant_apres
    for cle in sorted(set(avec) | set(sans)):
        if cle in ("decor", "patinoire"):
            continue
        assert json.dumps(avec.get(cle), sort_keys=True) == json.dumps(sans.get(cle), sort_keys=True), \
            f"la patinoire a changé « {cle} »"
    assert [d["type"] for d in avec["decor"]] == [d["type"] for d in sans["decor"]], \
        "un décor a été retiré ou ajouté : tout ce qui le suit change de numéro"
    p = avec["patinoire"]
    bouges = [(a, b) for a, b in zip(avec["decor"], sans["decor"]) if (a["x"], a["y"]) != (b["x"], b["y"])]
    assert len(bouges) == p["deplaces"] and bouges, f"{len(bouges)} décors bougés pour {p['deplaces']} annoncés"
    for a, b in bouges:
        assert p["x"] - 1 <= b["x"] <= p["x"] + p["l"] and p["y"] - 1 <= b["y"] <= p["y"] + p["h"], \
            f"le {b['type']} de ({b['x']}, {b['y']}) n'était pas sur la clairière, et il a bougé"
        assert avec["sol"][a["y"]][a["x"]] == ",", f"le {a['type']} déplacé n'est plus sur le gazon"
        assert max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"])) <= patinoire.PORTEE


def test_elle_descend_avec_la_ville_sous_la_bande_nord():
    """La bande nord fait descendre la ville de `decalage_nord` rangées : la patinoire la suit, portes
    comprises, et reste sur son gazon."""
    ville = villes.generer()
    p, n = ville["patinoire"], ville["decalage_nord"]
    avant = villes.generer(nord=False)["patinoire"]
    assert (p["x"], p["y"] - n, p["l"], p["h"]) == (avant["x"], avant["y"], avant["l"], avant["h"])
    assert [(q["x"], q["y"] - n) for q in p["portes"]] == [(q["x"], q["y"]) for q in avant["portes"]]
    assert ville["sol"][p["y"] + 1][p["x"] + 1] in (",", "g")


def test_la_fiche_du_navigateur():
    f = patinoire.pour_le_navigateur()
    for sorte in ("joueur", "pieton"):
        g = f["glisse"][sorte]
        assert 0 < g["freinage"] < g["elan"] < 0.2, f"la glisse du {sorte} ne glisse pas : {g}"
    assert f["chute"]["images_au_sol"] > 0
