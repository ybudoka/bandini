"""Les dispositions de manette — et pourquoi il en faut plusieurs.

⚠️ Le probleme, en une phrase : **les numeros de boutons d'une manette ne
veulent rien dire tant que le navigateur ne la reconnait pas**. Une manette
reconnue (`mapping: "standard"`, W3C) numerote toujours pareil : 0 le bouton du
bas, 1 celui de droite, 12-15 la croix. Une manette qu'il ne reconnait pas —
la plupart des Bluetooth, dont les 8BitDo — numerote comme elle veut, et la
meme manette n'a pas les memes numeros sur le telephone et sur le Mac.

On ne peut donc pas deviner. On propose : quelques dispositions connues, et un
DESSIN de manette qui sert de preuve — le joueur appuie, le bouton s'allume sur
le dessin. S'il s'allume au bon endroit, c'est la bonne. Sinon, il en essaie une
autre, ou il reapprend bouton par bouton (`Entree.apprendre`).

Deux differences comptent vraiment entre ces dispositions :

1. **La croix.** Quatre boutons (12-15) sur une manette reconnue ; **un seul
   axe a huit positions** (« chapeau ») sur beaucoup de Bluetooth. Dans ce
   deuxieme cas on appuie sur la croix et AUCUN numero ne s'allume : elle a
   l'air morte. Il suffit de donner HAUT et DROITE, le reste du tour se deduit
   (`Entree.lireCroix`).
2. **L'ordre des quatre boutons de droite.** Deux familles : « standard »
   (0 bas, 1 droite, 2 gauche, 3 haut) et « HID » (0 gauche, 1 bas, 2 droite,
   3 haut), celle des vieilles manettes DirectInput.

Les valeurs du chapeau sont celles de Chrome : huit positions regulierement
espacees a partir de -1 (haut), par pas de 2/7, dans le sens des aiguilles
d'une montre ; le repos tombe hors de l'anneau.
"""

from __future__ import annotations

from typing import TypedDict

#: Le tour d'un chapeau, en huit positions. Seuls HAUT et DROITE sont servis :
#: le navigateur deduit le reste, et ne se trompe pas de diagonale.
HAUT = -1.0
PAS_CHAPEAU = 2 / 7
CHAPEAU_AXE = 9

#: Les quatre boutons de droite, par POSITION (c'est ce que le dessin montre) :
#: `action` en bas, `esquive` a droite, `attaque` a gauche, `arme` en haut.
FACES_STANDARD = {"action": 0, "esquive": 1, "attaque": 2, "arme": 3}
#: ⚠️ La numerotation DirectInput saute des numeros : les quatre boutons de
#: droite sont 0, 1, 3 et 4 (2 et 5 ne servent a rien), les epaules 6 et 7, les
#: GACHETTES 8 et 9, et SELECT/START seulement 10 et 11. C'est Martin qui l'a
#: mesure en jeu, le 13 sept. 2026 : ses gachettes ouvraient la carte et la
#: pause — donc ses gachettes sont les boutons 8 et 9, et tout le reste suit.
FACES_DINPUT = {"action": 0, "esquive": 1, "attaque": 3, "arme": 4}


class Profil(TypedDict):
    slug: str
    nom: str
    detail: str
    boutons: dict[str, list[int]]
    axes: list[int]
    gaz: dict
    frein: dict
    croix: dict | None


def _chapeau() -> dict:
    return {"i": CHAPEAU_AXE,
            "valeurs": {"haut": HAUT, "droite": HAUT + 2 * PAS_CHAPEAU}}


def _profil(slug, nom, detail, *, faces, croix_boutons=True, epaules=(4, 5),
            gachettes=(6, 7), meta=(8, 9), axes=(0, 1)) -> Profil:
    """Une disposition. `faces` donne les quatre boutons de droite par position ;
    `croix_boutons` dit si la croix est quatre boutons ou un chapeau."""
    boutons: dict[str, list[int]] = {
        "action": [faces["action"]],
        "esquive": [faces["esquive"]],
        # ⚠️ Le bouton de droite sert AUSSI de RETOUR dans les menus : sans lui,
        # on ouvre un comptoir a la manette et on n'en sort plus.
        "annuler": [faces["esquive"]],
        "attaque": [faces["attaque"], epaules[1]],
        "arme": [faces["arme"], epaules[0]],
        "carte": [meta[0]],
        "pause": [meta[1]],
        "muet": [],
        "haut": [12] if croix_boutons else [],
        "bas": [13] if croix_boutons else [],
        "gauche": [14] if croix_boutons else [],
        "droite": [15] if croix_boutons else [],
    }
    return Profil(slug=slug, nom=nom, detail=detail, boutons=boutons,
                  axes=list(axes),
                  gaz={"type": "bouton", "i": gachettes[1]},
                  frein={"type": "bouton", "i": gachettes[0]},
                  croix=None if croix_boutons else _chapeau())


PROFILS: list[Profil] = [
    _profil("standard", "XBOX, PLAYSTATION", "LE NAVIGATEUR LA RECONNAÎT",
            faces=FACES_STANDARD),
    _profil("bt_dinput", "8BITDO EN BLUETOOTH", "GÂCHETTES 8 ET 9, CROIX SUR UN AXE",
            faces=FACES_DINPUT, croix_boutons=False,
            epaules=(6, 7), gachettes=(8, 9), meta=(10, 11)),
    _profil("bt_croix_axe", "BLUETOOTH — CROIX SUR UN AXE", "NUMÉROS STANDARDS, CROIX À PART",
            faces=FACES_STANDARD, croix_boutons=False),
]

#: Le slug de la disposition servie par defaut : celle d'une manette reconnue.
DEFAUT = "standard"


def par_slug(slug: str) -> Profil | None:
    for profil in PROFILS:
        if profil["slug"] == slug:
            return profil
    return None


def exporter() -> dict:
    return {"profils": PROFILS, "defaut": DEFAUT, "chapeau_axe": CHAPEAU_AXE}
