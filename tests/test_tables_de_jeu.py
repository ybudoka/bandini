"""Les tables du Dragon d'or : leurs règles et ce qu'elles rendent (docs/jalons/le-casino-du-petit-canton.md,
vagues 2 et 3). La vague 3 (tricher) : le SABOT du blackjack, le compte des cartes qui le rend payant à qui mise
gros quand le compte monte — mesuré sur un million de mains —, et l'œil de la sécurité qui le remarque.

⚠️ La règle d'or : **la maison gagne en moyenne, à chaque pari**, et le retour affiché au menu est le vrai —
calculé sur tous les coups possibles (la roulette, le sic bo), ou MESURÉ sur deux cent mille coups joués avec la
stratégie d'un habitué (le blackjack, le poker, le baccara). Le banc (`test_tables_js.py`) juge que le navigateur
joue les mêmes règles, coup pour coup.
"""

import random

import pytest

from app import casino, tables_de_jeu as t
from app import videopoker as vp

#: Combien de coups pour mesurer. ⚠️ Deux cent mille : l'écart type d'une main de blackjack est d'environ 1,15
#: mise, soit 0,26 point de retour — assez pour voir qu'on reste sous cent, et à un point de l'affiché.
N = 200_000
#: Au sabot, un million de mains (quatre secondes) : le compteur parfait mise de 10 à 500 $, et son retour varie
#: d'environ 0,35 point sur un million — il en faut autant pour voir qu'il bat la maison.
SABOT = 1_000_000


def c(rang, couleur="pique"):
    """Une carte : `rang` dans RANGS (« 10 », « V », « A »), `couleur` dans COULEURS."""
    return vp.COULEURS.index(couleur) * 13 + vp.RANGS.index(rang)


def habitue_bj(main, visible):
    """La stratégie de base d'un habitué, sans doubler ni séparer (la table ne le permet pas)."""
    total, souple = t.bj_valeur(main)
    v = t.bj_valeur([visible])[0]
    if souple:
        return total <= 17 or (total == 18 and v in (9, 10, 11))
    if total >= 17:
        return False
    if total >= 13:
        return not 2 <= v <= 6
    if total == 12:
        return not 4 <= v <= 6
    return True


def mesurer(jeu, n=N, graine=1):
    """Le retour moyen de chaque pari de `jeu`, par dollar misé, sur `n` coups tirés au hasard."""
    rng = random.Random(graine)
    if jeu == "blackjack":
        # Au SABOT (vague 3), à mise égale, l'habitué double comme il faut. ⚠️ Un million de mains : c'est le même
        # sabot que les mesures du compte, ci-dessous.
        rendu = pris = 0
        for _, _, paie, mise in t.jouer_au_sabot(rng, SABOT, lambda tc: 10):
            rendu, pris = rendu + paie, pris + mise
        return {"main": rendu / pris}
    if jeu == "poker":
        rendu = mise = 0
        for _ in range(n):
            p = rng.sample(range(52), 6)
            joue = t.poker_habitue(p[:3])
            mise += 2 if joue else 1
            rendu += t.poker_regler(p[:3], p[3:], joue)
        return {"main": rendu / mise}
    if jeu == "baccara":
        r = dict.fromkeys(t.PARIS_BACCARA, 0.0)
        for _ in range(n):
            joueur, banque = t.bac_coup(rng.sample(range(52), 6))
            for pari in r:
                r[pari] += t.bac_regler(pari, joueur, banque)
        return {pari: v / n for pari, v in r.items()}
    raise ValueError(jeu)


# --- La maison gagne ---------------------------------------------------------------------------------------

def test_la_roulette_et_le_sic_bo_se_calculent_et_la_maison_gagne():
    """Trente-sept cases, 216 jets : le retour exact, et c'est lui qui est affiché (arrondi en dessous)."""
    for pari in (*t.CHANCES, *range(37)):
        assert t.roulette_retour(pari) == pytest.approx(36 / 37), pari
    assert int(100 * 36 / 37) == t.RETOURS["roulette"]["chance"] == t.RETOURS["roulette"]["numero"]
    for pari in t.PARIS_SIC_BO:
        assert t.sic_bo_retour(pari) == pytest.approx(1 - 1 / 36)
        assert int(100 * t.sic_bo_retour(pari)) == t.RETOURS["sic_bo"][pari]
    for chiffre in range(1, 7):
        assert t.sic_bo_retour(chiffre) == pytest.approx(199 / 216)
    assert int(100 * 199 / 216) == t.RETOURS["sic_bo"]["chiffre"]


