"""Le brouillard de Baie-des-Brumes — la ville porte son nom pour vrai
(docs/jalons/le-brouillard-de-baie-des-brumes.md).

Certains matins, un brouillard roule de la baie : de l'aube à midi, on n'y voit plus à trois coins de
rue, et la police non plus. Plus épais près de l'eau, aux Quais et à La Pointe.

⚠️ **PYTHON RÈGLE, LE NAVIGATEUR EMBRUME** — la même règle que la neige de M12 (`neige.py`,
`static/js/neige.js`). L'intensité est une fonction du JOUR et de l'HEURE (`Brouillard.intensiteA`) :
rien à simuler, aucun dé, et deux joueurs voient le même brouillard le même matin. Un matin a son
brouillard à l'empreinte du jour (`hash2(jour, sel)`), pas au tirage.

⚠️ **DERRIÈRE UNE OPTION**, NON par défaut (« BROUILLARD (ESSAI) »), comme la neige : le voile se peint
sur toute la ville à chaque image, et la dette « rythme mesuré sur le vrai téléphone » demande de le
mesurer avant de l'allumer pour tout le monde (`test_navigateur.py`, la sonde du brouillard). Sans
l'option, l'intensité vaut 0, et 0 ne change rien : la police voit comme avant, rien ne se peint.
"""

from __future__ import annotations

#: Les matins de brouillard : une chance par jour, à l'empreinte du jour ; puis, en heures, l'aube où il
#: monte, le plein, la levée, et midi où il n'en reste rien.
MATINS = {
    "chance": 0.25,
    "sel": 0xB0B1,
    "debut_h": 4.5,
    "plein_h": 6.5,
    "leve_h": 10.0,
    "fin_h": 12.0,
}

#: Ce que fait le brouillard, à son plein.
EFFETS = {
    #: Le voile : à peine au milieu de l'écran, épais aux bords — on voit autour de soi, pas au bout
    #: de la rue. `clair` : la part de la demi-diagonale de l'écran qui reste claire.
    "voile_centre": 0.05,
    "voile_bord": 0.78,
    "clair": 0.30,
    #: La vue de la police et des témoins, en part de leur portée ordinaire.
    "vision": 0.45,
    #: Près de l'eau, il est entier ; ailleurs, il n'en reste que cette part.
    "pres_de_l_eau": ["quais", "pointe"],
    "ailleurs": 0.65,
    #: La corne du phare, toutes les tant de secondes, et jusqu'où on l'entend.
    "corne_s": 22,
    "corne_portee_px": 2400,
}

#: Ce que le Clairon écrit la veille d'un matin de brouillard, sous la manchette.
ANNONCE = "BROUILLARD À COUPER AU COUTEAU DEMAIN MATIN."


def pour_le_navigateur() -> dict:
    return {"matins": dict(MATINS), "effets": {**EFFETS, "pres_de_l_eau": list(EFFETS["pres_de_l_eau"])},
            "annonce": ANNONCE}
