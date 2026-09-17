"""Ça travaille : les chantiers de la ville.

Demande de Martin (15 sept. 2026) : « des maisons ou commerces ou des rues en
construction, avec des pelles, des boules de démolition, des grues ».

⚠️ **Un chantier est une HORLOGE, pas un décor.** La partie compte les jours
depuis M3 et rien ne s'en servait pour changer la ville. Un chantier avance
d'une phase tous les trois ou quatre jours :

    0 condamné     la maison debout, les fenêtres placardées, « À DÉMOLIR »
    1 démolition   la moitié du bâtiment par terre, la grue à boule
    2 rasé         de la friche où il y avait des murs, la pelle, un tas de terre
    3 charpente    la dalle, l'échafaudage, la grue à tour
    4 neuf         un bâtiment propre sur la même empreinte, « À LOUER »

Au bout d'une vingtaine de jours, la ville n'est plus celle du premier matin.

⚠️ **Python décide, JS joue.** Ce module choisit les bâtiments et calcule, pour
chacun, les TUILES de ses cinq phases. `chantiers.js` ne fait que poser la phase
du jour — et jamais sous les yeux du joueur. Toute la géométrie se juge donc
ici, phase par phase, avant qu'une seule tuile ne bouge en jeu.

⚠️ **Les cinq pièges du plan sont tous du même genre : une ville qui change casse
ce qui comptait sur elle.** Ce module en tient trois par construction :

1. jamais un lieu qui sert — ni porte vers un intérieur, ni enseigne, ni point
   d'intérêt, ni logement qu'on visite (`libres`) ;
2. une porte démolie ne mène nulle part — on ne tire QUE des bâtiments sans
   porte vers un intérieur, et le neuf n'a qu'une porte peinte, fermée ;
3. la géométrie se rejoue à chaque phase — tout le sol que libère une démolition
   touche le reste de la ville, machines comprises (`_touche_la_ville`).

Les deux autres vivent côté jeu : le cache de morceaux ne se recuit que hors de
l'écran, et le jour de départ voyage dans la sauvegarde.
"""

from __future__ import annotations

from . import carte

#: Combien de chantiers ouverts dans une ville. Deux ou trois, dit le plan : un
#: seul serait une curiosité, dix un quartier bombardé.
NOMBRE = 3

#: Les jours que dure une phase, tirés par chantier. ⚠️ Pas moins de trois : une
#: phase qu'on ne revoit pas deux fois ne se remarque pas comme une phase.
PAS_JOURS = (3, 4)

#: ⚠️ Deux chantiers ne se voisinent pas : deux grues au même coin de rue font un
#: parc industriel, pas une ville qui travaille. En tuiles, de centre à centre.
ECART_MIN = 48

#: Le gabarit d'un bâtiment qui se démolit en spectacle. ⚠️ Une maison de neuf
#: tuiles n'a pas la place d'une grue ET d'un passage autour d'elle.
TUILES_MIN = 15
LARGEUR_MIN = 4
PROFONDEUR_MIN = 3

#: Ce que devient le sol. La friche est celle des terrains vagues : c'est le sol
#: qu'on connaît déjà pour « ici il n'y a rien ». La dalle est la poussière de
#: pierre des allées, plus claire : on voit qu'on a coulé quelque chose.
GRAVATS = ";"
DALLE = "g"

#: ⚠️ Pas les cours de gang : on ne démolit pas le quartier général des Cravates
#: parce que la graine l'a voulu.
GENRES = ("maisons", "banlieue", "commerces", "industriel", "hangars")

PHASES: tuple[dict, ...] = (
    {"slug": "condamne", "nom": "Condamné", "panneau": "À DÉMOLIR"},
    {"slug": "demolition", "nom": "Démolition", "panneau": None},
    {"slug": "rase", "nom": "Terrain rasé", "panneau": None},
    {"slug": "charpente", "nom": "Dalle et grue", "panneau": None},
    {"slug": "neuf", "nom": "Bâtiment neuf", "panneau": "À LOUER"},
)
DERNIERE = len(PHASES) - 1

