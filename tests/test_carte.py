"""Les juges de la ville — ce qui doit etre vrai AVANT de dessiner une tuile.

Une ville generee peut etre injouable de six facons, et aucune ne se voit sur
une capture d'ecran : un trottoir enclave, un sens unique qui ne mene nulle
part, une porte devant un mur, un batiment pose sur la rue. Ces tests sont la
pour que la ville soit jouable par construction.
"""

import pytest

from app import carte, economie, magasins

CARTE = carte.exporter()


def test_rectangulaire_et_glyphes_connus():
    assert len(CARTE["sol"]) == CARTE["hauteur"]
    assert len(CARTE["voie"]) == CARTE["hauteur"]
    for ligne, voie in zip(CARTE["sol"], CARTE["voie"]):
        assert len(ligne) == CARTE["largeur"]
        assert len(voie) == CARTE["largeur"]
        assert set(ligne) <= set(carte.LEGENDE), set(ligne) - set(carte.LEGENDE)
        assert set(voie) <= carte.VOIES, set(voie) - carte.VOIES


def test_la_ville_a_la_taille_de_son_plan():
    assert CARTE["largeur"] == (len(carte.PLAN[0]) + 1) * carte.ROUTE + len(carte.PLAN[0]) * carte.BLOC_L
    assert CARTE["hauteur"] == (len(carte.PLAN) + 1) * carte.ROUTE + len(carte.PLAN) * carte.BLOC_H


def test_les_fleches_sont_sur_la_route_et_menent_quelque_part():
    for y, ligne in enumerate(CARTE["voie"]):
        for x, fleche in enumerate(ligne):
            if fleche == ".":
                continue
            assert carte.routier(CARTE["sol"][y][x]), (x, y, CARTE["sol"][y][x])
            assert carte.suivre_voie(CARTE, x, y), f"cul-de-sac routier en {(x, y)}"


def test_les_voies_sont_fortement_connexes():
    """De n'importe quelle tuile de rue on doit rejoindre n'importe quelle autre."""
    sans_aller, sans_retour = carte.voies_bloquees(CARTE)
    assert not sans_aller, f"{len(sans_aller)} tuiles inatteignables, p. ex. {sorted(sans_aller)[:5]}"
    assert not sans_retour, f"{len(sans_retour)} tuiles sans retour, p. ex. {sorted(sans_retour)[:5]}"


def test_les_lignes_d_arret_disent_leur_sens():
    marquees = {(x, y) for y, ligne in enumerate(CARTE["voie"])
                for x, fleche in enumerate(ligne) if fleche == "S"}
    declarees = {tuple(int(n) for n in cle.split(",")) for cle in CARTE["arrets"]}
    assert marquees == declarees, "le glyphe S et la table `arrets` ont derive"
    assert marquees, "aucune ligne d'arret"
    for cle, sens in CARTE["arrets"].items():
        x, y = (int(n) for n in cle.split(","))
        assert sens in carte.PAS
        dx, dy = carte.PAS[sens]
        assert CARTE["voie"][y + dy][x + dx] == "+", "une ligne d'arret entre dans un croisement"


def test_les_croisements_sont_des_croisements():
    assert len(CARTE["intersections"]) == (len(carte.PLAN[0]) + 1) * (len(carte.PLAN) + 1)
    for inter in CARTE["intersections"]:
        for y in range(inter["y"], inter["y"] + inter["h"]):
            for x in range(inter["x"], inter["x"] + inter["l"]):
                assert CARTE["voie"][y][x] == "+", (x, y)
                assert carte.routier(CARTE["sol"][y][x])


def test_tout_ce_qui_est_marchable_est_relie():
    groupes = carte.composantes_marchables(CARTE)
    assert len(groupes) == 1, f"{len(groupes)} ilots marchables : un trottoir est enclave"
    principal = groupes[0]
    depart = CARTE["apparition"]["joueur"]
    assert (depart["x"], depart["y"]) in principal
    for point in CARTE["points_interet"]:
        assert (point["x"], point["y"]) in principal, point
    for porte in CARTE["portes"]:
        assert (porte["x"], porte["y"] + 1) in principal, porte


def test_les_portes_menent_a_un_interieur():
    slugs = set()
    for porte in CARTE["portes"]:
        assert CARTE["sol"][porte["y"]][porte["x"]] == "D", porte
        assert carte.marchable(CARTE["sol"][porte["y"] + 1][porte["x"]]), porte
        assert porte["interieur"] in CARTE["interieurs"], porte
        slugs.add(porte["lieu"])
    portes_du_sol = {(x, y) for y, ligne in enumerate(CARTE["sol"])
                     for x, glyphe in enumerate(ligne) if glyphe == "D"}
    assert portes_du_sol == {(p["x"], p["y"]) for p in CARTE["portes"]}, \
        "une tuile D sans porte declaree : le joueur frapperait a une porte muette"
    assert len(slugs) == len(CARTE["portes"]), "deux portes pour le meme lieu"


