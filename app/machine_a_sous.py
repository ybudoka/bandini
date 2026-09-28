"""La machine à sous du Dragon d'or — trois rouleaux, un bras, et la maison qui gagne
(docs/jalons/le-casino-du-petit-canton.md, vague 1).

Python dit les règles (la mise, les rouleaux, la table des gains, la limite du jour) ; `static/js/casino.js`
tire le bras. Le modèle est celui du vidéopoker (`videopoker.py`) : la maison gagne, et le dit.

⚠️ **LE RETOUR EST CALCULÉ, PAS MESURÉ.** Trois rouleaux de vingt cases, c'est 8 000 arrêts possibles, tous
également probables : `retour_exact` les passe tous, et le chiffre affiché (`RETOUR_AFFICHE`) est le sien,
arrondi. Un juge refait le compte, et un autre tire cent mille coups en JS pour voir que le navigateur paie
comme Python le dit.

⚠️ **SOUS CENT POUR CENT, TOUJOURS** — la règle du vidéopoker : un jeu d'argent qui paierait plus qu'un
boulot casserait l'économie. On peut gagner gros un soir (le triple dragon paie quatre cents fois la mise),
jamais s'enrichir à la longue. La triche viendra à la vague 3 — et pas à cette machine-ci.
"""

from __future__ import annotations

from itertools import product

#: Ce que coûte un tour, en dollars.
MISE = 2

#: Combien de tours par jour de jeu, par partie : la machine finit par « avoir assez mangé ».
TOURS_PAR_JOUR = 80

#: Les symboles, du plus commun au plus rare, et leur nom à l'écran.
SYMBOLES: tuple[dict, ...] = (
    {"slug": "cerise", "nom": "CERISE"},
    {"slug": "citron", "nom": "CITRON"},
    {"slug": "prune", "nom": "PRUNE"},
    {"slug": "cloche", "nom": "CLOCHE"},
    {"slug": "bar", "nom": "BAR"},
    {"slug": "sept", "nom": "SEPT"},
    {"slug": "dragon", "nom": "DRAGON"},
)

#: Combien de cases de chaque symbole sur un rouleau de vingt (le même compte pour les trois).
COMPTE = {"cerise": 5, "citron": 4, "prune": 4, "cloche": 3, "bar": 2, "sept": 1, "dragon": 1}


def _rouleau(decalage: int) -> tuple[str, ...]:
    """Un rouleau de vingt cases : les symboles répartis, puis tournés de `decalage` — les trois rouleaux
    ont la même composition, pas le même ordre (on ne voit pas trois fois la même bande défiler)."""
    cases = [s for s in ("cerise", "citron", "cerise", "prune", "cloche", "cerise", "citron", "bar",
                         "prune", "cerise", "sept", "citron", "prune", "cloche", "cerise", "dragon",
                         "citron", "prune", "cloche", "bar")]
    return tuple(cases[decalage:] + cases[:decalage])


ROULEAUX: tuple[tuple[str, ...], ...] = (_rouleau(0), _rouleau(7), _rouleau(13))
#: L'index de chaque symbole : c'est lui qui voyage (`pour_le_navigateur`).
INDEX = {s["slug"]: i for i, s in enumerate(SYMBOLES)}

#: La table des gains, en multiples de la mise, de la plus grosse à la plus petite. `trois` : trois fois ce
#: symbole ; `cerises` : ce nombre exact de cerises n'importe où ; `premiere_cerise` : une cerise au premier
#: rouleau, et seulement là.
GAINS: tuple[dict, ...] = (
    {"slug": "trois_dragons", "nom": "TROIS DRAGONS", "trois": "dragon", "paie": 400},
    {"slug": "trois_sept", "nom": "TROIS SEPT", "trois": "sept", "paie": 100},
    {"slug": "trois_bar", "nom": "TROIS BAR", "trois": "bar", "paie": 40},
    {"slug": "trois_cloches", "nom": "TROIS CLOCHES", "trois": "cloche", "paie": 20},
    {"slug": "trois_prunes", "nom": "TROIS PRUNES", "trois": "prune", "paie": 10},
    {"slug": "trois_cerises", "nom": "TROIS CERISES", "trois": "cerise", "paie": 10},
    {"slug": "trois_citrons", "nom": "TROIS CITRONS", "trois": "citron", "paie": 8},
    {"slug": "deux_cerises", "nom": "DEUX CERISES", "cerises": 2, "paie": 2},
    {"slug": "premiere_cerise", "nom": "UNE CERISE", "premiere_cerise": True, "paie": 1},
)


def evaluer(arret: tuple[str, str, str]) -> str | None:
    """Le gain (un slug de `GAINS`) de ces trois symboles, ou None. ⚠️ Le jumeau de
    `Casino.evaluerRouleaux` en JS ; un juge les compare sur les 8 000 arrêts."""
    for g in GAINS:
        if g.get("trois") and arret[0] == arret[1] == arret[2] == g["trois"]:
            return g["slug"]
    cerises = sum(1 for s in arret if s == "cerise")
    if cerises == 2:
        return "deux_cerises"
    if cerises == 1 and arret[0] == "cerise":
        return "premiere_cerise"
    return None


def paie(arret: tuple[str, str, str]) -> int:
    """Ce que rend cet arrêt, en multiples de la mise (0 : la mise est perdue)."""
    slug = evaluer(arret)
    return next((g["paie"] for g in GAINS if g["slug"] == slug), 0)


def retour_exact() -> float:
    """Ce que la machine rend, en moyenne, par dollar misé : les 8 000 arrêts, tous également probables."""
    total = sum(paie(arret) for arret in product(*ROULEAUX))
    return total / (len(ROULEAUX[0]) ** 3)


#: Le retour affiché sur la machine, en pour cent — celui de `retour_exact`, arrondi. Un juge le recalcule.
RETOUR_AFFICHE = 89


def pour_le_navigateur() -> dict:
    return {"mise": MISE, "tours_par_jour": TOURS_PAR_JOUR, "retour": RETOUR_AFFICHE,
            # ⚠️ LES ROULEAUX EN CHIFFRES (l'index du symbole) : en mots, soixante slugs répétés faisaient
            # déborder le paquet des définitions de 190 octets gzip (`test_definitions`).
            "symboles": [s["slug"] for s in SYMBOLES],
            "rouleaux": ["".join(str(INDEX[s]) for s in r) for r in ROULEAUX],
            "gains": [dict(g) for g in GAINS]}
