"""La planque qu'on décore (P4, docs/jalons/des-choses-a-collectionner-et-la-planque-qu-on-decore.md), vague 2.

Une planque vide au début, pleine à la fin : c'est le bilan de la partie, qu'on regarde. Deux choses s'y posent :

- **les trophées** de l'album (`TROPHEES`) : le cadre des dix cartes, celui des vingt-cinq, et la coupe de la Ligue
  quand l'album est complet. On ne les achète pas : ils viennent d'eux-mêmes, au palier ;
- **les meubles** (`MEUBLES`) : on les commande au **catalogue Beausoleil**, sur la table de la planque (le point
  `catalogue`), et ils arrivent **le lendemain**. Chaque meuble dit `ou` il se vend — `catalogue` aujourd'hui ;
  le marché aux puces (sa ligne, après celle-ci) vendra ceux qui portent `puces`.

⚠️ **UNE PLACE ÉCRITE, JAMAIS UN DÉ** : chaque objet a sa tuile dans chaque planque (`PLACES`, par pièce : la
planque de Rocco et le chalet du rang — le même mécanisme sert aux deux). Le juge vérifie qu'avec TOUT posé,
chaque point de la pièce se rejoint encore depuis la porte.

⚠️ **CE QUI SE POSE NAÎT EN ENTRANT, À PART** : les objets sont des décors de la pièce, créés quand on y entre
(`Decoration.meubler`), numérotés hors de la suite de la ville (`Entites.enDehorsDeLaSuite`) — une partie qui
entre dans sa planque ne décale le numéro de rien de ce qui naît dehors.

⚠️ **LE POIDS** : le catalogue voyage avec les collections (`/api/collections`), pas dans les définitions.
"""

from __future__ import annotations

#: Les trophées de l'album, par palier de la famille. `palier` : le nombre de cartes qu'il faut.
TROPHEES: tuple[dict, ...] = (
    {"slug": "cadre_dix", "nom": "LE CADRE DES DIX CARTES", "famille": "cartes", "palier": 10},
    {"slug": "cadre_vingt_cinq", "nom": "LE GRAND CADRE DES VINGT-CINQ", "famille": "cartes", "palier": 25},
    {"slug": "coupe_album", "nom": "LA COUPE DE LA LIGUE", "famille": "cartes", "palier": 40},
    # Vague 3 : l'étagère des bebelles, dès la première — et chaque bebelle trouvée s'y pose d'elle-même.
    {"slug": "etagere_bebelles", "nom": "L’ÉTAGÈRE DES BEBELLES", "famille": "bebelles", "palier": 1},
    # Vague 5 : le mur des enseignes, dès la première — un panneau perforé où chaque enseigne dévissée pend à son crochet.
    {"slug": "mur_enseignes", "nom": "LE MUR DES ENSEIGNES", "famille": "enseignes", "palier": 1},
    # L'album des lieux complet (le photographe, `photos.ALBUM`) : dix cartes postales sous verre.
    {"slug": "cadre_lieux", "nom": "L’ALBUM DES LIEUX", "famille": "lieux", "palier": 10},
)

