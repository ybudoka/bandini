"""Le chalet du rang : la deuxième planque, au bout d'un rang de campagne (vague 3 des blocs).

Demande de Martin (25 sept. 2026) : « une 2e planque plus loin » — et, pour le premier vrai
bloc de carte, la deuxième planque. On la rejoint par le bord OUEST des Quais, à l'autre bout
de la ville par rapport à la planque de Rocco (au Faubourg) : on pousse contre le bord, la
carte fait un noir, et on est sur le rang qui mène au chalet, au bord d'un étang.

⚠️ Il S'ACHÈTE (2 500 $, le prix du bar) : avant, son lit, son coffre et sa garde-robe ne
proposent que de l'acheter. Après : on y dort, on s'y sauvegarde — et une partie rouverte se
réveille ICI, dans le bloc — et le char garé sur sa place revient avec la partie, comme
devant la planque de Rocco. Le coffre est PARTAGÉ avec la planque de Rocco : c'est le même
magot, rangé à deux endroits (la fiche le laissait à trancher ; partagé se joue mieux).
"""

from .. import carte

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AA,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A",
    "A,,,,,,,Asssss,,,A,A,,A,,,,AA,AAAA,,,,,,,,AA",
    "AAA,,,sss~~~~~sss,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,ss~~~~~~~~~ss,,,,,,,,,,,A,,,,,,,,,,,,AA",
    "AA,,s~~~~~~~~~~~~~s,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,ss~~~~~~~~~~~~~ss,,,,,,,,,,,,,,,,,,,,,AAA",
    "AA,s~~~~~~~~~~~~~~~s,,,,,,,,,,,b,,,,,,,,,A,A",
    "A,Ass~~~~~~~~~~~~~ss,,,,,,A,,,,,,,,,,,,,,AAA",
    "AAA,s~~~~~~~~~~~~~s,,,b,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,ss~~~~~~~~~ss,,,,,,,,,,,,,,,,b,,,,,,,AA",
    "AAA,A,sss~~~~PPPPPPPPPPP,,,,,,,,,,,,,,,,,A,A",
    "A,,,,,,,,ssssPPPPPPPPPPP,,,,,,,,,,,,bb,,,,AA",
    "AAA,,,b,,b,,,PPPPPPPPPPP,,,,,,A,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,PPPPPPPPPPP,,,,,,,,,,,,,,,,,,AA",
    "AA,,,,,,,,,b,PPPPPPPPPPP,,,,,,,,,,,,,,,,,A,A",
    "A,,,,,,,,,,,,HWWFFDFFWWH,,,,,,,,b,,,,,,,,,AA",
    "AA,,,,,,,,,,ggggggggggggg,,,,,,,A,,,,,,,,A,A",
    "A,,,,,,,,,,,gggggggggggggggggggggggggggggggg",
    "AAA,,,,,,,,,gggggggggggggggggggggggggggggggg",
    "A,,,,,,,,,,,gggggggggggggggggggggggggggggggg",
    "AAA,,,,,,,,,gggggggggpppg,A,,,,,,,,,,,b,,,,A",
    "A,A,,,,,,,,,gggggggggpppg,,,,,,,b,,,,,,,,,AA",
    "AAA,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,A",
    "A,,,,,,,b,,,,,,,,,,,,,,,,,,,b,,,,,,,,,,,,AAA",
    "AA,,,,,,AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,AA",
    "AA,,,,,AA,,,,A,,,,,AA,,,AAA,,A,AA,,,,,A,,,,A",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
    "b": (",", "buisson"),
}

#: Dedans : la planque de Rocco en plus petit, avec un poêle à bois (`z`) — c'est un chalet.
PIECE = carte._piece("chalet", "Le chalet du rang", porte="maison", plan="""
BBBWWWBBBBB
Bll   k  zB
Bll      nB
B ah yyy  B
B ah yyy  B
B    yyy eB
Bj      n B
BBBBWWDWWBB
""", points=(carte._pt("lit", 2, 2), carte._pt("coffre", 6, 1), carte._pt("garde_robe", 9, 5)))

BLOC = {
    "slug": "chalet",
    "nom": "Le chalet du rang",
    "plan": PLAN,
    "decors": DECORS,
    "panneau": "CHALET", "panneau_retour": "VILLE",
    # Le passage : le trottoir du bord OUEST des Quais, à l'autre bout de la ville par
    # rapport à la planque de Rocco (au Faubourg, 177 × 49).
    "passage": {"bord": "ouest", "de": 164, "l": 5},
    # Le rang arrive par le bord EST du bloc, ses trois rangées.
    "retour": {"bord": "est", "de": 18, "l": 3},
    "arrivee": {"x": 40, "y": 19},
    "gens": False,
    # ⚠️ En BOIS ROND (Martin : « une vraie texture de bois rond ») : les mêmes glyphes que la
    # ville — la porte reste un `D`, elle s'ouvre comme les autres —, un autre peintre.
    "materiaux": {"F": "bois_rond", "W": "bois_rond", "D": "bois_rond"},
    # La porte du chalet et sa pièce.
    "portes": [{"x": 18, "y": 16, "interieur": "chalet", "lieu": "chalet"}],
    "pieces": {"chalet": PIECE},
    # ⚠️ LA PLANQUE : ce qui la distingue d'une pièce ordinaire. Son prix, la pièce où
    # l'on dort, et la place où son char attend (la tuile du milieu du `ppp`).
    "planque": {"piece": "chalet", "prix": 2500, "char": {"x": 22, "y": 21}},
}
