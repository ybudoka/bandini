"""Le temps des Fêtes, côté Python (docs/jalons/le-temps-des-fetes.md) : décembre, le sapin sur une place du
Faubourg, et les dindes qui tiennent l'économie."""

import villes

from app import calendrier, carte, economie, fetes


def test_decembre_et_le_sapin_du_faubourg():
    assert fetes.jours() and all(calendrier.mois(j) == "decembre" for j in fetes.jours())
    v = villes.exporter()
    s = fetes.sapin(v)
    assert s  # sa place : `test_le_sapin_a_une_place_libre_sur_la_place`
    assert villes.assembler()["fetes"] == fetes.pour_le_navigateur(v)


def test_les_dindes_se_livrent_en_camion():
    """Le gain (entre le taxi et quatre fois le taxi) est jugé pour TOUS les boulots par
    `test_economie::test_chaque_boulot_vaut_la_peine_sans_ecraser_les_autres`."""
    assert economie.BOULOTS["dindes"]["vehicule"] == "camion"


def test_le_sapin_a_une_place_libre_sur_la_place():
    """Martin (26 sept. 2026, capture) : le sapin plantait ses branches dans un banc et dans la fontaine.
    Tout son gabarit est du sol de la place, sans décor, sans scène, sans devant de porte ; une tuile d'air
    autour, sans rue ; et l'amuseur de la scène voisine garde sa place."""
    from app import devants

    v = villes.exporter()
    s = fetes.sapin(v)
    assert s
    pris = {(d["x"], d["y"]) for d in v["decor"]}
    for couche in ("ambulants", "reclames", "paquets", "scenes"):
        pris |= {(o["x"], o["y"]) for o in v[couche]}
    larges = devants.devants(v)[0]
    for dy in range(-3, 3):
        for dx in range(-2, 3):
            x, y = s["x"] + dx, s["y"] + dy
            assert (x, y) not in pris, f"quelque chose se tient sous le sapin en {(x, y)}"
            assert not carte.routier(v["sol"][y][x]), f"le sapin déborde sur la rue en {(x, y)}"
            if -1 <= dx <= 1 and -2 <= dy <= 1:
                assert (x, y) not in larges, f"le sapin bouche un devant de porte en {(x, y)}"
    assert all(max(abs(q["x"] - s["x"]), abs(q["y"] - s["y"])) >= fetes.LOIN_D_UNE_SCENE for q in v["scenes"])
    faubourg = [q for q in v["scenes"] if q["district"] == "faubourg"]
    meilleure = min(faubourg, key=lambda q: (-q["valeur"], q["y"], q["x"]))
    assert max(abs(meilleure["x"] - s["x"]), abs(meilleure["y"] - s["y"])) <= fetes.PORTEE, "le sapin a quitté sa place"