def test_le_baccara_se_calcule_et_le_hasard_le_confirme():
    """Personne ne décide au baccara : son retour se CALCULE sur toutes les suites de cartes — et deux cent
    mille coups tirés au hasard retombent dessus (à quatre écarts types : l'égalité paie gros, elle varie)."""
    exact = t.bac_retours_exacts()
    # Le témoin du calcul (28 sept. 2026) : un paquet de cinquante-deux, sans commission, la banque à six paie
    # la moitié. Si une règle du tableau bouge, ces chiffres bougent.
    assert exact == pytest.approx({"joueur": 0.987136, "banque": 0.986148, "egalite": 0.842539}, abs=2e-6)
    for pari, retour in exact.items():
        assert retour < 0.99 and int(100 * retour) == t.RETOURS["baccara"][pari], (pari, retour)
    for pari, retour in mesurer("baccara").items():
        assert abs(retour - exact[pari]) < (0.024 if pari == "egalite" else 0.009), (pari, retour, exact[pari])


@pytest.mark.parametrize("jeu", ["blackjack", "poker"])
def test_deux_cent_mille_coups_rendent_moins_qu_on_y_met_au_chiffre_affiche(jeu):
    """⚠️ Mesuré, pas promis : chaque pari rend moins de cent pour cent, et l'affiché est à un point et demi
    de ce qu'on mesure (arrondi en dessous : il ne promet jamais plus que la table rend)."""
    for pari, retour in mesurer(jeu).items():
        assert retour < 0.995, f"{jeu} / {pari} rend {retour:.4f} : la maison ne gagne plus"
        affiche = t.RETOURS[jeu][pari]
        assert abs(retour * 100 - affiche) < 1.5, (jeu, pari, retour, affiche)


def test_un_joueur_qui_tire_toujours_ou_jamais_perd_plus_que_l_habitue():
    """La stratégie compte (sinon le blackjack serait une machine à sous), et aucune ne bat la maison."""
    rng = random.Random(9)
    paquets = [rng.sample(range(52), 14) for _ in range(40_000)]
    habitue = sum(t.bj_jouer(p, habitue_bj)[0] for p in paquets) / len(paquets)
    jamais = sum(t.bj_jouer(p, lambda m, v: False)[0] for p in paquets) / len(paquets)
    comme_le_croupier = sum(t.bj_jouer(p, lambda m, v: t.bj_valeur(m)[0] < 17)[0] for p in paquets) / len(paquets)
    assert jamais < habitue and comme_le_croupier < habitue < 1.0, (jamais, comme_le_croupier, habitue)


# --- Les règles, main par main ------------------------------------------------------------------------------

@pytest.mark.parametrize("main, total, souple", [
    ([c("A"), c("R")], 21, True),
    ([c("A"), c("A")], 12, True),
    ([c("A"), c("5"), c("R")], 16, False),
    ([c("9"), c("7")], 16, False),
    ([c("A"), c("6")], 17, True),
    ([c("A"), c("A"), c("9")], 21, True),
    ([c("V"), c("D"), c("2")], 22, False),
])
def test_le_total_du_blackjack(main, total, souple):
    assert t.bj_valeur(main) == (total, souple)


def test_le_croupier_tire_jusqu_a_dix_sept_et_reste_a_dix_sept_souple():
    assert t.bj_croupier([c("A"), c("6")], [c("5")]) == [c("A"), c("6")], "dix-sept souple : il reste"
    assert t.bj_croupier([c("10"), c("6")], [c("2"), c("R")]) == [c("10"), c("6"), c("2")]
    assert t.bj_croupier([c("10"), c("2")], [c("2"), c("3"), c("9")]) == [c("10"), c("2"), c("2"), c("3")]


