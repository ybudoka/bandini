"""Les blocs de carte : des morceaux de monde à part, derrière un fondu au noir.

Demande de Martin (25 sept. 2026) : « des blocs de cartes qu'on puisse ajouter comme des
extensions au jeu » — puis : « la carte fait un black-out et charge le nouveau morceau, et
ça continue ». Voir `docs/jalons/des-blocs-de-carte-en-extensions.md`.

⚠️ **UN BLOC N'EST PAS GREFFÉ À LA VILLE.** L'île et l'aéroport le sont (`ile.py`,
`aeroport.py`, posés en tout dernier dans `carte.generer`) ; un bloc est une CARTE À PART,
servie par `/api/carte/bloc/<slug>`, et la ville ne bouge pas d'une tuile — ni d'un octet
de `/api/carte` — quel que soit le nombre de blocs. On y passe comme on entre dans une
pièce (`Jeu.entrer`) : la ville mise de côté, la carte chargée au noir, et au retour la
ville telle qu'on l'a laissée. Mais dehors, et (vague 2) au volant.

⚠️ **Un bloc = un fichier** de ce dossier qui déclare `BLOC = {…}`, ajouté à `BLOCS` — et,
en ville, **la rue qui mène à son passage** : si aucune ne traverse jusqu'au bord, son ouverture
s'ajoute à `carte.OUVERTURES_DE_RUE`. Le juge des blocs la réclame (`sortie_sans_rue`, Martin,
30 sept. 2026 : chaque sortie de la ville a sa rue).
"""

from __future__ import annotations

#: ⚠️ **LES LIEUX DES BLOCS, AVANT TOUT IMPORT** (la villa, l'infiltration). Une mission peut nommer un
#: lieu de bloc, et `missions` bâtit ses scènes par défaut EN SE CHARGEANT — pendant que ce module-ci
#: attend `carte`, qui attend `missions`. Les noms sont donc écrits ici, avant l'import qui boucle ;
#: `erreurs` juge qu'ils sont exactement ceux de la fiche du bloc.
LIEUX_PAR_BLOC: dict[str, tuple[str, ...]] = {
    "villa": ("villa_chemin", "villa_service", "villa_bureau", "villa_terminal", "villa_voute"),
}


def lieux_des_blocs() -> dict[str, str]:
    """Chaque lieu de bloc et le bloc qui le porte — ce qu'une mission peut nommer en plus de la ville."""
    return {lieu: bloc for bloc, lieux in LIEUX_PAR_BLOC.items() for lieu in lieux}


import copy  # noqa: E402
import math  # noqa: E402

from .. import carte  # noqa: E402
from . import cineparc, galeries, rang, souterrain, villa  # noqa: E402

#: ⚠️ LE RANG (26 sept. 2026) : le chalet, la clairière et la cabane à sucre ne font plus qu'UN bloc, et
#: les trois passages sont au bord OUEST — la bande nord de la ville couvre l'ancien bord nord
#: (docs/jalons/la-ville-s-agrandit-au-nord.md).
BLOCS: list[dict] = [rang.BLOC, cineparc.BLOC, galeries.BLOC, villa.BLOC]

#: ⚠️ LES SOUS-SOLS : des blocs SANS passage en ville — on y descend par un rideau (`seuil`), pas en poussant contre
#: un bord. À part de `BLOCS`, dont les juges exigent un passage (docs/jalons/le-grand-garage-souterrain.md).
SOUS_SOLS: list[dict] = [souterrain.BLOC, souterrain.BLOC_2]

BORDS = ("nord", "sud", "est", "ouest")


def par_slug(slug: str) -> dict | None:
    return next((b for b in BLOCS + SOUS_SOLS if b["slug"] == slug), None)


