"""Les machines distributrices, et l'hopital qui soigne du monde.

Demande de Martin (16 sept. 2026) : « l'hopital devrait etre plus grand et avec
des malades, une salle d'attente, des solutes, machines de sante. Ajoute aussi un
concept de machine distributrice partout dans la ville. »

⚠️ Mesure avant : l'hopital faisait 11 x 8 tuiles, deux lits de bois, trois
chaises et pas un malade ; la ville n'avait AUCUNE distributrice. Ces juges
tiennent les deux promesses de la demande, et les regles qui les rendent
honnetes : une machine vend au prix du comptoir, une nuit a les defoncer toutes
ne vaut pas une journee de travail, et chaque malade est couche dans un lit, pas
debout a cote.
"""

from collections import Counter
from itertools import combinations

import pytest

from app import carte, devantures, economie, magasins, recherche

FICHE = economie.DISTRIBUTRICE
GRAINES = (carte.GRAINE, 1, 2)


@pytest.fixture(scope="module", params=GRAINES)
def ville(request):
    return carte.generer(graine=request.param)


def _machines(ville):
    decors = {fiche["decor"]: sorte for sorte, fiche in magasins.DISTRIBUTRICES.items()}
    return [(d, decors[d["type"]]) for d in ville["decor"] if d["type"] in decors]


# --- Le catalogue ------------------------------------------------------------


def test_une_machine_vend_au_prix_du_comptoir():
    """Chaque article pointe dans `economie.TARIFS`, comme au comptoir — une
    liqueur coute le meme prix a la machine qu'a la glaciere du depanneur, et
    ce qu'elle rend est ecrit une seule fois."""
    for sorte, fiche in magasins.DISTRIBUTRICES.items():
        assert fiche["articles"], f"{sorte} : une machine vide"
        for article in fiche["articles"]:
            assert article["tarif"] in economie.TARIFS, (sorte, article)
            for cle in ("gain_pv", "gain_souffle"):
                if article[cle]:
                    assert article[cle] in economie.TARIFS, (sorte, article)
            if article["effet"]:
                assert article["effet"] in magasins.EFFETS, (sorte, article)


def test_une_machine_ne_nourrit_pas_mieux_que_le_kiosque():
    """La regle du trottoir, appliquee a la machine : au dollar, jamais mieux
    que le hot-dog. ⚠️ Le cafe est hors concours, pour la meme raison qu'au
    comptoir : on le paie pour l'effet qui dure."""
    tarifs = economie.TARIFS
    reference = (tarifs["hotdog_pv"] + tarifs["hotdog_souffle"]) / tarifs["hotdog"]
    for sorte, fiche in magasins.DISTRIBUTRICES.items():
        for article in fiche["articles"]:
            if article["effet"]:
                continue
            gain = tarifs.get(article["gain_pv"], 0) + tarifs.get(article["gain_souffle"], 0)
            assert gain / tarifs[article["tarif"]] <= reference, f"{sorte}/{article['slug']}"


def test_chaque_famille_de_devanture_a_sa_machine():
    """Sinon toute une couleur d'enseigne ne recevrait jamais de machine devant
    elle, et « partout dans la ville » voudrait dire « devant certains »."""
    for genre in devantures.GENRES:
        assert magasins.sortes_devant(genre["slug"]), f"aucune machine devant « {genre['slug']} »"


def test_une_machine_defoncee_rapporte_moins_qu_une_journee_honnete():
    """⚠️ Toutes les machines de la ville, une nuit, a la plus grosse monnaie :
    ca reste moins qu'une journee de proprietes. C'est de la monnaie — la
    caisse d'une banque, c'est le guichet."""
    pire = FICHE["par_ville"][1] * FICHE["monnaie"][1]
    assert pire < economie.revenu_honnete_par_jour(), f"{pire} $ la nuit"
    assert FICHE["monnaie"][1] < economie.GUICHET["caisse"][0], "une machine vaut un guichet"


def test_defoncer_une_machine_est_un_petit_delit():
    """Une etoile, et il faut un temoin qui aille le raconter : personne
    n'appelle la police pour trois canettes, sauf s'il a tout vu."""
    delit = recherche.DELITS["distributrice"]
    assert delit["etoiles"] == 1
    assert delit["temoin"] is True
    assert delit["etoiles"] < recherche.DELITS["guichet"]["etoiles"]


def test_la_spirale_et_la_secousse_sont_des_chances():
    assert 0 < FICHE["coincee"] < 0.5, "une machine qui garde l'argent une fois sur deux est un vol"
    assert 0 < FICHE["brasser"] <= 1


def test_le_paquet_porte_les_machines():
    from app import definitions
    donnees = definitions.assembler()
    assert donnees["distributrices"] == magasins.DISTRIBUTRICES
    e = donnees["economie"]["distributrice"]
    assert list(e["monnaie"]) == list(FICHE["monnaie"])
    assert e["coincee"] == FICHE["coincee"]


