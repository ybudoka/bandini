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
from . import clairiere

BLOCS: list[dict] = [clairiere.BLOC]

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
        "portes": [], "lampes": [], "zones": [], "points_interet": [], "intersections": [],
        "arrets": {}, "interieurs": {}, "ambulants": [],
        # Ce que le navigateur doit savoir pour en ressortir.
        "bloc": {"slug": bloc["slug"], "nom": bloc["nom"], "retour": dict(bloc["retour"]),
                 "arrivee": dict(bloc["arrivee"]),
                 # Des passants y naissent-ils ? (`Entites.peupler`) — la vague 3 dira lesquels.
                 "gens": bool(bloc.get("gens", False)),
                 "panneau": bloc.get("panneau_retour", "VILLE")},
    }


def pour_le_navigateur() -> list[dict]:
    """Ce que le paquet des définitions dit des blocs : où est leur passage en ville.
    ⚠️ Rien de leur carte : elle voyage à part, à la demande."""
    return [{"slug": b["slug"], "nom": b["nom"], "passage": dict(b["passage"]),
             "panneau": b.get("panneau", b["nom"][:5].upper())} for b in BLOCS]


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
    if not (0 <= a["x"] < largeur and 0 <= a["y"] < hauteur) or not marchable(sol[a["y"]][a["x"]]):
        fautes.append(f"{slug} : l'arrivée ne se marche pas")
    else:
        vues, pile = {(a["x"], a["y"])}, [(a["x"], a["y"])]
        while pile:
            x, y = pile.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (0 <= nx < largeur and 0 <= ny < hauteur and (nx, ny) not in vues
                        and marchable(sol[ny][nx]) and (nx, ny) not in decor):
                    vues.add((nx, ny))
                    pile.append((nx, ny))
        if not set(ouverture) <= vues:
            fautes.append(f"{slug} : de l'arrivée, on ne rejoint pas le retour à pied")
    # Le passage, dans la ville : sur son bord, et chacune de ses tuiles se marche.
    if ville is not None:
        p = bloc["passage"]
        for x, y in _tuiles_du_bord(p, ville["largeur"], ville["hauteur"]):
            g = ville["sol"][y][x] if 0 <= y < ville["hauteur"] and 0 <= x < ville["largeur"] else "B"
            if not marchable(g):
                fautes.append(f"{slug} : la tuile ({x}, {y}) du passage en ville ne se marche pas ({g!r})")
    return fautes


def _tuiles_du_bord(ouverture: dict, largeur: int, hauteur: int) -> list[tuple[int, int]]:
    bord, debut, n = ouverture["bord"], ouverture["de"], ouverture["l"]
    if bord == "nord":
        return [(debut + i, 0) for i in range(n)]
    if bord == "sud":
        return [(debut + i, hauteur - 1) for i in range(n)]
    if bord == "ouest":
        return [(0, debut + i) for i in range(n)]
    return [(largeur - 1, debut + i) for i in range(n)]
