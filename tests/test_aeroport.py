"""L'aéroport de Baie-des-Brumes : la carte grandit au sud, et elle reste fermée.

⚠️ Deux promesses, et un juge pour chacune de leurs moitiés :

- **la ville d'avant ne bouge pas** — l'aéroport se pose en dernier, sans un dé,
  et seules les quatre colonnes du pont changent dans la carte d'hier ;
- **on n'y entre pas** — le pont s'arrête au-dessus de l'eau, le barbelé ferme
  tout sauf la guérite, et la guérite attend une mission qui n'existe pas encore.
  Chaque étage se juge SEUL, avec son témoin : ce qui ferme quand il est là
  s'ouvre quand on l'enlève.
"""

from __future__ import annotations

from collections import deque

import pytest

from app import aeroport, carte, economie, missions, recherche


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


@pytest.fixture(scope="module")
def sans(ville):
    """La même ville, l'aéroport jamais posé."""
    pose = aeroport.poser
    aeroport.poser = lambda chantier, v: None
    try:
        return carte.generer()
    finally:
        aeroport.poser = pose


def dedans(r, x, y):
    return r["x"] <= x < r["x"] + r["l"] and r["y"] <= y < r["y"] + r["h"]


def test_la_ville_d_avant_ne_bouge_pas(ville, sans):
    """Tuile pour tuile, la carte d'hier est la même — sauf le tablier du pont, qui
    part de La Pointe au-dessus de l'eau. Et tout ce que l'aéroport ajoute
    s'ajoute AU BOUT des listes : rien d'autre ne bouge, pas même un arbre de rue."""
    a = ville["aeroport"]
    pont = a["pont"]
    assert ville["largeur"] == sans["largeur"]
    for y in range(sans["hauteur"]):
        if ville["sol"][y] == sans["sol"][y]:
            continue
        colonnes = [x for x in range(sans["largeur"]) if ville["sol"][y][x] != sans["sol"][y][x]]
        assert pont["y"] <= y and all(pont["x"] <= x < pont["x"] + pont["l"] for x in colonnes), (y, colonnes)
    assert ville["voie"][:sans["hauteur"]] == sans["voie"], "le champ de direction a bougé"
    ajouts = ("decor", "portes", "points_interet", "lampes", "toits", "residences", "zones", "barrieres",
              "devantures")
    for cle in ajouts:
        assert ville[cle][:len(sans[cle])] == sans[cle], f"« {cle} » a bougé avant l'aéroport"
    for cle in sans:
        if cle in ("sol", "voie", "hauteur", "interieurs", "aeroport") + ajouts:
            continue
        assert ville[cle] == sans[cle], f"« {cle} » a bougé"
    assert {k: v for k, v in ville["interieurs"].items() if k not in aeroport.PIECES} == sans["interieurs"]


def test_la_carte_grandit_au_sud_et_ce_qu_elle_gagne_est_de_l_eau(ville, sans):
    """La carte s'allonge jusqu'au bas du plan ; hors du plan, ce qu'elle gagne est
    de l'eau, sans une flèche."""
    x0, y0, largeur, hauteur = a_plan = ville["aeroport"]["plan"]
    assert ville["hauteur"] == y0 + hauteur > sans["hauteur"], a_plan
    assert len(ville["sol"]) == len(ville["voie"]) == ville["hauteur"]
    pont = ville["aeroport"]["pont"]
    for y in range(sans["hauteur"], ville["hauteur"]):
        assert set(ville["voie"][y]) == {"."}, y
        for x in range(ville["largeur"]):
            if x0 <= x < x0 + largeur and y >= y0:
                continue
            if pont["x"] <= x < pont["x"] + pont["l"]:
                continue
            assert ville["sol"][y][x] == "~", (x, y)


