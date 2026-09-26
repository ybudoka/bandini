"""La cabane à sucre du rang des Érables (docs/jalons/la-cabane-a-sucre.md).

Au printemps du jeu (avril et mai, `calendrier`), la ville sent le sirop : au bout d'un rang, une
cabane s'ouvre dans l'érablière — son comptoir (oreilles de crisse, fèves au lard, tire sur la neige) et
son défi (la tire). On la rejoint par le bord NORD du Faubourg : on pousse contre le bord, la carte fait
un noir, et on est dans l'érablière.

⚠️ **UN BLOC**, comme le ciné-parc : une pièce de plus DANS la ville l'aurait fait glisser. La fiche la
voulait dans les bois de La Pointe — mais on n'y pousse contre aucun bord (seuls le nord et l'ouest de
la carte se marchent) ; elle est au nord du Faubourg, au bout d'un rang.

⚠️ **HORS SAISON, ELLE SE DIT FERMÉE** : le bloc, sa porte et sa pièce sont toujours là ; c'est son
comptoir qui le dit (`magasins.COMPTOIRS["sucre"]["saison"]`, lu par `Missions.comptoirFerme`).
"""

from .. import carte

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AA,,A,A,,,AA,,,,A,,,,AA,,,A,A,,A,,A,A,,A",
    "A,A,,,,AA,,,A,A,,A,,A,A,,,AA,,,,A,,,,AAA",
    "A,,A,,A,A,,,AA,,,,A,,,,AA,,,A,A,,A,,A,AA",
    "A,,,A,,,,AA,,,A,A,,A,,A,A,,,AA,,,,A,,,,A",
    "A,A,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,AA",
    "AA,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,A",
    "A,A,A,,A,,,,,PPPPPPPPPPPPPP,,,,,A,A,,A,A",
    "A,AA,,,,,,,,,PPPPPPPPPPPPPP,,,,,,A,,,,AA",
    "A,,,A,,,,,,,,PPPPPPPPPPPPPP,,,,,,,A,A,,A",
    "A,,,AA,,,,,,,PPPPPPPPPPPPPP,,,,,,,AA,,,A",
    "AAA,,,A,,,,,,PPPPPPPPPPPPPP,,,,,,,,,A,AA",
    "A,A,,,,A,,,,,HWWFFFDFFFFWWH,,,,,A,,,AA,A",
    "A,,AA,,,,,,,,,gggggggggggg,,,,,,,AA,,,AA",
    "A,A,A,,,,,,,,,,,,,ggg,,,,,,,,,,,,,A,,,AA",
    "A,,,,A,,,,b,,,,,,,ggg,,,,,,,,,,,,,,AA,,A",
    "AA,,A,A,,,,,,,,,,,ggg,,,,,,,,,,,,,A,A,,A",
    "A,A,,,,A,,,,,,,,,,ggg,,,,,,,,b,,A,,,,AAA",
    "A,,A,,,,,,,,,,,,,,ggg,,,,,,,,,,,,A,,A,AA",
    "A,,,A,,,,,,,,,,,,,ggg,,,,,,,,,,,,,A,,,,A",
    "A,A,,A,,b,,,,,,,,,ggg,,,,,,,,,,,,,,A,,AA",
    "AA,,,,A,,,,,,,,,,,ggg,,,,,,,,,,b,,,,A,,A",
    "A,A,A,,A,,,,,,,,,,ggg,,,,,,,,,,,A,A,,A,A",
    "A,AA,,,,,,,,,,,,,,ggg,,,,,,,,,,,,A,,,,AA",
    "A,,,A,,,,,,,,,,,,,ggg,,,,,,,,,,,,,A,A,,A",
    "AAAAAAAAAAAAAAAAAAgggAAAAAAAAAAAAAAAAAAA",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
    "b": (",", "buisson"),
}

#: Dedans : la salle des sucres, en bois rond. Le poêle à bois et la corde de bois au mur du haut, le
#: comptoir des sucres au milieu (`emplettes`, genre `sucre`), les grandes tables de pin et leurs bancs.
PIECE = carte._piece("cabane", "La cabane à sucre", porte="commerce", plan="""
BBBBBBBBBBBBB
Bz  L ccc  eB
B           B
B aaa   aaa B
B hhh   hhh B
B           B
BBBWWBDBWWBBB
""", points=(carte._pt("emplettes", 6, 1, genre="sucre"),),
    materiaux={"B": "bois_rond", "W": "bois_rond", "D": "bois_rond", "z": "chalet", "L": "chalet", "e": "chalet",
               "a": "chalet", "h": "chalet"})

BLOC = {
    "slug": "cabane",
    "nom": "La cabane à sucre",
    "plan": PLAN,
    "decors": DECORS,
    "panneau": "SUCRE", "panneau_retour": "VILLE",
    # Le passage : le trottoir de ceinture du bord NORD du Faubourg (colonnes 200 à 204), entre la
    # clairière (55) et le ciné-parc (350).
    "passage": {"bord": "nord", "de": 200, "l": 5},
    "retour": {"bord": "sud", "de": 18, "l": 3},
    "arrivee": {"x": 19, "y": 23},
    "gens": False,
    "materiaux": {"F": "bois_rond", "W": "bois_rond", "D": "bois_rond"},
    "portes": [{"x": 19, "y": 12, "interieur": "cabane", "lieu": "cabane"}],
    "pieces": {"cabane": PIECE},
    "lampes": [{"x": 14, "y": 13, "r": 26, "c": "fenetre"}, {"x": 25, "y": 13, "r": 26, "c": "fenetre"}],
}
