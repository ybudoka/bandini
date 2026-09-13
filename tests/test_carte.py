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


def test_la_ville_a_la_taille_de_sa_trame():
    assert CARTE["largeur"] == sum(carte.COLONNES) + sum(carte.RUES_V)
    assert CARTE["hauteur"] == sum(carte.RANGEES) + sum(carte.RUES_H)
    assert len(carte.RUES_V) == len(carte.COLONNES) + 1
    assert len(carte.RUES_H) == len(carte.RANGEES) + 1


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
    total = (len(carte.PLAN[0]) + 1) * (len(carte.PLAN) + 1)
    # Un superbloc avale des croisements : il en reste moins que la trame.
    assert 0 < len(CARTE["intersections"]) < total
    for inter in CARTE["intersections"]:
        assert len(inter["bras"]) >= 2, inter
        for y in range(inter["y"], inter["y"] + inter["h"]):
            for x in range(inter["x"], inter["x"] + inter["l"]):
                assert CARTE["voie"][y][x] == "+", (x, y)
                assert carte.routier(CARTE["sol"][y][x])


def test_la_ville_est_irreguliere():
    """⚠️ Le juge de l'asymetrie : une ville en damier n'a aucun repere.

    Chaque ligne ci-dessous protege une source d'irregularite ; si l'une saute,
    la ville redevient un damier sans qu'aucun autre test ne s'en apercoive.
    """
    assert len(set(carte.COLONNES)) >= 5, "les colonnes de blocs sont trop semblables"
    assert len(set(carte.RANGEES)) >= 4, "les rangees de blocs sont trop semblables"
    assert len(set(carte.RUES_V)) >= 2 and len(set(carte.RUES_H)) >= 2, \
        "toutes les rues ont la meme largeur"

    maitre = carte.regions_du_plan(carte.PLAN)
    regions = len(set(maitre.values()))
    assert regions < len(maitre), "aucun superbloc : aucune rue ne s'arrete"

    bras = {i["bras"] for i in CARTE["intersections"]}
    assert any(len(b) == 3 for b in bras), "aucun croisement en T"

    # Les batiments : autant de formes que possible, et au moins une cour.
    tailles = set()
    for porte in CARTE["portes"]:
        tailles.add(porte["x"])
    assert len(tailles) == len(CARTE["portes"])
    fronts = _empreintes_de_batiments(CARTE)
    assert len(fronts) >= 20, f"seulement {len(fronts)} batiments"
    assert len(set(fronts)) >= 8, "les batiments ont tous la meme boite"


def _empreintes_de_batiments(plan_carte):
    """Les boites (largeur, hauteur) des paquets de tuiles solides."""
    sol = plan_carte["sol"]
    vus = set()
    boites = []
    for y, ligne in enumerate(sol):
        for x, glyphe in enumerate(ligne):
            if carte.solidite(glyphe) != 1 or (x, y) in vus:
                continue
            groupe = set()
            pile = [(x, y)]
            while pile:
                cx, cy = pile.pop()
                if (cx, cy) in groupe or not (0 <= cy < len(sol) and 0 <= cx < len(sol[cy])):
                    continue
                if carte.solidite(sol[cy][cx]) != 1:
                    continue
                groupe.add((cx, cy))
                pile.extend(((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)))
            vus |= groupe
            largeur = max(c[0] for c in groupe) - min(c[0] for c in groupe) + 1
            hauteur = max(c[1] for c in groupe) - min(c[1] for c in groupe) + 1
            boites.append((largeur, hauteur))
    return boites


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


