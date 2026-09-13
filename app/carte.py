"""La carte de Baie-des-Brumes — un plan de blocs, des gabarits, un generateur.

Le Faubourg n'est pas dessine tuile par tuile : il est DECRIT par un plan de
blocs (8 x 6) et rebati par `generer(plan, graine)`. Six lignes qu'on relit d'un
coup d'oeil valent mieux que 110 lignes de 168 glyphes — et un gabarit corrige
corrige toute la ville d'un coup.

    minuscule = quartier ordinaire   c commerces · h habitations · g gang
                                     p parc · q quai · ~ eau
    MAJUSCULE = batiment garanti     T terminus · M armurerie · A vetements
                                     G garage · K planque · P poste · H hopital
                                     B bar · C casse-croute

Entre les blocs, des rues de 8 tuiles : 2 trottoirs, 4 voies (deux par sens,
circulation a droite), 2 trottoirs. Le champ `voie` dit ou va un vehicule depuis
chaque tuile : `> < ^ v` une voie, `+` un croisement (on en sort par ou on veut,
sauf a contresens), `S` une ligne d'arret — sa direction est dans `arrets`, pas
dans le glyphe — et `.` pas de route du tout.

⚠️ Les rues du bord touchent le bord de la carte : chaque tuile de rue du
pourtour tombe donc dans un croisement, et AUCUNE fleche ne pointe hors carte.
C'est ce qui rend les voies fortement connexes (juge `voies_bloquees`).

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

# --- Le plan du Faubourg ----------------------------------------------------

#: 8 blocs d'est en ouest, 6 du nord au sud. Le terminus au nord-ouest (on
#: debarque de l'autobus), le port au sud-ouest, la banlieue a l'est, le
#: territoire des Cravates au centre-sud.
PLAN: tuple[str, ...] = (
    "Tccchhhh",
    "cMcphhAh",
    "ccGKchhh",
    "PcBcgghh",
    "cCccggcH",
    "~~qqcccc",
)

BLOC_L, BLOC_H = 12, 9          # interieur d'un bloc, en tuiles
ROUTE = 8                       # 2 trottoirs + 4 voies + 2 trottoirs
TROTTOIR = 2
VOIE_L = ROUTE - 2 * TROTTOIR   # 4 voies de 1 tuile

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
        return a + self.suivant() % (b - a + 1)

    def chance(self, p: float) -> bool:
        return self.flottant() < p

    def choix(self, options):
        return options[self.suivant() % len(options)]


class _Chantier:
    """L'echafaudage : on pose les rues, puis les blocs, puis le decor."""

    def __init__(self, plan: tuple[str, ...], graine: int) -> None:
        self.plan = plan
        self.blocs_l = len(plan[0])
        self.blocs_h = len(plan)
        self.largeur = (self.blocs_l + 1) * ROUTE + self.blocs_l * BLOC_L
        self.hauteur = (self.blocs_h + 1) * ROUTE + self.blocs_h * BLOC_H
        self.sol = [[","] * self.largeur for _ in range(self.hauteur)]
        self.voie = [["."] * self.largeur for _ in range(self.hauteur)]
        self.des = Des(graine)
        self.portes: list[dict] = []
        self.points: list[dict] = []
        self.decor: list[dict] = []
        self.lampes: list[dict] = []
        self.intersections: list[dict] = []
        self.arrets: dict[str, str] = {}
        self.reserve: set[tuple[int, int]] = set()   # pas de decor ici (devants de porte)
        self.occupe: set[tuple[int, int]] = set()    # deja du decor

    # --- Poser des tuiles ---------------------------------------------------

    def rect(self, x: int, y: int, largeur: int, hauteur: int, glyphe: str) -> None:
        for j in range(y, min(y + hauteur, self.hauteur)):
            for i in range(x, min(x + largeur, self.largeur)):
                self.sol[j][i] = glyphe

    def batiment(self, x: int, y: int, largeur: int, hauteur: int, *, vitrines: float = 0.0,
                 special: dict | None = None) -> int:
        """Toit sur hauteur-1 rangees, facade au sud. Rend la colonne de la porte.

        Le toit est tire au sort parmi trois : vu d'en haut, c'est la SEULE
        chose qui separe deux batiments colles l'un a l'autre.
        """
        toit = self.des.choix("BEO")
        for j in range(hauteur - 1):
            for i in range(largeur):
                self.sol[y + j][x + i] = toit
        fy = y + hauteur - 1
        for i in range(largeur):
            bord = i == 0 or i == largeur - 1
            self.sol[fy][x + i] = "W" if (not bord and self.des.chance(vitrines)) else "F"
        px = x + largeur // 2
        if special:
            self.sol[fy][px] = "D"
            self.portes.append({"x": px, "y": fy, "interieur": special["interieur"],
                                "lieu": special["slug"]})
            self.points.append({"type": special["slug"], "slug": special["slug"],
                                "nom": special["nom"], "x": px, "y": fy + 1})
            if special.get("porte_garage") and largeur >= 6:
                self.sol[fy][px - 2] = "G"
        else:
            self.sol[fy][px] = "d"
        # Le devant de la porte : marchable, degage, et interdit au decor.
        for j in (1, 2):
            if fy + j < self.hauteur:
                if self.sol[fy + j][px] == ",":
                    self.sol[fy + j][px] = "."
                self.reserve.add((px, fy + j))
        return px

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
        """Les couloirs verticaux puis horizontaux ; les croisements recollent."""
        for i in range(self.blocs_l + 1):
            x0 = i * (BLOC_L + ROUTE)
            for y in range(self.hauteur):
                for d in range(ROUTE):
                    x = x0 + d
                    if d < TROTTOIR or d >= ROUTE - TROTTOIR:
                        self.sol[y][x] = "."
                    else:
                        k = d - TROTTOIR
                        self.sol[y][x] = ("#", "|", "*", "|")[k]
                        self.voie[y][x] = "v" if k < 2 else "^"
        for j in range(self.blocs_h + 1):
            y0 = j * (BLOC_H + ROUTE)
            for x in range(self.largeur):
                for d in range(ROUTE):
                    y = y0 + d
                    if d < TROTTOIR or d >= ROUTE - TROTTOIR:
                        self.sol[y][x] = "."
                        self.voie[y][x] = "."
                    else:
                        k = d - TROTTOIR
                        self.sol[y][x] = ("#", "-", "+", "-")[k]
                        self.voie[y][x] = "<" if k < 2 else ">"

    def croisements(self) -> None:
        for j in range(self.blocs_h + 1):
            y0 = j * (BLOC_H + ROUTE)
            for i in range(self.blocs_l + 1):
                x0 = i * (BLOC_L + ROUTE)
                for dy in range(ROUTE):
                    for dx in range(ROUTE):
                        x, y = x0 + dx, y0 + dy
                        sur_x = TROTTOIR <= dx < ROUTE - TROTTOIR   # chaussee nord-sud
                        sur_y = TROTTOIR <= dy < ROUTE - TROTTOIR   # chaussee est-ouest
                        if sur_x and sur_y:
                            self.sol[y][x] = "#"
                        elif sur_y:      # la rue est-ouest traverse le trottoir
                            self.sol[y][x] = "="
                        elif sur_x:
                            self.sol[y][x] = ":"
                        else:
                            self.sol[y][x] = "."
                        self.voie[y][x] = "+" if (sur_x or sur_y) else "."
                self.intersections.append({"x": x0 + TROTTOIR, "y": y0 + TROTTOIR,
                                           "l": VOIE_L, "h": VOIE_L})
                self._lignes_arret(x0, y0)

    def _lignes_arret(self, x0: int, y0: int) -> None:
        """Une ligne d'arret juste avant chaque entree du croisement."""
        approches = []
        for k in (2, 3):                      # voies vers l'est
            approches.append((x0 - 1, y0 + TROTTOIR + k, ">"))
        for k in (0, 1):                      # voies vers l'ouest
            approches.append((x0 + ROUTE, y0 + TROTTOIR + k, "<"))
        for k in (0, 1):                      # voies vers le sud
            approches.append((x0 + TROTTOIR + k, y0 - 1, "v"))
        for k in (2, 3):                      # voies vers le nord
            approches.append((x0 + TROTTOIR + k, y0 + ROUTE, "^"))
        for x, y, direction in approches:
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                continue
            if self.voie[y][x] != direction:
                continue
            self.voie[y][x] = "S"
            self.arrets[f"{x},{y}"] = direction

    # --- Les blocs ----------------------------------------------------------

    def bloc_origine(self, bx: int, by: int) -> tuple[int, int]:
        return bx * (BLOC_L + ROUTE) + ROUTE, by * (BLOC_H + ROUTE) + ROUTE

    def blocs(self) -> None:
        kiosque_pose = False
        for by, ligne in enumerate(self.plan):
            for bx, glyphe in enumerate(ligne):
                ix, iy = self.bloc_origine(bx, by)
                if glyphe in SPECIAUX:
                    self._commerces(ix, iy, special=SPECIAUX[glyphe])
                elif glyphe == "c":
                    self._commerces(ix, iy)
                elif glyphe == "h":
                    self._habitations(ix, iy)
                elif glyphe == "g":
                    self._gang(ix, iy)
                elif glyphe == "p":
                    self._parc(ix, iy, kiosque=not kiosque_pose)
                    kiosque_pose = True
                elif glyphe == "q":
                    self._quai(ix, iy)
                elif glyphe == "~":
                    self.rect(ix, iy, BLOC_L, BLOC_H, "~")
                else:  # pragma: no cover - garde-fou de relecture du plan
                    raise ValueError(f"glyphe de plan inconnu : {glyphe!r}")

    def _segments(self, total: int, mini: int, maxi: int) -> list[tuple[int, int]]:
        """Decoupe `total` en morceaux de `mini` a `maxi`, sans trou ni reste."""
        out: list[tuple[int, int]] = []
        x = 0
        while total - x >= mini:
            largeur = self.des.entier(mini, maxi)
            if total - x - largeur < mini:
                largeur = total - x
            out.append((x, largeur))
            x += largeur
        if x < total and out:
            debut, largeur = out[-1]
            out[-1] = (debut, largeur + total - x)
        return out

    def _commerces(self, ix: int, iy: int, special: dict | None = None) -> None:
        self.rect(ix, iy, BLOC_L, 2, "x")            # ruelle derriere
        self.rect(ix, iy + 7, BLOC_L, 2, ".")        # trottoir devant
        if special:
            self.rect(ix, iy + 2, BLOC_L, 5, ",")
            self.batiment(ix + 2, iy + 2, BLOC_L - 4, 5, vitrines=0.35, special=special)
            for cote in (0, BLOC_L - 1):
                if self.des.chance(0.5):
                    self.poser_decor("arbre", ix + cote, iy + 5)
        else:
            for debut, largeur in self._segments(BLOC_L, 4, 6):
                self.batiment(ix + debut, iy + 2, largeur, 5, vitrines=0.55)
            if self.des.chance(0.35):
                self.rect(ix, iy + 7, self.des.entier(3, 5), 2, "p")
        for _ in range(2):
            self.poser_decor("poubelle", ix + self.des.entier(0, BLOC_L - 1),
                             iy + self.des.entier(0, 1))

    def _habitations(self, ix: int, iy: int) -> None:
        self.rect(ix, iy, BLOC_L, 2, "x")
        x = self.des.entier(0, 1)
        while x + 4 <= BLOC_L:
            largeur = self.des.entier(4, 5)
            if x + largeur > BLOC_L:
                break
            self.batiment(ix + x, iy + 4, largeur, 3)
            x += largeur + self.des.entier(1, 2)
        for i in range(BLOC_L):
            if (ix + i, iy + 8) not in self.reserve and self.des.chance(0.55):
                self.sol[iy + 8][ix + i] = "f"
        for _ in range(3):
            self.poser_decor("arbre", ix + self.des.entier(0, BLOC_L - 1), iy + self.des.entier(2, 3))
        for _ in range(2):
            self.poser_decor("buisson", ix + self.des.entier(0, BLOC_L - 1), iy + 7)

    def _gang(self, ix: int, iy: int) -> None:
        self.rect(ix, iy, BLOC_L, 2, "x")
        self.batiment(ix, iy + 2, BLOC_L, 5, vitrines=0.1)
        self.sol[iy + 6][ix + BLOC_L // 2 - 3] = "G"
        self.rect(ix, iy + 7, BLOC_L, 2, "p")
        for _ in range(2):
            self.poser_decor("caisse", ix + self.des.entier(0, BLOC_L - 1), iy + 1)

    def _parc(self, ix: int, iy: int, kiosque: bool = False) -> None:
        self.rect(ix, iy, BLOC_L, BLOC_H, ",")
        self.rect(ix, iy + 4, BLOC_L, 1, ".")          # allee est-ouest
        self.rect(ix + 5, iy, 2, BLOC_H, ".")          # allee nord-sud
        if kiosque:
            self.batiment(ix + 8, iy + 5, 4, 3, vitrines=0.5, special={
                "slug": "kiosque", "nom": "Kiosque de Madame Thibodeau", "interieur": "kiosque"})
        for _ in range(16):
            self.poser_decor("arbre", ix + self.des.entier(0, BLOC_L - 1),
                             iy + self.des.entier(0, BLOC_H - 1))
        for _ in range(4):
            self.poser_decor("banc", ix + self.des.entier(0, BLOC_L - 1), iy + 3)
        for _ in range(3):
            self.poser_decor("buisson", ix + self.des.entier(0, BLOC_L - 1),
                             iy + self.des.entier(5, 8))

    def _quai(self, ix: int, iy: int) -> None:
        self.rect(ix, iy, BLOC_L, BLOC_H, "Q")
        for _ in range(7):
            self.poser_decor("caisse", ix + self.des.entier(0, BLOC_L - 1),
                             iy + self.des.entier(0, BLOC_H - 1))

    # --- Decor de rue -------------------------------------------------------

    def lampadaires(self) -> None:
        """Deux coins opposes par croisement : de la lumiere ou l'on tourne."""
        for inter in self.intersections:
            for dx, dy in ((-1, -1), (VOIE_L, VOIE_L)):
                x, y = inter["x"] + dx, inter["y"] + dy
                if self.poser_decor("lampadaire", x, y):
                    self.lampes.append({"x": x, "y": y})

    def bornes(self) -> None:
        """Des bornes-fontaines sur le trottoir (elles arroseront, en M2)."""
        for inter in self.intersections:
            if not self.des.chance(0.30):
                continue
            x, y = inter["x"] + VOIE_L, inter["y"] - 1
            if 0 <= x < self.largeur and 0 <= y < self.hauteur and self.sol[y][x] == ".":
                self.sol[y][x] = "b"

    # --- Zones et sortie ----------------------------------------------------

    def zone_des_blocs(self, glyphes: str) -> dict | None:
        cases = [(bx, by) for by, ligne in enumerate(self.plan)
                 for bx, g in enumerate(ligne) if g in glyphes]
        if not cases:
            return None
        x0, y0 = self.bloc_origine(min(b for b, _ in cases), min(b for _, b in cases))
        x1, y1 = self.bloc_origine(max(b for b, _ in cases), max(b for _, b in cases))
        return {"x": x0 - ROUTE, "y": y0 - ROUTE,
                "l": x1 + BLOC_L + ROUTE - (x0 - ROUTE), "h": y1 + BLOC_H + ROUTE - (y0 - ROUTE)}

    def zones(self) -> list[dict]:
        out = [{"slug": "faubourg", "nom": "Le Faubourg", "x": 0, "y": 0,
                "l": self.largeur, "h": self.hauteur, "gang": None,
                "pietons": 26, "vehicules": 12, "police": 2}]
        gang = self.zone_des_blocs("g")
        if gang:
            out.append({**gang, "slug": "cravates", "nom": "Les Cravates", "gang": "cravates",
                        "pietons": 10, "vehicules": 3, "police": 0})
        port = self.zone_des_blocs("~q")
        if port:
            out.append({**port, "slug": "port", "nom": "Le bassin", "gang": None,
                        "pietons": 6, "vehicules": 2, "police": 1})
        return out


def generer(plan: tuple[str, ...] = PLAN, graine: int = GRAINE) -> dict:
    chantier = _Chantier(plan, graine)
    chantier.rues()
    chantier.croisements()
    chantier.blocs()
    chantier.lampadaires()
    chantier.bornes()

    terminus = next(p for p in chantier.points if p["slug"] == "terminus")
    return {
        "slug": "faubourg",
        "nom": "Le Faubourg",
        "graine": graine,
        "largeur": chantier.largeur,
        "hauteur": chantier.hauteur,
        "tuile_px": TUILE_PX,
        "bloc": {"l": BLOC_L, "h": BLOC_H, "route": ROUTE, "trottoir": TROTTOIR},
        "sol": ["".join(ligne) for ligne in chantier.sol],
        "voie": ["".join(ligne) for ligne in chantier.voie],
        "arrets": chantier.arrets,
        "intersections": chantier.intersections,
        "portes": chantier.portes,
        "lampes": chantier.lampes,
        "decor": chantier.decor,
        "zones": chantier.zones(),
        "points_interet": chantier.points,
        "apparition": {"joueur": {"x": terminus["x"], "y": terminus["y"] + 1}},
        "interieurs": INTERIEURS,
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
