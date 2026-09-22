"""Ce que ACTION fait devant le décor et devant ceux qui travaillent dans la rue (P4).

Sept gestes, et aucun n'est un menu : on regarde la chose (`faceA`, comme pour
tout le reste) et on appuie.

- **s'asseoir** sur un banc : le souffle revient, les forces un peu, la première
  poussée du stick nous relève ;
- **fouiller** une poubelle, une benne, un bac : quelques sous, une canette, un
  reste — ou un rat. Une fois par jour et par bac, et le quartier compte ;
- **boire** à la fontaine de la place ;
- **manger au barbecue** (deuxième vague, 22 sept. 2026) — un décor déjà posé
  devant les maisons de banlieue, jamais encore servi : quelques PV et un peu
  de souffle, une fois par jour et par barbecue, toujours sous le hot-dog acheté ;
- **ouvrir la borne-fontaine** : la gerbe que la ville connaît déjà quand un char
  défonce une borne, mais à la main — on s'y rafraîchit ;
- **un pourboire** à l'artiste de rue : la pièce change vraiment de poche ;
- **la photo du touriste** : il nous tend son appareil, il paie de sa poche.

⚠️ **Python décide, le navigateur joue** : quel décor donne quel geste, ce que
chacun rend, et les mots qu'il dit, sont ici — `static/js/interactions.js` ne
garde aucun nombre. Et **rien ici ne rapporte gros** : le plus gros butin d'un
bac reste sous le dixième de la plus petite prime de mission
(`test_interactions.py`). Ces gestes sont de la ville, pas un métier.
"""

from __future__ import annotations

#: La portée d'un geste sur le décor, en pixels du centre du décor : celle du guichet
#: et de la machine distributrice — une machine et un banc se prennent de la même main.
PORTEE_PX = 22

# --- S'asseoir ------------------------------------------------------------------

ASSEOIR: dict = {
    "invite": "S’ASSEOIR",
    "portee_px": PORTEE_PX,
    # Où le corps se pose, depuis l'ancre du banc (le milieu du bas de la tuile), et
    # de quel côté il regarde. ⚠️ Le banc de face (`banc`) regarde le sud : l'assis
    # est DEVANT le dossier, il se dessine par-dessus. Le banc vu de dos
    # (`banc_nord`) regarde le nord : le dossier est devant l'assis, qui se dessine
    # avant lui (`y` plus petit) pour que la planche lui couvre les jambes. Les deux
    # bancs de profil sont longs (18 px) : l'assis se dessine PAR-DESSUS (`y` plus grand),
    # sinon la planche de l'assise lui coupe le corps en deux.
    "sieges": {
        "banc": {"pose": "assis_bas", "dx": 0, "dy": 2},
        "banc_nord": {"pose": "assis_haut", "dx": 0, "dy": -5},
        "banc_est": {"pose": "assis_droite", "dx": 1, "dy": 1},
        "banc_ouest": {"pose": "assis_gauche", "dx": -1, "dy": 1},
    },
    # ⚠️ Le souffle remonte plus vite assis : deux fois et demie la reprise
    # debout (`endurance_par_image * 0,6` — c'est le facteur de plus, pas le taux).
    "souffle_x": 2.5,
    # Les forces reviennent lentement (une PV toutes les trois secondes), et pas
    # au-delà des trois cinquièmes de la barre : un banc repose, il ne soigne pas —
    # la bouffe et l'hôpital gardent leur raison d'être.
    "pv_images": 180,
    "pv_plafond": 0.6,
    # Ce qui nous empêche de nous asseoir, et ce que l'invite en dit.
    "refus": {
        "police": "PAS AVEC LA POLICE AUX FESSES",
        "saigne": "TU SAIGNES ENCORE",
    },
}

# --- Fouiller -------------------------------------------------------------------

