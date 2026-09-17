#!/usr/bin/env python3
"""Les icones et le logo de Bandini — dessines en pixels ici, ecrits dans `static/img/`.

Le jeu dessine ses sprites en code (`static/js/sprites.js`) ; ses icones aussi.
Rien a installer : le script ecrit lui-meme ses PNG (zlib) et son .ico, et ses
SVG ne sont que des rectangles. Il ecrit :

- `favicon.svg`, `favicon.ico` (16, 32, 48) : l'onglet ;
- `icone-180.png` : l'ecran d'accueil d'iOS (`apple-touch-icon`) ;
- `icone-192.png`, `icone-512.png` : le manifeste (`/manifest.webmanifest`),
  la 512 sert aussi d'icone « maskable » ;
- `logo.svg` : le titre de l'ecran d'accueil du jeu.

Deux facons de l'appeler :

    uv run python scripts/icones.py             # reecrit static/img/
    uv run python scripts/icones.py --verifier  # dit ce qui n'est plus a jour

⚠️ `--verifier` compare les PIXELS des PNG, pas leurs octets : deux zlib
(macOS, la CI) ne compriment pas pareil la meme image, et un juge qui rougit
pour ca ne dit rien de l'icone.

⚠️ Bandini sur l'icone est LE sprite du jeu (`SPRITES.joueur`, pose `bas`,
image de repos), recopie ligne pour ligne : `tests/test_icones.py` verifie
qu'il existe encore tel quel dans `sprites.js`. Un Bandini redessine dans le
jeu qui ne l'est pas sur l'icone, c'est deux personnages.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "static" / "img"

# --- La palette ---------------------------------------------------------------------

#: Celles de `styles.css` (`--nuit`, `--brume`, `--or`, `--parchemin`)...
NUIT = "#0b0a12"
PARCHEMIN = "#efe6d0"
OR = "#e8b33c"
#: ... et celles de la nuit derriere lui.
CIEL_BAS = "#13111e"
VILLE = "#24203a"
RUE = "#2a2640"

#: `SPRITES.joueur.pal`, dans l'ordre du fichier.
JOUEUR_PAL = {
    "k": "#101018", "s": "#e8b088", "h": "#3a2a1a", "c": "#c0392b",
    "p": "#2a2a3a", "o": "#ffffff", "b": "#5a3a1a",
}

#: `SPRITES.joueur.poses.bas[0]` — 12 x 16, recopie tel quel.
JOUEUR = [
    "....kkkk....", "...khhhhk...", "..khhhhhhk..", "..khsssshk..",
    "..ksossosk..", "..kssssssk..", "...kssssk...", "..kcccccck..",
    ".kckccccckc.", ".kckccccckc.", ".kskccccksk.", "..kppppppk..",
    "..kpppkpppk.", "..kppk.kppk.", "..kbbk.kbbk.", "..kkkk.kkkk.",
]

Grille = list  # list[list[str | None]] : une couleur « #rrggbb » par pixel, ou None


def vide(w: int, h: int, fond: str | None = None) -> Grille:
    return [[fond] * w for _ in range(h)]


def poser(g: Grille, x0: int, y0: int, rangees: list[str], pal: dict[str, str]) -> None:
    for y, rangee in enumerate(rangees):
        for x, ch in enumerate(rangee):
            if ch in pal:
                g[y0 + y][x0 + x] = pal[ch]


def lune(g: Grille, cx: float, cy: float, r: float) -> None:
    """Un disque d'or : le bord eclaire en haut a gauche, dans l'ombre en bas a droite."""
    clair, sombre = "#f6d27a", "#c98f25"
    for y in range(len(g)):
        for x in range(len(g[0])):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d2 = dx * dx + dy * dy
            if d2 > r * r:
                continue
            if d2 > (r - 1) ** 2 and dx + dy > r * 0.6:
                g[y][x] = sombre
            elif d2 > (r - 1.2) ** 2 and dx + dy < -r * 0.5:
                g[y][x] = clair
            else:
                g[y][x] = OR


# --- L'icone ------------------------------------------------------------------------

#: Ou Bandini se tient sur la grille de 24 : le coin haut-gauche de son sprite.
BANDINI_ICONE = (6, 4)
#: La ville derriere lui : la hauteur du toit, colonne par colonne. Haute sur
#: les bords, basse au milieu : sa tete et ses epaules restent sur l'or.
TOITS = [12, 12, 12, 14, 14, 11, 11, 11, 15, 15, 16, 16, 16, 16, 16, 15, 15, 12, 12, 12, 14,
         10, 10, 10]
#: Les fenetres allumees, et les etoiles dans les coins que la lune laisse.
FENETRES = [(1, 14), (1, 17), (6, 13), (6, 16), (4, 17), (18, 14), (22, 12), (22, 15), (20, 17)]
ETOILES = [(2, 3), (21, 2), (23, 7), (1, 9)]
CRATERES = [(5, 8), (18, 5)]


def icone() -> Grille:
    """24 x 24 : Bandini debout devant la lune et la ville, la nuit.

    ⚠️ Son sprite tient entier dans le cercle du masque d'Android (80 % du
    cote, au centre) : la 512 sert donc aussi d'icone « maskable », et le ciel
    et la ville debordent jusqu'au bord comme Android le demande.
    """
    g = vide(24, 24, NUIT)
    for y in range(12, 20):
        g[y] = [CIEL_BAS] * 24
    for x, y in ETOILES:
        g[y][x] = PARCHEMIN
    lune(g, 12, 9.5, 8)
    for x, y in CRATERES:
        g[y][x] = "#d39a2c"
    for x, toit in enumerate(TOITS):
        for y in range(toit, 20):
            g[y][x] = VILLE
    for x, y in FENETRES:
        g[y][x] = OR
    for y in range(20, 24):
        g[y] = [RUE] * 24
    for x in range(8, 17):
        g[20][x] = "#050409"
    poser(g, *BANDINI_ICONE, JOUEUR, JOUEUR_PAL)
    return g


def favicon() -> Grille:
    """16 x 16 : la meme lune, serree — Bandini prend toute la hauteur de l'onglet."""
    g = vide(16, 16, NUIT)
    lune(g, 8, 7, 6.5)
    poser(g, 2, 0, JOUEUR, JOUEUR_PAL)
    for x, y in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        g[y][x] = None
    return g