#: Les machines de chaque phase, dans l'ordre où elles cherchent leur place. ⚠️
#: Ce sont du DÉCOR ANIMÉ (`DECORS[...].anime`) et pas des véhicules : la refonte
#: des chars interdit d'en ajouter avant elle. Elles travaillent, elles ne
#: roulent pas.
MACHINES: dict[int, tuple[str, ...]] = {
    1: ("grue_a_boule",),
    2: ("pelleteuse", "tas_de_terre"),
    3: ("grue",),
}

#: ⚠️ LA BOULE FRAPPE POUR VRAI : la grue à boule ne se pose qu'à DEUX tuiles de
#: la moitié encore debout, sur une rangée où le mur l'attend — elle-même et la
#: rangée au-dessus, puisque la boule pend en l'air, une tuile plus haut à
#: l'écran. Plus près, sa voisine serait le mur et la règle des quatre voisines
#: la refuse ; plus loin, la boule frapperait le vide. Mesuré sur sept graines :
#: la place existe 364 fois sur 374 (bâtiment libre × côté qui tombe) — un bâtiment
#: qui ne l'a pas ne se démolit pas, et la règle est donc TOUJOURS vraie.
FRAPPE = "grue_a_boule"
PORTEE_BOULE = 2

#: Ce qui fait qu'un bâtiment SERT. Une seule de ces choses sur lui ou devant lui,
#: et on ne le démolit pas.
SERVENT = ("portes", "devantures", "points_interet", "paquets", "ambulants", "scenes",
           "reclames", "amarrages", "barrieres", "jeux_de_foire", "kiosques_de_foire")


def _cases(objet: dict) -> set[tuple[int, int]]:
    """Les tuiles qu'occupe un objet posé : une, ou une bande de `l` tuiles."""
    largeur = objet["l"] if isinstance(objet.get("l"), int) else 1
    return {(objet["x"] + i, objet["y"]) for i in range(largeur)}


def cases_qui_servent(ville: dict) -> set[tuple[int, int]]:
    """Toutes les tuiles de la ville où quelque chose SERT.

    ⚠️ Une résidence ne sert que si sa porte mène à un intérieur. Les autres ne
    sont que des façades de maison peintes — et « la maison debout » est
    justement la phase 0 d'un chantier.
    """
    sert: set[tuple[int, int]] = set()
    for cle in SERVENT:
        for objet in ville.get(cle) or []:
            if isinstance(objet.get("x"), int) and isinstance(objet.get("y"), int):
                sert |= _cases(objet)
    portes = {(p["x"], p["y"]) for p in ville.get("portes") or []}
    for residence in ville.get("residences") or []:
        cases = _cases(residence)
        if cases & portes:
            sert |= cases
    return sert


def _facades(tuiles: set[tuple[int, int]]) -> list[tuple[int, int]]:
    """La règle de `batiment_forme` : une tuile dont la voisine du sud n'est pas
    au bâtiment est une façade."""
    return sorted((x, y) for x, y in tuiles if (x, y + 1) not in tuiles)


def libres(ville: dict, batiments: list[dict]) -> list[dict]:
    """Les bâtiments qu'on peut démolir, dans un ordre qui ne dépend de rien
    d'autre que la ville (⚠️ jamais l'ordre d'un ensemble de chaînes :
    `PYTHONHASHSEED` le brasse à chaque processus)."""
    sol = ville["sol"]
    sert = cases_qui_servent(ville)
    out = []
    for batiment in batiments:
        if batiment["genre"] not in GENRES:
            continue
        tuiles = {(x, y) for x, y in batiment["tuiles"]}
        if len(tuiles) < TUILES_MIN:
            continue
        xs = [x for x, _ in tuiles]
        ys = [y for _, y in tuiles]
        if max(xs) - min(xs) + 1 < LARGEUR_MIN or max(ys) - min(ys) + 1 < PROFONDEUR_MIN:
            continue
        # ⚠️ Toujours entier dans la ville FINIE : ce qu'on a posé au début de la
        # génération a pu être rogné par un port, une fourrière, une rampe.
        if any(carte.LEGENDE.get(sol[y][x], {}).get("solide") != 1 for x, y in tuiles):
            continue
        facades = _facades(tuiles)
        sur_rue = [(x, y) for x, y in facades
                   if y + 1 < len(sol) and carte.marchable(sol[y + 1][x])]
        # Un chantier se REGARDE : sans façade sur la rue, personne ne voit le
        # panneau, et la démolition se passe derrière un mur.
        if len(sur_rue) < LARGEUR_MIN:
            continue
        devant = {(x, y + j) for x, y in facades for j in (1, 2)}
        if (tuiles | devant) & sert:
            continue
        out.append({"tuiles": sorted(tuiles), "facades": facades, "sur_rue": sur_rue,
                    "genre": batiment["genre"]})
    out.sort(key=lambda b: b["tuiles"][0])
    return out


