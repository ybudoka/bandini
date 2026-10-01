"""Le rang : le chalet, le lac de la clairière et la cabane à sucre, un seul bloc
(docs/jalons/la-ville-s-agrandit-au-nord.md).

Martin (26 sept. 2026) : « Regroupe la clairière et la cabane à sucre avec le chalet. » Puis : « Je préfère
une vraie fusion », et « l'entrée de la ville au rang [doit être] une ouverture de rue ». On quitte la ville
par la rue des Quais qui traverse jusqu'au bord ouest (`carte.OUVERTURES_DE_RUE`) ; au noir, on est sur le
chemin de gravier qui la continue. Le chalet est au bord du lac de la clairière (son quai de bois), la cabane
dans son érablière, de l'autre côté de la haie. Entre les deux, depuis le 30 sept. 2026, une route en lacets
dans le bois (`CHEMIN`) : la cabane tout près de l'entrée, le chalet au bout du chemin.

⚠️ LE CHALET S'ACHÈTE (2 500 $, le prix du bar) et reste la deuxième planque : son lit, son coffre PARTAGÉ avec
la planque de Rocco et sa garde-robe ; une partie rouverte s'y réveille avec le char garé sur sa place. La cabane
garde son comptoir des sucres (le printemps seulement, `magasins.COMPTOIRS["sucre"]`) et le défi de la tire.
Leurs PIÈCES n'ont pas bougé d'une tuile : elles viennent des anciens `chalet.py` et `cabane.py`.

⚠️ LE PLAN EST LA VÉRITÉ, composé une fois et sans un dé depuis les trois plans d'avant (le script est dans la
fiche du jalon) : le lac et sa grève de la clairière, le toit et la façade du chalet, ceux de la cabane. Récrit
par un script pour la route en lacets : le vieux L de gravier redevenu de l'herbe, la haie de `HAIE_X`. La route,
sa lisière et la haie du bois ne sont PAS dans le plan : `blocs.plan_du_bloc` les cuit par-dessus, sans un dé.
"""

