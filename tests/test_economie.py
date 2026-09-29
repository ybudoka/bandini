import math

import pytest

from app import carte, economie, recherche


@pytest.mark.parametrize("argent", [0, 10, 500, 100_000])
@pytest.mark.parametrize("casier", [0, 1, 5, economie.CASIER_MAX, 99])
def test_l_amende_ne_depasse_jamais_l_argent_ni_le_zero(argent, casier):
    for etoiles in range(0, 7):
        a = economie.amende(argent, etoiles, casier)
        assert 0 <= a <= argent


def test_l_amende_monte_avec_les_etoiles_et_le_casier():
    riche = 10**9
    for casier in range(economie.CASIER_MAX):
        assert economie.amende(riche, 1, casier) <= economie.amende(riche, 1, casier + 1)
    for etoiles in range(1, 5):
        assert economie.amende(riche, etoiles, 0) < economie.amende(riche, etoiles + 1, 0)
    assert economie.amende(riche, 1, 0) == 60
    assert economie.amende(riche, 5, 2) == 2000


def test_le_pot_de_vin_tente_au_premier_delit():
    assert economie.pot_de_vin(1, 0) < economie.amende(10**9, 1, 0)
    assert economie.POT_DE_VIN_ACCEPTE[1] > economie.POT_DE_VIN_ACCEPTE[3] > economie.POT_DE_VIN_ACCEPTE[4]


def test_l_hopital_a_un_plancher_et_un_plafond():
    assert economie.facture_hopital(0) == 0
    assert economie.facture_hopital(100) == 30
    assert economie.facture_hopital(2000) == 200
    assert economie.facture_hopital(10**6) == 500


def test_prix_de_vente():
    assert economie.prix_vente(600, 100, 100, 0) == 150
    assert economie.prix_vente(600, 50, 100, 0) == 75
    assert economie.prix_vente(600, 100, 100, 5) == 0
    assert economie.prix_vente(600, 100, 0, 0) == 0


def test_la_bouffe_redonne_du_souffle_et_la_poutine_vaut_son_prix():
    souffle_max = recherche.VITESSES["endurance"]
    for cle in ("hotdog_souffle", "poutine_souffle", "cafe_souffle"):
        assert 0 < economie.TARIFS[cle] <= souffle_max, cle
    # Ce qui coute plus cher nourrit plus, en vie comme en jambes.
    assert economie.TARIFS["poutine"] > economie.TARIFS["hotdog"]
    assert economie.TARIFS["poutine_souffle"] > economie.TARIFS["hotdog_souffle"]
    assert economie.TARIFS["poutine_pv"] > economie.TARIFS["hotdog_pv"]


def test_le_surplus_de_souffle_est_un_reglage_de_poursuite():
    """⚠️ Le souffle remonte TOUT SEUL de 0,24 par image des qu'on arrete de
    courir : une barre vide se remplit en sept secondes, et une poutine a 18 $
    rendait 70 points qu'on aurait eus gratuitement en s'arretant quatre
    secondes. Le surplus est ce que la regeneration ne peut pas donner.

    Son plafond n'est donc pas un reglage de confort mais de POURSUITE : le
    joueur sprinte a 2,1, le policier court a 1,9, et chaque point de surplus
    est de l'avance qu'on ne peut pas lui reprendre. Ce test refait le calcul —
    il rougit si l'un des trois nombres bouge sans les autres."""
    v = recherche.VITESSES
    surplus = economie.SOUFFLE["surplus_max"]
    assert 0 < surplus <= v["endurance"], "un surplus plus gros que la barre elle-meme"
    # Le plein de surplus, en secondes de sprint — cafe compris, puisque le cafe
    # divise la depense et double donc ce que le surplus vaut.
    secondes = surplus / (v["endurance_par_image"] * economie.CAFE["depense"]) / 60
    assert secondes <= economie.SOUFFLE["surplus_secondes_max"], (
        f"{secondes:.1f} s de sprint gratuit sous cafe : la police ne rattrape plus personne"
    )
    # Et il vaut la peine : au moins une poutine doit pouvoir en donner un plein
    # morceau, sinon le comptoir promet une avance qu'il ne donne pas.
    assert economie.TARIFS["poutine_souffle"] >= surplus / 2


