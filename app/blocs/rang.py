"""Le rang : le chalet, le lac de la clairière et la cabane à sucre, un seul bloc
(docs/jalons/la-ville-s-agrandit-au-nord.md).

Martin (26 sept. 2026) : « Regroupe la clairière et la cabane à sucre avec le chalet. » Puis : « Je préfère
une vraie fusion », et « l'entrée de la ville au rang [doit être] une ouverture de rue ». On quitte la ville
par la rue des Quais qui traverse jusqu'au bord ouest (`carte.OUVERTURES_DE_RUE`) ; au noir, on est sur le
chemin de gravier qui la continue. Le chalet est au bord du lac de la clairière (son quai de bois), la cabane
dans son érablière, de l'autre côté de l'allée.

⚠️ LE CHALET S'ACHÈTE (2 500 $, le prix du bar) et reste la deuxième planque : son lit, son coffre PARTAGÉ avec
la planque de Rocco et sa garde-robe ; une partie rouverte s'y réveille avec le char garé sur sa place. La cabane
garde son comptoir des sucres (le printemps seulement, `magasins.COMPTOIRS["sucre"]`) et le défi de la tire.
Leurs PIÈCES n'ont pas bougé d'une tuile : elles viennent des anciens `chalet.py` et `cabane.py`.

⚠️ LE PLAN EST LA VÉRITÉ, composé une fois et sans un dé depuis les trois plans d'avant (le script est dans la
fiche du jalon) : le lac et sa grève de la clairière, le toit et la façade du chalet, ceux de la cabane.
"""

from .. import carte

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AA,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,b,,,,,,,,,,,A,,AA",
    "AAb,,,A,A,AA,sssssssssss,AA,,,,,,,,,,,,bA,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,b,,A",
    "A,,,,,,,,,ssss~~~~~~~~~ssss,,,,,,,,,,,,,,,,,,,,,,,,,b,,,,,,,,,,A,,,,,,,,,,,,,,AA",
    "AA,,,,,,sss~~~~~~~~~~~~~~~sss,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,b,,,,,,,,,,,,,A",
    "A,,,,,,ss~~~~~~~~~~~~~~~~~~~ss,,,,,,,,,,,b,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,AA",
    "AA,,,,ss~~~~~~~~~~~~~~~~~~~~~ss,,,,,,,,,,,,,,A,,,,,,,,b,,,,,,,,,,,,,,,,,,,A,,,,A",
    "A,,,,sss~~~~~~~~~~~~~~~~~~~~~sss,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,bA,,,,,,,,,AA",
    "AA,,,ss~~~~~~~~~~~~~~~~~~~~~~~ss,,,,,,,,,,,b,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,A",
    "A,,,,sss~~~~~~~~~~~~~~~~~~~~~sss,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,AA",
    "AA,,,,ss~~~~~~~~~~~~~~~~~~~~~ss,,,,,,,PPPPPPPPPPP,,,,,,,,,PPPPPPPPPPPPPP,,,,,,,A",
    "A,,,,,,ss~~~~~~~~~~~~~~~~~~~ss,,,,,,,,PPPPPPPPPPP,,,,,,,,,PPPPPPPPPPPPPP,A,,,,AA",
    "AA,,,,b,sss~~~~~~~~~~~~~~~sss,,,,,,,,,PPPPPPPPPPP,,,,,,,,,PPPPPPPPPPPPPP,,,,,,,A",
    "A,,,,,,,,,ssss~~~QQQ~~~ssss,,,,,,,,,,,PPPPPPPPPPP,,,,,,,,,PPPPPPPPPPPPPP,,,,,,AA",
    "AA,,b,,,,,,,,ssssgggssss,,,,,,,,,,,,,,PPPPPPPPPPP,,,,,,A,,PPPPPPPPPPPPPP,,,,,,,A",
    "A,,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,,,HWWFFDFFWWH,,,,,,,,,HWWFFFDFFFFWWH,,,,,,AA",
    "AA,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,,,,,,,,,,,,,g,,,,,,,,b,,,,,A",
    "A,,,,,,,A,,,b,,,,ggg,,,,,,,,,,,,,,,,,,,,,,,g,ppp,,,,,,,,,,,,,,,,g,,,,,,,,,,,,,AA",
    "AAA,,,,,,,,,,,,,,ggg,,,,,b,,,,,A,,,,,,,,,,,g,ppp,,,,,,,,,,,,,,,,g,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,ggg,,,,,A,,,,,,,,,,,,,,,,,g,,,,,,,,,,A,,,,,,,,,g,,,,,,,,,,b,,AA",
    "AA,,,,,,,,,,,,b,,ggg,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,b,,,,,,,,,,,,g,,,,,,,,,,,,A,A",
    "A,,,,,,,,,,,,A,,,ggg,,,,,,,b,,,,,,,,,,,,,,,g,,,,,,,,,,,,,,,,,,,,g,,,,,,,,,,,,,AA",
    "AA,b,,,A,,,,,,,,,ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg",
    "A,,,,,,,,,,,,,,,bggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg",
    "AA,,,,,,,,,,,,,,,ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg",
    "A,,,,b,,,,,,,,,,,ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg",
    "AA,,,,,,,,,,A,,,,,b,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,b,,,,,,,,,,,,,,A,,,,,,,,A",
    "A,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,b,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,b,,,,,,,,,AA",
    "AA,,,,,b,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,b,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,b,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,b,,,,,,,,,,,,,,,,,,,,AA",
    "AA,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,b,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,b,,,,A,,,A",
    "A,,,,,,,,b,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,b,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,AA",
    "AA,,,A,,,,,,,,,,,,,,,,b,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,b,,,A,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,b,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,b,,,,,AA",
    "AA,,,,,,,,,b,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,b,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,A,,,,,,,b,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,b,,,,,,,,,,,,A,,,AA",
    "AA,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,b,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,b,,,,A",
    "A,,,A,,,,,,,,b,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,b,,,,,,,,,,,A,,,,,,,,,,,,,,,AA",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,bA,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,b,,,,,,,,,,,,,,,A",
    "A,b,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,b,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,b,AA",
    "AA,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,b,,,,,,,,,,,,,,,,,,,,A,,,,,A",
    "A,,,,,,,,A,,,,,,,,,,,,,,,,,,b,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,b,A,,,,,,,,,,AA",
    "AA,Ab,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,b,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,b,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,bA,,,,,,,,,,,,,,,,,,,,,,AA",
    "AA,,,,,,,,,,,,,,,,,,A,,,,,,,,,b,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,b,,,,,,,,,,,A",
    "A,,,,,b,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,AA",
    "AA,,,,,,A,,,,,,,,,,b,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,b,,,,,,,,,A,,,,,,,,,,,,A",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
    "b": (",", "buisson"),
}

