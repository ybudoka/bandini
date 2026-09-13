"""La carte de Baie-des-Brumes — un plan de blocs, des gabarits, un generateur.

Le Faubourg n'est pas dessine tuile par tuile : il est DECRIT par un plan de
blocs et rebati par `generer(plan, graine)`. Six lignes qu'on relit d'un coup
d'oeil valent mieux que 112 lignes de 157 glyphes.

    minuscule = quartier ordinaire   c commerces · h habitations · g gang
                                     p parc · o place · q quai · ~ eau
    MAJUSCULE = batiment garanti     T terminus · M armurerie · A vetements
                                     G garage · K planque · P poste · H hopital
                                     B bar · C casse-croute
    < et ^    = ce bloc est AVALE par son voisin de l'ouest ou du nord

⚠️ **Rien n'est regulier, et c'est voulu.** Une ville en damier parfait n'a pas
de reperes : tous les coins s'y ressemblent et on s'y perd sans jamais la
connaitre. Trois sources d'irregularite se combinent ici :

1. **La trame** : chaque colonne de blocs a sa largeur, chaque rangee sa
   hauteur, chaque rue sa largeur (8 = boulevard a 4 voies, 6 = rue a 2 voies).
2. **Les superblocs** : `<` et `^` fusionnent des blocs, ce qui EFFACE la rue
   entre eux — d'ou des rues qui s'arretent en T, un parc a cheval sur deux
   blocs, une cour de gang qui en occupe quatre.
3. **Les parcelles** : l'interieur d'un ilot est redecoupe au hasard (BSP) en
   parcelles inegales ; chacune recoit un batiment a la profondeur variable
   (parfois en U autour d'une cour), un terrain vague, un stationnement ou un
   jardin. Deux ilots ne se ressemblent jamais.

Le champ `voie` dit ou va un vehicule depuis chaque tuile : `> < ^ v` une voie,
`+` un croisement (on en sort par ou on veut, sauf a contresens), `S` une ligne
d'arret — sa direction est dans `arrets`, pas dans le glyphe — et `.` pas de
route.

⚠️ Les rues du pourtour ne sont jamais avalees : chaque tuile de rue du bord
tombe donc dans un croisement, et AUCUNE fleche ne pointe hors carte. C'est ce
qui rend les voies fortement connexes (juge `voies_bloquees`).

Forme servie (`exporter()`) :
    largeur, hauteur, tuile_px   en tuiles
    sol                          lignes de glyphes (LEGENDE)
    voie                         lignes de direction routiere (VOIES)
    arrets                       "x,y" -> direction de la ligne d'arret
    intersections                boites de croisement (feux, plus tard)
    legende                      glyphe -> proprietes (solide, route, ...)
    portes, lampes, decor        listes de positions en tuiles
    zones                        rectangles nommes (district, gang, port)
    points_interet               lieux nommes (planque, hopital, magasins...)
    apparition                   ou le joueur commence
    interieurs                   petites cartes, meme forme, par slug
"""

from __future__ import annotations

from . import devantures as devantures_mod
from . import magasins

TUILE_PX = 16

#: Ce qu'il faut AUTOUR d'une rampe pour qu'elle serve, en tuiles : de l'ELAN
#: avant le pied, de la RECEPTION apres la levre.
#: ⚠️ C'est la mesure de « accessible », et elle ne se choisit pas au gout :
#: elle se CALCULE sur la physique. Le defi du Grand Saut demande 60 px de vol
#: en moto ; or une moto partie d'arret vole 54 px avec sept tuiles d'elan et
#: 68 px avec dix (mesure : `vehicules.PHYSIQUE`, rampe_impulsion 0,42 et
#: gravite 0,18). A sept, on aurait donc pose des tremplins sur lesquels le
#: defi du jeu est IMPOSSIBLE. La reception, elle, doit couvrir le vol : 68 px
#: font quatre tuiles et demie.
ELAN_RAMPE = 10
RECEPTION_RAMPE = 6

#: Solidite : 0 libre, 1 mur (bloque tout), 2 eau (bloque sauf les bateaux),
#: 3 basse (bloque les vehicules, pas les pietons).
LEGENDE: dict[str, dict] = {
    ".": {"nom": "trottoir", "trottoir": True},
    ",": {"nom": "herbe", "herbe": True},
    "x": {"nom": "ruelle", "ruelle": True},
    "s": {"nom": "sable"},
    "Q": {"nom": "quai"},
    "~": {"nom": "eau", "solide": 2},
    "#": {"nom": "asphalte", "route": True},
    "-": {"nom": "ligne de voie est-ouest", "route": True},
    "|": {"nom": "ligne de voie nord-sud", "route": True},
    "+": {"nom": "ligne centrale est-ouest", "route": True},
    "*": {"nom": "ligne centrale nord-sud", "route": True},
    "=": {"nom": "passage piéton est-ouest", "route": True, "trottoir": True},
    ":": {"nom": "passage piéton nord-sud", "route": True, "trottoir": True},
    "p": {"nom": "stationnement", "route": True, "stationnement": True},
    # ⚠️ Les quatre glyphes de CASE vivent dans `sol`, pas dans `voie` : ici la
    # fleche ne dit pas ou roule un char, elle dit ou pointe le NEZ de l'auto
    # garee. Le fond de la case est donc du cote de la fleche, et l'allee de
    # manoeuvre de l'autre.
    "^": {"nom": "case de stationnement, nez au nord", "route": True,
          "stationnement": True, "case": "N"},
    "v": {"nom": "case de stationnement, nez au sud", "route": True,
          "stationnement": True, "case": "S"},
    "<": {"nom": "case de stationnement, nez a l'ouest", "route": True,
          "stationnement": True, "case": "O"},
    ">": {"nom": "case de stationnement, nez a l'est", "route": True,
          "stationnement": True, "case": "E"},
    "I": {"nom": "ilot de stationnement", "trottoir": True},
    # ⚠️ Une rampe, c'est DEUX tuiles : le PIED ou l'on monte et la LEVRE
    # d'ou l'on decolle. Le dessin lit la paire pour savoir dans quel sens
    # ca grimpe (`varianteDeRampe`, monde.js) — un glyphe seul ne dirait rien,
    # et c'est pour ca que l'ancienne rampe n'avait l'air de rien.
    "R": {"nom": "pied de rampe", "route": True, "rampe": True},
    "J": {"nom": "lèvre de rampe", "route": True, "rampe": True},
    "B": {"nom": "toit de tole", "solide": 1},
    "E": {"nom": "toit d'ardoise", "solide": 1},
    "O": {"nom": "toit de gravier", "solide": 1},
    "F": {"nom": "façade", "solide": 1},
    "W": {"nom": "vitrine", "solide": 1, "lampe": True},
    "D": {"nom": "porte", "solide": 1, "porte": True},
    "d": {"nom": "porte condamnée", "solide": 1},
    "G": {"nom": "porte de garage", "solide": 1, "garage": True},
    "b": {"nom": "borne-fontaine", "solide": 3},
    "f": {"nom": "clôture", "solide": 3},
    "t": {"nom": "plancher"},
    "c": {"nom": "comptoir", "solide": 3},
}

VOIES = {".", ">", "<", "^", "v", "+", "S"}

#: Le gabarit d'un stationnement, en tuiles. Une case fait UNE tuile de large et
#: DEUX de creux : c'est exactement l'auto (32 x 16 px), pare-chocs compris.
#: Une allee de manoeuvre en fait deux — de quoi se croiser et braquer.
CASE_CREUX = 2
ALLEE = 2

PAS = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}

TOITS = "BEO"

#: ⚠️ Les genres d'ilot qui ont pignon sur rue. Pas les maisons ni la banlieue
#: (on n'accroche pas une enseigne sur un bungalow), pas les cours de gang.
GENRES_COMMERCANTS = frozenset({"commerces", "hangars", "industriel"})

# --- Les cinq districts -----------------------------------------------------

#: ⚠️ La ville est UNE SEULE grille de blocs (20 colonnes, 12 rangees) ; un
#: district en occupe un rectangle. C'est ce qui la garde d'un seul tenant : les
#: arteres traversent les frontieres, aucune rue ne s'arrete parce qu'on a
#: change de quartier, et il n'y a rien a charger en roulant. Un district se
#: reconnait a trois choses, et aucune n'est un decor : la LARGEUR de ses
#: colonnes, ses FUSIONS (`<` `^`, qui effacent les rues et font les gros
#: blocs), et le CONTENU de ses ilots.
#:
#: ⚠️ Un district ne fusionne JAMAIS par-dessus sa frontiere : pas de `<` en
#: premiere colonne, pas de `^` en premiere rangee (juge `_assembler`). Sans
#: cette regle, deplacer un quartier en casserait un autre.
DISTRICTS: tuple[dict, ...] = (
    # Le Faubourg — le quartier de la v1, intact. Trame serree, blocs courts,
    # la cour des Cravates au centre. C'est ici qu'on debarque de l'autobus.
    {"slug": "faubourg", "nom": "Le Faubourg", "bx": 5, "by": 0,
     "gang": "cravates", "gang_nom": "Les Cravates", "brume": True,
     "pietons": 26, "vehicules": 12, "police": 2, "rythme": (0.75, 1.0, 1.0),
     "plan": ("Tccchhhh",
              "cMck<hAh",
              "ccGKohhh",
              "PcBcg<hh",
              "cCcc^^hH",
              "~~qqcccc")},
    # Les Erables — la banlieue. Colonnes larges, maisons detachees sur grandes
    # parcelles, deux parcs, un depanneur, et les Chevreuils qui tournent en
    # char le soir faute de mieux.
    {"slug": "erables", "nom": "Les Érables", "bx": 0, "by": 0,
     "gang": "chevreuils", "gang_nom": "Les Chevreuils", "brume": False,
     "pietons": 14, "vehicules": 7, "police": 1, "rythme": (0.5, 1.1, 0.9),
     "plan": ("mmmpm",
              "m<m^m",
              "Dmmmm",
              "mm<mm",
              "ccgmm",
              "mmm<m")},
    # La Shop — l'industriel. Des blocs de 2 x 2 partout : presque pas de rues,
    # des entrepots gros comme un pate de maisons, des stationnements vides.
    # Deserte la nuit, et c'est exactement ce qui la rend inquietante.
    {"slug": "shop", "nom": "La Shop", "bx": 13, "by": 0,
     "gang": "boulonneux", "gang_nom": "Les Boulonneux", "brume": False,
     "pietons": 11, "vehicules": 9, "police": 1, "rythme": (0.15, 1.3, 0.6),
     "plan": ("U<i<i<p",
              "^<^<^<^",
              "i<g<i<i",
              "^<^<^<^",
              "i<Y<i<c",
              "^<^<^<^")},
    # Les Quais — le port. Blocs LONGS d'est en ouest (des hangars de trois
    # blocs de large), une rangee de quais, l'eau au sud. Ca grouille au matin,
    # ca se vide a la noirceur — sauf la Brume.
    {"slug": "quais", "nom": "Les Quais", "bx": 0, "by": 6,
     "gang": "morues", "gang_nom": "Les Morues", "brume": True,
     "pietons": 20, "vehicules": 8, "police": 1, "rythme": (0.7, 1.4, 0.9),
     "plan": ("cc<c<<c",
              "w<<w<<c",
              "L<g<w<c",
              "w<<N<<c",
              "q<<q<<q",
              "~<<~<<~")},
    # La baie — pas un quartier : l'eau. Un seul bloc fusionne de 7 x 6, ce qui
    # efface toutes les rues qui la traverseraient. Le traversier y passera (v2,
    # M12) ; pour l'instant on la longe.
    {"slug": "baie", "nom": "La baie", "bx": 7, "by": 6, "eau": True,
     "gang": None, "gang_nom": None, "brume": False,
     "pietons": 0, "vehicules": 0, "police": 0, "rythme": (1.0, 1.0, 1.0),
     "plan": ("~<<<<<<",
              "^<<<<<<",
              "^<<<<<<",
              "^<<<<<<",
              "^<<<<<<",
              "^<<<<<<")},
    # La Pointe — le parc au bout de la ville. Un chenal la coupe du reste :
    # UN pont, et rien d'autre. Des bois, des sentiers, un phare, quatre
    # maisons au bout, et les Skateux qui tiennent le stationnement.
    {"slug": "pointe", "nom": "La Pointe", "bx": 14, "by": 6,
     "gang": "skateux", "gang_nom": "Les Skateux", "brume": False,
     "pietons": 12, "vehicules": 4, "police": 1, "rythme": (0.35, 0.9, 1.2),
     "plan": ("~<<<<<",
              "n<<<nc",
              "^<<<^c",
              "n<<<^V",
              "^<<<^g",
              "~<<~<<")},
)

#: ⚠️ Aucune colonne n'a la largeur de sa voisine, aucune rangee la hauteur de
#: la sienne : c'est la premiere source d'irregularite, et la moins chere. Les
#: largeurs sont groupees par district — la banlieue et le port ont des blocs
#: larges, le Faubourg les siens (inchanges), l'industriel les plus gros.
COLONNES = (16, 13, 18, 14, 17,              # Les Érables / Les Quais
            13, 9, 12, 16, 10, 14, 9, 12,    # Le Faubourg (v1, intact)
            17, 13, 19, 14, 12, 16, 13)      # La Shop / La Pointe
