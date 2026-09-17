"""Les éboueurs de Baie-des-Brumes : une tournée, ses bacs, son horaire.

M12, « La ville vit » (17 sept. 2026) : « un camion à bras mécanique — Québec
ramasse les bacs comme ça — qui s'arrête tous les vingt mètres, lève un bac,
repart. Un obstacle qui BOUGE dans la rue, une raison de le dépasser. »

⚠️ **Python trace, le navigateur roule** — exactement comme les autobus, et avec
leur machinerie (`autobus._Reseau`, `autobus._boucle`) : une tournée est une boucle
qui obéit au champ de direction, ne tourne qu'une fois par boîte et ne passe jamais
où la ville peut fermer. Le camion ne choisit jamais une rue.

⚠️ **Rien ne se pose dans la ville.** Les bacs sont sortis le matin de la collecte
et rentrés l'après-midi : c'est le navigateur qui les fait naître, hors de l'écran,
aux points que ce module donne. La ville du premier matin est la même avec ou sans
éboueurs — pas un arbre ne bouge, et ce module ne tire aucun dé.
"""

from __future__ import annotations

from . import autobus

#: Le quartier de la tournée : la banlieue, là où il y a des bacs au bord du
#: trottoir devant chaque maison.
DISTRICT = "erables"

#: Combien d'étapes pour tracer la boucle : les quatre coins des maisons du
#: quartier. Assez pour faire le tour, pas assez pour y passer la journée.
ETAPES = 4

#: Le pas entre deux bacs, en tuiles le long de la tournée : « tous les vingt
#: mètres ». Et jamais un bac à moins de tant de tuiles d'une boîte de croisement :
#: le camion s'arrêterait dans le carrefour.
PAS_ENTRE_BACS = 5
LOIN_DES_BOITES = 3

#: Ce que le navigateur suit. `vitesse_px` : la vitesse MOYENNE, arrêts compris —
#: c'est elle qui place un camion qu'on ne voit pas sur sa tournée.
HORAIRE: dict = {
    "debut": 6 / 24,             # la tournée commence à six heures
    "fin": 12 / 24,              # et se termine à midi
    "sortis_des": 5 / 24,        # les bacs sont au bord du trottoir dès cinq heures
    "rentres_a": 15 / 24,        # et rentrés à quinze heures
    "vitesse_px": 0.55,
    "arret_images": 110,         # le temps de lever un bac, de le vider, de le poser
    "leve_images": 70,           # dont le bac en l'air
    "naissance_min_px": 300,     # hors de l'écran, dans la bulle (voir `autobus.ATTENTE`)
    "naissance_max_px": 480,
}

MIN_BACS = 12


def _coins_du_quartier(ville: dict) -> list[tuple[int, int]]:
    """Les quatre maisons du quartier les plus au nord-ouest, nord-est, sud-est et
    sud-ouest — dans cet ordre, pour que la boucle en fasse le tour."""
    zones = [z for z in ville["zones"] if z.get("district") == DISTRICT]
    maisons = []
    for r in ville["residences"]:
        if any(z["x"] <= r["x"] < z["x"] + z["l"] and z["y"] <= r["y"] < z["y"] + z["h"] for z in zones):
            maisons.append((r["x"], r["y"]))
    if len(maisons) < ETAPES:
        return []
    maisons.sort()
    return [min(maisons, key=lambda m: m[0] + m[1]),
            max(maisons, key=lambda m: m[0] - m[1]),
            max(maisons, key=lambda m: m[0] + m[1]),
            min(maisons, key=lambda m: m[0] - m[1])]


def tracer(ville: dict) -> dict | None:
    """La tournée, prête pour le paquet — ou None si le quartier n'en porte pas."""
    reseau = autobus._Reseau(ville)
    coins = _coins_du_quartier(ville)
    if not coins:
        return None
    voies = [(x, y) for y in range(reseau.hauteur) for x in range(reseau.largeur)
             if reseau.longe_le_trottoir(x, y) and (x, y) not in reseau.boites and (x, y) not in reseau.interdites]
    etapes = [sorted(voies, key=lambda t, c=c: (abs(t[0] - c[0]) + abs(t[1] - c[1]), t))[:autobus.ESSAIS_PAR_ETAPE]
              for c in coins]
    construite = autobus._boucle(reseau, etapes)
    if construite is None:
        return None
    boucle = construite[0]

    # Ce qui occupe déjà un bord de trottoir : le décor, les abribus et leur quai, les
    # portes et leur pas.
    occupe = {(d["x"], d["y"]) for d in ville["decor"]}
    for rang in range(len(ville["autobus"]["arrets"])):
        d = autobus.detail(ville, rang)
        occupe |= {tuple(d["quai"]), tuple(d["abri"])}
    portes = {(p["x"], p["y"] + 1) for p in ville["portes"]}

    n = len(boucle)
    points: list[list[int]] = []
    dernier = -PAS_ENTRE_BACS
    for i, (x, y) in enumerate(boucle):
        if i - dernier < PAS_ENTRE_BACS or not reseau.longe_le_trottoir(x, y):
            continue
        dx, dy = autobus.PAS[reseau.voie[y][x]]
        # Loin des boîtes, en amont comme en aval.
        if any(boucle[(i + k) % n] in reseau.boites for k in range(-LOIN_DES_BOITES, LOIN_DES_BOITES + 1)):
            continue
        rx, ry = autobus.a_droite(dx, dy)
        bord = (x + rx, y + ry)
        if bord in occupe or bord in portes or not reseau.dedans(*bord):
            continue
        if not any(z["x"] <= bord[0] < z["x"] + z["l"] and z["y"] <= bord[1] < z["y"] + z["h"]
                   for z in ville["zones"] if z.get("district") == DISTRICT):
            continue
        points.append([i, bord[0], bord[1]])
        dernier = i
    if len(points) < MIN_BACS:
        return None
    return {"trace": autobus.coins(boucle), "points": points, "horaire": dict(HORAIRE)}
