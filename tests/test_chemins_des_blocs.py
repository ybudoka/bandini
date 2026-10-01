"""Les chemins des blocs (docs/jalons/une-route-en-lacets-vers-le-chalet.md) : une courbe douce posée
sur la grille d'un bloc — son glyphe, son tracé, sa lisière, son bois."""

import math

from app import blocs, carte


def test_le_chemin_roule_n_est_ni_terre_ni_rue_ni_mur():
    """⚠️ Pas de la `terre` : une auto y roule à pleine vitesse (l'herbe du rang la ralentit). Pas une
    `route` : aucun trafic ne s'y engage, et `sortie_sans_rue` ne le compte pas. Et on marche dessus."""
    g = carte.LEGENDE["§"]
    assert not g.get("terre") and not g.get("route") and not g.get("solide"), g
    assert carte.LEGENDE["g"].get("terre"), "le g des allées de la ville a changé"


#: Un bloc de 30 x 20 tuiles, tout en herbe, des arbres (`A`) et un buisson (`b`) sur le passage d'un
#: chemin qui traverse d'ouest en est en faisant une bosse vers le sud.
PETIT = {
    "slug": "essai", "nom": "Essai",
    "plan": tuple(
        "".join("A" if (x, y) in {(10, 10), (11, 11), (20, 8)} else "b" if (x, y) == (15, 12) else ","
                for x in range(30))
        for y in range(20)),
    "decors": {"A": (",", "arbre"), "b": (",", "buisson")},
    "chemins": [{"points": [(0, 8), (10, 10), (20, 10), (30, 8)], "largeur": 3, "sol": "§",
                 "bois": [[0, 0, 30, 20]], "haie": 2, "arbre": "A"}],
    "passage": {"bord": "ouest", "de": 7, "l": 3}, "retour": {"bord": "ouest", "de": 7, "l": 3},
    "arrivee": {"x": 1, "y": 8},
}


def test_l_echantillon_suit_les_points_a_pas_regulier():
    pts = blocs.echantillonner([(0, 8), (10, 10), (20, 10), (30, 8)])
    assert pts[0] == (0.0, 128.0) and pts[-1] == (480.0, 128.0)
    pas = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    assert max(pas) <= 4.5 and min(pas) > 0, (min(pas), max(pas))
    # La courbe passe PAR chaque point de passage.
    for x, y in [(10, 10), (20, 10)]:
        assert min(math.dist(p, (x * 16, y * 16)) for p in pts) < 1


def test_la_chaussee_la_lisiere_et_la_haie():
    plan = blocs.plan_du_bloc(PETIT)
    d = blocs.distances_au_chemin(PETIT["chemins"][0], 30, 20)
    demi = 1.5 * 16
    for (x, y), dist in d.items():
        if dist <= demi:
            assert plan[y][x] == "§", ((x, y), dist, plan[y][x])
        elif dist <= demi + 16:
            assert plan[y][x] == ",", ("la lisière n'est pas dégagée", (x, y), plan[y][x])
        elif dist <= demi + 16 + 2 * 16:
            assert plan[y][x] == "A", ("un trou dans la haie", (x, y), plan[y][x])
    # Les arbres et le buisson SUR le chemin sont partis ; celui de loin (20, 8) reste un arbre.
    assert plan[10][10] == "§" and plan[12][15] in ",§"
    assert blocs.sol_du_bloc(PETIT)[10][10] == "§"
    assert (10, 10) not in {(e["x"], e["y"]) for e in blocs.decor_du_bloc(PETIT)}


def test_un_buisson_dans_la_haie_devient_un_arbre():
    """⚠️ Un char traverse un buisson : resté buisson au milieu de la haie, il y faisait un trou (au rang, le
    30 sept. 2026, on coupait la boucle des lacets par deux buissons du bois)."""
    demi = 1.5 * 16
    d = blocs.distances_au_chemin(PETIT["chemins"][0], 30, 20)
    x, y = min(t for t, e in d.items() if demi + 16 < e <= demi + 3 * 16)
    plan = [list(ligne) for ligne in PETIT["plan"]]
    plan[y][x] = "b"
    assert blocs.plan_du_bloc({**PETIT, "plan": tuple("".join(ligne) for ligne in plan)})[y][x] == "A"


def test_hors_du_bois_pas_de_haie():
    sans_bois = {**PETIT, "chemins": [{**PETIT["chemins"][0], "bois": [[0, 0, 5, 20]]}]}
    plan = blocs.plan_du_bloc(sans_bois)
    assert "A" not in "".join(ligne[6:] for ligne in plan[13:]), "une haie hors de la zone du bois"


def test_le_paquet_du_bloc_porte_le_trace_en_pixels():
    c = blocs.carte_du_bloc(PETIT)
    (ch,) = c["bloc"]["chemins"]
    assert ch["largeur_px"] == 48
    assert ch["points"][0] == [0.0, 128.0] and len(ch["points"]) > 100
    assert c["sol"][10][10] == "§"


def test_un_bloc_sans_chemin_n_a_pas_change():
    for b in blocs.BLOCS:
        if not b.get("chemins"):
            assert blocs.plan_du_bloc(b) == list(b["plan"]), b["slug"]


def test_erreurs_denonce_un_virage_trop_serre_et_un_decor_sur_la_route():
    serre = {**PETIT, "chemins": [{**PETIT["chemins"][0], "points": [(0, 8), (10, 8), (10.5, 12), (0, 12)]}]}
    assert any("virage" in f for f in blocs.erreurs(serre)), blocs.erreurs(serre)
    # Un décor qu'on ne dégage pas (une corde de bois) posé sur la chaussée.
    corde = {**PETIT, "decors": {**PETIT["decors"], "L": (",", "corde_bois")},
             "plan": tuple(ligne[:12] + ("L" if y == 10 else ligne[12]) + ligne[13:]
                           for y, ligne in enumerate(PETIT["plan"]))}
    assert any("sur le chemin" in f for f in blocs.erreurs(corde)), blocs.erreurs(corde)
    assert not [f for f in blocs.erreurs(PETIT) if "chemin" in f or "virage" in f], blocs.erreurs(PETIT)
