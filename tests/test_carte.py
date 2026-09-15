"""Les juges de la ville — ce qui doit etre vrai AVANT de dessiner une tuile.

Une ville generee peut etre injouable de six facons, et aucune ne se voit sur
une capture d'ecran : un trottoir enclave, un sens unique qui ne mene nulle
part, une porte devant un mur, un batiment pose sur la rue. Ces tests sont la
pour que la ville soit jouable par construction.
"""

import pytest

from app import carte, economie, magasins

CARTE = carte.exporter()

#: Les lieux qu'une ville DOIT avoir, quelle que soit la graine. ⚠️ Les autres
#: portes (un commerce ordinaire qui ouvre, un logement qu'on peut visiter) sont
#: tirees au sort : leur nombre et leurs noms changent d'une graine a l'autre,
#: et c'est voulu. Ce qui ne doit jamais changer, c'est cette liste-ci.
LIEUX_GARANTIS = {special["slug"] for special in carte.SPECIAUX.values()} | {"kiosque"}


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
    # ⚠️ Les portes ne s'alignent pas. Le juge exigeait des colonnes TOUTES
    # differentes ; il tenait tant qu'il y avait seize portes dans 421
    # colonnes. Depuis qu'un commerce ordinaire sur cinq ouvre la sienne, deux
    # portes tombent parfois dans la meme colonne a deux quartiers d'ecart —
    # ce n'est pas un damier, c'est un anniversaire partage. Ce qui compte,
    # c'est qu'elles restent EPARPILLEES.
    colonnes = {porte["x"] for porte in CARTE["portes"]}
    assert len(colonnes) >= len(CARTE["portes"]) * 0.8, "les portes s'alignent"
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


def test_les_trois_clotures_disent_ce_qu_elles_font():
    """⚠️ Le defaut que Martin a nomme : « une cloture, si elle n'est pas
    barbelee, qu'on puisse passer par-dessus ». On passait par-dessus TOUTES —
    sans meme ralentir. `f` etait solide 3 : le masque des vehicules la voyait,
    celui des pietons non. Une cloture n'arretait donc que les chars, et a pied
    elle n'existait pas.

    Les trois sortes vivent maintenant dans la legende, et rien d'autre ne les
    distingue : 4 s'enjambe (grillage, palissade de bois), 5 ne se passe pas
    (barbele). Aucune n'est solide 1 — on VOIT a travers une cloture."""
    for glyphe in carte.CLOTURES:
        proprietes = carte.LEGENDE[glyphe]
        assert proprietes.get("cloture"), glyphe
        assert carte.solidite(glyphe) in (4, 5), glyphe
        assert not carte.marchable(glyphe), f"on ne se tient pas SUR une cloture ({glyphe})"
        assert carte.solidite(glyphe) != 0, f"un char franchirait {glyphe}"
    for glyphe in carte.ENJAMBABLES:
        assert carte.solidite(glyphe) == 4 and carte.franchissable(glyphe), glyphe
    assert carte.solidite(carte.BARBELE) == 5
    assert not carte.franchissable(carte.BARBELE), "le barbele s'enjambe : il ne veut plus rien dire"


def test_la_ville_porte_les_trois_clotures_la_ou_elles_ont_un_sens():
    """Chacune a un endroit et une raison : du barbele la ou quelqu'un a paye
    pour que personne n'entre (les cours de gang, les cours de La Shop), du
    grillage la ou l'on passe par-dessus (la fourriere, les terrains vagues), et
    du bois dans les cours arriere de la banlieue — la variete demandee par
    Martin, et ce qui fait qu'une banlieue a l'air d'une banlieue vue d'en haut.
    """
    zones = [z for z in CARTE["zones"] if z.get("district")]

    def district(x, y):
        for z in zones:
            if z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"]:
                return z["slug"]
        return None

    par_cloture: dict[str, set[str]] = {g: set() for g in carte.CLOTURES}
    compte = dict.fromkeys(carte.CLOTURES, 0)
    for y, ligne in enumerate(CARTE["sol"]):
        for x, glyphe in enumerate(ligne):
            if glyphe in carte.CLOTURES:
                compte[glyphe] += 1
                par_cloture[glyphe].add(district(x, y))
    for glyphe, n in compte.items():
        assert n >= 20, f"presque pas de {carte.LEGENDE[glyphe]['nom']} dans la ville : {n}"
    assert par_cloture[carte.BOIS] == {"erables"},         f"la palissade de bois est une image de BANLIEUE : {par_cloture[carte.BOIS]}"
    assert "shop" in par_cloture[carte.BARBELE]
    # La fourriere garde son GRILLAGE, et c'est une decision : « on le reprend
    # par-dessus la cloture » est la moitie de ce qui la rend interessante.
    lot = CARTE["fourriere"]
    tour = ([(lot["x"] + i, lot["y"]) for i in range(lot["largeur"])]
            + [(lot["x"], lot["y"] + j) for j in range(lot["hauteur"])])
    clotures = [CARTE["sol"][y][x] for x, y in tour if CARTE["sol"][y][x] in carte.CLOTURES]
    assert len(clotures) > 10 and set(clotures) == {carte.GRILLAGE},         "du barbele a la fourriere : il ne reste qu'une caisse a payer"


