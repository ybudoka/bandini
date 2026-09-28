"""Les tables du Dragon d'or — le blackjack, la roulette, le poker à trois cartes, le sic bo et le baccara
(docs/jalons/le-casino-du-petit-canton.md, vague 2).

Martin (28 sept. 2026) : « ajoute des machines : roulette, poker, black jack et plus ». Cinq tables dans la
grande salle, un croupier à chacune. Python dit les règles (les mises, ce que chaque pari paie, la limite du
jour) et joue chaque coup à l'identique de `static/js/tables.js` ; le navigateur joue le coup qu'on voit.

⚠️ **LA MAISON GAGNE, EN MOYENNE, À CHAQUE PARI** — la règle du vidéopoker : un jeu d'argent qui paierait plus
qu'un boulot casserait l'économie. Le retour AFFICHÉ au menu (`RETOURS`) est :
- **calculé** là où tous les coups se comptent : la roulette (trente-sept cases), le sic bo (216 jets) et le
  baccara, où personne ne décide rien (toutes les suites de valeurs de cartes, `bac_retours_exacts`) ;
- **mesuré** là où le joueur décide (`tests/test_tables_de_jeu.py` joue deux cent mille mains, avec la stratégie
  d'un habitué : au blackjack, la stratégie de base sans doubler ni séparer ; au poker, « jouer à partir de
  dame-six-quatre »).
Arrondi à l'entier INFÉRIEUR, comme au vidéopoker : l'affiché ne promet jamais plus que la table rend.
Le retour se compte par dollar MISÉ : au poker, la deuxième mise (JOUER) compte aussi.

⚠️ **UN PAQUET NEUF À CHAQUE MAIN** (le blackjack, le poker, le baccara) : cinquante-deux cartes battues, semées
par la graine de la partie et le numéro du coup (`tables.js`, jamais `B.rng()`). On ne peut donc pas compter les
cartes — c'est la vague 3 (tricher) qui mettra un sabot de plusieurs mains sur la table du blackjack.

⚠️ **LES MISES SONT PAIRES** (`MISES`) : le blackjack naturel paie 3 pour 2 et la banque qui gagne avec six ne
paie que la moitié — sur une mise paire, ça tombe toujours sur un dollar rond.

Les cartes sont celles du vidéopoker : un entier de 0 à 51, `c % 13` le rang (0 le deux… 12 l'as), `c // 13`
la couleur (pique, coeur, carreau, trèfle).
"""

from __future__ import annotations

from itertools import product

#: Ce qu'on peut miser à une table, en dollars. Le joueur choisit au menu (MISE).
MISES = (10, 20, 50)

#: Combien de coups par jour de jeu, à CHAQUE table : la table finit par « fermer pour toi ».
COUPS_PAR_JOUR = 40

#: Les cinq tables, dans l'ordre de la salle (d'ouest en est), et leur nom au menu.
JEUX: dict[str, str] = {"blackjack": "BLACKJACK", "roulette": "ROULETTE", "poker": "POKER À TROIS CARTES",
                        "sic_bo": "SIC BO", "baccara": "BACCARA"}

# --- Le blackjack ------------------------------------------------------------------------------------------

#: Le croupier tire tant qu'il a moins de ça, et reste à dix-sept, même souple.
CROUPIER_RESTE = 17
#: Ce que rend un blackjack naturel (as et dix en deux cartes), mise comprise : 3 pour 2.
NATUREL = 2.5


def bj_valeur(cartes: list[int]) -> tuple[int, bool]:
    """Le total d'une main et s'il est SOUPLE (un as y compte pour onze)."""
    total, as_ = 0, 0
    for c in cartes:
        r = c % 13
        total += 1 if r == 12 else min(10, r + 2)
        as_ += r == 12
    if as_ and total + 10 <= 21:
        return total + 10, True
    return total, False


def bj_naturel(cartes: list[int]) -> bool:
    return len(cartes) == 2 and bj_valeur(cartes)[0] == 21


def bj_croupier(main: list[int], pioche: list[int]) -> list[int]:
    """Le croupier tire dans `pioche` (dans l'ordre) jusqu'à dix-sept. Rend sa main finale."""
    main, k = list(main), 0
    while bj_valeur(main)[0] < CROUPIER_RESTE:
        main.append(pioche[k])
        k += 1
    return main


