"""Le 1er juillet, jour du déménagement, côté ville (docs/jalons/le-1er-juillet-jour-du-demenagement.md) :
les camions se garent à cheval sur le trottoir, jamais sur la chaussée ni devant une porte ; les meubles
à côté ; pas dans une rue cossue ; et le boulot tient l'économie."""

from app import calendrier, carte, demenagement, economie

VILLE = carte.exporter()
P = demenagement.places(VILLE, carte.LEGENDE)


def test_le_jour_est_le_1er_juillet_du_calendrier():
    assert demenagement.JOUR == calendrier.DATES["demenagement"]


def test_les_camions_sont_sur_le_trottoir_loin_des_portes_et_ecartes():
    sol, legende = VILLE["sol"], carte.LEGENDE
    assert len(P["camions"]) >= 8, P["camions"]
    decor = {(d["x"], d["y"]) for d in VILLE["decor"]}
    for cx, cy in P["camions"]:
        for x in (cx - 1, cx, cx + 1):
            fiche = legende[sol[cy][x]]
            assert fiche.get("trottoir") and not fiche.get("route"), f"un camion mord sur « {sol[cy][x]} » en {x, cy}"
            assert sol[cy - 1][x] not in "Dd", f"un camion devant une porte en {x, cy}"
            assert (x, cy) not in decor
    for i, a in enumerate(P["camions"]):
        for b in P["camions"][i + 1:]:
            assert abs(a[0] - b[0]) + abs(a[1] - b[1]) >= demenagement.ECART


def test_les_meubles_sur_le_trottoir_et_pas_dans_une_rue_cossue():
    sol, legende = VILLE["sol"], carte.LEGENDE
    assert P["meubles"] and {m[2] for m in P["meubles"]} <= set(demenagement.MEUBLES)
    assert len({m[2] for m in P["meubles"]}) >= 4, "tout le monde jette le même sofa"
    for x, y, _ in P["meubles"]:
        assert legende[sol[y][x]].get("trottoir") and not legende[sol[y][x]].get("route")
    cossues = [r for r in VILLE["residences"] if r.get("standing") == "+"]
    for cx, cy in P["camions"]:
        assert not any(r["y"] + 1 == cy and r["x"] <= cx - 2 <= r["x"] + r["l"] + 2 and abs(r["x"] + r["porte"] - cx) <= 2
                       for r in cossues), (cx, cy)


def test_sans_de_la_meme_ville_donne_les_memes_places():
    assert demenagement.places(carte.exporter(), carte.LEGENDE) == P


def test_le_demenageur_tient_l_economie():
    b = economie.BOULOTS["demenagement"]
    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    assert taxi <= economie.gain_boulot(b) <= 4 * taxi and b["vehicule"] == "camion"
    assert b["malus_choc"] >= 0.3, "des boîtes de vaisselle : une bosse doit coûter"
