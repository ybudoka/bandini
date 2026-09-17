"""Le tramway de Baie-des-Brumes : du Faubourg aux Quais, sur ses rails.

M12, « La ville vit » : « une ligne sur rails du Faubourg aux Quais, des arrêts, des
portes — et il ne s'arrête pas pour toi. ⚠️ C'est un véhicule qui ignore le champ de
direction : il a ses propres rails, et le trafic doit lui céder. »

⚠️ **Python pose les rails, le navigateur roule** — comme les autobus et les éboueurs,
et avec leur machinerie côté navigateur : le tramway est une LIGNE (`T`) dont les
voitures sont des autobus marqués `rails`. Ce module ne pose rien dans la ville et ne
tire aucun dé : il trace, sur la ville finie, la voie double et ses arrêts.

⚠️ **Double voie, jamais à contresens.** L'aller roule sur la voie de droite d'une rue,
le retour sur celle d'en face, dans le sens du trafic : un tramway qui monte à
contresens se trouverait nez à nez avec un char qui ne peut ni reculer ni se ranger.
Ce qu'il ignore du champ de direction, ce sont les RÈGLES DES BOÎTES — il tourne de sa
voie, où qu'elle soit — et, aux deux terminus, il passe d'une voie à l'autre là où il
est : c'est une rame à deux cabines, elle ne fait pas demi-tour.
"""

from __future__ import annotations

import heapq

from . import autobus

#: D'où à où : un lieu garanti du Faubourg, et le quai du traversier (la
#: correspondance) — ou, sans traversier, un lieu garanti des Quais.
DEPART = "casse_croute"
ARRIVEE = "traversier"
ARRIVEE_SANS_TRAVERSIER = "cantine"

#: Autour de chaque bout, on cherche une place de départ dans ce rayon (tuiles).
RAYON_BOUT = 12

#: Un virage coûte : sans lui, deux chemins de même longueur se valent et la voie
#: traverse la ville en escalier.
COUT_VIRAGE = 6

#: ⚠️ **ET LA VOIE DU MILIEU COÛTE AUSSI** (17 sept. 2026), comme pour l'autobus
#: (`autobus.COUT_VOIE_DU_MILIEU`) — mais ici ce n'est pas une préférence, c'est
#: la ligne entière qui en dépend. Une rame roule par PAIRES de voies opposées :
#: sur un boulevard à quatre voies, la seule paire qui existe est celle du
#: MILIEU, et aucune de ses deux voies ne longe un trottoir — donc pas un arrêt
#: n'y tient. Mesuré le jour où la trame a bougé : la ligne s'est mise à
#: descendre un boulevard, elle est passée de 12 arrêts à 4, et le quai du
#: traversier n'avait plus le sien (`test_tramway`). Les rues à deux voies, elles,
#: bordent leurs deux trottoirs : c'est là que le tramway doit passer.
COUT_VOIE_DU_MILIEU = 8

#: Les arrêts, en tuiles de tracé : au moins tant entre deux, et jamais à moins de
#: tant d'une boîte (la rame fait trois tuiles, elle bloquerait le croisement).
ECART_ARRETS = 45
LOIN_DES_BOITES = 3
#: Un arrêt à moins de tant de tuiles (à pied) du quai du traversier en porte le nom.
#: ⚠️ 32 jusqu'au 17 sept. 2026, quand le chenal du pont s'est élargi : le quai du
#: traversier est descendu de dix-sept tuiles avec toute la bande sud, et les rues
#: qui l'entourent sont des boulevards — pas une place de rame n'y longe un
#: trottoir, donc pas un arrêt. Le dernier arrêt de la ligne est à 36 tuiles du
#: quai, et il est bien celui d'où l'on va prendre le bateau.
PRES_DU_TRAVERSIER = 40
#: Pas à moins de tant d'un arrêt d'autobus : deux abris côte à côte, c'est un terminus.
LOIN_DES_ABRIBUS = 6

#: Ce que le navigateur suit (voir `autobus.HORAIRE`). ⚠️ `vitesse_px` est la vitesse
#: MOYENNE, arrêts compris : c'est elle qui place une rame qu'on ne voit pas.
HORAIRE: dict = {
    "rames": 3,
    "couleur": "#c0392b",
    "vitesse_px": 1.4,
    "arret_images": 120,          # les portes s'ouvrent et se referment : il n'attend personne
}

PAS = autobus.PAS
FLECHE = {d: f for f, d in PAS.items()}


def _gauche(d: tuple[int, int]) -> tuple[int, int]:
    """La main gauche d'une rame qui roule dans ce sens (y vers le bas)."""
    return d[1], -d[0]


def _oppose(d: tuple[int, int]) -> tuple[int, int]:
    return -d[0], -d[1]


