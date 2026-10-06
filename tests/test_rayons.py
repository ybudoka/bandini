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
            elif point in ("salon", "journal"):
                # Le fauteuil d'une pièce de SERVICE, le présentoir d'une pièce du SAVOIR, deviennent le comptoir d'un
                # rayon neuf (`Missions.rayonDuFauteuil`) — jamais celui d'une famille (le barbier garde son fauteuil).
                ok = slug in rayons.RAYONS
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


def test_les_articles_des_rayons_existent_et_se_vendent():
    for slug, rayon in rayons.RAYONS.items():
        assert rayon["articles"] and rayon["nom"], slug
        vus = [a["slug"] for a in rayon["articles"]]
        assert len(vus) == len(set(vus)), f"{slug} : un article en double"
        for a in rayon["articles"]:
            cibles = [a["tarif"], a["arme"], a["tenue"], a.get("piece"), a.get("service"), a.get("meuble")]
            assert sum(1 for c in cibles if c) == 1, f"{slug}/{a['slug']} : une seule sorte d'article"
            if a["tarif"]:
                assert (rayons.tarif(a["tarif"]) or 0) > 0, f"{slug}/{a['slug']} : pas de prix"
                # Le format compact (`rayons.exporter`) : le tarif d'un article est son slug, ses gains suivent.
                assert (a["tarif"], a["gain_pv"], a["gain_souffle"]) == (
                    a["slug"], f"{a['slug']}_pv", f"{a['slug']}_souffle"), f"{slug}/{a['slug']}"
            if a["arme"]:
                arme = armes.par_slug(a["arme"]) or {}
                assert arme.get("prix", 0) > 0, a
                # Ce qui fait du bruit ne se vend qu'au marché noir (`test_armes`) : Gus a une vitrine, un rayon aussi.
                assert not arme.get("bruit"), f"{slug}/{a['slug']} : une arme qui détone, hors du marché noir"
                assert a["nom"] == arme["nom"], f"{slug}/{a['slug']} : le nom du catalogue (`_arme`)"
            if a["tenue"]:
                tenue = next((t for t in magasins.TENUES if t["slug"] == a["tenue"]), {})
                # Un lot (la casquette de la foire) ou un cadeau (la tuque de Rocco) ne s'achète nulle part.
                assert tenue.get("prix") and not tenue.get("prime"), f"{slug}/{a['slug']} : une tenue qui ne se vend pas"
                assert a["nom"] == tenue["nom"], f"{slug}/{a['slug']} : le nom du catalogue (`_tenue`)"
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


def test_les_rayons_voyagent_seuls(paquets):
    """Sur `/api/rayons` (sortis de la suite le 6 oct. 2026, Martin : elle débordait), compacts — ni dans les
    définitions d'avant l'écran titre, ni dans la suite ; les définitions nomment leur empreinte."""
    import json
    rayons_ = json.loads(paquets.rayons.corps)
    suite = json.loads(paquets.suite.corps)
    defs = json.loads(paquets.definitions.corps)
    assert "rayons" in rayons_ and "rayons" not in suite and "rayons" not in defs
    assert defs["rayons_empreinte"] == paquets.rayons.etag
    r = rayons_["rayons"]
    assert "BOULANGERIE" in r["enseignes"]["boulangerie"]
    assert r["rayons"]["boulangerie"][0][0] == "pain" and r["noms"]["pain"] == "Pain de ménage"
    assert r["tarifs"]["pain"] == list(rayons.BOUCHEES["pain"])


