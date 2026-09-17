"""Les lignes d'autobus de Baie-des-Brumes : un tracé, des arrêts, un horaire.

Demande de Martin (16 sept. 2026) : « des arrêts d'autobus pour se déplacer
réellement d'un arrêt à l'autre selon un tracé, et des bus qui passent aux
arrêts aussi ».

⚠️ **Python trace, JS roule.** Ce module calcule, une fois, sur la ville FINIE :
le tracé de chaque ligne (une boucle de tuiles qui obéit au champ de direction),
ses arrêts (une voie qui longe le trottoir, un abribus derrière), et l'horaire
que le navigateur suit. `vehicules.js` ne fait que conduire l'autobus le long du
tracé — il ne choisit jamais une rue. Toute la géométrie se juge donc ici.

⚠️ **Un tracé ne passe jamais là où la ville peut fermer.** Les entraves du
jour, les rues barrées, les bris d'aqueduc et les barrières qui arrêtent les
chars sont des LISTES que Python connaît d'avance : le tracé les contourne toutes,
et un autobus n'a jamais à décider quoi faire devant des cônes. C'est aussi pour
ça qu'aucune ligne ne va à La Pointe : le pont est barré tant que m2 n'est pas
faite, et c'est le seul lien.

⚠️ **Son propre ordre, après toute la ville.** Les abribus et leurs bancs se posent
après les chantiers : une ligne de plus ne déplace ni un arbre, ni un paquet, ni
une enseigne — un juge compare la ville avec et sans.
"""

from __future__ import annotations

import heapq

#: ⚠️ La couleur est celle de la CAISSE, et aucune n'est jaune : un autobus jaune
#: est un autobus scolaire (`SPRITES.autobus_scolaire`), il ne s'arrete pas aux abribus.
#: Les lignes. `passe_par` est une suite de lieux garantis (les mêmes d'une
#: graine à l'autre) : la ligne s'arrête devant chacun, dans cet ordre, et revient
#: au premier. ⚠️ Toutes partent du TERMINUS : c'est là qu'on débarque au premier
#: matin, et un terminus d'où ne part aucun autobus n'en est pas un.
LIGNES: tuple[dict, ...] = (
    {"numero": 1, "nom": "Le Faubourg", "couleur": "#d35400",
     "passe_par": ("terminus", "armurerie", "garage", "hopital", "casse_croute", "poste")},
    {"numero": 2, "nom": "Les Érables et les Quais", "couleur": "#2471a3",
     "passe_par": ("terminus", "depanneur", "hotel", "cantine", "poste")},
    {"numero": 3, "nom": "La Shop", "couleur": "#1e8449",
     "passe_par": ("terminus", "usine", "electronique", "hopital")},
)

#: Les arrêts d'une ligne, en tuiles de TRACÉ (pas à vol d'oiseau).
#: `ecart`     le plus court et le plus long écart entre deux arrêts d'une ligne ;
#: `droit`     les tuiles de voie droite qu'il faut avant et après l'arrêt : un
#:             autobus fait trois tuiles, et arrêté à cheval sur un passage
#:             piéton ou une ligne d'arrêt, il bloque le croisement ;
#: `voisin`    un arrêt d'une autre ligne à moins de ça, sur la même voie, SERT
#:             aux deux — deux abribus côte à côte, c'est un terminus ;
#: `rayon_nom` un lieu plus près que ça donne son nom à l'arrêt.
ARRETS: dict = {
    "ecart": (24, 42),
    "droit": 2,
    "voisin": 8,
    "rayon_nom": 18,
}

#: Ce que le navigateur suit. ⚠️ `vitesse_px` est la vitesse MOYENNE d'un autobus,
#: arrêts et feux compris : c'est elle qui place un autobus qu'on ne voit pas sur
#: son tracé (`Autobus.horaire`), et un autobus qu'on voit naître doit arriver à
#: l'arrêt à peu près quand l'horaire le dit.
HORAIRE: dict = {
    "vitesse_px": 1.0,           # px par image, en moyenne sur la boucle
    "arret_images": 150,         # portes ouvertes à chaque arrêt
    "tuiles_par_autobus": 220,   # un autobus par tant de tuiles de tracé
    "tarif": 3,                  # ce que coûte un passage, en dollars
    "rayon_monter_px": 34,       # à quelle distance de l'autobus on monte
}