RANGEES = (9, 12, 8, 11, 9, 13,              # la bande nord
           11, 12, 9, 11, 8, 10)             # la bande sud

#: La largeur de chaque rue, trottoirs compris. 8 = boulevard (4 voies),
#: 6 = rue (2 voies). Il y a une rue de plus que de blocs dans chaque sens.
RUES_V = (8, 6, 6, 8, 6,
          8, 6, 8, 6, 6, 8, 6, 6, 8,
          6, 8, 6, 6, 8, 6, 8)
RUES_H = (8, 6, 8, 6, 8, 6, 8,
          6, 8, 6, 6, 6, 8)

TROTTOIR = 2
GRAINE = 20260912

#: Les ponts : les seules rues qu'on construit PAR-DESSUS l'eau. Un pont est
#: un segment de rue ("v" verticale ou "h" horizontale) designe par sa rue et
#: la rangee (ou la colonne) qu'il longe — ici le seul lien vers La Pointe.
PONTS: frozenset = frozenset({("v", 17, 6)})

#: Les batiments garantis : un par majuscule du plan. `interieur` doit exister
#: dans INTERIEURS (juge `test_les_portes_menent_a_un_interieur`).
SPECIAUX: dict[str, dict] = {
    "T": {"slug": "terminus", "nom": "Terminus Baie-des-Brumes", "interieur": "terminus"},
    "M": {"slug": "armurerie", "nom": "Chez Gus", "interieur": "armurerie"},
    "A": {"slug": "vetements", "nom": "Boutique Rosa", "interieur": "vetements"},
    "G": {"slug": "garage", "nom": "Garage Rocco Bandini", "interieur": "garage", "porte_garage": True},
    "K": {"slug": "planque", "nom": "La planque de Rocco", "interieur": "planque"},
    "P": {"slug": "poste", "nom": "Poste de police", "interieur": "poste"},
    "H": {"slug": "hopital", "nom": "Hôpital de Baie-des-Brumes", "interieur": "hopital"},
    "B": {"slug": "bar", "nom": "Bar Le Brouillard", "interieur": "bar"},
    "C": {"slug": "casse_croute", "nom": "Casse-croûte du Faubourg", "interieur": "casse_croute"},
    # v2 / M8 — un point d'arret par district : on ne traverse pas la ville
    # pour un hot-dog ou pour sauver sa partie.
    "D": {"slug": "depanneur", "nom": "Dépanneur Chez Ti-Paul", "interieur": "depanneur",
          "genre": "banlieue"},
    "L": {"slug": "hotel", "nom": "Hôtel Bandini", "interieur": "hotel"},
    "N": {"slug": "cantine", "nom": "Cantine des Quais", "interieur": "cantine",
          "genre": "hangars"},
    "U": {"slug": "usine", "nom": "Usine Prévost", "interieur": "usine",
          "genre": "industriel"},
    "V": {"slug": "phare", "nom": "Le phare de La Pointe", "interieur": "phare",
          "genre": "banlieue"},
    # v2 / M9 — le lot de la fourriere. Ce n'est pas un ilot bati : c'est une
    # cour d'asphalte cloturee avec une guerite, et `_fourriere()` la pose.
    "Y": {"slug": "fourriere", "nom": "Fourrière municipale", "interieur": "fourriere",
          "genre": "industriel"},
}

FUSIONS = {"<": (-1, 0), "^": (0, -1)}

#: Les glyphes de plan qui sont de l'eau — une rue dont TOUS les blocs voisins
#: sont de l'eau est noyee : elle n'est pas batie, et personne n'y roule.
EAUX = "~"


def _assembler(districts: tuple[dict, ...]) -> tuple[str, ...]:
    """Le plan de la ville : les districts poses cote a cote sur la grille.

    Leve ValueError si deux districts se marchent dessus, s'il reste un trou,
    ou si une fusion sort d'un district (elle irait chercher son maitre chez le
    voisin, et deplacer un quartier en casserait un autre).
    """
    nc = max(d["bx"] + len(d["plan"][0]) for d in districts)
    nr = max(d["by"] + len(d["plan"]) for d in districts)
    grille: list[list[str | None]] = [[None] * nc for _ in range(nr)]
    for district in districts:
        plan = district["plan"]
        largeur = len(plan[0])
        for j, ligne in enumerate(plan):
            if len(ligne) != largeur:
                raise ValueError(f"{district['slug']} : plan pas rectangulaire")
            for i, glyphe in enumerate(ligne):
                if glyphe == "<" and i == 0:
                    raise ValueError(f"{district['slug']} : fusion vers l'ouest hors du district")
                if glyphe == "^" and j == 0:
                    raise ValueError(f"{district['slug']} : fusion vers le nord hors du district")
                x, y = district["bx"] + i, district["by"] + j
                if grille[y][x] is not None:
                    raise ValueError(f"deux districts sur le bloc {(x, y)}")
                grille[y][x] = glyphe
    for y, ligne in enumerate(grille):
        for x, glyphe in enumerate(ligne):
            if glyphe is None:
                raise ValueError(f"aucun district sur le bloc {(x, y)}")
    return tuple("".join(ligne) for ligne in grille)


PLAN: tuple[str, ...] = _assembler(DISTRICTS)


def district_par_slug(slug: str) -> dict | None:
    for district in DISTRICTS:
        if district["slug"] == slug:
            return district
    return None


