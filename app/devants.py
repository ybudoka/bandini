"""Rien devant une porte, plus large : ce qui bouche se déplace, la ville ne se re-tire pas.

Retour de Martin (20 sept. 2026) : « déplace les obstacles pour éviter que ça soit devant
les portes des commerces et dans les missions ».

⚠️ **Deux tuiles réservées ne suffisent pas.** `degager_le_devant` tient le pas de porte
(deux tuiles dans l'axe) et un juge le garde vide. Mais un obstacle se lit « devant » dès
qu'il est dans l'axe à TROIS tuiles, ou collé de côté : la scène d'un amuseur dont la foule
tombe sur le seuil, un kiosque contre la porte du terminus, un BBQ, une caisse, un arbre.
Mesuré sur quatre graines : quinze à quarante objets par ville, qu'aucune réserve ne voyait.

⚠️ **On DÉPLACE après coup, on ne réserve pas plus large.** Réserver des tuiles pendant la
construction re-tire toute la ville (voir `_Chantier.degager_le_devant` : deux tuiles ont
déjà fait tomber trois juges sans rapport, une rangée de la trame vingt-six). Ce module
tourne donc sur la ville FINIE, à la toute fin, **sans aucun dé** : il regarde ce qui se
tient devant une porte et le pose sur la tuile voisine qui convient — la plus proche, dans
l'ordre de lecture, jamais au hasard. Tout ce qui se pose autour (abribus, bacs des
éboueurs, édicules du métro, arbres de rue) a déjà choisi sa place, et une place prise ne
se reprend pas : elle est exclue de ce qu'on peut viser.

⚠️ **Le devant d'un lieu de mission est plus large** (`DEVANT_DE_MISSION`) : c'est là que le
donneur attend, que le char se livre, que la coupe de l'intro va filmer. Les lieux se lisent
dans `missions` (objectifs, scènes, personnages), jamais dans une liste écrite ici.

⚠️ **Ce qui apparaît en jeu** (la voie fermée du jour, le bris d'aqueduc, un nid-de-poule)
se tire dans des listes : ce qui tombe devant une porte est MARQUÉ `ecartee` (le jeu passe au
suivant) ou, pour les nids-de-poule, sorti de sa liste. On n'en fait pas glisser un autre :
la ville en garde assez, et le tracé des autobus, calculé sur la liste entière, reste valide.
"""

from __future__ import annotations

#: Le devant d'une porte : trois tuiles dans l'axe et une de chaque côté. C'est la fenêtre
#: que `mobilier` et `metro` tiennent déjà pour leurs propres pièces. ⚠️ Elle voyage avec la
#: ville (`ville["devant"]`) : le jeu la lit là pour ne poser aucun personnage de mission
#: sur un pas de porte, il ne la récrit pas.
DEVANT_COTE = 1
DEVANT_PROFONDEUR = 3
DEVANT = tuple((dx, dy) for dy in range(1, DEVANT_PROFONDEUR + 1)
               for dx in range(-DEVANT_COTE, DEVANT_COTE + 1))

#: Le devant d'un lieu de mission : le donneur se tient à deux tuiles de côté, le char se
#: livre plus loin devant.
DEVANT_DE_MISSION = tuple((dx, dy) for dy in (1, 2, 3, 4) for dx in (-2, -1, 0, 1, 2))

#: Jusqu'où on cherche une tuile voisine, en tuiles. Plus loin, l'objet n'est plus « à côté
#: de là où il était » : on le retire plutôt que de l'envoyer dans un autre quartier. Un
#: kiosque cherche plus loin qu'un baril : il y en a peu, et chacun a une raison d'être là.
PORTEE = 8
PORTEE_D_UN_KIOSQUE = 14
#: Une scène cherche dans tout son îlot ou presque : le numéro d'un amuseur se joue « sur la place »,
#: pas à deux tuiles près, et l'îlot lui borne déjà le quartier.
PORTEE_D_UNE_SCENE = 16