#: ⚠️ LES CHEMINS D'UN BLOC (docs/jalons/une-route-en-lacets-vers-le-chalet.md) : une courbe douce
#: posée sur la grille. Ses points de passage sont en TUILES continues (le centre de la tuile (x, y)
#: est (x + 0,5, y + 0,5)) ; la courbe passe par chacun (Catmull-Rom), échantillonnée tous les
#: PAS_DU_CHEMIN_PX pixels — comme la voie de la montagne russe. Tout se calcule sans un dé : le même
#: plan à chaque import.
PAS_DU_CHEMIN_PX = 4
#: La lisière : tant de tuiles, au-delà de la chaussée, d'où l'on retire arbres et buissons.
LISIERE_TUILES = 1
#: Un virage plus serré ne se prend pas en auto (trois tuiles de rayon).
RAYON_MIN_PX = 48
#: Les décors qu'un chemin a le droit de dégager ; tout autre décor sur sa chaussée ou sa lisière est une faute.
DEGAGEABLES = ("arbre", "buisson")


def _catmull_rom(p0, p1, p2, p3, t: float) -> tuple[float, float]:
    """Un point à t ∈ [0, 1] de la courbe de Catmull-Rom entre p1 et p2 (p0, p3 : les voisins)."""
    return tuple(
        0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
               + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1))


def echantillonner(points, pas_px: float = PAS_DU_CHEMIN_PX) -> list[tuple[float, float]]:
    """Les points de passage (en tuiles) → la courbe, en PIXELS du monde, un point tous les ~`pas_px`
    (au plus `pas_px` de large : un tronçon bombé va plus vite qu'en ligne droite, la corde p1-p2 sous-
    estime sa longueur — surtout au premier et au dernier tronçon, aux bouts dupliqués — alors on RAFFINE
    tant qu'un pas dépasse la cible, plutôt que de deviner un facteur de sécurité)."""
    t_px = carte.TUILE_PX
    p = [(x * t_px, y * t_px) for x, y in points]
    p = [p[0]] + p + [p[-1]]
    fins: list[tuple[float, float]] = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        n = max(1, math.ceil(math.dist(p1, p2) / pas_px))
        while True:
            pts = [_catmull_rom(p0, p1, p2, p3, k / n) for k in range(n)]
            if max(math.dist(a, b) for a, b in zip(pts, pts[1:] + [p2])) <= pas_px:
                break
            n += 1
        fins.extend(pts)
    fins.append(p[-2])
    return fins


def _portee_px(chemin: dict) -> float:
    """Jusqu'où un chemin touche le plan : la chaussée, la lisière, puis la haie."""
    t_px = carte.TUILE_PX
    return chemin["largeur"] * t_px / 2 + (LISIERE_TUILES + chemin.get("haie", 2)) * t_px