class Des:
    """Un generateur minuscule (LCG) — deterministe et lisible, sans `random`.

    Le hasard de la ville doit donner LA MEME ville a chaque demarrage du
    serveur : `random` suit un etat global que n'importe quel import pourrait
    bouger. Ici, la graine entre et rien d'autre.
    """

    def __init__(self, graine: int) -> None:
        self.etat = graine & 0xFFFFFFFF

    def suivant(self) -> int:
        self.etat = (self.etat * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.etat

    def flottant(self) -> float:
        return self.suivant() / 4294967296.0

    def entier(self, a: int, b: int) -> int:
        """Entre a et b, bornes comprises."""
        if b <= a:
            return a
        return a + self.suivant() % (b - a + 1)

    def chance(self, p: float) -> bool:
        return self.flottant() < p

    def choix(self, options):
        return options[self.suivant() % len(options)]


def _coupe(largeur: int, vertical: bool) -> list[tuple[str, str]]:
    """La coupe d'une rue : (glyphe, fleche) pour chaque tuile de sa largeur.

    ⚠️ Le marquage se peint sur le BORD de la tuile : la ligne centrale tombe
    donc ENTRE les deux sens, et non au milieu d'une voie.
    """
    voies = largeur - 2 * TROTTOIR
    moitie = voies // 2
    sortie = []
    for d in range(largeur):
        if d < TROTTOIR or d >= largeur - TROTTOIR:
            sortie.append((".", "."))
            continue
        k = d - TROTTOIR
        if vertical:
            glyphe = "#" if k == 0 else ("*" if k == moitie else "|")
            sortie.append((glyphe, "v" if k < moitie else "^"))
        else:
            glyphe = "#" if k == 0 else ("+" if k == moitie else "-")
            sortie.append((glyphe, "<" if k < moitie else ">"))
    return sortie


def regions_du_plan(plan: tuple[str, ...]) -> dict[tuple[int, int], tuple[int, int]]:
    """Pour chaque bloc, le bloc « maitre » de sa region (lui-meme, ou celui
    qui l'a avale). Leve ValueError si une fusion ne fait pas un rectangle."""
    maitre: dict[tuple[int, int], tuple[int, int]] = {}
    for by, ligne in enumerate(plan):
        for bx, glyphe in enumerate(ligne):
            if glyphe in FUSIONS:
                dx, dy = FUSIONS[glyphe]
                voisin = (bx + dx, by + dy)
                if voisin not in maitre:
                    raise ValueError(f"fusion sans voisin en {(bx, by)}")
                maitre[(bx, by)] = maitre[voisin]
            else:
                maitre[(bx, by)] = (bx, by)
    groupes: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for cellule, chef in maitre.items():
        groupes.setdefault(chef, []).append(cellule)
    for chef, cellules in groupes.items():
        xs = {c[0] for c in cellules}
        ys = {c[1] for c in cellules}
        if len(cellules) != len(xs) * len(ys) or max(xs) - min(xs) + 1 != len(xs) \
                or max(ys) - min(ys) + 1 != len(ys):
            raise ValueError(f"la region {chef} n'est pas un rectangle : {sorted(cellules)}")
    return maitre


class _Chantier:
    """L'echafaudage : la trame, puis les rues, puis les ilots, puis le decor."""

    def __init__(self, plan: tuple[str, ...], graine: int) -> None:
        self.plan = plan
        self.nc = len(plan[0])
        self.nr = len(plan)
        if len(COLONNES) != self.nc or len(RANGEES) != self.nr:
            raise ValueError("COLONNES/RANGEES ne collent pas au plan")
        if len(RUES_V) != self.nc + 1 or len(RUES_H) != self.nr + 1:
            raise ValueError("il faut une rue de plus que de blocs dans chaque sens")
        self.maitre = regions_du_plan(plan)

        # La trame : ou commence chaque rue et chaque bloc.
        self.xr, self.xb = [], []
        x = 0
        for i in range(self.nc):
            self.xr.append(x)
            x += RUES_V[i]
            self.xb.append(x)
            x += COLONNES[i]
        self.xr.append(x)
        self.largeur = x + RUES_V[self.nc]
        self.yr, self.yb = [], []
        y = 0
        for j in range(self.nr):
            self.yr.append(y)
            y += RUES_H[j]
            self.yb.append(y)
            y += RANGEES[j]
        self.yr.append(y)
        self.hauteur = y + RUES_H[self.nr]

        self.sol = [[","] * self.largeur for _ in range(self.hauteur)]
        self.voie = [["."] * self.largeur for _ in range(self.hauteur)]
        #: De quoi boucher une poche injoignable, par tuile (voir boucher_les_poches).
        self.bouchon = [["B"] * self.largeur for _ in range(self.hauteur)]
        self.des = Des(graine)
        self.portes: list[dict] = []
        self.points: list[dict] = []
        self.decor: list[dict] = []
        self.fourriere: dict | None = None
        self.lampes: list[dict] = []
        self.intersections: list[dict] = []
        self.arrets: dict[str, str] = {}
        self.reserve: set[tuple[int, int]] = set()
        self.occupe: set[tuple[int, int]] = set()
        #: Les devantures (bandeau + nom + vitrines + pancarte) et les tags.
        #: ⚠️ Ce sont des COUCHES PEINTES : elles ne changent aucune solidite,
        #: donc aucun juge de circulation ni de connexite ne depend d'elles.
        self.devantures: list[dict] = []
        self.graffitis: list[dict] = []
        self.murs_tagges: set[tuple[int, int]] = set()
        #: ⚠️ Les devantures tirent dans LEUR PROPRE de. Avec le de commun, choisir
        #: un nom d'enseigne decalait toute la suite du hasard et deplacait des
        #: arbres a l'autre bout de la ville : une couche peinte ne doit pas
        #: bouger un seul mur. Cette graine-ci peut changer sans rien casser.
        self.des_devanture = Des(graine ^ 0x5EA51)
        #: Les rampes, meme regle du de separe : un tremplin de plus ne doit
        #: pas deplacer un arbre a l'autre bout de la ville.
        self.des_rampe = Des(graine ^ 0x5A17E)
        self.rampes: list[dict] = []
        self.rampes_proposees: list[dict] = []

    # --- Trame --------------------------------------------------------------

    def glyphe_bloc(self, bx: int, by: int) -> str:
        """Le glyphe qui REGNE sur ce bloc : le sien, ou celui qui l'a avale."""
        mx, my = self.maitre[(bx, by)]
        return self.plan[my][mx]

    def _noyee(self, voisins: list[tuple[int, int]]) -> bool:
        """Une rue dont TOUS les blocs voisins sont de l'eau : elle n'existe pas.

        ⚠️ C'est la regle qui fait la geographie. Une baie fermee par un
        superbloc n'aurait pas suffi : il faut aussi que la rue du pourtour
        s'arrete au bord de l'eau, et que le chenal de La Pointe coupe VRAIMENT
        le quartier. Une rue le long d'une rive (eau d'un bord, terre de
        l'autre) reste une rue — c'est le boulevard du bassin.
        """
        return all(self.glyphe_bloc(*bloc) in EAUX for bloc in voisins)

    def rue_v_existe(self, i: int, j: int) -> bool:
        """La rue verticale `i` longe-t-elle la rangee de blocs `j` ?"""
        if ("v", i, j) in PONTS:
            return True                      # un pont : la rue passe SUR l'eau
        voisins = ([(i - 1, j)] if i > 0 else []) + ([(i, j)] if i < self.nc else [])
        if self._noyee(voisins):
            return False
        if i <= 0 or i >= self.nc:
            return True                      # les rues du pourtour, jamais avalees
        return self.maitre[(i - 1, j)] != self.maitre[(i, j)]

    def rue_h_existe(self, i: int, j: int) -> bool:
        if ("h", i, j) in PONTS:
            return True
        voisins = ([(i, j - 1)] if j > 0 else []) + ([(i, j)] if j < self.nr else [])
        if self._noyee(voisins):
            return False
        if j <= 0 or j >= self.nr:
            return True
        return self.maitre[(i, j - 1)] != self.maitre[(i, j)]

    def bras(self, i: int, j: int) -> tuple[bool, bool, bool, bool]:
        """Les quatre bras du croisement (i, j) : nord, sud, ouest, est."""
        return (j > 0 and self.rue_v_existe(i, j - 1),
                j < self.nr and self.rue_v_existe(i, j),
                i > 0 and self.rue_h_existe(i - 1, j),
                i < self.nc and self.rue_h_existe(i, j))

    def eaux(self) -> None:
        """L'eau AVANT les rues : ce qu'aucune rue ne recouvrira reste mouille.

        Les segments noyes et les croisements entierement cernes d'eau sont
        peints ici ; `rues()` et `croisements()` repeignent par-dessus tout ce
        qui existe pour de vrai.
        """
        for j in range(self.nr):
            for i in range(self.nc + 1):
                if self.rue_v_existe(i, j):
                    continue
                voisins = ([(i - 1, j)] if i > 0 else []) + ([(i, j)] if i < self.nc else [])
                if not self._noyee(voisins):
                    continue                 # avalee par un superbloc : pas de l'eau
                self.rect(self.xr[i], self.yb[j], RUES_V[i], RANGEES[j], "~")
                self.bouchon_rect(self.xr[i], self.yb[j], RUES_V[i], RANGEES[j], "~")
        for j in range(self.nr + 1):
            for i in range(self.nc):
                if self.rue_h_existe(i, j):
                    continue
                voisins = ([(i, j - 1)] if j > 0 else []) + ([(i, j)] if j < self.nr else [])
                if not self._noyee(voisins):
                    continue
                self.rect(self.xb[i], self.yr[j], COLONNES[i], RUES_H[j], "~")
                self.bouchon_rect(self.xb[i], self.yr[j], COLONNES[i], RUES_H[j], "~")
        for j in range(self.nr + 1):
            for i in range(self.nc + 1):
                coins = [(bx, by) for bx, by in ((i - 1, j - 1), (i, j - 1), (i - 1, j), (i, j))
                         if 0 <= bx < self.nc and 0 <= by < self.nr]
                if not self._noyee(coins):
                    continue
                self.rect(self.xr[i], self.yr[j], RUES_V[i], RUES_H[j], "~")
                self.bouchon_rect(self.xr[i], self.yr[j], RUES_V[i], RUES_H[j], "~")

    def ponts(self) -> list[dict]:
        """Le tablier des ponts — repose APRES les ilots.

        ⚠️ L'ordre n'est pas negociable : un bloc d'eau fusionne repeint TOUT
        son rectangle, rues avalees comprises, et le pont se retrouverait au
        fond du chenal (vu en plein visage : la chaussee etait de l'eau, les
        fleches par-dessus, et La Pointe injoignable a pied).

        On ne touche qu'au SOL : les fleches et les lignes d'arret de `rues()`
        sont deja les bonnes, et les repeindre effacerait les `S`.
        """
        sortie = []
        for sens, i, j in sorted(PONTS):
            vertical = sens == "v"
            if vertical:
                x, y, largeur, hauteur = self.xr[i], self.yb[j], RUES_V[i], RANGEES[j]
                coupe = _coupe(largeur, True)
            else:
                x, y, largeur, hauteur = self.xb[i], self.yr[j], COLONNES[i], RUES_H[j]
                coupe = _coupe(hauteur, False)
            for dy in range(hauteur):
                for dx in range(largeur):
                    glyphe = coupe[dx if vertical else dy][0]
                    # Les trottoirs du pont sont des planches : on y marche,
                    # et ca ne ressemble pas a une rue ordinaire.
                    self.sol[y + dy][x + dx] = "Q" if glyphe == "." else glyphe
            sortie.append({"x": x, "y": y, "l": largeur, "h": hauteur, "sens": sens})
        return sortie

    def regions(self) -> list[tuple[str, int, int, int, int]]:
        """(glyphe, x, y, largeur, hauteur) de chaque ilot, rues avalees comprises."""
        groupes: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for cellule, chef in self.maitre.items():
            groupes.setdefault(chef, []).append(cellule)
        sortie = []
        for (bx, by), cellules in sorted(groupes.items()):
            bx1 = max(c[0] for c in cellules)
            by1 = max(c[1] for c in cellules)
            x0, y0 = self.xb[bx], self.yb[by]
            largeur = self.xb[bx1] + COLONNES[bx1] - x0
            hauteur = self.yb[by1] + RANGEES[by1] - y0
            sortie.append((self.plan[by][bx], x0, y0, largeur, hauteur))
        return sortie

    # --- Poser des tuiles ---------------------------------------------------

    def rect(self, x: int, y: int, largeur: int, hauteur: int, glyphe: str) -> None:
        for j in range(max(0, y), min(y + hauteur, self.hauteur)):
            for i in range(max(0, x), min(x + largeur, self.largeur)):
                self.sol[j][i] = glyphe

    def bouchon_rect(self, x: int, y: int, largeur: int, hauteur: int, glyphe: str) -> None:
        for j in range(max(0, y), min(y + hauteur, self.hauteur)):
            for i in range(max(0, x), min(x + largeur, self.largeur)):
                self.bouchon[j][i] = glyphe

    def marchable_en(self, x: int, y: int) -> bool:
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        return marchable(self.sol[y][x])

    def batiment_forme(self, tuiles: set[tuple[int, int]], vitrines: float = 0.0) -> list[tuple[int, int]]:
        """Peint un batiment de forme QUELCONQUE et rend ses tuiles de facade.

        ⚠️ La regle est purement locale : toute tuile dont la voisine du sud
        n'appartient pas au batiment est une facade. C'est ce qui fait marcher
        les formes en U et en L sans un seul cas particulier — on voit toujours
        le mur avant, jamais le dos d'un toit.
        """
        toit = self.des.choix(TOITS)
        facades = []
        for tx, ty in sorted(tuiles):
            if (tx, ty + 1) in tuiles:
                self.sol[ty][tx] = toit
            else:
                facades.append((tx, ty))
        for tx, ty in facades:
            coin = (tx - 1, ty) not in tuiles or (tx + 1, ty) not in tuiles
            self.sol[ty][tx] = "W" if (not coin and self.des.chance(vitrines)) else "F"
        return facades

    def poser_porte(self, facades: list[tuple[int, int]], special: dict | None = None,
                    proba: float = 0.65) -> tuple[int, int] | None:
        """Une porte sur la facade la plus au sud QUI DONNE SUR DU MARCHABLE.

        ⚠️ A appeler apres avoir pose TOUS les batiments de l'ilot : une facade
        peut se retrouver nez a nez avec le toit du voisin, et une porte qui
        ouvre sur un mur est une promesse qu'on ne tient pas.
        """
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
        if not candidats and special:
            # Un batiment garanti DOIT s'ouvrir : on lui degage son devant.
            tx, ty = max(facades, key=lambda t: (t[1], t[0]))
            if ty + 1 < self.hauteur:
                self.sol[ty + 1][tx] = "."
                candidats = [(tx, ty)]
        if not candidats:
            return None
        bas = max(ty for _, ty in candidats)
        rangee = sorted(c for c in candidats if c[1] == bas)
        px, py = rangee[len(rangee) // 2]
        if special:
            self.sol[py][px] = "D"
            self.portes.append({"x": px, "y": py, "interieur": special["interieur"],
                                "lieu": special["slug"]})
            self.points.append({"type": special["slug"], "slug": special["slug"],
                                "nom": special["nom"], "x": px, "y": py + 1})
            if special.get("porte_garage") and (px - 2, py) in facades:
                self.sol[py][px - 2] = "G"
        elif self.des.chance(proba):
            self.sol[py][px] = "d"
        else:
            return None
        for j in (1, 2):
            self.reserve.add((px, py + j))
        return px, py

    # --- Les devantures ------------------------------------------------------

    #: Quatre tuiles par defaut (64 px, seize lettres) ; cinq seulement pour
    #: faire tenir un nom long. Au-dela, l'enseigne avale la facade du voisin
    #: et deux commerces mitoyens n'en font plus qu'un.
    ENSEIGNE_MAX = 4
    ENSEIGNE_ETIREE = 5
    ENSEIGNE_MIN = 2

    def district_en(self, x: int, y: int) -> str:
        """Le quartier d'une tuile — il decide des noms sur les enseignes."""
        for district in DISTRICTS:
            dx, dy, dl, dh = self.rect_district(district)
            if dx <= x < dx + dl and dy <= y < dy + dh:
                return district["slug"]
        return DISTRICTS[0]["slug"]

    def _bande_de_facade(self, facades: set[tuple[int, int]],
                         ax: int, ay: int) -> tuple[int, int]:
        """Les facades d'un seul tenant autour de `ax` sur la rangee `ay`.

        ⚠️ Sur la MEME rangee et contigues : une facade en L a des morceaux de
        mur a deux hauteurs, et un bandeau a cheval sur les deux flotterait sur
        le toit.
        """
        gauche = ax
        while (gauche - 1, ay) in facades:
            gauche -= 1
        droite = ax
        while (droite + 1, ay) in facades:
            droite += 1
        return gauche, droite - gauche + 1

    def poser_devanture(self, facades: list[tuple[int, int]], ancre: tuple[int, int],
                        genre: str, special: dict | None = None) -> bool:
        """Un bandeau, un nom, des vitrines et une pancarte. Rend True si pose.

        ⚠️ Les tuiles du bandeau deviennent des VITRINES (`W`) : meme solidite
        que la facade, mais elles portent une lampe — une rue commercante
        s'allume la nuit, et c'est ce qui la distingue d'une rue d'entrepots.
        """
        ax, ay = ancre
        ensemble = set(facades)
        depart, dispo = self._bande_de_facade(ensemble, ax, ay)
        if dispo < self.ENSEIGNE_MIN:
            return False
        large = min(self.ENSEIGNE_MAX, dispo)
        # Centree sur la porte, puis ramenee dans la bande.
        x0 = min(max(ax - large // 2, depart), depart + dispo - large)

        if special is not None:
            choix = devantures_mod.enseigne_speciale(special["slug"], special["nom"])
            if choix is None:
                return False
            texte, genre_visuel = choix
        else:
            catalogue = devantures_mod.commerces_du_district(self.district_en(ax, ay))
            texte, famille = catalogue[self.des_devanture.entier(0, len(catalogue) - 1)]
            genre_visuel = devantures_mod.genre_index(famille)
        # ⚠️ Un nom trop long pour la bande n'est pas coupe : on elargit tant
        # qu'on peut, et si ca ne rentre toujours pas on renonce a l'enseigne
        # plutot que d'afficher « QUINCAILLE ».
        while (not devantures_mod.tient_en(texte, large, TUILE_PX)
               and large < min(dispo, self.ENSEIGNE_ETIREE)):
            large += 1
            x0 = min(max(ax - large // 2, depart), depart + dispo - large)
        if not devantures_mod.tient_en(texte, large, TUILE_PX):
            return False

        for i in range(large):
            tx = x0 + i
            if self.sol[ay][tx] == "F":
                self.sol[ay][tx] = "W"

        # La pancarte pend a un bout du bandeau, du cote ou il y a du trottoir.
        # ⚠️ Tiree au sort parmi les bouts possibles : en prenant toujours le
        # premier, toutes les pancartes de la ville pendaient a gauche.
        cotes = [sens for bout, sens in ((x0, -1), (x0 + large - 1, 1))
                 if self.marchable_en(bout, ay + 1)]
        pancarte = cotes[self.des_devanture.entier(0, len(cotes) - 1)] if cotes else 0

        # ⚠️ Ce qu'il y a SOUS le bandeau, tuile par tuile : « W » vitrine,
        # « D » porte, « d » porte condamnee, « G » porte de garage. Sans ce
        # masque, le peintre couvrait toute la bande de vitrine et la porte
        # disparaissait — on voyait le nom du commerce mais plus par ou entrer.
        motifs = "".join(self.sol[ay][x0 + i] for i in range(large))
        # ⚠️ Un commerce sans porte du tout n'existe pas. Un tiers des bandes
        # n'en avaient aucune (le batiment a tire « pas de porte ») : on en
        # PEINT une, marquee « P ». Elle ne touche pas au sol — c'est une porte
        # fermee, comme les « d », et elle ne promet donc rien qu'on ne tienne.
        if not set(motifs) & set("DdG"):
            # Contre le trottoir : on peint la porte la ou le joueur passe.
            visibles = [i for i in range(large) if self.marchable_en(x0 + i, ay + 1)]
            ou = visibles[len(visibles) // 2] if visibles else large // 2
            motifs = motifs[:ou] + "P" + motifs[ou + 1:]
        self.devantures.append({
            "x": x0, "y": ay, "l": large, "genre": genre_visuel,
            "texte": texte, "pancarte": pancarte, "motifs": motifs,
            "porte": 1 if special is not None else 0,
        })
        # ⚠️ Une vitrine eclaire le trottoir. Sans ca, la rue commercante et la
        # rangee d'entrepots sont le meme noir a minuit, et tout le travail des
        # enseignes disparaît la moitie du temps de jeu. Lueur BASSE et courte :
        # c'est un reflet sur le trottoir, pas un lampadaire.
        self.lampes.append({"x": x0 + large // 2, "y": ay + 1,
                            "r": 20 + 4 * large, "c": "vitrine"})
        for i in range(large):
            self.murs_tagges.add((x0 + i, ay))       # pas de graffiti sur une vitrine
        return True

    # --- Les graffitis -------------------------------------------------------

    def graffitis_sur_les_murs(self) -> None:
        """Des tags sur les murs nus. Le gang du coin signe chez lui.

        ⚠️ Jamais sur une devanture : un commerce lave sa vitrine. Les tags
        vont sur les facades restees nues (`F`) et sur les portes condamnees —
        c'est-a-dire exactement les murs dont personne ne s'occupe.
        """
        cours = [(z["x"], z["y"], z["l"], z["h"], z["gang"])
                 for z in self.zones() if z.get("gang")]

        def gang_proche(x: int, y: int) -> str | None:
            for zx, zy, zl, zh, gang in cours:
                if zx - 6 <= x < zx + zl + 6 and zy - 6 <= y < zy + zh + 6:
                    return gang
            return None

        for y in range(self.hauteur):
            for x in range(self.largeur):
                if self.sol[y][x] not in ("F", "d"):
                    continue
                if (x, y) in self.murs_tagges:
                    continue
                # Un mur ne se tague que s'il se VOIT : il faut pouvoir se
                # planter devant.
                if not self.marchable_en(x, y + 1):
                    continue
                gang = gang_proche(x, y)
                #: Trois murs sur cent en ville, un sur cinq au pied d'une cour
                #: de gang : un tag partout ne marque plus rien.
                chance = 0.20 if gang else 0.03
                if not self.des_devanture.chance(chance):
                    continue
                if gang and self.des_devanture.chance(0.75):
                    mots = devantures_mod.TAGS_GANG.get(gang, devantures_mod.TAGS_LIBRES)
                else:
                    mots = devantures_mod.TAGS_LIBRES
                # ⚠️ Un tag long deborde sur les murs voisins : on compte
                # d'abord la place REELLE (jusqu'a trois tuiles de mur d'un
                # seul tenant), puis on ne tire que parmi les mots qui y
                # tiennent. Sans ca, « LA VILLE DORT » finissait ecrit en
                # travers d'un trottoir ou d'une vitrine.
                place = 1
                while place < 3 and x + place < self.largeur \
                        and self.sol[y][x + place] in ("F", "d") \
                        and (x + place, y) not in self.murs_tagges:
                    place += 1
                possibles = [m for m in mots
                             if devantures_mod.tient_en(m, place, TUILE_PX, marge=0)]
                if not possibles:
                    continue
                texte = possibles[self.des_devanture.entier(0, len(possibles) - 1)]
                self.graffitis.append({
                    "x": x, "y": y,
                    "motif": devantures_mod.MOTIFS[self.des_devanture.entier(0, len(devantures_mod.MOTIFS) - 1)],
                    "couleur": self.des_devanture.entier(0, len(devantures_mod.COULEURS_TAG) - 1),
                    "texte": texte,
                    "penche": self.des_devanture.entier(0, 1),
                })
                self.murs_tagges.add((x, y))

    def _ancre_devanture(self, facades: list[tuple[int, int]]) -> tuple[int, int] | None:
        """Ou irait la porte si ce batiment en avait une : le milieu de sa
        facade la plus au sud qui donne sur du marchable."""
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
        if not candidats:
            return None
        bas = max(ty for _, ty in candidats)
        rangee = sorted(c for c in candidats if c[1] == bas)
        return rangee[len(rangee) // 2]

    def poser_decor(self, type_: str, x: int, y: int) -> bool:
        """Du decor seulement sur une tuile libre, hors route et hors devant de porte."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        if (x, y) in self.reserve or (x, y) in self.occupe:
            return False
        proprietes = LEGENDE[self.sol[y][x]]
        if proprietes.get("solide") or proprietes.get("route"):
            return False
        self.occupe.add((x, y))
        self.decor.append({"type": type_, "x": x, "y": y})
        return True

    # --- Les rues -----------------------------------------------------------

    def rues(self) -> None:
        """Chaque rue est posee SEGMENT PAR SEGMENT : un segment avale par un
        superbloc n'est simplement pas peint."""
        for i in range(self.nc + 1):
            coupe = _coupe(RUES_V[i], True)
            for j in range(self.nr):
                if not self.rue_v_existe(i, j):
                    continue
                for y in range(self.yb[j], self.yb[j] + RANGEES[j]):
                    for d, (glyphe, fleche) in enumerate(coupe):
                        self.sol[y][self.xr[i] + d] = glyphe
                        self.voie[y][self.xr[i] + d] = fleche
        for j in range(self.nr + 1):
            coupe = _coupe(RUES_H[j], False)
            for i in range(self.nc):
                if not self.rue_h_existe(i, j):
                    continue
                for d, (glyphe, fleche) in enumerate(coupe):
                    y = self.yr[j] + d
                    for x in range(self.xb[i], self.xb[i] + COLONNES[i]):
                        self.sol[y][x] = glyphe
                        self.voie[y][x] = fleche

    def croisements(self) -> None:
        for j in range(self.nr + 1):
            for i in range(self.nc + 1):
                nord, sud, ouest, est = self.bras(i, j)
                x0, y0, lv, lh = self.xr[i], self.yr[j], RUES_V[i], RUES_H[j]

                if not (nord or sud or ouest or est):
                    continue                      # entierement avale par un superbloc
                if not (ouest or est):            # la rue verticale passe tout droit
                    for dy in range(lh):
                        for dx, (glyphe, fleche) in enumerate(_coupe(lv, True)):
                            self.sol[y0 + dy][x0 + dx] = glyphe
                            self.voie[y0 + dy][x0 + dx] = fleche
                    continue
                if not (nord or sud):
                    for dy, (glyphe, fleche) in enumerate(_coupe(lh, False)):
                        for dx in range(lv):
                            self.sol[y0 + dy][x0 + dx] = glyphe
                            self.voie[y0 + dy][x0 + dx] = fleche
                    continue

                for dy in range(lh):
                    for dx in range(lv):
                        sur_x = TROTTOIR <= dx < lv - TROTTOIR
                        sur_y = TROTTOIR <= dy < lh - TROTTOIR
                        if sur_x and sur_y:
                            glyphe, fleche = "#", "+"
                        elif sur_y:               # la rue est-ouest traverse le trottoir
                            bras = ouest if dx < TROTTOIR else est
                            glyphe, fleche = ("=", "+") if bras else (".", ".")
                        elif sur_x:
                            bras = nord if dy < TROTTOIR else sud
                            glyphe, fleche = (":", "+") if bras else (".", ".")
                        else:
                            glyphe, fleche = ".", "."
                        self.sol[y0 + dy][x0 + dx] = glyphe
                        self.voie[y0 + dy][x0 + dx] = fleche
                self.intersections.append({"x": x0 + TROTTOIR, "y": y0 + TROTTOIR,
                                           "l": lv - 2 * TROTTOIR, "h": lh - 2 * TROTTOIR,
                                           "bras": "".join(c for c, present in
                                                           zip("NSOE", (nord, sud, ouest, est)) if present)})
                self._lignes_arret(i, j, nord, sud, ouest, est)

    def _lignes_arret(self, i: int, j: int, nord: bool, sud: bool,
                      ouest: bool, est: bool) -> None:
        """Une ligne d'arret juste avant chaque entree du croisement."""
        x0, y0, lv, lh = self.xr[i], self.yr[j], RUES_V[i], RUES_H[j]
        voies_h = lh - 2 * TROTTOIR
        voies_v = lv - 2 * TROTTOIR
        approches = []
        for k in range(voies_h // 2, voies_h):            # vers l'est, arrive de l'ouest
            if ouest:
                approches.append((x0 - 1, y0 + TROTTOIR + k, ">"))
        for k in range(voies_h // 2):                     # vers l'ouest, arrive de l'est
            if est:
                approches.append((x0 + lv, y0 + TROTTOIR + k, "<"))
        for k in range(voies_v // 2):                     # vers le sud, arrive du nord
            if nord:
                approches.append((x0 + TROTTOIR + k, y0 - 1, "v"))
        for k in range(voies_v // 2, voies_v):            # vers le nord, arrive du sud
            if sud:
                approches.append((x0 + TROTTOIR + k, y0 + lh, "^"))
        for x, y, direction in approches:
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                continue
            if self.voie[y][x] != direction:
                continue
            self.voie[y][x] = "S"
            self.arrets[f"{x},{y}"] = direction

    # --- Les ilots ----------------------------------------------------------

    def ilots(self) -> None:
        kiosque_pose = False
        for glyphe, x, y, largeur, hauteur in self.regions():
            if glyphe == "Y":
                self._fourriere(x, y, largeur, hauteur, SPECIAUX["Y"])
            elif glyphe in SPECIAUX:
                special = SPECIAUX[glyphe]
                self._ilot_bati(x, y, largeur, hauteur,
                                genre=special.get("genre", "commerces"), special=special)
            elif glyphe == "c":
                self._ilot_bati(x, y, largeur, hauteur)
            elif glyphe == "h":
                self._ilot_bati(x, y, largeur, hauteur, genre="maisons")
            elif glyphe == "m":
                self._ilot_bati(x, y, largeur, hauteur, genre="banlieue")
            elif glyphe == "w":
                self._ilot_bati(x, y, largeur, hauteur, genre="hangars")
            elif glyphe == "i":
                self._ilot_bati(x, y, largeur, hauteur, genre="industriel")
            elif glyphe == "g":
                self._ilot_bati(x, y, largeur, hauteur, genre="gang")
            elif glyphe == "k":
                self._parc(x, y, largeur, hauteur, kiosque=not kiosque_pose)
                kiosque_pose = True
            elif glyphe == "p":
                self._parc(x, y, largeur, hauteur)
            elif glyphe == "n":
                self._parc(x, y, largeur, hauteur, sauvage=True)
            elif glyphe == "o":
                self._place(x, y, largeur, hauteur)
            elif glyphe == "q":
                self._quai(x, y, largeur, hauteur)
            elif glyphe == "~":
                self._eau(x, y, largeur, hauteur)
            else:  # pragma: no cover - garde-fou de relecture du plan
                raise ValueError(f"glyphe de plan inconnu : {glyphe!r}")

    def _bandes(self, y: int, hauteur: int, genre: str = "commerces") -> list[tuple[int, int]]:
        """Un ilot profond se coupe en bandes : ruelle, batiments, devant.

        Sans cela, un superbloc de 28 tuiles de haut serait un seul batiment
        monstrueux ; avec, il a un coeur de ruelles comme un vrai pate de
        maisons.
        """
        if genre in ("hangars", "industriel"):
            # Un entrepot mange son ilot : une bande jusqu'a 26 tuiles de fond.
            nombre = 1 if hauteur <= 26 else 2
        else:
            nombre = 1 if hauteur <= 15 else (2 if hauteur <= 28 else 3)
        base, reste = divmod(hauteur, nombre)
        bandes, cy = [], y
        for k in range(nombre):
            h = base + (1 if k < reste else 0)
            bandes.append((cy, h))
            cy += h
        return bandes

    def _parcelles(self, x: int, y: int, largeur: int, hauteur: int,
                   mini: int = 5, profondeur: int = 0) -> list[tuple[int, int, int, int]]:
        """Decoupe recursive (BSP) en parcelles INEGALES.

        ⚠️ La coupe se tire au sort entre `mini` et le reste : des parcelles de
        meme taille donneraient exactement ce qu'on veut eviter, une rangee de
        batiments identiques.
        """
        peut_v = largeur >= mini * 2
        peut_h = hauteur >= mini * 2
        if profondeur >= 3 or not (peut_v or peut_h):
            return [(x, y, largeur, hauteur)]
        vertical = peut_v if not peut_h else (peut_v and (largeur > hauteur or self.des.chance(0.35)))
        if vertical:
            coupe = self.des.entier(mini, largeur - mini)
            return (self._parcelles(x, y, coupe, hauteur, mini, profondeur + 1)
                    + self._parcelles(x + coupe, y, largeur - coupe, hauteur, mini, profondeur + 1))
        coupe = self.des.entier(mini, hauteur - mini)
        return (self._parcelles(x, y, largeur, coupe, mini, profondeur + 1)
                + self._parcelles(x, y + coupe, largeur, hauteur - coupe, mini, profondeur + 1))

    def _ilot_bati(self, x: int, y: int, largeur: int, hauteur: int, *,
                   genre: str = "commerces", special: dict | None = None) -> None:
        devant = {"maisons": ",", "banlieue": ","}.get(genre, ".")
        #: Des parcelles d'autant plus grandes que le batiment l'est : une
        #: maison de banlieue tient sur son terrain, un entrepot sur le sien.
        mini = {"maisons": 4, "banlieue": 7, "hangars": 9, "industriel": 10}.get(genre, 5)
        parcelles: list[tuple[tuple[int, int, int, int], bool]] = []
        for by, bh in self._bandes(y, hauteur, genre):
            self.rect(x, by, largeur, 2, "x")                      # ruelle derriere
            self.rect(x, by + bh - 2, largeur, 2, devant)           # devant
            zy, zh = by + 2, bh - 4
            if zh < 3:
                continue
            self.rect(x, zy, largeur, zh, "," if genre in ("maisons", "banlieue") else ".")
            for parcelle in self._parcelles(x, zy, largeur, zh, mini):
                parcelles.append((parcelle, parcelle[1] + parcelle[3] >= zy + zh))
            if genre == "gang":
                # Une cour cloturee, avec une entree pour les chars.
                ouverture = self.des.entier(2, max(3, largeur - 7))
                for i in range(largeur):
                    if not ouverture <= i < ouverture + 5 and self.des.chance(0.8):
                        self.sol[by + bh - 1][x + i] = "f"
                for _ in range(3):
                    self.poser_decor("caisse", x + self.des.entier(0, largeur - 1),
                                     by + self.des.entier(0, 1))

        contenus = [self._contenu(genre) for _ in parcelles]
        # ⚠️ « Les Skateux tiennent le stationnement » (voir DISTRICTS) — sauf
        # que La Pointe n'en avait pas UNE tuile : la phrase etait une legende.
        # Leur bloc en porte donc un pour de bon, et c'est la que se pose leur
        # tremplin (`_tremplin_de_stationnement`).
        if genre == "gang" and parcelles and self.district_en(x, y) == "pointe":
            contenus[max(range(len(parcelles)),
                         key=lambda k: parcelles[k][0][2] * parcelles[k][0][3])] = "stationnement"
        vedette = -1
        if special and parcelles:
            # ⚠️ Le batiment garanti ne peut pas dependre d'un tirage : sans
            # cette ligne, un ilot de neuf tuiles tire « terrain vague » et
            # l'armurerie n'existe pas. Il prend la plus grosse parcelle qui
            # donne sur la rue, et elle est batie quoi qu'il arrive.
            vedette = max(range(len(parcelles)),
                          key=lambda k: (parcelles[k][1], parcelles[k][0][2] * parcelles[k][0][3]))
            contenus[vedette] = "bati"

        batiments: list[tuple[list, bool, int]] = []
        facades_vedette = None
        for k, ((px, py, pl, ph), devant_rue) in enumerate(parcelles):
            contenu = contenus[k]
            if contenu == "bati":
                facades = self._pose_batiment(px, py, pl, ph, genre, force=(k == vedette))
                if facades and k == vedette:
                    facades_vedette = facades
                elif facades:
                    batiments.append((facades, devant_rue, pl * ph))
            elif contenu == "vague":
                self._terrain_vague(px, py, pl, ph)
            elif contenu == "stationnement":
                self._stationnement(px, py, pl, ph, genre)
            else:
                self._jardin(px, py, pl, ph)
        if facades_vedette:
            porte = self.poser_porte(facades_vedette, special)
            if porte:
                self.poser_devanture(facades_vedette, porte, genre, special)
        for facades, _, _ in batiments:
            porte = self.poser_porte(facades)
            # ⚠️ Une devanture ne suit pas la porte : un commerce a pignon sur
            # rue qu'on ne peut pas visiter reste un commerce, et une rue ou
            # seuls les trois batiments visitables ont une enseigne n'a l'air
            # d'une rue commercante nulle part.
            if genre in GENRES_COMMERCANTS:
                ancre = porte or self._ancre_devanture(facades)
                if ancre:
                    self.poser_devanture(facades, ancre, genre)
        for _ in range(max(1, largeur // 10)):
            self.poser_decor("poubelle", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, 1))

    def _contenu(self, genre: str) -> str:
        tirage = self.des.flottant()
        if genre == "maisons":
            return "bati" if tirage < 0.74 else ("jardin" if tirage < 0.92 else "stationnement")
        if genre == "banlieue":
            return "bati" if tirage < 0.72 else ("jardin" if tirage < 0.94 else "stationnement")
        if genre == "hangars":
            return "bati" if tirage < 0.80 else ("stationnement" if tirage < 0.95 else "vague")
        if genre == "industriel":
            # La Shop, c'est autant d'asphalte vide que de tole : des cours de
            # manoeuvre, des terrains de ferraille, et trois entrepots dedans.
            return "bati" if tirage < 0.60 else ("stationnement" if tirage < 0.88 else "vague")
        if genre == "gang":
            return "bati" if tirage < 0.70 else ("stationnement" if tirage < 0.85 else "vague")
        return "bati" if tirage < 0.88 else ("vague" if tirage < 0.95 else "stationnement")

    def _pose_batiment(self, px: int, py: int, pl: int, ph: int, genre: str,
                       force: bool = False) -> list | None:
        """Un batiment dans sa parcelle, avec des marges tirees au sort.

        Les marges sont ce qui cree les ruelles, les cours et les dents creuses
        entre deux immeubles colles.
        """
        if genre == "maisons":
            ouest, est = self.des.entier(0, 2), self.des.entier(0, 2)
            nord, sud = self.des.entier(0, 3), self.des.entier(0, 2)
        elif genre == "banlieue":
            # ⚠️ La banlieue se reconnait au VIDE autour des maisons, pas aux
            # maisons : des marges larges, et le gazon qu'on voit entre deux.
            ouest, est = self.des.entier(1, 4), self.des.entier(1, 4)
            nord, sud = self.des.entier(1, 5), self.des.entier(1, 3)
        elif genre in ("hangars", "industriel"):
            ouest = est = 1 if self.des.chance(0.35) else 0
            nord, sud = self.des.entier(0, 2), self.des.entier(0, 1)
        else:
            # ⚠️ Un immeuble de centre-ville colle a son voisin : la marge est
            # l'exception (une ruelle, une dent creuse), pas la regle.
            ouest = 1 if self.des.chance(0.22) else 0
            est = 1 if self.des.chance(0.22) else 0
            nord = 1 if self.des.chance(0.35) else 0
            sud = 1 if self.des.chance(0.25) else 0
        # ⚠️ Les marges cedent avant le batiment : une parcelle mince ne doit
        # pas rendre un batiment de deux tuiles — ou pas de batiment du tout.
        while pl - ouest - est < 3 and (ouest or est):
            if est:
                est -= 1
            else:
                ouest -= 1
        while ph - nord - sud < 3 and (nord or sud):
            if nord:
                nord -= 1
            else:
                sud -= 1
        bx, by = px + ouest, py + nord
        bl, bh = pl - ouest - est, ph - nord - sud
        if bl < 3 or bh < 3:
            return None
        tuiles = {(bx + i, by + j) for j in range(bh) for i in range(bl)}
        if bl >= 9 and bh >= 6 and self.des.chance(0.32):
            # Un U autour d'une cour ouverte au sud.
            cl = self.des.entier(2, bl - 6)
            cx = bx + self.des.entier(2, bl - cl - 2)
            ch = self.des.entier(2, bh - 3)
            tuiles -= {(cx + i, by + bh - 1 - j) for j in range(ch) for i in range(cl)}
        elif bl >= 6 and bh >= 5 and self.des.chance(0.30):
            # Un L : on mord un coin au sud.
            cl, ch = self.des.entier(2, bl // 2), self.des.entier(2, bh // 2)
            coin = bx if self.des.chance(0.5) else bx + bl - cl
            tuiles -= {(coin + i, by + bh - 1 - j) for j in range(ch) for i in range(cl)}
        vitrines = {"commerces": 0.5, "maisons": 0.12, "banlieue": 0.10,
                    "hangars": 0.03, "industriel": 0.05, "gang": 0.08}.get(genre, 0.3)
        if force:
            # Un batiment garanti garde sa masse : ni cour ni coin mordu.
            tuiles = {(bx + i, by + j) for j in range(bh) for i in range(bl)}
        return self.batiment_forme(tuiles, vitrines)

    # --- La fourriere (M9) --------------------------------------------------

    #: La cour, en tuiles. ⚠️ Elle ne prend PAS tout l'ilot : un bloc fusionne
    #: de La Shop fait 39 x 24 tuiles, et une fourriere de cette taille serait
    #: un quartier a elle seule. Le lot prend le sud-est, le reste redevient de
    #: l'industriel ordinaire — et la cour garde des voisins, ce qui est bien
    #: le genre d'endroit ou on la met.
    LOT_L, LOT_H = 22, 16
    #: Une place : un char de 48 px (l'autobus) tient dans trois tuiles, et il
    #: faut de quoi ouvrir la portiere a cote.
    PLACE_L, PLACE_H = 4, 3
    #: La guerite, et la grille — la seule ouverture de la cloture.
    GUERITE_L, GUERITE_H, GRILLE_L = 6, 4, 4

    def _fourriere(self, x: int, y: int, largeur: int, hauteur: int, special: dict) -> None:
        """Une cour d'asphalte cloturee, une guerite, UNE grille.

        ⚠️ Tout le lot tient sur une propriete de la cloture : `f` est solide 3
        — elle arrete les chars, pas les gens. C'est ce qui fait les deux
        facons de reprendre son char sans une ligne de code pour les
        distinguer : par la grille, en payant au comptoir ; ou par-dessus la
        cloture, a pied, et le lot appelle.

        ⚠️ Et il n'y a QU'UNE grille. Deux ouvertures, et sortir son char sans
        payer ne demanderait plus rien a personne.
        """
        lot_l, lot_h = min(largeur, self.LOT_L), min(hauteur, self.LOT_H)
        lx, ly = x + largeur - lot_l, y + hauteur - lot_h
        if lx - x >= 10:
            self._ilot_bati(x, y, lx - x, hauteur, genre="industriel")
        else:
            lx, lot_l = x, largeur
        if ly - y >= 8:
            self._ilot_bati(lx, y, lot_l, ly - y, genre="industriel")
        else:
            ly, lot_h = y, hauteur

        self.rect(lx, ly, lot_l, 2, "x")                        # ruelle derriere
        self.rect(lx, ly + lot_h - 2, lot_l, 2, ".")            # trottoir devant
        zy, zh = ly + 2, lot_h - 4
        if zh < 10 or lot_l < 16:  # pragma: no cover - garde-fou de relecture du plan
            raise ValueError(f"le lot de la fourriere ne tient pas : {lot_l} x {zh}")
        self.rect(lx, zy, lot_l, zh, "p")
        # La guerite, au coin nord-ouest : elle donne sur la cour, pas sur la
        # rue — on entre par la grille, comme tout le monde.
        guerite = {(lx + 1 + i, zy + 1 + j)
                   for i in range(self.GUERITE_L) for j in range(self.GUERITE_H)}
        facades = self.batiment_forme(guerite)
        gx = lx + lot_l - self.GRILLE_L - 2
        for i in range(lot_l):
            if not gx <= lx + i < gx + self.GRILLE_L:
                self.sol[zy + zh - 1][lx + i] = "f"
            self.sol[zy][lx + i] = "f"
        for j in range(zh):
            self.sol[zy + j][lx] = "f"
            self.sol[zy + j][lx + lot_l - 1] = "f"
        for tx, ty in guerite:                                  # la guerite reste batie
            if self.sol[ty][tx] == "f":
                self.sol[ty][tx] = "F"
        porte = self.poser_porte(facades, special)
        # Les places : sous la guerite, jamais dans l'axe de la grille.
        places = []
        for py in range(zy + self.GUERITE_H + 1, zy + zh - self.PLACE_H, self.PLACE_H):
            for px in range(lx + 2, lx + lot_l - self.PLACE_L - 1, self.PLACE_L):
                if gx - 1 <= px < gx + self.GRILLE_L + 1:
                    continue
                places.append({"x": px + 1, "y": py + 1})
        for _ in range(3):
            self.poser_decor("debris",
                             lx + self.des.entier(self.GUERITE_L + 3, lot_l - 3),
                             zy + self.des.entier(1, self.GUERITE_H))
        self.fourriere = {
            "x": lx, "y": zy, "largeur": lot_l, "hauteur": zh,
            "grille": {"x": gx, "y": zy + zh - 1, "largeur": self.GRILLE_L},
            "porte": {"x": porte[0], "y": porte[1]} if porte else None,
            "places": places,
        }

    def _terrain_vague(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.rect(x, y, largeur, hauteur, ",")
        for i in range(largeur):
            if self.des.chance(0.5):
                self.sol[y + hauteur - 1][x + i] = "f"
        for _ in range(max(1, largeur * hauteur // 12)):
            self.poser_decor("debris", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        # Un tremplin de planches sur les gravats : le terrain vague est
        # l'endroit ou une rampe se raconte toute seule. ⚠️ On COUPE la cloture
        # devant : sinon c'est un tremplin derriere un grillage, et on vient de
        # passer une heure a se debarrasser de ceux-la. Apres les debris, pour
        # ne pas en poser un au milieu de la piste.
        if largeur >= 5 and hauteur >= 4 and self.des_rampe.chance(0.45):
            cx = x + largeur // 2
            self.proposer_rampe([(cx, y + hauteur // 2, None)],
                                cloture=(cx, y + hauteur - 1))

    def _jardin(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.rect(x, y, largeur, hauteur, ",")
        for _ in range(max(1, largeur * hauteur // 10)):
            self.poser_decor(self.des.choix(("arbre", "buisson")),
                             x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    # --- Les rampes ---------------------------------------------------------

    def _roulable(self, x: int, y: int) -> bool:
        """Une tuile ou un char passe VRAIMENT : rien de solide, pas de decor,
        pas le devant d'une porte.

        ⚠️ Une solidite de 3 (cloture, borne-fontaine) laisse passer un pieton
        mais arrete un char. Une cloture dans l'elan, c'est un elan qui
        n'existe pas — c'est ce qui rendait les rampes de la cour des gangs
        injouables : on les voyait, on ne pouvait pas les prendre.
        """
        return (0 <= x < self.largeur and 0 <= y < self.hauteur
                and solidite(self.sol[y][x]) == 0
                and (x, y) not in self.occupe and (x, y) not in self.reserve)

    def _course(self, x: int, y: int, dx: int, dy: int, voulu: int) -> int:
        """Combien de tuiles roulables d'affilee dans cette direction."""
        n = 0
        while n < voulu and self._roulable(x + dx * (n + 1), y + dy * (n + 1)):
            n += 1
        return n

    def _libre_pour_rampe(self, x: int, y: int) -> bool:
        """Ou une rampe a le droit de se poser.

        ⚠️ Jamais sur une voie de circulation : le trafic roule sur des rails,
        et un tremplin au milieu de sa trajectoire enverrait un char dans le
        decor a chaque tour.

        ⚠️ Jamais sur un TROTTOIR non plus, et c'est la vraie lecon du retour de
        Martin : les anciennes rampes avaient de l'elan — vingt et une tuiles !
        — mais uniquement le long du trottoir, entre un grillage et des murs.
        De l'elan qu'on ne peut prendre qu'en roulant sur le trottoir n'est pas
        de l'elan, c'est un couloir. Une rampe se pose la ou les chars passent
        deja : asphalte, stationnement, cour, quai, terrain vague.
        """
        return (self._roulable(x, y) and self.voie[y][x] == "."
                and not LEGENDE[self.sol[y][x]].get("trottoir"))

    def proposer_rampe(self, essais: list[tuple[int, int, tuple[int, int] | None]],
                       cloture: tuple[int, int] | None = None) -> None:
        """Une rampe A ESSAYER quand la ville sera finie : chaque essai est un
        (x, y, axe), et le premier qui tient gagne.

        ⚠️ Meme lecon que les graffitis (« apres les ilots, on tague des murs
        qui existent ») : un tremplin pose pendant les ilots voyait sa
        reception muree par la parcelle d'a cote, batie trois lignes plus tard.
        Mesure avant correctif : trois rampes sur onze retombaient sur un mur.
        """
        self.rampes_proposees.append({"essais": essais, "cloture": cloture})

    def poser_les_rampes(self) -> None:
        """Le tour des propositions, sur la ville FINIE."""
        for proposition in self.rampes_proposees:
            cloture = proposition["cloture"]
            if cloture:
                # Le trou dans le grillage se fait meme si le tremplin ne tient
                # pas : un terrain vague avec sa cloture percee, c'est une
                # image juste de toute facon.
                cx, cy = cloture
                for i in (-1, 0, 1):
                    if 0 <= cx + i < self.largeur and self.sol[cy][cx + i] == "f":
                        self.sol[cy][cx + i] = ","
            for x, y, axe in proposition["essais"]:
                if self.poser_rampe(x, y, axe):
                    break

    def poser_rampe(self, x: int, y: int, sens: tuple[int, int] | None = None) -> bool:
        """Une rampe de deux tuiles en (x, y) : le pied, puis la levre.

        ⚠️ On ne CHOISIT pas le sens, on le MESURE : les quatre axes sont
        essayes, le plus long gagne, et aucun ne passe sans son elan et sa
        reception. Rien de pose vaut mieux qu'un tremplin contre un mur — un
        tremplin qu'on ne peut pas prendre n'est pas un decor, c'est une
        enigme.
        """
        meilleur = None
        for dx, dy in ([sens] if sens else [(1, 0), (-1, 0), (0, 1), (0, -1)]):
            if not (self._libre_pour_rampe(x, y) and self._libre_pour_rampe(x + dx, y + dy)):
                continue
            # ⚠️ On mesure BIEN AU-DELA du minimum exige : plafonnee au
            # minimum, la mesure donnait la meme note aux quatre axes et « le
            # plus long gagne » ne voulait plus rien dire — l'est gagnait
            # toujours, par ordre de la liste.
            elan = self._course(x, y, -dx, -dy, ELAN_RAMPE * 3)
            reception = self._course(x + dx, y + dy, dx, dy, RECEPTION_RAMPE * 3)
            if elan < ELAN_RAMPE or reception < RECEPTION_RAMPE:
                continue
            if meilleur is None or elan + reception > meilleur[0]:
                meilleur = (elan + reception, dx, dy)
        if meilleur is None:
            return False
        _, dx, dy = meilleur
        self.sol[y][x] = "R"
        self.sol[y + dy][x + dx] = "J"
        # ⚠️ La piste se RESERVE : un arbre pose plus tard au milieu de l'elan
        # rendrait la rampe inutilisable sans qu'aucun juge ne bronche.
        for k in range(-ELAN_RAMPE, RECEPTION_RAMPE + 2):
            self.occupe.add((x + dx * k, y + dy * k))
        self.rampes.append({"x": x, "y": y, "dx": dx, "dy": dy})
        return True

    # --- Stationnements -----------------------------------------------------

    def _bandes_stationnement(self, creux: int) -> list[tuple[str, int]]:
        """Decoupe l'axe PROFOND d'un stationnement en bandes : « R » une
        rangee de cases, « A » une allee de manoeuvre.

        ⚠️ La regle qui tient tout le dessin : TOUTE rangee touche une allee.
        Sans elle on peint de belles cases ou aucune auto ne peut entrer, et
        le stationnement redevient un champ d'asphalte raye au hasard.

        Le motif est donc « R A (R R A)* [R] » : une rangee contre le bord, son
        allee, puis des rangees DOS A DOS qui se partagent l'allee suivante —
        exactement le dessin des vrais. Il faut 4 tuiles pour une rangee, 6
        pour deux, 10 pour trois, 12 pour quatre. Ce qui reste elargit les
        allees, puis longe le bord en voie de contournement.
        """
        rangees = 1
        while 2 * (rangees + 1) + ALLEE * ((rangees + 2) // 2) <= creux:
            rangees += 1
        bandes = [("R", CASE_CREUX), ("A", ALLEE)]
        paires, seule = divmod(rangees - 1, 2)
        for _ in range(paires):
            bandes += [("R", CASE_CREUX), ("R", CASE_CREUX), ("A", ALLEE)]
        if seule:
            bandes.append(("R", CASE_CREUX))
        # ⚠️ Une rangee de plus vaut mieux qu'une allee large, mais une allee
        # de plus de quatre tuiles n'est plus une allee : c'est une place
        # publique. Au-dela, le reste longe le bord — la voie de contournement
        # par ou les autos entrent.
        reste = creux - sum(taille for _, taille in bandes)
        for i, (type_, taille) in enumerate(bandes):
            if type_ == "A" and reste:
                ajout = min(reste, 4 - taille)
                bandes[i] = ("A", taille + ajout)
                reste -= ajout
        if reste:
            bandes.append(("A", reste))
        return bandes

    @staticmethod
    def _nez_au_debut(bandes: list[tuple[str, int]], i: int) -> bool:
        """De quel cote une rangee tourne-t-elle son PARE-CHOCS ?

        Le fond de la case va contre ce qui ferme : le bord du terrain d'abord,
        le dos de la rangee voisine ensuite — et si les deux cotes sont des
        allees, contre la plus etroite, pour laisser la grande a la
        circulation.
        """
        def ferme(k: int) -> int:
            if not 0 <= k < len(bandes):
                return 10                       # le bord du terrain : le mieux
            return 5 if bandes[k][0] == "R" else -bandes[k][1]

        return ferme(i - 1) >= ferme(i + 1)

    def _stationnement(self, x: int, y: int, largeur: int, hauteur: int,
                       genre: str = "commerces") -> None:
        """Un vrai stationnement : des rangees de cases, des allees pour y
        entrer, et un ilot de beton au bout des rangees.

        Une case fait UNE tuile de large et DEUX de creux — exactement le
        gabarit d'une auto (32 x 16 px), pour qu'une auto garee tombe dans ses
        lignes au pixel pres.

        ⚠️ Avant, une parcelle de stationnement etait un rectangle de « p » et
        le peintre posait une ligne toutes les trois tuiles : de loin, un
        code-barres ; de pres, des places de travers, sans allee et sans
        entree. Le dessin se decide ICI, ou l'on connait la forme du terrain.
        """
        self.rect(x, y, largeur, hauteur, "p")
        # Les allees suivent le GRAND cote : des rangees en travers du long,
        # c'est deux fois moins d'asphalte perdu en manoeuvres.
        debout = largeur >= hauteur
        creux = hauteur if debout else largeur
        longueur = largeur if debout else hauteur
        if creux < CASE_CREUX + 2 or longueur < 3:
            return          # une cour de service, pas un stationnement : nue
        bandes = self._bandes_stationnement(creux)
        allees: list[tuple[int, int]] = []
        d = 0
        for i, (type_, taille) in enumerate(bandes):
            if type_ == "A":
                allees.append((d, taille))
                d += taille
                continue
            vers_le_debut = self._nez_au_debut(bandes, i)
            if debout:
                self.rect(x, y + d, largeur, taille, "^" if vers_le_debut else "v")
            else:
                self.rect(x + d, y, taille, hauteur, "<" if vers_le_debut else ">")
            # Un ilot de beton au bout de la rangee, et un lampadaire une
            # rangee sur deux (deux lampes cote a cote sur le meme ilot, ca
            # eclaire deux fois moins bien et ca coute deux fois plus cher).
            # ⚠️ L'ilot n'est PAS du trottoir : un kiosque a hot-dogs se pose
            # sur le trottoir, et il se poserait au milieu de l'asphalte, sur
            # le pied du lampadaire.
            if genre not in ("hangars", "industriel") and longueur >= 8:
                bouts = [longueur - 1] if longueur < 12 else [0, longueur - 1]
                for k, bout in enumerate(bouts):
                    if debout:
                        ix, iy, il, ih = x + bout, y + d, 1, taille
                    else:
                        ix, iy, il, ih = x + d, y + bout, taille, 1
                    self.rect(ix, iy, il, ih, "I")
                    if i % 2 == 0 and k == 0:
                        if self.poser_decor("lampadaire", ix, iy):
                            self.lampes.append({"x": ix, "y": iy})
            d += taille
        self._tremplin_de_stationnement(x, y, debout, longueur, allees)

    def _tremplin_de_stationnement(self, x: int, y: int, debout: bool,
                                   longueur: int, allees: list[tuple[int, int]]) -> None:
        """Le tremplin se pose dans une ALLEE : c'est l'axe ou l'on roule deja,
        et le seul qui offre une piste droite — en travers des cases, on
        arriverait de biais et on ne decollerait pas.

        ⚠️ Dans La Pointe, il y en a un a tout coup : « les Skateux tiennent le
        stationnement » (voir DISTRICTS). C'est ce qui fait de leur coin autre
        chose qu'un decor, et ca donne au joueur une raison de traverser le
        pont.
        """
        if not allees:
            return
        if self.district_en(x, y) != "pointe" and not self.des_rampe.chance(0.35):
            return
        d, taille = allees[len(allees) // 2]
        milieu = d + taille // 2
        # ⚠️ L'elan n'a pas a tenir dans le terrain : il continue dans la rue,
        # et c'est tant mieux — on arrive lance au lieu de partir d'arret.
        essais = []
        for part in (3, 2, 1):
            le_long = max(1, longueur * part // 4)
            cx, cy = (x + le_long, y + milieu) if debout else (x + milieu, y + le_long)
            for sens in (((1, 0), (-1, 0)) if debout else ((0, 1), (0, -1))):
                essais.append((cx, cy, sens))
        self.proposer_rampe(essais)

    # --- Parc, place, port --------------------------------------------------

    def _parc(self, x: int, y: int, largeur: int, hauteur: int, kiosque: bool = False,
              sauvage: bool = False) -> None:
        """Un parc de ville, ou — `sauvage` — le bois de La Pointe : les memes
        allees, mais en terre battue, et des arbres au lieu des bancs."""
        pave = "s" if sauvage else "."
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, ",")
        centre = (x + largeur // 2, y + hauteur // 2)
        # Des allees en baionnette depuis les quatre bords vers le coeur.
        for bord in range(4):
            if bord == 0:
                depart = (x + self.des.entier(2, largeur - 3), y)
            elif bord == 1:
                depart = (x + self.des.entier(2, largeur - 3), y + hauteur - 1)
            elif bord == 2:
                depart = (x, y + self.des.entier(2, hauteur - 3))
            else:
                depart = (x + largeur - 1, y + self.des.entier(2, hauteur - 3))
            self._allee(depart, centre, pave)
        self.rect(centre[0] - 2, centre[1] - 2, 5, 5, pave)
        # Un etang, toujours a plus de trois tuiles du bord : il ne doit
        # enfermer aucun coin de pelouse.
        if largeur >= 16 and hauteur >= 12:
            el = self.des.entier(5, min(9, largeur // 3))
            eh = self.des.entier(3, min(6, hauteur // 3))
            ex = x + self.des.entier(3, largeur - el - 4)
            ey = y + self.des.entier(3, hauteur - eh - 4)
            for j in range(eh):
                for i in range(el):
                    bord = i == 0 or j == 0 or i == el - 1 or j == eh - 1
                    if self.sol[ey + j][ex + i] == pave:
                        continue
                    self.sol[ey + j][ex + i] = "s" if bord else "~"
        if kiosque:
            kx = x + largeur - self.des.entier(7, 9)
            ky = y + hauteur - 5
            facades = self.batiment_forme({(kx + i, ky + j) for j in range(3) for i in range(4)}, 0.6)
            self.poser_porte(facades, {"slug": "kiosque", "interieur": "kiosque",
                                       "nom": "Kiosque de Madame Thibodeau"})
        for _ in range(largeur * hauteur // (7 if sauvage else 14)):
            self.poser_decor("arbre", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        for _ in range(largeur * hauteur // (90 if sauvage else 40)):
            self.poser_decor("banc", x + self.des.entier(1, largeur - 2),
                             y + self.des.entier(1, hauteur - 2))
        for _ in range(largeur * hauteur // (18 if sauvage else 30)):
            self.poser_decor("buisson", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    def _allee(self, depart: tuple[int, int], arrivee: tuple[int, int], pave: str = ".") -> None:
        """Une allee de deux tuiles, avec un coude au hasard — jamais tout droit."""
        dx, dy = depart
        ax, ay = arrivee
        coude = dx + (ax - dx) * self.des.entier(2, 8) // 10
        for x in range(min(dx, coude), max(dx, coude) + 1):
            self.rect(x, dy, 1, 2, pave)
        for y in range(min(dy, ay), max(dy, ay) + 1):
            self.rect(coude, y, 2, 1, pave)
        for x in range(min(coude, ax), max(coude, ax) + 1):
            self.rect(x, ay, 1, 2, pave)

    def _place(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Une place publique : du pave, une fontaine, des bancs. Pas une rue."""
        self.bouchon_rect(x, y, largeur, hauteur, ".")
        self.rect(x, y, largeur, hauteur, ".")
        self.rect(x + 1, y + 1, largeur - 2, hauteur - 2, ".")
        fx, fy = x + largeur // 2, y + hauteur // 2
        self.poser_decor("fontaine", fx, fy)
        for coin in ((x + 1, y + 1), (x + largeur - 2, y + 1),
                     (x + 1, y + hauteur - 2), (x + largeur - 2, y + hauteur - 2)):
            self.poser_decor("arbre", *coin)
        for _ in range(max(2, largeur // 4)):
            self.poser_decor("banc", x + self.des.entier(1, largeur - 2),
                             y + self.des.entier(1, hauteur - 2))
        if self.poser_decor("lampadaire", fx - 2, fy - 2):
            self.lampes.append({"x": fx - 2, "y": fy - 2})

    def _quai(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "Q")
        for _ in range(largeur * hauteur // 14):
            self.poser_decor("caisse", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        # Une rampe de debarquement, la ou un quai en porte vraiment une.
        # ⚠️ L'eau n'est pas roulable : `poser_rampe` ne choisira jamais l'axe
        # qui envoie au fond de la baie, le saut longe le port.
        if largeur >= 10 and hauteur >= 3 and self.des_rampe.chance(0.5):
            self.proposer_rampe([(x + largeur // 2, y + hauteur // 2, None)])

    def _terre_a_cote(self, tuiles: list[tuple[int, int]]) -> bool:
        """Y a-t-il de la terre le long de ce bord ? Hors carte : non.

        ⚠️ Une plage au fond d'une baie, de l'autre bord de l'eau, personne ne
        la verra jamais — et `boucher_les_poches` la noierait de toute facon.
        On ne dessine une rive que la ou il y a un rivage.
        """
        for x, y in tuiles:
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                return False
            if self.sol[y][x] != "~":
                return True
        return False

    def _eau(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Un bassin a rive irreguliere : du sable qui avance et recule."""
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "~")
        pas = max(1, largeur // 8)
        nord = self._terre_a_cote([(x + i, y - 1) for i in range(0, largeur, pas)])
        sud = self._terre_a_cote([(x + i, y + hauteur) for i in range(0, largeur, pas)])
        pas = max(1, hauteur // 8)
        ouest = self._terre_a_cote([(x - 1, y + j) for j in range(0, hauteur, pas)])
        est = self._terre_a_cote([(x + largeur, y + j) for j in range(0, hauteur, pas)])
        # ⚠️ La rive ne mange jamais plus du tiers du bassin : sans ce plafond,
        # le sable des deux rives se rejoint au milieu d'un chenal etroit — et
        # La Pointe, qu'un pont devait seul relier, se traverse a pied.
        sable_h = min(4, hauteur // 3)
        sable_v = min(3, largeur // 3)
        profondeur = min(2, sable_h)
        for i in range(largeur):
            profondeur = max(0, min(sable_h, profondeur + self.des.entier(-1, 1)))
            for j in range(profondeur):
                if nord:
                    self.sol[y + j][x + i] = "s"
                if sud:
                    self.sol[y + hauteur - 1 - j][x + i] = "s"
        profondeur = min(2, sable_v)
        for j in range(hauteur):
            profondeur = max(0, min(sable_v, profondeur + self.des.entier(-1, 1)))
            for i in range(profondeur):
                if ouest:
                    self.sol[y + j][x + i] = "s"
                if est:
                    self.sol[y + j][x + largeur - 1 - i] = "s"

    # --- Decor de rue et finitions -----------------------------------------

    #: Ou chercher le trottoir autour d'un coin de croisement : le coin
    #: d'abord, puis ses voisines, les plus proches en premier.
    AUTOUR = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))

    def lampadaires(self) -> None:
        """Deux coins opposes par croisement : de la lumiere ou l'on tourne.

        ⚠️ Un poteau se plante sur un TROTTOIR, jamais sur un parterre. Le coin
        d'un croisement n'en est pas toujours un : devant une maison, la bande
        de devant est en gazon, et devant la fourriere, en asphalte. On cherche
        alors le trottoir a cote. Sans ca, le juge ne tenait que par chance —
        il suffisait qu'un arbre libere le coin pour qu'une lampe pousse dans
        une pelouse.
        """
        for inter in self.intersections:
            for dx, dy in ((-1, -1), (inter["l"], inter["h"])):
                x, y = inter["x"] + dx, inter["y"] + dy
                for ix, iy in self.AUTOUR:
                    cx, cy = x + ix, y + iy
                    if not (0 <= cx < self.largeur and 0 <= cy < self.hauteur):
                        continue
                    if self.sol[cy][cx] != "." or not self.poser_decor("lampadaire", cx, cy):
                        continue
                    self.lampes.append({"x": cx, "y": cy})
                    break

    def ambulants(self) -> list[dict]:
        """Les commerces sans porte : kiosques sur le trottoir, camions au
        stationnement. On les espace : trois kiosques a hot-dogs au meme coin,
        c'est une file d'attente, pas une ville."""
        poses: list[dict] = []
        ecart = 22
        for commerce in magasins.AMBULANTS:
            candidats = self._places_ambulantes(commerce["sur"])
            if not candidats:
                continue
            for _ in range(commerce["nombre"]):
                choisi = None
                for _essai in range(60):
                    x, y = candidats[self.des.suivant() % len(candidats)]
                    if any(abs(p["x"] - x) + abs(p["y"] - y) < ecart for p in poses):
                        continue
                    if (x, y) in self.occupe or (x, y) in self.reserve:
                        continue
                    choisi = (x, y)
                    break
                if not choisi:
                    continue
                self.occupe.add(choisi)
                poses.append({"slug": commerce["slug"], "x": choisi[0], "y": choisi[1]})
        return poses

    def _places_ambulantes(self, sur: str) -> list[tuple[int, int]]:
        """Une place est bonne si on peut s'y arreter ET etre servi devant."""
        places = []
        for y in range(1, self.hauteur - 2):
            for x in range(1, self.largeur - 1):
                glyphe = self.sol[y][x]
                if sur == "trottoir":
                    if glyphe != "." or not marchable(self.sol[y + 1][x]):
                        continue
                    voisins = (self.sol[y][x - 1], self.sol[y][x + 1],
                               self.sol[y - 1][x], self.sol[y + 1][x])
                    if not any(routier(v) for v in voisins):
                        continue
                elif sur == "stationnement":
                    if glyphe != "p" or self.sol[y][x + 1] != "p":
                        continue
                    if not marchable(self.sol[y + 1][x]):
                        continue
                else:  # pragma: no cover - garde-fou de relecture du catalogue
                    raise ValueError(f"support inconnu : {sur!r}")
                places.append((x, y))
        return places

    def paquets(self, nombre: int = 20) -> list[dict]:
        """Vingt paquets caches dans les recoins : ruelles, terrains vagues,
        coins de parc, quais. Jamais sur une rue, jamais devant une porte,
        et espaces — les trouver doit faire visiter la ville."""
        recoins = [(x, y) for y in range(1, self.hauteur - 1) for x in range(1, self.largeur - 1)
                   if self.sol[y][x] in "x,Qs" and (x, y) not in self.reserve and (x, y) not in self.occupe]
        poses: list[dict] = []
        for _essai in range(4000):
            if len(poses) >= nombre or not recoins:
                break
            x, y = recoins[self.des.suivant() % len(recoins)]
            if any(abs(p["x"] - x) + abs(p["y"] - y) < 18 for p in poses):
                continue
            self.occupe.add((x, y))
            poses.append({"numero": len(poses), "x": x, "y": y})
        return poses

    def bornes(self) -> None:
        for inter in self.intersections:
            if not self.des.chance(0.30):
                continue
            x, y = inter["x"] + inter["l"], inter["y"] - 1
            if 0 <= x < self.largeur and 0 <= y < self.hauteur and self.sol[y][x] == ".":
                self.sol[y][x] = "b"

    def boucher_les_poches(self, depart: tuple[int, int]) -> int:
        """Bouche toute poche marchable qu'on ne peut pas rejoindre a pied.

        ⚠️ C'est le FILET du generateur. Un gabarit qui referme une cour, deux
        batiments qui se rejoignent sur une ruelle : au lieu d'un juge rouge et
        d'un ilot injouable, la poche redevient du bati (ou de l'eau dans un
        parc). Si elle en bouche beaucoup, c'est un gabarit qu'il faut revoir,
        et `generer()` le dit tout haut.
        """
        vus = {depart}
        pile = [depart]
        while pile:
            cx, cy = pile.pop()
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if (nx, ny) in vus or not self.marchable_en(nx, ny):
                    continue
                vus.add((nx, ny))
                pile.append((nx, ny))
        bouchees = 0
        for y in range(self.hauteur):
            for x in range(self.largeur):
                if marchable(self.sol[y][x]) and (x, y) not in vus:
                    self.sol[y][x] = self.bouchon[y][x]
                    bouchees += 1
        if bouchees:
            self.decor = [d for d in self.decor
                          if marchable(self.sol[d["y"]][d["x"]])]
            # ⚠️ Une rampe prise dans une poche bouchee n'existe plus : la
            # laisser dans la liste, c'est promettre au defi du Grand Saut un
            # tremplin qui n'est plus la.
            self.rampes = [r for r in self.rampes if self.sol[r["y"]][r["x"]] == "R"]
        return bouchees

    def rect_district(self, district: dict) -> tuple[int, int, int, int]:
        """Le rectangle de tuiles d'un district — chaque rue frontiere coupee
        en deux, pour qu'un char sur le boulevard appartienne a un quartier et
        a un seul."""
        bx, by = district["bx"], district["by"]
        bx1, by1 = bx + len(district["plan"][0]), by + len(district["plan"])
        x0 = 0 if bx == 0 else self.xr[bx] + RUES_V[bx] // 2
        y0 = 0 if by == 0 else self.yr[by] + RUES_H[by] // 2
        x1 = self.largeur if bx1 == self.nc else self.xr[bx1] + RUES_V[bx1] // 2
        y1 = self.hauteur if by1 == self.nr else self.yr[by1] + RUES_H[by1] // 2
        return x0, y0, x1 - x0, y1 - y0

    def zones(self) -> list[dict]:
        """Les districts d'abord, leurs cours de gang ensuite : `Monde.zoneA`
        garde la DERNIERE qui contient le point, donc la plus precise."""
        sortie = []
        for district in DISTRICTS:
            x, y, largeur, hauteur = self.rect_district(district)
            sortie.append({"slug": district["slug"], "nom": district["nom"],
                           "district": district["slug"], "x": x, "y": y, "l": largeur, "h": hauteur,
                           "gang": None, "brume": bool(district.get("brume")),
                           "pietons": district["pietons"], "vehicules": district["vehicules"],
                           "police": district["police"], "rythme": list(district["rythme"])})
        for district in DISTRICTS:
            if not district.get("gang"):
                continue
            cour = self._enveloppe("g", district)
            if not cour:
                continue
            sortie.append({**cour, "slug": district["gang"], "nom": district["gang_nom"],
                           "district": district["slug"], "gang": district["gang"], "brume": False,
                           "pietons": 10, "vehicules": 3, "police": 0,
                           "rythme": list(district["rythme"])})
        bassin = self._enveloppe("~q", district_par_slug("faubourg"))
        if bassin:
            sortie.append({**bassin, "slug": "port", "nom": "Le bassin", "district": "faubourg",
                           "gang": None, "brume": True, "pietons": 6, "vehicules": 2,
                           "police": 1, "rythme": [0.8, 1.0, 1.0]})
        return sortie

    def _enveloppe(self, glyphes: str, district: dict | None = None) -> dict | None:
        """Le rectangle qui contient tous les ilots de ces types, rues comprises."""
        borne = self.rect_district(district) if district else None
        rects = []
        for glyphe, x, y, largeur, hauteur in self.regions():
            if glyphe not in glyphes:
                continue
            if borne and not (borne[0] <= x and x + largeur <= borne[0] + borne[2]
                              and borne[1] <= y and y + hauteur <= borne[1] + borne[3]):
                continue
            rects.append((x, y, largeur, hauteur))
        if not rects:
            return None
        x0 = min(r[0] for r in rects)
        y0 = min(r[1] for r in rects)
        x1 = max(r[0] + r[2] for r in rects)
        y1 = max(r[1] + r[3] for r in rects)
        marge = 2 * TROTTOIR
        x0, y0 = max(0, x0 - marge), max(0, y0 - marge)
        x1 = min(self.largeur, x1 + marge)
        y1 = min(self.hauteur, y1 + marge)
        return {"x": x0, "y": y0, "l": x1 - x0, "h": y1 - y0}


def generer(plan: tuple[str, ...] = PLAN, graine: int = GRAINE) -> dict:
    chantier = _Chantier(plan, graine)
    chantier.eaux()
    chantier.rues()
    chantier.croisements()
    chantier.ilots()
    ponts = chantier.ponts()
    chantier.lampadaires()
    chantier.bornes()
    # ⚠️ Apres les ilots, les ponts et le decor : une rampe se juge sur la ville
    # FINIE. Avant les paquets et les ambulants, pour que la piste d'elan soit
    # reservee quand ils cherchent leur place.
    chantier.poser_les_rampes()
    ambulants = chantier.ambulants()
    paquets = chantier.paquets()
    # ⚠️ Apres les ilots ET les ponts : on tague des murs qui existent, et on
    # ne tague pas une vitrine (les devantures ont deja reserve les leurs).
    chantier.graffitis_sur_les_murs()

    terminus = next(p for p in chantier.points if p["slug"] == "terminus")
    depart = (terminus["x"], terminus["y"])
    bouchees = chantier.boucher_les_poches(depart)
    if bouchees > chantier.largeur * chantier.hauteur // 50:
        raise ValueError(f"{bouchees} tuiles enclavees : un gabarit enferme la ville")

    return {
        "slug": "baie_des_brumes",
        "nom": "Baie-des-Brumes",
        "graine": graine,
        "districts": [{"slug": d["slug"], "nom": d["nom"], "gang": d["gang"],
                       "eau": bool(d.get("eau"))} for d in DISTRICTS],
        "largeur": chantier.largeur,
        "hauteur": chantier.hauteur,
        "tuile_px": TUILE_PX,
        "grille": {"colonnes": list(COLONNES), "rangees": list(RANGEES),
                   "rues_v": list(RUES_V), "rues_h": list(RUES_H), "trottoir": TROTTOIR},
        "sol": ["".join(ligne) for ligne in chantier.sol],
        "voie": ["".join(ligne) for ligne in chantier.voie],
        "arrets": chantier.arrets,
        "ponts": ponts,
        "intersections": chantier.intersections,
        "portes": chantier.portes,
        "lampes": chantier.lampes,
        "decor": chantier.decor,
        "rampes": chantier.rampes,
        "devantures": chantier.devantures,
        "graffitis": chantier.graffitis,
        "fourriere": chantier.fourriere,
        "ambulants": ambulants,
        "paquets": paquets,
        "zones": chantier.zones(),
        "points_interet": chantier.points,
        "apparition": {"joueur": {"x": depart[0], "y": depart[1]}},
        "interieurs": INTERIEURS,
        "tuiles_bouchees": bouchees,
    }

# --- Les interieurs ---------------------------------------------------------


def _salle(slug: str, nom: str, largeur: int, hauteur: int,
           meubles: tuple = (), points: tuple = ()) -> dict:
    """Une piece : des murs, un plancher, une porte au sud, des meubles."""
    grille = [["t"] * largeur for _ in range(hauteur)]
    for x in range(largeur):
        grille[0][x] = "B"
        grille[hauteur - 1][x] = "B"
    for y in range(hauteur):
        grille[y][0] = "B"
        grille[y][largeur - 1] = "B"
    for x in range(2, largeur - 2, 3):
        grille[0][x] = "W"
    px = largeur // 2
    grille[hauteur - 1][px] = "D"
    for mx, my, glyphe in meubles:
        grille[my][mx] = glyphe
    return {
        "slug": slug,
        "nom": nom,
        "largeur": largeur,
        "hauteur": hauteur,
        "sol": ["".join(ligne) for ligne in grille],
        "sortie": {"x": px, "y": hauteur - 1},
        "apparition": {"x": px, "y": hauteur - 2},
        "points": [dict(p) for p in points],
    }


def _comptoir(y: int, x0: int, x1: int) -> tuple:
    return tuple((x, y, "c") for x in range(x0, x1 + 1))


INTERIEURS: dict[str, dict] = {
    "terminus": _salle("terminus", "Terminus Baie-des-Brumes", 15, 8,
                       meubles=_comptoir(2, 2, 5),
                       points=({"type": "guichet", "x": 3, "y": 3},)),
    "planque": _salle("planque", "La planque de Rocco", 13, 8,
                      meubles=((2, 2, "c"), (3, 2, "c"), (10, 2, "c")),
                      points=({"type": "lit", "x": 3, "y": 3},
                              {"type": "coffre", "x": 10, "y": 3},
                              {"type": "garde_robe", "x": 6, "y": 2})),
    "garage": _salle("garage", "Garage Rocco Bandini", 15, 9,
                     meubles=_comptoir(2, 2, 4) + ((11, 2, "c"), (12, 2, "c")),
                     points=({"type": "vendre", "x": 3, "y": 3},
                             {"type": "reparer", "x": 11, "y": 3},
                             {"type": "repeindre", "x": 7, "y": 3})),
    "armurerie": _salle("armurerie", "Chez Gus", 13, 8,
                        meubles=_comptoir(3, 3, 9),
                        points=({"type": "acheter", "x": 6, "y": 4},)),
    "vetements": _salle("vetements", "Boutique Rosa", 13, 8,
                        meubles=_comptoir(3, 2, 4) + ((9, 2, "c"), (10, 2, "c")),
                        points=({"type": "acheter", "x": 6, "y": 4},)),
    "poste": _salle("poste", "Poste de police", 15, 9,
                    meubles=_comptoir(2, 4, 10),
                    points=({"type": "sortie_prison", "x": 7, "y": 4},
                            {"type": "casier", "x": 3, "y": 3})),
    "hopital": _salle("hopital", "Hôpital de Baie-des-Brumes", 15, 9,
                      meubles=_comptoir(2, 5, 9),
                      points=({"type": "soigner", "x": 7, "y": 4},)),
    "bar": _salle("bar", "Bar Le Brouillard", 13, 8,
                  meubles=_comptoir(3, 2, 8),
                  points=({"type": "caisse", "x": 5, "y": 4},
                          {"type": "contact", "x": 9, "y": 3})),
    "casse_croute": _salle("casse_croute", "Casse-croûte du Faubourg", 13, 8,
                           meubles=_comptoir(3, 3, 9),
                           points=({"type": "hotdog", "x": 6, "y": 4},
                                   {"type": "sergent", "x": 10, "y": 5})),
    "kiosque": _salle("kiosque", "Kiosque de Madame Thibodeau", 9, 6,
                      meubles=_comptoir(2, 2, 6),
                      points=({"type": "caisse", "x": 4, "y": 3},
                              {"type": "journal", "x": 6, "y": 3})),
    # v2 / M8 — un arret par district. ⚠️ Chaque point doit etre d'un type que
    # `missions.js` sait servir : un comptoir qui ne donne rien est une porte
    # qu'on ouvre pour rien.
    "depanneur": _salle("depanneur", "Dépanneur Chez Ti-Paul", 13, 8,
                        meubles=_comptoir(3, 2, 6) + ((9, 2, "c"), (10, 2, "c")),
                        points=({"type": "caisse", "x": 4, "y": 4},
                                {"type": "journal", "x": 9, "y": 3})),
    "hotel": _salle("hotel", "Hôtel Bandini", 15, 9,
                    meubles=_comptoir(2, 3, 7) + ((11, 3, "c"),),
                    points=({"type": "caisse", "x": 5, "y": 3},
                            {"type": "lit", "x": 11, "y": 4})),
    "cantine": _salle("cantine", "Cantine des Quais", 13, 8,
                      meubles=_comptoir(3, 3, 9),
                      points=({"type": "hotdog", "x": 6, "y": 4},
                              {"type": "caisse", "x": 3, "y": 4})),
    "usine": _salle("usine", "Usine Prévost", 15, 9,
                    meubles=_comptoir(2, 2, 5) + _comptoir(6, 9, 12),
                    points=({"type": "caisse", "x": 3, "y": 3},)),
    # ⚠️ Le comptoir de la fourriere est le SEUL point d'ou l'on ressort avec
    # un char : `missions.js` y montre le lot et ce que chacun coute.
    "fourriere": _salle("fourriere", "Fourrière municipale", 13, 8,
                        meubles=_comptoir(3, 2, 7) + ((10, 2, "c"),),
                        points=({"type": "fourriere", "x": 4, "y": 4},)),
    "phare": _salle("phare", "Le phare de La Pointe", 9, 7,
                    meubles=((2, 2, "c"), (6, 2, "c")),
                    points=({"type": "lit", "x": 6, "y": 3},
                            {"type": "journal", "x": 2, "y": 3})),
}


def exporter() -> dict:
    carte = generer()
    carte["legende"] = LEGENDE
    return carte


# --- Outils de verification (les juges des tests) ---------------------------


def solidite(glyphe: str) -> int:
    return int(LEGENDE.get(glyphe, {}).get("solide", 0))


def marchable(glyphe: str) -> bool:
    return solidite(glyphe) in (0, 3)


def routier(glyphe: str) -> bool:
    return bool(LEGENDE.get(glyphe, {}).get("route"))


def composantes_marchables(carte: dict) -> list[set[tuple[int, int]]]:
    """Les groupes de tuiles marchables reliees entre elles (4-connexite)."""
    sol = carte["sol"]
    vues: set[tuple[int, int]] = set()
    groupes = []
    for y, ligne in enumerate(sol):
        for x, glyphe in enumerate(ligne):
            if not marchable(glyphe) or (x, y) in vues:
                continue
            groupe: set[tuple[int, int]] = set()
            pile = [(x, y)]
            while pile:
                cx, cy = pile.pop()
                if (cx, cy) in groupe:
                    continue
                if not (0 <= cy < len(sol) and 0 <= cx < len(sol[cy])):
                    continue
                if not marchable(sol[cy][cx]):
                    continue
                groupe.add((cx, cy))
                pile.extend(((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)))
            vues |= groupe
            groupes.append(groupe)
    return groupes


def direction_voie(carte: dict, x: int, y: int) -> tuple[int, int] | None:
    """Le sens impose a cette tuile, ou None (croisement ou hors route)."""
    fleche = carte["voie"][y][x]
    if fleche in PAS:
        return PAS[fleche]
    if fleche == "S":
        return PAS.get(carte["arrets"].get(f"{x},{y}", ""))
    return None


def suivre_voie(carte: dict, x: int, y: int) -> list[tuple[int, int]]:
    """Les tuiles ou peut aller un vehicule qui respecte les fleches.

    Sur une voie : la tuile suivante. Sur un croisement : les quatre voisines
    routieres, SAUF celles qui pointent vers nous (on n'entre pas a contresens).
    """
    voie = carte["voie"]
    hauteur, largeur = len(voie), len(voie[0])
    if voie[y][x] == ".":
        return []
    pas = direction_voie(carte, x, y)
    if pas:
        candidats = [(x + pas[0], y + pas[1])]
    else:
        candidats = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    sorties = []
    for cx, cy in candidats:
        if not (0 <= cx < largeur and 0 <= cy < hauteur) or voie[cy][cx] == ".":
            continue
        if pas is None:
            voisine = direction_voie(carte, cx, cy)
            if voisine and (cx + voisine[0], cy + voisine[1]) == (x, y):
                continue
        sorties.append((cx, cy))
    return sorties


def tuiles_voie(carte: dict) -> list[tuple[int, int]]:
    return [(x, y) for y, ligne in enumerate(carte["voie"])
            for x, fleche in enumerate(ligne) if fleche != "."]


def voies_bloquees(carte: dict) -> tuple[set, set]:
    """(tuiles qu'on ne peut pas atteindre, tuiles d'ou l'on ne revient pas).

    Les deux ensembles vides = les rues sont FORTEMENT connexes : depuis
    n'importe quelle tuile de rue on rejoint n'importe quelle autre. Un sens
    interdit pose a l'envers, une bretelle sans sortie, un croisement muet :
    tout cela se voit ici avant de se voir a l'ecran.
    """
    toutes = tuiles_voie(carte)
    if not toutes:
        return set(), set()
    depart = toutes[0]
    avant: dict[tuple[int, int], list] = {}
    arriere: dict[tuple[int, int], list] = {}
    for tuile in toutes:
        avant[tuile] = suivre_voie(carte, *tuile)
    for tuile, sorties in avant.items():
        for sortie in sorties:
            arriere.setdefault(sortie, []).append(tuile)

    def parcourir(graphe):
        vues = {depart}
        pile = [depart]
        while pile:
            courant = pile.pop()
            for voisin in graphe.get(courant, ()):
                if voisin not in vues:
                    vues.add(voisin)
                    pile.append(voisin)
        return vues

    ensemble = set(toutes)
    return ensemble - parcourir(avant), ensemble - parcourir(arriere)