def test_un_barbele_ne_referme_jamais_une_poche():
    """⚠️ Le piege du barbele : c'est un mur pour un pieton. Une cour qu'il
    referme n'est plus dans la ville — et `boucher_les_poches`, qui est le filet
    du generateur, la MURE en silence (avec ses arbres, et parfois le devant
    d'une porte d'a cote).

    Le juge est double : la ville reste d'un seul tenant a pied en comptant le
    barbele comme un mur (c'est ce que fait `composantes_marchables`), et la
    graine livree ne fait boucher aucune tuile."""
    assert len(carte.composantes_marchables(CARTE)) == 1
    assert CARTE["tuiles_bouchees"] == 0
    principal = carte.composantes_marchables(CARTE)[0]
    for y, ligne in enumerate(CARTE["sol"]):
        for x, glyphe in enumerate(ligne):
            if glyphe != carte.BARBELE:
                continue
            for vx, vy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if not (0 <= vy < CARTE["hauteur"] and 0 <= vx < CARTE["largeur"]):
                    continue
                if carte.marchable(CARTE["sol"][vy][vx]):
                    assert (vx, vy) in principal,                         f"du sol enferme par du barbele en ({vx},{vy})"


def test_une_cloture_relie_ses_deux_cotes_mais_le_barbele_coupe():
    """Les deux faces de `composantes_marchables`, sur une petite carte a la
    main : un grillage est un PONT (on l'enjambe), un barbele est un mur."""
    def petite(cloture):
        return {"sol": ["BBBBB", "B.f.B".replace("f", cloture), "BBBBB"]}

    assert len(carte.composantes_marchables(petite(carte.GRILLAGE))) == 1
    assert len(carte.composantes_marchables(petite(carte.BOIS))) == 1
    assert len(carte.composantes_marchables(petite(carte.BARBELE))) == 2
    # Et la tuile de cloture n'est jamais DANS un groupe : on ne s'y tient pas.
    groupe = carte.composantes_marchables(petite(carte.GRILLAGE))[0]
    assert (2, 1) not in groupe and {(1, 1), (3, 1)} <= groupe


def test_chaque_lieu_declare_sa_famille_et_sa_couleur():
    """⚠️ Zero repli gris. Les couleurs des blips de la carte codent des familles
    — dore pour tes places, bleu pour les services, vert pour les magasins — mais
    la table vivait dans `hud.js`, ecrite a la main : elle declarait dix lieux, la
    ville en compte seize, et les six autres (depanneur, hotel, cantine, usine,
    phare, fourriere) tombaient tous sur le meme gris par defaut. M8 en avait
    ajoute cinq, M9 un sixieme, et personne n'avait touche a la table.

    Les couleurs sont maintenant des DONNEES qui descendent avec les lieux, et ce
    juge est ce qui remplace la relecture : un lieu de plus sans famille fait
    rougir le test, pas le joueur."""
    for glyphe, special in carte.SPECIAUX.items():
        assert special.get("famille") in carte.FAMILLES_DE_LIEU, (glyphe, special["slug"])
    for point in CARTE["points_interet"]:
        assert point.get("famille") in carte.FAMILLES_DE_LIEU, point
    for nom, famille in carte.FAMILLES_DE_LIEU.items():
        assert famille["couleur"].startswith("#") and len(famille["couleur"]) == 7, nom
        assert famille["libelle"] and famille["libelle"] == famille["libelle"].upper(), nom
    # La legende du joueur ne vaut que si les familles servent vraiment : une
    # famille declaree que personne ne porte est une ligne de legende vide.
    portees = {point["famille"] for point in CARTE["points_interet"]}
    assert portees == set(carte.FAMILLES_DE_LIEU), \
        f"familles sans lieu : {set(carte.FAMILLES_DE_LIEU) - portees}"
    assert CARTE["familles"] == carte.FAMILLES_DE_LIEU, "les familles doivent voyager dans le paquet"


def test_la_couverture_d_un_toit_suit_le_genre_du_batiment():
    """⚠️ `batiment_forme` faisait `des.choix(TOITS)` : un entrepot heritait de
    l'ardoise et un bungalow du gravier goudronne. Un toit se lit d'abord a sa
    matiere, et la matiere appartient au BATIMENT, pas au hasard."""
    for genre, couverture in carte.COUVERTURES.items():
        assert couverture, genre
        assert set(couverture) <= set(carte.TOITS), (genre, couverture)
        for glyphe in couverture:
            assert carte.LEGENDE[glyphe].get("toit"), glyphe
    # La banlieue est faite de bungalows : deux versants, jamais autre chose.
    assert set(carte.COUVERTURES["banlieue"]) == {carte.TOIT_PENTE}
    # Et un entrepot n'a pas d'ardoise.
    for genre in ("hangars", "industriel"):
        assert "E" not in carte.COUVERTURES[genre], genre