class _Rails:
    def __init__(self, ville: dict) -> None:
        self.reseau = autobus._Reseau(ville)
        self.voie = ville["voie"]

    def roule(self, x: int, y: int, d: tuple[int, int]) -> bool:
        """Une rame peut-elle être sur cette tuile dans ce sens ?"""
        r = self.reseau
        if not r.dedans(x, y) or (x, y) in r.interdites:
            return False
        if self.voie[y][x] == "+":
            return True
        return r.sens(x, y) == d

    def paire(self, x: int, y: int, d: tuple[int, int]) -> bool:
        """La tuile, ET celle d'en face pour le retour."""
        g = _gauche(d)
        return self.roule(x, y, d) and self.roule(x + g[0], y + g[1], _oppose(d))

    def chemin(self, departs, arrivees):
        tas, dist, avant = [], {}, {}
        for x, y, d in departs:
            dist[(x, y, d)] = 0
            heapq.heappush(tas, (0, x, y, d))
        fin = set(arrivees)
        while tas:
            c, x, y, d = heapq.heappop(tas)
            if c > dist.get((x, y, d), 1 << 60):
                continue
            if (x, y) in fin:
                out = [(x, y, d)]
                while out[-1] in avant:
                    out.append(avant[out[-1]])
                return out[::-1]
            sens = [d]
            if self.voie[y][x] == "+":
                sens += [_gauche(d), _oppose(_gauche(d))]
            for nd in sens:
                nx, ny = x + nd[0], y + nd[1]
                if not self.paire(nx, ny, nd):
                    continue
                nc = c + 1 + (COUT_VIRAGE if nd != d else 0)
                if self.voie[ny][nx] in PAS and not self.reseau.longe_le_trottoir(nx, ny):
                    nc += COUT_VOIE_DU_MILIEU
                if nc < dist.get((nx, ny, nd), 1 << 60):
                    dist[(nx, ny, nd)] = nc
                    avant[(nx, ny, nd)] = (x, y, d)
                    heapq.heappush(tas, (nc, nx, ny, nd))
        return None


def _bout(ville: dict, slug: str) -> tuple[int, int] | None:
    if slug == "traversier":
        t = ville.get("traversier")
        return tuple(t["escales"][0]["acces"][0]) if t else None
    lieu = next((p for p in ville["points_interet"] if p.get("slug") == slug), None)
    return (lieu["x"], lieu["y"]) if lieu else None


def _places(rails: _Rails, centre: tuple[int, int]) -> list[tuple[int, int, tuple[int, int]]]:
    """Les places d'une rame près d'un bout : une voie (pas une boîte) avec sa voie d'en face."""
    r = rails.reseau
    cx, cy = centre
    out = []
    for y in range(cy - RAYON_BOUT, cy + RAYON_BOUT + 1):
        for x in range(cx - RAYON_BOUT, cx + RAYON_BOUT + 1):
            if not r.dedans(x, y) or rails.voie[y][x] not in PAS:
                continue
            d = PAS[rails.voie[y][x]]
            if rails.paire(x, y, d):
                out.append((x, y, d))
    return sorted(out, key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), t[1], t[0]))


def _coins_decales(chemin: list[tuple[int, int, tuple[int, int]]]) -> list[tuple[int, int]]:
    """Le retour : l'aller décalé d'une tuile à sa gauche, parcouru à l'envers.

    ⚠️ Un coin se décale des DEUX gauches, celle d'avant et celle d'après : à un virage
    à gauche, le retour prend le coin intérieur (il coupe) ; à droite, l'extérieur."""
    points = []
    for k, (x, y, d) in enumerate(chemin):
        avant = chemin[k - 1][2] if k > 0 else d
        if k == 0 or k == len(chemin) - 1 or avant != d:
            g1, g2 = _gauche(avant), _gauche(d)
            dx, dy = (g1[0] + g2[0], g1[1] + g2[1]) if avant != d else g1
            # ⚠️ Le virage se lit sur la tuile où le sens CHANGE : c'est la boîte d'avant.
            if avant != d:
                px, py, _ = chemin[k - 1]
                points.append((px + dx, py + dy))
            else:
                points.append((x + dx, y + dy))
    return points[::-1]


def boucle(ville: dict) -> tuple[list[tuple[int, int]], int] | None:
    """La voie double, tuile par tuile, comme une boucle : l'aller, le passage d'une voie
    à l'autre au terminus, le retour, et le passage au départ — et la longueur de
    l'aller (l'indice du terminus des Quais)."""
    a, b = _bout(ville, DEPART), _bout(ville, ARRIVEE) or _bout(ville, ARRIVEE_SANS_TRAVERSIER)
    if not a or not b:
        return None
    rails = _Rails(ville)
    departs = _places(rails, a)[:40]
    arrivees = [(x, y) for x, y, _d in _places(rails, b)[:40]]
    if not departs or not arrivees:
        return None
    aller = rails.chemin(departs, arrivees)
    if not aller or len(aller) < 20:
        return None
    tuiles = autobus.derouler(autobus.coins([(x, y) for x, y, _d in aller] + _coins_decales(aller)))
    return tuiles, len(aller)