def test_le_pont_prolonge_une_rue_de_la_pointe_et_le_trafic_ne_le_connait_pas(ville):
    """Le tablier part du trottoir sud de la rue du bord de l'eau, sous la rue qui y
    finit en T, avec la coupe d'une rue de sa largeur. Et pas une flèche dessus :
    le trafic ne sait pas qu'il existe."""
    pont = ville["aeroport"]["pont"]
    coupe = carte._coupe(pont["l"], True)
    zone = next(z for z in ville["zones"] if z["slug"] == "pointe")
    assert dedans(zone, pont["x"], pont["y"] - 1), "le pont ne part pas de La Pointe"
    for d in range(pont["l"]):
        assert ville["sol"][pont["y"] - 1][pont["x"] + d] == "."
        assert carte.routier(ville["sol"][pont["y"] - 2][pont["x"] + d]), "pas de rue au nord du trottoir"
        # La rue qu'il prolonge descend jusqu'à la rue du bord de l'eau.
        assert carte.routier(ville["sol"][pont["y"] - 5][pont["x"] + 1])
    bout = pont["y"] + pont["nord"] + pont["trou"]
    for y in list(range(pont["y"], pont["y"] + pont["nord"])) + list(range(bout, bout + pont["sud"])):
        for d, (glyphe, _) in enumerate(coupe):
            assert ville["sol"][y][pont["x"] + d] == ("Q" if glyphe == "." else glyphe), (d, y)
            assert ville["voie"][y][pont["x"] + d] == ".", "une flèche sur un pont fermé"


def test_le_chantier_a_six_piles_et_ne_se_franchit_qu_a_la_nage_bien_nourri(ville):
    """⚠️ Le deuxième étage — « ajoute 4 sections de plus de pont en construction »
    (Martin, 21 sept. 2026) : six piles, une toutes les cinq tuiles, sur trente-deux
    tuiles d'EAU entre le bout du tablier et celui de l'île. Pas une rampe sur le pont
    ni devant, et même lancée sur une rampe, aucune moto ne saute ça (sa réception,
    `carte.RECEPTION_DEFI`, fait 13 tuiles). À la nage : ni à jeun, ni au seul café —
    le café ET l'estomac plein, et de justesse. La guérite attend de l'autre côté."""
    pont = ville["aeroport"]["pont"]
    sol = ville["sol"]
    for y in range(pont["y"] + pont["nord"], pont["y"] + pont["nord"] + pont["trou"]):
        assert all(sol[y][pont["x"] + d] == "~" for d in range(pont["l"])), y
    rangees = sorted({y for _, y in pont["piles"]})
    assert len(rangees) == 6, rangees
    assert all(b - a == 5 for a, b in zip(rangees, rangees[1:])), rangees
    assert rangees[0] - (pont["y"] + pont["nord"]) == 3 and pont["y"] + pont["nord"] + pont["trou"] - 1 - rangees[-1] == 3
    abords = {"x": pont["x"] - 3, "y": pont["y"] - 8, "l": pont["l"] + 6, "h": pont["nord"] + 8}
    assert not [r for r in ville["rampes"] if dedans(abords, r["x"], r["y"])], "une rampe devant le chantier"
    assert not any(carte.LEGENDE[sol[y][x]].get("rampe") for y in range(abords["y"], abords["y"] + abords["h"])
                   for x in range(abords["x"], abords["x"] + abords["l"]))
    assert pont["trou"] > carte.RECEPTION_DEFI, "une moto lancée saute le chantier"
    # La nage : la première et la dernière tuile sont de l'eau basse (`Monde.eauBasse`).
    a_payer = pont["trou"] - 2
    endurance = recherche.VITESSES["endurance"]
    assert a_payer * cout_par_tuile() > endurance, "le chantier se nage à jeun"
    assert a_payer * cout_par_tuile(cafe=True) > endurance, "le chantier se nage au seul café"
    assert a_payer * cout_par_tuile(cafe=True) <= endurance + economie.SOUFFLE["surplus_max"], (
        "même avec le café et l'estomac plein, le chantier ne se nage plus")


def cout_par_tuile(cafe: bool = False) -> float:
    """Ce qu'une tuile d'eau coute de souffle (la formule de `test_eau`)."""
    depense = economie.CAFE["depense"] if cafe else 1.0
    return carte.TUILE_PX / recherche.NAGE["vitesse"] * recherche.NAGE["souffle_par_image"] * depense


