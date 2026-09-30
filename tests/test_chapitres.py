"""Des missions en chapitres (docs/jalons/des-missions-en-chapitres.md) — la forme, en Python."""

from app import missions


def _chapitre(**plus):
    base = {"slug": "zz", "titre": "Zz", "donneur": "bilodeau", "recompense": 100,
            "remplace": ["za", "zb"],
            "objectifs": [
                {"type": "acte", "texte": "ACTE 1 — LE PONT", "donneur": "bilodeau"},
                {"type": "aller", "texte": "VA AU PONT", "lieu": "phare", "rayon": 5},
                {"type": "acte", "texte": "ACTE 2 — LES COLLETS", "donneur": "trappeur"},
                {"type": "retourner", "texte": "RETOURNE VOIR LE TRAPPEUR"},
            ],
            "dialogue": {"intro": [], "fin": []}}
    base.update(plus)
    return base


def test_acte_est_un_type_d_objectif_et_donne_une_option():
    assert "acte" in missions.TYPES_OBJECTIFS
    assert "donne" in missions.OPTIONS_OBJECTIFS


def test_un_chapitre_bien_forme_n_a_aucune_erreur():
    assert missions.erreurs_de_chapitre(_chapitre(), catalogue=[]) == []


def test_une_mission_ordinaire_n_a_aucune_erreur_de_chapitre():
    assert missions.erreurs_de_chapitre({"slug": "zo", "objectifs": [{"type": "aller"}]}, catalogue=[]) == []


def test_un_chapitre_commence_par_un_acte():
    m = _chapitre()
    m["objectifs"] = m["objectifs"][1:]
    assert any("commence" in e for e in missions.erreurs_de_chapitre(m, catalogue=[]))


def test_un_chapitre_ne_finit_pas_sur_un_acte():
    m = _chapitre()
    m["objectifs"].append({"type": "acte", "texte": "ACTE 3 — RIEN", "donneur": "zed"})
    m["remplace"].append("zc")
    assert any("finit" in e for e in missions.erreurs_de_chapitre(m, catalogue=[]))


def test_autant_de_missions_remplacees_que_d_actes():
    assert any("remplace" in e for e in missions.erreurs_de_chapitre(_chapitre(remplace=["za"]), catalogue=[]))


def test_le_donneur_d_un_acte_existe():
    m = _chapitre()
    m["objectifs"][2]["donneur"] = "personne_de_connu"
    assert any("donneur" in e for e in missions.erreurs_de_chapitre(m, catalogue=[]))


def test_une_mission_remplacee_ne_reste_pas_au_catalogue_ni_en_prerequis():
    autre = {"slug": "za", "prerequis": []}
    assert any("za" in e for e in missions.erreurs_de_chapitre(_chapitre(), catalogue=[autre]))
    suite = {"slug": "zq", "prerequis": ["zb"]}
    assert any("zb" in e for e in missions.erreurs_de_chapitre(_chapitre(), catalogue=[suite]))


def test_le_catalogue_n_a_aucune_erreur_de_chapitre():
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_chapitre(m) == [], m["slug"]


def test_la_fin_d_un_chapitre_se_joue_chez_le_donneur_du_dernier_acte():
    assert missions.donneur_final(_chapitre()) == "trappeur"
    assert missions.donneur_final({"donneur": "zed", "objectifs": []}) == "zed"