def test_les_tenues_et_les_armes_se_vendent_chez_qui_le_dit():
    """Vague 2a : les bottes au magasin de bottes, le complet chez le tailleur, le bâton aux sports — ce que Rosa et
    Chez Gus vendaient seuls se trouve chez qui l'annonce."""
    def vend(nom):
        slug = rayons.ENSEIGNES[nom]
        return {a["tenue"] or a["arme"] or a["slug"] for a in (rayons.RAYONS.get(slug) or magasins.COMPTOIRS[slug])["articles"]}
    assert "bottes_hiver" in vend("BOTTES DE TRAVAIL") and "bottes_hiver" in vend("CORDONNERIE")
    assert "salopette" in vend("SALOPETTES")
    assert "complet" in vend("TAILLEUR ROMÉO")
    assert "batte" in vend("SPORTS BEAULIEU") and "couteau" in vend("PÊCHE ET CHASSE")
    assert "ceinture_flechee" in vend("SOUVENIRS")
    assert not vend("MODISTE") & {"sandwich", "chips"}
    genres = rayons.noms_des_enseignes()
    reste = sorted(n for n in rayons.EN_ATTENTE if "mode" in genres[n])
    assert reste == ["PARFUMERIE", "TATOUAGE"], reste


def test_le_format_compact_dit_la_sorte_de_chaque_article():
    """`rayons.exporter` : une tenue part en `t:<slug>`, une arme en `a:<slug>`, une bouchée en slug avec son nom
    UNE fois dans `noms` — et la marge et le rabais suivent le rayon quand ils ne valent pas 1 (`Missions.rayons`
    les relit)."""
    e = rayons.exporter()
    r, noms = e["rayons"], e["noms"]
    assert r["sports"][0][0] == "a:batte" and "t:tuque_bbr" in r["sports"][0]
    assert r["sports"][1:] == [1.2, 1.0]
    assert r["liquidation"][1:] == [1.0, 0.5]
    assert r["boulangerie"] == [["pain", "croissant", "beigne", "cafe"]]
    assert noms["pain"] == "Pain de ménage" and noms["cafe"] == ["Café", "cafe"]
    assert {n[1] for n in noms.values() if isinstance(n, list)} <= set(magasins.EFFETS)
    assert not any(":" in a for a in noms), "un slug de bouchée qui se lirait comme une tenue ou une arme"
    # Ce qui retombe de soi-même au comptoir de sa famille ne voyage pas : la TAVERNE, le barbier.
    envoyees = {n for ns in e["enseignes"].values() for n in ns}
    assert "TAVERNE" not in envoyees and "BARBIER" not in envoyees
    assert "DÉPANNEUR" in envoyees and "BOULANGERIE" in envoyees


def test_une_bouchee_a_le_meme_nom_dans_tous_les_rayons():
    """Son nom voyage une fois (`exporter`, `noms`) : deux rayons qui la nommeraient autrement mentiraient l'un des deux."""
    vus: dict[str, set] = {}
    for rayon in rayons.RAYONS.values():
        for a in rayon["articles"]:
            if a["tarif"]:
                vus.setdefault(a["slug"], set()).add((a["nom"], a["effet"]))
    assert not {s: v for s, v in vus.items() if len(v) > 1}


def test_les_commerces_de_l_auto_travaillent_sur_le_char():
    """Vague 2b : les PNEUS posent des pneus d'hiver, la PEINTURE AUTO repeint, la CARROSSERIE répare — les pièces et
    les gestes de Ti-Guy (`garage.PIECES`, `Missions.menuGarage`), sur le char garé devant la porte."""
    from app import garage
    def fait(nom):
        r = rayons.RAYONS[rayons.ENSEIGNES[nom]]
        return {a.get("piece") or a.get("service") for a in r["articles"]} - {None}
    assert fait("PNEUS DESCHAMPS") == {"pneus"} and fait("PNEUS BEAULIEU") == {"pneus"}
    assert fait("PEINTURE AUTO") == {"repeindre"} and fait("DÉBOSSELAGE") == {"reparer"}
    assert "blindage" in fait("SOUDURE PELLETIER") and "moteur" in fait("TRANSMISSION")
    pieces = {q["slug"] for q in garage.PIECES}
    for slug, r in rayons.RAYONS.items():
        for a in r["articles"]:
            assert not a.get("piece") or a["piece"] in pieces, f"{slug}/{a['slug']}"
            assert not a.get("service") or a["service"] in rayons.SERVICES, f"{slug}/{a['slug']}"
    genres = rayons.noms_des_enseignes()
    assert not [n for n in ("PNEUS DESCHAMPS", "PEINTURE AUTO") if n in rayons.EN_ATTENTE]
    assert all("industrie" in genres[n] for n in ("PNEUS DESCHAMPS", "SOUDURE", "PIÈCES USAGÉES"))


