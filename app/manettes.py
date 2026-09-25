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


#: La PIECE du dessin de chaque bouton de droite (voir `hud.js`,
#: `MANETTE_PIECES`) : c'est elle qui porte la lettre imprimee. Le A d'une
#: manette Xbox est EN BAS, quel que soit le numero que le navigateur lui donne.
POSITIONS_DES_FACES = {"action": "bas", "esquive": "droite", "attaque": "gauche", "arme": "haut"}


class Profil(TypedDict):
    slug: str
    nom: str
    detail: str
    boutons: dict[str, list[int]]
    #: Pour chaque action, la piece du dessin de chacun de ses boutons, dans
    #: l'ordre de `boutons` (`None` : un numero qui n'est nulle part sur le dessin).
    pieces: dict[str, list[str | None]]
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
    `croix_boutons` dit si la croix est quatre boutons ou un chapeau.

    ⚠️ VISER UNE CIBLE (`verrouiller`) n'est dans aucune disposition : c'est la
    gachette de droite, celle du GAZ, a pied (`entree.js`, `gachetteVise`). Demande
    de Martin, 22 sept. 2026 — sur `bt_dinput` c'etait le bouton 2, un numero que
    DirectInput saute et que rien sur la manette ne porte."""
    boutons: dict[str, list[int]] = {
        "action": [faces["action"]],
        "esquive": [faces["esquive"]],
        # ⚠️ Le bouton de droite sert AUSSI de RETOUR dans les menus : sans lui,
        # on ouvre un comptoir a la manette et on n'en sort plus.
        "annuler": [faces["esquive"]],
        # ⚠️ L'epaule de droite etait le deuxieme bouton de FRAPPE : elle est a
        # SAISIR depuis les projections (docs/jalons/les-techniques-d-arts-martiaux.md).
        "attaque": [faces["attaque"]],
        "saisir": [epaules[1]],
        "arme": [faces["arme"], epaules[0]],
        "carte": [meta[0]],
        "pause": [meta[1]],
        "muet": [],
        "haut": [12] if croix_boutons else [],
        "bas": [13] if croix_boutons else [],
        "gauche": [14] if croix_boutons else [],
        "droite": [15] if croix_boutons else [],
    }
    pos = POSITIONS_DES_FACES
    pieces: dict[str, list[str | None]] = {
        "action": [pos["action"]],
        "esquive": [pos["esquive"]],
        "annuler": [pos["esquive"]],
        "attaque": [pos["attaque"]],
        "saisir": ["epaule_d"],
        "arme": [pos["arme"], "epaule_g"],
        "carte": ["select"],
        "pause": ["start"],
        "muet": [],
        "haut": ["croix"] if croix_boutons else [],
        "bas": ["croix"] if croix_boutons else [],
        "gauche": ["croix"] if croix_boutons else [],
        "droite": ["croix"] if croix_boutons else [],
    }
    return Profil(slug=slug, nom=nom, detail=detail, boutons=boutons, pieces=pieces,
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


# --- L'ecran COMMANDES : ce que chaque bouton fait, et la lettre qu'il porte -----------

#: Les LETTRES imprimees sur la manette, par piece du dessin. Trois familles ;
#: la meme piece (le bouton du bas) est un A vert chez Xbox, une croix bleue chez
#: PlayStation, un B chez Nintendo. `forme` : un symbole que la police pixel
#: n'a pas, et que `hud.js` dessine (`FORMES_DE_BOUTON`).
#:
#: ⚠️ Une PlayStation se reconnait a son fabricant (`DETECTION`) ; une Nintendo,
#: NON : la 8BitDo de Martin en Bluetooth se presente parfois en « Pro
#: Controller » de Nintendo, et porte pourtant les lettres Xbox — lui montrer un
#: B la ou son pouce lit un A, c'est mentir. Nintendo se choisit a la main
#: (OPTIONS > MANETTE > LETTRES), comme toute famille que l'on devine mal.
def _lettre(texte: str, couleur: str) -> dict:
    return {"texte": texte, "couleur": couleur}


def _forme(forme: str, couleur: str) -> dict:
    return {"forme": forme, "couleur": couleur}


_GRIS = "#cdc6e6"

FAMILLES: dict[str, dict] = {
    "xbox": {
        "nom": "XBOX",
        "boutons": {
            "bas": _lettre("A", "#5fb84a"), "droite": _lettre("B", "#d9463b"),
            "gauche": _lettre("X", "#3f7fd6"), "haut": _lettre("Y", "#e8c23c"),
            "epaule_g": _lettre("LB", _GRIS), "epaule_d": _lettre("RB", _GRIS),
            "gachette_g": _lettre("LT", _GRIS), "gachette_d": _lettre("RT", _GRIS),
            "select": _lettre("SELECT", _GRIS), "start": _lettre("START", _GRIS),
            "stick": _lettre("LS", _GRIS), "clic": _lettre("CLIC LS", _GRIS),
        },
    },
    "playstation": {
        "nom": "PLAYSTATION",
        "boutons": {
            "bas": _forme("croix", "#7ea6e0"), "droite": _forme("rond", "#e06a64"),
            "gauche": _forme("carre", "#d690c8"), "haut": _forme("triangle", "#43bfa0"),
            "epaule_g": _lettre("L1", _GRIS), "epaule_d": _lettre("R1", _GRIS),
            "gachette_g": _lettre("L2", _GRIS), "gachette_d": _lettre("R2", _GRIS),
            "select": _lettre("SHARE", _GRIS), "start": _lettre("OPTIONS", _GRIS),
            "stick": _lettre("L", _GRIS), "clic": _lettre("L3", _GRIS),
        },
    },
    "nintendo": {
        "nom": "NINTENDO",
        "boutons": {
            "bas": _lettre("B", _GRIS), "droite": _lettre("A", _GRIS),
            "gauche": _lettre("Y", _GRIS), "haut": _lettre("X", _GRIS),
            "epaule_g": _lettre("L", _GRIS), "epaule_d": _lettre("R", _GRIS),
            "gachette_g": _lettre("ZL", _GRIS), "gachette_d": _lettre("ZR", _GRIS),
            "select": _lettre("-", _GRIS), "start": _lettre("+", _GRIS),
            "stick": _lettre("LS", _GRIS), "clic": _lettre("CLIC LS", _GRIS),
        },
    },
}
#: Les formes que `hud.js` sait dessiner.
FORMES = ("croix", "rond", "carre", "triangle")
#: Sans rien de mieux : les lettres Xbox, celles de la plupart des manettes.
FAMILLE_DEFAUT = "xbox"
#: `id` de la manette (insensible a la casse) -> famille. 054c : Sony.
#: « Wireless Controller » AU DEBUT du nom : une DualShock 4 en Bluetooth.
#: ⚠️ Ancre : la manette Xbox s'appelle « Xbox Wireless Controller », et elle
#: se lisait PlayStation — vu a la capture, une croix bleue sous un A.
DETECTION = [
    {"famille": "playstation", "motif": r"054c|sony|playstation|dualsense|dualshock|^wireless controller"},
]

#: Les deux pages de l'ecran COMMANDES. `c` : une action d'`entree.js`
#: (`MAP_TOUCHES`), ou l'un des gestes composes de `GESTES` — marcher, tourner,
#: le gaz et le frein ne sont pas un bouton mais un stick, une gachette, ou
#: plusieurs touches. Chaque appareil (manette, clavier, doigt) montre la ligne
#: avec SON bouton ; une ligne qu'un appareil ne sait pas faire ne s'y montre
#: pas (le son se coupe au clavier, a M, et nulle part a la manette).
#:
#: ⚠️ Un libelle tient en 20 caracteres : il partage l'ecran avec le dessin.
GESTES = ("marcher", "tourner", "gaz", "frein")
PAGES_COMMANDES = [
    {"slug": "pied", "titre": "À PIED", "lignes": [
        {"c": "marcher", "texte": "MARCHER"},
        {"c": "action", "texte": "ENTRER · PARLER"},
        {"c": "attaque", "texte": "FRAPPER · TIRER"},
        {"c": "saisir", "texte": "SAISIR · PROJETER"},
        {"c": "esquive", "texte": "SPRINT"},
        {"c": "arme", "texte": "ARME · TENU : ROUE"},
        {"c": "verrouiller", "texte": "VISER UNE CIBLE"},
        {"c": "carte", "texte": "CARTE"},
        {"c": "pause", "texte": "PAUSE"},
        {"c": "muet", "texte": "SON"},
    ]},
    {"slug": "volant", "titre": "AU VOLANT", "lignes": [
        {"c": "gaz", "texte": "GAZ"},
        {"c": "frein", "texte": "FREIN · RECUL"},
        {"c": "tourner", "texte": "TOURNER"},
        {"c": "esquive", "texte": "FREIN À MAIN"},
        {"c": "attaque", "texte": "KLAXON · SIRÈNE"},
        {"c": "action", "texte": "SORTIR"},
        {"c": "arme", "texte": "RADIO"},
        {"c": "carte", "texte": "CARTE"},
        {"c": "pause", "texte": "PAUSE"},
    ]},
]
LIBELLE_MAX = 20


def exporter() -> dict:
    return {"profils": PROFILS, "defaut": DEFAUT, "chapeau_axe": CHAPEAU_AXE,
            "familles": FAMILLES, "famille_defaut": FAMILLE_DEFAUT, "detection": DETECTION,
            "formes": list(FORMES), "gestes": list(GESTES), "pages": PAGES_COMMANDES}
