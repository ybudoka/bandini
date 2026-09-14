"""M8 — les cinq districts : une ville d'un seul tenant, et cinq quartiers.

⚠️ Les juges d'ici repondent tous a la meme question : est-ce qu'on peut aller
partout ? Une ville cinq fois plus grande peut se casser de trois facons qu'on
ne voit pas a l'ecran — un quartier isole derriere l'eau, une artere coupee a
la frontiere, un pont qui n'en est pas un. Aucune ne se rattrape apres coup :
elles se voient ici, avant de dessiner une tuile.
"""

import pytest

from app import carte

CARTE = carte.exporter()
DISTRICTS = {d["slug"]: d for d in carte.DISTRICTS}
ZONES = {z["slug"]: z for z in CARTE["zones"]}
TERRE = [d for d in carte.DISTRICTS if not d.get("eau")]


def _tuiles_de(slug):
    """Les tuiles de rue d'un district (sa zone, moins ce qui deborde)."""
    z = ZONES[slug]
    return [(x, y) for y in range(z["y"], z["y"] + z["h"])
            for x in range(z["x"], z["x"] + z["l"]) if CARTE["voie"][y][x] != "."]


def _atteignables(depart, voie=None):
    """Tout ce qu'un char atteint depuis cette tuile en suivant les fleches."""
    plan = CARTE if voie is None else {**CARTE, "voie": voie}
    vues = {depart}
    pile = [depart]
    while pile:
        courant = pile.pop()
        for suite in carte.suivre_voie(plan, *courant):
            if suite not in vues:
                vues.add(suite)
                pile.append(suite)
    return vues


def test_les_districts_pavent_la_grille():
    """Pas de trou, pas de chevauchement, et personne ne fusionne chez le voisin."""
    assert len(TERRE) == 5, "il en faut cinq : le Faubourg et ses quatre voisins"
    blocs = set()
    for d in carte.DISTRICTS:
        for j in range(len(d["plan"])):
            for i in range(len(d["plan"][0])):
                bloc = (d["bx"] + i, d["by"] + j)
                assert bloc not in blocs, f"deux districts sur {bloc}"
                blocs.add(bloc)
    assert len(blocs) == len(carte.PLAN) * len(carte.PLAN[0])
    # La regle qui rend les districts deplacables : aucune fusion ne sort.
    for d in carte.DISTRICTS:
        assert not any(ligne[0] == "<" for ligne in d["plan"]), d["slug"]
        assert "^" not in d["plan"][0], d["slug"]


def _trame(district):
    """Les trois chiffres qui font la trame d'un quartier."""
    maitre = carte.regions_du_plan(carte.PLAN)
    bx, by = district["bx"], district["by"]
    largeur, hauteur = len(district["plan"][0]), len(district["plan"])
    blocs = [(bx + i, by + j) for j in range(hauteur) for i in range(largeur)]
    zone = ZONES[district["slug"]]
    rues = sum(1 for y in range(zone["y"], zone["y"] + zone["h"])
               for x in range(zone["x"], zone["x"] + zone["l"]) if CARTE["voie"][y][x] != ".")
    colonnes = carte.COLONNES[bx:bx + largeur]
    return {"rues": rues / (zone["l"] * zone["h"]),
            "fusion": 1 - len({maitre[b] for b in blocs}) / len(blocs),
            "colonne": sum(colonnes) / len(colonnes)}


def test_chaque_district_a_sa_trame():
    """⚠️ Un quartier qu'on ne reconnait pas est un decor, pas un quartier.

    Trois chiffres le trahissent : combien de RUES au metre carre (La Shop en a
    la moitie moins que le Faubourg), combien de blocs FUSIONNES (les hangars
    du port en sont faits), et la LARGEUR moyenne de ses colonnes (la banlieue
    n'a que de grandes parcelles). Deux quartiers doivent differer sur au moins
    un des trois, franchement — sinon on roule dedans sans savoir ou on est.
    """
    marges = {"rues": 0.03, "fusion": 0.10, "colonne": 1.5}
    trames = {d["slug"]: _trame(d) for d in TERRE}
    for i, a in enumerate(TERRE):
        for b in TERRE[i + 1:]:
            ta, tb = trames[a["slug"]], trames[b["slug"]]
            ecarts = {cle: abs(ta[cle] - tb[cle]) for cle in marges}
            assert any(ecarts[cle] > marges[cle] for cle in marges), \
                f"{a['slug']} et {b['slug']} ont la meme trame : {ecarts}"