#: Les trouvailles. `argent` = (min, max) ; `pv` et `souffle` se prennent ; un `pv`
#: négatif est une morsure, et elle ne tue jamais (il reste toujours un point).
TROUVAILLES: dict[str, dict] = {
    "rien": {"texte": "RIEN QUE DES ORDURES"},
    "monnaie": {"texte": "DE LA MONNAIE", "argent": (1, 3)},
    "canettes": {"texte": "DES CANETTES CONSIGNÉES", "argent": (2, 4)},
    "reste": {"texte": "UN RESTE DE POUTINE", "pv": 4, "souffle": 6},
    "rat": {"texte": "UN RAT !", "pv": -3},
    # La nuit, c'est lui qui est dans la poubelle (voir `FOUILLER["la_nuit"]`).
    "raton": {"texte": "UN RATON LAVEUR !", "pv": -4},
}

FOUILLER: dict = {
    "invite": "FOUILLER",
    "deja": "DÉJÀ FOUILLÉ",
    "portee_px": PORTEE_PX,
    # Quel décor se fouille, et quelle table il tire. ⚠️ `poubelle_pleine` et les
    # ordures sont ce que le quartier pauvre laisse traîner (`salete.py`) : c'est
    # là qu'il y a quelque chose.
    "decors": {
        "poubelle": "ordinaire",
        "bac": "ordinaire",
        "poubelle_pleine": "pleine",
        "ordures": "pleine",
        "benne": "pleine",
        "bac_recyclage": "recyclage",
    },
    # (poids, trouvaille). Le tirage est UN `B.rng()`, ordonné comme écrit.
    "tables": {
        "ordinaire": ((50, "rien"), (26, "monnaie"), (10, "canettes"), (7, "reste"), (7, "rat")),
        "pleine": ((30, "rien"), (30, "monnaie"), (16, "canettes"), (12, "reste"), (12, "rat")),
        "recyclage": ((35, "rien"), (10, "monnaie"), (55, "canettes")),
    },
    # ⚠️ Le quartier dit la poubelle : ce facteur multiplie le poids de « rien ». Un
    # bac de quartier cossu est presque toujours vide, celui d'un quartier pauvre
    # déborde (`Monde.standingA`). Sans standing (une ruelle hors quartier) : 1.
    "standing": {"cossu": 3.0, "ordinaire": 1.0, "pauvre": 0.6},
    # ⚠️ LA NUIT A SES HABITUDES : la nuit, le rat de la table est un RATON LAVEUR,
    # et il y en a plus (son poids fois `poids`). Le tirage reste UN `B.rng()` : la
    # nuit ne tire pas un de de plus, elle change ce qu'il rend. Et le raton se
    # sauve de la poubelle — on le voit filer (`Entites.fairePartirUnRaton`).
    "la_nuit": {"remplace": "rat", "par": "raton", "poids": 2.0},
    "trouvailles": {slug: dict(t) for slug, t in TROUVAILLES.items()},
}

# --- Boire ----------------------------------------------------------------------

BOIRE: dict = {
    "invite": "BOIRE",
    "encore": "PLUS SOIF",
    "message": "L’EAU EST FRAÎCHE",
    "decors": ("fontaine",),
    # Une fontaine de place est plus grosse qu'un banc : on la touche de plus loin.
    "portee_px": 28,
    "souffle": 40,
    # On ne rebuvait pas dix fois de suite : dix secondes avant d'avoir soif.
    "repit_images": 600,
}

# --- Manger au barbecue -----------------------------------------------------------

#: ⚠️ **AUCUNE PLACE NEUVE À TROUVER** (deuxième vague, 22 sept. 2026) : `bbq` est déjà
#: posé par `carte.py` (devant les maisons de banlieue, `DECOR_SOLIDE`) — c'est pour ça
#: qu'il ouvre la vague, avant le chat (une confiance à écrire) et le buisson (la police
#: à équilibrer). Un reste de poutine ramassé dans une poubelle vaut 4 PV/6 de souffle
#: (`FOUILLER`) ; un repas assis au barbecue en vaut un peu plus — jamais dix, jamais le
#: hot-dog du kiosque (25 PV/40 de souffle, `economie.TARIFS`) : on grignote, on n'achète
#: rien.
BARBECUE: dict = {
    "invite": "MANGER",
    "deja": "DÉJÀ MANGÉ",
    "message": "ÇA SENT BON",
    "decors": ("bbq",),
    "portee_px": PORTEE_PX,
    "pv": 8,
    "souffle": 15,
}

