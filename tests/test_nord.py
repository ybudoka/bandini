"""La ville s'agrandit au nord (docs/jalons/la-ville-s-agrandit-au-nord.md)."""

from app import carte


def test_le_chantier_lit_sa_trame_et_pas_les_globales():
    """Une autre trame passée en paramètre bâtit une autre ville, même si les globales ne bougent pas."""
    trame = {"colonnes": (10, 10), "rangees": (10,), "rues_v": (4, 4, 4), "rues_h": (4, 4),
             "districts": ({"slug": "essai", "nom": "Essai", "bx": 0, "by": 0, "gang": None,
                            "gang_nom": None, "brume": False, "pietons": 0, "vehicules": 0, "police": 0,
                            "rythme": (0.1, 1.0, 1.0), "rares": (), "plan": ("hh",), "standing": ("==",)},),
             "standing": ("==",)}
    ch = carte._Chantier(("hh",), 1, trame=trame)
    assert (ch.largeur, ch.hauteur) == (32, 18)
    assert ch.district_en(5, 5) == "essai"


# --- La bande, bâtie à part (tâche 3) --------------------------------------------------------

def _bande():
    from app import nord
    return nord.batir_la_bande()


def _dans(ch, slug, o):
    from app import nord
    x0, _y0, large, _h = ch.rect_district(nord.district(slug))
    return x0 <= o["x"] < x0 + large and o["y"] < nord.DECALAGE_NORD


def test_la_bande_fait_110_rangees_plus_la_couture_et_la_largeur_de_la_trame():
    from app import nord
    ch = _bande()
    assert ch.hauteur == nord.DECALAGE_NORD + 6 and ch.largeur == 419


def test_trois_districts_dans_la_bande_avec_leur_gang():
    from app import nord
    assert [(d["slug"], d["gang"]) for d in nord.DISTRICTS_NORD] == [
        ("friches", "chevreuils"), ("canton", "cravates"), ("gare", "boulonneux")]


def test_la_gare_a_ses_voies_ses_wagons_et_son_poste():
    from app import nord
    ch = _bande()
    x0, y0, large, _h = ch.rect_district(nord.district("gare"))
    zone = ["".join(ch.sol[y][x0:x0 + large]) for y in range(y0, nord.DECALAGE_NORD)]
    assert sum(ligne.count("T") for ligne in zone) > 200, "des voies ferrées"
    # Les wagons : du toit de tôle SUR une rangée de voie (les hangars de la gare en ont aussi, à côté).
    assert sum(ligne.count("B") for ligne in zone if "T" in ligne) > 30, "des wagons"
    postes = [p for p in ch.portes if p["interieur"] == "nord_aiguillage"]
    assert len(postes) == 1 and ch.marchable_en(postes[0]["x"], postes[0]["y"] + 1)
    assert "nord_aiguillage" in ch.pieces


def test_le_canton_n_a_que_des_terrains_a_batir():
    ch = _bande()
    assert not [p for p in ch.portes if _dans(ch, "canton", p)], "personne n'y habite encore"
    pancartes = [d for d in ch.decor if d["type"] == "pancarte_a_batir" and _dans(ch, "canton", d)]
    assert len(pancartes) >= 20, len(pancartes)


def test_les_friches_ont_leurs_carcasses_et_pas_une_porte():
    ch = _bande()
    assert [d for d in ch.decor if d["type"] == "carcasse" and _dans(ch, "friches", d)]
    assert not [p for p in ch.portes if _dans(ch, "friches", p)]


def test_tout_ce_que_la_bande_nomme_commence_par_nord():
    ch = _bande()
    assert all(k.startswith("nord_") for k in ch.pieces)
    assert all(p["interieur"].startswith("nord_") and p["lieu"].startswith("nord_") for p in ch.portes)


def test_la_bande_ne_tire_rien_de_la_ville():
    """Même graine, même bande ; et bâtir la bande ne change pas la ville."""
    avant = carte.generer()
    a, b = _bande(), _bande()
    assert a.sol == b.sol and a.decor == b.decor
    assert carte.generer()["sol"] == avant["sol"]


# --- La translation (tâche 4) ----------------------------------------------------------------

def _ville_d_avant():
    return carte.generer(nord=False)


