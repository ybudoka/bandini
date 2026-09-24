"""Les grands bateaux de Baie-des-Brumes : où mouillent le chalutier et le porte-conteneurs.

Demande de Martin (21 sept. 2026) : « nouveau bateau : chalutier + porte-conteneurs ».
La chaloupe attend contre n'importe quelle rive bâtie (`carte.amarrages`, une tuile
d'eau) ; un chalutier demande trois tuiles et demie de quai, un porte-conteneurs dix.
Ce module leur trouve une place, et c'est tout.

⚠️ **Il ne pose rien et ne tire aucun dé** — comme le traversier. Il lit la ville
FINIE (tout à la fin de `carte.generer`) et rend des places ; le navigateur fait
naître les coques hors champ, comme les chaloupes (`Vehicules.majMouillages`). La ville
est la même, clé par clé, avec ou sans lui (un juge compare) : ce qu'on AJOUTE se pose
en dernier, et rien de ce qui précède ne le lit.

**Un mouillage** est un rectangle d'eau de la baie assez grand pour la coque, couché le
long d'un QUAI (la moitié au moins de son long flanc contre le glyphe `Q`), avec de
l'eau libre au large et un CHENAL devant l'étrave pour repartir. Il se tient loin des
chaloupes, des ponts, de l'île et de la route du traversier — un traversier qui frôle
une coque la coule.

**Qui va où** : le porte-conteneurs au plus près de la chaîne du quai du cargo
(`BARRIERES`, « le quai du cargo ») — le quai avait sa chaîne, son contrebandier et
sa cale, il lui manquait le cargo ; les chalutiers au plus près de lui ensuite,
espacés, et sans jamais boucher un chenal. Entre deux places aussi proches, la plus
au nord, puis la plus à l'ouest.
"""

from __future__ import annotations

import math

from . import carte as carte_mod
from . import vehicules

#: La flotte qui mouille dans la ville, dans l'ordre où elle choisit sa place.
FLOTTE: tuple[tuple[str, int], ...] = (("porte_conteneurs", 1), ("chalutier", 2))

#: Combien de rangées d'eau libre au large du flanc qui ne touche pas le quai : de
#: quoi s'écarter avant de virer. ⚠️ Pas davantage : un bassin de port en a six ou
#: sept, et un mouillage qui exige la pleine baie n'est plus à quai.
LARGE = 4

#: À combien de tuiles d'une chaloupe amarrée (le rectangle grossi d'autant) : on ne
#: fait pas naître une coque de dix tuiles sur une chaloupe.
MARGE_AMARRAGE = 2

#: Deux grands bateaux : au moins tant de tuiles d'eau entre leurs rectangles.
ECART = 3

#: Rien à moins de tant de tuiles de la route du traversier.
MARGE_TRAVERSIER = 2

#: On cherche d'abord dans ce rayon autour du repère (le cargo), puis partout s'il
#: n'y a rien : c'est le plus proche qu'on veut, et balayer la baie entière pour
#: chaque bateau coûtait un cinquième de seconde à chaque ville.
RAYON = 48

#: Le cap de la coque selon le bout où l'étrave pointe.
CAPS = {(1, 0): 0.0, (-1, 0): round(math.pi, 4), (0, 1): round(math.pi / 2, 4), (0, -1): round(-math.pi / 2, 4)}


def dimensions(slug: str) -> tuple[int, int]:
    """Le rectangle de tuiles d'une coque couchée est-ouest : sa longueur et une
    tuile de jeu (la chaîne de cercles s'arrondit au bout), sa largeur arrondie à
    la tuile."""
    fiche = vehicules.par_slug(slug)
    tuile = carte_mod.TUILE_PX
    return math.ceil(fiche["longueur"] / tuile) + 1, math.ceil(fiche["largeur"] / tuile)