def test_les_meubles_de_la_planque_se_vendent_en_ville():
    """Vague 2c : le téléviseur à la RADIO-TV, le sofa chez MEUBLES GAGNON, l'aquarium à l'ANIMALERIE — les meubles du
    catalogue Beausoleil (`decoration.MEUBLES`), chacun avec sa place à la planque de Rocco (sinon la livraison n'a
    nulle part où le poser)."""
    from app import decoration
    def meubles(nom):
        r = rayons.RAYONS[rayons.ENSEIGNES[nom]]
        return {a.get("meuble") for a in r["articles"]} - {None}
    assert meubles("RADIO-TV DUMAS") == {"televiseur", "jukebox"} == meubles("RADIO-TV KWOK")
    assert "sofa" in meubles("MEUBLES GAGNON") and "sofa" in meubles("TAPISSIER")
    assert meubles("ANIMALERIE") == {"aquarium"}
    for slug, r in rayons.RAYONS.items():
        for a in r["articles"]:
            if a.get("meuble"):
                m = next(m for m in decoration.MEUBLES if m["slug"] == a["meuble"])
                assert a["meuble"] in decoration.PLACES[m.get("piece", "planque")], f"{slug}/{a['slug']}"


def test_le_neuf_se_porte_au_cou_et_sur_les_yeux_et_rosa_ne_le_vend_pas():
    """Vague 2d : la chaîne en or à la BIJOUTERIE, les lunettes fumées chez l'OPTICIEN, le foulard de soie à la
    SOIERIE — des tenues à deux places neuves (`cou`, `yeux` : `magasins.PLACES`), vendues EN VILLE seulement."""
    from app import garderobe
    def vend(nom):
        return {a["tenue"] for a in rayons.RAYONS[rayons.ENSEIGNES[nom]]["articles"]} - {None}
    assert "chaine_or" in vend("BIJOUTERIE") and "chaine_or" in vend("BIJOUX CHEUNG")
    assert vend("OPTICIEN") == {"lunettes_fumees"} == vend("OPTIQUE")
    assert "foulard_soie" in vend("SOIERIE MEI")
    en_ville = [t for t in magasins.TENUES if t.get("en_ville")]
    assert {t["emplacement"] for t in en_ville} == {"cou", "yeux"} <= set(magasins.PLACES)
    vendues = {a["tenue"] for r in rayons.RAYONS.values() for a in r["articles"]}
    for t in en_ville:
        assert t["slug"] in vendues, f"{t['slug']} : vendue en ville, mais par personne"
        assert set(t["piece"]["accessoires"]) <= set(garderobe.ACCESSOIRES), t["slug"]


def test_chaque_service_rend_le_sien():
    """Vague 3a (Martin, 6 oct. 2026) : un commerce qui ne vend rien rend un service à lui — l'hôtel loue un lit, la
    clinique soigne, la banque ouvre le coffre, les prêteurs prennent la dette, le prêt sur gages rachète les armes."""
    def services(nom):
        return {a.get("service") for a in rayons.RAYONS[rayons.ENSEIGNES[nom]]["articles"]} - {None}
    assert services("HÔTEL DES QUAIS") == {"nuit", "sieste"} == services("MOTEL LA POINTE")
    assert all(services(n) == {"soins"} for n in ("CLINIQUE", "DOCTEUR", "DENTISTE", "SPA", "ACUPUNCTURE LEE"))
    assert services("BANQUE") == {"coffre"} == services("CAISSE POP")
    assert services("PRÊTS RAPIDES") == {"dette"} and services("PRÊT SUR GAGES") == {"gages"}
    assert services("BUANDERIE") == {"linge"} and services("FERRAILLE") == {"epave"}
    assert services("CLUB MAH-JONG") == {"sic_bo"} and services("CLUB VIDÉO") == {"film"}
    vendus = {a.get("service") for r in rayons.RAYONS.values() for a in r["articles"]}
    assert set(rayons.SERVICES) <= vendus, f"des services que personne ne rend : {set(rayons.SERVICES) - vendus}"
    # Plus de coupe de cheveux à la banque : les pièces de service qui gardent le fauteuil sont des barbiers, ou attendent.
    genres = rayons.noms_des_enseignes()
    for nom, slug in rayons.ENSEIGNES.items():
        if "service" in genres[nom] and slug == "salon":
            assert "BARBIER" in nom or "COIFFURE" in nom or "SALON" in nom, nom


