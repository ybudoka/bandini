"""Un passant qui donne une job (1er oct. 2026) — la FORME d'une petite job (`missions.erreurs_de_passant`), sur le
catalogue et sur des fiches cassées exprès."""

import copy

from app import missions

JOBS = [m for m in missions.CATALOGUE if m.get("passant")]


def _t02():
    return copy.deepcopy(missions.par_slug("t02"))


def _erreurs_apres(changer, slug="t02"):
    m = copy.deepcopy(missions.par_slug(slug))
    changer(m)
    return " | ".join(missions.erreurs_de_passant(m))


def test_les_petites_jobs_tiennent_leur_forme():
    assert {m["slug"] for m in JOBS} >= {"t02", "t03", "t05", "t13"}
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_passant(m) == [], m["slug"]
    for m in JOBS:
        assert m["donneur"] in missions.DONNEURS_PASSANTS and not m["dialogue"].get("appel"), m["slug"]
        # Les voix de la rue : un passant parle avec la voix des passants (`audio.VOIX_PAR_GENRE`).
        from app import audio
        perso = missions.personnage(m["donneur"])
        assert perso["voix"] == audio.VOIX_PAR_GENRE[perso["genre"]], m["slug"]
        assert not missions.on_le_rencontre(m["donneur"]), "un passant ne se présente pas"


def test_le_hele_se_dit_en_premier_et_se_compte_en_dernier():
    m = missions.par_slug("t02")
    assert missions.dans_l_ordre_ou_on_les_entend(m)[0] is m["dialogue"]["hele"][0]
    slugs = [r for r in missions.repliques() if r["mission"] == "t02"]
    assert slugs[-1]["partie"] == "hele" and slugs[-1]["telephone"] is False, slugs[-1]


def test_une_job_mal_formee_se_refuse():
    assert "passant ordinaire" in _erreurs_apres(lambda m: m["passant"].update(archetype="cravate"))
    assert "passant ordinaire" in _erreurs_apres(lambda m: m["passant"].update(archetype="commis"))
    assert "district inconnu" in _erreurs_apres(lambda m: m["passant"].update(district="lune"))
    assert "clés inconnues" in _erreurs_apres(lambda m: m["passant"].update(heure="nuit"))
    assert "nom de sa boîte" in _erreurs_apres(lambda m: m["passant"].update(nom="X" * 30))
    assert "n'appelle pas" in _erreurs_apres(lambda m: m["dialogue"].update(appel=m["dialogue"]["intro"][:1]))
    assert "hèlement" in _erreurs_apres(lambda m: m["dialogue"]["hele"][0].update(texte="Hé! Toi, là-bas, viens ici!"))
    assert "hèlement" in _erreurs_apres(lambda m: m["dialogue"].pop("hele"))
    assert "seul le passant parle" in _erreurs_apres(lambda m: m["dialogue"]["fin"][0].update(qui="lulu"))
    assert "devant lui" in _erreurs_apres(lambda m: m["objectifs"].pop())
    assert "par un passant" in _erreurs_apres(lambda m: m.update(donneur="marco"))


def test_un_passant_sans_job_ne_donne_rien_et_personne_d_autre_ne_hele():
    m = copy.deepcopy(missions.par_slug("m3"))
    m["donneur"] = "passant"
    assert "clé `passant`" in " | ".join(missions.erreurs_de_passant(m))
    m = copy.deepcopy(missions.par_slug("m3"))
    m["dialogue"]["hele"] = [{"qui": "marco", "texte": "Hé! Cousin!"}]
    assert "seul un passant" in " | ".join(missions.erreurs_de_passant(m))


def test_une_job_finit_devant_lui_et_ne_voyage_pas_au_telephone():
    for m in JOBS:
        assert missions.fin_chez_le_donneur(m) and missions.fin_dite_en_personne(m), m["slug"]
    # ⚠️ Les jobs voyagent PLIÉES (`jobs_pour_le_navigateur`, l'ordre de `CHAMPS_D_UNE_JOB`), pas avec le catalogue, et
    # n'y gardent que ce qui les CHOISIT (`jobs.js`) ; le nom de sa boîte arrive avec elle (`pour_jouer`).
    assert not any(m.get("passant") for m in missions.pour_le_navigateur())
    pliees = {j[0]: dict(zip(missions.CHAMPS_D_UNE_JOB, j)) for j in missions.jobs_pour_le_navigateur()}
    assert set(pliees) == {m["slug"] for m in JOBS}
    assert pliees["t02"] == {"slug": "t02", "titre": "Le lunch des gars", "donneur": "passant", "recompense": 30,
                             "passant": "docker@quais", "prerequis": ["m6"]}, pliees["t02"]
    assert missions.pour_jouer("t02")["passant"]["nom"] == "Le débardeur"
