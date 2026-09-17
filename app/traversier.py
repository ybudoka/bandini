"""Le traversier de Baie-des-Brumes : Les Quais ↔ La Pointe, à l'heure.

M12, « La ville vit » : « Les Quais ↔ La Pointe, à l'heure, quatre chars à bord, il
part sans toi. »

⚠️ **Python trouve les quais, le navigateur fait la traversée** — comme les autobus
et les éboueurs. Ce module ne dessine rien et ne pose rien : il cherche, sur la ville
FINIE, les deux places où une coque de traversier peut accoster (de l'eau profonde,
et un bout de rue carrossable qui y touche), et le couloir d'eau libre qui les relie.
La place du bateau n'est ensuite qu'une fonction de l'heure, et c'est `traversier.js`
qui la calcule.

⚠️ **Il ne choisit rien au hasard.** Aucun dé : parmi les paires de quais possibles,
la traversée la plus courte, puis la plus droite, puis la plus au nord-ouest. La
ville du premier matin est la même avec ou sans traversier (un juge compare).

**La coque** : `LONGUEUR` × `LARGEUR` tuiles, couchée est-ouest. Ses deux premières
rangées sont le PONT des chars ; la dernière, au sud, est la CABINE. On embarque donc
par le nord (de côté) ou par un bout (dans l'axe des deux voies du pont) — jamais par
la cabine.
"""

from __future__ import annotations

from . import carte as carte_mod

LONGUEUR = 8
LARGEUR = 3
#: La rangée de la cabine, dans la coque. Les autres sont le pont.
CABINE = 2
VOIES = tuple(r for r in range(LARGEUR) if r != CABINE)

#: Les deux escales, d'ouest en est.
ESCALES = ("quais", "pointe")

#: Un quai appartient à une escale s'il touche le quartier à moins de tant de
#: tuiles : les rives de la baie sont dans la zone « baie », pas dans le quartier.
PRES_DU_QUARTIER = 3

#: Combien de tuiles de rive carrossables doivent toucher le pont pour qu'un char y
#: monte sans viser au pixel.
ACCES_MIN = 2

#: Rien ne passe à moins de tant de tuiles de l'île (sa ceinture d'eau) ni d'un
#: amarrage : un traversier qui frôle une chaloupe amarrée la coule.
MARGE_AMARRAGE = 1

#: L'horaire, en heures de jeu. ⚠️ **Départ à l'heure juste** : des Quais aux
#: heures paires, de La Pointe aux heures impaires. Une période = deux traversées et
#: deux escales, et la traversée finit à l'heure moins `quai_h`.
HORAIRE: dict = {
    "periode_h": 2.0,
    "traversee_h": 0.65,
    "quai_h": 0.35,
    #: La part de la traversée passée à prendre de la vitesse (et autant à freiner).
    "elan": 0.12,
}


def _zones(ville: dict, district: str) -> list[dict]:
    return [z for z in ville["zones"] if z.get("district") == district]


def _pres(zones: list[dict], x: int, y: int, marge: int) -> bool:
    return any(z["x"] - marge <= x < z["x"] + z["l"] + marge and z["y"] - marge <= y < z["y"] + z["h"] + marge
               for z in zones)


class _Baie:
    """La carte vue par un capitaine : l'eau profonde, en somme cumulée."""

    def __init__(self, ville: dict) -> None:
        self.sol = ville["sol"]
        self.h, self.l = len(self.sol), len(self.sol[0])
        # `terre[y][x]` = combien de tuiles NON navigables dans le rectangle (0,0)-(x,y).
        cumul = [[0] * (self.l + 1) for _ in range(self.h + 1)]
        for y in range(self.h):
            ligne = 0
            for x in range(self.l):
                ligne += 0 if self.sol[y][x] == "~" else 1
                cumul[y + 1][x + 1] = cumul[y][x + 1] + ligne
        self.cumul = cumul
        ile = ville.get("ile") or None
        from . import ile as ile_mod
        m = ile_mod.ILE["ceinture"]
        self.ile = (ile["x"] - m, ile["y"] - m, ile["x"] + ile["l"] + m, ile["y"] + ile["h"] + m) if ile else None
        self.amarrages = [(a["x"], a["y"]) for a in ville.get("amarrages", [])]
        if ile:
            self.amarrages += [(a["x"], a["y"]) for a in ile.get("amarrages", [])]

    def eau(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        """Le rectangle [x0, x1] × [y0, y1] (bornes comprises) est-il tout d'eau profonde ?"""
        if x0 < 0 or y0 < 0 or x1 >= self.l or y1 >= self.h:
            return False
        c = self.cumul
        return c[y1 + 1][x1 + 1] - c[y0][x1 + 1] - c[y1 + 1][x0] + c[y0][x0] == 0

    def libre(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        """De l'eau, loin de l'île et d'un amarrage."""
        if not self.eau(x0, y0, x1, y1):
            return False
        if self.ile and x0 < self.ile[2] and x1 >= self.ile[0] and y0 < self.ile[3] and y1 >= self.ile[1]:
            return False
        m = MARGE_AMARRAGE
        return not any(x0 - m <= ax <= x1 + m and y0 - m <= ay <= y1 + m for ax, ay in self.amarrages)

    def carrossable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.l and 0 <= y < self.h):
            return False
        g = self.sol[y][x]
        return g != "~" and carte_mod.solidite(g) == 0

    def pres_d_une_rue(self, x: int, y: int) -> bool:
        return any(0 <= x + dx < self.l and 0 <= y + dy < self.h and carte_mod.routier(self.sol[y + dy][x + dx])
                   for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))


