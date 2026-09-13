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

from . import magasins

TUILE_PX = 16

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
    "R": {"nom": "rampe", "route": True, "rampe": True},
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

PAS = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}

TOITS = "BEO"

# --- Le plan du Faubourg ----------------------------------------------------

#: 8 blocs d'est en ouest, 6 du nord au sud. Le terminus au nord-ouest (on
#: debarque de l'autobus), le port au sud-ouest, la banlieue a l'est, la cour
#: des Cravates au centre (quatre blocs fusionnes), une place publique au
#: milieu et un parc a cheval sur deux blocs.
PLAN: tuple[str, ...] = (
    "Tccchhhh",
    "cMcp<hAh",
    "ccGKohhh",
    "PcBcg<hh",
    "cCcc^^hH",
    "~~qqcccc",
)

#: ⚠️ Aucune colonne n'a la largeur de sa voisine, aucune rangee la hauteur de
#: la sienne : c'est la premiere source d'irregularite, et la moins chere.
COLONNES = (13, 9, 12, 16, 10, 14, 9, 12)
RANGEES = (9, 12, 8, 11, 9, 13)

#: La largeur de chaque rue, trottoirs compris. 8 = boulevard (4 voies),
#: 6 = rue (2 voies). Il y a une rue de plus que de blocs dans chaque sens.
RUES_V = (8, 6, 8, 6, 6, 8, 6, 6, 8)
RUES_H = (8, 6, 8, 6, 8, 6, 8)

TROTTOIR = 2
GRAINE = 20260912

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
}