#: Le catalogue Beausoleil. `texte` : la ligne du catalogue (une ligne du menu, 44 caractères au plus) — le ton
#: de docs/ecrire-drole.md : c'est le catalogue qui se vante, et c'est lui qui a tort. `ou` : où il se vend.
MEUBLES: tuple[dict, ...] = (
    {"slug": "jukebox", "nom": "LE JUKE-BOX", "prix": 1500, "ou": ["catalogue", "puces"],
     "texte": "TOUTES LES STATIONS. MÊME CELLES QU’ON FUIT."},
    {"slug": "aquarium", "nom": "L’AQUARIUM", "prix": 600, "ou": ["catalogue"],
     "texte": "POISSON ROUGE INCLUS. IL S’APPELLE GÉRALD."},
    {"slug": "sofa", "nom": "LE SOFA À CARREAUX", "prix": 400, "ou": ["catalogue", "puces"],
     "texte": "À CARREAUX : LES TACHES NE PARAISSENT PAS."},
    {"slug": "televiseur", "nom": "LE TÉLÉVISEUR", "prix": 350, "ou": ["catalogue", "puces"],
     "texte": "DEUX POSTES. TROIS SI TU TIENS L’ANTENNE."},
    {"slug": "lampe_lave", "nom": "LA LAMPE À LAVE", "prix": 150, "ou": ["catalogue"],
     "texte": "LA LAVE NE SORT PAS. GARANTIE UN AN."},
    {"slug": "tapis_tresse", "nom": "LE TAPIS TRESSÉ", "prix": 90, "ou": ["catalogue", "puces"],
     "texte": "TRESSÉ À LA MAIN. PAR QUI ? NE DEMANDE PAS."},
    # Le portrait du photographe (docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-l-enseigne.md, vague 3c) : tiré au
    # studio avec la tenue et la coupe du jour (`partie.portrait`), encadré, livré le lendemain.
    # Vague 4b : ce qui se vend EN VILLE (`ou: ville`, les rayons des comptoirs) et se pose dans la pièce d'en arrière
    # de la planque (`piece`) — la lanterne, le ficus, le vaisselier, le tableau, l'horloge, le miroir.
    {"slug": "lanterne", "nom": "LA LANTERNE DE PAPIER", "prix": 80, "ou": ["ville"], "piece": "planque_arriere",
     "texte": "PORTE BONHEUR. PAS GARANTI."},
    {"slug": "ficus", "nom": "LE FICUS", "prix": 45, "ou": ["ville"], "piece": "planque_arriere",
     "texte": "ARROSE-LE. IL T'EN VOUDRA PAS."},
    {"slug": "vaisselier", "nom": "LE VAISSELIER", "prix": 300, "ou": ["ville"], "piece": "planque_arriere",
     "texte": "LA VAISSELLE DES GRANDES OCCASIONS. AUCUNE."},
    {"slug": "tableau", "nom": "LE TABLEAU", "prix": 450, "ou": ["ville"], "piece": "planque_arriere",
     "texte": "UN COUCHER DE SOLEIL SUR LA BAIE. SIGNÉ."},
    {"slug": "horloge", "nom": "L’HORLOGE GRAND-PÈRE", "prix": 600, "ou": ["ville"], "piece": "planque_arriere",
     "texte": "ELLE SONNE LES HEURES. ET LES QUARTS."},
    {"slug": "miroir", "nom": "LE MIROIR DORÉ", "prix": 120, "ou": ["ville"], "piece": "planque_arriere",
     "texte": "TU Y VERRAS UN BANDIT. C'EST NORMAL."},
    {"slug": "portrait", "nom": "TON PORTRAIT", "prix": 60, "ou": ["photographe"],
     "texte": "TON MEILLEUR PROFIL. IL A FAIT SON POSSIBLE."},
)

#: Ce qui ne se pose QUE dans certaines planques : les rondins du chalet n'ont plus de place au mur (les deux cadres,
#: les fenêtres, la cheminée) ni de table libre — le portrait et l'album des lieux vont chez Rocco.
SEULEMENT: dict[str, tuple[str, ...]] = {"portrait": ("planque",), "cadre_lieux": ("planque",),
                                         # La pièce d'en arrière (vague 4b) : ce qui se vend en ville.
                                         **{s: ("planque_arriere",) for s in ("lanterne", "ficus", "vaisselier",
                                                                               "tableau", "horloge", "miroir")}}
#: Les planques où va ce qui n'a pas de `SEULEMENT` : celle de Rocco et le chalet.
PARTOUT: tuple[str, ...] = ("planque", "chalet")