def test_de_la_rive_de_la_pointe_l_ile_ne_se_nage_pas(ville):
    """⚠️ Le cinquième étage : le large. De n'importe quelle rive de la ville — le
    tablier inachevé mis à part —, l'île de l'aéroport est plus loin que ce qu'on
    nage avec le café ET l'estomac plein."""
    sol = ville["sol"]
    pont = ville["aeroport"]["pont"]
    tablier = {(x, y) for x in range(pont["x"], pont["x"] + pont["l"])
               for y in range(pont["y"], pont["y"] + pont["nord"])}
    bout = pont["y"] + pont["nord"] + pont["trou"]
    bout_du_pont = {(x, y) for x in range(pont["x"], pont["x"] + pont["l"]) for y in range(bout, bout + pont["sud"])}
    terres = carte.composantes_par_terre(ville)
    rives = set().union(*terres["ville"]) - tablier
    # L'île, pas le bout du pont : lui se rejoint par la travée, et c'est voulu.
    arrivee = set().union(*terres["aeroport"]) - bout_du_pont
    dist = {t: 0 for t in rives}
    file = deque(rives)
    nage = None
    while file and nage is None:
        x, y = file.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in dist or not (0 <= n[0] < ville["largeur"] and 0 <= n[1] < ville["hauteur"]):
                continue
            if n in arrivee:
                nage = dist[(x, y)]
                break
            if sol[n[1]][n[0]] != "~" or n in tablier or n in bout_du_pont:
                continue
            dist[n] = dist[(x, y)] + 1
            file.append(n)
    assert nage is not None, "l'île ne se voit d'aucune rive ?"
    barre = recherche.VITESSES["endurance"] + economie.SOUFFLE["surplus_max"]
    assert (nage - 2) * cout_par_tuile(cafe=True) > barre, (
        f"{nage} tuiles d'eau de la rive à l'île : avec le café et l'estomac plein, "
        f"{(nage - 2) * cout_par_tuile(cafe=True):.0f} points sur {barre} — on y va à la nage")


def test_on_n_y_va_pas_a_pied(ville):
    """Une troisième terre : d'un seul tenant, et que rien ne relie à la ville.
    Le bout du pont côté île est à elle, celui de La Pointe à la ville."""
    terres = carte.composantes_par_terre(ville)
    assert len(terres["ville"]) == 1 and len(terres["aeroport"]) == 1, {t: len(g) for t, g in terres.items()}
    pont = ville["aeroport"]["pont"]
    assert (pont["x"], pont["y"]) in terres["ville"][0]
    assert (pont["x"], pont["y"] + pont["nord"] + pont["trou"]) in terres["aeroport"][0]
    aerogare = next(p for p in ville["points_interet"] if p["slug"] == "aeroport")
    assert (aerogare["x"], aerogare["y"]) in terres["aeroport"][0]


def _a_pied_depuis_le_bout_du_pont(ville, murs=frozenset()):
    """Ce qu'on atteint à pied en sortant de l'eau au bout du pont côté île, les
    `murs` en plus — en ENJAMBANT ce qui s'enjambe, comme un vrai piéton."""
    sol = ville["sol"]
    pont = ville["aeroport"]["pont"]
    depart = (pont["x"] + 1, pont["y"] + pont["nord"] + pont["trou"])
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in vus or n in murs or not (0 <= n[1] < ville["hauteur"] and 0 <= n[0] < ville["largeur"]):
                continue
            if not carte.franchissable(sol[n[1]][n[0]]):
                continue
            vus.add(n)
            file.append(n)
    return vus


def test_le_barbele_ferme_tout_sauf_la_guerite(ville):
    """⚠️ Les troisième et quatrième étages. Sorti de l'eau au bout du pont, la
    guérite fermée : l'aérogare est hors d'atteinte, même en enjambant ce qui
    s'enjambe. Le TÉMOIN : la guérite levée, on y va — c'est donc bien elle, et
    seulement elle, qui ferme le barbelé."""
    guerite = next(b for b in ville["barrieres"] if b["slug"] == "aeroport")
    murs = {(x, y) for x in range(guerite["x"], guerite["x"] + guerite["l"])
            for y in range(guerite["y"], guerite["y"] + guerite["h"])}
    aerogare = next(p for p in ville["points_interet"] if p["slug"] == "aeroport")
    assert (aerogare["x"], aerogare["y"]) not in _a_pied_depuis_le_bout_du_pont(ville, murs)
    assert (aerogare["x"], aerogare["y"]) in _a_pied_depuis_le_bout_du_pont(ville), "le témoin ne mord pas"
    # La guérite est une OUVERTURE du barbelé : du barbelé à sa gauche et à sa droite.
    sol = ville["sol"]
    assert sol[guerite["y"]][guerite["x"] - 1] == "X" and sol[guerite["y"]][guerite["x"] + guerite["l"]] == "X"
    assert "X" not in carte.ENJAMBABLES


