"""Un choix dans un dialogue (1er oct. 2026) — la FORME, jugée sur le catalogue et sur des fiches cassées exprès
(`missions.erreurs_de_choix`, cousu à `erreurs_de_mise_en_scene`)."""

import copy

from app import missions


def _d09():
    return copy.deepcopy(missions.par_slug("d09"))


def _question(m):
    return m["dialogue"]["accueil"][0]


def test_d09_pose_sa_question_et_chaque_reponse_change_la_mission():
    m = _d09()
    assert missions.erreurs_de_choix(m) == []
    partie, i, ligne = missions.question(m)
    assert (partie, i) == ("accueil", 0) and [r["cle"] for r in ligne["choix"]] == ["coucher", "payer"]
    # Chaque réponse a ses objectifs, et « payer » paie autrement : la question n'est pas pour la forme.
    assert {o.get("branche") for o in m["objectifs"]} == {None, "coucher", "payer"}
    assert m["branches"]["payer"]["donne"]["dette"] == -800 and m["branches"]["payer"]["recompense"] == 0


def test_tout_le_catalogue_tient_ses_choix():
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_choix(m) == [], m["slug"]


def test_le_paquet_ne_porte_ni_les_branches_ni_les_questions_mais_la_mission_les_apporte():
    paquet = next(m for m in missions.pour_le_navigateur() if m["slug"] == "d09")
    assert "branches" not in paquet and "dialogue" not in paquet
    jouee = missions.pour_jouer("d09")
    assert jouee["branches"]["payer"]["donne"]["dette"] == -800
    assert _question(jouee["dialogue"] and jouee)["choix"][1]["cle"] == "payer"
    assert "jeu" not in _question(jouee), "le jeu des voix ne voyage pas"


def _erreurs_apres(changer):
    m = _d09()
    changer(m)
    return " | ".join(missions.erreurs_de_choix(m))


def test_une_question_mal_posee_se_refuse():
    # Au combiné de l'appel, ou à la fin : il n'y a personne devant soi, ou plus rien à bifurquer.
    assert "en personne" in _erreurs_apres(lambda m: m["dialogue"]["fin"][0].update(choix=_question(m)["choix"]) or _question(m).pop("choix"))
    # Une réponse seule, ou quatre.
    assert "réponses" in _erreurs_apres(lambda m: _question(m)["choix"].pop())
    assert "réponses" in _erreurs_apres(lambda m: _question(m)["choix"].extend(
        [{"cle": "fuir", "texte": "JE M'EN VAIS."}, {"cle": "rire", "texte": "HA HA."}]))
    # En minuscules, ou trop longue pour sa ligne.
    assert "MAJUSCULES" in _erreurs_apres(lambda m: _question(m)["choix"][0].update(texte="tout de suite"))
    assert "MAJUSCULES" in _erreurs_apres(lambda m: _question(m)["choix"][0].update(texte="X" * 45))
    # Deux questions dans la même mission.
    assert "une question par mission" in _erreurs_apres(
        lambda m: m["dialogue"]["intro"][0].update(choix=_question(m)["choix"]))


def test_une_branche_doit_suivre_une_reponse_et_venir_apres_la_question():
    assert "n'est pas une réponse" in _erreurs_apres(lambda m: m["objectifs"][3].update(branche="fuir"))
    assert "avant que la question" in _erreurs_apres(lambda m: m["objectifs"][1].update(branche="payer"))
    assert "avant que la question" in _erreurs_apres(lambda m: m["dialogue"]["intro"][2].update(branche="payer"))
    assert "n'est pas une réponse" in _erreurs_apres(lambda m: m["branches"].update(fuir={}))
    assert "clés inconnues" in _erreurs_apres(lambda m: m["branches"]["payer"].update(arme="batte"))
    assert "jamais négative" in _erreurs_apres(lambda m: m["branches"]["payer"].update(recompense=-5))


def test_une_reponse_qui_ne_change_rien_n_en_est_pas_une():
    def rien_pour_payer(m):
        for o in m["objectifs"]:
            if o.get("branche") == "payer":
                del o["branche"]
        for lignes in m["dialogue"].values():
            for ligne in lignes:
                if ligne.get("branche") == "payer":
                    del ligne["branche"]
        del m["branches"]
    assert "'payer' ne change rien" in _erreurs_apres(rien_pour_payer)


def test_des_branches_sans_question_et_un_exige_qui_ne_se_tient_pas():
    assert "sans question" in _erreurs_apres(lambda m: _question(m).pop("choix"))
    assert "ce choix n'existe pas" in _erreurs_apres(lambda m: m.setdefault("exige", {}).update(choix={"d09": "fuir"}))
    assert "ce choix n'existe pas" in _erreurs_apres(lambda m: m.setdefault("exige", {}).update(choix={"q10": "x"}))