def distances_au_chemin(chemin: dict, largeur: int, hauteur: int) -> dict[tuple[int, int], float]:
    """Chaque tuile à portée du chemin, et la distance (px) de son centre au tracé."""
    t_px, portee = carte.TUILE_PX, _portee_px(chemin)
    d: dict[tuple[int, int], float] = {}
    for px, py in echantillonner(chemin["points"]):
        for ty in range(max(0, int((py - portee) // t_px)), min(hauteur, int((py + portee) // t_px) + 1)):
            for tx in range(max(0, int((px - portee) // t_px)), min(largeur, int((px + portee) // t_px) + 1)):
                e = math.hypot((tx + 0.5) * t_px - px, (ty + 0.5) * t_px - py)
                if e <= portee and e < d.get((tx, ty), math.inf):
                    d[(tx, ty)] = e
    return d


def _dans(rectangles, x: int, y: int) -> bool:
    return any(rx <= x < rx + rl and ry <= y < ry + rh for rx, ry, rl, rh in rectangles)


def plan_du_bloc(bloc: dict) -> list[str]:
    """Le plan, ses chemins posés : la chaussée sur chaque tuile dont le centre tombe dans la largeur,
    la lisière dégagée de ses arbres et buissons, la haie du bois (dans ses zones, sur l'herbe seulement — et
    sur les buissons : un char traverse un buisson, resté au milieu de la haie il y faisait un trou).
    ⚠️ Ce que le chemin ne peut pas dégager (une corde de bois, de l'eau) reste : `erreurs` le dénonce."""
    plan = [list(ligne) for ligne in bloc["plan"]]
    if not bloc.get("chemins"):
        return ["".join(ligne) for ligne in plan]
    decors = bloc.get("decors", {})
    hauteur, largeur, t_px = len(plan), len(plan[0]), carte.TUILE_PX
    degageables = {g: sol for g, (sol, genre) in decors.items() if genre in DEGAGEABLES}
    for chemin in bloc["chemins"]:
        demi = chemin["largeur"] * t_px / 2
        lisiere = demi + LISIERE_TUILES * t_px
        for (x, y), e in distances_au_chemin(chemin, largeur, hauteur).items():
            g = plan[y][x]
            if e <= demi:
                if g in degageables or carte.LEGENDE.get(g, {}).get("terre"):
                    plan[y][x] = chemin["sol"]
            elif e <= lisiere:
                if g in degageables:
                    plan[y][x] = degageables[g]
            elif (g == "," or degageables.get(g) == ",") and _dans(chemin.get("bois", ()), x, y):
                plan[y][x] = chemin.get("arbre", "A")
    return ["".join(ligne) for ligne in plan]


def sol_du_bloc(bloc: dict) -> list[str]:
    """Le plan (chemins posés), ses décors remplacés par le sol qu'ils couvrent."""
    decors = bloc.get("decors", {})
    return ["".join(decors[g][0] if g in decors else g for g in ligne) for ligne in plan_du_bloc(bloc)]


def decor_du_bloc(bloc: dict) -> list[dict]:
    decors = bloc.get("decors", {})
    return [{"type": decors[g][1], "x": x, "y": y}
            for y, ligne in enumerate(plan_du_bloc(bloc)) for x, g in enumerate(ligne) if g in decors]


def carte_du_bloc(bloc: dict) -> dict:
    """La carte d'un bloc, au format de la ville (`carte.exporter`) — ce que
    `Monde.charger` lit. ⚠️ Vague 1 : ni voies, ni lampes, ni zones — le trafic, la police
    et la nuit du bloc viennent à la vague 3. Les listes sont VIDES, pas absentes : ce qui
    tourne à chaque image les parcourt sans rien trouver."""
    sol = sol_du_bloc(bloc)
    hauteur, largeur = len(sol), len(sol[0])
    return {
        "slug": bloc["slug"], "nom": bloc["nom"], "largeur": largeur, "hauteur": hauteur,
        "tuile_px": carte.TUILE_PX, "sol": sol, "voie": ["." * largeur] * hauteur,
        "legende": carte.LEGENDE, "decor": decor_du_bloc(bloc),
        "apparition": {"joueur": dict(bloc["arrivee"])},
        # ⚠️ Ses portes et ses pièces : on entre dans un bâtiment de bloc exactement comme en
        # ville (`Monde.entrer` lit `interieurs` dans la carte COURANTE).
        "portes": [dict(p) for p in bloc.get("portes", [])],
        "interieurs": {slug: dict(piece) for slug, piece in bloc.get("pieces", {}).items()},
        # Les glyphes peints autrement que dans la ville (le bois rond du chalet).
        "materiaux": dict(bloc.get("materiaux", {})),
        # Ses lampes, s'il en declare (le cine-parc : ses vitrines, ses lampadaires) ; aucune sinon.
        "lampes": [dict(la) for la in bloc.get("lampes", [])], "zones": [], "intersections": [],
        # ⚠️ SES LIEUX (la villa, l'infiltration) : des points d'intérêt comme ceux de la ville — une
        # mission les nomme (`lieu`, `ou`), et `Histoire.lieu` les trouve quand on est dans le bloc.
        "points_interet": points_du_bloc(bloc),
        # ⚠️ SES SERRURES : des barrières comme celles de la ville (`carte.BARRIERES`, condition
        # `objet`), que `Monde.barrieres` lit dans la carte COURANTE — une porte de la villa se ferme
        # tant que la clé n'est pas dans le sac, et elle ne se force pas.
        "barrieres": [serrure(s) for s in bloc.get("serrures", ())],
        "arrets": {}, "ambulants": [],
        # Ce que le navigateur doit savoir pour en ressortir.
        "bloc": {"slug": bloc["slug"], "nom": bloc["nom"], "retour": dict(bloc["retour"]),
                 "arrivee": dict(bloc["arrivee"]),
                 # Des passants y naissent-ils ? (`Entites.peupler`) — la vague 3 dira lesquels.
                 "gens": bool(bloc.get("gens", False)),
                 "panneau": bloc.get("panneau_retour", "VILLE"),
                 # Une planque (le chalet) : son prix, sa pièce, la place de son char.
                 "planque": dict(bloc["planque"]) if bloc.get("planque") else None,
                 # Ses cheminées (le chalet) : une pierre sur le toit, et la fumée qui en sort.
                 "cheminees": [dict(c) for c in bloc.get("cheminees", [])],
                 # ⚠️ SES CHEMINS (la route en lacets du rang) : le tracé en pixels, que `Blocs.dessinerChemins`
                 # peint en ruban lisse ; les tuiles `§` dessous portent la vitesse et la collision.
                 "chemins": [{"largeur_px": c["largeur"] * carte.TUILE_PX,
                              "points": [[round(x, 1), round(y, 1)] for x, y in echantillonner(c["points"])]}
                             for c in bloc.get("chemins", ())],
                 # L'ecran du cine-parc : son cadre, en tuiles (`Cineparc` peint la toile).
                 "ecran": dict(bloc["ecran"]) if bloc.get("ecran") else None,
                 # La fenêtre de sa cabine de projection (`Cineparc.faisceau` en part).
                 "cabine": dict(bloc["cabine"]) if bloc.get("cabine") else None,
                 # La cabane à sucre, pour vrai : la calèche, la tubulure, la table de tire et ses gens (`Cabane`).
                 "cabane": copy.deepcopy(bloc["cabane"]) if bloc.get("cabane") else None,
                 # ⚠️ L'INFILTRATION (la villa) : ses escaliers d'un étage à l'autre, les cadres où la
                 # caméra se tient, le terrain privé, ses gardes et leurs règles (`Infiltration`,
                 # `Police.garder`). Vides ailleurs.
                 "escaliers": [dict(e) for e in bloc.get("escaliers", ())],
                 "cadres": [list(c) for c in bloc.get("cadres", ())],
                 "noms_des_cadres": list(bloc.get("noms_des_cadres", ())),
                 "prive": [list(c) for c in bloc.get("prive", ())],
                 "gardes": [dict(g) for g in bloc.get("gardes", ())],
                 "regles_des_gardes": dict(bloc["regles_des_gardes"]) if bloc.get("regles_des_gardes") else None,
                 # La nuit y attend qu'on ressorte (la villa, `Monde.majHeure`).
                 "nuit_tient": bool(bloc.get("nuit_tient", False)),
                 # Sous terre (le garage souterrain) : ni pluie, ni neige, ni nuit (`Monde.aLAbri`).
                 "abrite": bool(bloc.get("abrite", False)),
                 # Ses cases et son ascenseur (`Souterrain`) ; null ailleurs.
                 "souterrain": copy.deepcopy(bloc["souterrain"]) if bloc.get("souterrain") else None,
                 # Ses rampes vers un AUTRE bloc (le −1 et le −2 du sous-sol, `Jeu.changerDeBloc`) ; vides ailleurs.
                 "rampes": copy.deepcopy(bloc.get("rampes", []))},
    }


def points_du_bloc(bloc: dict) -> list[dict]:
    """Les lieux d'un bloc, au format des points d'intérêt de la ville (`slug`, `nom`, `x`, `y`)."""
    return [{"slug": slug, "nom": lieu["nom"], "x": lieu["x"], "y": lieu["y"]} for slug, lieu in bloc.get("lieux", {}).items()]


def serrure(s: dict) -> dict:
    """Une serrure de bloc, au format d'une barrière de la ville (`carte.BARRIERES`) : une porte qui arrête
    tout le monde, pleine, qui ne se force pas, et qui se peint en porte cadenassée (`decor: serrure`)."""
    return {"slug": s["slug"], "nom": s["nom"], "x": s["x"], "y": s["y"], "l": s.get("l", 1), "h": s.get("h", 1),
            "arrete": ["pieton", "vehicule"], "condition": dict(s["condition"]), "forcer": None,
            "raison": s["raison"], "decor": "serrure", "plein": True, "existant": False}



def passage_en_ville(bloc: dict) -> dict:
    """Le passage sur la carte FINIE. ⚠️ Les blocs écrivent leur passage en coordonnées de la ville
    d'avant ; la ville a descendu de `nord.DECALAGE_NORD` rangées (docs/jalons/la-ville-s-agrandit-au-nord.md) :
    un passage de l'ouest ou de l'est descend avec elle."""
    from .. import nord
    p = dict(bloc["passage"])
    if p["bord"] in ("ouest", "est"):
        p["de"] += nord.DECALAGE_NORD
    return p


def pour_le_navigateur() -> list[dict]:
    """Ce que le paquet des définitions dit des blocs : où est leur passage en ville.
    ⚠️ Rien de leur carte : elle voyage à part, à la demande. Seulement leurs PORTES, avec le
    nom de la pièce : la triche ENDROITS CLÉS les liste (le chalet, la cabane à sucre) avant
    qu'aucune carte de bloc ne soit arrivée."""
    return [{"slug": b["slug"], "nom": b["nom"],
             "passage": passage_en_ville(b) if b.get("passage") else None,
             "panneau": b.get("panneau", b["nom"][:5].upper()),
             "portes": [{"x": p["x"], "y": p["y"], "nom": b.get("pieces", {})[p["interieur"]]["nom"]}
                        for p in b.get("portes", [])],
             # ⚠️ Les NOMS de ses lieux, seulement (la villa) : en ville, une mission qui en nomme un
             # fait viser le passage du bloc au GPS — le pixel, lui, n'existe que dans le bloc.
             **({"lieux": sorted(b["lieux"])} if b.get("lieux") else {}),
             # Une planque qui s'achète (le chalet) : la triche TOUTES LES PROPRIÉTÉS la donne sans charger le bloc.
             **({"planque": True} if b.get("planque") else {}),
             # ⚠️ Un sous-sol : le rideau devant lequel on ressort (`Blocs.retourEnVille`).
             **({"seuil": b["seuil"]} if b.get("seuil") else {})} for b in BLOCS + SOUS_SOLS]


def erreurs(bloc: dict, ville: dict | None = None) -> list[str]:
    """Ce qui cloche dans un bloc — le juge de `tests/test_blocs.py`."""
    slug, fautes = bloc["slug"], []
    if len({len(ligne) for ligne in bloc["plan"]}) != 1:
        fautes.append(f"{slug} : les lignes du plan n'ont pas toutes la même largeur")
    plan = plan_du_bloc(bloc)
    connus = set(carte.LEGENDE) | set(bloc.get("decors", {}))
    inconnus = {g for ligne in plan for g in ligne} - connus
    if inconnus:
        fautes.append(f"{slug} : glyphes inconnus {sorted(inconnus)}")
    for cote in ("passage", "retour"):
        if cote == "passage" and bloc.get("passage") is None and bloc.get("seuil"):
            continue   # un sous-sol : pas de bord en ville, un rideau
        if bloc[cote]["bord"] not in BORDS:
            fautes.append(f"{slug} : le {cote} n'est sur aucun bord ({bloc[cote]['bord']!r})")
    sol = sol_du_bloc(bloc)
    hauteur, largeur = len(sol), len(sol[0])

    def marchable(g: str) -> bool:
        return carte.LEGENDE.get(g, {}).get("solide", 0) == 0

    decor = {(d["x"], d["y"]) for d in decor_du_bloc(bloc) if d["type"] == "arbre"}
    # Le retour s'ouvre sur SON bord, et chacune de ses tuiles se marche.
    r = bloc["retour"]
    ouverture = _tuiles_du_bord(r, largeur, hauteur)
    for x, y in ouverture:
        if not (0 <= x < largeur and 0 <= y < hauteur) or not marchable(sol[y][x]) or (x, y) in decor:
            fautes.append(f"{slug} : la tuile ({x}, {y}) du retour ne se marche pas")
    # De l'arrivée, on rejoint le retour à pied.
    a = bloc["arrivee"]
    a_pied = None
    if not (0 <= a["x"] < largeur and 0 <= a["y"] < hauteur) or not marchable(sol[a["y"]][a["x"]]):
        fautes.append(f"{slug} : l'arrivée ne se marche pas")
    else:
        a_pied = a_pied_depuis_l_arrivee(bloc)
        if not set(ouverture) <= a_pied:
            fautes.append(f"{slug} : de l'arrivée, on ne rejoint pas le retour à pied")
    # Ses portes : sur une porte dessinée, vers une pièce qu'il déclare, et on les atteint à
    # pied depuis l'arrivée (le pas devant la porte).
    for porte in bloc.get("portes", []):
        x, y = porte["x"], porte["y"]
        if not (0 <= x < largeur and 0 <= y < hauteur) or plan[y][x] != "D":
            fautes.append(f"{slug} : la porte ({x}, {y}) n'est pas sur un « D » du plan")
        if porte.get("interieur") not in bloc.get("pieces", {}):
            fautes.append(f"{slug} : la porte ({x}, {y}) mène à une pièce inconnue {porte.get('interieur')!r}")
        elif a_pied is not None and (x, y + 1) not in a_pied:
            fautes.append(f"{slug} : on n'atteint pas la porte ({x}, {y}) à pied depuis l'arrivée")
    planque = bloc.get("planque")
    if planque:
        if planque["piece"] not in bloc.get("pieces", {}):
            fautes.append(f"{slug} : la planque dort dans une pièce inconnue {planque['piece']!r}")
        c = planque["char"]
        if a_pied is not None and (c["x"], c["y"]) not in a_pied:
            fautes.append(f"{slug} : la place du char ({c['x']}, {c['y']}) ne se rejoint pas depuis l'arrivée")
    # ⚠️ L'INFILTRATION (la villa) : chaque lieu, chaque marche d'escalier, chaque point de ronde se
    # marche et se rejoint à pied depuis l'arrivée — en prenant les escaliers, et en passant les serrures
    # (une mission donne toujours de quoi les ouvrir). Et un cadre de caméra plus petit que l'écran
    # laisserait voir l'étage d'à côté.
    if set(bloc.get("lieux", {})) != set(LIEUX_PAR_BLOC.get(slug, ())):
        fautes.append(f"{slug} : ses lieux ne sont pas ceux de `LIEUX_PAR_BLOC`")
    for nom, lieu in bloc.get("lieux", {}).items():
        if a_pied is not None and (lieu["x"], lieu["y"]) not in a_pied:
            fautes.append(f"{slug} : on ne rejoint pas le lieu {nom} ({lieu['x']}, {lieu['y']}) à pied")
    for escalier in bloc.get("escaliers", ()):
        for bout in (escalier["a"], escalier["b"]):
            for x, y in list(bout["tuiles"]) + [bout["arrivee"]]:
                if a_pied is not None and (x, y) not in a_pied:
                    fautes.append(f"{slug} : l'escalier vers {bout['nom']} ({x}, {y}) ne se rejoint pas à pied")
    for garde in bloc.get("gardes", ()):
        for point in garde["ronde"]:
            if a_pied is not None and (point[0], point[1]) not in a_pied:
                fautes.append(f"{slug} : la ronde du garde {garde['slug']} passe par ({point[0]}, {point[1]}), "
                              "qu'on ne rejoint pas")
        # ⚠️ Et entre ses points, rien ne l'arrête : depuis qu'un meuble arrête un garde (30 sept. 2026), le
        # garde de la cave restait pris sur les deux machines que sa ronde traversait.
        for x, y in _tuiles_de_la_ronde(garde["ronde"]):
            if 0 <= y < hauteur and 0 <= x < largeur and not marchable(sol[y][x]):
                fautes.append(f"{slug} : la ronde du garde {garde['slug']} traverse ({x}, {y}) ({sol[y][x]!r})")
    if bloc.get("noms_des_cadres") and len(bloc["noms_des_cadres"]) != len(bloc.get("cadres", ())):
        fautes.append(f"{slug} : {len(bloc['noms_des_cadres'])} noms pour {len(bloc.get('cadres', ()))} cadres")
    for cx, cy, cl, ch in bloc.get("cadres", ()):
        if cl * carte.TUILE_PX < ECRAN_PX[0] or ch * carte.TUILE_PX < ECRAN_PX[1]:
            fautes.append(f"{slug} : le cadre ({cx}, {cy}, {cl}, {ch}) est plus petit que l'écran")
    # ⚠️ SES CHEMINS : la chaussée entière est du chemin (rien qu'on ne sache dégager dessus), aucun décor
    # sur la chaussée ni la lisière, et aucun virage qu'une auto ne prend pas.
    decors_poses = {(d["x"], d["y"]): d["type"] for d in decor_du_bloc(bloc)}
    for i, chemin in enumerate(bloc.get("chemins", ())):
        demi = chemin["largeur"] * carte.TUILE_PX / 2
        lisiere = demi + LISIERE_TUILES * carte.TUILE_PX
        for (x, y), e in sorted(distances_au_chemin(chemin, largeur, hauteur).items()):
            if e <= demi and sol[y][x] != chemin["sol"]:
                fautes.append(f"{slug} : le chemin {i} passe sur ({x}, {y}) {sol[y][x]!r}")
            if e <= lisiere and (x, y) in decors_poses:
                fautes.append(f"{slug} : un décor {decors_poses[(x, y)]} sur le chemin {i} en ({x}, {y})")
        pts = echantillonner(chemin["points"])
        k = 8                                                    # 32 px entre les trois points du cercle
        for a, b, c in zip(pts, pts[k:], pts[2 * k:]):
            ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
            aire2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
            if aire2 > 1e-6 and ab * bc * ca / (2 * aire2) < RAYON_MIN_PX:
                fautes.append(f"{slug} : le chemin {i} a un virage trop serré vers ({b[0]:.0f}, {b[1]:.0f}) px")
                break
    # Le passage, dans la ville : sur son bord, et chacune de ses tuiles se marche.
    if ville is not None and bloc.get("passage"):
        p = passage_en_ville(bloc) if ville.get("decalage_nord") else bloc["passage"]
        for x, y in _tuiles_du_bord(p, ville["largeur"], ville["hauteur"]):
            g = ville["sol"][y][x] if 0 <= y < ville["hauteur"] and 0 <= x < ville["largeur"] else "B"
            if not marchable(g):
                fautes.append(f"{slug} : la tuile ({x}, {y}) du passage en ville ne se marche pas ({g!r})")
        fautes.extend(sortie_sans_rue(slug, p, ville))
    return fautes


#: ⚠️ CHAQUE SORTIE DE LA VILLE A SA RUE (Martin, 30 sept. 2026 : « valide que toutes les sorties de la ville
#: aient bien une rue ou une voie qui permette de sortir — dans le futur aussi »). La villa est arrivée sans
#: la sienne : sa rue s'arrêtait sur la rue de l'ouest, et le juge, qui ne demandait qu'une tuile qui se
#: marche, laissait passer le trottoir de ceinture. Il faut maintenant, sur le bord du passage, au moins
#: LARGEUR_DE_SORTIE tuiles de chaussée côte à côte (un char y passe)…
LARGEUR_DE_SORTIE = 2
#: … et que cette chaussée rejoigne LES rues de la ville, pas un bout d'asphalte isolé : au moins cette part
#: de toute la chaussée, sans passer une rue barrée, une barrière (même celles qui s'ouvrent) ni un décor solide.
PART_DU_RESEAU = 0.5


def sortie_sans_rue(slug: str, passage: dict, ville: dict) -> list[str]:
    """Ce qui manque à la sortie de la ville d'un bloc pour qu'on la prenne au volant (voir LARGEUR_DE_SORTIE)."""
    sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
    bouchees: set[tuple[int, int]] = set()
    for r in list(ville.get("fermetures", ())) + list(ville.get("barrieres", ())):
        bouchees |= {(r["x"] + i, r["y"] + j) for i in range(r.get("l", 1)) for j in range(r.get("h", 1))}
    solides = set(ville.get("decor_solide", ()))
    bouchees |= {(d["x"], d["y"]) for d in ville.get("decor", ()) if d["type"] in solides}

    def chaussee(x: int, y: int) -> bool:
        return (0 <= x < largeur and 0 <= y < hauteur and (x, y) not in bouchees
                and bool(carte.LEGENDE.get(sol[y][x], {}).get("route")))

    bord = _tuiles_du_bord(passage, largeur, hauteur)
    suite = plus_large = 0
    for x, y in bord:
        suite = suite + 1 if chaussee(x, y) else 0
        plus_large = max(plus_large, suite)
    if plus_large < LARGEUR_DE_SORTIE:
        return [f"{slug} : la sortie de la ville n'a pas de rue — {plus_large} tuile(s) de chaussée côte à côte "
                f"sur le bord {passage['bord']} ({passage['de']} à {passage['de'] + passage['l'] - 1}), "
                f"il en faut {LARGEUR_DE_SORTIE} (`carte.OUVERTURES_DE_RUE`)"]
    vues = {(x, y) for x, y in bord if chaussee(x, y)}
    pile = list(vues)
    while pile:
        x, y = pile.pop()
        for voisine in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if voisine not in vues and chaussee(*voisine):
                vues.add(voisine)
                pile.append(voisine)
    toute = sum(chaussee(x, y) for y in range(hauteur) for x in range(largeur))
    if len(vues) < PART_DU_RESEAU * toute:
        return [f"{slug} : la rue de la sortie ne rejoint pas les rues de la ville "
                f"({len(vues)} tuiles de chaussée sur {toute})"]
    return []


#: L'écran du jeu, en pixels (`VW`, `VH` de `base.js`) : un cadre de caméra plus petit laisserait voir à côté.
ECRAN_PX = (480, 270)


def a_pied_depuis_l_arrivee(bloc: dict) -> set[tuple[int, int]]:
    """Les tuiles qu'on rejoint à pied depuis l'arrivée du bloc (les arbres arrêtent). ⚠️ Un escalier
    (la villa) mène à son autre bout : on y pose le pied, on arrive en haut."""
    sol = sol_du_bloc(bloc)
    hauteur, largeur = len(sol), len(sol[0])
    arbres = {(d["x"], d["y"]) for d in decor_du_bloc(bloc) if d["type"] == "arbre"}
    sauts: dict[tuple[int, int], tuple[int, int]] = {}
    for escalier in bloc.get("escaliers", ()):
        for depart, arrivee in ((escalier["a"], escalier["b"]), (escalier["b"], escalier["a"])):
            for x, y in depart["tuiles"]:
                sauts[(x, y)] = tuple(arrivee["arrivee"])
    a = bloc["arrivee"]
    vues, pile = {(a["x"], a["y"])}, [(a["x"], a["y"])]
    while pile:
        x, y = pile.pop()
        voisines = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        if (x, y) in sauts:
            voisines.append(sauts[(x, y)])
        for nx, ny in voisines:
            if (0 <= nx < largeur and 0 <= ny < hauteur and (nx, ny) not in vues
                    and (carte.LEGENDE.get(sol[ny][nx], {}).get("solide", 0) == 0 or (nx, ny) in sauts)
                    and (nx, ny) not in arbres):
                vues.add((nx, ny))
                pile.append((nx, ny))
    return vues


def _tuiles_de_la_ronde(ronde: list) -> list[tuple[int, int]]:
    """Les tuiles qu'un garde foule en ligne droite d'un point de sa ronde au suivant (et du dernier au premier)."""
    tuiles = []
    for k, a in enumerate(ronde):
        b = ronde[(k + 1) % len(ronde)]
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
        tuiles += [(round(a[0] + (b[0] - a[0]) * q / n), round(a[1] + (b[1] - a[1]) * q / n)) for q in range(n + 1)]
    return tuiles


def _tuiles_du_bord(ouverture: dict, largeur: int, hauteur: int) -> list[tuple[int, int]]:
    bord, debut, n = ouverture["bord"], ouverture["de"], ouverture["l"]
    if bord == "nord":
        return [(debut + i, 0) for i in range(n)]
    if bord == "sud":
        return [(debut + i, hauteur - 1) for i in range(n)]
    if bord == "ouest":
        return [(0, debut + i) for i in range(n)]
    return [(largeur - 1, debut + i) for i in range(n)]
