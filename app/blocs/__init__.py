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

⚠️ **Un bloc = un fichier** de ce dossier qui déclare `BLOC = {…}`, ajouté à `BLOCS`.
Comme une mission : rien d'autre à toucher.
"""

from __future__ import annotations

from .. import carte
from . import cineparc, galeries, rang

#: ⚠️ LE RANG (26 sept. 2026) : le chalet, la clairière et la cabane à sucre ne font plus qu'UN bloc, et
#: les trois passages sont au bord OUEST — la bande nord de la ville couvre l'ancien bord nord
#: (docs/jalons/la-ville-s-agrandit-au-nord.md).
BLOCS: list[dict] = [rang.BLOC, cineparc.BLOC, galeries.BLOC]

BORDS = ("nord", "sud", "est", "ouest")


def par_slug(slug: str) -> dict | None:
    return next((b for b in BLOCS if b["slug"] == slug), None)


def sol_du_bloc(bloc: dict) -> list[str]:
    """Le plan, ses décors remplacés par le sol qu'ils couvrent."""
    decors = bloc.get("decors", {})
    return ["".join(decors[g][0] if g in decors else g for g in ligne) for ligne in bloc["plan"]]


def decor_du_bloc(bloc: dict) -> list[dict]:
    decors = bloc.get("decors", {})
    return [{"type": decors[g][1], "x": x, "y": y}
            for y, ligne in enumerate(bloc["plan"]) for x, g in enumerate(ligne) if g in decors]


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
        "lampes": [dict(la) for la in bloc.get("lampes", [])], "zones": [], "points_interet": [], "intersections": [],
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
                 # L'ecran du cine-parc : son cadre, en tuiles (`Cineparc` peint la toile).
                 "ecran": dict(bloc["ecran"]) if bloc.get("ecran") else None},
    }


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
    return [{"slug": b["slug"], "nom": b["nom"], "passage": passage_en_ville(b),
             "panneau": b.get("panneau", b["nom"][:5].upper()),
             "portes": [{"x": p["x"], "y": p["y"], "nom": b.get("pieces", {})[p["interieur"]]["nom"]}
                        for p in b.get("portes", [])]} for b in BLOCS]


def erreurs(bloc: dict, ville: dict | None = None) -> list[str]:
    """Ce qui cloche dans un bloc — le juge de `tests/test_blocs.py`."""
    slug, fautes = bloc["slug"], []
    plan = bloc["plan"]
    if len({len(ligne) for ligne in plan}) != 1:
        fautes.append(f"{slug} : les lignes du plan n'ont pas toutes la même largeur")
    connus = set(carte.LEGENDE) | set(bloc.get("decors", {}))
    inconnus = {g for ligne in plan for g in ligne} - connus
    if inconnus:
        fautes.append(f"{slug} : glyphes inconnus {sorted(inconnus)}")
    for cote in ("passage", "retour"):
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
    # Le passage, dans la ville : sur son bord, et chacune de ses tuiles se marche.
    if ville is not None:
        p = passage_en_ville(bloc) if ville.get("decalage_nord") else bloc["passage"]
        for x, y in _tuiles_du_bord(p, ville["largeur"], ville["hauteur"]):
            g = ville["sol"][y][x] if 0 <= y < ville["hauteur"] and 0 <= x < ville["largeur"] else "B"
            if not marchable(g):
                fautes.append(f"{slug} : la tuile ({x}, {y}) du passage en ville ne se marche pas ({g!r})")
    return fautes


def a_pied_depuis_l_arrivee(bloc: dict) -> set[tuple[int, int]]:
    """Les tuiles qu'on rejoint à pied depuis l'arrivée du bloc (les arbres arrêtent)."""
    sol = sol_du_bloc(bloc)
    hauteur, largeur = len(sol), len(sol[0])
    arbres = {(d["x"], d["y"]) for d in decor_du_bloc(bloc) if d["type"] == "arbre"}
    a = bloc["arrivee"]
    vues, pile = {(a["x"], a["y"])}, [(a["x"], a["y"])]
    while pile:
        x, y = pile.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= nx < largeur and 0 <= ny < hauteur and (nx, ny) not in vues
                    and carte.LEGENDE.get(sol[ny][nx], {}).get("solide", 0) == 0 and (nx, ny) not in arbres):
                vues.add((nx, ny))
                pile.append((nx, ny))
    return vues


def _tuiles_du_bord(ouverture: dict, largeur: int, hauteur: int) -> list[tuple[int, int]]:
    bord, debut, n = ouverture["bord"], ouverture["de"], ouverture["l"]
    if bord == "nord":
        return [(debut + i, 0) for i in range(n)]
    if bord == "sud":
        return [(debut + i, hauteur - 1) for i in range(n)]
    if bord == "ouest":
        return [(0, debut + i) for i in range(n)]
    return [(largeur - 1, debut + i) for i in range(n)]