#: Dedans : un vrai camp en bois rond (Martin, 26 sept. 2026 : « je veux que ça ait vraiment l'air
#: d'être un chalet »). Les murs en rondins (`B`, `W`, `D` en bois rond, comme dehors) ; au mur du
#: haut, le FOYER de pierre (`Y`, deux tuiles) sous sa cheminée (`K`), la corde de bois (`L`) à
#: côté, la peau d'ours (`U`) et les deux berçantes (`V`) devant le feu ; le panache d'orignal
#: (`N`) et les raquettes (`&`) accrochés aux rondins. Le lit à carreaux de bûcheron, le coffre
#: cerclé de fer, l'armoire de pin, le poêle à bois en fonte et la table de pin sont les meubles
#: de la ville repeints (`materiaux` : `l@chalet`…) — ils gardent ce qu'ils font.
PIECE_CHALET = carte._piece("chalet", "Le chalet du rang", porte="maison", plan="""
BWWBNKKB&WB
Bll  YYL eB
Bll VUU   B
Bk   UUV  B
B        zB
Bhaah     B
B        LB
BBBBWWDWWBB
""", points=(carte._pt("lit", 2, 2), carte._pt("coffre", 1, 3), carte._pt("garde_robe", 9, 1)),
    materiaux={"B": "bois_rond", "W": "bois_rond", "D": "bois_rond", "t": "chalet", "l": "chalet",
               "k": "chalet", "e": "chalet", "z": "chalet", "a": "chalet", "h": "chalet"})

#: Dedans : la salle des sucres, en bois rond. Le poêle à bois et la corde de bois au mur du haut, le
#: comptoir des sucres au milieu (`emplettes`, genre `sucre`), les grandes tables de pin et leurs bancs.
PIECE_CABANE = carte._piece("cabane", "La cabane à sucre", porte="commerce", plan="""
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
    "slug": "rang",
    "nom": "Le rang",
    "plan": PLAN,
    "decors": DECORS,
    "panneau": "RANG", "panneau_retour": "VILLE",
    # Le passage : la rue des Quais qui traverse jusqu'au bord ouest — trottoir, deux voies, trottoir.
    "passage": {"bord": "ouest", "de": 171, "l": 4},
    # Le chemin de gravier la continue, par le bord EST du bloc : les mêmes quatre rangées.
    "retour": {"bord": "est", "de": 23, "l": 4},
    "arrivee": {"x": 77, "y": 24},
    "gens": False,
    # ⚠️ En BOIS ROND, le chalet comme la cabane : les mêmes glyphes que la ville, un autre peintre.
    "materiaux": {"F": "bois_rond", "W": "bois_rond", "D": "bois_rond"},
    "portes": [{"x": 43, "y": 16, "interieur": "chalet", "lieu": "chalet"},
               {"x": 64, "y": 16, "interieur": "cabane", "lieu": "cabane"}],
    "pieces": {"chalet": PIECE_CHALET, "cabane": PIECE_CABANE},
    # ⚠️ LA PLANQUE : le chalet, son prix, et la place où son char attend (le milieu du `ppp` d'en haut).
    "planque": {"piece": "chalet", "prix": 2500, "char": {"x": 46, "y": 18}},
    # La cheminée du chalet, au-dessus de son foyer : elle fume (`Blocs.dessiner`).
    "cheminees": [{"x": 43, "y": 12, "l": 2}],
    # Les fenêtres de la cabane, devant sa façade.
    "lampes": [{"x": 59, "y": 17, "r": 26, "c": "fenetre"}, {"x": 70, "y": 17, "r": 26, "c": "fenetre"}],
}