def bj_regler(joueur: list[int], croupier: list[int]) -> float:
    """Ce que rend la main du joueur contre celle du croupier, en multiples de la mise (mise comprise)."""
    j, c = bj_valeur(joueur)[0], bj_valeur(croupier)[0]
    if j > 21:
        return 0
    if bj_naturel(joueur):
        return 1 if bj_naturel(croupier) else NATUREL
    if bj_naturel(croupier) or (c <= 21 and c > j):
        return 0
    return 1 if c == j else 2


def bj_jouer(paquet: list[int], tirer) -> tuple[float, list[int], list[int]]:
    """Une main entière. Le joueur reçoit les cartes 0 et 2, le croupier 1 et 3 ; ensuite on pige dans
    l'ordre. `tirer(main, visible)` dit si le joueur tire encore. ⚠️ Le jumeau de `Tables` en JS."""
    joueur, croupier, k = [paquet[0], paquet[2]], [paquet[1], paquet[3]], 4
    if not bj_naturel(joueur):
        while bj_valeur(joueur)[0] < 21 and tirer(joueur, croupier[0]):
            joueur.append(paquet[k])
            k += 1
    if bj_valeur(joueur)[0] <= 21 and not bj_naturel(joueur):
        croupier = bj_croupier(croupier, paquet[k:])
    return bj_regler(joueur, croupier), joueur, croupier


# --- La roulette -------------------------------------------------------------------------------------------

#: La roue EUROPÉENNE, un seul zéro, dans l'ordre des cases. ⚠️ Les couleurs y alternent : la case d'après le
#: zéro est rouge, la suivante noire, et ainsi de suite — le navigateur les lit ainsi (un juge le vérifie).
ROUE = (0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
        22, 18, 29, 7, 28, 12, 35, 3, 26)
ROUGES = frozenset(n for i, n in enumerate(ROUE) if i % 2 == 1)
#: Ce que rend un numéro plein, mise comprise (35 pour 1). Les chances simples rendent 2 (1 pour 1).
NUMERO_PLEIN = 36
#: Les chances simples. ⚠️ Le zéro les perd toutes : c'est lui, la maison.
CHANCES = ("rouge", "noir", "pair", "impair")


def roulette_paie(pari: str | int, n: int) -> int:
    """Ce que rend `pari` (une chance simple, ou un numéro de 0 à 36) quand la bille tombe sur `n`."""
    if isinstance(pari, int):
        return NUMERO_PLEIN if pari == n else 0
    if n == 0:
        return 0
    gagne = {"rouge": n in ROUGES, "noir": n not in ROUGES, "pair": n % 2 == 0, "impair": n % 2 == 1}[pari]
    return 2 if gagne else 0


def roulette_retour(pari: str | int) -> float:
    return sum(roulette_paie(pari, n) for n in range(37)) / 37


# --- Le sic bo ---------------------------------------------------------------------------------------------

#: PETIT (4 à 10) et GRAND (11 à 17) rendent 2 — et perdent sur un triple : c'est la maison.
#: UN CHIFFRE rend 1 + le nombre de dés qui le montrent (1 pour 1, 2 pour 1, 3 pour 1).
PARIS_SIC_BO = ("petit", "grand")


def sic_bo_paie(pari: str | int, des: tuple[int, int, int]) -> int:
    """Ce que rend `pari` (petit, grand, ou un chiffre de 1 à 6) sur ces trois dés."""
    if isinstance(pari, int):
        k = sum(1 for d in des if d == pari)
        return 1 + k if k else 0
    if des[0] == des[1] == des[2]:
        return 0
    total = sum(des)
    return 2 if (4 <= total <= 10) == (pari == "petit") else 0


def sic_bo_retour(pari: str | int) -> float:
    jets = list(product(range(1, 7), repeat=3))
    return sum(sic_bo_paie(pari, d) for d in jets) / len(jets)


# --- Le poker à trois cartes -------------------------------------------------------------------------------