FUSIONS = {"<": (-1, 0), "^": (0, -1)}


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
        self.lampes: list[dict] = []
        self.intersections: list[dict] = []
        self.arrets: dict[str, str] = {}
        self.reserve: set[tuple[int, int]] = set()
        self.occupe: set[tuple[int, int]] = set()

    # --- Trame --------------------------------------------------------------

    def rue_v_existe(self, i: int, j: int) -> bool:
        """La rue verticale `i` longe-t-elle la rangee de blocs `j` ?"""
        if i <= 0 or i >= self.nc:
            return True                      # les rues du pourtour, jamais avalees
        return self.maitre[(i - 1, j)] != self.maitre[(i, j)]

    def rue_h_existe(self, i: int, j: int) -> bool:
        if j <= 0 or j >= self.nr:
            return True
        return self.maitre[(i, j - 1)] != self.maitre[(i, j)]

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
                nord = j > 0 and self.rue_v_existe(i, j - 1)
                sud = j < self.nr and self.rue_v_existe(i, j)
                ouest = i > 0 and self.rue_h_existe(i - 1, j)
                est = i < self.nc and self.rue_h_existe(i, j)
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
            if glyphe in SPECIAUX:
                self._ilot_bati(x, y, largeur, hauteur, special=SPECIAUX[glyphe])
            elif glyphe == "c":
                self._ilot_bati(x, y, largeur, hauteur)
            elif glyphe == "h":
                self._ilot_bati(x, y, largeur, hauteur, genre="maisons")
            elif glyphe == "g":
                self._ilot_bati(x, y, largeur, hauteur, genre="gang")
            elif glyphe == "p":
                self._parc(x, y, largeur, hauteur, kiosque=not kiosque_pose)
                kiosque_pose = True
            elif glyphe == "o":
                self._place(x, y, largeur, hauteur)
            elif glyphe == "q":
                self._quai(x, y, largeur, hauteur)
            elif glyphe == "~":
                self._eau(x, y, largeur, hauteur)
            else:  # pragma: no cover - garde-fou de relecture du plan
                raise ValueError(f"glyphe de plan inconnu : {glyphe!r}")

    def _bandes(self, y: int, hauteur: int) -> list[tuple[int, int]]:
        """Un ilot profond se coupe en bandes : ruelle, batiments, devant.

        Sans cela, un superbloc de 28 tuiles de haut serait un seul batiment
        monstrueux ; avec, il a un coeur de ruelles comme un vrai pate de
        maisons.
        """
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
        devant = {"maisons": ","}.get(genre, ".")
        mini = 4 if genre == "maisons" else 5
        parcelles: list[tuple[tuple[int, int, int, int], bool]] = []
        for by, bh in self._bandes(y, hauteur):
            self.rect(x, by, largeur, 2, "x")                      # ruelle derriere
            self.rect(x, by + bh - 2, largeur, 2, devant)           # devant
            zy, zh = by + 2, bh - 4
            if zh < 3:
                continue
            self.rect(x, zy, largeur, zh, "," if genre == "maisons" else ".")
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
                self.rect(px, py, pl, ph, "p")
            else:
                self._jardin(px, py, pl, ph)
        if facades_vedette:
            self.poser_porte(facades_vedette, special)
        for facades, _, _ in batiments:
            self.poser_porte(facades)
        for _ in range(max(1, largeur // 10)):
            self.poser_decor("poubelle", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, 1))

    def _contenu(self, genre: str) -> str:
        tirage = self.des.flottant()
        if genre == "maisons":
            return "bati" if tirage < 0.74 else ("jardin" if tirage < 0.92 else "stationnement")
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
        vitrines = {"commerces": 0.5, "maisons": 0.12, "gang": 0.08}.get(genre, 0.3)
        if force:
            # Un batiment garanti garde sa masse : ni cour ni coin mordu.
            tuiles = {(bx + i, by + j) for j in range(bh) for i in range(bl)}
        return self.batiment_forme(tuiles, vitrines)

    def _terrain_vague(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.rect(x, y, largeur, hauteur, ",")
        for i in range(largeur):
            if self.des.chance(0.5):
                self.sol[y + hauteur - 1][x + i] = "f"
        for _ in range(max(1, largeur * hauteur // 12)):
            self.poser_decor("debris", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    def _jardin(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.rect(x, y, largeur, hauteur, ",")
        for _ in range(max(1, largeur * hauteur // 10)):
            self.poser_decor(self.des.choix(("arbre", "buisson")),
                             x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    # --- Parc, place, port --------------------------------------------------

    def _parc(self, x: int, y: int, largeur: int, hauteur: int, kiosque: bool = False) -> None:
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
            self._allee(depart, centre)
        self.rect(centre[0] - 2, centre[1] - 2, 5, 5, ".")
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
                    if self.sol[ey + j][ex + i] == ".":
                        continue
                    self.sol[ey + j][ex + i] = "s" if bord else "~"
        if kiosque:
            kx = x + largeur - self.des.entier(7, 9)
            ky = y + hauteur - 5
            facades = self.batiment_forme({(kx + i, ky + j) for j in range(3) for i in range(4)}, 0.6)
            self.poser_porte(facades, {"slug": "kiosque", "interieur": "kiosque",
                                       "nom": "Kiosque de Madame Thibodeau"})
        for _ in range(largeur * hauteur // 14):
            self.poser_decor("arbre", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        for _ in range(largeur * hauteur // 40):
            self.poser_decor("banc", x + self.des.entier(1, largeur - 2),
                             y + self.des.entier(1, hauteur - 2))
        for _ in range(largeur * hauteur // 30):
            self.poser_decor("buisson", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    def _allee(self, depart: tuple[int, int], arrivee: tuple[int, int]) -> None:
        """Une allee de deux tuiles, avec un coude au hasard — jamais tout droit."""
        dx, dy = depart
        ax, ay = arrivee
        coude = dx + (ax - dx) * self.des.entier(2, 8) // 10
        for x in range(min(dx, coude), max(dx, coude) + 1):
            self.rect(x, dy, 1, 2, ".")
        for y in range(min(dy, ay), max(dy, ay) + 1):
            self.rect(coude, y, 2, 1, ".")
        for x in range(min(coude, ax), max(coude, ax) + 1):
            self.rect(x, ay, 1, 2, ".")

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

    def _eau(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Un bassin a rive irreguliere : du sable qui avance et recule."""
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "~")
        profondeur = 2
        for i in range(largeur):
            profondeur = max(0, min(4, profondeur + self.des.entier(-1, 1)))
            for j in range(profondeur):
                self.sol[y + j][x + i] = "s"
                self.sol[y + hauteur - 1 - j][x + i] = "s"
        profondeur = 2
        for j in range(hauteur):
            profondeur = max(0, min(3, profondeur + self.des.entier(-1, 1)))
            for i in range(profondeur):
                self.sol[y + j][x + i] = "s"
                self.sol[y + j][x + largeur - 1 - i] = "s"

    # --- Decor de rue et finitions -----------------------------------------

    def lampadaires(self) -> None:
        """Deux coins opposes par croisement : de la lumiere ou l'on tourne."""
        for inter in self.intersections:
            for dx, dy in ((-1, -1), (inter["l"], inter["h"])):
                x, y = inter["x"] + dx, inter["y"] + dy
                if self.poser_decor("lampadaire", x, y):
                    self.lampes.append({"x": x, "y": y})

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
        return bouchees

    def zones(self) -> list[dict]:
        sortie = [{"slug": "faubourg", "nom": "Le Faubourg", "x": 0, "y": 0,
                   "l": self.largeur, "h": self.hauteur, "gang": None,
                   "pietons": 26, "vehicules": 12, "police": 2}]
        gang = self._enveloppe("g")
        if gang:
            sortie.append({**gang, "slug": "cravates", "nom": "Les Cravates", "gang": "cravates",
                           "pietons": 10, "vehicules": 3, "police": 0})
        port = self._enveloppe("~q")
        if port:
            sortie.append({**port, "slug": "port", "nom": "Le bassin", "gang": None,
                           "pietons": 6, "vehicules": 2, "police": 1})
        return sortie

    def _enveloppe(self, glyphes: str) -> dict | None:
        """Le rectangle qui contient tous les ilots de ces types, rues comprises."""
        rects = [(x, y, largeur, hauteur) for glyphe, x, y, largeur, hauteur in self.regions()
                 if glyphe in glyphes]
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
    chantier.rues()
    chantier.croisements()
    chantier.ilots()
    chantier.lampadaires()
    chantier.bornes()
    ambulants = chantier.ambulants()

    terminus = next(p for p in chantier.points if p["slug"] == "terminus")
    depart = (terminus["x"], terminus["y"])
    bouchees = chantier.boucher_les_poches(depart)
    if bouchees > chantier.largeur * chantier.hauteur // 50:
        raise ValueError(f"{bouchees} tuiles enclavees : un gabarit enferme la ville")

    return {
        "slug": "faubourg",
        "nom": "Le Faubourg",
        "graine": graine,
        "largeur": chantier.largeur,
        "hauteur": chantier.hauteur,
        "tuile_px": TUILE_PX,
        "grille": {"colonnes": list(COLONNES), "rangees": list(RANGEES),
                   "rues_v": list(RUES_V), "rues_h": list(RUES_H), "trottoir": TROTTOIR},
        "sol": ["".join(ligne) for ligne in chantier.sol],
        "voie": ["".join(ligne) for ligne in chantier.voie],
        "arrets": chantier.arrets,
        "intersections": chantier.intersections,
        "portes": chantier.portes,
        "lampes": chantier.lampes,
        "decor": chantier.decor,
        "ambulants": ambulants,
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