def test_ce_que_rend_une_main_de_blackjack():
    assert t.bj_regler([c("A"), c("R")], [c("10"), c("7")]) == 2.5, "le naturel paie 3 pour 2"
    assert t.bj_regler([c("A"), c("R")], [c("A"), c("V")]) == 1, "naturel contre naturel : rendu"
    assert t.bj_regler([c("10"), c("5"), c("6")], [c("A"), c("V")]) == 0, "21 en trois ne bat pas le naturel"
    assert t.bj_regler([c("10"), c("9")], [c("10"), c("7")]) == 2
    assert t.bj_regler([c("10"), c("7")], [c("10"), c("7")]) == 1
    assert t.bj_regler([c("10"), c("5"), c("9")], [c("10"), c("6"), c("9")]) == 0, "on crève AVANT le croupier"
    assert t.bj_regler([c("10"), c("5")], [c("10"), c("6"), c("9")]) == 2


def test_la_roue_alterne_rouge_et_noir_comme_une_vraie():
    assert sorted(t.ROUE) == list(range(37)) and t.ROUE[0] == 0
    assert t.ROUGES == {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    assert t.roulette_paie("rouge", 0) == t.roulette_paie("pair", 0) == 0, "le zéro prend les chances"
    assert t.roulette_paie(0, 0) == 36 and t.roulette_paie("noir", 2) == 2 and t.roulette_paie("impair", 2) == 0


def test_le_sic_bo_et_ses_triples():
    assert t.sic_bo_paie("petit", (1, 2, 3)) == 2 and t.sic_bo_paie("grand", (1, 2, 3)) == 0
    assert t.sic_bo_paie("grand", (6, 5, 6)) == 2
    assert t.sic_bo_paie("petit", (2, 2, 2)) == t.sic_bo_paie("grand", (5, 5, 5)) == 0, "le triple est à la maison"
    assert t.sic_bo_paie(4, (4, 1, 4)) == 3 and t.sic_bo_paie(4, (4, 4, 4)) == 4 and t.sic_bo_paie(3, (1, 2, 4)) == 0


@pytest.mark.parametrize("main, attendu", [
    ([c("A", "coeur"), c("2", "coeur"), c("3", "coeur")], "quinte_flush"),
    ([c("7"), c("7", "coeur"), c("7", "trefle")], "brelan"),
    ([c("D"), c("R", "coeur"), c("A", "trefle")], "quinte"),
    ([c("A"), c("2", "coeur"), c("3", "trefle")], "quinte"),
    ([c("R"), c("A", "coeur"), c("2", "trefle")], "carte_haute"),
    ([c("2"), c("9"), c("R")], "couleur"),
    ([c("9"), c("9", "coeur"), c("R")], "paire"),
])
def test_une_main_de_trois_cartes(main, attendu):
    """⚠️ À trois cartes, la quinte bat la couleur ; la roue A-2-3 est une quinte, R-A-2 n'en est pas une."""
    assert t.poker_main(main) == attendu


def test_le_poker_departage_et_le_croupier_ouvre_a_la_dame():
    roue, haute = [c("A"), c("2", "coeur"), c("3")], [c("D"), c("R", "coeur"), c("A")]
    assert t.poker_force(haute) > t.poker_force(roue), "la roue est la plus petite quinte"
    assert t.poker_force([c("9"), c("9", "coeur"), c("4")]) > t.poker_force([c("9", "carreau"), c("9", "trefle"), c("3")])
    assert not t.poker_ouvre([c("V"), c("9", "coeur"), c("4")]) and t.poker_ouvre([c("D"), c("3", "coeur"), c("2")])
    joueur = [c("5"), c("5", "coeur"), c("9")]
    assert t.poker_regler(joueur, [c("V"), c("9", "coeur"), c("4")], True) == 3, "le croupier n'ouvre pas"
    assert t.poker_regler(joueur, [c("D"), c("9", "coeur"), c("4")], True) == 4
    assert t.poker_regler(joueur, [c("A"), c("A", "coeur"), c("4")], True) == 0
    assert t.poker_regler(joueur, [c("A"), c("A", "coeur"), c("4")], False) == 0
    assert t.poker_regler([c("7"), c("7", "coeur"), c("7", "trefle")], [c("A"), c("A", "coeur"), c("4")], True) == 8


def test_le_baccara_suit_son_tableau():
    # Un naturel arrête tout ; le joueur tire à cinq ; la banque à trois tire, sauf sur un huit.
    assert t.bac_coup([c("9"), c("2"), c("R"), c("3"), c("5"), c("5")]) == ([c("9"), c("R")], [c("2"), c("3")])
    joueur, banque = t.bac_coup([c("2"), c("R"), c("3"), c("3"), c("8"), c("4")])
    assert len(joueur) == 3 and len(banque) == 2, "la banque à trois ne tire pas sur un huit"
    joueur, banque = t.bac_coup([c("2"), c("R"), c("3"), c("3"), c("7"), c("4")])
    assert len(banque) == 3
    # La banque à six ne tire que sur un six ou un sept du joueur ; à quatre, sur deux à sept ; à cinq, sur quatre
    # à sept. (Les cartes : joueur 0 et 2, banque 1 et 3, puis la troisième du joueur, puis celle de la banque.)
    for banque, troisieme, tire in (("6", "6", True), ("6", "7", True), ("6", "8", False), ("6", "5", False),
                                    ("4", "2", True), ("4", "A", False), ("4", "8", False),
                                    ("5", "4", True), ("5", "3", False), ("3", "9", True), ("7", "6", False)):
        paquet = [c("2"), c("R"), c("3"), c(banque), c(troisieme), c("9")]
        assert len(t.bac_coup(paquet)[1]) == (3 if tire else 2), (banque, troisieme)
    assert len(t.bac_coup([c("3"), c("2"), c("3"), c("3"), c("9"), c("9")])[1]) == 3, "joueur reste à six : la banque tire à cinq"
    assert t.bac_point([c("7"), c("8"), c("R")]) == 5 and t.bac_point([c("A"), c("V")]) == 1
    assert t.bac_regler("banque", [c("2"), c("3")], [c("3"), c("3")]) == 1.5, "la banque qui gagne à six"
    assert t.bac_regler("joueur", [c("2"), c("3")], [c("2"), c("3")]) == 1 and t.bac_regler("egalite", [c("2")], [c("2")]) == 9


# --- La salle et le paquet ------------------------------------------------------------------------------------

def test_les_cinq_tables_ont_leur_croupier_et_leur_point():
    salle = casino.PIECE
    types = [p["type"] for p in salle["points"]]
    assert sorted(j for j, _ in casino.TABLES) == sorted(t.JEUX)
    for jeu, x in casino.TABLES:
        assert types.count(jeu) == 1, jeu
        point = next(p for p in salle["points"] if p["type"] == jeu)
        assert salle["sol"][point["y"]][point["x"]] == "!", f"le point {jeu} n'est pas sur le feutre"
        assert salle["sol"][point["y"] + 1][point["x"]] == salle["plancher"], "le joueur se tient devant"
        assert {"qui": "croupier", "x": x, "y": point["y"] - 2} in salle["gens"], f"{jeu} n'a pas de croupier"


def test_les_mises_sont_paires_et_le_navigateur_recoit_les_regles():
    """⚠️ Paires : le naturel à 3 pour 2 et la banque à six tombent sur un dollar rond."""
    assert all(m % 2 == 0 for m in t.MISES)
    for m in t.MISES:
        assert (m * t.NATUREL).is_integer() and (m * t.BANQUE_SIX).is_integer()
    r = t.pour_le_navigateur()
    assert r["roue"] == list(t.ROUE) and r["mises"] == list(t.MISES) and r["par_jour"] == t.COUPS_PAR_JOUR
    assert set(r["retours"]) == set(t.JEUX) and all(v < 100 for d in r["retours"].values() for v in d.values())


# --- La vague 3 : le sabot, le compte, doubler, la sécurité ----------------------------------------------------

def test_doubler_prend_une_deuxieme_mise_et_une_seule_carte():
    #          joueur  croupier joueur croupier  la carte   le croupier tire
    paquet = [c("6"), c("6", "coeur"), c("5"), c("10"), c("10", "coeur"), c("10", "trefle"), c("2")]
    paie, fois, joueur, croupier = t.bj_main(paquet, lambda m, v: True, lambda m, v: True)
    assert fois == 2 and joueur == [c("6"), c("5"), c("10", "coeur")], "doubler : UNE carte, pas une de plus"
    assert croupier == [c("6", "coeur"), c("10"), c("10", "trefle")] and paie == 4, "22 : le croupier crève, 4 mises"
    assert t.bj_main(paquet, lambda m, v: False)[:2] == (2, 1), "sans doubler : une seule mise, gagnée"
    naturel = [c("A"), c("9"), c("R"), c("7")]
    assert t.bj_main(naturel, lambda m, v: True, lambda m, v: True)[:2] == (2.5, 1), "on ne double pas un naturel"
    assert t.bj_jouer(paquet, lambda m, v: True)[0] == 2, "bj_jouer ne double jamais (le jumeau de la vague 2)"
    assert t.bj_habitue_double([c("6"), c("5")], c("6")) and not t.bj_habitue_double([c("6"), c("5")], c("A"))


def test_le_compte_hi_lo():
    assert [t.hi_lo(c(r)) for r in vp.RANGS] == [1, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, -1, -1]
    assert sum(t.hi_lo(x) for x in range(52)) == 0, "un paquet entier revient à zéro"
    assert t.compte_par_paquet(6, 78) == 4 and t.compte_par_paquet(-3, 26) == -6
    assert [t.compteur_parfait(tc) for tc in (-3, 0.5, 1, 2.5, 3.9, 4, 6)] == [10, 10, 20, 50, 100, 200, 500]
    assert set(t.MISES_BLACKJACK) >= {t.compteur_parfait(tc) for tc in range(-5, 9)}, "chaque mise se pose à la table"
    assert all(m % 2 == 0 for m in t.MISES_BLACKJACK), "paires : le naturel à 3 pour 2 tombe rond"


def test_le_sabot_se_rebrasse_a_la_carte_de_coupe():
    """Les cartes sortent dans l'ordre, main après main, et le croupier ne rebrasse qu'une fois la carte de coupe
    sortie : environ une fois toutes les quinze mains (soixante-dix-huit cartes, un peu plus de cinq par main)."""
    class Compte(random.Random):
        brassages = 0

        def shuffle(self, x):
            Compte.brassages += 1
            super().shuffle(x)
    mains = list(t.jouer_au_sabot(Compte(4), 300, lambda tc: 10))
    assert mains[0][0] == 0
    assert 300 * 4.5 / t.COUPE <= Compte.brassages <= 300 * 6.5 / t.COUPE, Compte.brassages
    assert len({round(m[0], 3) for m in mains}) > 30, "le compte bouge d'une main à l'autre"


def test_sans_compter_la_maison_gagne_et_en_comptant_on_la_bat():
    """⚠️ LA MESURE DE LA VAGUE 3, sur un million de mains au sabot, les mêmes pour tous : à mise égale, la
    maison garde près d'un pour cent ; un compteur PARFAIT qui mise de 10 à 500 $ selon le compte par paquet la
    bat d'environ un et demi ; un compteur prudent (de 10 à 100 $) la bat à peine."""
    plat = parfait = prudent = 0.0
    mises = {"plat": 0.0, "parfait": 0.0, "prudent": 0.0}
    for tc, _, paie, pris in t.jouer_au_sabot(random.Random(1), SABOT, lambda tc: 1):
        for nom, m in (("plat", 10), ("parfait", t.compteur_parfait(tc)), ("prudent", min(100, t.compteur_parfait(tc)))):
            mises[nom] += pris * m
            if nom == "plat":
                plat += paie * m
            elif nom == "parfait":
                parfait += paie * m
            else:
                prudent += paie * m
    retour = {"plat": plat / mises["plat"], "parfait": parfait / mises["parfait"], "prudent": prudent / mises["prudent"]}
    assert retour["plat"] < 0.995, retour
    assert int(100 * retour["plat"]) == t.RETOURS["blackjack"]["main"], "l'affiché est le retour au sabot"
    assert retour["parfait"] > 1.005, f"compter parfaitement ne paie pas : {retour}"
    assert retour["plat"] < retour["prudent"] < retour["parfait"], retour


def jours_de_casino(miser, jours=300, graine=5):
    """Des jours de quarante mains au sabot, l'œil de la sécurité ouvert : combien de jours on est averti,
    combien on est sorti, et à quelle main."""
    rng, des = random.Random(graine), random.Random(graine + 1)
    averti = sorti = 0
    quand = []
    for _ in range(jours):
        chaleur, habitude, net, deja = 0.0, None, 0.0, False
        for k, (tc, mise, paie, pris) in enumerate(t.jouer_au_sabot(rng, 40, lambda tc: miser(tc, des))):
            if chaleur >= t.SURVEILLANCE["sortir"]:
                sorti += 1
                quand.append(k)
                break
            chaleur, habitude = t.chaleur_de_la_mise(chaleur, habitude, mise, tc)
            net += paie - pris
            chaleur = t.chaleur_du_gain(chaleur, net, paie - pris)
            if chaleur >= t.SURVEILLANCE["avertir"] and not deja:
                deja, averti = True, averti + 1
    return averti, sorti, sorted(quand)


def test_la_securite_laisse_jouer_le_joueur_et_sort_le_compteur():
    """Qui mise toujours pareil n'est jamais inquiété, à 10 comme à 500 $ ; le compteur parfait (de 10 à 500)
    est sorti plus d'un jour sur trois, vers sa quinzième main ; le prudent (de 10 à 100) rarement ; et miser
    gros sur un sabot froid, de temps en temps, couvre son jeu."""
    for mise in (10, 500):
        assert jours_de_casino(lambda tc, d: mise)[:2] == (0, 0), f"un joueur à {mise} $ inquiété"
    averti, sorti, quand = jours_de_casino(lambda tc, d: t.compteur_parfait(tc))
    assert averti > 150 and sorti > 100, (averti, sorti)
    assert quand[len(quand) // 2] <= 25, f"sorti trop tard : main {quand[len(quand) // 2]}"
    prudent = jours_de_casino(lambda tc, d: min(100, t.compteur_parfait(tc)))[1]
    couvert = jours_de_casino(lambda tc, d: 50 if tc <= 0 and d.random() < 0.15 else min(100, t.compteur_parfait(tc)))[1]
    assert couvert < prudent < sorti / 2, (couvert, prudent, sorti)


def test_ce_que_l_oeil_pense_d_une_mise():
    s = t.SURVEILLANCE
    assert t.chaleur_de_la_mise(0, None, 50, 5) == (0, 50), "la première mise EST l'habitude"
    chaud, hab = t.chaleur_de_la_mise(10, 10, 80, 3)
    assert chaud == pytest.approx(10 + s["rampe"] * 3 * 2) and hab == pytest.approx(10 + 70 * s["habitude"])
    assert t.chaleur_de_la_mise(30, 10, 80, 0)[0] == pytest.approx(30 - s["couverture"] * 3), "froid : ça couvre"
    assert t.chaleur_de_la_mise(30, 10, 80, 1)[0] == 30, "tiède : rien à dire"
    assert t.chaleur_de_la_mise(30, 20, 10, 5)[0] == 30 - s["calme"], "à sa mise ou moins : l'œil se calme"
    assert t.chaleur_de_la_mise(1, 20, 10, 5)[0] == 0 and t.chaleur_de_la_mise(149, 10, 500, 9)[0] == 150
    assert t.chaleur_du_gain(10, s["gains"] + 1, 20) == 10 + s["par_gain"]
    assert t.chaleur_du_gain(10, s["gains"] - 1, 20) == 10 and t.chaleur_du_gain(10, 5000, -20) == 10
    assert s["avertir"] < s["sortir"] and s["oublie_sous"] < s["avertir"]
    r = t.pour_le_navigateur()
    assert r["surveillance"] == s and r["sabot"] == {"paquets": t.PAQUETS_DU_SABOT, "coupe": t.COUPE,
                                                      "mises": list(t.MISES_BLACKJACK)}