#: Le coût d'un pas dans la recherche du tracé. ⚠️ Un VIRAGE coûte : sans lui,
#: deux chemins de même longueur se valent, et le tracé traverse une boîte de
#: croisement en escalier. Une voie qui ne longe PAS le trottoir coûte aussi :
#: sur un boulevard, l'autobus roule à droite, là où sont les arrêts.
COUT_VIRAGE = 4
COUT_VOIE_DU_MILIEU = 2
COUT_DEPORT = 3

#: Ce que vaut, en tuiles de marche, un arrêt tourné dans le sens du voyage.
SENS_DU_VOYAGE = 8

PAS = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}

#: ⚠️ **LE PARVIS DU TERMINUS RESTE NU**, sur tant de tuiles autour du point
#: d'apparition. C'est là que le car de l'ouverture dépose le cousin et qu'il
#: marche jusqu'à la porte — et c'est la première image du jeu. Mesuré le 16 sept.
#: 2026 : un abribus à deux tuiles de la porte arrêtait la balle du juge du
#: pistolet et empêchait Ti-Guy de revenir à son poste. Le mobilier de rue
#: (`mobilier.py`) le respecte aussi.
PARVIS = 6


def parvis(ville: dict) -> set[tuple[int, int]]:
    """Les tuiles du parvis du terminus, où rien de solide ne se pose."""
    x, y = ville["apparition"]["joueur"]["x"], ville["apparition"]["joueur"]["y"]
    return {(x + i, y + j) for i in range(-PARVIS, PARVIS + 1) for j in range(-PARVIS, PARVIS + 1)}

#: ⚠️ L'ABRI REGARDE LA RUE, et c'est le sens de la voie qui le dit : on roule à
#: droite, donc le trottoir — et l'abri derrière lui — est à droite du char. Un
#: autobus qui file vers l'est a son abri au SUD de la rue, ouvert vers le nord.
#: Le banc d'à côté regarde du même côté (`mobilier.BANCS_PAR_COTE`).
ABRIS = {"<": "abribus", ">": "abribus_nord", "v": "abribus_est", "^": "abribus_ouest"}
BANCS = {"<": "banc", ">": "banc_nord", "v": "banc_est", "^": "banc_ouest"}


def a_droite(dx: int, dy: int) -> tuple[int, int]:
    """La main droite d'un char qui roule dans ce sens (y vers le bas)."""
    return -dy, dx