def _arrets(ville: dict, rails: _Rails, tuiles: list[tuple[int, int]], aller: int) -> list[list]:
    """Les arrêts le long de la boucle : [indice de tracé, x, y] de la tuile de voie.

    Une place possible : une voie droite qui longe le trottoir (`LOIN_DES_BOITES` tuiles
    droites de part et d'autre, hors boîte), un trottoir libre à droite (ni meuble, ni
    abribus, ni le pas d'une porte), loin des abribus. ⚠️ Les TERMINUS d'abord — le
    premier et le dernier arrêt de chaque voie : une ligne dont le dernier arrêt est à dix
    rues du quai ne mène pas au traversier. Puis les autres, à `ECART_ARRETS` tuiles au
    moins de tous."""
    r = rails.reseau
    n = len(tuiles)
    occupe = {(d["x"], d["y"]) for d in ville["decor"]}
    abribus = []
    for rang in range(len(ville["autobus"]["arrets"])):
        d = autobus.detail(ville, rang)
        occupe |= {tuple(d["quai"]), tuple(d["abri"])}
        abribus.append(tuple(d["quai"]))
    portes = {(p["x"], p["y"] + 1) for p in ville["portes"]}
    places = []
    for i, (x, y) in enumerate(tuiles):
        nx, ny = tuiles[(i + 1) % n]
        d = (nx - x, ny - y)
        if d not in PAS.values() or not r.longe_le_trottoir(x, y) or r.sens(x, y) != d:
            continue
        if not all(tuiles[(i + k) % n] == (x + d[0] * k, y + d[1] * k) and tuiles[(i + k) % n] not in r.boites
                   for k in range(-LOIN_DES_BOITES, LOIN_DES_BOITES + 1)):
            continue
        rx, ry = autobus.a_droite(*d)
        quai = (x + rx, y + ry)
        if quai in occupe or quai in portes:
            continue
        if any(abs(quai[0] - a[0]) + abs(quai[1] - a[1]) < LOIN_DES_ABRIBUS for a in abribus):
            continue
        places.append(i)
    if not places:
        return []

    def ecart(i: int, k: int) -> int:
        return min((i - k) % n, (k - i) % n)

    choisis: list[int] = []
    for moitie in ([i for i in places if i < aller], [i for i in places if i >= aller]):
        if moitie:
            # Le bout de chaque voie : on descend au terminus, on remonte en repartant.
            choisis += [k for k in (min(moitie), max(moitie)) if k not in choisis]
    for i in places:
        if all(ecart(i, k) >= ECART_ARRETS for k in choisis):
            choisis.append(i)
    return [[i, tuiles[i][0], tuiles[i][1]] for i in sorted(choisis)]


def _nom(ville: dict, x: int, y: int, sens: str, aller: bool, pris: set[str]) -> str:
    """Le quai du traversier s'il est à deux pas ; sinon le lieu garanti le plus proche
    s'il est tout près ; sinon le coin de rue. ⚠️ Le même nom sert aux deux voies (on
    descend d'un côté de la rue, on remonte de l'autre) : le second dit son sens."""
    nom = None
    t = ville.get("traversier")
    if t:
        ax, ay = t["escales"][0]["acces"][0]
        if abs(ax - x) + abs(ay - y) <= PRES_DU_TRAVERSIER:
            nom = "Quai du traversier"
    if nom is None:
        rayon = autobus.ARRETS["rayon_nom"]
        proches = sorted(((x - p["x"]) ** 2 + (y - p["y"]) ** 2, p["nom"]) for p in ville["points_interet"])
        nom = next((n for d2, n in proches if d2 <= rayon * rayon), None)
    if nom is None:
        nom = autobus.nom_de_coin(ville["grille"], x, y, sens)
    if nom in pris:
        nom = f"{nom} ({'vers les Quais' if aller else 'vers le Faubourg'})"
    pris.add(nom)
    return nom


def tracer(ville: dict) -> dict | None:
    """La ligne, prête pour le paquet — ou None si la ville n'en porte pas."""
    trace = boucle(ville)
    if not trace:
        return None
    tuiles, aller = trace
    rails = _Rails(ville)
    arrets = _arrets(ville, rails, tuiles, aller)
    if len(arrets) < 4:
        return None
    pris: set[str] = set()
    for a in arrets:
        a.append(_nom(ville, a[1], a[2], ville["voie"][a[2]][a[1]], a[0] < aller, pris))
    return {"numero": "T", "nom": "Tramway du Faubourg", "trace": autobus.coins(tuiles), "aller": aller,
            "arrets": arrets, "horaire": dict(HORAIRE)}