# --- Le logo ------------------------------------------------------------------------

LETTRES = {
    "B": ["#######.", "##....##", "##....##", "##....##", "##...##.", "######..",
          "##...##.", "##....##", "##....##", "##....##", "#######."],
    "A": ["..####..", ".##..##.", "##....##", "##....##", "##....##", "########",
          "##....##", "##....##", "##....##", "##....##", "##....##"],
    "N": ["##....##", "###...##", "###...##", "####..##", "##.##.##", "##.##.##",
          "##..####", "##...###", "##...###", "##....##", "##....##"],
    "D": ["######..", "##...##.", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", "##....##", "##...##.", "######.."],
    "I": ["######", "..##..", "..##..", "..##..", "..##..", "..##..",
          "..##..", "..##..", "..##..", "..##..", "######"],
}

#: L'or « chrome » des titres d'arcade, rangee par rangee : clair en haut, un
#: trait presque blanc a l'horizon, puis un or plus sombre qui remonte vers le bas.
DEGRADE = ["#fff3c8", "#fbe29a", "#f6d27a", "#f0c35a", "#e8b33c", "#fff8e0",
           "#a85a1a", "#c4741f", "#d68d2a", "#e6a536", "#8a4a16"]
CONTOUR = "#2a1608"
OMBRE = "#000000"
PENCHE = 3


def logo(mot: str = "BANDINI") -> Grille:
    """Le mot en lettres d'or penchees, contour brun, ombre portee noire, un eclat."""
    h = len(DEGRADE)
    largeur = sum(len(LETTRES[c][0]) for c in mot) + 2 * (len(mot) - 1)
    w, H = largeur + PENCHE + 4, h + 4
    plein = {}
    x0 = 1
    for c in mot:
        for y, rangee in enumerate(LETTRES[c]):
            decalage = PENCHE * (h - 1 - y) // (h - 1)
            for dx, ch in enumerate(rangee):
                if ch == "#":
                    plein[(x0 + dx + decalage, 1 + y)] = DEGRADE[y]
        x0 += len(LETTRES[c][0]) + 2
    contour = {(x + dx, y + dy) for x, y in plein for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    g = vide(w, H)
    for x, y in contour:
        if x + 2 < w and y + 2 < H:
            g[y + 2][x + 2] = OMBRE
    for x, y in contour:
        g[y][x] = CONTOUR
    for (x, y), c in plein.items():
        g[y][x] = c
    # L'eclat, sur l'empattement du dernier I.
    ex, ey = w - 4 - PENCHE // 2, 1
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        g[ey + dy][ex + dx] = PARCHEMIN
    g[ey][ex] = "#ffffff"
    return g


# --- Les formats --------------------------------------------------------------------


def en_svg(g: Grille) -> str:
    """Une rangee de pixels pareils, un rectangle."""
    h, w = len(g), len(g[0])
    rects = []
    for y, rangee in enumerate(g):
        x = 0
        while x < w:
            n = 1
            while x + n < w and rangee[x + n] == rangee[x]:
                n += 1
            if rangee[x]:
                rects.append(f'<rect x="{x}" y="{y}" width="{n}" height="1" fill="{rangee[x]}"/>')
            x += n
    corps = "\n  ".join(rects)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" shape-rendering="crispEdges">\n  {corps}\n</svg>\n')


def pixels(g: Grille, cote: int) -> bytes:
    """RGBA, `cote` x `cote`, agrandi au plus proche voisin."""
    h, w = len(g), len(g[0])
    sortie = bytearray()
    for Y in range(cote):
        rangee = g[Y * h // cote]
        for X in range(cote):
            c = rangee[X * w // cote]
            sortie += bytes.fromhex(c[1:]) + b"\xff" if c else b"\0\0\0\0"
    return bytes(sortie)


def en_png(g: Grille, cote: int) -> bytes:
    rgba = pixels(g, cote)
    brut = b"".join(b"\0" + rgba[i : i + 4 * cote] for i in range(0, len(rgba), 4 * cote))

    def morceau(nom: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(nom + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + nom + data + struct.pack(">I", crc)

    tete = struct.pack(">IIBBBBB", cote, cote, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + morceau(b"IHDR", tete)
            + morceau(b"IDAT", zlib.compress(brut, 9)) + morceau(b"IEND", b""))


def lire_png(octets: bytes) -> tuple[int, int, bytes] | None:
    """(largeur, hauteur, RGBA) d'un PNG ecrit par `en_png` ; None pour tout autre PNG."""
    if not octets.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    i, idat, tete = 8, b"", None
    while i + 8 <= len(octets):
        n, nom = struct.unpack(">I4s", octets[i : i + 8])
        data = octets[i + 8 : i + 8 + n]
        if nom == b"IHDR":
            tete = struct.unpack(">IIBBBBB", data)
        elif nom == b"IDAT":
            idat += data
        i += 12 + n
    if not tete or tete[2:] != (8, 6, 0, 0, 0):
        return None
    w, h = tete[:2]
    brut = zlib.decompress(idat)
    pas = 1 + 4 * w
    if len(brut) != pas * h or any(brut[r * pas] != 0 for r in range(h)):
        return None
    return w, h, b"".join(brut[r * pas + 1 : (r + 1) * pas] for r in range(h))


def en_ico(g: Grille, cotes: list[int]) -> bytes:
    """Un .ico qui porte des PNG — tous les navigateurs le lisent."""
    images = [en_png(g, c) for c in cotes]
    entrees, decalage = b"", 6 + 16 * len(images)
    for c, img in zip(cotes, images):
        entrees += struct.pack("<BBBBHHII", c % 256, c % 256, 0, 0, 1, 32, len(img), decalage)
        decalage += len(img)
    return struct.pack("<HHH", 0, 1, len(images)) + entrees + b"".join(images)


def lire_ico(octets: bytes) -> list[bytes]:
    """Les PNG d'un .ico."""
    _, _, n = struct.unpack("<HHH", octets[:6])
    images = []
    for k in range(n):
        *_, taille, decalage = struct.unpack("<BBBBHHII", octets[6 + 16 * k : 22 + 16 * k])
        images.append(octets[decalage : decalage + taille])
    return images


# --- Ecrire, verifier -----------------------------------------------------------------


def fichiers() -> dict[str, bytes]:
    ic, fav = icone(), favicon()
    return {
        "favicon.svg": en_svg(fav).encode(),
        "favicon.ico": en_ico(fav, [16, 32, 48]),
        "icone-180.png": en_png(ic, 180),
        "icone-192.png": en_png(ic, 192),
        "icone-512.png": en_png(ic, 512),
        "logo.svg": en_svg(logo()).encode(),
    }


def meme_image(nom: str, attendu: bytes, present: bytes) -> bool:
    if nom.endswith(".svg"):
        return attendu == present
    if nom.endswith(".png"):
        return lire_png(attendu) == lire_png(present)
    a, p = lire_ico(attendu), lire_ico(present)
    return len(a) == len(p) and all(lire_png(x) == lire_png(y) for x, y in zip(a, p))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verifier", action="store_true",
                        help="ne rien ecrire, dire ce qui n'est plus a jour")
    parser.add_argument("--dossier", type=Path, default=DOSSIER)
    args = parser.parse_args(argv)
    perimes = []
    for nom, octets in fichiers().items():
        chemin = args.dossier / nom
        if not args.verifier:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_bytes(octets)
        elif not chemin.exists() or not meme_image(nom, octets, chemin.read_bytes()):
            perimes.append(nom)
    if perimes:
        print(f"pas a jour : {', '.join(perimes)} — uv run python scripts/icones.py",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
