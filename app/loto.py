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


def pour_le_navigateur() -> dict:
    return {"prix": PRIX, "billets_par_jour": BILLETS_PAR_JOUR, "numeros": NUMEROS, "boules": BOULES,
            "lots": {str(bons): lot for bons, lot in LOTS.items()}}