def test_le_cafe_fait_courir_plus_longtemps_sans_courir_plus_vite():
    """⚠️ Le cafe n'achete que de la DUREE.

    Les 2,1 du sprint sont ce qui separe le joueur du policier (1,9) et de la
    foule : une gorgee qui y toucherait rendrait toutes les poursuites du jeu
    ingagnables pour la police. `CAFE` ne connait donc que `depense`, et
    l'effet doit durer plus longtemps qu'un seul plein de souffle, sinon il ne
    vaut pas le detour par la roulotte.
    """
    v = recherche.VITESSES
    assert "vitesse" not in economie.CAFE and "joueur_sprint" not in economie.CAFE
    assert 0 < economie.CAFE["depense"] < 1
    a_jeun_s = v["endurance"] / v["endurance_par_image"] / 60
    sous_cafe_s = a_jeun_s / economie.CAFE["depense"]
    assert sous_cafe_s >= 2 * a_jeun_s
    assert economie.CAFE["duree_s"] > sous_cafe_s, "l'effet ne couvre meme pas un sprint"


def test_les_proprietes():
    slugs = [p["slug"] for p in economie.PROPRIETES]
    assert len(slugs) == len(set(slugs))
    # ⚠️ Le lieu de chaque propriete sur la carte est juge STRICTEMENT par
    # `test_carte.py::test_les_lieux_des_magasins_et_des_proprietes_existent` ;
    # ici une branche `pass` batissait la ville pour ne rien verifier.
    for p in economie.PROPRIETES:
        assert p["prix"] > 0 and p["revenu_par_jour"] > 0
        assert 10 <= economie.retour_sur_investissement_min(p) <= 200
    assert economie.FORTUNE_MAX >= 3 * sum(p["prix"] for p in economie.PROPRIETES)


# --- M9 : les boulots et la fourriere ---------------------------------------


def test_chaque_boulot_vaut_la_peine_sans_ecraser_les_autres():
    """⚠️ Le juge d'equilibrage, celui que le plan reclame : tous les boulots
    se comparent sur LA MEME course. Un boulot qui rapporte moins que le taxi
    ne se prend jamais ; un boulot qui rapporte cinq fois plus rend les
    quatre autres decoratifs. Entre les deux, on choisit selon l'envie — et
    c'est tout ce qu'on demande a un boulot."""
    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    assert taxi > 0
    for slug, boulot in economie.BOULOTS.items():
        gain = economie.gain_boulot(boulot)
        assert taxi <= gain <= 4 * taxi, f"{slug} rapporte {gain} $ contre {taxi} $ au taxi"
        # Rate : on garde la base, jamais rien de plus.
        rate = economie.gain_boulot(boulot, parfait=False)
        assert 0 < rate <= gain
        assert boulot["base"] > 0 and boulot["etapes"] >= 1
        assert 0 <= boulot["malus_choc"] < 1
        assert boulot["chrono_s"] >= 0


def test_la_pizza_refroidit_et_le_blesse_se_perd():
    """Les deux boulots a chrono n'ont pas le meme enjeu : la pizza ne coute
    qu'un pourboire, le blesse coute le boulot. Le chrono de l'ambulance doit
    donc etre le plus large des deux."""
    pizza, ambulance = economie.BOULOTS["pizza"], economie.BOULOTS["ambulance"]
    assert pizza["chrono_s"] > 0 and ambulance["chrono_s"] > pizza["chrono_s"]
    assert pizza["etapes"] == 3, "trois livraisons d'affilee"
    assert ambulance["prime"] > ambulance["base"], "la prime, c'est la vie du blesse"
    assert economie.BOULOTS["remorquage"]["chrono_s"] == 0, "une epave n'est plus a une heure pres"


def test_la_fourriere_ne_peut_pas_devenir_une_machine_a_argent():
    """⚠️ Racheter doit couter plus cher que revendre. Sinon le tour est
    imparable : on se fait saisir un char, on le rachete moins cher qu'il ne
    se revend au garage de Ti-Guy, et on recommence."""
    from app import vehicules

    # ⚠️ TOUT LE CATALOGUE, pas seulement la phase 1 : c'est tout le catalogue qui
    # descend au navigateur, et le juge du moteur qui faisait la même boucle sur
    # `paquet["vehicules"]` a été retiré (vague C, 28 sept. 2026) au profit de celui-ci.
    for v in vehicules.CATALOGUE:
        rachat = economie.prix_rachat(v["prix"])
        revente = economie.prix_vente(v["prix"], v["vie"], v["vie"], 0)
        assert rachat > revente, f"{v['slug']} : rachat {rachat} $, revente {revente} $"
    # Et ce sont ces nombres-là que le navigateur reçoit : une fraction exportée
    # qui divergerait de celle de Python rouvrirait la machine à argent en jeu.
    e = economie.exporter()
    assert e["vente_fraction"] == economie.VENTE_FRACTION
    for cle in ("rachat_fraction", "rachat_minimum"):
        assert e["fourriere"][cle] == economie.FOURRIERE[cle], cle
    assert economie.prix_rachat(1) == economie.FOURRIERE["rachat_minimum"]
    assert economie.FOURRIERE["places"] >= 1
    assert economie.FOURRIERE["etoiles_vol"] >= 1, "reprendre son char sans payer, c'est un vol"