def test_les_barrieres_de_l_aeroport_attendent_les_missions_a_venir(ville):
    """Le premier et le quatrième étage : deux fiches du catalogue des barrières,
    résolues par l'aéroport, qui attendent des missions DÉCLARÉES et pas écrites."""
    fiches = {b["slug"]: b for b in carte.BARRIERES if "aeroport" in b["ou"]}
    posees = {b["slug"]: b for b in ville["barrieres"]}
    assert set(fiches) == {"pont_aeroport", "aeroport"} and set(fiches) <= set(posees)
    ecrites = {m["slug"] for m in missions.CATALOGUE}
    for slug, fiche in fiches.items():
        attend = fiche["condition"]["apres"]
        assert attend in aeroport.MISSIONS_A_VENIR and attend not in ecrites, slug
        assert set(fiche["arrete"]) == {"pieton", "vehicule"}, slug
    pont = ville["aeroport"]["pont"]
    tete = posees["pont_aeroport"]
    assert (tete["x"], tete["y"], tete["l"], tete["h"]) == (pont["x"], pont["y"], pont["l"], 1)
    # La barricade se force (un chantier, pas un crime : aucune étoile) ; la guérite, non.
    assert fiches["pont_aeroport"]["forcer"] and not fiches["pont_aeroport"]["forcer"].get("etoiles")
    assert fiches["aeroport"]["forcer"] is None


def test_l_aerogare_est_un_lieu_et_elle_a_sa_piece(ville):
    """Le seul bâtiment qui s'ouvre : un repère de la carte (famille transport), une
    porte, et la pièce que les missions de l'arc A attendent. Les autres portes de
    l'aéroport sont peintes et fermées."""
    points = [p for p in ville["points_interet"] if dedans(ville["aeroport"], p["x"], p["y"])]
    assert [(p["slug"], p["famille"]) for p in points] == [("aeroport", "transport")]
    portes = [p for p in ville["portes"] if dedans(ville["aeroport"], p["x"], p["y"])]
    assert [(p["lieu"], p["interieur"]) for p in portes] == [("aeroport", "aerogare")]
    assert ville["interieurs"]["aerogare"] is aeroport.PIECES["aerogare"]
    enseignes = [d for d in ville["devantures"] if dedans(ville["aeroport"], d["x"], d["y"])]
    assert [(d["texte"], "D" in d["motifs"]) for d in enseignes] == [("AÉROPORT", True)]
    tour = [t for t in ville["toits"] if t["type"] == "tour_controle"]
    assert len(tour) == 1 and dedans(ville["aeroport"], tour[0]["x"], tour[0]["y"])


def test_ce_qui_ne_s_ouvre_pas_est_peint_et_rien_n_y_nait(ville):
    """⚠️ Les portes fermées, les arbres et la manche à air sont PEINTS : pas un
    décor dans la liste de la ville, pas une porte `d` au sol. Le jeu crée tout le
    décor au chargement et tire au hasard dans toutes les portes `d` : quinze
    entités et quatre portes de plus au bout décalaient le hasard de la ville
    entière, et cinq juges sans rapport sont tombés."""
    a = ville["aeroport"]
    assert not [d for d in ville["decor"] if dedans(a, d["x"], d["y"])]
    assert not any("d" in ligne for ligne in ville["sol"][a["y"]:a["y"] + a["h"]])
    assert sum(ligne.count("D") for ligne in ville["sol"][a["y"]:a["y"] + a["h"]]) == 1, "l'aérogare seule s'ouvre"
    sol = ville["sol"]
    assert len(a["portes_peintes"]) == 4
    for x, y, large in a["portes_peintes"]:
        assert carte.solidite(sol[y][x]) == 1 and sol[y + 1][x] not in "FWBEOP", (x, y)
    assert sorted({t for t, _, _ in a["peints"]}) == ["arbre", "manche_a_air"]
    for _, x, y in a["peints"]:
        assert carte.marchable(sol[y][x]) and not carte.routier(sol[y][x]), (x, y)


def test_la_zone_de_l_aeroport_est_surveillee(ville):
    """Pas un refuge : l'aéroport a sa police. Et le large, que la carte a gagné,
    n'a personne."""
    zones = {z["slug"]: z for z in ville["zones"]}
    a, large = zones["aeroport"], zones["large"]
    assert a["police"] > 0 and not a.get("refuge")
    assert (a["x"], a["y"], a["l"], a["h"]) == tuple(ville["aeroport"][k] for k in ("x", "y", "l", "h"))
    assert large["pietons"] == large["vehicules"] == large["police"] == 0
    assert [z["slug"] for z in ville["zones"]][-2:] == ["large", "aeroport"], "l'aéroport doit passer après le large"


