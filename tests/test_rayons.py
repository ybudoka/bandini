"""Des comptoirs qui vendent ce que dit l'enseigne (docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-l-enseigne.md) :
le rayon de chaque enseigne, écrit à la main (`app/rayons.py`) — la ville, les tables et les prix."""

import villes

from app import armes, carte, devantures, economie, magasins, rayons

#: La borne du trottoir (`test_reclame`) : au dollar, rien ne bat le hot-dog — écrite ici, pas relue.
PAR_DOLLAR_MAX = 6.5


def test_chaque_enseigne_a_son_rayon_ou_attend_le_sien():
    """Une enseigne neuve sans rayon tomberait au comptoir de sa couleur sans que personne le décide."""
    noms = set(rayons.noms_des_enseignes())
    decidees, attente = set(rayons.ENSEIGNES), set(rayons.EN_ATTENTE)
    assert not (noms - decidees - attente), sorted(noms - decidees - attente)
    assert not (decidees & attente), sorted(decidees & attente)
    assert not ((decidees | attente) - noms), f"des noms que la ville ne peint pas : {sorted((decidees | attente) - noms)}"
    assert all(v.strip() for v in rayons.EN_ATTENTE.values()), "une enseigne en attente dit ce qu'elle vendra"


def test_un_rayon_decide_est_un_rayon_un_comptoir_de_famille_ou_le_point_de_son_genre():
    """Le rayon d'une enseigne vend à SON point : un rayon de comptoir chez qui a un comptoir d'emplettes, le
    fauteuil chez le barbier (`salon`), le présentoir au Clairon (`journal`) — `carte.MOBILIER`."""
    genres, faux = rayons.noms_des_enseignes(), []
    for nom, slug in rayons.ENSEIGNES.items():
        for genre in genres[nom]:
            point = carte.MOBILIER[genre]["point"][0]
            if slug in rayons.POINTS:
                ok = point == slug
            else:
                comptoir = rayons.RAYONS.get(slug) or magasins.COMPTOIRS.get(slug)
                ok = (point == "emplettes" and comptoir is not None and not comptoir.get("bloc")
                      and not comptoir.get("enseigne"))
            if not ok:
                faux.append((nom, genre, slug, point))
    assert not faux, faux


def test_la_bouffe_vend_ce_que_dit_son_nom():
    """Vague 1 : plus une enseigne de bouffe au comptoir de sa couleur — et la BOULANGERIE vend du pain."""
    genres = rayons.noms_des_enseignes()
    reste = sorted(n for n in rayons.EN_ATTENTE if "bouffe" in genres[n])
    assert not reste, reste
    def vend(nom):
        slug = rayons.ENSEIGNES[nom]
        return {a["slug"] for a in (rayons.RAYONS.get(slug) or magasins.COMPTOIRS[slug])["articles"]}
    assert "pain" in vend("BOULANGERIE")
    assert {"pizza", "pizza_garnie"} <= vend("PIZZERIA NAPOLI")
    assert "canard_laque" in vend("CANARD LAQUÉ") and "pate_chinois" not in vend("JARDIN DE JADE")
    assert "beigne" in vend("BEIGNES CHEZ TI")
    assert "tourtiere" in vend("BOUCHERIE PARÉ")


def test_les_articles_des_rayons_existent_et_se_mangent():
    for slug, rayon in rayons.RAYONS.items():
        assert rayon["articles"] and rayon["nom"], slug
        vus = [a["slug"] for a in rayon["articles"]]
        assert len(vus) == len(set(vus)), f"{slug} : un article en double"
        for a in rayon["articles"]:
            cibles = [a["tarif"], a["arme"], a["tenue"]]
            assert sum(1 for c in cibles if c) == 1, f"{slug}/{a['slug']} : une seule sorte d'article"
            if a["tarif"]:
                assert (rayons.tarif(a["tarif"]) or 0) > 0, f"{slug}/{a['slug']} : pas de prix"
                # Le format compact (`rayons.exporter`) : le tarif d'un article est son slug, ses gains suivent.
                assert (a["tarif"], a["gain_pv"], a["gain_souffle"]) == (
                    a["slug"], f"{a['slug']}_pv", f"{a['slug']}_souffle"), f"{slug}/{a['slug']}"
            if a["arme"]:
                assert (armes.par_slug(a["arme"]) or {}).get("prix", 0) > 0, a
            for cle in ("gain_pv", "gain_souffle"):
                if a[cle]:
                    assert 0 < (rayons.tarif(a[cle]) or 0) <= 100, f"{slug}/{a['slug']} : {a[cle]}"


def test_rien_dans_un_rayon_ne_bat_le_hot_dog_au_dollar():
    for slug, rayon in rayons.RAYONS.items():
        for a in rayon["articles"]:
            if not a["tarif"] or not (a["gain_pv"] or a["gain_souffle"]) or a["effet"]:
                continue
            rend = (rayons.tarif(a["gain_pv"] or "") or 0) + (rayons.tarif(a["gain_souffle"] or "") or 0)
            assert rend / rayons.tarif(a["tarif"]) <= PAR_DOLLAR_MAX + 1e-9, f"{slug}/{a['slug']}"


def test_une_bouchee_de_rayon_n_a_qu_un_prix():
    """Les prix ne vivent jamais en double : une bouchée de rayon (`rayons.BOUCHEES`) n'est pas déjà dans
    `economie.TARIFS` — le navigateur les verse dans les mêmes tarifs (`Missions.rayons`)."""
    assert not set(rayons.TARIFS) & set(economie.TARIFS), sorted(set(rayons.TARIFS) & set(economie.TARIFS))
    vendues = {a["tarif"] for r in rayons.RAYONS.values() for a in r["articles"]}
    assert set(rayons.BOUCHEES) <= vendues, f"des bouchées que rien ne vend : {sorted(set(rayons.BOUCHEES) - vendues)}"


def test_chaque_porte_de_commerce_de_la_ville_porte_un_nom_que_les_rayons_connaissent():
    """Le navigateur cherche le rayon au NOM de la porte (`Missions.comptoirDuPoint`) : un nom renommé ou
    coupé en route (les vitrines, la réserve) tomberait au comptoir de sa couleur sans un mot."""
    v = villes.exporter()
    connus = set(rayons.ENSEIGNES) | set(rayons.EN_ATTENTE)
    vus, inconnus = 0, []
    for p in v["portes"]:
        piece = v["interieurs"].get(p.get("interieur") or "")
        if not piece or not p.get("nom"):
            continue
        if not any(q["type"] in ("emplettes", "salon", "journal") and (q.get("genre") or q["type"]) in
                   devantures.INDEX_GENRE | {"salon": 0, "journal": 0} for q in piece["points"]):
            continue
        vus += 1
        if p["nom"] not in connus:
            inconnus.append((p["nom"], p["interieur"]))
    assert vus >= 20, f"{vus} portes de commerce jugées seulement"
    assert not inconnus, inconnus


def test_la_suite_porte_les_rayons(paquets):
    """Dans la suite du paquet (`DANS_LA_SUITE`), compacts — pas dans les définitions d'avant l'écran titre."""
    import json
    suite = json.loads(paquets.suite.corps)
    defs = json.loads(paquets.definitions.corps)
    assert "rayons" in suite and "rayons" not in defs
    r = suite["rayons"]
    assert "BOULANGERIE" in r["enseignes"]["boulangerie"]
    assert r["rayons"]["boulangerie"][1][0] == ["pain", "Pain de ménage"]
    assert r["tarifs"]["pain"] == list(rayons.BOUCHEES["pain"])
