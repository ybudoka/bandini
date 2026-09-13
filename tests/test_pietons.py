"""Le catalogue des passants — et ce que le navigateur en fait."""

import pytest

from app import armes, carte, pietons


@pytest.mark.parametrize("pieton", pietons.CATALOGUE, ids=lambda p: p["slug"])
def test_un_pieton_est_jouable(pieton):
    assert pieton["nom"]
    assert set(pieton["couleurs"]) == {"c", "h", "s", "p"}, pieton["slug"]
    for couleur in pieton["couleurs"].values():
        assert couleur.startswith("#") and len(couleur) == 7, couleur
    assert 0.5 <= pieton["vitesse"] <= 1.5
    assert 0.0 <= pieton["courage"] <= 1.0
    assert 0.0 <= pieton["temoin"] <= 1.0
    assert 20 <= pieton["vie"] <= 150
    mini, maxi = pieton["argent"]
    assert 0 <= mini <= maxi <= 200
    if pieton["arme"]:
        assert armes.par_slug(pieton["arme"]), pieton["arme"]


def test_les_slugs_sont_uniques():
    assert len(pietons.SLUGS) == len(set(pietons.SLUGS))


def test_il_y_a_du_monde_ordinaire_dans_la_rue():
    ordinaires = pietons.ordinaires()
    assert len(ordinaires) >= 5
    assert sum(p["frequence"] for p in ordinaires) > 0
    # ⚠️ Un membre de gang n'apparait JAMAIS au hasard dans la rue : il sort
    # de son territoire. Sinon on croise des Cravates a l'autre bout de la ville.
    for pieton in ordinaires:
        assert pieton["gang"] is None


def test_le_courage_va_du_fuyard_au_bagarreur():
    courages = sorted(p["courage"] for p in pietons.CATALOGUE)
    assert courages[0] == 0.0, "personne ne fuit sans se poser de question ?"
    assert courages[-1] >= 0.8, "personne ne riposte ?"


def test_les_gangs_ont_un_territoire_et_un_archetype():
    zones = {z["slug"] for z in carte.exporter()["zones"]}
    for gang in pietons.GANGS:
        assert pietons.par_slug(gang["pieton"]), gang["pieton"]
        assert gang["zone"] in zones, f"{gang['slug']} : territoire {gang['zone']} absent de la carte"
        assert 1 <= gang["membres"] <= 30


def test_les_reactions_sont_des_durees_credibles():
    reactions = pietons.REACTIONS
    assert reactions["recul_images"] < reactions["ko_images"]
    assert 1 <= reactions["fuite_secondes"] <= 30
    assert 0 < reactions["pickpocket_dos_degres"] <= 180