class _Reseau:
    """Le graphe des voies d'une ville bâtie, et ce qu'on n'a pas le droit d'y faire."""

    def __init__(self, ville: dict) -> None:
        self.voie = ville["voie"]
        self.sol = ville["sol"]
        self.arrets = ville["arrets"]
        self.hauteur = len(self.voie)
        self.largeur = len(self.voie[0])
        self.boites: set[tuple[int, int]] = set()
        for inter in ville["intersections"]:
            for y in range(inter["y"], inter["y"] + inter["h"]):
                for x in range(inter["x"], inter["x"] + inter["l"]):
                    self.boites.add((x, y))
        #: ⚠️ TOUT ce que la ville peut fermer un jour, pas seulement ce qui est
        #: fermé aujourd'hui : un tracé ne change pas d'un jour à l'autre.
        self.interdites: set[tuple[int, int]] = set()
        rectangles = list(ville["fermetures"]) + list(ville["entraves"])
        rectangles += [b for b in ville["barrieres"] if "vehicule" in b["arrete"]]
        rectangles += list(ville["ponts"])
        for r in rectangles:
            for y in range(r["y"], r["y"] + r["h"]):
                for x in range(r["x"], r["x"] + r["l"]):
                    self.interdites.add((x, y))
        for a in ville["aqueducs"]:
            self.interdites.add((a["x"], a["y"]))
        self.parvis = parvis(ville)

    def dedans(self, x: int, y: int) -> bool:
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def sens(self, x: int, y: int) -> tuple[int, int] | None:
        fleche = self.voie[y][x]
        if fleche in PAS:
            return PAS[fleche]
        if fleche == "S":
            return PAS.get(self.arrets.get(f"{x},{y}", ""))
        return None

    def longe_le_trottoir(self, x: int, y: int) -> bool:
        """Une voie (une flèche, pas une ligne d'arrêt) qui a le trottoir à droite."""
        fleche = self.voie[y][x]
        if fleche not in PAS:
            return False
        rx, ry = a_droite(*PAS[fleche])
        return self.dedans(x + rx, y + ry) and self.sol[y + ry][x + rx] == "."

    def peut_sortir(self, x: int, y: int, d: tuple[int, int]) -> bool:
        """`Vehicules.peutSortir` : depuis cette tuile de boîte, tout droit dans ce
        sens à travers la boîte, trouve-t-on une voie qui va dans ce sens ?"""
        for _ in range(9):
            x, y = x + d[0], y + d[1]
            if not self.dedans(x, y) or (x, y) in self.interdites:
                return False
            if self.sens(x, y) == d:
                return True
            if self.voie[y][x] != "+":
                return False
        return False

    def sorties(self, x: int, y: int, d: tuple[int, int] | None):
        """Les pas permis depuis cette tuile quand on y roule dans le sens `d` —
        `carte.suivre_voie`, plus les règles de conduite du trafic : on ne sort
        d'une boîte que dans le sens de la voie qu'on prend, on ne TOURNE dans une
        boîte que là où ce virage mène à une voie (un virage à gauche se prend au
        fond, comme `prochaineCible`), et jamais sur une tuile que la ville peut
        fermer."""
        pas = self.sens(x, y)
        if pas:
            candidats = [(x + pas[0], y + pas[1], pas)]
        elif self.voie[y][x] == "+":
            candidats = [(x + dx, y + dy, (dx, dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        else:
            return
        for cx, cy, nd in candidats:
            if not self.dedans(cx, cy) or self.voie[cy][cx] == "." or (cx, cy) in self.interdites:
                continue
            if pas is None:
                voisine = self.sens(cx, cy)
                if voisine and voisine != nd:
                    continue
                if d is not None and nd != d and not self.peut_sortir(x, y, nd):
                    continue
            yield cx, cy, nd

    def chemin(self, depart: tuple[int, int], arrivee: tuple[int, int],
               un_virage: bool = True) -> list[tuple[int, int]] | None:
        """Le plus court trajet permis, virages, déports et voies du milieu comptés.

        ⚠️ **UN SEUL VIRAGE PAR BOÎTE.** Deux virages dans la même boîte, c'est un
        demi-tour au milieu du carrefour : le premier tracé le faisait pour
        servir un arrêt de l'autre côté de la rue, et l'autobus, arrêté en
        travers de la voie d'en face, attendait le char qui l'attendait. L'état
        de la recherche porte donc « a-t-on déjà tourné dans cette boîte ».
        """
        pas0 = self.sens(*depart)
        dist = {(depart, pas0, False): 0}
        avant: dict = {}
        tas = [(0, depart, pas0, False)]
        while tas:
            cout, (x, y), d, tourne = heapq.heappop(tas)
            if dist.get(((x, y), d, tourne)) != cout:
                continue
            if (x, y) == arrivee and cout > 0:
                trajet = [(x, y)]
                cle = ((x, y), d, tourne)
                while cle in avant:
                    cle = avant[cle]
                    trajet.append(cle[0])
                return trajet[::-1]
            dans_la_boite = self.voie[y][x] == "+"
            pas_possibles = [(cx, cy, nd, nd, d is not None and nd != d, False)
                             for cx, cy, nd in self.sorties(x, y, d)]
            # ⚠️ **LE DÉPORT** : un pas de côté DANS la boîte, le cap gardé. Sans lui,
            # une entrave possible sur la voie de droite poussait l'autobus sur la
            # voie du milieu, et il y restait jusqu'au prochain vrai virage —
            # 105 tuiles sans un seul arrêt sur la ligne 3, parce qu'un arrêt se
            # prend le long du trottoir. Changer de voie coûtait deux virages.
            if dans_la_boite and d is not None:
                for lx, ly in ((-d[1], d[0]), (d[1], -d[0])):
                    cx, cy = x + lx, y + ly
                    if (self.dedans(cx, cy) and self.voie[cy][cx] == "+" and (cx, cy) not in self.interdites
                            and self.peut_sortir(cx, cy, d)):
                        pas_possibles.append((cx, cy, (lx, ly), d, False, True))
            for cx, cy, _pas, cap, virage, deport in pas_possibles:
                if (virage or deport) and dans_la_boite and tourne and un_virage:
                    continue
                pas = 1 + (COUT_VIRAGE if virage else 0) + (COUT_DEPORT if deport else 0)
                if self.voie[cy][cx] in PAS and not self.longe_le_trottoir(cx, cy):
                    pas += COUT_VOIE_DU_MILIEU
                apres = (tourne or virage or deport) if self.voie[cy][cx] == "+" else False
                cle = ((cx, cy), cap, apres)
                if cout + pas < dist.get(cle, 1 << 60):
                    dist[cle] = cout + pas
                    avant[cle] = ((x, y), d, tourne)
                    heapq.heappush(tas, (cout + pas, (cx, cy), cap, apres))
        return None


def _libre_pour_l_abri(chantier, x: int, y: int, nus: set[tuple[int, int]] = frozenset()) -> bool:
    """La tuile derrière le trottoir peut-elle recevoir un abribus ?"""
    if not (0 <= x < chantier.largeur and 0 <= y < chantier.hauteur) or (x, y) in nus:
        return False
    if chantier.sol[y][x] not in ("_", ","):
        return False
    if (x, y) in chantier.reserve or (x, y) in chantier.occupe:
        return False
    # ⚠️ Ni devant une porte, ni JUSTE À CÔTÉ : les abords d'une porte sont
    # réservés sur deux tuiles de profondeur, pas de largeur.
    return not any((x + dx, y + dy) in chantier.reserve for dx in (-1, 0, 1) for dy in (-1, 0, 1))


def arret_possible(reseau: _Reseau, chantier, x: int, y: int) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """(le trottoir où l'on attend, la tuile de l'abribus) — ou None.

    Une voie droite qui longe le trottoir sur `droit` tuiles de part et d'autre,
    hors de toute boîte, et une tuile libre derrière le trottoir pour l'abri.
    """
    fleche = reseau.voie[y][x]
    if fleche not in PAS or (x, y) in reseau.boites:
        return None
    dx, dy = PAS[fleche]
    rx, ry = a_droite(dx, dy)
    droit = ARRETS["droit"]
    for k in range(-droit, droit + 1):
        tx, ty = x + dx * k, y + dy * k
        if not reseau.dedans(tx, ty) or reseau.voie[ty][tx] != fleche:
            return None
        if (tx, ty) in reseau.boites or (tx, ty) in reseau.interdites:
            return None
        if not reseau.longe_le_trottoir(tx, ty):
            return None
    # ⚠️ LE TRONÇON ENTIER EST OUVERT. Une voie ne change pas de voie hors d'une
    # boîte : un arrêt en aval d'un bris d'aqueduc possible n'a pas d'entrée, un
    # arrêt en amont n'a pas de sortie — mesuré sur la graine 7, où la ligne 2 ne
    # trouvait plus de tracé.
    for sens in (1, -1):
        tx, ty = x, y
        while reseau.dedans(tx, ty) and reseau.voie[ty][tx] == fleche:
            if (tx, ty) in reseau.interdites:
                return None
            tx, ty = tx + dx * sens, ty + dy * sens
    quai = (x + rx, y + ry)
    abri = (x + 2 * rx, y + 2 * ry)
    if quai in chantier.occupe or quai in chantier.reserve:
        return None
    if not _libre_pour_l_abri(chantier, *abri, reseau.parvis):
        return None
    return quai, abri


#: Combien d'arrêts candidats on essaie pour une étape avant de se rabattre sur
#: un tracé qui tourne deux fois dans une boîte. ⚠️ Chaque essai raté coûte une
#: recherche dans TOUTE la ville : il en faut peu.
ESSAIS_PAR_ETAPE = 4


def _boucle(reseau: _Reseau, choix: list[list[tuple[int, int]]]):
    """La boucle qui passe par une place de chaque étape, dans l'ordre : (boucle,
    indice de chaque étape, places retenues) — ou None.

    Pour chaque étape on prend la première place candidate qu'on sait rejoindre ;
    si aucune ne se rejoint en ne tournant qu'une fois par boîte, on accepte le
    double virage plutôt qu'une ligne qui ne dessert pas son lieu."""
    etapes = [choix[0][0]]
    boucle: list[tuple[int, int]] = []
    indices: list[int] = []
    for k in range(1, len(choix) + 1):
        depart = etapes[-1]
        cibles = choix[k][:ESSAIS_PAR_ETAPE] if k < len(choix) else [etapes[0]]
        trajet, cible = None, None
        for un_virage in (True, False):
            for c in cibles:
                trajet = reseau.chemin(depart, c, un_virage)
                if trajet is not None:
                    cible = c
                    break
            if trajet is not None:
                break
        if trajet is None:
            return None
        indices.append(len(boucle))
        boucle += trajet[:-1]
        if k < len(choix):
            etapes.append(cible)
    return boucle, indices, etapes


def coins(boucle: list[tuple[int, int]]) -> list[list[int]]:
    """La boucle réduite à ses coins : là où le sens change. Le navigateur la
    redéroule tuile par tuile (`Autobus.derouler`)."""
    n = len(boucle)
    sortie = []
    for i, (x, y) in enumerate(boucle):
        px, py = boucle[i - 1]
        nx, ny = boucle[(i + 1) % n]
        if (x - px, y - py) != (nx - x, ny - y) or i == 0:
            sortie.append([x, y])
    return sortie


def derouler(trace: list[list[int]]) -> list[tuple[int, int]]:
    """Le contraire de `coins` : chaque tuile de la boucle, dans l'ordre."""
    tuiles: list[tuple[int, int]] = []
    n = len(trace)
    for i in range(n):
        x, y = trace[i]
        nx, ny = trace[(i + 1) % n]
        dx = (nx > x) - (nx < x)
        dy = (ny > y) - (ny < y)
        while (x, y) != (nx, ny):
            tuiles.append((x, y))
            x, y = x + dx, y + dy
    return tuiles


def tracer(chantier, ville: dict) -> dict:
    """Les lignes, leurs arrêts et l'horaire, prêts pour le paquet. Pose aussi
    les abribus (et un banc à côté) dans `chantier.decor`."""
    reseau = _Reseau(ville)
    lieux = {p["slug"]: p for p in ville["points_interet"]}
    #: Toutes les voies où l'on POURRAIT s'arrêter, une fois pour toutes.
    possibles: dict[tuple[int, int], tuple] = {}
    for y in range(reseau.hauteur):
        for x in range(reseau.largeur):
            if reseau.voie[y][x] in PAS:
                place = arret_possible(reseau, chantier, x, y)
                if place:
                    possibles[(x, y)] = place
    arrets: dict[tuple[int, int], dict] = {}

    def voisin_existant(x: int, y: int) -> tuple[int, int] | None:
        fleche = reseau.voie[y][x]
        for (ax, ay), arret in arrets.items():
            if reseau.voie[ay][ax] == fleche and abs(ax - x) + abs(ay - y) <= ARRETS["voisin"]:
                return (ax, ay)
        return None

    lignes = []
    #: L'arrêt qui SERT un lieu (une étape d'une ligne) porte son nom, quoi qu'il
    #: arrive — même quand deux lignes le servent chacune d'un côté de la rue.
    lieux_des_etapes: dict[tuple[int, int], str] = {}
    for fiche in LIGNES:
        etapes = []
        passe_par = fiche["passe_par"]
        for rang, slug in enumerate(passe_par):
            lieu = lieux[slug]
            avant_lui = lieux[passe_par[rang - 1]]
            apres_lui = lieux[passe_par[(rang + 1) % len(passe_par)]]
            # ⚠️ **DU BON CÔTÉ DE LA RUE.** L'arrêt le plus proche du lieu est
            # souvent sur la voie d'en face : pour le servir, l'autobus faisait le
            # tour du bloc. On préfère la voie qui va déjà dans le sens du voyage
            # — d'où l'on vient vers où l'on va — quitte à marcher trois tuiles.
            tx, ty = apres_lui["x"] - avant_lui["x"], apres_lui["y"] - avant_lui["y"]
            norme = max(1.0, (tx * tx + ty * ty) ** 0.5)

            def note(t: tuple[int, int], deja_la: bool) -> float:
                dx, dy = PAS[reseau.voie[t[1]][t[0]]]
                ecart = abs(t[0] - lieu["x"]) + abs(t[1] - lieu["y"])
                return ecart - SENS_DU_VOYAGE * (dx * tx + dy * ty) / norme - (4 if deja_la else 0)

            proches = [t for t in possibles if abs(t[0] - lieu["x"]) + abs(t[1] - lieu["y"]) <= ARRETS["rayon_nom"]]
            choix = sorted([(note(t, True), t) for t in arrets if abs(t[0] - lieu["x"]) + abs(t[1] - lieu["y"]) <= ARRETS["rayon_nom"]]
                           + [(note(t, False), t) for t in proches])
            if not choix:
                choix = sorted((abs(t[0] - lieu["x"]) + abs(t[1] - lieu["y"]), t) for t in possibles)
            etapes.append([t for _note, t in choix])
        construite = _boucle(reseau, etapes)
        if construite is None:
            raise ValueError(f"ligne {fiche['numero']} : pas de tracé entre ses étapes")
        boucle, fixes, retenues = construite
        for slug, t in zip(passe_par, retenues):
            lieux_des_etapes.setdefault(t, lieux[slug]["nom"])
        n = len(boucle)
        choisis: list[int] = []
        mini, maxi = ARRETS["ecart"]
        for rang, i in enumerate(fixes):
            choisis.append(i)
            fin = fixes[rang + 1] if rang + 1 < len(fixes) else n + fixes[0]
            dernier = i
            while fin - dernier > maxi:
                pris = None
                # Un arrêt existant d'abord, puis une place neuve, du plus loin
                # au plus près : on espace autant qu'on peut.
                fenetre = [k for k in range(dernier + maxi, dernier + mini - 1, -1) if fin - k >= mini]
                for k in fenetre:
                    t = boucle[k % n]
                    if t in arrets:
                        pris = k
                        break
                if pris is None:
                    for k in fenetre:
                        t = boucle[k % n]
                        if t in possibles and voisin_existant(*t) is None:
                            pris = k
                            break
                if pris is None:
                    dernier += maxi // 2
                    continue
                choisis.append(pris % n)
                dernier = pris
        vus: set[int] = set()
        ordre = []
        for i in sorted(choisis):
            if i in vus:
                continue
            vus.add(i)
            t = boucle[i]
            if t not in arrets:
                existant = voisin_existant(*t)
                if existant and existant in boucle:
                    t = existant
                    i = boucle.index(existant)
                else:
                    quai, abri = possibles[t]
                    arrets[t] = {"x": t[0], "y": t[1], "sens": reseau.voie[t[1]][t[0]],
                                 "quai": list(quai), "abri": list(abri), "lignes": []}
            # ⚠️ L'arrêt voisin d'une autre ligne REMPLACE la place choisie : deux
            # places de la boucle peuvent donc tomber sur le même abri, et la ligne
            # s'y serait arrêtée deux fois de suite.
            if any(j == i for j, _t in ordre):
                continue
            if fiche["numero"] not in arrets[t]["lignes"]:
                arrets[t]["lignes"].append(fiche["numero"])
            ordre.append((i, t))
        ordre.sort()
        lignes.append({"fiche": fiche, "boucle": boucle, "ordre": ordre})

    # Les abris, puis les noms — dans l'ordre des tuiles, pour que les numéros
    # ne dépendent que de la ville.
    for rang, (t, arret) in enumerate(sorted(arrets.items(), key=lambda kv: (kv[0][1], kv[0][0]))):
        arret["id"] = rang
        ax, ay = arret["abri"]
        chantier.poser_decor(ABRIS[arret["sens"]], ax, ay)
        dx, dy = PAS[arret["sens"]]
        # ⚠️ Le banc EN AMONT de l'abri : on attend en regardant venir l'autobus.
        for k in (-1, 1):
            bx, by = ax + dx * k, ay + dy * k
            if _libre_pour_l_abri(chantier, bx, by, reseau.parvis) and chantier.poser_decor(BANCS[arret["sens"]], bx, by):
                break
    _nommer(ville, arrets, lieux_des_etapes)

    sortie_lignes = []
    for ligne in lignes:
        fiche, boucle = ligne["fiche"], ligne["boucle"]
        sortie_lignes.append({
            "numero": fiche["numero"],
            "nom": fiche["nom"],
            "couleur": fiche["couleur"],
            "longueur": len(boucle),
            "autobus": max(2, round(len(boucle) / HORAIRE["tuiles_par_autobus"])),
            "trace": coins(boucle),
            "arrets": [[arrets[t]["id"], i] for i, t in ligne["ordre"]],
        })
    return {
        "lignes": sortie_lignes,
        # ⚠️ LE NOM ET LA TUILE, RIEN D'AUTRE. Le sens est la flèche de la voie, le
        # trottoir et l'abri s'en déduisent (`detail`), les lignes sont dans les
        # lignes : les envoyer coûtait 670 octets gzip à un paquet qui n'en avait
        # plus 500 sous son plafond.
        "arrets": [{"nom": a["nom"], "x": a["x"], "y": a["y"]}
                   for _t, a in sorted(arrets.items(), key=lambda kv: kv[1]["id"])],
        "horaire": dict(HORAIRE),
    }


def detail(ville: dict, rang: int) -> dict:
    """Un arrêt du paquet, avec ce qu'on en déduit — le même calcul que
    `Autobus.donnees` côté navigateur : son sens, son trottoir, son abri, ses lignes."""
    arret = ville["autobus"]["arrets"][rang]
    sens = ville["voie"][arret["y"]][arret["x"]]
    rx, ry = a_droite(*PAS[sens])
    lignes = [ligne["numero"] for ligne in ville["autobus"]["lignes"] if any(i == rang for i, _k in ligne["arrets"])]
    return {**arret, "id": rang, "sens": sens, "lignes": lignes,
            "quai": [arret["x"] + rx, arret["y"] + ry], "abri": [arret["x"] + 2 * rx, arret["y"] + 2 * ry]}


def ordinal(n: int) -> str:
    """1re, 2e, 3e — l'abréviation qu'on lit sur une plaque de rue au Québec."""
    return "1re" if n == 1 else f"{n}e"


def _rues(largeurs: list[int], blocs: list[int]) -> list[tuple[int, int]]:
    """Le début et la fin de chaque rue d'une trame (rue, bloc, rue, bloc…)."""
    rues, x = [], 0
    for i, largeur in enumerate(largeurs):
        rues.append((x, x + largeur))
        x += largeur + (blocs[i] if i < len(blocs) else 0)
    return rues


def nom_de_coin(grille: dict, x: int, y: int, sens: str) -> str:
    """« 3e Rue / 5e Avenue » : la rue qu'on longe, puis la plus proche qui la croise.

    ⚠️ Les rues de la trame n'avaient pas de nom, et un arrêt s'appelait
    « Le Faubourg 7 » — un numéro qui ne dit pas où l'on descend. Les avenues
    vont du nord au sud et se comptent d'ouest en est ; les rues vont d'est en
    ouest et se comptent du nord au sud — comme à Limoilou.
    """
    avenues = _rues(grille["rues_v"], grille["colonnes"])
    rues = _rues(grille["rues_h"], grille["rangees"])

    def la_plus_proche(bandes: list[tuple[int, int]], v: int) -> int:
        return min(range(len(bandes)), key=lambda i: (abs((bandes[i][0] + bandes[i][1] - 1) / 2 - v), i))

    avenue = la_plus_proche(avenues, x) + 1
    rue = la_plus_proche(rues, y) + 1
    if sens in ("<", ">"):
        return f"{ordinal(rue)} Rue / {ordinal(avenue)} Avenue"
    return f"{ordinal(avenue)} Avenue / {ordinal(rue)} Rue"


def _nommer(ville: dict, arrets: dict, lieux_des_etapes: dict) -> None:
    """Un arrêt porte le nom du lieu qu'il sert ; sinon celui d'un lieu tout
    proche qui n'a pas encore d'arrêt ; sinon celui de son coin de rue."""
    lieux = sorted(ville["points_interet"], key=lambda p: (p["y"], p["x"]))
    servis: set[str] = set(lieux_des_etapes.values())
    pris: set[str] = set()
    rayon = ARRETS["rayon_nom"]
    for t, arret in sorted(arrets.items(), key=lambda kv: kv[1]["id"]):
        nom = lieux_des_etapes.get(t)
        if nom is None:
            qx, qy = arret["quai"]
            proches = sorted(((qx - p["x"]) ** 2 + (qy - p["y"]) ** 2, p["nom"]) for p in lieux)
            nom = next((n for d2, n in proches if d2 <= rayon * rayon and n not in pris and n not in servis), None)
        if nom is None:
            nom = nom_de_coin(ville["grille"], arret["x"], arret["y"], arret["sens"])
        # ⚠️ Deux arrêts au même coin (un de chaque côté de la rue) : on dit le sens.
        if nom in pris:
            nom = nom + {"<": " (ouest)", ">": " (est)", "^": " (nord)", "v": " (sud)"}[arret["sens"]]
        pris.add(nom)
        arret["nom"] = nom