#: Le décor qu'on peut prendre et poser ailleurs : du mobilier de ville sans sens ni attache.
#: ⚠️ Pas les machines encastrées dans une vitrine (`guichet`, `distributrice_*`), pas les
#: lampadaires (une lampe les suit), pas les abribus (le tracé des lignes), les édicules (le
#: métro), les bancs (ils regardent la rue) ni ce qui vit au bord de l'eau ou à la foire.
DECOR_MOBILE = frozenset({
    "arbre", "buisson", "caisse", "baril", "bbq", "debris", "ordures", "pneu", "palettes",
    "poubelle", "poubelle_pleine", "boite_aux_lettres", "bac_recyclage", "benne", "cabanon",
    "table_pique_nique", "caddie", "parcometre", "borne_fontaine", "bac_fleurs",
})


def portes(ville: dict) -> dict[tuple[int, int], str | None]:
    """Toutes les portes qu'on VOIT, avec le lieu qu'elles ouvrent (`None` : une porte peinte
    ou condamnée). Celles du sol (poussée, condamnée, de garage) et celles qu'une devanture
    ou un logement se peint (`P`)."""
    from . import carte

    lieux = {(p["x"], p["y"]): p["lieu"] for p in ville["portes"]}
    trouvees: dict[tuple[int, int], str | None] = {}
    for y, ligne in enumerate(ville["sol"]):
        for x, glyphe in enumerate(ligne):
            if glyphe in carte.PORTES_DE_FACADE:
                trouvees[(x, y)] = lieux.get((x, y))
    for facade in ville["devantures"] + ville["residences"]:
        for i, motif in enumerate(facade["motifs"]):
            if motif == "P":
                trouvees.setdefault((facade["x"] + i, facade["y"]), None)
    for garage in ville.get("portes_garage") or []:
        for i in range(garage["l"]):
            trouvees[(garage["x"] + i, garage["y"])] = garage["lieu"]
    return trouvees


def lieux_de_mission(ville: dict) -> set[str]:
    """Les lieux où les missions et les défis vont, attendent ou livrent : tout ce qu'un
    objectif, une scène ou un personnage nomme (`lieu`, `porte:<lieu>`, `ruelle:<lieu>:n`), et
    la pièce du personnage qui se tient dedans (`point:<type>`)."""
    from . import carte, missions

    lieux: set[str] = set()

    def lire(valeur, cle: str = "") -> None:
        if isinstance(valeur, str):
            if valeur.startswith("porte:"):
                lieux.add(valeur.split(":")[1])
            elif valeur.startswith("ruelle:"):
                lieux.add(valeur.split(":")[1])
            elif cle == "lieu":
                lieux.add(valeur)
        elif isinstance(valeur, dict):
            for k, v in valeur.items():
                lire(v, k)
        elif isinstance(valeur, (list, tuple)):
            for v in valeur:
                lire(v, cle)

    lire(missions.CATALOGUE)
    lire(missions.DEFIS)
    for personnage in missions.PERSONNAGES:
        ou = personnage["ou"]
        lire(ou)
        if ou.startswith("point:"):
            lieux |= {slug for slug, piece in carte.INTERIEURS.items()
                      if any(p["type"] == ou[6:] for p in piece["points"])}
    return lieux & {p["lieu"] for p in ville["portes"]}


def devants(ville: dict) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """(le devant élargi, le pas de porte réservé) de toutes les portes de la ville."""
    missions_ = lieux_de_mission(ville)
    larges: set[tuple[int, int]] = set()
    pas: set[tuple[int, int]] = set()
    for (x, y), lieu in portes(ville).items():
        zone = DEVANT_DE_MISSION if lieu in missions_ else DEVANT
        larges |= {(x + dx, y + dy) for dx, dy in zone}
        pas |= {(x, y + 1), (x, y + 2)}
    return larges, pas


def _anneaux(x: int, y: int, portee: int = PORTEE):
    """Les tuiles autour de (x, y), de la plus proche à la plus lointaine, dans l'ordre de
    lecture : aucun dé, la même réponse à chaque génération."""
    for r in range(1, portee + 1):
        for j in range(y - r, y + r + 1):
            for i in range(x - r, x + r + 1):
                if max(abs(i - x), abs(j - y)) == r:
                    yield i, j


