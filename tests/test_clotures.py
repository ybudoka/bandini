"""Des terrains vraiment clôturés (vague 2 de docs/jalons/des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md) :
une clôture ne tombe que sur l'herbe d'une cour, sa matière suit le standing, rien d'autre ne bouge, et chaque porte
de logement reste rejoignable à pied depuis la rue (le portail est ouvert devant elle)."""

from collections import deque

import pytest

from app import carte, clotures


@pytest.fixture(scope="module")
def deux_villes():
    avec = carte.generer()
    garde = clotures.poser
    clotures.poser = lambda ville: []
    try:
        sans = carte.generer()
    finally:
        clotures.poser = garde
    return avec, sans


def test_une_cloture_ne_tombe_que_sur_l_herbe_d_une_cour_et_rien_d_autre_ne_bouge(deux_villes):
    avec, sans = deux_villes
    changees = [(x, y, a, b) for y, (ra, rb) in enumerate(zip(avec["sol"], sans["sol"]))
                for x, (a, b) in enumerate(zip(ra, rb)) if a != b]
    assert len(changees) >= 500, f"presque aucune clôture : {len(changees)}"
    for x, y, a, b in changees:
        assert a in clotures.CLOTURE.values() and b in clotures.COUR, (x, y, a, b)
    # ⚠️ Sauf ce qui se pose APRÈS elles et lit la ville clôturée : les frénésies et les cartes de hockey choisissent
    # leurs recoins sur elle (une cour fermée n'est plus un recoin de la rue).
    for cle in avec:
        if cle not in ("sol", "frenesies", "collections"):
            assert avec[cle] == sans[cle], f"les clôtures déplacent « {cle} »"
    decor = {(d["x"], d["y"]) for d in avec["decor"]}
    assert not [c for c in changees if (c[0], c[1]) in decor], "une clôture sur un décor"


def test_la_cloture_suit_le_standing(deux_villes):
    avec, sans = deux_villes
    faux = []
    for r in avec["residences"]:
        # ⚠️ La table ATTENDUE, écrite ici : lue dans le module, le juge ne verrait pas qu'on la change. Le bois
        # seulement en banlieue (les Érables) ; ailleurs, l'ordinaire a la grille de fer.
        banlieue = any(z.get("district") == "erables" and z["x"] <= r["x"] < z["x"] + z["l"] and z["y"] <= r["y"] < z["y"] + z["h"]
                       for z in avec["zones"])
        g = ({"+": "(", "=": "w", "-": "f"} if banlieue else {"+": "(", "=": "(", "-": "f"})[r.get("standing") or "="]
        for x in range(r["x"], r["x"] + r["l"]):
            for yy in range(r["y"] + 1, min(r["y"] + 8, len(avec["sol"]))):
                a = avec["sol"][yy][x]
                if a != sans["sol"][yy][x] and a != g:
                    # Une clôture d'un voisin peut longer ce terrain : seulement la sienne, droit devant la façade.
                    if not any(q is not r and q["x"] - 5 <= x < q["x"] + q["l"] + 5 and abs(q["y"] - r["y"]) <= 1
                               for q in avec["residences"]):
                        faux.append((x, yy, a, g))
    assert not faux, faux[:5]


def _portes_enfermees(ville):
    sol, legende = ville["sol"], carte.LEGENDE
    h, w = len(sol), len(sol[0])

    def marche(x, y):
        return 0 <= y < h and 0 <= x < w and not legende[sol[y][x]].get("solide")

    # Depuis le trottoir d'une porte ordinaire du Faubourg : le coeur de la ville, a pied.
    depart = next((x, y) for y in range(h) for x in range(w) if sol[y][x] == ".")
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in vus and marche(*q):
                vus.add(q)
                file.append(q)
    return {(r["x"] + r["porte"], r["y"] + 1) for r in ville["residences"]
            if marche(r["x"] + r["porte"], r["y"] + 1) and (r["x"] + r["porte"], r["y"] + 1) not in vus}


def test_chaque_porte_de_logement_reste_rejoignable_a_pied(deux_villes):
    """Depuis la rue, à pied (tout ce qui n'est pas solide), on atteint la tuile devant chaque porte de logement — aussi
    bien qu'avant les clôtures (l'île, elle, ne se rejoint pas à pied : c'est la même avant et après)."""
    avec, sans = deux_villes
    de_plus = _portes_enfermees(avec) - _portes_enfermees(sans)
    assert not de_plus, f"des portes enfermées derrière une clôture : {sorted(de_plus)[:5]}"