# --- La borne-fontaine -----------------------------------------------------------

BORNE: dict = {
    "invite_ouvrir": "OUVRIR LA BORNE",
    "invite_fermer": "FERMER LA BORNE",
    "decors": ("borne_fontaine",),
    "portee_px": PORTEE_PX,
    # ⚠️ La même gerbe que celle d'une borne défoncée (`Entites.JET_EAU_IMAGES`, dix
    # secondes), mais on la ferme : vingt secondes, et elle se referme seule.
    "duree_images": 1200,
    # Se rafraîchir : à ce rayon de la gerbe, le souffle revient plus vite qu'à
    # l'ordinaire — le facteur de plus, comme pour le banc.
    "rayon_px": 34,
    "souffle_x": 2.0,
}

# --- Le pourboire ---------------------------------------------------------------

POURBOIRE: dict = {
    "invite": "UN POURBOIRE",
    "montant": 1,
    "metiers": ("musicien", "amuseur", "jongleur", "echassier"),
    "portee_px": 26,
    # Ce que l'artiste répond. ⚠️ Le musicien a déjà son mot (`pietons.PAROLES`,
    # « chapeau ») : on ne le redit pas, on le reprend ici avec ceux des autres.
    "merci": {
        "musicien": ("MERCI M’SIEUR-DAME", "ÇA VA À LA GUITARE"),
        "amuseur": ("HA! MERCI, PATRON", "T’ES UN VRAI"),
        "jongleur": ("ET HOP! MERCI", "UNE DE PLUS!"),
        "echassier": ("MERCI D’EN BAS!", "ÇA MONTE AU CHAPEAU"),
    },
}

# --- La photo du touriste --------------------------------------------------------

PHOTO: dict = {
    "invite": "PRENDRE SA PHOTO",
    "metier": "touriste",
    "portee_px": 26,
    "pose_images": 100,
    # Il paie de SA poche (`argent` du passant), pas d'un puits sans fond.
    "pourboire": (2, 5),
    "merci": ("THANK YOU!", "VERY NICE!", "MERCI BEAUCOUP!", "SO NICE, BAIE-DES-BRUMES!"),
}


def exporter() -> dict:
    """Le catalogue tel que le navigateur le tient : des listes, jamais des tuples."""
    return {
        "asseoir": {**ASSEOIR, "sieges": {k: dict(v) for k, v in ASSEOIR["sieges"].items()},
                    "refus": dict(ASSEOIR["refus"])},
        "fouiller": {**FOUILLER, "decors": dict(FOUILLER["decors"]),
                     "tables": {t: [list(e) for e in table] for t, table in FOUILLER["tables"].items()},
                     "standing": dict(FOUILLER["standing"]),
                     "trouvailles": {s: {k: (list(v) if isinstance(v, tuple) else v) for k, v in t.items()}
                                     for s, t in FOUILLER["trouvailles"].items()}},
        "boire": {**BOIRE, "decors": list(BOIRE["decors"])},
        "barbecue": {**BARBECUE, "decors": list(BARBECUE["decors"])},
        "borne": {**BORNE, "decors": list(BORNE["decors"])},
        "pourboire": {**POURBOIRE, "metiers": list(POURBOIRE["metiers"]),
                      "merci": {m: list(mots) for m, mots in POURBOIRE["merci"].items()}},
        "photo": {**PHOTO, "pourboire": list(PHOTO["pourboire"]), "merci": list(PHOTO["merci"])},
    }