@pytest.mark.parametrize("slug", sorted(carte.INTERIEURS))
def test_un_interieur_est_une_piece_habitable(slug):
    piece = CARTE["interieurs"][slug]
    assert len(piece["sol"]) == piece["hauteur"]
    for ligne in piece["sol"]:
        assert len(ligne) == piece["largeur"]
        assert set(ligne) <= set(carte.LEGENDE)
    sortie = piece["sortie"]
    assert piece["sol"][sortie["y"]][sortie["x"]] == "D"
    assert "".join(piece["sol"]).count("D") == 1
    depart = piece["apparition"]
    assert carte.marchable(piece["sol"][depart["y"]][depart["x"]])
    groupes = carte.composantes_marchables(piece)
    assert len(groupes) == 1, f"{slug} : un coin de la piece est mure"
    for point in piece["points"]:
        assert 0 < point["x"] < piece["largeur"] - 1
        assert 0 < point["y"] < piece["hauteur"] - 1


def test_aucun_gabarit_ne_deborde_sur_la_rue():
    """Les couloirs de rue appartiennent a la rue : rien de solide dedans."""
    pas_rue = 0
    for i in range(len(carte.PLAN[0]) + 1):
        x0 = i * (carte.BLOC_L + carte.ROUTE)
        for y in range(CARTE["hauteur"]):
            for dx in range(carte.ROUTE):
                glyphe = CARTE["sol"][y][x0 + dx]
                assert carte.solidite(glyphe) != 1, f"batiment sur la rue en {(x0 + dx, y)}"
                pas_rue += 1
    assert pas_rue > 0
    for j in range(len(carte.PLAN) + 1):
        y0 = j * (carte.BLOC_H + carte.ROUTE)
        for x in range(CARTE["largeur"]):
            for dy in range(carte.ROUTE):
                glyphe = CARTE["sol"][y0 + dy][x]
                assert carte.solidite(glyphe) != 1, f"batiment sur la rue en {(x, y0 + dy)}"


def test_les_chaussees_sont_des_routes_sur_toute_leur_longueur():
    for j in range(len(carte.PLAN) + 1):
        y0 = j * (carte.BLOC_H + carte.ROUTE) + carte.TROTTOIR
        for x in range(CARTE["largeur"]):
            for k in range(carte.VOIE_L):
                assert carte.routier(CARTE["sol"][y0 + k][x]), (x, y0 + k)
                assert CARTE["voie"][y0 + k][x] != "."


def test_le_decor_ne_bouche_ni_la_rue_ni_les_portes():
    devants = {(p["x"], p["y"] + 1) for p in CARTE["portes"]}
    devants |= {(p["x"], p["y"] + 2) for p in CARTE["portes"]}
    vus = set()
    for morceau in CARTE["decor"]:
        position = (morceau["x"], morceau["y"])
        glyphe = CARTE["sol"][morceau["y"]][morceau["x"]]
        assert not carte.routier(glyphe), f"{morceau} est sur la chaussee"
        assert carte.marchable(glyphe), morceau
        assert position not in devants, f"{morceau} bouche une porte"
        assert position not in vus, f"deux decors sur {position}"
        vus.add(position)


def test_les_lampadaires_eclairent_depuis_un_trottoir():
    positions = {(d["x"], d["y"]) for d in CARTE["decor"] if d["type"] == "lampadaire"}
    assert len(CARTE["lampes"]) >= 40
    for lampe in CARTE["lampes"]:
        assert (lampe["x"], lampe["y"]) in positions, "une lampe sans poteau"
        assert CARTE["sol"][lampe["y"]][lampe["x"]] == "."


def test_les_lieux_des_magasins_et_des_proprietes_existent():
    lieux = {p["slug"] for p in CARTE["points_interet"]}
    for magasin in magasins.CATALOGUE:
        if magasin["phase"] == 1:
            assert magasin["lieu"] in lieux, magasin["slug"]
    for propriete in economie.PROPRIETES:
        if propriete["phase"] == 1:
            assert propriete["lieu"] in lieux, propriete["slug"]
    assert "planque" in lieux and "terminus" in lieux


def test_les_zones_tiennent_dans_la_carte():
    for zone in CARTE["zones"]:
        assert 0 <= zone["x"] and 0 <= zone["y"]
        assert zone["x"] + zone["l"] <= CARTE["largeur"]
        assert zone["y"] + zone["h"] <= CARTE["hauteur"]
    slugs = [z["slug"] for z in CARTE["zones"]]
    assert slugs[0] == "faubourg" and "cravates" in slugs


def test_deterministe():
    assert carte.generer() == carte.generer()
    assert carte.exporter()["sol"] == CARTE["sol"]


def test_une_autre_graine_redecore_la_meme_ossature():
    autre = carte.generer(graine=carte.GRAINE + 1)
    assert autre["voie"] == CARTE["voie"], "les rues ne dependent pas du hasard"
    assert autre["portes"] == CARTE["portes"], "les batiments garantis non plus"
    assert autre["sol"] != CARTE["sol"], "la graine ne change rien : le hasard est mort"
    assert len(carte.composantes_marchables(autre)) == 1
    sans_aller, sans_retour = carte.voies_bloquees(autre)
    assert not sans_aller and not sans_retour
