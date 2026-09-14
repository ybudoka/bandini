from app import vehicules


def test_slugs_uniques_et_classes_connues():
    slugs = [v["slug"] for v in vehicules.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    for v in vehicules.CATALOGUE:
        assert v["classe"] in vehicules.CLASSES
        assert 0 <= v["frequence"] <= 1
        assert v["prix"] > 0 and v["vie"] > 0 and v["places"] >= 1
        assert 0 < v["vitesse_max"] <= 8
        assert 0 < v["braquage"] < 0.2
        assert v["couleurs"] and all(c.startswith("#") for c in v["couleurs"])
        assert v["phase"] in (1, 2)


def test_une_auto_de_police_le_parc_complet_et_le_velo():
    assert any(v["police"] for v in vehicules.CATALOGUE)
    # M9 : le parc au complet roule. Le bateau reste en phase 2 — il demande
    # une physique a part et des quais ou embarquer (voir la fiche).
    assert {v["slug"] for v in vehicules.de_phase(1)} == {
        "auto", "taxi", "moto", "velo", "police",
        "camion", "autobus", "ambulance", "remorqueuse"}
    assert {v["slug"] for v in vehicules.CATALOGUE} - {v["slug"] for v in vehicules.de_phase(1)} == {"bateau"}
    assert vehicules.par_slug("moto")["ejecte"] is True
    assert vehicules.par_slug("velo")["ejecte"] is True, "on tombe d'un velo au premier choc"
    assert vehicules.par_slug("velo")["radio"] is None, "un velo n'a pas de radio"
    assert vehicules.par_slug("velo")["frequence"] > 0, "il faut des cyclistes dans la rue"
    assert vehicules.par_slug("inconnu") is None


def test_la_moto_est_la_plus_rapide_et_le_velo_le_plus_fragile():
    moto, velo = vehicules.par_slug("moto"), vehicules.par_slug("velo")
    for v in vehicules.CATALOGUE:
        assert moto["vitesse_max"] >= v["vitesse_max"], v["slug"]
        assert velo["vie"] <= v["vie"], v["slug"]
    assert velo["vitesse_max"] < moto["vitesse_max"] / 2, "un velo ne suit pas une moto"


def test_le_trafic_et_la_physique_sont_bornes():
    t, ph = vehicules.TRAFIC, vehicules.PHYSIQUE
    assert 1 <= t["vehicules_max"] <= 30 and 0 <= t["stationnes_max"] <= 20
    assert 0.2 <= t["vitesse_ville"] <= 1.0
    assert t["feu_vert_images"] > t["feu_orange_images"] > 0
    # ⚠️ On ne se deporte pas les yeux plus courts que devant soi : la voie
    # d'a cote doit etre degagee au moins aussi loin qu'on regarde, sinon on
    # se tasse derriere un char qu'on aurait vu en restant dans sa voie.
    assert t["depassement_tuiles"] >= t["regard_tuiles"]
    assert t["depassement_images"] > 0
    assert t["naissance_px"] < t["oubli_px"]
    assert 0 < ph["sous_pas_px"] <= 4, "un sous-pas plus grand qu'un rayon traverse les murs"
    assert ph["cercles"] >= 2
    assert 0 < ph["choc_vitesse_min"] < ph["ejection_vitesse_min"]
    assert 0 < ph["renverse_vitesse_min"] < 3
    assert 0 < ph["feu_sous"] < ph["fumee_sous"] < 1
    assert ph["explosion_degats"] >= 50 and ph["explosion_rayon_px"] >= 32
    assert 0 < ph["choc_rebond"] < 1


def test_le_sous_pas_ne_traverse_jamais_un_char():
    """⚠️ Le sous-pas doit rester plus petit que le demi-largeur du char le
    plus etroit : sinon, a pleine vitesse, deux cercles se croisent sans se
    voir et la moto passe a travers l'autobus."""
    plus_etroit = min(v["largeur"] for v in vehicules.de_phase(1))
    assert vehicules.PHYSIQUE["sous_pas_px"] <= plus_etroit / 2


# --- M9 : le parc automobile ------------------------------------------------


def test_la_chaine_de_cercles_ne_laisse_aucun_trou():
    """⚠️ Le juge de geometrie. Un char est une CHAINE DE CERCLES de rayon
    `largeur / 2`, tendue sur `longueur`. Pour qu'elle couvre la carrosserie,
    il en faut au moins `longueur / largeur` : en dessous, deux cercles
    voisins laissent un trou, et une moto entre dans l'autobus par le milieu
    sans que rien ne se touche. C'est la seule raison d'etre des cinq cercles
    de l'autobus — « deux de plus » que les trois de tout le monde.
    """
    for v in vehicules.CATALOGUE:
        mini = v["longueur"] / v["largeur"]
        assert v["cercles"] >= mini, f"{v['slug']} : {v['cercles']} cercles pour {mini:.1f} demandes"
        assert v["cercles"] >= 2
    assert vehicules.par_slug("autobus")["cercles"] == vehicules.PHYSIQUE["cercles"] + 2


def test_seul_le_velo_n_a_pas_de_reservoir():
    """⚠️ Retour de Martin : aujourd'hui, un velo EXPLOSE. Il a 30 PV — le plus
    fragile du jeu — et `endommager()` appelait `exploser()` des que les PV
    tombaient a zero, pour tous les vehicules sans une seule exception. Deux
    coups de batte, et il partait en boule de feu : quarante particules, une
    deflagration de 60 px a 90 points de degats, l'ecran qui tremble, et un
    delit `explosion` a +2★. On renversait un velo, et la police arrivait.

    La regle tient sur une ligne de fiche : ce qui n'a pas de reservoir ne
    brule pas et n'explose pas. C'est ICI qu'elle se decide — pas dans un
    `slug === 'velo'` cache dans le navigateur. Le jour ou on ajoute une
    trottinette, ce test le dira."""
    sans = {v["slug"] for v in vehicules.CATALOGUE if not v["reservoir"]}
    assert sans == {"velo"}, f"le catalogue a change de sens : {sans}"
    for v in vehicules.CATALOGUE:
        assert isinstance(v["reservoir"], bool), v["slug"]
        # ⚠️ Ce qui a un moteur a de l'essence. La coupure n'est pas le prix ni
        # les PV : c'est la classe.
        if v["classe"] != "velo":
            assert v["reservoir"], f"{v['slug']} roule sans essence ?"


def test_seuls_les_lourds_defoncent():
    """Un char leger ne casse rien : sinon la ville entiere se demonte a la
    berline, et les clotures ne veulent plus rien dire."""
    for v in vehicules.CATALOGUE:
        assert 0 <= v["defonce"] < 1, v["slug"]
        if v["defonce"]:
            assert v["masse"] >= 2.0, f"{v['slug']} defonce sans etre lourd"
    lourds = {v["slug"] for v in vehicules.CATALOGUE if v["defonce"]}
    assert lourds == {"camion", "autobus", "remorqueuse"}
    assert vehicules.par_slug("camion")["defonce"] > vehicules.par_slug("remorqueuse")["defonce"], \
        "le camion est celui qui passe le mieux au travers"
    assert vehicules.PHYSIQUE["defonce_vitesse_min"] > 0


def test_l_ambulance_soigne_et_la_remorqueuse_accroche():
    assert vehicules.par_slug("ambulance")["soigne"] > 0
    assert vehicules.par_slug("ambulance")["sirene"] is True
    assert [v["slug"] for v in vehicules.CATALOGUE if v["soigne"]] == ["ambulance"]
    assert [v["slug"] for v in vehicules.CATALOGUE if v["crochet"]] == ["remorqueuse"]
    ph = vehicules.PHYSIQUE
    assert ph["crochet_cable_px"] < ph["crochet_portee_px"], \
        "le cable doit etre plus court que la portee, sinon le char accroche puis se detache"
    assert 0 < ph["crochet_raideur"] <= 1


def test_un_boulot_par_char_et_jamais_deux_fois_le_meme():
    """Le klaxon ne peut pas offrir deux boulots : `boulot` est la seule
    chose qui decide, et deux chars ne se partagent pas un boulot."""
    from app import economie

    boulots = [v["boulot"] for v in vehicules.CATALOGUE if v["boulot"]]
    assert len(boulots) == len(set(boulots))
    assert set(boulots) == set(economie.BOULOTS)
    for slug, boulot in economie.BOULOTS.items():
        char = vehicules.par_slug(boulot["vehicule"])
        assert char and char["boulot"] == slug, slug
        assert char["phase"] == 1, f"{slug} : le char du boulot doit rouler"


# --- Le saut se voit ---------------------------------------------------------


def test_un_saut_se_voit_ou_n_a_pas_lieu():
    """⚠️ Le juge du retour de Martin : « les rampes n'ont pas l'air de
    fonctionner ». Elles fonctionnaient — avec 0,42 d'impulsion et 0,18 de
    gravite, une berline montait de **7,8 px** pendant 0,31 s, sur des tuiles
    de 16 px et pour un char dessine 32 x 16. Ce n'est pas un saut, c'est une
    bosse, et le joueur en concluait raisonnablement que le tremplin ne marchait
    pas.

    Deux regles, et elles suffisent : un char qui decolle monte au moins sa
    propre hauteur, et un char qui ne peut pas monter `saut_hauteur_min` ne
    decolle pas du tout. Un velo qui « saute » de deux pixels est pire qu'un
    velo qui refuse la rampe.
    """
    seuil = vehicules.saut_vitesse_min()
    assert seuil > 0
    for v in vehicules.de_phase(1):
        s = vehicules.saut(v)
        if v["vitesse_max"] < seuil:
            assert s["hauteur"] == 0, f"{v['slug']} decolle sous le seuil"
            continue
        assert s["hauteur"] >= v["largeur"] / 2, (
            f"{v['slug']} ne monte que {s['hauteur']} px : ca ne se voit pas"
        )
        assert s["duree"] >= 12, f"{v['slug']} : {s['duree']} images en l'air, c'est un clignement"
    assert vehicules.saut(vehicules.par_slug("velo"))["hauteur"] == 0, \
        "un velo a 2 px/image montait de deux pixels — il ne decolle pas"
    assert vehicules.saut(vehicules.par_slug("auto"))["hauteur"] >= 16, \
        "la berline doit quitter le sol d'au moins une tuile"


def test_le_seuil_de_decollage_se_deduit_et_voyage():
    """Le navigateur n'a plus de seuil ecrit dedans : il recoit celui que
    Python calcule. L'ancien `1.5` etait une constante du JS, et c'est elle qui
    laissait sauter le velo."""
    ph = vehicules.PHYSIQUE
    attendu = (2 * ph["gravite"] * ph["saut_hauteur_min"]) ** 0.5 / ph["rampe_impulsion"]
    assert abs(vehicules.saut_vitesse_min() - attendu) < 0.01
    assert vehicules.exporter_conduite()["saut_vitesse_min"] == vehicules.saut_vitesse_min()


def test_l_elan_pour_voler_grandit_avec_la_distance_demandee():
    moto = vehicules.par_slug("moto")
    court, long = vehicules.elan_pour_voler(moto, 60), vehicules.elan_pour_voler(moto, 120)
    assert 0 < court < long, "voler plus loin doit demander plus d'elan"


def test_une_moto_et_un_velo_n_ont_pas_de_portiere():
    """Le bruit de la montee vient de la fiche, pas d'un `slug === 'velo'`
    dans le JS : une portiere claque sur une auto et un camion, et sur rien
    d'autre — une moto et un velo, on les enfourche."""
    assert set(vehicules.CLASSES_A_PORTIERES) <= set(vehicules.CLASSES)
    par_slug = {v["slug"]: v for v in vehicules.CATALOGUE}
    for slug in ("moto", "velo", "bateau"):
        assert not par_slug[slug]["portieres"], slug
    for slug in ("auto", "taxi", "police", "camion", "autobus", "ambulance", "remorqueuse"):
        assert par_slug[slug]["portieres"], slug
