"""Le catalogue des passants — et ce que le navigateur en fait."""

import pytest

from app import armes, carte, pietons


@pytest.mark.parametrize("pieton", pietons.CATALOGUE, ids=lambda p: p["slug"])
def test_un_pieton_est_jouable(pieton):
    assert pieton["nom"]
    assert set(pieton["couleurs"]) == {"c", "h", "s", "p"}, pieton["slug"]
    for couleur in pieton["couleurs"].values():
        assert couleur.startswith("#") and len(couleur) == 7, couleur
    # Un marchand derriere son kiosque ne marche pas : sa vitesse est nulle,
    # et c'est ce qui le dit. Tous les autres marchent.
    if pieton["metier"] == "ambulant":
        assert pieton["vitesse"] == 0.0
    else:
        assert 0.5 <= pieton["vitesse"] <= 1.5
    assert 0.0 <= pieton["courage"] <= 1.0
    assert 0.0 <= pieton["temoin"] <= 1.0
    assert 20 <= pieton["vie"] <= 150
    mini, maxi = pieton["argent"]
    assert 0 <= mini <= maxi <= 200
    if pieton["arme"]:
        assert armes.par_slug(pieton["arme"]), pieton["arme"]


def test_les_enfants_sont_intouchables():
    """⚠️ Le jeu est adulte : on y meurt, le sang coule. Un enfant, non.

    C'est une regle du catalogue, donc du moteur — pas une consigne qu'on
    peut oublier d'appliquer dans une branche du code de combat.
    """
    enfants = [p for p in pietons.CATALOGUE if p["sprite"] == "enfant"]
    assert enfants, "plus d'enfants dans la ville ?"
    for enfant in enfants:
        assert enfant["intouchable"] is True, enfant["slug"]
        assert enfant["arme"] is None
        assert enfant["courage"] == 0.0, "un enfant ne riposte pas"
    for pieton in pietons.CATALOGUE:
        if pieton["accompagne"]:
            accompagne = pietons.par_slug(pieton["accompagne"])
            assert accompagne and accompagne["intouchable"], pieton["slug"]


def test_les_metiers_ont_leurs_heures():
    for pieton in pietons.CATALOGUE:
        if pieton["metier"]:
            assert pieton["frequence"] == 0.0, \
                f"{pieton['slug']} : un metier ne nait pas au hasard dans la rue"
        if pieton["heures"]:
            debut, fin = pieton["heures"]
            assert 0 <= debut < 1 and 0 <= fin < 1
    nuit = pietons.par_slug("racoleuse")
    assert pietons.travaille_a(nuit, 0.95) and not pietons.travaille_a(nuit, 0.5)
    assert pietons.de_metier("compagnie") and pietons.de_metier("ambulant")


def test_la_fille_de_la_brume_ne_porte_les_couleurs_de_personne():
    """⚠️ Retour de Martin (13 sept. 2026) : on ne les distinguait plus. Son
    rose etait celui de la passante a une nuance pres, et ses cheveux ceux de
    la moitie du catalogue. Le CONTOUR est dans sprites.js (`racoleuse`) ; ici
    on garde l'autre moitie : aucune de ses couleurs ne se recroise ailleurs.
    La peau, elle, se partage — c'est une peau."""
    fille = pietons.par_slug("racoleuse")
    assert fille["sprite"] == "racoleuse", "elle a repris le corps de tout le monde"
    for autre in pietons.CATALOGUE:
        if autre["slug"] == "racoleuse":
            continue
        for cle in ("c", "h", "p"):
            assert autre["couleurs"][cle].lower() != fille["couleurs"][cle].lower(), \
                f"{autre['slug']} porte la meme couleur « {cle} » que la fille de la Brume"


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


def test_l_agent_de_police_est_un_pieton_arme_qui_ne_nait_pas_au_hasard():
    agent = pietons.par_slug("policier")
    assert agent and agent["metier"] == "police" and agent["frequence"] == 0.0
    # Les gars du lot : un metier, donc jamais dans la rue ; du courage, une
    # batte, et surtout PAS d'arme a feu — ils ripostent, ils n'abattent pas.
    gardiens = pietons.de_metier("gardien")
    assert gardiens and all(g["frequence"] == 0.0 for g in gardiens)
    assert all(g["courage"] >= 0.9 and g["arme"] == "batte" for g in gardiens)
    assert agent["arme"] == "pistolet" and agent["courage"] == 1.0
    assert agent["temoin"] == 0.0, "un agent ne temoigne pas : il agit"
    assert agent not in pietons.ordinaires()
