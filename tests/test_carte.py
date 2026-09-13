from app import carte

CARTE = carte.exporter()


def test_rectangulaire_et_glyphes_connus():
    assert len(CARTE["sol"]) == CARTE["hauteur"]
    assert len(CARTE["voie"]) == CARTE["hauteur"]
    for ligne, voie in zip(CARTE["sol"], CARTE["voie"]):
        assert len(ligne) == CARTE["largeur"]
        assert len(voie) == CARTE["largeur"]
        assert set(ligne) <= set(carte.LEGENDE), set(ligne) - set(carte.LEGENDE)
        assert set(voie) <= carte.VOIES


def test_les_fleches_sont_sur_la_route_et_menent_quelque_part():
    for y, ligne in enumerate(CARTE["voie"]):
        for x, f in enumerate(ligne):
            if f == ".":
                continue
            assert carte.routier(CARTE["sol"][y][x]), (x, y)
            assert carte.suivre_voie(CARTE, x, y), f"cul-de-sac routier en {(x, y)}"


def test_tout_ce_qui_est_marchable_est_relie():
    groupes = carte.composantes_marchables(CARTE)
    principal = max(groupes, key=len)
    app = CARTE["apparition"]["joueur"]
    assert (app["x"], app["y"]) in principal
    for p in CARTE["portes"]:
        assert (p["x"], p["y"] + 1) in principal, p
    # Une petite ile de trottoir enclavee serait un bug : tout le marchable
    # doit etre le meme groupe, a un ecart pres (les tuiles sous les arbres).
    assert len(principal) >= 0.98 * sum(len(g) for g in groupes)


def test_les_portes_sont_des_tuiles_porte():
    for p in CARTE["portes"]:
        assert CARTE["sol"][p["y"]][p["x"]] == "D", p
        assert carte.marchable(CARTE["sol"][p["y"] + 1][p["x"]])
    for poi in CARTE["points_interet"]:
        assert carte.marchable(CARTE["sol"][poi["y"]][poi["x"]]), poi


def test_deterministe():
    assert carte.exporter() == CARTE