def _pris(chantier, ville: dict) -> set[tuple[int, int]]:
    """Ce qui a déjà choisi sa place et ne la rend pas : le décor et tout ce qui s'y ajoute
    après lui (les quais et abris d'autobus, les stations du métro, les bacs de la tournée
    des éboueurs, les rampes et leur piste)."""
    from . import autobus

    pris = set(chantier.occupe) | set(chantier.reserve)
    pris |= {(d["x"], d["y"]) for d in ville["decor"]}
    for couche in ("ambulants", "reclames", "paquets", "scenes"):
        pris |= {(o["x"], o["y"]) for o in ville[couche]}
    # ⚠️ `.get` partout : les juges qui comparent la ville avec et sans une étape (les lignes,
    # le métro) la vident — et cette étape-ci vient après elles toutes.
    for rang in range(len((ville.get("autobus") or {}).get("arrets", []))):
        detail = autobus.detail(ville, rang)
        pris |= {tuple(detail["quai"]), tuple(detail["abri"])}
    pris |= {(s["x"], s["y"]) for s in (ville.get("metro") or {}).get("stations", [])}
    pris |= {(x, y) for _, x, y in (ville.get("eboueurs") or {}).get("points", [])}
    for rampe in ville["rampes"]:
        for n in range(-12, rampe["reception"] + 3):
            for lat in (-1, 0, 1):
                pris.add((rampe["x"] + rampe["dx"] * n - rampe["dy"] * lat,
                          rampe["y"] + rampe["dy"] * n + rampe["dx"] * lat))
    return pris


def _evitees(chantier, ville: dict) -> set[tuple[int, int]]:
    """Ce qui reste nu : les coins de croisement, le parvis du terminus, les chantiers, les
    plages, la foire et le rond des amuseurs. ⚠️ C'est la liste de la saleté, lue au même
    endroit — le décor s'y range, un kiosque déjà en place n'en est pas chassé."""
    from . import salete

    return salete._evitees(chantier, ville)


def _deplacer_le_decor(chantier, ville: dict, larges: set, pris: set,
                       evitees: set) -> tuple[int, int]:
    """Le décor mobile qui bouche : posé sur la tuile voisine la plus proche, du même sol,
    qui ne coupe aucun passage — sinon retiré. Rend (déplacés, retirés)."""
    from . import carte, mobilier

    solides = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
    deplaces = retires = 0
    for d in sorted((d for d in ville["decor"]
                     if d["type"] in DECOR_MOBILE and (d["x"], d["y"]) in larges),
                    key=lambda d: (d["y"], d["x"])):
        x0, y0 = d["x"], d["y"]
        chantier.occupe.discard((x0, y0))
        solides.discard((x0, y0))
        glyphe = chantier.sol[y0][x0]
        cible = next(((x, y) for x, y in _anneaux(x0, y0)
                      if 0 <= x < chantier.largeur and 0 <= y < chantier.hauteur
                      and chantier.sol[y][x] == glyphe
                      and (x, y) not in larges and (x, y) not in pris and (x, y) not in evitees
                      and mobilier._place_libre(chantier, x, y, solides)), None)
        if cible is None:
            ville["decor"].remove(d)
            retires += 1
            continue
        d["x"], d["y"] = cible
        chantier.occupe.add(cible)
        pris.add(cible)
        if d["type"] in carte.DECOR_SOLIDE:
            solides.add(cible)
        deplaces += 1
    return deplaces, retires


