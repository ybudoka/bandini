"""Le 6/49 du dépanneur — un billet à 2 $ chez Ti-Paul, et le lendemain matin, les numéros dans le
Clairon (docs/jalons/le-6-49-du-depanneur.md).

Python dit les règles (le prix, les lots, la limite) ; `static/js/missions.js` vend le billet, fait le
tirage la nuit (`nuitDuLoto`) et le publie sous la manchette du matin.

⚠️ **LES CHANCES SONT LES VRAIES**, donc minuscules : trois bons numéros une fois sur 57, quatre une fois
sur mille, six une fois sur quatorze millions. Presque personne ne gagne, et c'est drôle. Un billet
rend en moyenne moins du cinquième de ce qu'il coûte (`test_loto.py` le calcule exactement) — un jeu
d'argent ne bat jamais un boulot honnête.

⚠️ **LE GROS LOT EST PLAFONNÉ** (`LOTS[6]`) : un million en poche casserait l'économie (`fortune_max`),
et une chance sur quatorze millions n'a pas besoin d'un chiffre plus gros pour faire rêver.

⚠️ **LE TIRAGE NE DÉPEND QUE DU JOUR** : le même jour, les mêmes numéros pour tout le monde, quelle que
soit la partie. Il se calcule — jamais `B.rng()`, qui décalerait tout le hasard du jeu. Les numéros du
billet, eux, se tirent au générateur de la partie et du numéro du billet (pas `B.rng()` non plus).
"""

from __future__ import annotations

from math import comb

#: Le prix d'un billet, en dollars.
PRIX = 2

#: Combien de billets par jour : Ti-Paul n'en vend pas plus à la même personne.
BILLETS_PAR_JOUR = 5

#: Combien de numéros, et parmi combien.
NUMEROS = 6
BOULES = 49

#: Ce que paie un billet selon ses bons numéros (les autres ne paient rien).
LOTS: dict[int, int] = {3: 10, 4: 75, 5: 1500, 6: 25000}


def chance(bons: int) -> float:
    """La probabilité qu'un billet ait exactement `bons` bons numéros."""
    return comb(NUMEROS, bons) * comb(BOULES - NUMEROS, NUMEROS - bons) / comb(BOULES, NUMEROS)


def retour_moyen() -> float:
    """Ce que rend un billet en moyenne, en fraction de son prix."""
    return sum(chance(bons) * lot for bons, lot in LOTS.items()) / PRIX


#: ⚠️ **LE TIRAGE SE DIT** (Martin, 26 sept. 2026 : « 6/49 doit se dire »). Les numéros changent chaque
#: jour : on ne génère pas une phrase par tirage, on fait comme l'annonceur de la loterie — une
#: amorce, les nombres un par un (`narrateur-loto-1` à `-49`), et ce que ton billet a donné. Le
#: navigateur les enchaîne après la manchette (`Missions.direLeLoto`). Le texte écrit, lui, ne change
#: pas : les chiffres sous la une.
DIT = {
    # En toutes lettres : « 6/49 » se lirait « six barre quarante-neuf ».
    "amorce": "Les numéros du six-quarante-neuf.",
    #: Ce que ton meilleur billet a donné : sous trois bons numéros, rien.
    "rien": "Ton billet? Rien. Comme d'habitude.",
    "trois": "Ton billet : trois bons numéros. De quoi payer la poutine.",
    "quatre": "Ton billet : quatre bons numéros! Pas pire pantoute.",
    "cinq": "Cinq bons numéros! Le gagnant est d'ici!",
    "six": "Six sur six! Le gros lot! Le gagnant est d'ici!",
}

#: Le mot de ce que ton billet a donné, selon ses bons numéros.
ISSUES = {0: "rien", 1: "rien", 2: "rien", 3: "trois", 4: "quatre", 5: "cinq", 6: "six"}

_UNITES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze",
           "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
_DIZAINES = {2: "vingt", 3: "trente", 4: "quarante"}


def en_lettres(n: int) -> str:
    """Un nombre de la boule, de 1 à 49, en toutes lettres (« vingt et un », « quarante-neuf »)."""
    if not 1 <= n <= BOULES:
        raise ValueError(n)
    if n < 20:
        return _UNITES[n]
    d, u = divmod(n, 10)
    if u == 0:
        return _DIZAINES[d]
    return _DIZAINES[d] + (" et un" if u == 1 else "-" + _UNITES[u])


def repliques() -> list[dict]:
    """Ce que le narrateur dit du tirage : l'amorce, les 49 boules, les issues. `slug` et `texte`."""
    out = [{"slug": "narrateur-loto-amorce", "texte": DIT["amorce"]}]
    out += [{"slug": f"narrateur-loto-{n}", "texte": en_lettres(n).capitalize() + "."} for n in range(1, BOULES + 1)]
    out += [{"slug": f"narrateur-loto-{cle}", "texte": DIT[cle]} for cle in ("rien", "trois", "quatre", "cinq", "six")]
    return out


def pour_le_navigateur() -> dict:
    return {"prix": PRIX, "billets_par_jour": BILLETS_PAR_JOUR, "numeros": NUMEROS, "boules": BOULES,
            "lots": {str(bons): lot for bons, lot in LOTS.items()},
            "issues": {str(bons): mot for bons, mot in ISSUES.items()}}
