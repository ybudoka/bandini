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
        glyphe = "^" if c["cap"] < 0 else "v"
        assert all(plan[y][x] == glyphe for x, y in tuiles), f"la case P{c['n']} n'est pas peinte"
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


def test_deux_rangees_face_a_face_autour_d_une_allee():
    """Martin, 30 sept. 2026 : « le stationnement me semble beaucoup trop grand. on pourrait mettre 2 rangées face à
    face ». Cinq cases au nord le nez au mur nord, cinq au sud le nez au mur sud, une allée de cinq tuiles entre les
    deux ; le tout plus petit que l'écran (centré, du noir autour, comme une pièce)."""
    cases, plan = souterrain.CASES, souterrain.PLAN
    nord = [c for c in cases if c["cap"] < 0]
    sud = [c for c in cases if c["cap"] > 0]
    assert [c["n"] for c in nord] == [1, 2, 3, 4, 5] and [c["n"] for c in sud] == [6, 7, 8, 9, 10]
    assert [c["x"] for c in nord] == [c["x"] for c in sud], "les deux rangées se font face, case pour case"
    bas_du_nord, haut_du_sud = nord[0]["y"] + nord[0]["h"], sud[0]["y"]
    assert haut_du_sud - bas_du_nord == 5, "une allée de cinq tuiles"
    for y in range(bas_du_nord, haut_du_sud):
        assert all(plan[y][x] == "#" for x in range(1, len(plan[0]) - 1)), f"l'allée est libre à la rangée {y}"
    assert len(plan[0]) * carte.TUILE_PX <= blocs.ECRAN_PX[0] and len(plan) * carte.TUILE_PX <= blocs.ECRAN_PX[1]