from .. import carte

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AA,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AAb,,,A,A,AA,sssssssssss,AA,,,,,,,,,,,,bA,,,,,,,,,,,,T,,T,,T,,T,,,,,T,,T,,T,,T,A",
    "A,,,,,,,,,ssss~~~~~~~~~ssss,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,,,,,sss~~~~~~~~~~~~~~~sss,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,ss~~~~~~~~~~~~~~~~~~~ss,,,,,,,,,,,b,,,,,,,,,,,AT,,T,,T,,T,,,T,,T,,T,,T,,A",
    "AA,,,,ss~~~~~~~~~~~~~~~~~~~~~ss,,,,,,,,,,,,,,A,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,sss~~~~~~~~~~~~~~~~~~~~~sss,,,,,,,A,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,,ss~~~~~~~~~~~~~~~~~~~~~~~ss,,,,,,,,,,,b,,,,,,,,,T,,T,,T,,T,,,,,T,,T,,T,,T,A",
    "A,,,,sss~~~~~~~~~~~~~~~~~~~~~sss,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,,,ss~~~~~~~~~~~~~~~~~~~~~ss,,,,,,,PPPPPPPPPPP,,,,A,,,,PPPPPPPPPPPPPP,,,,,,,A",
    "A,,,,,,ss~~~~~~~~~~~~~~~~~~~ss,,,,,,,,PPPPPPPPPPP,,,,A,,,,PPPPPPPPPPPPPP,LLLLL,A",
    "AA,,,,b,sss~~~~~~~~~~~~~~~sss,,,,,,,,,PPPPPPPPPPP,,,,A,,,,PPPPPPPPPPPPPP,,,,,,,A",
    "A,,,,,,,,,ssss~~~QQQ~~~ssss,,,,,,,,,,,PPPPPPPPPPP,,,,LLLL,PPPPPPPPPPPPPP,,,,,,,A",
    "AA,,b,,,,,,,,ssssgggssss,,,,,,,,,,,,,,PPPPPPPPPPP,,,,A,,,,PPPPPPPPPPPPPP,LLLLL,A",
    "A,,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,,,HWWFFDFFWWH,,,,A,,,,HWWFFFDFFFFWWH,,,,,,,A",
    "AA,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,,A,,,,,,,,,,g,,,,,,,,,,,,,,A",
    "A,,,,,,,A,,,b,,,,ggg,,,,,,,,,,,,,,,,,,,,,,,g,ppp,,,,,A,,,,,,,,,,g,,,,,,,,,,,,,,A",
    "AAA,,,,,,,,,,,,,,ggg,,,,,b,,,,,A,,,,,,,,,,,g,ppp,,,,,A,,,,,,,,,,g,,=,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,g,,,,,,,,,,,,,,A",
    "AA,,,,,,,,,,,,b,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,g,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,A,,,,,,,,,,,,,b,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,g,,,,,,,,,,,,,,A",
    "AA,b,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,,,,,,,,",
    "A,,,,,,,,,,,,,,,b,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
    "A,,,,b,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,gg,,,,,,,,,,,,,,,,",
    "AA,,,,,,,,,,A,,,,,b,,,,,,,,,,,,,,,,,,,,,,A,,,E,,,,,E,,,E,,,,,gg,,,E,,,E,,E,,,E,A",
    "A,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,b,,,A,,,,,,,,,,,,,,,,,,,,,,,,,gg,,,,,,,,,,,,,,,,A",
    "AA,,,,,b,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,ggggggggggggggggggggggggggggg,,,A",
    "A,,,,,,,,,,,,,,,,,,,b,,A,,,,,,,,,,,,,,,,,,,,,,,ggggggggggggggggggggggggggggg,,,A",
    "AA,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,b,,,,,,,,,,,,,gg,,,,,,,,,,,,,,,,,,,,,,,,,gg,,,A",
    "A,,,,,,,,b,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,gg,E,,E,,,E,,E,,E,,E,,,E,,,gg,,,A",
    "AA,,,A,,,,,,,,,,,,,,,,b,,,,,,,,,,,A,,,,,,,,,,E,gg,,,,,,E,,,,,,,,,,,,E,,,E,gg,,EA",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,b,,,,,,,,,,,gg,E,,,,,,E,,E,,,E,,,,,E,,,gg,,,A",
    "AA,,,,,,,,,b,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,gg,,,E,,,,,,,,,E,,,E,,,,,E,gg,,,A",
    "A,,,,,,,,,,,,,,,A,,,,,,,b,,,,,,,,,,,,,,,,,,,,,,gg,,,,,E,,E,,,,,,E,,,E,,,,,gg,,,A",
    "AA,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,b,A,,,,,E,gg,E,,,,,,,,E,,,,,,E,,,,,E,gg,,EA",
    "A,,,A,,,,,,,,b,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,gg,,,E,,E,,,,,E,,E,,,E,,,,,gg,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,bA,,,,,,,,,,,,,,,,,,,gg,E,,,,,,E,,,,,,,,E,,,E,,,gg,,,A",
    "A,b,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,b,,,,,,,gg,,,E,,E,,,E,,E,,,,,E,,,E,gg,,,A",
    "AA,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,E,gg,E,,,,,,E,,,,,,E,,,,,E,,,gg,,EA",
    "A,,,,,,,,A,,,,,,,,,,,,,,,,,,b,,,,,,,,,A,,,,,,,,gg,,,,,,,,,,,,,,,,,,,,,,,,,gg,,,A",
    "AA,Ab,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,b,,,,,ggggggggggggggggggggggggggggg,,,A",
    "A,,,,,,,,,,,,,,,,b,,,,,,,,A,,,,,,,,,,,,,,,,,,,,ggggggggggggggggggggggggggggg,,,A",
    "AA,,,,,,,,,,,,,,,,,,A,,,,,,,,,b,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,b,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,,,,,A,,,,,,,,,,b,,,,,,,,,,,,,,,,,A,,,,,,,E,,,,E,,,E,,,E,,,,E,,,E,,,E,,,,,E,A",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
    "b": (",", "buisson"),
    # L'ÉRABLIÈRE (docs/jalons/la-cabane-a-sucre-pour-vrai.md) : au nord de la cabane, les érables en
    # TUBULURE (`T`, leur chalumeau et la ligne bleue d'arbre en arbre, peinte par `Cabane`) ; au sud, le long
    # du sentier de la calèche, les érables aux CHAUDIÈRES (`E`, le seau de tôle au couvercle pointu).
    "T": (",", "erable_tube"),
    "E": (",", "erable_seau"),
    # Les cordes de bois de l'évaporateur, contre la cabane ; la table de tire, dans la cour.
    "L": (",", "corde_bois"),
    "=": (",", "table_tire"),
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
""", points=(carte._pt("lit", 2, 2), carte._pt("coffre", 1, 3), carte._pt("garde_robe", 9, 1),
             # Le catalogue Beausoleil, sur la table de pin : les meubles du chalet (`decoration.py`).
             carte._pt("catalogue", 2, 5)),
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

#: LA CABANE, POUR VRAI (docs/jalons/la-cabane-a-sucre-pour-vrai.md) — ce que `static/js/cabane.js` anime.
#:
#: ⚠️ `caleche` : le sentier, en COUTURES de tuiles (le sentier fait deux tuiles de large, la calèche roule sur
#: la couture du milieu), une boucle fermée qui part de l'arrêt et y revient. Elle attend `attente` images à
#: l'arrêt, puis fait le tour à `vitesse` pixels par image — sans un dé ; `Cabane` arrondit les coins. `pancarte` : la
#: tuile de son poteau de GAUCHE — l'écriteau s'étend vers l'est, dans l'herbe, contre le passage qui descend de la
#: cabane (colonnes 61-62), les pieds au bord du sentier.
#: ⚠️ `tubulure` : le tuyau maître descend la colonne `x` du rang `de` jusqu'au toit de la cabane (`a`) ; chaque
#: rang d'érables en tubulure y court, d'arbre en arbre.
#: ⚠️ `gens` : qui est à la cabane au temps des sucres, pendant les heures du comptoir `sucre` — le tireur
#: derrière la table, ceux qui roulent leur tire, le musicien à la porte, ceux qui attendent la calèche.
CABANE = {
    "caleche": {"chemin": [[60, 30], [48, 30], [48, 44], [75, 44], [75, 30], [60, 30]],
                "attente": 420, "vitesse": 0.75, "pancarte": [63, 28]},
    "tubulure": {"x": 65, "de": 3, "a": 11},
    "table": {"x": 67, "y": 19},
    "gens": [
        {"qui": "tireur", "arch": "commis", "x": 67, "y": 18, "face": "bas"},
        {"qui": "client", "arch": "passante", "x": 66, "y": 20, "face": "haut"},
        {"qui": "client", "arch": "ouvrier", "x": 68, "y": 20, "face": "haut"},
        {"qui": "client", "arch": "ado", "x": 69, "y": 19, "face": "gauche"},
        {"qui": "musicien", "arch": "musicien", "x": 61, "y": 18, "face": "bas"},
        {"qui": "client", "arch": "dame", "x": 56, "y": 18, "face": "droite"},
        {"qui": "client", "arch": "passant", "x": 57, "y": 18, "face": "gauche"},
        {"qui": "client", "arch": "promeneur", "x": 66, "y": 28, "face": "gauche"},
        {"qui": "client", "arch": "banlieusard", "x": 67, "y": 28, "face": "gauche"},
    ],
}

#: ⚠️ LA ROUTE EN LACETS (docs/jalons/une-route-en-lacets-vers-le-chalet.md) — Martin (30 sept. 2026) :
#: « Montée vers le chalet », « Lacets dans le bois », « Bois dense + route roulante ». De l'entrée est, devant
#: l'allée de la cabane, on file à l'ouest jusqu'à l'érable (45, 27) qu'on contourne, on plonge au sud dans le
#: bois, on longe le fond du rang, on remonte à l'ouest (le sommet frôle le bord : sa haie y touche les arbres
#: de la bordure, sinon on filerait par le bord jusqu'au lac), et on arrive au chalet PAR L'OUEST, devant sa
#: cour, au pied de son allée (x 43) : au bout du chemin.
#: ⚠️ LE BOIS : la haie de la route ne pousse que dans ses rectangles. Le premier ferme le côté du chalet au-dessus
#: de la route, de l'allée du chalet à `HAIE_X` (rangées 20-22) ; le second, le sud-ouest, s'arrête à x = 46 —
#: plus à l'est, un arbre tomberait à moins de 18 px du sentier de la calèche. La haie de `HAIE_X`, tracée
#: dans le plan du bord nord à la rangée 22, sépare la cabane du chalet.
HAIE_X = 53
CHEMIN = {
    "points": [(80, 24.5), (66, 24.5), (52, 24.5), (45.5, 24.5), (42.67, 25.67), (41.5, 28.5), (41.5, 33),
               (41, 38), (36, 42.5), (26, 43.5), (16, 42), (9, 37), (6.3, 31), (9, 25), (14, 20), (20, 18.5),
               (30, 18.5), (38, 18.5), (41.5, 18.5)],
    "largeur": 3, "sol": "§", "arbre": "A", "haie": 2,
    "bois": [[42, 20, HAIE_X - 41, 3], [1, 21, 46, 27]],
}

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
    # ⚠️ LE 4 ROUES DU CHALET (docs/jalons/les-4-roues.md) : le tien, sur l'herbe à côté de la place du char —
    # à plus de 48 px d'elle, sinon la planque le garde pour SON char (`garderLesCharsDesPlanques`).
    "quatre_roues": {"x": 52, "y": 19},
    # La cheminée du chalet, au-dessus de son foyer : elle fume (`Blocs.dessiner`). Celles de la CABANE ne
    # fument qu'au temps des sucres, quand on fait bouillir (`sucres`) : la cheminée de tôle de l'évaporateur,
    # et le lanterneau du faîte d'où sort la vapeur blanche (`genre`, `Blocs.dessinerCheminees`).
    "cheminees": [{"x": 43, "y": 12, "l": 2},
                  {"x": 69, "y": 11, "l": 1, "genre": "tole", "sucres": True},
                  {"x": 62, "y": 11, "l": 3, "genre": "lanterneau", "sucres": True}],
    "chemins": [CHEMIN],
    # Les fenêtres de la cabane, devant sa façade.
    "lampes": [{"x": 59, "y": 17, "r": 26, "c": "fenetre"}, {"x": 70, "y": 17, "r": 26, "c": "fenetre"}],
    "cabane": CABANE,
}
