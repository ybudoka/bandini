"""Les concessionnaires : Prestige Automobiles aux Érables, Chez Ti-Pout dans les Friches
(docs/jalons/les-concessionnaires-le-neuf-aux-erables-l-usage-dans-les-friches.md).

Martin (28 sept. 2026) : « je veux un vendeur de voitures neuves dans un quartier riche avec plusieurs voitures
dans le stationnement et un vendeur de voitures usagées dans un quartier plus pauvre ou industriel ». On achète
ET on vole : le char payé est à toi (`aToi`), celui qu'on prend sans payer est un vol — et le neuf sonne.

⚠️ SUR LA VILLE FINIE ET SANS UN DÉ, comme le lot du poste (`poser_les_lots_et_les_rideaux`) et le dojo : chaque
lieu MESURE sa place, écrit ses tuiles dans `ville["sol"]` et AJOUTE sa porte, sa devanture, son point et sa pièce
au bout de leurs listes. Rien de la ville d'avant ne bouge.

⚠️ PAS LA QUINCAILLERIE, pourtant proposée d'abord : c'est la seule porte `artisan` de la ville d'avant, et deux
missions (`f04`, `p01`) y envoient acheter. Le Salon se BÂTIT sur la moitié sud du plus grand stationnement cossu
des Érables ; la moitié nord, ses cases `^` telles quelles, est le lot d'exposition.

La donnée d'un lot (Python décide, le navigateur fait naître les chars — `Vehicules.majLotsDeConcession`) :
`places` (y = la tuile du NEZ, comme au poste), `garees` (les index des places garnies), `stock` (un char par
place), `usure`, `alarme`, et `cour` (le rectangle de tuiles touché, pour les juges).
"""

from __future__ import annotations

from . import carte, devantures, vehicules

# --- Prestige Automobiles -------------------------------------------------------------------------

SALON_SLUG = "prestige"
SALON_NOM = "Prestige Automobiles"
#: La première qui tient dans le bandeau (`devantures.tient_en`).
SALON_ENSEIGNES = ("PRESTIGE AUTOMOBILES", "PRESTIGE AUTOS", "PRESTIGE")
#: Au moins six cases dans la rangée : « plusieurs voitures dans le stationnement ».
SALON_CASES_MIN = 6
#: Trois rangées de toit d'ardoise, une de façade.
SALON_PROFONDEUR = 4
#: Ce qui se vend neuf : (fiche du catalogue, silhouette). ⚠️ Pas le cabriolet : il a sa conductrice
#: (`au_volant`), et il n'est pas à vendre.
NEUFS = (("sport", "sport"), ("luxe", "luxe"), ("auto", "auto"), ("luxe", "luxe_vus"), ("auto", "auto_familiale"))
#: Le devant du Salon : ce sur quoi on sort en poussant la porte.
DEVANT = frozenset("_.,")


def _rangee(sol: list[str], y: int, x0: int, largeur: int, glyphes) -> bool:
    return all(sol[y][x] in glyphes for x in range(x0, x0 + largeur))


def _batissable(sol: list[str], y: int, x0: int, largeur: int) -> bool:
    return all(carte.solidite(sol[y][x]) == 0 and sol[y][x] not in "Dd" for x in range(x0, x0 + largeur))


def trouver_le_salon(chantier, ville: dict) -> dict | None:
    """La plus longue rangée de cases `^` d'un stationnement cossu des Érables dont le dessous se prête au Salon :
    la case fait deux tuiles, une allée de `p` la suit, puis `SALON_PROFONDEUR` rangées sans rien de solide (le
    Salon), puis un devant marchable. À égalité, la plus au nord, puis la plus à l'ouest. Aucune : None."""
    sol = ville["sol"]
    hauteur = len(sol)
    meilleure = None
    for y in range(1, hauteur - 1):
        ligne, x = sol[y], 0
        while x < len(ligne):
            if ligne[x] != "^":
                x += 1
                continue
            x0 = x
            while x < len(ligne) and ligne[x] == "^":
                x += 1
            largeur = x - x0
            if largeur < SALON_CASES_MIN or not _rangee(sol, y + 1, x0, largeur, "^"):
                continue
            if any(sol[y - 1][i] == "^" for i in range(x0, x0 + largeur)):
                continue                                  # pas le nez de la case
            allee = y + 2
            while allee < hauteur and _rangee(sol, allee, x0, largeur, "p"):
                allee += 1
            if allee - (y + 2) < carte.ALLEE:
                continue
            yb, yd = allee, allee + SALON_PROFONDEUR
            if yd >= hauteur or not all(_batissable(sol, j, x0, largeur) for j in range(yb, yd)):
                continue
            if not _rangee(sol, yd, x0, largeur, DEVANT):
                continue
            milieu = x0 + largeur // 2
            if chantier.district_en(milieu, y) != "erables" or chantier.standing_en(milieu, y) != "cossu":
                continue
            cle = (-largeur, y, x0)
            if meilleure is None or cle < meilleure[0]:
                meilleure = (cle, {"x": x0, "y": y, "largeur": largeur, "batiment": yb})
    return meilleure[1] if meilleure else None