def test_deux_batiments_mitoyens_ne_portent_pas_la_meme_couverture():
    """⚠️ Le bord d'un toit se lit dans le VOISINAGE : « ma voisine n'est pas le
    meme toit ». Entre deux batiments collés couverts pareil, il n'y a donc aucun
    bord a trouver — ils n'en font plus qu'un vu d'en haut, et c'est justement ce
    que le bord devait empecher.

    Le generateur corrige le tirage au lieu d'en refaire un : un de de plus
    decalerait toute la ville (la lecon du de des devantures, du de des rampes et
    du de des clotures). Ce juge pose deux batiments collés, l'un apres l'autre,
    et regarde ce que le second choisit."""
    chantier = carte._Chantier(carte.PLAN, 7)
    premier = {(3 + i, 3 + j) for i in range(4) for j in range(3)}
    second = {(7 + i, 3 + j) for i in range(4) for j in range(3)}
    chantier.batiment_forme(premier, genre="commerces")
    toit_premier = chantier.sol[3][3]
    for _ in range(12):
        chantier.batiment_forme(second, genre="commerces")
        assert chantier.sol[3][7] != toit_premier, "le voisin a la meme couverture"
    assert toit_premier in carte.COUVERTURES["commerces"]


def test_ce_qu_un_toit_porte_ne_se_pose_jamais_n_importe_ou():
    """L'equipement de toit — ventilation, climatisation, cheminee, cage,
    reservoir, antennes — est ce qui rend un toit credible vu d'en haut.

    ⚠️ Il n'est PAS du decor (`poser_decor` refuse les tuiles solides, et il a
    raison : le decor est une entite qu'on heurte). Il voyage donc dans le
    paquet, et ces regles-la sont tout ce qui l'empeche de se poser au mauvais
    endroit : jamais sur un bord (un equipement au ras du parapet se lit comme
    un morceau de mur), jamais colle a un autre, jamais sur une facade."""
    sol = CARTE["sol"]
    poses = {(t["x"], t["y"]) for t in CARTE["toits"]}
    types = {e["type"] for e in carte.EQUIPEMENTS_DE_TOIT}
    assert len(CARTE["toits"]) >= 40, f"presque rien sur les toits : {len(CARTE['toits'])}"
    assert {t["type"] for t in CARTE["toits"]} <= types
    for t in CARTE["toits"]:
        x, y = t["x"], t["y"]
        assert sol[y][x] in carte.TOITS, f"{t['type']} sur « {sol[y][x]} »"
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            voisine = sol[y + dy][x + dx]
            assert voisine in carte.TOITS, (
                f"{t['type']} au bord du toit : « {voisine} » en ({x + dx},{y + dy})"
            )
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx or dy) and (x + dx, y + dy) in poses:
                    raise AssertionError(f"deux equipements colles en ({x},{y})")


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
    """⚠️ Deux sortes de lumiere depuis les devantures : le LAMPADAIRE, qui a
    toujours son poteau planté dans du sol qu'on foule, et la VITRINE, qui n'en
    a pas — elle n'est qu'un reflet au pied d'un mur. Confondre les deux ferait
    echouer ce juge des qu'on ajoute un commerce.

    ⚠️ Le poteau n'est pas toujours sur un TROTTOIR : les allees d'un parc et
    le pourtour d'une place en portent aussi, et ceux-la sont sur de l'herbe ou
    du sable. Ce qui doit rester vrai, c'est qu'aucun poteau ne pousse dans un
    mur ni au milieu de la chaussee — un lampadaire sur l'asphalte, c'est un
    accident qui attend. (Le juge exigeait le trottoir ; il tenait par chance,
    parce qu'un arbre occupait les coins qui auraient rougi.)
    """
    positions = {(d["x"], d["y"]) for d in CARTE["decor"] if d["type"] == "lampadaire"}
    #: ⚠️ Trois sortes de lumiere, maintenant : le poteau, la VITRINE (un reflet
    #: au pied d'un commerce) et la FENETRE allumee d'un logement. Seul le
    #: premier a un poteau plante dans le sol.
    poteaux = [lampe for lampe in CARTE["lampes"]
               if lampe.get("c") not in ("vitrine", "fenetre")]
    assert len(poteaux) >= 40
    trottoirs = 0
    for lampe in poteaux:
        assert (lampe["x"], lampe["y"]) in positions, "une lampe sans poteau"
        glyphe = CARTE["sol"][lampe["y"]][lampe["x"]]
        assert carte.marchable(glyphe) and not carte.routier(glyphe), glyphe
        trottoirs += glyphe == "."
    assert trottoirs > len(poteaux) * 0.8, "la plupart des poteaux bordent une rue"


