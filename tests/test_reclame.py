"""Les commerces de fruits de mer et les hommes-sandwichs (13 sept. 2026).

Demande de Martin : « ajoute des commerces de fruits de mer et des solliciteurs
hommes-sandwichs ». Deux choses qui se tiennent : la cabane du port a besoin
qu'on sache qu'elle existe, et l'homme-sandwich est celui qui le crie.

Ici, les juges du catalogue et de la carte ; ceux du jeu (il vient vers toi,
il te parle, le coupon vaut quelque chose) sont dans `test_reclame_js.py`.
"""

import pytest

from app import audio, carte, devantures, economie, magasins, pietons

#: Au dollar, rien ne bat le hot-dog (`economie.py` le dit en toutes lettres).
PAR_DOLLAR_MAX = (economie.TARIFS["hotdog_pv"] + economie.TARIFS["hotdog_souffle"]) / economie.TARIFS["hotdog"]


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


# --- Les fruits de mer ---------------------------------------------------------


def test_la_cabane_a_fruits_de_mer_est_un_commerce_du_port():
    cabane = magasins.ambulant("fruits_de_mer")
    assert cabane and cabane["service"] == "manger"
    assert set(cabane["districts"]) == {"quais", "pointe"}, "c'est le port qu'on mange"
    assert cabane["reclame"], "personne ne crie pour la cabane"
    assert cabane["sprite"] == "cabane_fruits_de_mer"


def test_la_cabane_ne_se_pose_qu_aux_quais_et_a_la_pointe(ville):
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    poses = [p for p in ville["ambulants"] if p["slug"] == "fruits_de_mer"]
    assert len(poses) >= 2, f"seulement {len(poses)} cabane(s)"
    for pose in poses:
        district = chantier.district_en(pose["x"], pose["y"])
        assert district in ("quais", "pointe"), f"une cabane a fruits de mer dans {district}"


def test_les_quais_et_la_pointe_ont_des_enseignes_de_fruits_de_mer():
    quais = {nom for nom, _ in devantures.COMMERCES["quais"]}
    pointe = {nom for nom, _ in devantures.COMMERCES["pointe"]}
    assert {"FRUITS DE MER", "HOMARD VIVANT", "CREVETTES", "CRABE DES NEIGES"} <= quais
    assert "FRUITS DE MER" in pointe
    # Et pas a La Shop ni aux Erables : un homard en banlieue, c'est un district repeint.
    for district in ("shop", "erables", "faubourg"):
        noms = {nom for nom, _ in devantures.COMMERCES[district]}
        assert not (noms & {"FRUITS DE MER", "HOMARD VIVANT", "CRABE DES NEIGES"}), district


def test_la_poissonnerie_sert_des_fruits_de_mer():
    slugs = {a["slug"] for a in magasins.COMPTOIRS["marine"]["articles"]}
    assert {"guedille", "crevettes", "chaudree"} <= slugs


# --- De quoi manger et boire partout ou ca a du sens ----------------------------


def test_chaque_comptoir_qui_le_peut_nourrit_et_abreuve():
    """Demande de Martin : « plus de bouffe et de choses a manger et a boire
    dans tous les magasins, ou ca fit ». La friperie n'en vend pas — ca ne
    fitte pas — et c'est la seule."""
    for genre, comptoir in magasins.COMPTOIRS.items():
        mange = [a for a in comptoir["articles"] if a["gain_souffle"]]
        if genre == "mode":
            assert not mange, "la friperie ne vend pas a manger"
            continue
        assert len(mange) >= 2, f"{genre} : {len(mange)} chose(s) a manger ou a boire seulement"
    # Le depanneur (bouffe), le bar (nuit) et le magasin ont de quoi choisir.
    for genre in ("bouffe", "nuit", "commerce"):
        assert len(magasins.COMPTOIRS[genre]["articles"]) >= 5, genre


def test_rien_ne_bat_le_hot_dog_au_dollar():
    """⚠️ La regle de `economie.TARIFS` : ce qu'on achete au comptoir, on
    l'achete parce qu'on est DEVANT — pas parce que c'est une aubaine. Un
    article qui rendrait plus au dollar que le kiosque ferait du kiosque une
    arnaque."""
    for genre, comptoir in magasins.COMPTOIRS.items():
        for a in comptoir["articles"]:
            # Le cafe est l'exception assumee : il vend de la DUREE de sprint
            # (`economie.CAFE`), ses points ne sont que la soucoupe.
            if not a["tarif"] or not a["gain_pv"] or a["effet"]:
                continue
            prix = economie.TARIFS[a["tarif"]]
            rend = economie.TARIFS[a["gain_pv"]] + economie.TARIFS.get(a["gain_souffle"] or "", 0)
            assert prix > 0 and rend > 0, a
            assert rend / prix <= PAR_DOLLAR_MAX + 1e-9, f"{genre}/{a['slug']} : {rend / prix:.2f} par dollar"
    for c in magasins.AMBULANTS:
        if c["gain_pv"] and not c["effet"]:
            rend = economie.TARIFS[c["gain_pv"]] + economie.TARIFS[c["gain_souffle"]]
            assert rend / economie.TARIFS[c["tarif"]] <= PAR_DOLLAR_MAX + 1e-9, c["slug"]