def _facade(largeur: int, porte: int) -> str:
    return "".join("D" if i == porte else "F" if i in (0, largeur - 1) else "W" for i in range(largeur))


def _ecrire(ville: dict, x: int, y: int, texte: str) -> None:
    ligne = ville["sol"][y]
    ville["sol"][y] = ligne[:x] + texte + ligne[x + len(texte):]


def _degager(ville: dict, tuiles: set[tuple[int, int]]) -> None:
    """Ce qui s'était posé sur les tuiles du bâtiment ou devant sa porte s'en va, sa lampe avec."""
    partis = [d for d in ville["decor"] if (d["x"], d["y"]) in tuiles]
    ville["decor"][:] = [d for d in ville["decor"] if (d["x"], d["y"]) not in tuiles]
    eteintes = {(d["x"], d["y"]) for d in partis if d["type"] == "lampadaire"}
    ville["lampes"][:] = [lampe for lampe in ville["lampes"] if (lampe["x"], lampe["y"]) not in eteintes]


def _enseigne(textes: tuple[str, ...], largeur: int) -> str:
    return next((t for t in textes if devantures.tient_en(t, largeur, carte.TUILE_PX)), textes[-1])


def _devanture(ville: dict, x: int, y: int, motifs: str, porte: int, textes: tuple[str, ...], genre: str,
               standing: str) -> None:
    """L'enseigne au-dessus de la porte, et la lampe de sa vitrine. ⚠️ Les règles de toutes les devantures
    (`test_devantures`) : au plus `ENSEIGNE_ETIREE` tuiles, centrée sur la porte ; rien que des vitrines et la
    porte dessous (pas les coins de façade) ; le `standing` du bloc ; une lampe de vitrine au trottoir."""
    large = min(len(motifs), carte._Chantier.ENSEIGNE_ETIREE)
    dx = max(0, min(len(motifs) - large, porte - large // 2))
    dessous = motifs[dx:dx + large]
    ville["devantures"].append({"x": x + dx, "y": y, "l": large, "genre": devantures.genre_index(genre),
                                "texte": _enseigne(textes, large), "pancarte": -1, "motifs": dessous,
                                "porte": porte - dx, "standing": standing})
    ville["lampes"].append({"x": x + dx + large // 2, "y": y + 1, "r": 20 + 4 * large, "c": "vitrine"})


def _stock(modeles: tuple[tuple[str, str], ...], n: int, part: float) -> list[dict]:
    """Un char par place, et son prix : celui du catalogue (`vehicules.CATALOGUE`), fois `part`."""
    prix = {v["slug"]: v["prix"] for v in vehicules.CATALOGUE}
    return [{"slug": s, "sprite": sp, "prix": round(prix[s] * part)} for s, sp in (modeles[i % len(modeles)]
                                                                               for i in range(n))]


def piece_de_salon(slug: str, largeur: int, hauteur: int, porte: int) -> dict:
    """Le salon d'exposition aux mesures de son bâtiment : des plantes aux coins du fond, le bureau du gérant et
    sa chaise du côté opposé à la porte, le comptoir à l'avant-dernière rangée et le vendeur derrière ; la dernière
    rangée libre — on entre. ⚠️ Sans un dé : les mêmes mesures donnent le même salon."""
    grille = [[" "] * largeur for _ in range(hauteur)]
    grille[0][0], grille[0][largeur - 1] = "n", "n"
    # ⚠️ LE COMPTOIR LOIN DE LA PORTE, au fond : devant elle, il lui volerait ACTION (`carte.RAYON_POINT`).
    long_, gauche = 3, porte > largeur / 2
    debut = 1 if gauche else largeur - 1 - long_
    comptoir = [(x, 1) for x in range(debut, debut + long_)]
    for x, y in comptoir:
        grille[y][x] = "c"
    bureau = largeur - 3 if gauche else 1
    grille[1][bureau], grille[1][bureau + 1] = "a", "h"
    point = carte._poser_le_point(grille, "concession", None, porte, list(reversed(comptoir)), lot=slug)
    pris: set[tuple[int, int]] = set()
    vendeur = carte._quelqu_un(grille, "commis", (debut + 1, 0), porte, pris)
    return carte._piece(slug, SALON_NOM, carte._plan_de(grille, porte), sol="t", points=(point,),
                        gens=carte._gens(vendeur))


def poser_le_salon(chantier, ville: dict) -> None:
    """Prestige Automobiles, bâti sur la moitié sud du stationnement trouvé ; la moitié nord est son lot."""
    trouve = trouver_le_salon(chantier, ville)
    if not trouve:
        return
    x0, largeur, yb = trouve["x"], trouve["largeur"], trouve["batiment"]
    yf, px = yb + SALON_PROFONDEUR - 1, x0 + largeur // 2
    for j in range(yb, yf):
        _ecrire(ville, x0, j, "E" * largeur)
    motifs = _facade(largeur, px - x0)
    _ecrire(ville, x0, yf, motifs)
    # ⚠️ LES ÎLOTS DES CASES `v` qu'on a bâties : ils bordaient une rangée qui n'est plus là, et un îlot ne se
    # tient qu'au bout d'une rangée (`test_carte`). Ils redeviennent de la pelouse.
    for y in range(yb, yf + 1):
        for x in (x0 - 1, x0 + largeur):
            if ville["sol"][y][x] == "I":
                _ecrire(ville, x, y, ",")
    _degager(ville, {(x, y) for x in range(x0, x0 + largeur) for y in range(yb, yf + 1)} | {(px, yf + 1)})
    ville["portes"].append({"x": px, "y": yf, "interieur": SALON_SLUG, "lieu": SALON_SLUG, "nom": SALON_NOM,
                            "vitrine": [x0, largeur]})
    _devanture(ville, x0, yf, motifs, px - x0, SALON_ENSEIGNES, "commerce", "+")
    ville["points_interet"].append({"type": SALON_SLUG, "slug": SALON_SLUG, "nom": SALON_NOM,
                                    "x": px, "y": yf + 1, "famille": "magasin"})
    ville["interieurs"][SALON_SLUG] = piece_de_salon(SALON_SLUG, largeur, SALON_PROFONDEUR, px - x0 + 1)
    places = [{"x": x0 + i, "y": trouve["y"], "sens": "N"} for i in range(largeur)]
    en_face = px - x0
    ville["concessionnaires"].append({
        "slug": SALON_SLUG, "nom": SALON_NOM, "genre": "neuf",
        "places": places, "garees": [i for i in range(largeur) if i != en_face],
        "stock": _stock(NEUFS, largeur, 1.0),
        "usure": 1.0, "alarme": True,
        "cour": {"x": x0 - 1, "y": trouve["y"], "l": largeur + 2, "h": yf + 1 - trouve["y"]},
    })


# --- Chez Ti-Pout -----------------------------------------------------------------------------------

TI_POUT_SLUG = "ti_pout"
TI_POUT_NOM = "Chez Ti-Pout — Autos usagées"
TI_POUT_ENSEIGNES = ("TI-POUT AUTOS", "TI-POUT")
#: La cour, en tuiles, grillage compris ; sa dernière rangée touche le trottoir du boulevard.
TI_POUT_L, TI_POUT_H = 16, 8
#: La trouée du grillage, au sud : (décalage depuis l'ouest, largeur). La seule entrée.
TROUEE = (9, 5)
#: La roulotte-bureau : (décalage depuis l'ouest, largeur), rangées 1 à 3 de la cour (deux de tôle, une de façade).
ROULOTTE = (1, 5)
#: Les places, (décalage x, rangée du NEZ, sens) : quatre nez au sud contre le grillage du nord, trois nez au nord
#: devant la roulotte. ⚠️ Pas de cases peintes : un lot d'usagés n'a pas de lignes, et des `^` ici attireraient la
#: nuit les chars de la rue (`placeDeNuit` choisit parmi les cases de la carte).
PLACES_TI_POUT = ((8, 2, "S"), (10, 2, "S"), (12, 2, "S"), (14, 2, "S"), (2, 5, "N"), (4, 5, "N"), (6, 5, "N"))
#: Ce qui se vend usagé : des minounes et un vieux camion.
USAGES = (("auto", "auto_compacte"), ("auto", "auto_familiale"), ("camion", "camion"), ("auto", "auto_camionnette"),
          ("auto", "auto"))
#: La vie d'un usagé, en fraction : celle des minounes des rues pauvres (`STANDING_DU_PARC`).
USURE_USAGEE = 0.6
#: Le prix d'un usagé, en fraction de celui du catalogue.
PRIX_USAGE = 0.4
#: La façade de la roulotte : des fenêtres et la porte — une de placardée, c'est les Friches (`test_quartiers` :
#: en pauvre, une vitrine sur trois). ⚠️ Rien d'autre que `WDB` : c'est tout entière la devanture.
FACADE_ROULOTTE = "WWDWB"


def trouver_ti_pout(ville: dict) -> dict | None:
    """Une cour de `TI_POUT_L` × `TI_POUT_H` d'herbe, SANS décor ni lampe, dans les Friches, contre le boulevard qui
    les borde au sud (sa dernière rangée est `decalage_nord - 1`). La plus proche du milieu du district."""
    n = ville.get("decalage_nord")
    zone = next((z for z in ville["zones"] if z["slug"] == "friches" and not z.get("gang")), None)
    if not n or not zone:
        return None
    sol, y0 = ville["sol"], n - TI_POUT_H
    occupees = {(d["x"], d["y"]) for d in ville["decor"]} | {(lampe["x"], lampe["y"]) for lampe in ville["lampes"]}
    milieu = zone["x"] + zone["l"] / 2
    meilleure = None
    for x0 in range(zone["x"], zone["x"] + zone["l"] - TI_POUT_L + 1):
        tuiles = [(x, y) for y in range(y0, n) for x in range(x0, x0 + TI_POUT_L)]
        if any(sol[y][x] != "," or (x, y) in occupees for x, y in tuiles):
            continue
        if any(carte.solidite(sol[n][x0 + TROUEE[0] + i]) != 0 for i in range(TROUEE[1])):
            continue
        cle = (abs(x0 + TI_POUT_L / 2 - milieu), x0)
        if meilleure is None or cle < meilleure[0]:
            meilleure = (cle, {"x": x0, "y": y0})
    return meilleure[1] if meilleure else None


def piece_de_roulotte(slug: str, largeur: int, hauteur: int, porte: int) -> dict:
    """Le bureau de Ti-Pout : la cafetière sur son poêle, le classeur des papiers, le bureau et sa chaise, et
    Ti-Pout debout à côté — il vient au-devant du client. ⚠️ Sans un dé."""
    grille = [[" "] * largeur for _ in range(hauteur)]
    grille[0][0], grille[0][largeur - 2], grille[0][largeur - 1] = "z", "a", "k"
    grille[1][largeur - 2] = "h"
    point = carte._poser_le_point(grille, "concession", None, porte, [(largeur - 2, 0)], lot=slug)
    pris: set[tuple[int, int]] = set()
    ti_pout = carte._quelqu_un(grille, "commis", (largeur // 2, 1), porte, pris)
    return carte._piece(slug, TI_POUT_NOM, carte._plan_de(grille, porte), sol="t", points=(point,),
                        gens=carte._gens(ti_pout))


def poser_ti_pout(ville: dict) -> None:
    """Chez Ti-Pout : une cour de poussière de pierre grillagée, sa roulotte, et ses minounes."""
    trouve = trouver_ti_pout(ville)
    if not trouve:
        return
    x0, y0 = trouve["x"], trouve["y"]
    x1, y1 = x0 + TI_POUT_L - 1, y0 + TI_POUT_H - 1
    for y in range(y0, y1 + 1):
        bord = y in (y0, y1)
        ligne = "".join("f" if bord or x in (x0, x1) else "g" for x in range(x0, x1 + 1))
        if y == y1:
            debut = TROUEE[0]
            ligne = ligne[:debut] + "g" * TROUEE[1] + ligne[debut + TROUEE[1]:]
        _ecrire(ville, x0, y, ligne)
    rx, rl = x0 + ROULOTTE[0], ROULOTTE[1]
    px, yf = rx + FACADE_ROULOTTE.index("D"), y0 + 3
    _ecrire(ville, rx, y0 + 1, "B" * rl)
    _ecrire(ville, rx, y0 + 2, "B" * rl)
    # Le sol porte la vitre (`W`), la devanture dit qu'elle est placardée (`B`) — comme partout ailleurs.
    _ecrire(ville, rx, yf, FACADE_ROULOTTE.replace("B", "W"))
    ville["portes"].append({"x": px, "y": yf, "interieur": TI_POUT_SLUG, "lieu": TI_POUT_SLUG, "nom": TI_POUT_NOM,
                            "vitrine": [rx, rl]})
    _devanture(ville, rx, yf, FACADE_ROULOTTE, px - rx, TI_POUT_ENSEIGNES, "industrie", "-")
    ville["points_interet"].append({"type": TI_POUT_SLUG, "slug": TI_POUT_SLUG, "nom": TI_POUT_NOM,
                                    "x": px, "y": yf + 1, "famille": "magasin"})
    ville["interieurs"][TI_POUT_SLUG] = piece_de_roulotte(TI_POUT_SLUG, rl, 3, px - rx + 1)
    places = [{"x": x0 + dx, "y": y0 + dy, "sens": sens} for dx, dy, sens in PLACES_TI_POUT]
    ville["concessionnaires"].append({
        "slug": TI_POUT_SLUG, "nom": TI_POUT_NOM, "genre": "usage",
        "places": places, "garees": list(range(len(places))),
        "stock": _stock(USAGES, len(places), PRIX_USAGE),
        "usure": USURE_USAGEE, "alarme": False,
        "cour": {"x": x0, "y": y0, "l": TI_POUT_L, "h": TI_POUT_H},
    })