# --- La ville -----------------------------------------------------------------


def test_il_y_a_des_machines_partout_dans_la_ville(ville):
    """⚠️ Le juge de la demande : pas deux quartiers. Chaque district bati en a
    au moins une, et aucun n'en prend plus que son plafond."""
    machines = _machines(ville)
    lo, hi = FICHE["par_ville"]
    assert lo <= len(machines) <= hi, f"{len(machines)} machines"
    chantier = carte._Chantier(carte.PLAN, ville["graine"])
    par_district = Counter(chantier.district_en(d["x"], d["y"]) for d, _ in machines)
    batis = {d["slug"] for d in carte.DISTRICTS if not d.get("eau")}
    assert batis <= set(par_district), f"des quartiers sans machine : {batis - set(par_district)}"
    assert max(par_district.values()) <= FICHE["par_district"], par_district
    assert len(set(sorte for _, sorte in machines)) == len(magasins.DISTRIBUTRICES), "une sorte ne sort jamais"


def test_une_machine_est_adossee_a_une_devanture_et_laisse_passer(ville):
    """Contre le mur d'un commerce — jamais sous sa porte — et une rangee libre
    devant elle, pour qu'on l'atteigne et que la foule passe."""
    sol = ville["sol"]
    portes = {(p["x"], p["y"]) for p in ville["portes"]}
    # ⚠️ Et les portes PEINTES : a l'oeil, c'est une porte (la PIZZERIA NAPOLI).
    portes |= {(f["x"] + i, f["y"]) for f in ville["devantures"] + ville["residences"]
               for i, motif in enumerate(f["motifs"]) if motif == "P"}
    for d, sorte in _machines(ville):
        x, y = d["x"], d["y"]
        assert sol[y][x] in ("_", "."), f"une machine sur « {sol[y][x]} » en {x},{y}"
        assert carte.solidite(sol[y - 1][x]) == 1, f"une machine qui ne s'adosse a rien en {x},{y}"
        assert sol[y - 1][x] not in ("D", "d", "G") and (x, y - 1) not in portes, \
            f"une machine plantee devant une porte en {x},{y}"
        # ⚠️ Ni juste a cote : a moins de 22 px, elle volait ACTION a la porte.
        for dx in (-1, 1):
            assert sol[y - 1][x + dx] not in carte.PORTES_DE_FACADE and (x + dx, y - 1) not in portes, \
                f"une machine collee a une porte en {x},{y} — elle vole ACTION a l'entree"
        devant = sol[y + 1][x]
        assert devant in ("_", "."), f"rien pour se tenir devant la machine en {x},{y} (« {devant} »)"
        famille = next(devantures.GENRES[v["genre"]]["slug"] for v in ville["devantures"]
                       if v["y"] == y - 1 and v["x"] <= x < v["x"] + v["l"])
        assert sorte in magasins.sortes_devant(famille), f"{sorte} devant « {famille} »"


def test_deux_machines_ne_se_voisinent_pas_ni_un_guichet(ville):
    machines = [d for d, _ in _machines(ville)]
    for a, b in combinations(machines, 2):
        assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) >= FICHE["ecart"], (a, b)
    guichets = [d for d in ville["decor"] if d["type"] == "guichet"]
    for m in machines:
        for g in guichets:
            assert abs(m["x"] - g["x"]) + abs(m["y"] - g["y"]) >= FICHE["ecart_guichet"], (m, g)
    places = Counter((d["x"], d["y"]) for d in ville["decor"])
    for m in machines:
        assert places[(m["x"], m["y"])] == 1, f"une machine partage sa place en {m['x']},{m['y']}"


def test_une_machine_de_plus_ne_deplace_rien_d_autre():
    """⚠️ Elle tire dans SON de, apres tout le reste : sans machines, la ville
    est exactement la meme — les paquets, les kiosques et le reste du decor au
    meme endroit. C'est ce qui permet d'en regler le nombre sans toucher aux
    missions ni aux juges des autres."""
    # ⚠️ LES CARROSSERIES DES DEUX COTES : posees sur la ville finie, elles ecartent une
    # facade qui a une machine devant — une machine de plus les ferait changer de rue.
    carrosseries = carte._Chantier.poser_les_carrosseries
    carte._Chantier.poser_les_carrosseries = lambda self, ville_: []
    try:
        avec = carte.generer()
        decors = {fiche["decor"] for fiche in magasins.DISTRIBUTRICES.values()}
        sauve = carte._Chantier.distributrices
        try:
            carte._Chantier.distributrices = lambda self: 0
            sans = carte.generer()
        finally:
            carte._Chantier.distributrices = sauve
    finally:
        carte._Chantier.poser_les_carrosseries = carrosseries
    assert [d for d in avec["decor"] if d["type"] not in decors] == sans["decor"]
    assert avec["paquets"] == sans["paquets"]
    assert avec["ambulants"] == sans["ambulants"]
    assert avec["sol"] == sans["sol"]