def acces(x0: int, y0: int, cote: str) -> list[tuple[int, int]]:
    """Les tuiles de rive qui touchent le PONT d'une coque posée en (x0, y0), du côté
    d'où l'on embarque : le nord (tout le long), ou un bout (face aux deux voies)."""
    if cote == "nord":
        return [(x, y0 - 1) for x in range(x0, x0 + LONGUEUR)]
    bout = x0 - 1 if cote == "ouest" else x0 + LONGUEUR
    return [(bout, y0 + r) for r in VOIES]


def _quais(baie: _Baie, ville: dict, district: str) -> list[dict]:
    """Toutes les places d'accostage d'une escale."""
    zones = _zones(ville, district)
    if not zones:
        return []
    # Une coque à quai touche le quartier : on ne cherche qu'autour de ses zones.
    m = PRES_DU_QUARTIER + LONGUEUR + 1
    xa, xb = max(1, min(z["x"] for z in zones) - m), min(baie.l - LONGUEUR, max(z["x"] + z["l"] for z in zones) + m)
    ya, yb = max(1, min(z["y"] for z in zones) - m), min(baie.h - LARGEUR, max(z["y"] + z["h"] for z in zones) + m)
    out = []
    for y0 in range(ya, yb):
        for x0 in range(xa, xb):
            # ⚠️ Le couloir rejugerait la coque à quai (`balayage` commence et finit sur
            # elle), mais ce filtre est celui de la VITESSE : sans lui, chaque tuile de
            # rive devient un quai possible et la recherche passe de 20 ms à 3 min 30.
            if not baie.eau(x0, y0, x0 + LONGUEUR - 1, y0 + LARGEUR - 1):
                continue
            for cote in ("nord", "ouest", "est"):
                rive = [t for t in acces(x0, y0, cote) if baie.carrossable(*t)]
                if len(rive) < ACCES_MIN or not any(baie.pres_d_une_rue(*t) for t in rive):
                    continue
                if not any(_pres(zones, tx, ty, PRES_DU_QUARTIER) for tx, ty in rive):
                    continue
                out.append({"x": x0, "y": y0, "cote": cote, "acces": [list(t) for t in rive]})
    return out


def balayage(a: dict, b: dict) -> list[tuple[int, int, int, int]]:
    """Les rectangles de tuiles que la coque couvre en allant de `a` à `b` en ligne
    droite, une tuile de pas à la fois (bornes comprises)."""
    dx, dy = b["x"] - a["x"], b["y"] - a["y"]
    n = max(abs(dx), abs(dy), 1)
    out = []
    for k in range(n + 1):
        fx, fy = a["x"] + dx * k / n, a["y"] + dy * k / n
        x0, y0 = int(fx // 1), int(fy // 1)
        x1 = x0 + LONGUEUR - 1 + (1 if fx != x0 else 0)
        y1 = y0 + LARGEUR - 1 + (1 if fy != y0 else 0)
        out.append((x0, y0, x1, y1))
    return out


def tracer(ville: dict) -> dict | None:
    """Les deux escales et l'horaire, prêts pour le paquet — ou None si la baie n'en
    porte pas."""
    baie = _Baie(ville)
    ouest = [q for q in _quais(baie, ville, ESCALES[0]) if q["cote"] != "est"]
    est = [q for q in _quais(baie, ville, ESCALES[1]) if q["cote"] != "ouest"]
    paires = sorted(((b["x"] - a["x"], abs(b["y"] - a["y"]), a["y"], a["x"], b["y"], i, j)
                     for i, a in enumerate(ouest) for j, b in enumerate(est) if b["x"] - a["x"] > LONGUEUR),
                    key=lambda p: p[:5])
    noms = {d["slug"]: d["nom"] for d in ville.get("districts", [])}
    for *_, i, j in paires:
        a, b = ouest[i], est[j]
        if all(baie.libre(*r) for r in balayage(a, b)):
            escales = [dict(q, district=d, nom=noms.get(d, d)) for q, d in ((a, ESCALES[0]), (b, ESCALES[1]))]
            return {"coque": {"longueur": LONGUEUR, "largeur": LARGEUR, "cabine": CABINE},
                    "escales": escales, "horaire": dict(HORAIRE)}
    return None