def test_aucun_boulot_ne_depasse_la_borne_de_vraisemblance():
    """Le boulot le plus riche, fait a la chaine sans jamais rater, doit rester
    sous la borne de vraisemblance (`GAIN_MAX_PAR_SECONDE`). Elle gardait le
    tableau des scores ; depuis son retrait (17 sept. 2026) c'est un garde
    d'equilibre : un boulot qui l'explose rend l'argent du jeu sans valeur."""
    for slug, boulot in economie.BOULOTS.items():
        # Un boulot ne se fait pas en moins de vingt secondes par etape.
        par_seconde = economie.gain_boulot(boulot) / (20 * boulot["etapes"])
        assert par_seconde < economie.GAIN_MAX_PAR_SECONDE, slug


def test_export():
    e = economie.exporter()
    assert e["boulots"]["taxi"]["base"] == economie.BOULOTS["taxi"]["base"]
    assert set(e["boulots"]) == set(economie.BOULOTS)
    assert e["fourriere"]["rachat_fraction"] > economie.VENTE_FRACTION
    assert e["cafe"] == economie.CAFE
    assert e["tarifs"]["hotdog_souffle"] == economie.TARIFS["hotdog_souffle"]
    assert len(e["amendes"]) == 5 and len(e["amendes"][0]) == economie.CASIER_MAX + 1
    assert e["amendes"][0][0] == 60
    assert e["pots_de_vin"][0][0] == economie.pot_de_vin(1, 0)


def test_la_fourriere_laisse_le_temps_de_se_garer():
    """⚠️ Un delai avant la remorqueuse, et il n'est pas la pour etre gentil :
    sans lui, descendre deux secondes sur un passage pieton couterait le prix
    d'un rachat, et plus personne n'oserait s'arreter. Assez long pour faire
    une course, assez court pour qu'on sente qu'on est mal gare."""
    f = economie.FOURRIERE
    assert 15 <= f["remorquage_s"] <= 120, f["remorquage_s"]
    # Et se faire remorquer doit couter plus cher que le temps qu'on gagne :
    # le rachat minimum reste au-dessus d'une course de taxi type.
    course = economie.gain_boulot(economie.BOULOTS["taxi"])
    assert f["rachat_minimum"] > course, (
        f"racheter ({f['rachat_minimum']} $) coute moins qu'une course ({course} $) : "
        "se faire remorquer ne serait pas une punition"
    )


def test_un_sprint_plein_ouvre_un_ecart_borne_sur_la_police():
    """⚠️ Rendre la course gratuite casserait toutes les poursuites à pied si on
    s'arrêtait là : une course gratuite plus rapide que le policier, c'est
    s'échapper **toujours**, sans rien dépenser. La parade est celle que le
    dépôt s'est déjà donnée deux fois — le char rapide, les armes à feu : **la
    vitesse achète de la distance, jamais l'impunité.**

    Donc : le policier court **exactement** à la vitesse de la course (jugé par
    `test_monde_js::test_le_joueur_a_trois_vitesses_et_ne_traverse_pas_les_murs`),
    et c'est le sprint — qui coûte — qui ouvre un écart. Le juge le mesure, et le
    veut **borné** : assez pour casser une ligne de vue, pas assez pour semer
    quelqu'un en ligne droite.

    ⚠️ Venu de `test_moteur_js` (vague C, 28 sept. 2026) : le banc ne faisait que
    multiplier des nombres qu'on lui passait — le calcul, pas la simulation."""
    v = recherche.VITESSES

    def ecart_px(depense):
        # Un sprint dure `endurance / cout` images, et il gagne la différence de
        # vitesse à chaque image. (Arrondi à la façon de `Math.round`.)
        images = v["endurance"] / (v["endurance_par_image"] * depense)
        return math.floor((v["joueur_sprint"] - v["policier"]) * images + 0.5)

    tuiles_nu = ecart_px(1) / carte.TUILE_PX
    tuiles_cafe = ecart_px(economie.CAFE["depense"]) / carte.TUILE_PX
    assert 5 <= tuiles_nu <= 20, (
        "un sprint plein ouvre %.1f tuiles : trop peu pour casser une ligne de vue, ou trop pour être une fuite"
        % tuiles_nu
    )
    assert tuiles_cafe > tuiles_nu, "le café doit servir à s'échapper, pas seulement à courir"
    # ⚠️ Borné, café compris : la vision d'un agent porte 9 tuiles de jour.
    vision = recherche.VISION["policier"]["jour"]
    assert tuiles_cafe <= vision * 4, (
        "%.1f tuiles d'écart, c'est semer la police en ligne droite (vision : %s tuiles)"
        % (tuiles_cafe, vision)
    )