def _deplacer_les_scenes(chantier, ville: dict, larges: set, pas: set) -> tuple[int, int]:
    """La scène d'un amuseur dont le centre est devant une porte, ou dont la foule (une tuile
    autour) tombe sur un pas de porte : reposée dans son îlot sur la tuile qui convient, la
    plus proche. Rend (déplacées, retirées)."""
    regions = chantier.regions()
    scenes = ville["scenes"]
    deplacees = retirees = 0

    def foule_sur_un_seuil(x: int, y: int) -> bool:
        return any((x + i, y + j) in pas for i in (-1, 0, 1) for j in (-1, 0, 1))

    for s in sorted((s for s in scenes
                     if (s["x"], s["y"]) in larges or foule_sur_un_seuil(s["x"], s["y"])),
                    key=lambda s: (s["y"], s["x"])):
        region = next((r for r in regions if r[0] == s["ilot"]
                       and r[1] <= s["x"] < r[1] + r[3] and r[2] <= s["y"] < r[2] + r[4]), None)
        autres = [(o["x"], o["y"]) for o in scenes if o is not s]
        cible = None
        if region:
            _, rx, ry, rl, rh = region
            cible = next(((x, y) for x, y in _anneaux(s["x"], s["y"], PORTEE_D_UNE_SCENE)
                          if rx <= x < rx + rl and ry <= y < ry + rh
                          and (x, y) not in larges and not foule_sur_un_seuil(x, y)
                          and chantier._scene_possible(x, y)
                          and all(abs(x - ox) + abs(y - oy) >= chantier.SCENES_ECART
                                  for ox, oy in autres)), None)
        if cible is None:
            scenes.remove(s)
            retirees += 1
            continue
        s["x"], s["y"] = cible
        deplacees += 1
    return deplacees, retirees


def _deplacer_les_kiosques(chantier, ville: dict, larges: set, pris: set) -> tuple[int, int]:
    """Un kiosque ou une roulotte devant une porte (ou dont le client, sur la dalle devant lui,
    se tient devant une porte) : sur la place de même sorte, du même quartier, la plus proche.
    Sa réclame le suit, et se déplace à son tour si elle n'est plus à portée de marche."""
    from . import magasins

    places: dict[tuple, set] = {}
    ambulants = ville["ambulants"]
    deplaces = retires = 0
    for a in sorted((a for a in ambulants
                     if (a["x"], a["y"]) in larges or (a["x"], a["y"] + 1) in larges),
                    key=lambda a: (a["y"], a["x"])):
        commerce = magasins.ambulant(a["slug"])
        cle = (commerce["sur"], tuple(commerce.get("districts") or ()))
        if cle not in places:
            places[cle] = set(chantier._places_ambulantes(commerce["sur"], commerce.get("districts")))
        district = chantier.district_en(a["x"], a["y"])
        autres = [(o["x"], o["y"]) for o in ambulants if o is not a]
        cible = next(((x, y) for x, y in _anneaux(a["x"], a["y"], PORTEE_D_UN_KIOSQUE)
                      if (x, y) in places[cle] and (x, y) not in larges and (x, y + 1) not in larges
                      and (x, y) not in pris and chantier.district_en(x, y) == district
                      and all(abs(x - ox) + abs(y - oy) >= 22 for ox, oy in autres)), None)
        ancien = (a["x"], a["y"])
        if cible is None:
            ambulants.remove(a)
            ville["reclames"][:] = [r for r in ville["reclames"]
                                    if (r["kiosque"]["x"], r["kiosque"]["y"]) != ancien]
            retires += 1
            continue
        a["x"], a["y"] = cible
        pris.add(cible)
        chantier.occupe.discard(ancien)
        chantier.occupe.add(cible)
        for r in ville["reclames"]:
            if (r["kiosque"]["x"], r["kiosque"]["y"]) == ancien:
                r["kiosque"] = {"x": cible[0], "y": cible[1]}
        deplaces += 1
    return deplaces, retires