def test_chaque_destination_du_taxi_a_sa_porte_dans_la_ville():
    """Vague 3b : TAXI DIAMANT dépose devant la porte d'un lieu (`rayons.TAXI`) — une destination sans porte serait une
    ligne qui ne se montre jamais."""
    v = villes.exporter()
    lieux = {p.get("lieu") for p in v["portes"]}
    assert not [s for s, _ in rayons.TAXI if s not in lieux], [s for s, _ in rayons.TAXI if s not in lieux]
    assert rayons.ENSEIGNES["TAXI DIAMANT"] == "taxi"


def test_chaque_lieu_de_l_album_a_sa_porte_et_le_photographe_le_developpe():
    """Vague 3c (Martin, 6 oct. 2026 : « photos de voyage ») : le mode photo reconnaît la PORTE d'un lieu de l'album
    (`photos.ALBUM`) — un lieu sans porte ne se prendrait jamais ; et les quatre photographes développent et rachètent."""
    from app import photos
    v = villes.exporter()
    lieux = {p.get("lieu") for p in v["portes"]}
    assert len(photos.ALBUM) == 10 and not [s for s, _ in photos.ALBUM if s not in lieux]
    for nom in ("PHOTO EXPRESS", "PHOTO SOUVENIR", "PHOTOGRAPHE", "STUDIO LAU"):
        assert {a.get("service") for a in rayons.RAYONS[rayons.ENSEIGNES[nom]]["articles"]} >= {"developper", "rachat"}


def test_ceux_qui_ne_vendent_rien_disent_leur_replique():
    """Vague 3d (Martin, 6 oct. 2026 : « soupe et répliques ») : chaque enseigne d'un rayon à réplique a la sienne,
    courte (elle s'écrit sous le menu) ; la MISSION DU PORT et l'HOSPICE servent la soupe ; et plus aucun service
    n'attend."""
    a_replique = {nom for nom, slug in rayons.ENSEIGNES.items()
                  if any(a.get("service") == "replique" for a in (rayons.RAYONS.get(slug) or {}).get("articles", []))}
    assert a_replique == set(rayons.REPLIQUES), a_replique ^ set(rayons.REPLIQUES)
    assert all(0 < len(t) <= 50 for t in rayons.REPLIQUES.values()), [t for t in rayons.REPLIQUES.values() if len(t) > 50]
    assert rayons.ENSEIGNES["MISSION DU PORT"] == rayons.ENSEIGNES["HOSPICE"] == "soupe_populaire"
    genres = rayons.noms_des_enseignes()
    services = sorted(n for n in rayons.EN_ATTENTE if genres[n] & {"service"})
    assert not services, f"des services en attente : {services}"


def test_ce_qui_se_branche_sur_l_existant():
    """Vague 4a : les grossistes rachètent la contrebande, la location pose un vélo, le chantier naval répare le bateau,
    et les fournisseurs (qui ne vendent pas au détail) disent leur réplique."""
    def services(nom):
        return {a.get("service") for a in rayons.RAYONS[rayons.ENSEIGNES[nom]]["articles"]} - {None}
    assert all(services(n) == {"revente"} for n in ("GROSSISTE", "ENTREPÔT 7", "IMPORT YIP"))
    assert services("LOCATION VÉLOS") == {"velo"} and services("CHANTIER NAVAL") == {"radouber"}
    assert services("ACIER DU NORD") == {"replique"} and "ACIER DU NORD" in rayons.REPLIQUES
    assert services("À LOUER") == {"replique"}
    genres = rayons.noms_des_enseignes()
    assert not [n for n in rayons.EN_ATTENTE if genres[n] & {"industrie", "marine"}], "l'industrie et la marine attendent"
