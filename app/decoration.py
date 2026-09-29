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
)

#: Où chaque objet se pose, par pièce de planque : une tuile de la pièce. ⚠️ Les cadres se posent sur la rangée
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
    },
    # Le chalet du rang (`blocs/rang.py`) : les cadres sur les rondins, de part et d'autre de la cheminée, la coupe
    # et la lampe sur la table de pin, le coin salon à droite (la garde-robe reste à portée), l'aquarium sous le
    # coffre, le juke-box à gauche de la porte.
    "chalet": {
        "cadre_dix": {"x": 3, "y": 1}, "cadre_vingt_cinq": {"x": 7, "y": 1}, "coupe_album": {"x": 2, "y": 5},
        "lampe_lave": {"x": 3, "y": 5}, "televiseur": {"x": 8, "y": 3}, "aquarium": {"x": 1, "y": 4},
        "sofa": {"x": 8, "y": 5}, "jukebox": {"x": 1, "y": 6}, "tapis_tresse": {"x": 6, "y": 6},
    },
}

#: Comment chaque objet se tient dans sa tuile : `mur` (sur la rangée sous le mur du haut, peint SUR le mur),
#: `table` (sur la table de sa tuile), `sol` (debout : il ferme sa tuile), `plat` (à plat, sous les pieds).
#: ⚠️ Le navigateur le lit d'ici (`Decoration`), et ce qui est `sol` est `solide` dans ses dessins — un juge les
#: compare.
POSES: dict[str, str] = {
    "cadre_dix": "mur", "cadre_vingt_cinq": "mur", "coupe_album": "table", "lampe_lave": "table",
    "jukebox": "sol", "aquarium": "sol", "sofa": "sol", "televiseur": "sol", "tapis_tresse": "plat",
}
SOLIDES = frozenset(s for s, p in POSES.items() if p == "sol")


def exporter() -> dict:
    """Ce que `/api/collections` sert de la planque : les trophées, le catalogue et les places."""
    return {"trophees": [dict(t) for t in TROPHEES],
            "meubles": [{**m, "ou": list(m["ou"])} for m in MEUBLES],
            "places": {piece: {s: dict(p) for s, p in places.items()} for piece, places in PLACES.items()},
            "poses": dict(POSES)}