def _boite(tuiles: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    xs = [x for x, _ in tuiles]
    ys = [y for _, y in tuiles]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


def _toit_d_origine(sol: list[str], tuiles: list[tuple[int, int]],
                    facades: list[tuple[int, int]]) -> str:
    avant = set(facades)
    comptes: dict[str, int] = {}
    for x, y in tuiles:
        if (x, y) not in avant:
            comptes[sol[y][x]] = comptes.get(sol[y][x], 0) + 1
    # ⚠️ Égalités tranchées par le glyphe, pas par l'ordre d'insertion.
    return max(sorted(comptes), key=lambda g: comptes[g]) if comptes else carte.TOITS[0]


def _touche_la_ville(sol: list[str], neuves: set[tuple[int, int]],
                     bloquees: set[tuple[int, int]], tuiles: set[tuple[int, int]]) -> bool:
    """Tout le sol neuf rejoint-il la ville ?

    ⚠️ La ville de base est d'un seul tenant (`boucher_les_poches` et son juge).
    Démolir ne fait qu'AJOUTER du sol : il suffit donc que chaque morceau de sol
    neuf touche une tuile marchable hors du bâtiment. Sans cette garde, une
    maison murée au fond d'une cour deviendrait, rasée, une poche où l'on naît
    sans pouvoir sortir. Les machines comptent comme des murs.
    """
    restantes = neuves - bloquees
    while restantes:
        depart = min(restantes)
        groupe = {depart}
        pile = [depart]
        touche = False
        while pile:
            x, y = pile.pop()
            for vx, vy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (vx, vy) in bloquees:
                    continue
                if (vx, vy) in restantes and (vx, vy) not in groupe:
                    groupe.add((vx, vy))
                    pile.append((vx, vy))
                elif (vx, vy) not in tuiles and 0 <= vy < len(sol) and 0 <= vx < len(sol[vy]) \
                        and carte.marchable(sol[vy][vx]):
                    touche = True
        if not touche:
            return False
        restantes -= groupe
    return True


def _frappe(x: int, y: int, debout: set[tuple[int, int]], sens: int) -> tuple[int, int] | None:
    """La tuile du mur que frappe une boule posée en (x, y), ou None.

    (Rien de debout ENTRE la boule et le mur : c'est la règle des quatre voisines
    qui le garantit, la tuile d'à côté est du sol.)
    """
    mur = (x + PORTEE_BOULE * sens, y)
    if mur in debout and (mur[0], y - 1) in debout:
        return mur
    return None


def _poser_machines(sol: list[str], phase: int, neuves: set[tuple[int, int]],
                    tuiles: set[tuple[int, int]], des: carte.Des,
                    debout: set[tuple[int, int]] | None = None,
                    sens: int = 1) -> list[dict] | None:
    """Une place par machine, ou None si la phase ne peut pas les porter.

    ⚠️ Une machine ne se pose que sur une tuile dont les quatre voisines sont du
    sol : une pelle dans l'embrasure d'un passage le bouche aussi sûrement
    qu'un mur. Et on rejoue `_touche_la_ville` avec elle.

    `debout` et `sens` : la moitié qui tient encore et le côté où elle est (+1 à
    l'est, -1 à l'ouest) — la grue à boule ne se pose que là d'où elle la frappe.
    """
    poses: list[dict] = []
    bloquees: set[tuple[int, int]] = set()

    def du_sol(x: int, y: int) -> bool:
        if (x, y) in bloquees:
            return False
        if (x, y) in neuves:
            return True
        return (x, y) not in tuiles and 0 <= y < len(sol) and 0 <= x < len(sol[y]) \
            and carte.marchable(sol[y][x])

    for sorte in MACHINES.get(phase, ()):
        candidates = [
            (x, y) for x, y in sorted(neuves)
            if (x, y) not in bloquees
            and all(du_sol(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            and (sorte != FRAPPE or _frappe(x, y, debout or set(), sens))
        ]
        # ⚠️ COTE RUE d'abord : une pelle qui travaille au fond du terrain, derriere
        # la moitie encore debout, personne ne la voit passer. On tire parmi les
        # trois places les plus au sud, puis on recule si aucune ne tient.
        candidates.sort(key=lambda t: (-t[1], t[0]))
        place = None
        while candidates:
            essai = candidates.pop(des.entier(0, min(2, len(candidates) - 1)))
            if _touche_la_ville(sol, neuves, bloquees | {essai}, tuiles):
                place = essai
                break
        if place is None:
            return None
        bloquees.add(place)
        pose = {"type": sorte, "x": place[0], "y": place[1]}
        if sorte == FRAPPE:
            mur = _frappe(place[0], place[1], debout or set(), sens)
            pose["sens"] = sens
            pose["frappe"] = [mur[0], mur[1]]
        poses.append(pose)
    return poses


def _phases(sol: list[str], libre: dict, des: carte.Des) -> list[dict] | None:
    """Les cinq phases d'un bâtiment, ou None s'il ne tient pas l'une d'elles."""
    tuiles = set(libre["tuiles"])
    x0, y0, largeur, hauteur = _boite(libre["tuiles"])
    base = [sol[y0 + j][x0:x0 + largeur] for j in range(hauteur)]
    facades = libre["facades"]

    def rangees(remplace: dict[tuple[int, int], str]) -> list[str]:
        return ["".join(remplace.get((x0 + i, y0 + j), base[j][i]) for i in range(largeur))
                for j in range(hauteur)]

    def patche(remplace: dict[tuple[int, int], str]) -> list[str]:
        lignes = list(sol)
        for j, rangee in enumerate(rangees(remplace)):
            ligne = lignes[y0 + j]
            lignes[y0 + j] = ligne[:x0] + rangee + ligne[x0 + largeur:]
        return lignes

    # ⚠️ La porte du neuf se peint au MILIEU de ce qui donne sur la rue : c'est
    # le même choix que `poser_porte`, pour que le neuf ait l'air d'un bâtiment
    # de la ville et pas d'un bloc tombé du ciel.
    sur_rue = libre["sur_rue"]
    bas = max(y for _, y in sur_rue)
    rangee_rue = sorted(t for t in sur_rue if t[1] == bas)
    porte = rangee_rue[len(rangee_rue) // 2]

    # ⚠️ La démolition coupe en DEUX DANS LA LARGEUR : chaque colonne reste
    # entière d'un côté ou de l'autre, donc la moitié debout garde exactement
    # ses façades. Coupée dans la profondeur, on verrait le dos d'un toit.
    milieu = x0 + largeur // 2
    est = des.chance(0.5)
    tombees = {(x, y) for x, y in tuiles if (x >= milieu) == est}
    debout = tuiles - tombees
    # Le côté de la moitié debout, vu de celle qui tombe : c'est là que frappe la boule.
    sens = -1 if est else 1

    toit = _toit_d_origine(sol, libre["tuiles"], facades)
    # ⚠️ Le neuf a le toit PLAT, de gravier : c'est ce qu'on coule aujourd'hui,
    # et c'est ce qui le distingue d'un coup d'oeil de la maison qu'il remplace.
    # Pas la tole — celle des hangars : un bungalow en tole a l'air d'une remise.
    neuf_toit = "O" if toit != "O" else "E"
    avant = set(facades)
    neuf: dict[tuple[int, int], str] = {}
    for x, y in tuiles:
        if (x, y) not in avant:
            neuf[(x, y)] = neuf_toit
        else:
            coin = (x - 1, y) not in tuiles or (x + 1, y) not in tuiles
            # Une fenêtre sur deux, jamais au coin : un immeuble neuf est RÉGULIER,
            # c'est ce qui le distingue de ce qu'il remplace.
            neuf[(x, y)] = "W" if (not coin and (x - x0) % 2 == 1) else "F"
    # La porte peinte se pose sur un MUR : peinte sur une vitrine, on verrait la
    # vitre a travers le battant.
    neuf[porte] = "F"

    remplacements = (
        {},
        {t: GRAVATS for t in tombees},
        {t: GRAVATS for t in tuiles},
        {t: DALLE for t in tuiles},
        neuf,
    )
    phases = []
    for numero, remplace in enumerate(remplacements):
        neuves = set(remplace) if numero in MACHINES else set()
        lignes = patche(remplace)
        if neuves and not _touche_la_ville(lignes, neuves, set(), tuiles):
            return None
        machines = _poser_machines(lignes, numero, neuves, tuiles, des, debout, sens) if neuves else []
        if machines is None:
            return None
        phases.append({
            "sol": rangees(remplace),
            "machines": machines,
            "panneau": PHASES[numero]["panneau"],
            "porte": [porte[0], porte[1]] if numero == DERNIERE else None,
        })
    return phases


def tirer(ville: dict, batiments: list[dict], graine: int) -> list[dict]:
    """Les chantiers de la ville, prêts pour le paquet.

    ⚠️ Son PROPRE dé, tiré APRÈS toute la ville : un chantier ne déplace ni un
    arbre, ni un paquet, ni une enseigne. La ville avec et sans chantiers est la
    même au premier matin — un juge le tient.
    """
    des = carte.Des(graine ^ 0xC4A471E)
    sol = ville["sol"]
    candidats = libres(ville, batiments)
    choisis: list[dict] = []
    centres: list[tuple[float, float]] = []
    while candidats and len(choisis) < NOMBRE:
        libre = candidats.pop(des.entier(0, len(candidats) - 1))
        x0, y0, largeur, hauteur = _boite(libre["tuiles"])
        centre = (x0 + largeur / 2, y0 + hauteur / 2)
        if any(max(abs(centre[0] - cx), abs(centre[1] - cy)) < ECART_MIN for cx, cy in centres):
            continue
        phases = _phases(sol, libre, des)
        if phases is None:
            continue
        numero = len(choisis)
        siennes = set(libre["tuiles"])
        masque = ["".join("X" if (x0 + i, y0 + j) in siennes else "."
                          for i in range(largeur)) for j in range(hauteur)]
        choisis.append({
            "id": numero,
            "x": x0, "y": y0, "l": largeur, "h": hauteur,
            "genre": libre["genre"],
            "masque": masque,
            # ⚠️ Chacun commence à une phase différente : au premier matin, la
            # ville montre déjà une maison condamnée, une démolition et un
            # terrain rasé. Sans ce décalage, il faudrait trois jours de jeu
            # avant de voir la moindre machine.
            "decalage": numero % len(PHASES),
            "pas": PAS_JOURS[des.entier(0, len(PAS_JOURS) - 1)],
            "phases": phases,
        })
        centres.append(centre)
    return choisis


def phase_du_jour(chantier: dict, jour: int, debut: int) -> int:
    """La phase qu'un chantier doit montrer ce jour-là.

    ⚠️ Elle ne dépend que du jour et du jour de départ de la partie : deux
    appareils qui chargent la même sauvegarde voient la même ville.
    """
    ecoules = max(0, jour - debut)
    return min(DERNIERE, chantier["decalage"] + ecoules // chantier["pas"])


def appliquer(sol: list[str], chantier: dict, phase: int) -> list[str]:
    """La ville avec ce chantier à cette phase — ce que `chantiers.js` pose."""
    rangees = chantier["phases"][phase]["sol"]
    lignes = list(sol)
    x0, y0 = chantier["x"], chantier["y"]
    for j, rangee in enumerate(rangees):
        ligne = lignes[y0 + j]
        lignes[y0 + j] = ligne[:x0] + rangee + ligne[x0 + len(rangee):]
    return lignes


def tuiles(chantier: dict) -> list[tuple[int, int]]:
    """Les tuiles du bâtiment, relues dans son masque."""
    return [(chantier["x"] + i, chantier["y"] + j)
            for j, rangee in enumerate(chantier["masque"])
            for i, case in enumerate(rangee) if case == "X"]
