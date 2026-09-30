"""Le grand garage souterrain, en Python (docs/jalons/le-grand-garage-souterrain.md) : le bloc tient debout, ses dix
cases sont peintes et se rejoignent, sa rampe et son ascenseur sont où la fiche le dit, le paquet le nomme sans
passage, et la sortie devant le rideau de Ti-Guy tombe sur la chaussée."""

from app import blocs, carte
from app.blocs import souterrain
from tests import villes


def test_le_souterrain_tient_debout():
    assert blocs.erreurs(souterrain.BLOC) == []


def test_il_n_est_pas_un_bloc_de_bord_de_ville():
    """⚠️ Pas dans `BLOCS` : les juges des blocs y exigent un passage sur un bord de la ville."""
    assert souterrain.BLOC not in blocs.BLOCS and souterrain.BLOC in blocs.SOUS_SOLS
    assert blocs.par_slug("souterrain") is souterrain.BLOC
    assert souterrain.BLOC["passage"] is None and souterrain.BLOC["seuil"] == "garage"


def test_dix_cases_peintes_qui_ne_se_chevauchent_pas_et_se_rejoignent():
    plan, cases = souterrain.PLAN, souterrain.CASES
    assert len(cases) == souterrain.PAR_NIVEAU == 10
    assert [c["n"] for c in cases] == list(range(1, 11))
    vues: set[tuple[int, int]] = set()
    a_pied = blocs.a_pied_depuis_l_arrivee(souterrain.BLOC)
    for c in cases:
        tuiles = {(c["x"] + i, c["y"] + j) for i in range(c["l"]) for j in range(c["h"])}
        assert all(plan[y][x] == "^" for x, y in tuiles), f"la case P{c['n']} n'est pas peinte"
        assert not tuiles & vues, f"la case P{c['n']} en chevauche une autre"
        assert tuiles <= a_pied, f"on ne rejoint pas la case P{c['n']}"
        vues |= tuiles


def test_la_rampe_au_nord_et_l_arrivee_au_bas_de_la_rampe():
    r, a = souterrain.BLOC["retour"], souterrain.BLOC["arrivee"]
    assert r["bord"] == "nord"
    assert r["de"] <= a["x"] < r["de"] + r["l"], "on arrive dans l'axe de la rampe"
    assert 2 <= a["y"] <= 5, "au bas de la rampe, pas dessus ni au milieu de l'allée"


def test_l_ascenseur_est_devant_ses_portes():
    s = souterrain.ASCENSEUR
    a_pied = blocs.a_pied_depuis_l_arrivee(souterrain.BLOC)
    for i in range(s["l"]):
        assert souterrain.PLAN[s["y"] + 1][s["x"] + i] == "D", "les portes de l'ascenseur, sous la rangée où l'on attend"
        assert (s["x"] + i, s["y"]) in a_pied


def test_la_carte_du_bloc_porte_ses_cases_et_son_abri():
    c = blocs.carte_du_bloc(souterrain.BLOC)
    assert c["bloc"]["abrite"] is True
    assert len(c["bloc"]["souterrain"]["cases"]) == 10 and c["bloc"]["souterrain"]["ascenseur"] == souterrain.ASCENSEUR
    assert blocs.carte_du_bloc(blocs.par_slug("rang"))["bloc"]["abrite"] is False


def test_le_paquet_nomme_le_sous_sol_sans_passage(paquet):
    b = next(b for b in paquet["blocs"] if b["slug"] == "souterrain")
    assert b["passage"] is None and b["seuil"] == "garage" and b["portes"] == []


def test_la_sortie_devant_le_rideau_tombe_sur_la_chaussee():
    """La sortie (`Blocs.retourEnVille`) : quatre tuiles devant la façade du rideau de Ti-Guy, au milieu de sa
    largeur — la chaussée, et rien de solide sur la longueur d'un char (une tuile de chaque côté)."""
    ville = villes.exporter()
    pg = next(p for p in ville["portes_garage"] if p["lieu"] == "garage")
    x, y = pg["x"] + pg["l"] // 2, pg["y"] + 4
    assert carte.LEGENDE[ville["sol"][y][x]].get("route"), ville["sol"][y][x]
    for dy in (-1, 0, 1):
        assert carte.LEGENDE[ville["sol"][y + dy][x]].get("solide", 0) == 0


def test_la_piece_du_garage_a_son_ascenseur_sur_le_plancher():
    ville = villes.exporter()
    piece = ville["interieurs"]["garage"]
    pt = next(p for p in piece["points"] if p["type"] == "ascenseur")
    sol = piece["sol"]
    assert carte.LEGENDE[sol[pt["y"]][pt["x"]]].get("solide", 0) == 0, "l'ascenseur s'attend debout, sur le plancher"
    assert sol[pt["y"] - 1][pt["x"]] == "B", "ses portes se peignent sur le mur, juste au nord"
