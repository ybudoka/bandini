"""Les tables du Dragon d'or : leurs règles et ce qu'elles rendent (docs/jalons/le-casino-du-petit-canton.md,
vague 2).

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
        return {"main": sum(t.bj_jouer(rng.sample(range(52), 14), habitue_bj)[0] for _ in range(n)) / n}
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
