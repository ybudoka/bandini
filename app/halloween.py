"""L'Halloween à Baie-des-Brumes (docs/jalons/les-quatre-saisons-realistes.md, lot 3, 29 sept. 2026).

Tout octobre, des citrouilles sur les perrons, allumées la nuit. Le 31 (jour 33 de l'année du jeu), les
fenêtres prennent des lumières orange et violettes, un passant sur trois sort déguisé, des bandes d'enfants
vont de porte en porte, et une maison des Érables est hantée de 18 h à minuit.

⚠️ **UNE PURE FONCTION DU JOUR ET DE L'HEURE, RIEN DE POSÉ** (la recette des Fêtes, `fetes.py`) : les
citrouilles sont PEINTES à côté des portes des logements (à l'empreinte du logement), les lumières sont la
COULEUR des lampes qui existent, les costumes se tirent à l'empreinte du passant. La ville ne bouge pas
d'un octet ; la maison hantée est un logement qu'on visite déjà.
"""

from __future__ import annotations

from . import calendrier

#: Le 31 octobre, dans l'année du jeu.
JOUR = calendrier.DATES["halloween"]

#: Les citrouilles d'octobre : un logement sur `part` en a une sur son perron, à l'empreinte du logement.
#: La nuit, elles s'allument : leur lueur (couleur, rayon en px, opacité).
CITROUILLES = {"part": 0.33, "sel": 0xC17E, "lueur": [255, 150, 40], "rayon": 26, "force": 0.55}

#: Le soir du 31, les fenêtres et les vitrines prennent ces couleurs, dès `des_h`.
LUMIERES = {"couleurs": [[255, 140, 30], [150, 70, 210]], "force": 0.45, "sortes": ["fenetre", "vitrine"],
            "des_h": 16.0}

#: Les déguisés du 31, dès `des_h` : un passant sur `part`, à l'empreinte du passant.
DEGUISES = {"part": 0.33, "sel": 0xDE61, "des_h": 16.0,
            "costumes": ["sorciere", "fantome", "squelette", "citrouille"]}

#: Les enfants qui passent l'Halloween : des bandes de 2 ou 3, jamais plus de `bandes_max` à la fois, entre
#: `des_h` et `jusqu_h`, dans les quartiers de maisons ; ce qu'ils disent à une porte qui a sa citrouille.
ENFANTS = {"bandes_max": 4, "taille": [2, 3], "des_h": 17.0, "jusqu_h": 21.5, "sel": 0xE7FA,
           "districts": ["erables", "pointe", "faubourg"],
           "mots": ["DES BONBONS!", "DES BONBONS OU UN SORT!", "HALLOWEEN!", "BOUH!"]}

#: La maison hantée : un logement des Érables, de `des_h` à `jusqu_h` le 31. Dedans, les lumières
#: s'éteignent une toutes les `lumiere_s` secondes, le fantôme s'évanouit quand on l'approche à
#: `fantome_px`, et le sac de bonbons au fond vaut `prime`, une fois par année.
MAISON = {"district": "erables", "des_h": 18.0, "jusqu_h": 24.0, "lumiere_s": 3, "lumieres": 4,
          "fantome_px": 36, "fantome_revient_s": 2, "prime": 150}

#: LA VOIX DE LA MAISON : générée pour elle, et à elle seule (`audio.VOIX_RESERVEES`). Une voix
#: française de savant fou — ce qui hante la maison n'est pas d'ici, et ça s'entend.
VOIX = "Dr. Von Fusion - VF"

#: Ce que chuchote la maison, et quand (`halloween.js`) : `entree` (on entre), `lumiere` (la deuxième
#: s'éteint), `fantome` (il s'est évanoui), `sac` (on le trouve), `bonbons` (on le prend). Drôle d'abord,
#: jamais gore. Le texte s'affiche ; le `jeu` (balises eleven_v3) reste ici, jamais dans le paquet.
MURMURES: tuple[dict, ...] = (
    {"cle": "entree", "texte": "Qui vient nous voir un soir pareil?",
     "jeu": "[whispers] Qui vient nous voir… [mysteriously] un soir pareil?"},
    {"cle": "lumiere", "texte": "L'électricité, ça fait cinquante ans qu'on la paie plus.",
     "jeu": "[whispers] L'électricité… [mysteriously] ça fait cinquante ans qu'on la paie plus."},
    {"cle": "fantome", "texte": "Bouh! T'as eu peur, hein?",
     "jeu": "[mischievously] Bouh! [laughs] T'as eu peur, hein?"},
    {"cle": "sac", "texte": "Prends-en un. Un seul. On compte.",
     "jeu": "[whispers] Prends-en un. [quietly] Un seul. [mysteriously] On compte."},
    {"cle": "bonbons", "texte": "Un sac de bonbons, et cent cinquante piastres au fond. Reviens l'an prochain.",
     "jeu": "[warmly] Un sac de bonbons… et cent cinquante piastres au fond. [whispers] Reviens l'an prochain."},
)

#: Ce que dit le Clairon la veille.
CLAIRON = "C'EST L'HALLOWEEN DEMAIN SOIR : ATTENTION AUX PETITS MONSTRES."


def pour_le_navigateur() -> dict:
    return {"jour": JOUR,
            "citrouilles": {**CITROUILLES, "lueur": list(CITROUILLES["lueur"])},
            "lumieres": {**LUMIERES, "couleurs": [list(c) for c in LUMIERES["couleurs"]],
                         "sortes": list(LUMIERES["sortes"])},
            "deguises": {**DEGUISES, "costumes": list(DEGUISES["costumes"])},
            "enfants": {**ENFANTS, "taille": list(ENFANTS["taille"]), "districts": list(ENFANTS["districts"]),
                        "mots": list(ENFANTS["mots"])},
            "maison": dict(MAISON), "murmures": {m["cle"]: m["texte"] for m in MURMURES}, "clairon": CLAIRON}