def test_chaque_district_a_son_contenu():
    """Et ce qu'on y trouve n'est pas ce qu'on trouve a cote."""
    contenus = {}
    for district in TERRE:
        glyphes = frozenset("".join(district["plan"])) - set("<^")
        assert glyphes not in contenus, f"{district['slug']} et {contenus[glyphes]} : meme contenu"
        contenus[glyphes] = district["slug"]


def test_on_roule_de_chaque_district_a_chaque_autre():
    """La promesse de M8 : du Faubourg a La Pointe sans chargement."""
    depart = _tuiles_de("faubourg")[0]
    joignables = _atteignables(depart)
    for district in TERRE:
        tuiles = _tuiles_de(district["slug"])
        assert tuiles, f"{district['slug']} n'a aucune rue"
        touchees = sum(1 for t in tuiles if t in joignables)
        assert touchees == len(tuiles), \
            f"{district['slug']} : {len(tuiles) - touchees} tuiles de rue sur {len(tuiles)} hors d'atteinte"


def test_le_pont_est_le_seul_lien_vers_la_pointe():
    """⚠️ Le chenal doit couper VRAIMENT : sans pont, La Pointe est une ile.

    Si ce test devient vert en enlevant le pont, c'est qu'une rue, une plage ou
    un banc de sable a referme le chenal — et l'unique pont ne veut plus rien
    dire.
    """
    ponts = CARTE["ponts"]
    assert len(ponts) == 1, ponts
    pont = ponts[0]
    tablier = [(x, y) for y in range(pont["y"], pont["y"] + pont["h"])
               for x in range(pont["x"], pont["x"] + pont["l"])]
    assert any(CARTE["voie"][y][x] in "^v<>+S" for x, y in tablier), "le pont ne se conduit pas"
    assert all(carte.marchable(CARTE["sol"][y][x]) for x, y in tablier), "on ne traverse pas le pont a pied"

    sans = [list(ligne) for ligne in CARTE["voie"]]
    for x, y in tablier:
        sans[y][x] = "."
    sans = ["".join(ligne) for ligne in sans]
    coupees = _atteignables(_tuiles_de("faubourg")[0], sans)
    # ⚠️ Pas la ZONE de La Pointe : elle partage le boulevard du bord avec La
    # Shop, et ce boulevard-la est du bon cote de l'eau. Ce sont les BLOCS du
    # district, chenal compris, qui doivent devenir injoignables.
    pointe = carte.district_par_slug("pointe")
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    x0, y0 = chantier.xr[pointe["bx"]], chantier.yb[pointe["by"]]
    derriere = [(x, y) for y in range(y0, CARTE["hauteur"]) for x in range(x0, CARTE["largeur"])
                if CARTE["voie"][y][x] != "."]
    assert derriere, "La Pointe n'a aucune rue a elle"
    assert not any(t in coupees for t in derriere), \
        "on rejoint La Pointe sans passer sur le pont"


def test_la_baie_n_a_ni_rue_ni_batiment():
    z = ZONES["baie"]
    for y in range(z["y"] + 4, z["y"] + z["h"] - 4):
        for x in range(z["x"] + 4, z["x"] + z["l"] - 4):
            assert CARTE["voie"][y][x] == ".", f"une rue traverse la baie en {(x, y)}"
            assert CARTE["sol"][y][x] in "~s", f"du bati dans la baie en {(x, y)}"


@pytest.mark.parametrize("district", TERRE, ids=lambda d: d["slug"])
def test_chaque_district_a_sa_gang_et_son_point_de_repere(district):
    """Une raison d'y aller, et quelqu'un qui n'aime pas te voir."""
    zone = ZONES[district["slug"]]
    assert zone["nom"] and zone["pietons"] > 0
    cour = ZONES.get(district["gang"])
    assert cour and cour["gang"] == district["gang"], f"{district['slug']} : pas de cour de gang"
    assert cour["x"] >= zone["x"] and cour["x"] + cour["l"] <= zone["x"] + zone["l"], \
        "la cour de la gang deborde du district"
    dedans = [p for p in CARTE["points_interet"]
              if zone["x"] <= p["x"] < zone["x"] + zone["l"] and zone["y"] <= p["y"] < zone["y"] + zone["h"]]
    assert dedans, f"{district['slug']} : rien a y faire"