#: Où chaque objet se pose, par pièce de planque : une tuile de la pièce (`l` : sa largeur en tuiles, 1 si absent —
#: l'étagère des bebelles en prend deux). ⚠️ Les cadres se posent sur la rangée
#: sous le mur du haut et se peignent SUR le mur ; la coupe et la lampe, sur une table ; le tapis, à plat devant
#: la porte. Ce qui est `solide` (dans `DECORS`) ferme sa tuile : le juge de la pièce le compte.
PLACES: dict[str, dict[str, dict]] = {
    # La planque de Rocco (`carte._piece("planque")`) : les cadres au-dessus du lit, la coupe et la lampe sur la
    # table, le coin salon à droite (le téléviseur contre le mur, le sofa en face), le juke-box sous les fenêtres,
    # contre le lit, l'aquarium à côté du coffre, le tapis tressé devant la porte.
    "planque": {
        "cadre_dix": {"x": 1, "y": 1}, "cadre_vingt_cinq": {"x": 2, "y": 1}, "coupe_album": {"x": 2, "y": 3},
        "lampe_lave": {"x": 2, "y": 4}, "televiseur": {"x": 8, "y": 1}, "aquarium": {"x": 7, "y": 1},
        "sofa": {"x": 8, "y": 4}, "jukebox": {"x": 3, "y": 1}, "tapis_tresse": {"x": 6, "y": 6},
        # L'étagère des bebelles, contre le mur du bas entre le poêle et la porte : DEUX tuiles (`l`).
        "etagere_bebelles": {"x": 4, "y": 6, "l": 2},
        # Le mur des enseignes, appuyé au mur du haut sous les fenêtres, à côté du juke-box : DEUX tuiles.
        "mur_enseignes": {"x": 4, "y": 1, "l": 2},
        # Le photographe (vague 3c) : l'album des lieux au-dessus du coffre, le portrait dans le coin, au-dessus de la
        # garde-robe — les deux derniers bouts de mur.
        "cadre_lieux": {"x": 6, "y": 1}, "portrait": {"x": 9, "y": 1},
    },
    # Le chalet du rang (`blocs/rang.py`) : les cadres sur les rondins, de part et d'autre de la cheminée, la coupe
    # et la lampe sur la table de pin, le coin salon à droite (la garde-robe reste à portée), l'aquarium sous le
    # coffre, le juke-box à gauche de la porte, le mur des enseignes dans le coin du bas.
    "chalet": {
        "cadre_dix": {"x": 3, "y": 1}, "cadre_vingt_cinq": {"x": 7, "y": 1}, "coupe_album": {"x": 2, "y": 5},
        "lampe_lave": {"x": 3, "y": 5}, "televiseur": {"x": 8, "y": 3}, "aquarium": {"x": 1, "y": 4},
        "sofa": {"x": 8, "y": 5}, "jukebox": {"x": 3, "y": 6}, "tapis_tresse": {"x": 6, "y": 6},
        # Derrière le sofa, contre le mur du bas (la table de pin ferme le coin de gauche : le juke-box y est seul).
        "etagere_bebelles": {"x": 7, "y": 6, "l": 2},
        # Dans le coin du bas, contre les rondins (ceux du haut portent les cadres et la cheminée) : le juke-box
        # lui a laissé le coin et s'est rapproché de la porte (1er oct. 2026).
        "mur_enseignes": {"x": 1, "y": 6, "l": 2},
    },
    # La pièce d'en arrière de la planque (vague 4b) : le tableau, le miroir et la lanterne au mur, l'horloge et le
    # vaisselier contre les murs du haut, le ficus dans le coin — le passage (1, 5) et l'entrée (4, 5) dégagés.
    "planque_arriere": {
        "tableau": {"x": 2, "y": 1}, "miroir": {"x": 5, "y": 1}, "lanterne": {"x": 6, "y": 1},
        "horloge": {"x": 1, "y": 2}, "vaisselier": {"x": 7, "y": 2}, "ficus": {"x": 7, "y": 4},
    },
}

#: Comment chaque objet se tient dans sa tuile : `mur` (sur la rangée sous le mur du haut, peint SUR le mur),
#: `table` (sur la table de sa tuile), `sol` (debout : il ferme sa tuile), `plat` (à plat, sous les pieds).
#: ⚠️ Le navigateur le lit d'ici (`Decoration`), et ce qui est `sol` est `solide` dans ses dessins — un juge les
#: compare.
POSES: dict[str, str] = {
    "cadre_dix": "mur", "cadre_vingt_cinq": "mur", "coupe_album": "table", "lampe_lave": "table",
    "jukebox": "sol", "aquarium": "sol", "sofa": "sol", "televiseur": "sol", "tapis_tresse": "plat",
    "etagere_bebelles": "sol", "mur_enseignes": "sol", "cadre_lieux": "mur", "portrait": "mur",
    "tableau": "mur", "miroir": "mur", "lanterne": "mur", "horloge": "sol", "vaisselier": "sol", "ficus": "sol",
}
SOLIDES = frozenset(s for s, p in POSES.items() if p == "sol")


def exporter() -> dict:
    """Ce que `/api/collections` sert de la planque : les trophées, le catalogue et les places."""
    return {"trophees": [dict(t) for t in TROPHEES],
            "meubles": [{**m, "ou": list(m["ou"])} for m in MEUBLES],
            "places": {piece: {s: dict(p) for s, p in places.items()} for piece, places in PLACES.items()},
            "poses": dict(POSES)}