class _Port:
    """La baie vue d'un pilote de port : l'eau, les quais, et ce qu'il faut éviter."""

    def __init__(self, chantier, ville: dict) -> None:
        self.sol = ville["sol"]
        self.h, self.l = len(self.sol), len(self.sol[0])
        baie, occupe = chantier.la_baie(), chantier.occupe
        eau = [[(x, y) in baie and (x, y) not in occupe for x in range(self.l)] for y in range(self.h)]
        # Ce qu'une coque ne doit pas couvrir : les pieds des ponts, les chaloupes
        # amarrées, la ceinture de l'île, la route du traversier.
        interdits: list[tuple[int, int, int, int]] = []
        garde = carte_mod.GREVE["pont_ecart"]
        interdits += [(p["x"] - garde, p["y"] - garde, p["x"] + p["l"] + garde, p["y"] + p["h"] + garde)
                      for p in ville["ponts"]]
        ile = ville.get("ile") or None
        m = MARGE_AMARRAGE
        amarrages = list(ville.get("amarrages", [])) + list((ile or {}).get("amarrages", []))
        interdits += [(a["x"] - m, a["y"] - m, a["x"] + m + 1, a["y"] + m + 1) for a in amarrages]
        if ile:
            from . import ile as ile_mod
            c = ile_mod.ILE["ceinture"]
            interdits.append((ile["x"] - c, ile["y"] - c, ile["x"] + ile["l"] + c, ile["y"] + ile["h"] + c))
        # ⚠️ La route du traversier : le rectangle qui couvre ses deux coques à quai
        # couvre aussi le couloir qui les relie, quelle qu'en soit la forme.
        trav = ville.get("traversier") or {}
        escales = trav.get("escales") or []
        if escales:
            coque, t = trav["coque"], MARGE_TRAVERSIER
            interdits.append((min(e["x"] for e in escales) - t, min(e["y"] for e in escales) - t,
                              max(e["x"] for e in escales) + coque["longueur"] + t,
                              max(e["y"] for e in escales) + coque["largeur"] + t))
        libre = [ligne[:] for ligne in eau]
        for x0, y0, x1, y1 in interdits:
            for y in range(max(0, y0), min(self.h, y1)):
                for x in range(max(0, x0), min(self.l, x1)):
                    libre[y][x] = False
        self._eau, self._libre = self._cumul(eau), self._cumul(libre)
        # Le long des flancs : le quai (`Q`), et ce qui n'est ni du quai ni de l'eau.
        self._pas_quai = self._cumul([[g == "Q" for g in ligne] for ligne in self.sol])
        self._pas_rive = self._cumul([[g in ("Q", "~") for g in ligne] for ligne in self.sol])

    def _cumul(self, grille: list[list[bool]]) -> list[list[int]]:
        """`c[y][x]` : combien de tuiles NON prises dans le rectangle (0, 0)-(x - 1, y - 1)."""
        c = [[0] * (self.l + 1) for _ in range(self.h + 1)]
        for y in range(self.h):
            ligne, haut, bas = 0, c[y], c[y + 1]
            for x in range(self.l):
                ligne += 0 if grille[y][x] else 1
                bas[x + 1] = haut[x + 1] + ligne
        return c

    def _dehors(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        return x0 < 0 or y0 < 0 or x1 > self.l or y1 > self.h

    @staticmethod
    def _compte(c: list[list[int]], x0: int, y0: int, x1: int, y1: int) -> int:
        return c[y1][x1] - c[y0][x1] - c[y1][x0] + c[y0][x0]

    def eau(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        """Le rectangle [x0, x1[ × [y0, y1[ est-il tout de la baie ?"""
        return not self._dehors(x0, y0, x1, y1) and self._compte(self._eau, x0, y0, x1, y1) == 0

    def libre(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        """… et loin de tout ce qu'une coque ne doit pas couvrir ?"""
        return not self._dehors(x0, y0, x1, y1) and self._compte(self._libre, x0, y0, x1, y1) == 0

    def quai(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        """Le long flanc contre le quai (la rangée ou la colonne [x0, x1[ × [y0, y1[
        qui le borde) : la moitié au moins de ses tuiles sont du quai, et les autres
        sont de l'eau — un flanc à moitié contre le sable, c'est un bateau échoué."""
        if self._dehors(x0, y0, x1, y1):
            return False
        n = (x1 - x0) * (y1 - y0)
        quai = n - self._compte(self._pas_quai, x0, y0, x1, y1)
        return 2 * quai >= n and self._compte(self._pas_rive, x0, y0, x1, y1) == 0

    def postes(self, longueur: int, largeur: int, autour: tuple[float, float] | None = None) -> list[dict]:
        """Toutes les places d'une coque de `longueur` × `largeur` tuiles, dans les
        deux sens : le quai d'un côté, le large de l'autre, et le CHENAL devant
        l'étrave — de l'eau sur une longueur de coque, pour repartir en avant.
        `autour` : seulement dans le `RAYON` de ce point.

        ⚠️ **Le chenal, parce qu'un port a des jetées.** Sans lui, le premier
        porte-conteneurs s'est couché dans le bassin sous la chaîne du cargo, le
        nez à quatre tuiles d'une jetée et la poupe contre l'autre : on y montait,
        et il ne sortait plus. Le nez va au bout dont le chenal est libre ; si les
        deux le sont, à l'est (couché) ou au sud (debout) — sans dé."""
        out = []
        for couche in (True, False):
            lx, ly = (longueur, largeur) if couche else (largeur, longueur)
            # ⚠️ Des noms à elle, pour la fenêtre : le `xa` du large, plus bas,
            # écrasait sa borne, et la rangée suivante commençait où finissait le
            # large — un poste sur trois n'était jamais regardé.
            gauche, droite, haut, bas = 1, self.l - lx, 1, self.h - ly
            if autour:
                gauche, droite = max(gauche, int(autour[0]) - RAYON), min(droite, int(autour[0]) + RAYON)
                haut, bas = max(haut, int(autour[1]) - RAYON), min(bas, int(autour[1]) + RAYON)
            for y0 in range(haut, bas):
                for x0 in range(gauche, droite):
                    if not self.libre(x0, y0, x0 + lx, y0 + ly):
                        continue
                    for cote in (-1, 1):
                        if couche:
                            bord = y0 - 1 if cote < 0 else y0 + ly
                            flanc = (x0, bord, x0 + lx, bord + 1)
                            ya = y0 + ly if cote < 0 else y0 - LARGE
                            large = (x0, ya, x0 + lx, ya + LARGE)
                        else:
                            bord = x0 - 1 if cote < 0 else x0 + lx
                            flanc = (bord, y0, bord + 1, y0 + ly)
                            xa = x0 + lx if cote < 0 else x0 - LARGE
                            large = (xa, y0, xa + LARGE, y0 + ly)
                        if not (self.quai(*flanc) and self.eau(*large)):
                            continue
                        # ⚠️ LE POSTE : la tuile du QUAI au milieu du flanc, celle d'où l'on
                        # monte à bord — pas le centre de la coque, qui est dans l'eau. C'est
                        # là que Sven se tient (§ « Sven et le piratage »), et là que
                        # `Histoire.poserLeChar` pose le joueur avant de faire naître le char.
                        poste = (x0 + lx // 2, bord) if couche else (bord, y0 + ly // 2)
                        p = {"x0": x0, "y0": y0, "l": lx, "h": ly, "couche": couche, "poste": poste}
                        for sens in ((1, 0), (-1, 0)) if couche else ((0, 1), (0, -1)):
                            c = chenal(p, sens, longueur)
                            if self.eau(*c):
                                p["angle"], p["chenal"] = CAPS[sens], c
                                out.append(p)
                                break
                        break
        return out


def chenal(p: dict, sens: tuple[int, int], n: int) -> tuple[int, int, int, int]:
    """Le rectangle de `n` tuiles devant le bout `sens` de la coque."""
    x0, y0, x1, y1 = _rect(p)
    dx, dy = sens
    if dx > 0:
        return (x1, y0, x1 + n, y1)
    if dx < 0:
        return (x0 - n, y0, x0, y1)
    if dy > 0:
        return (x0, y1, x1, y1 + n)
    return (x0, y0 - n, x1, y0)


def _centre(p: dict) -> tuple[float, float]:
    return p["x0"] + p["l"] / 2, p["y0"] + p["h"] / 2


def _rect(p: dict) -> tuple[int, int, int, int]:
    return p["x0"], p["y0"], p["x0"] + p["l"], p["y0"] + p["h"]


def _touche(a: tuple[int, int, int, int], b: tuple[int, int, int, int], e: int) -> bool:
    return a[0] < b[2] + e and b[0] < a[2] + e and a[1] < b[3] + e and b[1] < a[3] + e


def _libre_des_autres(p: dict, pris: list[dict]) -> bool:
    """Ni sur un autre, ni dans son chenal, et son chenal à lui n'en traverse aucun."""
    return all(not _touche(_rect(p), _rect(q), ECART) and not _touche(_rect(p), q["chenal"], 0)
               and not _touche(p["chenal"], _rect(q), 0) for q in pris)


def amarrer(chantier, ville: dict) -> list[dict]:
    """Les mouillages de la ville : `slug`, le centre de la coque en PIXELS (`x`,
    `y`) et son cap (`angle`, en radians, 0 à l'est), plus le `poste` — la tuile de
    quai d'où l'on monte à bord, en pixels elle aussi. Vide s'il n'y a pas de quai
    du cargo — un porte-conteneurs n'a rien à faire ailleurs."""
    cargo = next((b for b in ville.get("barrieres", []) if b["slug"] == "cargo"), None)
    if not cargo:
        return []
    port = _Port(chantier, ville)
    repere = (cargo["x"] + cargo["l"] / 2, cargo["y"] + cargo["h"] / 2)
    pris: list[dict] = []
    sortie: list[dict] = []
    tuile = carte_mod.TUILE_PX
    for slug, combien in FLOTTE:
        cx, cy = repere
        cle = lambda p: ((_centre(p)[0] - cx) ** 2 + (_centre(p)[1] - cy) ** 2, p["y0"], p["x0"])  # noqa: E731
        # ⚠️ La fenêtre d'abord, toute la baie ensuite — et seulement s'il manque
        # encore un bateau. Un poste de la fenêtre revu dans la baie est refusé
        # comme la première fois : il touche celui qu'on a pris, ou il était pris.
        for autour in (repere, None):
            for p in sorted(port.postes(*dimensions(slug), autour=autour), key=cle):
                if combien == 0:
                    break
                if not _libre_des_autres(p, pris):
                    continue
                pris.append(p)
                combien -= 1
                px, py = _centre(p)
                gx, gy = p["poste"]
                sortie.append({"slug": slug, "x": round(px * tuile), "y": round(py * tuile), "angle": p["angle"],
                               "poste": {"x": gx * tuile + tuile // 2, "y": gy * tuile + tuile // 2}})
                # ⚠️ Les chalutiers se rangent autour du CARGO, pas de la chaîne : le
                # port, c'est là où est le grand bateau.
                if slug == "porte_conteneurs":
                    repere = _centre(p)
            if combien == 0:
                break
    return sortie
