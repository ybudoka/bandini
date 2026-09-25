"""Les gestes du décor, de la rue et de ceux qui y travaillent : le catalogue et ses bornes.

Le navigateur ne garde aucun de ces nombres (`static/js/interactions.js` lit le
paquet) : c'est donc ici qu'on les juge. ⚠️ Ces gestes sont de la VILLE, pas un
métier — aucun ne doit rapporter de quoi remplacer une mission, un repas ou un
séjour à l'hôpital.
"""

import json

import pytest

from app import carte, definitions, interactions, missions, recherche


def _mots_affiches():
    """Tous les mots que la ville écrit ou dit : invites, refus, messages, répliques."""
    a, f, b, bb, pc, ca, bo, p, ph = (interactions.ASSEOIR, interactions.FOUILLER, interactions.BOIRE,
                                      interactions.BARBECUE, interactions.PARCOMETRE, interactions.CARESSER,
                                      interactions.BORNE, interactions.POURBOIRE, interactions.PHOTO)
    mots = [a["invite"], *a["refus"].values(), f["invite"], f["deja"], *(t["texte"] for t in f["trouvailles"].values()),
            b["invite"], b["encore"], b["message"], bb["invite"], bb["deja"], bb["message"],
            pc["invite"], pc["deja"], pc["message"], ca["invite"], *ca["mots"],
            bo["invite_ouvrir"], bo["invite_fermer"], p["invite"], ph["invite"], *ph["merci"]]
    for liste in p["merci"].values():
        mots.extend(liste)
    return mots


def test_le_catalogue_voyage_dans_le_paquet_et_se_lit_en_json():
    exporte = interactions.exporter()
    assert set(exporte) == {"asseoir", "fouiller", "boire", "barbecue", "parcometre", "caresser", "borne",
                             "pourboire", "photo"}
    assert json.loads(json.dumps(exporte)) == exporte, "des listes et des dicts, jamais des tuples"
    assert definitions.assembler()["interactions"] == exporte, "le navigateur lit `B.defs.interactions`"


def test_un_decor_ne_donne_qu_un_seul_geste():
    """`decorSousLaMain` s'arrête au premier geste qui reconnaît le décor : deux gestes sur le même
    décor, et le second n'existerait jamais."""
    par_geste = {
        "asseoir": set(interactions.ASSEOIR["sieges"]),
        "fouiller": set(interactions.FOUILLER["decors"]),
        "boire": set(interactions.BOIRE["decors"]),
        "barbecue": set(interactions.BARBECUE["decors"]),
        "parcometre": set(interactions.PARCOMETRE["decors"]),
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
    # ⚠️ Une FIN DE PARTIE paie 0 $ (m99, M13) : on part avec un générique, pas une prime. La
    # plus petite prime est celle d'une mission qui en paie une.
    plus_petite_prime = min(m["recompense"] for m in missions.CATALOGUE
                            if "recompense" in m and not (m.get("donne") or {}).get("generique"))
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
    # Un repas au barbecue non plus : gratuit, donc sous le hot-dog achete (`economie.TARIFS`),
    # en vie comme en souffle.
    from app import economie
    bb = interactions.BARBECUE
    assert bb["pv"] < economie.TARIFS["hotdog_pv"] and bb["souffle"] < economie.TARIFS["hotdog_souffle"], \
        "le barbecue rapporte autant ou plus qu'un hot-dog achete"
    # Un parcomètre forcé non plus : plus qu'une poubelle, sous une distributrice défoncée.
    pc = interactions.PARCOMETRE
    assert pc["argent"][1] * 10 <= plus_petite_prime, \
        "le plus gros gain d'un parcomètre (%s $) doit rester sous le dixième de la plus petite prime" % pc["argent"][1]
    assert plus_gros_butin <= pc["argent"][0], "un parcomètre devrait rapporter au moins autant qu'une poubelle"
    assert pc["argent"][1] < economie.DISTRIBUTRICE["monnaie"][1], \
        "un parcomètre ne devrait pas valoir plus qu'une distributrice défoncée"


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


def test_forcer_un_parcometre_est_un_delit_que_recherche_connait():
    """⚠️ `interactions.py` déclare le geste, `recherche.py` déclare le délit — deux fichiers,
    une seule règle : un `decors` du catalogue de gestes qui manque à `DELITS` serait un vol
    que la police ne verrait jamais."""
    pc = interactions.PARCOMETRE
    assert "parcometre" in recherche.DELITS, "le geste existe, le délit non"
    delit = recherche.DELITS["parcometre"]
    assert delit["temoin"] is True, "quelques dollars de monnaie : ça se raconte, ça n'alarme pas"
    assert delit["etoiles"] == recherche.DELITS["distributrice"]["etoiles"], \
        "même gabarit qu'une distributrice défoncée"
    assert 1 <= pc["argent"][0] <= pc["argent"][1]


def test_caresser_le_chat_ne_rapporte_rien():
    """⚠️ Le seul des neuf gestes sans PV, sans souffle, sans argent : `pietons.BETES` et
    `Entites.majBete` décident déjà qui laisse approcher (le chat, pas le goéland) — ici,
    seulement l'invite et ce qu'on dit."""
    from app import pietons

    c = interactions.CARESSER
    assert c["espece"] == "chat"
    assert not (set(c) & {"pv", "souffle", "argent", "montant"}), "caresser ne devrait rien rapporter"
    assert len(c["mots"]) >= 2, "toujours le même mot serait une bête muette"
    assert "confiance_px" in pietons.BETES["chat"], "rien ne laisse approcher le chat sans cette clé"
    assert "confiance_px" not in pietons.BETES["goeland"], "le goéland doit rester farouche (fiche de la 2e vague)"
    assert pietons.BETES["chat"]["confiance_px"] < pietons.BETES["chat"]["fuite_px"], \
        "la confiance doit laisser approcher PLUS PRÈS que la fuite normale"
    # ⚠️ La fenêtre où l'on est confiant assez pour ne pas fuir ET assez près pour
    # `Interactions.caresserSousLaMain` (`c["portee_px"]`) doit être JOUABLE — quelques
    # pixels de marge, pas deux : un chat qui fuit pile à la portée du bouton ne se
    # caresse jamais (mesuré : `confiance_px` à 20 px pour un `portee_px` de 22 ne
    # laissait que 2 px).
    from app import armes

    marge = c["portee_px"] - pietons.BETES["chat"]["confiance_px"]
    assert marge >= 5, f"seulement {marge} px entre la fuite et la portée d'ACTION : injouable"
    # Et l'inverse tient toujours : même confiant, un poing ne l'atteint pas.
    poings = armes.par_slug("poings")
    assert pietons.BETES["chat"]["confiance_px"] > poings["portee"], \
        "confiant, le chat resterait quand même à portée d'un poing"


def test_les_mots_de_la_ville_sont_ecrits_pour_la_police_pixel():
    """La police du jeu ne sait que les majuscules : une invite en minuscules se dessinerait en
    majuscules quand même, mais un mot à peine écrit trahit un texte oublié."""
    mots = _mots_affiches()
    assert len(mots) > 20
    for texte in mots:
        assert texte == texte.upper() and texte.strip() == texte and texte, "un mot mal ecrit : %r" % texte


@pytest.mark.parametrize("nom", ["asseoir", "fouiller", "boire", "barbecue", "parcometre", "caresser", "borne"])
def test_une_portee_de_geste_est_celle_d_une_main(nom):
    portee = interactions.exporter()[nom]["portee_px"]
    assert 16 <= portee <= 32, "%s : %s px ne se prend pas d'une main" % (nom, portee)
