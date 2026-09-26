"""Le vidéopoker du Brouillard — une machine qui clignote au fond du bar et du dépanneur, et qui
mange ton argent comme les vraies (docs/jalons/le-videopoker-du-brouillard.md).

Python dit les règles (la mise, la table des gains, la limite du jour) ; `static/js/missions.js`
joue la main. Le poker est le plus simple qui soit : cinq cartes, on garde ce qu'on veut, on retire
le reste une fois, et la main paie selon la table — « valets ou mieux », celle des bars du Québec.

⚠️ **LA MAISON GAGNE, ET LE DIT.** La table est une 6/5 à une pièce (la main pleine paie 6, la
couleur 5, la quinte flush royale 250) : en moyenne, la machine rend MOINS qu'on y met, et elle
l'écrit en petit (`RETOUR_AFFICHE`). Un jeu d'argent qui paierait plus qu'un boulot casserait
l'économie — même règle que les défis de la foire, qui ne battent jamais un boulot honnête. Le
chiffre affiché est MESURÉ (`tests/test_videopoker.py` joue deux cent mille mains avec la stratégie
d'un habitué), pas promis.

⚠️ **SON HASARD EST À ELLE.** Les cartes se battent avec un générateur à part, semé par la graine de
la partie et le numéro de la main (`static/js/missions.js`, `paquetDuVideopoker`) — jamais `B.rng()`,
qui décalerait tout le hasard du jeu (règle 8 de `ecrire-drole.md`).
"""

from __future__ import annotations

#: Ce que coûte une main, en dollars.
MISE = 5

#: Combien de mains par jour de jeu, toutes machines comprises. ⚠️ Sans limite, un joueur patient
#: « farme » les gros lots : la moyenne est contre lui, mais une quinte flush royale paie 1 250 $.
MAINS_PAR_JOUR = 40

#: La table des gains, de la meilleure main à la plus petite, en multiples de la MISE, mise
#: comprise (« paie 3 pour 1 » : on récupère trois mises). Une main qui n'y est pas perd la mise.
GAINS: list[dict] = [
    {"slug": "quinte_flush_royale", "nom": "QUINTE FLUSH ROYALE", "paie": 250},
    {"slug": "quinte_flush", "nom": "QUINTE FLUSH", "paie": 50},
    {"slug": "carre", "nom": "CARRÉ", "paie": 25},
    {"slug": "main_pleine", "nom": "MAIN PLEINE", "paie": 6},
    {"slug": "couleur", "nom": "COULEUR", "paie": 5},
    {"slug": "quinte", "nom": "QUINTE", "paie": 4},
    {"slug": "brelan", "nom": "BRELAN", "paie": 3},
    {"slug": "deux_paires", "nom": "DEUX PAIRES", "paie": 2},
    {"slug": "valets", "nom": "VALETS OU MIEUX", "paie": 1},
]

#: Le retour moyen, en pour cent, qu'affiche la machine. Mesuré, arrondi à l'entier inférieur
#: (`test_videopoker.py` le tient à deux points de ce qu'on mesure).
RETOUR_AFFICHE = 93

#: Les cartes : un entier de 0 à 51. `c % 13` est le rang (0 le deux… 9 le valet, 12 l'as),
#: `c // 13` la couleur.
RANGS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "V", "D", "R", "A")
COULEURS = ("pique", "coeur", "carreau", "trefle")
VALET = 9


def evaluer(cartes: list[int]) -> str | None:
    """La main que font ces cinq cartes (un slug de `GAINS`), ou None si elle ne paie pas."""
    rangs = sorted(c % 13 for c in cartes)
    compte: dict[int, int] = {}
    for r in rangs:
        compte[r] = compte.get(r, 0) + 1
    paquets = sorted(compte.values(), reverse=True)
    couleur = len({c // 13 for c in cartes}) == 1
    quinte = len(compte) == 5 and (rangs[4] - rangs[0] == 4 or rangs == [0, 1, 2, 3, 12])
    if quinte and couleur:
        return "quinte_flush_royale" if rangs[0] == 8 else "quinte_flush"
    if paquets[0] == 4:
        return "carre"
    if paquets == [3, 2]:
        return "main_pleine"
    if couleur:
        return "couleur"
    if quinte:
        return "quinte"
    if paquets[0] == 3:
        return "brelan"
    if paquets[:2] == [2, 2]:
        return "deux_paires"
    if paquets[0] == 2 and any(n == 2 and r >= VALET for r, n in compte.items()):
        return "valets"
    return None


def paie(cartes: list[int]) -> int:
    """Ce que rend la main, en multiples de la mise (0 : la mise est perdue)."""
    main = evaluer(cartes)
    return next((g["paie"] for g in GAINS if g["slug"] == main), 0)


def pour_le_navigateur() -> dict:
    return {"mise": MISE, "mains_par_jour": MAINS_PAR_JOUR, "gains": [dict(g) for g in GAINS],
            "retour": RETOUR_AFFICHE, "rangs": list(RANGS)}