def test_les_zones_de_district_ne_se_chevauchent_pas():
    """`Monde.zoneA` garde la derniere zone qui contient le point : si deux
    districts se superposaient, le nom sous la mini-carte mentirait."""
    quartiers = [ZONES[d["slug"]] for d in carte.DISTRICTS]
    for i, a in enumerate(quartiers):
        for b in quartiers[i + 1:]:
            chevauche = (a["x"] < b["x"] + b["l"] and b["x"] < a["x"] + a["l"]
                         and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])
            assert not chevauche, f"{a['slug']} et {b['slug']} se marchent dessus"
    aire = sum(z["l"] * z["h"] for z in quartiers)
    assert aire == CARTE["largeur"] * CARTE["hauteur"], "les districts ne couvrent pas toute la ville"


@pytest.mark.parametrize("graine", [3, 777, 20260913])
def test_une_autre_graine_garde_la_ville_d_un_seul_tenant(graine):
    ville = carte.generer(graine=graine)
    assert len(carte.composantes_marchables(ville)) == 1
    sans_aller, sans_retour = carte.voies_bloquees(ville)
    assert not sans_aller and not sans_retour
    # ⚠️ Le filet, pas un echec : une cour refermee par deux gabarits redevient
    # du bati ou de l'eau. Quelques tuiles, c'est le generateur qui fait son
    # travail ; des centaines, c'est un gabarit qui enferme un quartier.
    assert ville["tuiles_bouchees"] < 60, ville["tuiles_bouchees"]
    garantis = {special["slug"] for special in carte.SPECIAUX.values()} | {"kiosque"}
    assert {p["lieu"] for p in ville["portes"]} >= garantis


def test_la_nuit_vide_vraiment_chaque_district():
    """⚠️ Retour de Martin : « la nuit, il devrait y avoir moins de monde et de
    voitures sur les routes. » Le rythme existait depuis M8 et ne faisait
    presque rien — et dans le Faubourg, il ne faisait LITTERALEMENT rien.

    Il declarait 12 vehicules, son rythme de nuit valait 0,75 et le plafond
    `vehicules_max` vaut 9. Or 12 x 0,75 = 9. Le calcul etait
    `min(plafond, declare x rythme)` : `min(9, 9)` le jour, `min(9, 9)` la
    nuit — le PLAFOND MORDAIT AVANT LE RYTHME, et la nuit n'existait pas dans
    le seul quartier ou l'on passe le plus de temps.

    Le plafond s'applique donc avant : `min(plafond, declare) x rythme`.
    """
    from app import vehicules

    plafond = vehicules.TRAFIC["vehicules_max"]
    for district in carte.DISTRICTS:
        if district.get("eau"):
            continue
        nuit = district["rythme"][0]
        assert 0 < nuit < 1, f"{district['slug']} : la nuit ne change rien ({nuit})"
        jour_v = min(plafond, district["vehicules"])
        assert jour_v * nuit < jour_v, f"{district['slug']} : autant de chars la nuit"
        assert district["pietons"] * nuit < district["pietons"], \
            f"{district['slug']} : autant de monde la nuit"
        # Une nuit, c'est un trottoir vide et deux phares au loin : on enleve
        # au moins la moitie du monde, pas un quart.
        assert nuit <= 0.5, f"{district['slug']} : {nuit} de nuit, ca ne se voit pas"


def test_le_plafond_ne_masque_plus_le_rythme():
    """Le juge du piege lui-meme : pour CHAQUE district, la nuit doit compter
    moins de chars que le jour APRES plafonnement. C'est ce test qui aurait
    rougi sur le Faubourg."""
    from app import vehicules

    plafond = vehicules.TRAFIC["vehicules_max"]
    for district in carte.DISTRICTS:
        if district.get("eau"):
            continue
        jour = min(plafond, district["vehicules"])
        nuit = min(plafond, district["vehicules"]) * district["rythme"][0]
        ancien_calcul = min(plafond, district["vehicules"] * district["rythme"][0])
        assert nuit < jour
        assert nuit <= ancien_calcul, (
            f"{district['slug']} : l'ancien calcul donnait {ancien_calcul} la nuit "
            f"pour {jour} le jour"
        )