def _deplacer_les_reclames(chantier, ville: dict, larges: set, pris: set) -> tuple[int, int]:
    """Le poste d'un homme-sandwich devant une porte, ou devenu trop loin de son kiosque :
    la place de trottoir la plus proche, à portée de marche du kiosque, dans son quartier."""
    from . import magasins

    mini, maxi = magasins.RECLAME["poste_tuiles"]
    trottoirs = set(chantier._places_ambulantes("trottoir"))
    deplaces = retires = 0

    def a_portee(r: dict, x: int, y: int) -> bool:
        k = r["kiosque"]
        return mini <= abs(x - k["x"]) + abs(y - k["y"]) <= maxi

    for r in sorted((r for r in ville["reclames"]
                     if (r["x"], r["y"]) in larges or not a_portee(r, r["x"], r["y"])),
                    key=lambda r: (r["y"], r["x"])):
        district = chantier.district_en(r["kiosque"]["x"], r["kiosque"]["y"])
        cible = next(((x, y) for x, y in _anneaux(r["kiosque"]["x"], r["kiosque"]["y"],
                                                  PORTEE_D_UN_KIOSQUE)
                      if (x, y) in trottoirs and a_portee(r, x, y)
                      and (x, y) not in larges and (x, y) not in pris
                      and chantier.district_en(x, y) == district), None)
        if cible is None:
            ville["reclames"].remove(r)
            retires += 1
            continue
        chantier.occupe.discard((r["x"], r["y"]))
        r["x"], r["y"] = cible
        pris.add(cible)
        chantier.occupe.add(cible)
        deplaces += 1
    return deplaces, retires


def _ecarter_les_evenements(ville: dict, larges: set) -> dict[str, int]:
    """Ce qui apparaît en jeu et tombe devant une porte : la voie fermée du jour, la rue barrée,
    le bris d'aqueduc — écartés, `ecartee: 1` — et les nids-de-poule, qui sortent de leur liste.

    ⚠️ **On marque, on ne retire pas** : le jeu tire son événement dans ces listes par
    `hash % longueur`, et une entrée de moins reshuffle TOUS les jours (un juge de trafic qui
    prend « le premier chantier » en a trouvé un autre, planté avant un croisement). Marqués,
    les jours dont le tirage ne tombait pas sur eux gardent leur événement, et les autres
    passent au suivant (`Monde.entraveDuJour`, `Monde.brisDAqueduc`). Le tracé des autobus les
    contourne tous, marqués ou non. Les nids-de-poule sont tous actifs en même temps, sans
    tirage : ceux-là sortent de leur liste. Et le bris compte son eau (`flaque`)."""
    ecartes: dict[str, int] = {}

    def couvre(o: dict, rayon: int = 0) -> bool:
        largeur = o["l"] if isinstance(o.get("l"), int) else 1
        hauteur = o["h"] if isinstance(o.get("h"), int) else 1
        return any((x, y) in larges
                   for x in range(o["x"] - rayon, o["x"] + largeur + rayon)
                   for y in range(o["y"] - rayon, o["y"] + hauteur + rayon))

    for cle, rayon in (("entraves", 0), ("fermetures", 0), ("aqueducs", ville["aqueduc"]["flaque"])):
        ecartes[cle] = 0
        for o in ville[cle]:
            if couvre(o, rayon):
                o["ecartee"] = 1
                ecartes[cle] += 1
    avant = len(ville["nids_de_poule"])
    ville["nids_de_poule"][:] = [o for o in ville["nids_de_poule"] if not couvre(o)]
    ecartes["nids_de_poule"] = avant - len(ville["nids_de_poule"])
    return ecartes


def deplacer(chantier, ville: dict) -> dict[str, tuple[int, int] | int]:
    """Déplace ce qui bouche le devant des portes. Rend ce qui a bougé, par sorte :
    `(déplacés, retirés)` pour les objets posés, un nombre pour ce qu'on retire des listes.

    ⚠️ Dans cet ordre : les scènes d'abord (leur foule prend la place autour d'elles, que le
    décor doit ensuite leur laisser), puis les kiosques et leurs réclames, puis le décor."""
    larges, pas = devants(ville)
    comptes: dict[str, tuple[int, int] | int] = {}
    comptes["scenes"] = _deplacer_les_scenes(chantier, ville, larges, pas)
    pris = _pris(chantier, ville)
    comptes["kiosques"] = _deplacer_les_kiosques(chantier, ville, larges, pris)
    comptes["reclames"] = _deplacer_les_reclames(chantier, ville, larges, pris)
    pris = _pris(chantier, ville)
    comptes["decor"] = _deplacer_le_decor(chantier, ville, larges, pris, _evitees(chantier, ville))
    comptes.update(_ecarter_les_evenements(ville, larges))
    ville["devant"] = {"cote": DEVANT_COTE, "profondeur": DEVANT_PROFONDEUR}
    return comptes