def test_ce_que_le_dessin_lit(ville):
    """La piste, l'axe jaune, les avions et les balises voyagent dans le paquet, et
    ce sont bien des tuiles d'asphalte de l'aéroport."""
    a = ville["aeroport"]
    sol = ville["sol"]
    p = a["piste"]
    assert p["l"] > 100 and p["h"] == 6
    assert all(sol[y][x] == "#" for y in range(p["y"], p["y"] + p["h"]) for x in range(p["x"], p["x"] + p["l"]))
    assert len(a["avions"]) == len(aeroport.AVIONS)
    for v in a["avions"]:
        assert sol[v["y"]][v["x"]] == "#" and v["modele"] and v["livree"], v
    for s in a["axes"]:
        assert s[0] == s[2] or s[1] == s[3], s
        assert all(sol[y][x] == "#" for y in range(min(s[1], s[3]), max(s[1], s[3]) + 1)
                   for x in range(min(s[0], s[2]), max(s[0], s[2]) + 1)), s
    balises = [lampe for lampe in ville["lampes"] if lampe.get("c") == "balise"]
    assert len(balises) == len(a["balises"]) > 20
    assert all(dedans(p, b["x"], b["y"]) for b in balises)


@pytest.mark.parametrize("graine", [3, 777, 2026])
def test_une_autre_graine_a_le_meme_aeroport(graine, ville):
    """L'aéroport est dessiné : à la même place d'une graine à l'autre. ⚠️ Et le pont
    part parfois du SABLE : sur ces graines-là, la plage de La Pointe descend sous
    le tablier, et ce qui y traînait a déménagé — plus rien sur le pont ni à son flanc."""
    autre = carte.generer(graine=graine)
    for cle in ("x", "y", "l", "h", "plan", "piste", "avions", "pont"):
        assert autre["aeroport"][cle] == ville["aeroport"][cle], cle
    pont = autre["aeroport"]["pont"]
    flanc = {"x": pont["x"] - 1, "y": pont["y"], "l": pont["l"] + 2, "h": pont["nord"]}
    assert not [d for d in autre["decor"] if dedans(flanc, d["x"], d["y"])]
    assert all(len(g) == 1 for g in carte.composantes_par_terre(autre).values())


def test_la_carte_cache_l_ile_jusqu_au_pont_fini(ville, sans):
    """« La carte de l'aéroport peut-elle être masquée » (Martin) : l'île ENTIÈRE, bout
    du pont compris, jusqu'au pont fini. Python dit quoi cacher et jusqu'à quand : le
    rectangle de la terre de l'aéroport, la mission `a01`, et la hauteur de la carte
    connue — sous elle, hors de l'île, il n'y a QUE de l'eau (la grande carte s'y arrête
    sans rien cacher d'autre)."""
    a = ville["aeroport"]
    m = a["masque"]
    assert (m["x"], m["y"], m["l"], m["h"]) == (a["x"], a["y"], a["l"], a["h"])
    assert m["apres"] in aeroport.MISSIONS_A_VENIR
    assert m["apres"] == next(b for b in carte.BARRIERES if b["slug"] == "pont_aeroport")["condition"]["apres"], (
        "l'île doit apparaître le jour où le pont se finit, pas un autre")
    assert m["carte_h"] == sans["hauteur"] <= m["y"]
    aerogare = next(p for p in ville["points_interet"] if p["slug"] == "aeroport")
    assert dedans(m, aerogare["x"], aerogare["y"])
    pont = a["pont"]
    assert pont["y"] + pont["nord"] <= m["carte_h"], "le tablier de La Pointe se voit : il est de ce côté-ci"
    for y in range(m["carte_h"], ville["hauteur"]):
        for x in range(ville["largeur"]):
            if not dedans(m, x, y):
                assert ville["sol"][y][x] == "~", f"la grande carte coupe autre chose que de l'eau en {(x, y)}"


def test_les_missions_a_venir_sont_celles_de_l_arc_a():
    """Des slugs d'arc A (`a01`…), chacun avec ce qu'il ouvrira — c'est la fiche
    que la mission, le jour où elle s'écrit, viendra relire."""
    assert aeroport.MISSIONS_A_VENIR
    for slug, quoi in aeroport.MISSIONS_A_VENIR.items():
        assert slug[0] == "a" and slug[1:].isdigit() and len(quoi) > 20, slug
