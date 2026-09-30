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

#: Le −1, en deux rangées face à face (Martin, 30 sept. 2026 : « le stationnement me semble beaucoup trop grand. on
#: pourrait mettre 2 rangées face à face ») : cinq cases au nord, le nez au mur nord (`^`), cinq au sud, le nez au mur
#: sud (`v`), une allée de cinq tuiles entre les deux — assez pour qu'un camion recule d'une case. La rampe au
#: nord-est (12 à 14), l'ascenseur au mur sud-est (ses portes, les deux `D`). `B` : du béton peint (`materiaux`, comme
#: les murs d'une pièce). 17 × 14 : plus petit que l'écran, centré avec du noir autour, comme une pièce.
PLAN: tuple[str, ...] = (
    "BBBBBBBBBBBB###BB",
    "BBBBBBBBBBBB###BB",
    "B^^^^^^^^^^#####B",
    "B^^^^^^^^^^#####B",
    "B^^^^^^^^^^#####B",
    "B###############B",
    "B###############B",
    "B###############B",
    "B###############B",
    "B###############B",
    "Bvvvvvvvvvv#####B",
    "Bvvvvvvvvvv#####B",
    "Bvvvvvvvvvv#####B",
    "BBBBBBBBBBBBBDDBB",
)

#: Les dix cases : deux tuiles de large, trois de creux. P1 à P5 au nord (le nez au mur nord), P6 à P10 en face, au
#: sud (le nez au mur sud), case pour case.
CASES: tuple[dict, ...] = (
    tuple({"n": k + 1, "x": x, "y": 2, "l": 2, "h": 3, "cap": -math.pi / 2} for k, x in enumerate((1, 3, 5, 7, 9)))
    + tuple({"n": k + 6, "x": x, "y": 10, "l": 2, "h": 3, "cap": math.pi / 2} for k, x in enumerate((1, 3, 5, 7, 9))))

#: La rangée où l'on attend l'ascenseur (ses portes juste au sud) : ACTION y remonte à la pièce du garage, et on y
#: arrive en descendant.
ASCENSEUR = {"x": 13, "y": 12, "l": 2}

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
    "retour": {"bord": "nord", "de": 12, "l": 3},
    "arrivee": {"x": 13, "y": 3},
    "gens": False,
    # Sous terre : ni pluie, ni neige, ni nuit (`Monde.aLAbri`).
    "abrite": True,
    "materiaux": {"B": "piece", "D": "piece"},
    "souterrain": {"cases": CASES, "ascenseur": ASCENSEUR},
}