def test_un_article_qui_nourrit_a_ses_deux_gains_dans_les_tarifs():
    for genre, comptoir in magasins.COMPTOIRS.items():
        for a in comptoir["articles"]:
            for cle in ("gain_pv", "gain_souffle"):
                if a[cle]:
                    assert a[cle] in economie.TARIFS, f"{genre}/{a['slug']} : {a[cle]}"
                    assert 0 < economie.TARIFS[a[cle]] <= 100


# --- L'homme-sandwich -------------------------------------------------------------


def test_l_homme_sandwich_est_un_solliciteur_de_jour_avec_son_propre_sprite():
    crieur = pietons.par_slug("homme_sandwich")
    assert crieur and crieur["metier"] == "reclame"
    assert crieur["frequence"] == 0.0, "il ne nait pas au hasard : il a un poste"
    assert crieur["sprite"] == "homme_sandwich", "sur le corps commun, sa pancarte ne se voit pas"
    debut, fin = crieur["heures"]
    assert debut < fin and pietons.travaille_a(crieur, 0.5) and not pietons.travaille_a(crieur, 0.95)
    assert crieur["courage"] == 0.0, "un solliciteur ne riposte pas, il crie"
    assert crieur not in pietons.ordinaires()


def test_la_reclame_est_un_solliciteur_pas_un_mur():
    r = magasins.RECLAME
    assert 0 < r["rabais"] < 1, "un coupon qui ne rabat rien n'est pas un coupon"
    assert 60 <= r["coupon_s"] <= 600, "il expire, mais on a le temps d'y aller"
    assert r["portee_px"] < r["rayon_tuiles"] * carte.TUILE_PX, "il s'arrete avant de te rentrer dedans"
    assert r["boniment_images"] < r["repos_images"], "il parle moins qu'il ne se tait"
    mini, maxi = r["poste_tuiles"]
    assert 2 <= mini < maxi <= 20
    assert r["poste_rayon_px"] >= 48, "il fait les cent pas, il n'attend pas au lampadaire"


def test_chaque_homme_sandwich_a_un_poste_pres_de_son_kiosque(ville):
    """Sur le trottoir, dans le meme district, ni devant le kiosque ni a l'autre
    bout de la ville : le coupon expire, il faut que ca se marche."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    mini, maxi = magasins.RECLAME["poste_tuiles"]
    kiosques = {(p["x"], p["y"]): p["slug"] for p in ville["ambulants"]}
    postes = ville["reclames"]
    assert len(postes) >= 5, f"seulement {len(postes)} hommes-sandwichs"
    for poste in postes:
        commerce = magasins.ambulant(poste["commerce"])
        assert commerce and commerce["reclame"], poste
        k = (poste["kiosque"]["x"], poste["kiosque"]["y"])
        assert kiosques.get(k) == poste["commerce"], f"{poste} : ce kiosque n'existe pas"
        glyphe = ville["sol"][poste["y"]][poste["x"]]
        assert glyphe == ".", f"un homme-sandwich sur « {glyphe} »"
        ecart = abs(poste["x"] - k[0]) + abs(poste["y"] - k[1])
        assert mini <= ecart <= maxi, f"{poste['commerce']} : a {ecart} tuiles de son kiosque"
        assert chantier.district_en(poste["x"], poste["y"]) == chantier.district_en(*k)
    # Un kiosque qui a un boniment recrute ; les autres (journaux, cafe) non.
    recrutes = {p["commerce"] for p in postes}
    for c in magasins.AMBULANTS:
        if c["reclame"]:
            assert c["slug"] in recrutes, f"{c['slug']} n'a personne pour crier"
        else:
            assert c["slug"] not in recrutes, f"{c['slug']} n'a rien a crier"


def test_le_boniment_tient_dans_une_bulle():
    for c in magasins.AMBULANTS:
        if c["reclame"]:
            assert devantures.largeur_texte_px(c["reclame"]) <= 120, c["reclame"]


def test_le_crieur_a_de_quoi_crier():
    crieur = [v for v in audio.VOIX if v["genre"] == "crieur"]
    assert len(crieur) >= 2
    for v in crieur:
        assert v["voix"] == audio.VOIX_CRIEUR, "le crieur a sa voix de pub"
        assert v["texte"].endswith("!"), "un crieur crie"


def test_le_paquet_porte_la_reclame_et_les_postes():
    from app import definitions

    paquet = definitions.assembler()
    assert paquet["reclame"] == magasins.RECLAME
    assert paquet["carte"]["reclames"]
    assert any(c["slug"] == "fruits_de_mer" for c in paquet["ambulants"])