#: Les mains, de la plus petite à la plus grosse. ⚠️ À trois cartes, la quinte bat la couleur (elle est plus
#: rare), et la roue A-2-3 est une quinte, la plus petite.
MAINS_POKER = ("carte_haute", "paire", "couleur", "quinte", "brelan", "quinte_flush")
NOMS_POKER = {"carte_haute": "CARTE HAUTE", "paire": "PAIRE", "couleur": "COULEUR", "quinte": "QUINTE",
              "brelan": "BRELAN", "quinte_flush": "QUINTE FLUSH"}
#: Le croupier « ouvre » à partir de dame haute : sinon, la mise de départ est payée et JOUER est rendu.
DAME = 10
#: Le bonus de la mise de départ, payé en plus sur une grosse main, que le croupier ouvre ou pas.
BONUS_POKER = {"quinte": 1, "brelan": 4, "quinte_flush": 5}


def poker_force(cartes: list[int]) -> tuple[int, ...]:
    """La force d'une main de trois cartes : (rang de la main, puis les cartes qui départagent)."""
    rangs = sorted((c % 13 for c in cartes), reverse=True)
    couleur = len({c // 13 for c in cartes}) == 1
    roue = rangs == [12, 1, 0]
    quinte = roue or (rangs[0] - rangs[2] == 2 and len(set(rangs)) == 3)
    haut = (1, 0, -1) if roue else tuple(rangs)
    if quinte and couleur:
        return (5,) + haut
    if rangs[0] == rangs[2]:
        return (4,) + haut
    if quinte:
        return (3,) + haut
    if couleur:
        return (2,) + haut
    if rangs[0] == rangs[1] or rangs[1] == rangs[2]:
        paire = rangs[1]
        seule = rangs[2] if rangs[0] == rangs[1] else rangs[0]
        return (1, paire, seule)
    return (0,) + haut


def poker_main(cartes: list[int]) -> str:
    return MAINS_POKER[poker_force(cartes)[0]]


def poker_ouvre(cartes: list[int]) -> bool:
    f = poker_force(cartes)
    return f[0] >= 1 or f[1] >= DAME


def poker_regler(joueur: list[int], croupier: list[int], joue: bool) -> int:
    """Ce que rend la main, en multiples de la mise de départ, mise comprise (JOUER a misé une fois de plus)."""
    if not joue:
        return 0
    bonus = BONUS_POKER.get(poker_main(joueur), 0)
    if not poker_ouvre(croupier):
        return 3 + bonus                      # le départ payé, JOUER rendu
    fj, fc = poker_force(joueur), poker_force(croupier)
    if fj > fc:
        return 4 + bonus
    if fj == fc:
        return 2 + bonus
    return bonus


def poker_habitue(cartes: list[int]) -> bool:
    """La stratégie d'un habitué : JOUER à partir de dame-six-quatre, passer en dessous."""
    f = poker_force(cartes)
    return f[0] >= 1 or f[1:] >= (DAME, 4, 2)


# --- Le baccara --------------------------------------------------------------------------------------------

#: Les paris, et ce qu'ils rendent quand ils gagnent (mise comprise). ⚠️ SANS COMMISSION : la banque qui gagne
#: avec six ne rend que la moitié de son gain (`BANQUE_SIX`) ; sur une égalité, JOUEUR et BANQUE sont rendus.
PARIS_BACCARA = ("joueur", "banque", "egalite")
EGALITE = 9
BANQUE_SIX = 1.5


def bac_point(cartes: list[int]) -> int:
    """Le point : l'as vaut un, les figures et le dix rien, et on ne garde que les unités."""
    return sum(0 if c % 13 >= 8 and c % 13 != 12 else (1 if c % 13 == 12 else c % 13 + 2) for c in cartes) % 10


def _bac_tire_banque(banque: int, troisieme: int | None) -> bool:
    if troisieme is None:
        return banque <= 5
    return (banque <= 2 or (banque == 3 and troisieme != 8) or (banque == 4 and 2 <= troisieme <= 7)
            or (banque == 5 and 4 <= troisieme <= 7) or (banque == 6 and troisieme in (6, 7)))


def bac_coup(paquet: list[int]) -> tuple[list[int], list[int]]:
    """Le coup, selon le tableau (personne n'y décide rien) : le joueur a les cartes 0 et 2, la banque 1 et 3,
    puis la troisième carte de chacun, s'il la tire, dans l'ordre. ⚠️ Le jumeau de `Tables` en JS."""
    joueur, banque, k = [paquet[0], paquet[2]], [paquet[1], paquet[3]], 4
    if bac_point(joueur) >= 8 or bac_point(banque) >= 8:
        return joueur, banque
    troisieme = None
    if bac_point(joueur) <= 5:
        joueur.append(paquet[k])
        k += 1
        troisieme = bac_point([joueur[2]])
    if _bac_tire_banque(bac_point(banque), troisieme):
        banque.append(paquet[k])
    return joueur, banque


def bac_regler(pari: str, joueur: list[int], banque: list[int]) -> float:
    pj, pb = bac_point(joueur), bac_point(banque)
    if pari == "egalite":
        return EGALITE if pj == pb else 0
    if pj == pb:
        return 1
    if pari == "joueur":
        return 2 if pj > pb else 0
    return (BANQUE_SIX if pb == 6 else 2) if pb > pj else 0


def bac_retours_exacts() -> dict[str, float]:
    """Le retour EXACT de chaque pari du baccara, sur un paquet de cinquante-deux : on passe toutes les suites de
    VALEURS de cartes (seize cartes valent zéro, quatre chacune des autres), chacune avec sa probabilité, en ne
    tirant la cinquième et la sixième que si le tableau les demande."""
    compte = [16] + [4] * 9
    retours = dict.fromkeys(PARIS_BACCARA, 0.0)

    def regler(pj: int, pb: int, poids: float) -> None:
        for pari in retours:
            if pari == "egalite":
                retours[pari] += poids * (EGALITE if pj == pb else 0)
            elif pj == pb:
                retours[pari] += poids
            elif pari == "joueur":
                retours[pari] += poids * (2 if pj > pb else 0)
            else:
                retours[pari] += poids * ((BANQUE_SIX if pb == 6 else 2) if pb > pj else 0)

    def piger(reste: int):
        for v in range(10):
            if compte[v]:
                p = compte[v] / reste
                compte[v] -= 1
                yield v, p
                compte[v] += 1

    for a, pa in piger(52):
        for b, pb_ in piger(51):
            for c_, pc in piger(50):
                for d, pd in piger(49):
                    poids = pa * pb_ * pc * pd
                    joueur, banque = (a + c_) % 10, (b + d) % 10
                    if joueur >= 8 or banque >= 8:
                        regler(joueur, banque, poids)
                    elif joueur <= 5:
                        for e, pe in piger(48):
                            j3 = (joueur + e) % 10
                            if _bac_tire_banque(banque, e):
                                for f, pf in piger(47):
                                    regler(j3, (banque + f) % 10, poids * pe * pf)
                            else:
                                regler(j3, banque, poids * pe)
                    elif banque <= 5:
                        for e, pe in piger(48):
                            regler(joueur, (banque + e) % 10, poids * pe)
                    else:
                        regler(joueur, banque, poids)
    return retours


# --- Les retours ------------------------------------------------------------------------------------------

#: Le retour AFFICHÉ, en pour cent, par table et par pari quand ils diffèrent. ⚠️ Calculé (la roulette, le sic
#: bo) ou MESURÉ sur deux cent mille coups (le reste) — `test_tables_de_jeu.py` tient chaque chiffre à ce qu'on
#: mesure, et chacun sous cent.
RETOURS: dict[str, dict[str, int]] = {
    "blackjack": {"main": 97},
    "roulette": {"chance": 97, "numero": 97},
    "poker": {"main": 98},
    "sic_bo": {"petit": 97, "grand": 97, "chiffre": 92},
    "baccara": {"joueur": 98, "banque": 98, "egalite": 84},
}


def pour_le_navigateur() -> dict:
    """⚠️ Le paquet des définitions est au bord de son plafond : les règles voyagent en chiffres, et le
    navigateur tient le jumeau de chaque fonction (un juge les compare, coup pour coup)."""
    return {"mises": list(MISES), "par_jour": COUPS_PAR_JOUR, "noms": JEUX, "retours": RETOURS,
            "roue": list(ROUE), "naturel": NATUREL, "croupier": CROUPIER_RESTE, "plein": NUMERO_PLEIN,
            "dame": DAME, "bonus": BONUS_POKER, "egalite": EGALITE, "six": BANQUE_SIX}
