"""Le grand garage souterrain, sous le Garage Rocco Bandini (docs/jalons/le-grand-garage-souterrain.md).

Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des véhicules que nous pourrons reprendre après
dans un grand garage souterrain ». On y descend au volant par le rideau de Ti-Guy (DESCENDRE AU SOUS-SOL), ou à pied
par l'ascenseur de la pièce du garage ; on y gare son char sur une case, et il y est encore au retour.

⚠️ **UN BLOC SANS PASSAGE EN VILLE** : il n'est pas au bout d'une rue, il est SOUS le garage. Il vit dans
`blocs.SOUS_SOLS`, pas dans `blocs.BLOCS` (dont les juges exigent un passage sur un bord de la ville) ; son `seuil`
dit devant quel rideau on ressort (`Blocs.retourEnVille`).

⚠️ **LES CHARS NE SONT PAS DANS LE PLAN** : ils vivent dans la partie (`partie.souterrain.cases`), et le navigateur
les pose sur les cases à chaque descente (`static/js/souterrain.js`). Le plan ne porte que le béton.
"""

import math

#: Les cases d'un niveau, et de tout le sous-sol (le −2 est la vague 2).
PAR_NIVEAU = 10
CASES_MAX = 20

#: Le −1 : la rampe au nord (14 à 16), dix cases contre le mur nord (le nez au mur), l'allée, deux piliers, et
#: l'ascenseur au milieu du mur sud (ses portes, les deux `D`). `B` : du béton peint (`materiaux`, comme les murs
#: d'une pièce). 32 × 18 : plus grand que l'écran (30 × 17), la caméra n'y voit jamais le vide.
PLAN: tuple[str, ...] = (
    "BBBBBBBBBBBBBB###BBBBBBBBBBBBBBB",
    "BBBBBBBBBBBBBB###BBBBBBBBBBBBBBB",
    "B#^^^^^^^^^^######^^^^^^^^^^###B",
    "B#^^^^^^^^^^######^^^^^^^^^^###B",
    "B#^^^^^^^^^^######^^^^^^^^^^###B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B######B################B######B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "BBBBBBBBBBBBBBBDDBBBBBBBBBBBBBBB",
)

#: Les dix cases, de gauche à droite : deux tuiles de large, trois de creux, le nez au mur nord.
CASES: tuple[dict, ...] = tuple({"n": k + 1, "x": x, "y": 2, "l": 2, "h": 3, "cap": -math.pi / 2}
                                for k, x in enumerate((2, 4, 6, 8, 10, 18, 20, 22, 24, 26)))

#: La rangée où l'on attend l'ascenseur (ses portes juste au sud) : ACTION y remonte à la pièce du garage, et on y
#: arrive en descendant.
ASCENSEUR = {"x": 15, "y": 16, "l": 2}

BLOC = {
    "slug": "souterrain",
    "nom": "Le garage souterrain",
    "panneau": "SOUS-SOL", "panneau_retour": "RUE",
    "plan": PLAN,
    "decors": {},
    # Pas de passage en ville : on ressort devant le rideau de Ti-Guy (`porte_de_garage` au lieu `garage`).
    "passage": None,
    "seuil": "garage",
    # La rampe, au nord : on la monte au volant (ou à pied), et on est devant le rideau.
    "retour": {"bord": "nord", "de": 14, "l": 3},
    "arrivee": {"x": 15, "y": 4},
    "gens": False,
    # Sous terre : ni pluie, ni neige, ni nuit (`Monde.aLAbri`).
    "abrite": True,
    "materiaux": {"B": "piece", "D": "piece"},
    "souterrain": {"cases": CASES, "ascenseur": ASCENSEUR},
}
