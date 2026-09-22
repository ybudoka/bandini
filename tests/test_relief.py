"""Les montagnes et les falaises : la carte a une limite, et elle se voit.

⚠️ Deux promesses, comme l'aéroport avant lui :

- **la ville d'avant (aéroport compris) ne bouge pas** — le relief se pose en
  tout dernier, sans un dé ; la seule exception est l'eau du large, au sud de
  l'aéroport, que la ligne de falaises recouvre EXPRÈS ;
- **le relief est infranchissable partout où il se trouve** — solidité 1,
  comme une façade : ni à pied, ni en char, ni à la nage.
"""

from __future__ import annotations

import pytest

from app import carte, relief


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


@pytest.fixture(scope="module")
def sans(ville):
    """La même ville, le relief jamais posé."""
    pose = relief.poser
    relief.poser = lambda chantier, v: {"montagnes": None}
    try:
        return carte.generer()
    finally:
        relief.poser = pose


def test_la_ville_d_avant_ne_bouge_pas(ville, sans):
    """Tuile pour tuile, la carte d'hier (aéroport compris) est la même — sauf
    l'eau du large, au sud de l'aéroport, que les falaises recouvrent. Et tout
    ce que le relief ajoute s'ajoute AU BOUT des rangées : rien d'autre ne
    bouge, pas même un arbre de rue."""
    assert ville["hauteur"] == sans["hauteur"]
    assert ville["largeur"] > sans["largeur"]
    largeur_avant = sans["largeur"]
    carte_h = ville["aeroport"]["masque"]["carte_h"]
    for y in range(sans["hauteur"]):
        for x in range(largeur_avant):
            if ville["sol"][y][x] == sans["sol"][y][x]:
                continue
            assert y >= carte_h and sans["sol"][y][x] == "~" and ville["sol"][y][x] in ("M", "C"), \
                (x, y, sans["sol"][y][x], ville["sol"][y][x])
    assert [ligne[:largeur_avant] for ligne in ville["voie"][:sans["hauteur"]]] == sans["voie"], \
        "le champ de direction a bougé"
    for cle in sans:
        if cle in ("sol", "voie", "largeur", "relief"):
            continue
        assert ville[cle] == sans[cle], f"« {cle} » a bougé"


def test_la_chaine_de_montagnes_est_a_l_est_et_infranchissable(ville):
    """Des colonnes ajoutées après la dernière rue, sur toute la hauteur de la
    carte — une paroi de falaise côté ville, du rocher plein derrière."""
    m = ville["relief"]["montagnes"]
    assert m["x"] == ville["largeur"] - m["l"] and m["l"] == relief.LARGEUR_MONTAGNES
    assert (m["y"], m["h"]) == (0, ville["hauteur"])
    for y in range(m["y"], m["y"] + m["h"]):
        for x in range(m["x"], m["x"] + m["l"]):
            g = ville["sol"][y][x]
            assert g in ("M", "C"), (x, y, g)
            assert carte.solidite(g) == 1, (x, y, g)
        # La première colonne — celle qu'on voit en arrivant de la ville — est
        # toujours la falaise, jamais un rocher plein tout seul.
        assert ville["sol"][y][m["x"]] == "C", y


def test_la_chaine_ne_touche_aucun_batiment(ville):
    """⚠️ `_empreinte` (`test_carte.py`, « une pièce plus grande que sa maison »)
    fait la crue de tout ce qui est solide == 1 et connecté : si la montagne
    touchait le mur d'un bâtiment, un juge très éloigné en hériterait sans
    qu'on comprenne pourquoi. La rue qui longe le bord est de la trame doit
    rester entre les deux — le relief peut en revanche toucher LE RELIEF (la
    ligne de falaises du sud rejoint la chaîne de l'est, au coin sud-est)."""
    batiments = {g for g, p in carte.LEGENDE.items() if p.get("solide") == 1 and g not in ("M", "C")}
    m = ville["relief"]["montagnes"]
    for y in range(m["y"], m["y"] + m["h"]):
        voisine = ville["sol"][y][m["x"] - 1]
        assert voisine not in batiments, (y, voisine)


def test_les_falaises_du_large_ne_recouvrent_que_de_l_eau(ville, sans):
    """Colonne par colonne, la bande sud ne mord jamais sur l'aéroport, sa
    clôture ou sa grève : tout ce qui est devenu `M`/`C` sous la ligne d'eau du
    large était de l'eau dans la ville SANS relief — jamais autre chose."""
    carte_h = ville["aeroport"]["masque"]["carte_h"]
    for y in range(carte_h, ville["hauteur"]):
        for x in range(sans["largeur"]):
            if ville["sol"][y][x] in ("M", "C"):
                assert sans["sol"][y][x] == "~", (x, y, sans["sol"][y][x])


def test_sans_aeroport_pas_de_falaises_du_large():
    """Sans aéroport, il n'y a pas de « large » à border : `poser` grandit
    quand même la ville à l'est (le mur du bord de carte existe toujours),
    mais ne touche pas une seule tuile d'eau au sud."""
    class Chantier:
        def __init__(self, largeur: int, hauteur: int) -> None:
            self.largeur, self.hauteur = largeur, hauteur
            self.sol = [["~"] * largeur for _ in range(hauteur)]
            self.voie = [["."] * largeur for _ in range(hauteur)]
            self.bouchon = [["B"] * largeur for _ in range(hauteur)]

    chantier = Chantier(40, 40)
    ville = {"largeur": 40, "hauteur": 40, "sol": ["~" * 40] * 40, "voie": ["." * 40] * 40, "aeroport": None}
    fiche = relief.poser(chantier, ville)
    assert fiche["montagnes"] is not None
    for y in range(chantier.hauteur):
        for x in range(fiche["montagnes"]["x"]):
            assert ville["sol"][y][x] == "~", (x, y, "le sud a bougé sans aéroport")


def test_deterministe():
    a, b = carte.generer(), carte.generer()
    assert a["relief"] == b["relief"]
    assert a["sol"] == b["sol"]