def test_aucun_lampadaire_ne_prend_le_coin_d_un_feu():
    """⚠️ **Retour de Martin : « ne mets pas de lampadaire aux intersections,
    déplace-les — ça va laisser la place libre aux feux ».**

    `lampadaires()` plantait ses poteaux **sur les coins** du croisement, et
    c'est exactement là que va le mât d'un feu. Tant qu'il n'y avait que deux
    mâts et qu'aucune lanterne n'était peinte, les deux cohabitaient sans
    qu'on le voie ; depuis qu'un tricolore ne montre qu'une rue, il y a
    **quatre mâts par croisement, un par coin**, et le lampadaire leur
    disputait la place au vu de tous.

    Le coin d'un croisement à feux est la place du **feu**. Le lampadaire
    s'écarte le long du trottoir — où il éclaire d'ailleurs mieux, entre deux
    croisements plutôt que dessus.
    """
    reserves = set()
    for inter in CARTE["intersections"]:
        if len(inter["bras"]) < 4:
            continue
        for cx, cy in ((inter["x"] + inter["l"], inter["y"] - 1),
                       (inter["x"] - 1, inter["y"] + inter["h"]),
                       (inter["x"] - 1, inter["y"] - 1),
                       (inter["x"] + inter["l"], inter["y"] + inter["h"])):
            for ix in (-1, 0, 1):
                for iy in (-1, 0, 1):
                    reserves.add((cx + ix, cy + iy))
    poteaux = [lampe for lampe in CARTE["lampes"]
               if lampe.get("c") not in ("vitrine", "fenetre")]
    dessus = [(lampe["x"], lampe["y"]) for lampe in poteaux if (lampe["x"], lampe["y"]) in reserves]
    assert not dessus, f"{len(dessus)} lampadaires sur un coin reserve au feu (ex. {dessus[:4]})"
    # ⚠️ Et il en reste : ecarter n'est pas supprimer. Sans cette borne, la
    # regle serait tenue par une ville sans lampadaires.
    assert len(poteaux) >= 40, f"{len(poteaux)} lampadaires : la rue est noire"


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
    assert {p["lieu"] for p in autre["portes"]} >= LIEUX_GARANTIS, \
        "un batiment garanti a disparu avec la graine"
    assert autre["portes"] != CARTE["portes"], "les batiments ne bougent pas du tout ?"
    assert len(carte.composantes_marchables(autre)) == 1
    # ⚠️ Le filet a le droit de servir, pas de porter la ville. Deux batiments
    # tires au sort qui se rejoignent laissent parfois une cour de six tuiles,
    # et `boucher_les_poches` la rebatit — c'est exactement son role. Ce qui
    # serait grave, c'est qu'il en bouche des dizaines : la, c'est un gabarit
    # qui enferme, et le nombre le dit. (Le juge exigeait zero ; il tenait par
    # chance, et le premier arbre deplace le faisait rougir.)
    assert autre["tuiles_bouchees"] < 40, autre["tuiles_bouchees"]
    assert CARTE["tuiles_bouchees"] == 0, "la graine du jeu, elle, n'enferme rien"
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
    assert {p["lieu"] for p in ville["portes"]} >= LIEUX_GARANTIS
    for porte in ville["portes"]:
        assert carte.marchable(ville["sol"][porte["y"] + 1][porte["x"]]), porte


#: Ou pointe le NEZ de l'auto, pour chaque glyphe de case.
NEZ = {"^": (0, -1), "v": (0, 1), "<": (-1, 0), ">": (1, 0)}


