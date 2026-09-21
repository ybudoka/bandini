"""La nuit a ses habitudes (P2) : ce que la nuit change, en une table.

Demande de Martin (21 sept. 2026) : « la nuit, personne ne se baigne, plus de
véhicules stationnés, et donne-moi d'autres idées pour la nuit » — puis « je veux
toutes les idées ». Les deux demandes vivent là où vit ce qu'elles règlent
(`pietons.PLAGE["heures"]`, `vehicules.TRAFIC["garer_la_nuit"]`) ; ce module
porte le reste.

⚠️ **Python décide, le navigateur joue**, et **rien ici ne tire un dé** : quelle
fenêtre s'éteint, quel lampadaire grésille, se lit à l'empreinte de sa position
(`carte.empreinte_de_tuile`, le `hash2` de base.js). La ville ne bouge pas d'une
tuile.

Les heures sont sur 24 h ramenées à 0..1, comme partout (`B.partie.heure`) ; la
nuit qu'on voit va de 19 h 53 (0,828) à 6 h 24 (0,267) — `Monde.estNuit`.
"""

from __future__ import annotations

#: **LES FENÊTRES S'ÉTEIGNENT UNE À UNE.** Une fenêtre de logement sur trois
#: s'allume à la brunante depuis les résidences (`carte.py`) — et restait allumée
#: jusqu'au matin, toutes ensemble. Chacune a maintenant son COUCHER, tiré à
#: l'empreinte de sa tuile entre 22 h et 3 h, et son LEVER entre 5 h et 6 h 15 :
#: une rue qui se vide de ses lumières à mesure que la nuit avance, puis quelques
#: cuisines qui se rallument avant le jour.
FENETRES: dict = {
    "coucher": (22 / 24, 27 / 24),   # peut passer minuit : 27 h = 3 h du matin
    "lever": (5 / 24, 6.25 / 24),   # avant le jour (6 h 24) : on allume pour y voir
}

#: **LES LAMPADAIRES QUI GRÉSILLENT** (en quartier pauvre). Un sur trois y est
#: déjà mort (`mobilier.PART_EN_PANNE`) ; parmi ceux qui marchent encore, une part
#: grésille. Une ampoule qui grésille vit par SALVES : la plupart du temps elle
#: tient, puis elle hoquette une seconde. Tout se lit à l'empreinte de la lampe et
#: de l'instant (`B.t`) — jamais au dé du jeu.
LAMPADAIRES: dict = {
    "part_qui_gresille": 0.2,     # des lampadaires pauvres qui marchent encore
    "salve_images": 150,          # une fenêtre de temps de 2,5 s…
    "part_des_salves": 0.4,       # …qui, quatre fois sur dix, hoquette
    "clignote_images": 4,         # un hoquet dure quatre images
    "part_eteinte": 0.55,         # et pendant la salve, l'ampoule est noire plus d'une fois sur deux
}


#: **LE LAST CALL.** Au Québec, les bars ferment à 3 h. Une grappe de fêtards sort
#: alors de chaque bar de la bulle — une fois par bar et par nuit — et prend la rue :
#: ils chantent, ils zigzaguent (ce sont des ivrognes, `pietons.py`, avec leur
#: routine), et celui qu'on frôle cherche la chicane. Les bars sont les devantures
#: de la famille « nuit » (tavernes, bingo, vidéo poker, disco, hôtels), sauf celles
#: À LOUER : `bars(ville)` les lit dans la ville finie.
#:
#: ⚠️ `jusqu_a` : un bar qu'on n'approche qu'à 3 h 40 se vide encore — mais à 4 h, la
#: rue est retombée. Et ⚠️ le NOMBRE se lit à l'empreinte du jour et du bar, jamais au
#: dé : deux joueurs voient sortir la même grappe du même bar.
LAST_CALL: dict = {
    "heure": 3 / 24,
    "jusqu_a": 3.75 / 24,
    "fetards": (3, 5),
    "portee_px": 460,            # le bar doit être dans la bulle (520) : on les voit vivre
    # Des airs à boire du folklore — domaine public, et tout le monde les connaît.
    "chansons": [
        "PRENDRE UN P’TIT COUP C’EST AGRÉABLE",
        "ALOUETTE, GENTILLE ALOUETTE",
        "C’EST À BOIRE QU’IL NOUS FAUT",
        "À LA CLAIRE FONTAINE",
        "UN AUTRE, UN AUTRE!",
    ],
    "chante": 0.3,               # la chance, par battement d'ivrogne, d'entonner
    # La chicane : on le frôle, il se retourne. Une fois par fêtard.
    "chicane": {
        "portee_px": 30,
        "part": 0.35,            # la part de ceux qui passent aux poings
        "mots": ["TU ME CHERCHES-TU?", "VIENS-T’EN DEHORS!", "R’GARDE-MOÉ DANS LES YEUX"],
    },
}

#: **LE CAMELOT DU CLAIRON** (`pietons.py` : son corps et ses heures, 4 h 34 à 6 h 22).
#: Il lance le journal sur le perron ; le journal y reste jusqu'à ce qu'on le rentre.
CAMELOT: dict = {
    "rentre_a": 9 / 24,          # on a rentré le journal : il disparaît (hors champ)
    "parle": 0.25,               # la chance, par perron, de lancer son « LE CLAIRON! »
}


def bars(ville: dict) -> list[dict]:
    """Où sort le last call : la porte de chaque devanture de la famille « nuit »,
    et la tuile de trottoir juste devant. Sans un dé, dans l'ordre de la ville."""
    from . import devantures

    nuit = devantures.genre_index("nuit")
    sortie = []
    for d in ville.get("devantures", []):
        if d["genre"] != nuit or d["texte"] == devantures.A_LOUER:
            continue
        portes = [i for i, m in enumerate(d["motifs"]) if m in "DdP"]
        if not portes:
            continue
        x = d["x"] + portes[0]
        sortie.append({"x": x, "y": d["y"] + 1, "porte": [x, d["y"]], "nom": d["texte"]})
    return sortie


def exporter(ville: dict | None = None) -> dict:
    return {
        "fenetres": {cle: list(v) for cle, v in FENETRES.items()},
        "lampadaires": dict(LAMPADAIRES),
        "last_call": {**LAST_CALL, "fetards": list(LAST_CALL["fetards"]),
                      "bars": bars(ville) if ville else []},
        "camelot": dict(CAMELOT),
    }
