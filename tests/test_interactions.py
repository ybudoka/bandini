"""Les gestes du décor, de la rue et de ceux qui y travaillent : le catalogue et ses bornes.

Le navigateur ne garde aucun de ces nombres (`static/js/interactions.js` lit le
paquet) : c'est donc ici qu'on les juge. ⚠️ Ces gestes sont de la VILLE, pas un
métier — aucun ne doit rapporter de quoi remplacer une mission, un repas ou un
séjour à l'hôpital.
"""

import json

import pytest

from app import carte, definitions, interactions, missions


def _mots_affiches():
    """Tous les mots que la ville écrit ou dit : invites, refus, messages, répliques."""
    a, f, b, bo, p, ph = (interactions.ASSEOIR, interactions.FOUILLER, interactions.BOIRE,
                          interactions.BORNE, interactions.POURBOIRE, interactions.PHOTO)
    mots = [a["invite"], *a["refus"].values(), f["invite"], f["deja"], *(t["texte"] for t in f["trouvailles"].values()),
            b["invite"], b["encore"], b["message"], bo["invite_ouvrir"], bo["invite_fermer"], p["invite"], ph["invite"], *ph["merci"]]
    for liste in p["merci"].values():
        mots.extend(liste)
    return mots


def test_le_catalogue_voyage_dans_le_paquet_et_se_lit_en_json():
    exporte = interactions.exporter()
    assert set(exporte) == {"asseoir", "fouiller", "boire", "borne", "pourboire", "photo"}
    assert json.loads(json.dumps(exporte)) == exporte, "des listes et des dicts, jamais des tuples"
    assert definitions.assembler()["interactions"] == exporte, "le navigateur lit `B.defs.interactions`"


def test_un_decor_ne_donne_qu_un_seul_geste():
    """`decorSousLaMain` s'arrête au premier geste qui reconnaît le décor : deux gestes sur le même
    décor, et le second n'existerait jamais."""
    par_geste = {
        "asseoir": set(interactions.ASSEOIR["sieges"]),
        "fouiller": set(interactions.FOUILLER["decors"]),
        "boire": set(interactions.BOIRE["decors"]),
        "borne": set(interactions.BORNE["decors"]),
    }
    noms = [nom for decors in par_geste.values() for nom in decors]
    assert len(noms) == len(set(noms)), "un decor est nomme par deux gestes : %s" % par_geste


def test_les_bancs_sont_les_quatre_de_la_ville_et_regardent_du_bon_cote():
    sieges = interactions.ASSEOIR["sieges"]
    assert set(sieges) == {"banc", "banc_nord", "banc_est", "banc_ouest"}
    # Le banc vu de face regarde le sud, celui vu de dos le nord, les deux de profil l'est et l'ouest.
    assert {d: s["pose"] for d, s in sieges.items()} == {
        "banc": "assis_bas", "banc_nord": "assis_haut", "banc_est": "assis_droite", "banc_ouest": "assis_gauche"}


def test_rien_ici_ne_remplace_une_mission_un_repas_ou_l_hopital():
    plus_petite_prime = min(m["recompense"] for m in missions.CATALOGUE if "recompense" in m)
    f = interactions.FOUILLER
    plus_gros_butin = max(t["argent"][1] for t in f["trouvailles"].values() if "argent" in t)
    assert plus_gros_butin * 10 <= plus_petite_prime, \
        "le plus gros butin d'un bac (%s $) doit rester sous le dixieme de la plus petite prime (%s $)" % (plus_gros_butin, plus_petite_prime)
    # L'esperance d'une fouille, table par table : de la monnaie, pas un salaire.
    for nom, table in f["tables"].items():
        total = sum(p for p, _ in table)
        esperance = sum(p / total * sum(f["trouvailles"][s]["argent"]) / 2 for p, s in table if "argent" in f["trouvailles"][s])
        assert esperance <= 2.0, "%s : une fouille rapporte %.2f $ en moyenne, c'est trop" % (nom, esperance)
    # Un banc repose, il ne soigne pas : une PV toutes les deux secondes au plus, et pas la barre entiere.
    a = interactions.ASSEOIR
    assert 60 / a["pv_images"] <= 0.5 and a["pv_plafond"] <= 0.6
    # Un reste de poutine ne vaut pas un hot-dog achete (`economie`) : quelques PV, pas dix.
    assert f["trouvailles"]["reste"]["pv"] <= 5


def test_les_tables_de_fouille_se_tiennent():
    f = interactions.FOUILLER
    assert set(f["decors"].values()) <= set(f["tables"]), "un decor renvoie a une table qui n'existe pas"
    for nom, table in f["tables"].items():
        assert all(isinstance(p, int) and p > 0 for p, _ in table), "%s : des poids entiers et positifs" % nom
        assert {s for _, s in table} <= set(f["trouvailles"]), "%s : une trouvaille inconnue" % nom
        assert len({s for _, s in table}) == len(table), "%s : une trouvaille deux fois" % nom
    tirees = {s for table in f["tables"].values() for _, s in table}
    # La nuit, le rat de la table est un raton (`la_nuit`) : c'est elle qui le tire.
    tirees.add(f["la_nuit"]["par"])
    assert f["la_nuit"]["remplace"] in {s for table in f["tables"].values() for _, s in table}
    assert set(f["trouvailles"]) == tirees, "une trouvaille que rien ne tire"
    # La morsure ne tue jamais (le navigateur garde toujours un point) et reste petite.
    assert -5 <= f["trouvailles"]["rat"]["pv"] < 0
    assert -5 <= f["trouvailles"]["raton"]["pv"] < 0
    for slug, t in f["trouvailles"].items():
        if "argent" in t:
            assert 1 <= t["argent"][0] <= t["argent"][1], slug


def test_le_quartier_dit_la_poubelle_du_plus_riche_au_plus_pauvre():
    s = interactions.FOUILLER["standing"]
    assert set(s) <= set(carte.STANDINGS.values()), "un standing que la ville ne connait pas"
    assert s["cossu"] > s["ordinaire"] >= s["pauvre"] > 0, "plus le quartier est riche, plus son bac est vide"


def test_le_pourboire_et_la_photo_restent_des_gestes_de_rue():
    p, ph = interactions.POURBOIRE, interactions.PHOTO
    assert p["montant"] >= 1
    assert set(p["merci"]) == set(p["metiers"]), "chaque metier d'artiste a son mot"
    assert all(m in ("musicien", "amuseur", "jongleur", "echassier") for m in p["metiers"])
    assert ph["metier"] == "touriste"
    assert 1 <= ph["pourboire"][0] <= ph["pourboire"][1] <= 5
    assert ph["pose_images"] >= 30, "le temps d'un flash"


def test_les_mots_de_la_ville_sont_ecrits_pour_la_police_pixel():
    """La police du jeu ne sait que les majuscules : une invite en minuscules se dessinerait en
    majuscules quand même, mais un mot à peine écrit trahit un texte oublié."""
    mots = _mots_affiches()
    assert len(mots) > 20
    for texte in mots:
        assert texte == texte.upper() and texte.strip() == texte and texte, "un mot mal ecrit : %r" % texte


@pytest.mark.parametrize("nom", ["asseoir", "fouiller", "boire", "borne"])
def test_une_portee_de_geste_est_celle_d_une_main(nom):
    portee = interactions.exporter()[nom]["portee_px"]
    assert 16 <= portee <= 32, "%s : %s px ne se prend pas d'une main" % (nom, portee)