def _decalee(ville):
    import copy
    from app import nord
    v = copy.deepcopy(ville)
    nord.decaler(v, nord.DECALAGE_NORD)
    return v


def test_une_cle_inconnue_fait_echouer_la_translation():
    import copy
    import pytest
    from app import nord
    v = copy.deepcopy(_ville_d_avant())
    v["cle_neuve"] = [{"x": 1, "y": 1}]
    with pytest.raises(KeyError, match="cle_neuve"):
        nord.decaler(v, 1)


def _objets_xy(o, chemin=()):
    """Chaque objet {x, y} de la carte, par son chemin — sauf les pièces (leurs coordonnées sont à elles)."""
    if isinstance(o, dict):
        if isinstance(o.get("x"), int) and isinstance(o.get("y"), int):
            yield chemin, o["y"]
        for k, v in o.items():
            if chemin == () and k == "interieurs":
                continue
            yield from _objets_xy(v, chemin + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _objets_xy(v, chemin + (i,))


def test_chaque_objet_xy_descend_de_110_tuiles_ou_de_110_x_16_pixels():
    from app import nord
    avant = _ville_d_avant()
    apres = dict(_objets_xy(_decalee(avant)))
    vus = 0
    for chemin, y in _objets_xy(avant):
        attendu = y + nord.DECALAGE_NORD * (carte.TUILE_PX if chemin[0] == "mouillages" else 1)
        if chemin[:2] == ("relief", "montagnes"):
            attendu = y                                   # les montagnes grandissent vers le haut
        assert apres[chemin] == attendu, chemin
        vus += 1
    assert vus > 3000, vus


def test_le_sol_de_la_ville_d_avant_est_identique_110_rangees_plus_bas():
    from app import nord
    avant = _ville_d_avant()
    v = _decalee(avant)
    n = nord.DECALAGE_NORD
    assert v["sol"][n:] == avant["sol"] and v["voie"][n:] == avant["voie"]
    assert v["hauteur"] == avant["hauteur"] + n and v["grille"]["y0"] == n
    assert v["relief"]["montagnes"]["h"] == avant["relief"]["montagnes"]["h"] + n


def test_les_paires_descendent_aussi():
    from app import nord
    avant = _ville_d_avant()
    v, n = _decalee(avant), nord.DECALAGE_NORD
    assert v["autobus"]["lignes"][0]["trace"][0][1] == avant["autobus"]["lignes"][0]["trace"][0][1] + n
    assert v["autobus"]["lignes"][0]["arrets"] == avant["autobus"]["lignes"][0]["arrets"], "des indices"
    assert v["tramway"]["arrets"][0][2] == avant["tramway"]["arrets"][0][2] + n
    assert v["tramway"]["trace"][0][1] == avant["tramway"]["trace"][0][1] + n
    assert v["eboueurs"]["points"][0][2] == avant["eboueurs"]["points"][0][2] + n
    assert v["eboueurs"]["trace"][0][1] == avant["eboueurs"]["trace"][0][1] + n
    assert v["neige"]["charrue"]["trace"][0][1] == avant["neige"]["charrue"]["trace"][0][1] + n
    assert v["chemins_des_bois"][0][1] == avant["chemins_des_bois"][0][1] + n
    assert v["foire_enclos"][0][0] == avant["foire_enclos"][0][0] + n
    assert v["train_de_foire"]["voie"][0][1] == avant["train_de_foire"]["voie"][0][1] + n
    assert v["train_de_foire"]["quai"][2] == avant["train_de_foire"]["quai"][2] + n
    assert v["montagne_russe"]["voie"][0][1] == avant["montagne_russe"]["voie"][0][1] + n * carte.TUILE_PX
    assert v["montagne_russe"]["supports"][0][2] == avant["montagne_russe"]["supports"][0][2] + n
    assert v["aeroport"]["axes"][0][1] == avant["aeroport"]["axes"][0][1] + n
    assert v["aeroport"]["axes"][0][3] == avant["aeroport"]["axes"][0][3] + n
    assert v["aeroport"]["plan"][1] == avant["aeroport"]["plan"][1] + n
    assert v["aeroport"]["balises"][0][1] == avant["aeroport"]["balises"][0][1] + n
    assert v["aeroport"]["peints"][0][2] == avant["aeroport"]["peints"][0][2] + n
    assert v["aeroport"]["portes_peintes"][0][1] == avant["aeroport"]["portes_peintes"][0][1] + n
    assert v["aeroport"]["pont"]["piles"][0][1] == avant["aeroport"]["pont"]["piles"][0][1] + n
    assert v["aeroport"]["masque"]["carte_h"] == avant["aeroport"]["masque"]["carte_h"] + n
    assert v["traversier"]["escales"][0]["acces"][0][1] == avant["traversier"]["escales"][0]["acces"][0][1] + n
    c0 = next(c for c in avant["chantiers"] if isinstance(c.get("tranchee"), list))
    c1 = next(c for c in v["chantiers"] if c["id"] == c0["id"])
    assert c1["tranchee"][0][1] == c0["tranchee"][0][1] + n and c1["signaleur"][1] == c0["signaleur"][1] + n
    x, y = next(iter(avant["arrets"])).split(",")
    assert f"{x},{int(y) + n}" in v["arrets"]


# --- La pose : décaler, coller, coudre (tâche 5) ---------------------------------------------

def test_la_carte_finie_a_la_bande_au_dessus_de_la_ville_d_avant():
    from app import nord
    avant = _ville_d_avant()
    apres = carte.generer()
    n = nord.DECALAGE_NORD
    assert (apres["largeur"], apres["hauteur"]) == (avant["largeur"], avant["hauteur"] + n)
    couture = {(x, n) for x in nord.colonnes_de_la_couture()}
    assert couture, "aucune rue de la bande ne débouche sur le boulevard"
    for y, ligne in enumerate(avant["sol"]):
        for x, g in enumerate(ligne):
            if (x, y + n) not in couture:
                assert apres["sol"][y + n][x] == g, (x, y + n)
    assert "M" not in "".join(apres["sol"][y][:419] for y in range(n)), "une rangée de la bande est restée vide"


def _atteint(v, depart):
    vues, pile = {depart}, [depart]
    while pile:
        for s in carte.suivre_voie(v, *pile.pop()):
            if s not in vues:
                vues.add(s)
                pile.append(s)
    return vues


def _voies_de(v, slug):
    z = next(z for z in v["zones"] if z["slug"] == slug and not z["gang"])
    return [(x, y) for y in range(z["y"], z["y"] + z["h"]) for x in range(z["x"], z["x"] + z["l"])
            if v["voie"][y][x] != "."]


def test_on_roule_de_la_ville_au_canton_et_on_en_revient():
    v = carte.generer()
    assert set(_voies_de(v, "canton")) & _atteint(v, _voies_de(v, "faubourg")[0]), "le Faubourg → le Canton"
    assert set(_voies_de(v, "faubourg")) & _atteint(v, _voies_de(v, "canton")[0]), "le Canton → le Faubourg"
    assert set(_voies_de(v, "gare")) & _atteint(v, _voies_de(v, "friches")[0]), "les Friches → la Gare"


def test_la_bande_se_marche_depuis_le_terminus():
    v = carte.generer()
    t = next(p for p in v["points_interet"] if p["slug"] == "terminus")
    groupe = next(g for g in carte.composantes_par_terre(v)["ville"] if (t["x"], t["y"]) in g)
    assert (0, 50) in groupe, "le trottoir de ceinture des Friches ne se rejoint pas à pied"
    poste = next(p for p in v["portes"] if p["interieur"] == "nord_aiguillage")
    assert (poste["x"], poste["y"] + 1) in groupe, "le poste d'aiguillage ne se rejoint pas"


def test_les_trois_districts_de_la_bande_et_leurs_zones():
    from app import nord
    v = carte.generer()
    assert [d["slug"] for d in v["districts"][-3:]] == ["friches", "canton", "gare"]
    for slug in ("friches", "canton", "gare"):
        z = next(z for z in v["zones"] if z["slug"] == slug)
        assert z["y"] == 0 and z["y"] + z["h"] <= nord.DECALAGE_NORD, (slug, z)
    assert v["grille_nord"]["y0"] == 0 and v["grille"]["y0"] == nord.DECALAGE_NORD


def test_aucun_nom_de_la_bande_n_entre_en_collision():
    v = carte.generer()
    lieux = [p["lieu"] for p in v["portes"]]
    assert len(lieux) == len(set(lieux)), [x for x in lieux if lieux.count(x) > 1][:5]
    assert all(p["interieur"] in v["interieurs"] for p in v["portes"])


def test_les_passages_de_blocs_suivent_la_ville():
    from app import blocs, nord
    v = carte.generer()
    for b in blocs.BLOCS:
        assert blocs.erreurs(b, v) == [], b["slug"]
    rang = next(b for b in blocs.pour_le_navigateur() if b["slug"] == "rang")
    assert rang["passage"]["de"] == 171 + nord.DECALAGE_NORD


def test_les_croisements_de_la_couture_s_ouvrent_au_nord():
    """⚠️ Les chars du navigateur choisissent leur sortie par `bras` (`Vehicules`, `inter.bras`) : sans « N »,
    la circulation de la ville ne monterait jamais dans la bande, même si les flèches y mènent."""
    from app import nord
    v, n = carte.generer(), nord.DECALAGE_NORD
    couture = nord.colonnes_de_la_couture()
    boites = [i for i in v["intersections"] if i["y"] <= n + carte.TROTTOIR < i["y"] + i["h"]
              and any(i["x"] <= x < i["x"] + i["l"] for x in couture)]
    assert len(boites) >= 10, len(boites)
    assert all("N" in i["bras"] for i in boites), [i for i in boites if "N" not in i["bras"]][:3]
    for x in couture:
        assert any(i["x"] <= x < i["x"] + i["l"] for i in boites), f"la voie x={x} débouche hors d'un croisement"


# --- Corrections de la relecture ---------------------------------------------------------------

def test_une_autre_graine_se_genere_et_se_decale_aussi():
    """⚠️ Une autre graine n'a pas toujours tout (pas d'éboueurs, p. ex.) : une clé à `None` ne descend pas,
    elle ne plante pas la génération. Treize fichiers de juges bâtissent d'autres graines."""
    from app import nord
    for graine in (1, 7, 777):
        v = carte.generer(graine=graine)
        assert v["hauteur"] == 304 + nord.DECALAGE_NORD, graine


def test_les_cibles_de_la_galerie_descendent_avec_elle():
    from app import nord
    avant, v = _ville_d_avant(), carte.generer()
    a = next(j for j in avant["jeux_de_foire"] if j.get("cibles"))
    b = next(j for j in v["jeux_de_foire"] if j["slug"] == a["slug"])
    assert [c[1] for c in b["cibles"]] == [c[1] + nord.DECALAGE_NORD for c in a["cibles"]]


def test_la_bande_n_a_ni_pont_ni_quai():
    """Le pont de La Pointe (`carte.PONTS`) est indexé sur la trame de la VILLE : il n'a rien à faire dans la
    bande, dont la trame est autre (il y peignait du quai sur onze rangées de la gare)."""
    ch = _bande()
    assert not ch._ponts_de_la_trame, ch._ponts_de_la_trame
    assert "Q" not in "".join("".join(r) for r in ch.sol[:110])


def test_la_gare_n_a_qu_une_porte_le_poste_d_aiguillage():
    """La spec : UNE pièce visitable à la Gare. Ni clinique, ni notaire, ni disco au milieu des wagons."""
    ch = _bande()
    portes = [p for p in ch.portes if _dans(ch, "gare", p)]
    assert [p["interieur"] for p in portes] == ["nord_aiguillage"], [p["interieur"] for p in portes]
    assert not [d for d in ch.devantures if _dans(ch, "gare", d)], "des devantures dans la gare"


def test_le_lecteur_de_la_carte_finie_lit_les_deux_trames():
    """`nord.LECTEUR` : le quartier d'une tuile de la CARTE FINIE — la bande au-dessus de `DECALAGE_NORD`, la
    ville d'avant en dessous (le miroir de `Monde.lettreDuBloc`)."""
    from app import nord
    n, lecteur = nord.DECALAGE_NORD, nord.LECTEUR
    ville = carte._Chantier(carte.PLAN, carte.GRAINE)
    assert lecteur.district_en(140, 20) == "canton" and lecteur.district_en(140, n + 20) == "faubourg"
    assert lecteur.standing_en(10, 10) == "pauvre" and lecteur.standing_en(10, n + 10) == ville.standing_en(10, 10)
    assert lecteur.usage_en(300, 20) == "industriel"
    assert lecteur.usage_en(140, n + 20) == ville.usage_en(140, 20)