def test_toute_rangee_de_stationnement_touche_une_allee():
    """Le juge du decoupage, sur toutes les profondeurs possibles.

    ⚠️ C'est LA regle du stationnement : une rangee qui ne touche aucune allee
    est une rangee de cases ou aucune auto ne peut entrer. Elle ne se voit pas
    sur une capture d'ecran — les lignes sont peintes pareil.
    """
    for creux in range(4, 41):
        bandes = carte._Chantier._bandes_stationnement(None, creux)
        assert sum(taille for _, taille in bandes) == creux, (creux, bandes)
        rangees = [i for i, (type_, _) in enumerate(bandes) if type_ == "R"]
        assert rangees, creux
        for i in rangees:
            assert bandes[i][1] == carte.CASE_CREUX, (creux, bandes)
            voisines = [bandes[k][0] for k in (i - 1, i + 1) if 0 <= k < len(bandes)]
            assert "A" in voisines, f"creux {creux} : la rangee {i} n'a pas d'allee ({bandes})"
        # Une rangee de plus a chaque fois qu'il y a la place : sinon on livre
        # un terrain a moitie vide.
        assert 2 * (len(rangees) + 1) + carte.ALLEE * ((len(rangees) + 2) // 2) > creux, \
            f"creux {creux} : {len(rangees)} rangees, il en tenait une de plus"


def test_les_cases_de_stationnement_sont_au_gabarit_de_l_auto():
    """Deux tuiles de creux — pas une de plus, pas une de moins — et le cote
    ouvert donne sur de quoi rouler. C'est ce qui fait qu'une auto garee tombe
    dans ses lignes au pixel pres, et qu'elle peut en ressortir."""
    sol = CARTE["sol"]
    cases = 0
    for y, ligne in enumerate(sol):
        for x, glyphe in enumerate(ligne):
            if glyphe not in NEZ:
                continue
            cases += 1
            dx, dy = NEZ[glyphe]
            devant = sol[y + dy][x + dx] == glyphe
            derriere = sol[y - dy][x - dx] == glyphe
            assert devant != derriere, f"case de creux irregulier en {(x, y)}"
            fx, fy = (x + dx, y + dy) if devant else (x, y)     # la tuile du fond
            ox, oy = fx - 2 * dx, fy - 2 * dy                   # ce qui ouvre l'allee
            ouvert = sol[oy][ox]
            assert carte.routier(ouvert) and ouvert not in NEZ, \
                f"la case en {(x, y)} est muree : « {ouvert} » devant son ouverture"
    assert cases >= 400, f"seulement {cases} cases de stationnement dans la ville"


def test_les_ilots_de_stationnement_sont_au_bout_des_rangees():
    """Un ilot ferme une rangee : on marche dessus, on ne roule pas dedans, et
    il touche toujours des cases — un ilot au milieu de l'asphalte n'est qu'un
    obstacle."""
    sol = CARTE["sol"]
    ilots = 0
    for y, ligne in enumerate(sol):
        for x, glyphe in enumerate(ligne):
            if glyphe != "I":
                continue
            ilots += 1
            assert carte.marchable(glyphe) and not carte.routier(glyphe)
            voisins = [sol[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            assert any(v in NEZ for v in voisins), f"ilot esseule en {(x, y)}"
    assert ilots >= 8, f"seulement {ilots} tuiles d'ilot"


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


# --- La fourriere : une cour, pas un champ d'asphalte -----------------------


def test_la_cour_de_la_fourriere_se_range_en_cases():
    """⚠️ Elle etait un rectangle de « p » avec des places calculees a la main,
    alors que toute la ville range ses stationnements en cases depuis qu'on les
    dessine. Des chars saisis ranges de travers dans un lot municipal, c'est
    exactement le defaut qu'on a corrige partout ailleurs.

    Les places se LISENT donc dans les cases — chacune est le fond d'une case,
    la tuile qui porte le pare-chocs — et plus personne ne les invente.
    """
    from app import economie

    lot = CARTE["fourriere"]
    assert lot, "la ville n'a pas de fourriere"
    places = lot["places"]
    assert len(places) >= economie.FOURRIERE["places"], \
        f"{len(places)} places pour {economie.FOURRIERE['places']} chars gardes"
    for place in places:
        glyphe = CARTE["sol"][place["y"]][place["x"]]
        assert carte.LEGENDE[glyphe].get("case") == place["sens"], \
            f"la place {place} ne tombe pas sur une case de stationnement"
        # Le fond d'une case : la tuile suivante, dans l'axe du nez, n'est plus
        # la meme case. Sinon on garerait deux chars l'un dans l'autre.
        dx, dy = carte.PAS[{"N": "^", "S": "v", "O": "<", "E": ">"}[place["sens"]]]
        assert CARTE["sol"][place["y"] + dy][place["x"] + dx] != glyphe, \
            f"la place {place} n'est pas le fond de sa case"


def test_la_cour_de_la_fourriere_n_a_pas_de_tremplin():
    """⚠️ `_stationnement` finit par poser un tremplin dans une allee. Dans la
    cour de la fourriere, ce serait une sortie PAR-DESSUS LA CLOTURE sans
    payer — et toute l'idee du lot tombe : on le rachete au comptoir, ou on le
    reprend a pied et le lot appelle."""
    lot = CARTE["fourriere"]
    dedans = [r for r in CARTE["rampes"]
              if lot["x"] <= r["x"] < lot["x"] + lot["largeur"]
              and lot["y"] <= r["y"] < lot["y"] + lot["hauteur"]]
    assert not dedans, f"un tremplin dans la cour de la fourriere : {dedans}"


def test_on_entre_dans_la_fourriere_par_une_seule_grille():
    """La cloture arrete les chars et pas les gens (solidite 3) : c'est ce qui
    fait les deux facons de reprendre son char sans une ligne de code pour les
    distinguer. Mais il n'y a QU'UNE ouverture — deux, et sortir sans payer ne
    demanderait plus rien a personne."""
    lot, grille = CARTE["fourriere"], CARTE["fourriere"]["grille"]
    ouvertures = 0
    for tx in range(lot["x"], lot["x"] + lot["largeur"]):
        for ty in (lot["y"], lot["y"] + lot["hauteur"] - 1):
            if carte.solidite(CARTE["sol"][ty][tx]) == 0:
                ouvertures += 1
    for ty in range(lot["y"], lot["y"] + lot["hauteur"]):
        for tx in (lot["x"], lot["x"] + lot["largeur"] - 1):
            if carte.solidite(CARTE["sol"][ty][tx]) == 0:
                ouvertures += 1
    assert ouvertures == grille["largeur"], \
        f"{ouvertures} tuiles ouvertes dans la cloture, la grille en fait {grille['largeur']}"


def test_aucun_arbre_ne_bouche_un_sentier_de_parc():
    """⚠️ Retour de Martin : « les arbres ne devraient pas être dans les
    sentiers. » Et ce n'etait pas qu'une question de vue : un arbre est
    SOLIDE, rayon 5. `_parc` trace ses allees en baionnette puis seme ses
    arbres, ses bancs et ses buissons **sur tout le rectangle** du parc, au
    hasard ; `poser_decor` ne refuse que le solide, le routier, l'occupe et le
    reserve. Une allee est du pave : marchable, pas routiere. Rien ne la
    protegeait, et un sentier barre par ses propres arbres est pire qu'un parc
    sans sentier — on l'a dessine pour dire « passe par ici ».

    Le juge REJOUE le chantier pour savoir ou sont les sentiers, au lieu de
    deviner « du pave » (le trottoir de toute la ville en est aussi, et un
    arbre de rue est exactement ce qu'on veut).
    """
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    chantier.eaux()
    chantier.rues()
    chantier.croisements()
    chantier.ilots()
    solides = {"arbre", "banc", "poubelle", "caisse", "fontaine", "buisson", "debris"}
    dessus = [d for d in CARTE["decor"]
              if d["type"] in solides and (d["x"], d["y"]) in chantier.reserve]
    assert not dessus, f"{len(dessus)} decors solides posés sur un sentier : {dessus[:4]}"
    assert chantier.reserve, "plus rien n'est reserve : les sentiers ne se protegent plus"


def test_un_sentier_de_parc_se_traverse_de_bout_en_bout():
    """La reserve ne sert a rien si l'allee est coupee autrement. On verifie
    qu'un parc se traverse : de chaque tuile d'allee, on rejoint les autres."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    chantier.eaux()
    chantier.rues()
    chantier.croisements()
    chantier.ilots()
    allees = {(x, y) for (x, y) in chantier.reserve
              if carte.marchable(CARTE["sol"][y][x])}
    assert len(allees) > 100, f"seulement {len(allees)} tuiles de sentier dans toute la ville"
    for x, y in allees:
        assert carte.solidite(CARTE["sol"][y][x]) == 0, \
            f"la tuile de sentier {(x, y)} est solide : on ne passe pas"


# --- Une piece plus grande que sa maison ------------------------------------

#: Ce qui fait la CARCASSE d'un batiment : mur, toit, facade, vitrine, porte —
#: y compris la porte de garage, qui est du batiment et pas du trottoir. ⚠️ Lu
#: dans LEGENDE et pas ecrit a la main : un glyphe de batiment ajoute demain
#: entre tout seul dans le compte, au lieu de faire mentir le juge en silence.
CARCASSE = {g for g in carte.LEGENDE if carte.LEGENDE[g].get("solide") == 1}


def _empreinte(sol: list[str], x: int, y: int) -> int:
    """Les tuiles du batiment qui porte cette porte — ce que le joueur VOIT."""
    hauteur, largeur = len(sol), len(sol[0])
    vues = {(x, y)}
    pile = [(x, y)]
    while pile:
        cx, cy = pile.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < largeur and 0 <= ny < hauteur
                    and (nx, ny) not in vues and sol[ny][nx] in CARCASSE):
                vues.add((nx, ny))
                pile.append((nx, ny))
    return len(vues)


#: ⚠️ CINQ graines, parce que c'est le tirage des marges qui creait l'ecart :
#: une seule graine dirait « ca tient » de la meme facon qu'une piece de
#: monnaie dit pile.
GRAINES = (carte.GRAINE, 1, 2, 3, 4)


def _part_de_la_vitrine(sol: list[str], porte: dict) -> set[tuple[int, int]]:
    """Les tuiles de batiment qu'on voit AU-DESSUS d'une vitrine.

    C'est la part de batiment qui appartient a cette porte-la, donc ce a quoi sa
    piece doit ressembler. ⚠️ On monte tant que le TOIT ne change pas : deux
    batiments colles n'ont jamais la meme couverture (`batiment_forme` y veille,
    « ma voisine n'est pas le meme toit »), et c'est ce qui permet de mesurer un
    commerce sans avaler celui d'a cote ni celui de derriere.
    """
    x0, large = porte["vitrine"]
    part = set()
    for x in range(x0, x0 + large):
        if not (0 <= x < len(sol[0])) or sol[porte["y"]][x] not in CARCASSE:
            continue
        part.add((x, porte["y"]))
        toit, y = None, porte["y"] - 1
        while y >= 0:
            glyphe = sol[y][x]
            if glyphe not in CARCASSE or (toit is not None and glyphe != toit):
                break
            toit = glyphe
            part.add((x, y))
            y -= 1
    return part


@pytest.mark.parametrize("graine", GRAINES)
def test_la_piece_a_les_mesures_de_son_batiment(graine):
    """Martin : « je veux que l'interieur soit PROPORTIONNE a l'exterieur ».

    ⚠️ La regle d'avant etait une INEGALITE — le plancher ne depasse pas
    l'empreinte — et une inegalite se satisfait tres bien d'une piece minuscule
    dans un immeuble immense : un bloc de 59 x 8 ouvrait sur un 9 x 8, treize
    pour cent, et un batiment de quatre tuiles de profond sur une piece qui en
    fait six. Ce juge-ci mesure les DEUX cotes de la proportion.

    On compare le PLANCHER (murs deduits) a la part de batiment que la vitrine
    possede, parce que c'est la convention du jeu : une cabane de 3 x 3 ouvre
    sur 3 x 3 de plancher, donc une piece de 5 x 5 murs compris — les murs de la
    piece SONT ceux du batiment.
    """
    ville = carte.generer(graine=graine)
    sol, pieces = ville["sol"], ville["interieurs"]
    faux = []
    for porte in ville["portes"]:
        largeur, hauteur = carte.mesures_de_la_suite(porte["interieur"], pieces)
        part = _part_de_la_vitrine(sol, porte)
        xs = [x for x, _ in part]
        ys = [y for _, y in part]
        boite = (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
        if (largeur, hauteur) != boite or largeur * hauteur > len(part):
            faux.append((porte["interieur"], f"{boite[0]}x{boite[1]}", f"{largeur}x{hauteur}"))
    assert not faux, (
        f"{len(faux)} portes ouvrent sur une piece qui n'a pas les mesures de son "
        f"batiment (graine {graine}) : " + ", ".join(
            f"{slug} {dehors} dehors, {dedans} dedans" for slug, dehors, dedans in faux[:5]))


@pytest.mark.parametrize("graine", GRAINES)
def test_les_portes_s_ouvrent_quand_meme(graine):
    """Le juge du dessus passerait aussi si PLUS AUCUNE porte ne s'ouvrait.

    C'est la moitie qu'on oublie : condamner les quarante portes serait une
    facon de ne jamais mentir. On exige donc l'inverse — la ville garde ses
    portes, les petites maisons ouvrent sur de petites pieces (elles ne
    s'ouvraient pas du tout avant qu'on descende a trois sur trois), et les
    grandes sur des grandes.
    """
    ville = carte.generer(graine=graine)
    pieces = ville["interieurs"]
    planchers = [carte.mesures_de_la_suite(p["interieur"], pieces) for p in ville["portes"]]
    assert len(planchers) >= 25, f"seulement {len(planchers)} portes s'ouvrent (graine {graine})"
    petites = [m for m in planchers if m[0] * m[1] <= 16]
    grandes = [m for m in planchers if m[0] * m[1] >= 50]
    assert petites, "aucune petite piece : les petites maisons ont toutes ete condamnees"
    assert grandes, "aucune grande piece : les grands batiments ouvrent sur des cabanes"


@pytest.mark.parametrize("graine", GRAINES)
def test_une_longue_facade_porte_plusieurs_vitrines(graine):
    """Soixante tuiles de large, ce n'est pas un commerce : c'est une rangee.

    ⚠️ L'autre moitie de la demande de Martin, et celle qui rend la premiere
    tenable : sans decouper les facades, « proportionne » voudrait dire une
    piece de cinquante tuiles de large derriere une seule porte. Ici on juge la
    ville finie — deux vitrines ne se marchent jamais dessus, et il y a bien des
    facades qui en portent plusieurs ; la COUPE elle-meme se juge juste en
    dessous, sans generer quoi que ce soit.
    """
    ville = carte.generer(graine=graine)
    par_rangee: dict[int, list[tuple[int, int]]] = {}
    for porte in ville["portes"]:
        par_rangee.setdefault(porte["y"], []).append(tuple(porte["vitrine"]))
    for rangee, vitrines in par_rangee.items():
        bornes = sorted(vitrines)
        for (x0, l0), (x1, _) in zip(bornes, bornes[1:]):
            assert x0 + l0 <= x1, f"deux vitrines se chevauchent en rangee {rangee}"
    assert [v for v in par_rangee.values() if len(v) > 1], \
        "aucune facade ne porte deux commerces : le decoupage ne sert a rien"


def test_une_part_de_batiment_donne_les_mesures_de_sa_piece():
    """La regle, en trois lignes, sans generer la ville.

    ⚠️ `None` est un RESULTAT, pas un echec : un bout de batiment trop petit
    garde sa porte, elle ne s'ouvre simplement pas. Une porte qui donne sur plus
    grand que la maison est un mensonge ; une porte qu'on ne pousse pas n'en est
    pas un.
    """
    plein = {(x, y) for x in range(10) for y in range(4)}
    assert carte.mesures_de_la_part(plein) == (10, 4), "un batiment plein donne sa boite"
    # Un L : la boite ment de six tuiles, et c'est la PROFONDEUR qui cede — la
    # largeur d'une vitrine est ce que le joueur compare en poussant la porte.
    en_l = plein - {(x, 0) for x in range(6)}
    assert carte.mesures_de_la_part(en_l) == (10, 3)
    assert carte.mesures_de_la_part({(0, 0), (1, 0), (0, 1), (1, 1)}) is None
    assert carte.mesures_de_la_part(set()) is None


def test_un_etage_est_une_piece_de_plus_pas_une_piece_plus_grande():
    """La nuance des plex : N etages, c'est N pieces de l'empreinte.

    ⚠️ Et les deux escaliers ou aucun — un escalier qui ne redescend pas laisse
    le joueur pris en haut, la porte du bas etant la seule sortie.
    """
    bas = carte.piece_de_logement("essai", 8, 5, 4, etage="essai_haut")
    haut = carte.piece_de_logement("essai_haut", 8, 5, 4, etage="essai", haut=True)
    assert (bas["largeur"], bas["hauteur"]) == (haut["largeur"], haut["hauteur"])
    assert carte.mesures_de_la_suite("essai", {"essai": bas, "essai_haut": haut}) == (8, 5)
    for piece, vers in ((bas, "essai_haut"), (haut, "essai")):
        marches = [p for p in piece["points"] if p["type"] == "escalier"]
        assert marches and marches[0]["vers"] == vers, \
            f"{piece['slug']} : l'escalier ne mene pas a {vers}"


def test_une_facade_se_coupe_en_commerces_sauf_un_entrepot():
    """La coupe, mesuree sur une facade de soixante tuiles.

    ⚠️ L'entrepot est l'exception, et c'est la MEME regle de proportion : un
    hangar est une seule affaire, sa facade porte un nom et une porte, et
    derriere il y a un entrepot de toute sa largeur. Le decouper en sept
    magasins de huit serait inventer une rue commercante dans La Shop.
    """
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)      # tout est gazon : on voit partout
    facade = [(x, 10) for x in range(60)]
    vitrines = chantier.decouper_la_facade(facade, "commerces")
    assert len(vitrines) == 8, f"{len(vitrines)} vitrines pour soixante tuiles"
    assert sum(v[1] for v in vitrines) == 60, "la facade n'est pas entierement partagee"
    assert all(carte._Chantier.VITRINE_MIN <= v[1] <= 2 * carte._Chantier.VITRINE
               for v in vitrines), f"des vitrines hors mesure : {vitrines}"
    assert [v[0] for v in vitrines] == sorted(v[0] for v in vitrines)
    entrepot = chantier.decouper_la_facade(facade, "hangars")
    assert entrepot == [(0, 60, 10)], f"un entrepot s'est fait couper en {len(entrepot)}"
    # Une facade a trous (un batiment en L) : une suite, une coupe.
    troue = [(x, 10) for x in list(range(6)) + list(range(20, 26))]
    assert chantier.decouper_la_facade(troue, "commerces") == [(0, 6, 10), (20, 6, 10)]


# --- Une cloture cloture un terrain -----------------------------------------

def _courses_de_cloture(sol) -> list[list[tuple[int, int]]]:
    """Les morceaux de clôture d'une carte, en 4-connexité (une clôture est
    orthogonale : deux tuiles en diagonale ne se tiennent pas)."""
    tuiles = {(x, y) for y, ligne in enumerate(sol) for x, g in enumerate(ligne)
              if g in carte.CLOTURES}
    vus: set[tuple[int, int]] = set()
    courses = []
    for depart in sorted(tuiles):
        if depart in vus:
            continue
        pile, course = [depart], []
        vus.add(depart)
        while pile:
            x, y = pile.pop()
            course.append((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                voisine = (x + dx, y + dy)
                if voisine in tuiles and voisine not in vus:
                    vus.add(voisine)
                    pile.append(voisine)
        courses.append(course)
    return courses


def _tourne(course) -> bool:
    """Une course qui fait au moins un COIN : une tuile qui a une voisine
    horizontale ET une voisine verticale. C'est ce qui sépare une clôture d'une
    barre posée sur un gazon."""
    dedans = set(course)
    return any(
        (((x + 1, y) in dedans or (x - 1, y) in dedans)
         and ((x, y + 1) in dedans or (x, y - 1) in dedans))
        for x, y in course)


@pytest.mark.parametrize("ville", [CARTE] + [carte.generer(graine=g) for g in (1, 7, 99, 777)])
def test_une_cloture_cloture_un_terrain(ville):
    """⚠️ Demande de Martin : « les clôtures doivent clôturer les terrains, pas
    juste être là seules ». Il regardait le jeu, et la mesure lui donnait raison
    trois fois : sur la ville livrée, **361 tuiles de clôture en 80 morceaux,
    dont 69 sans un seul coin** (216 tuiles de barre droite) et **24 toutes
    seules**. Un piquet planté au milieu d'une pelouse n'enferme rien.

    Trois sources, et chacune avait sa raison d'avoir tort : le terrain vague ne
    peignait qu'UN côté, et une tuile sur deux ; la cour de gang ne peignait que
    la rangée du sud ; la cour arrière de `_jardin` posait son U tuile par tuile
    et `poser_cloture` en refusait en silence. `clore` pose des enceintes (tout
    ou rien, une trouée garantie) et `elaguer_les_clotures` enlève ce que la
    ville leur mange ensuite.

    Le juge tient la règle telle qu'elle se dit : **une clôture tourne, ou elle
    n'est pas là**.
    """
    courses = _courses_de_cloture(ville["sol"])
    assert courses, "plus une seule clôture dans la ville"
    droites = [c for c in courses if not _tourne(c)]
    assert not droites, (
        f"{len(droites)} clôtures ne tournent jamais "
        f"({sum(len(c) for c in droites)} tuiles) : "
        f"{[sorted(c)[0] for c in droites[:5]]}"
    )
    seules = [c for c in courses if len(c) == 1]
    assert not seules, f"{len(seules)} tuiles de clôture toutes seules : {seules[:5]}"


def test_une_cloture_ne_remplace_ni_un_mur_ni_une_chaussee():
    """⚠️ `clore` passe là où il y a déjà quelque chose — c'est tout l'objet
    d'une enceinte. Sans ce garde-fou, le barbelé de la cour des Skateux
    mangeait deux colonnes de leur stationnement et « il y a un tremplin à La
    Pointe à tout coup » redevenait une légende."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    chantier.rect(0, 0, 8, 8, ",")
    chantier.sol[4][3] = "F"                     # un mur
    chantier.sol[4][4] = "#"                     # de la chaussée
    chantier.sol[4][5] = "^"                     # une case de stationnement
    assert not chantier.cloture_possible(3, 4)
    assert not chantier.cloture_possible(4, 4)
    assert not chantier.cloture_possible(5, 4)
    assert chantier.cloture_possible(6, 4)


def test_une_enceinte_garde_toujours_une_trouee():
    """⚠️ Sans trouée, une enceinte fermée est une poche que
    `boucher_les_poches` murerait — et le terrain disparaîtrait avec."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    chantier.rect(0, 0, 20, 20, ",")
    posees = chantier.clore(2, 2, 10, 8, carte.GRILLAGE)
    tour = 2 * (10 + 8) - 4
    assert 0 < posees < tour, f"{posees} tuiles pour un tour de {tour}"
    dedans = [(x, y) for y in range(3, 9) for x in range(3, 11)
              if chantier.sol[y][x] in carte.CLOTURES]
    assert not dedans, f"une enceinte a peint dans son terrain : {dedans}"