def test_les_salles_d_attente_ont_leur_machine():
    """Le terminus (la premiere piece du jeu), le poste et l'urgence."""
    for slug, voulues in (("terminus", 1), ("poste", 1), ("hopital", 2)):
        piece = carte.INTERIEURS[slug]
        points = [p for p in piece["points"] if p["type"] == "distributrice"]
        assert len(points) == voulues, f"{slug} : {len(points)} machines"
        for p in points:
            assert p["sorte"] in magasins.DISTRIBUTRICES, (slug, p)
            assert piece["sol"][p["y"]][p["x"]] == "b", f"{slug} : le point de la machine n'est pas sur la machine"


# --- L'hopital ------------------------------------------------------------------


def _suite_de_l_hopital():
    return [carte.INTERIEURS[s] for s in carte.suite_de("hopital")]


def test_l_hopital_est_plus_grand_et_a_un_etage():
    """⚠️ 54 tuiles de plancher avant. Plus grand en PROFONDEUR et par un etage :
    l'ilot fait douze tuiles de large, et une piece a exactement les mesures de
    son batiment (`test_la_piece_a_les_mesures_de_son_batiment`)."""
    suite = _suite_de_l_hopital()
    assert len(suite) >= 2, "l'hopital n'a plus d'etage"
    plancher = sum(large * haut for large, haut in (carte.mesures_de(p) for p in suite))
    assert plancher >= 3 * 54, f"{plancher} tuiles de plancher"


def test_l_hopital_a_des_malades_couches_dans_des_lits():
    malades = [(p, g) for p in _suite_de_l_hopital() for g in p["gens"] if g["qui"] == "malade"]
    assert len(malades) >= 6, f"{len(malades)} malades"
    for piece, g in malades:
        sol = piece["sol"]
        assert sol[g["y"]][g["x"]] == "r" and sol[g["y"] + 1][g["x"]] == "r", (piece["slug"], g)
    lits = sum(1 for p in _suite_de_l_hopital() for y, ligne in enumerate(p["sol"])
               for x, glyphe in enumerate(ligne) if glyphe == "r" and p["sol"][y - 1][x] != "r")
    assert len(malades) == lits, "un lit d'hopital vide, ou deux malades dans le meme"


def test_chaque_malade_a_son_solute_et_son_moniteur():
    """Le materiel est AU CHEVET : la potence a l'ouest de la tete de lit (son
    tube file vers l'est), l'ecran a l'est."""
    for piece in _suite_de_l_hopital():
        sol = piece["sol"]
        for g in piece["gens"]:
            if g["qui"] != "malade":
                continue
            x, y = g["x"], g["y"]
            assert sol[y][x - 1] == "i", f"{piece['slug']} : pas de solute au chevet en {x},{y}"
            assert sol[y][x + 1] == "q", f"{piece['slug']} : pas de moniteur au chevet en {x},{y}"


def test_l_hopital_a_une_salle_d_attente_pleine():
    urgence = carte.INTERIEURS["hopital"]
    chaises = sum(ligne.count("h") for ligne in urgence["sol"])
    patients = [g for g in urgence["gens"] if g["qui"] == "patient"]
    assert chaises >= 12, f"{chaises} chaises"
    assert len(patients) >= 5, f"{len(patients)} patients"
    assert len(patients) < chaises, "une salle d'attente sans une chaise libre"
    assert any(g["qui"] == "soignant" for g in urgence["gens"]), "personne au triage"
    assert any(p["type"] == "soigner" for p in urgence["points"])


@pytest.mark.parametrize("qui, plan, bien, mal, reproche", [
    # Un malade au PIED du lit : la tete tomberait sur la couverture.
    ("malade", "BBBBBB\nB r  B\nB r  B\nB    B\nBBDBBB", (2, 1), (2, 2), "pied du lit"),
    # Un patient debout au milieu de la salle d'attente.
    ("patient", "BBBBBB\nB hh B\nB    B\nB    B\nBBDBBB", (3, 1), (3, 2), "n'est pas sur"),
])
def test_le_plan_refuse_un_malade_ou_un_patient_mal_pose(qui, plan, bien, mal, reproche):
    """⚠️ La regle est jugee AU CHARGEMENT, par `_piece` : on juge donc le juge.
    Le meme plan passe avec la personne bien posee — sinon on attraperait une
    autre faute et on croirait tenir celle-ci."""
    def poser(x, y):
        return carte._piece("essai", "Essai", plan, sol="u", points=(carte._pt("soigner", 4, 2),),
                            gens=carte._gens((qui, x, y)))
    assert poser(*bien)["gens"] == [{"qui": qui, "x": bien[0], "y": bien[1]}]
    with pytest.raises(ValueError, match=reproche):
        poser(*mal)