def test_aucun_gabarit_ne_deborde_sur_une_rue_qui_existe():
    """Une rue posee appartient a la rue : rien de solide dedans, et de la
    chaussee sur toute sa longueur. Un segment AVALE par un superbloc, lui,
    appartient a l'ilot — c'est tout l'interet des superblocs."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    vues = 0
    for i in range(chantier.nc + 1):
        for j in range(chantier.nr):
            if not chantier.rue_v_existe(i, j):
                continue
            for y in range(chantier.yb[j], chantier.yb[j] + carte.RANGEES[j]):
                for dx in range(carte.RUES_V[i]):
                    x = chantier.xr[i] + dx
                    assert carte.solidite(CARTE["sol"][y][x]) != 1, f"batiment sur la rue en {(x, y)}"
                    if carte.TROTTOIR <= dx < carte.RUES_V[i] - carte.TROTTOIR:
                        assert carte.routier(CARTE["sol"][y][x]), (x, y)
                        assert CARTE["voie"][y][x] != "."
                        vues += 1
    for j in range(chantier.nr + 1):
        for i in range(chantier.nc):
            if not chantier.rue_h_existe(i, j):
                continue
            for dy in range(carte.RUES_H[j]):
                y = chantier.yr[j] + dy
                for x in range(chantier.xb[i], chantier.xb[i] + carte.COLONNES[i]):
                    assert carte.solidite(CARTE["sol"][y][x]) != 1, f"batiment sur la rue en {(x, y)}"
                    if carte.TROTTOIR <= dy < carte.RUES_H[j] - carte.TROTTOIR:
                        assert carte.routier(CARTE["sol"][y][x]), (x, y)
                        assert CARTE["voie"][y][x] != "."
                        vues += 1
    assert vues > 3000, f"seulement {vues} tuiles de chaussee verifiees"


def test_un_superbloc_avale_bien_sa_rue():
    """La cour des Cravates couvre quatre blocs : au centre, plus de rue."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    avales = [(i, j) for i in range(1, chantier.nc) for j in range(chantier.nr)
              if not chantier.rue_v_existe(i, j)]
    assert avales, "aucune rue verticale avalee"
    for i, j in avales:
        milieu = chantier.xr[i] + carte.RUES_V[i] // 2
        y = chantier.yb[j] + carte.RANGEES[j] // 2
        assert CARTE["voie"][y][milieu] == ".", f"la rue {i} existe encore en {(milieu, y)}"


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
    """Le hasard redessine les ilots ; il ne touche ni aux rues ni aux lieux."""
    autre = carte.generer(graine=carte.GRAINE + 1)
    assert autre["voie"] == CARTE["voie"], "les rues ne dependent pas du hasard"
    assert autre["sol"] != CARTE["sol"], "la graine ne change rien : le hasard est mort"
    assert ({p["lieu"] for p in autre["portes"]} == {p["lieu"] for p in CARTE["portes"]}), \
        "un batiment garanti a disparu avec la graine"
    assert autre["portes"] != CARTE["portes"], "les batiments ne bougent pas du tout ?"
    assert len(carte.composantes_marchables(autre)) == 1
    assert autre["tuiles_bouchees"] == 0, "des poches a boucher : un gabarit enferme"
    sans_aller, sans_retour = carte.voies_bloquees(autre)
    assert not sans_aller and not sans_retour


@pytest.mark.parametrize("graine", [1, 7, 12345, 20260912, 99999999])
def test_n_importe_quelle_graine_donne_une_ville_jouable(graine):
    """⚠️ Le decoupage en parcelles tire beaucoup de des : une seule graine
    verte ne prouve rien. Cinq villes entieres, cinq fois les memes juges."""
    ville = carte.generer(graine=graine)
    assert len(carte.composantes_marchables(ville)) == 1
    sans_aller, sans_retour = carte.voies_bloquees(ville)
    assert not sans_aller and not sans_retour
    assert {p["lieu"] for p in ville["portes"]} == {p["lieu"] for p in CARTE["portes"]}
    for porte in ville["portes"]:
        assert carte.marchable(ville["sol"][porte["y"] + 1][porte["x"]]), porte


def test_les_commerces_ambulants_ont_leur_place():
    """Un kiosque se pose sur un trottoir au bord de la rue, un camion sur un
    stationnement — et jamais devant une porte."""
    from app import magasins

    poses = CARTE["ambulants"]
    assert len(poses) >= 6, f"seulement {len(poses)} commerces ambulants"
    devants = {(p["x"], p["y"] + 1) for p in CARTE["portes"]}
    vus = set()
    for pose in poses:
        commerce = magasins.ambulant(pose["slug"])
        assert commerce, pose["slug"]
        glyphe = CARTE["sol"][pose["y"]][pose["x"]]
        attendu = "." if commerce["sur"] == "trottoir" else "p"
        assert glyphe == attendu, f"{pose['slug']} pose sur « {glyphe} »"
        assert carte.marchable(CARTE["sol"][pose["y"] + 1][pose["x"]]), \
            f"{pose['slug']} : on ne peut pas se placer devant"
        assert (pose["x"], pose["y"]) not in devants, "un kiosque bouche une porte"
        assert (pose["x"], pose["y"]) not in vus, "deux commerces sur la meme tuile"
        vus.add((pose["x"], pose["y"]))
    for a, b in zip(sorted(vus), sorted(vus)[1:]):
        if a[1] == b[1]:
            assert abs(a[0] - b[0]) >= 2, "deux kiosques colles"
