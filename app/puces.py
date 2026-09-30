"""Le marché aux puces du dimanche (P4, docs/jalons/le-marche-aux-puces-du-dimanche.md).

Le dimanche, de l'aube à midi, deux étals se montent sur le terrain vague le plus proche de la planque : **Ti-Rhéal**
vend les cartes de hockey de la Ligue (quatre numéros par semaine, plus cher que ce qu'une carte paie par terre) et
**Gisèle** les meubles qui portent `ou: puces` (moins cher qu'au catalogue Beausoleil, livrés le lendemain). On y
marchande : offrir moins, et le marchand accepte ou refuse selon son humeur — calculée, comme le reste.

⚠️ **RIEN AU DÉ, RIEN DANS LA VILLE** : le terrain se choisit par une règle sur la ville finie (après les cartes, les
bebelles et les sauts), les étals se PEIGNENT (aucune entité, aucun passant de plus : rien ne s'empile), et ce qui se
vend cette semaine-là est une fonction de la semaine (`Puces.stock`, dans le navigateur) — le même dimanche, le même
étal pour tout le monde. Tout voyage sur `/api/collections`.

⚠️ **UN DIMANCHE** : le jour de partie divisible par sept (le jour 7, le 14…) ; « la semaine » est `(jour - 1) // 7`.
"""

from __future__ import annotations

from . import frenesies

#: Les étals, de gauche à droite. `marchand` : qui tient l'étal (son nom, ses couleurs, ce qu'il dit en ouvrant — le
#: ton de docs/ecrire-drole.md : le marchand se vante, et c'est lui qui a tort). `vend` : `cartes` ou `meubles`.
ETALS: tuple[dict, ...] = (
    {"slug": "cartes", "nom": "LES CARTES DE TI-RHÉAL", "vend": "cartes", "nappe": "#2a4a9a",
     "marchand": {"nom": "TI-RHÉAL", "chandail": "#b02a22", "peau": "#e0b08a", "cheveux": "#d8d8d8",
                  "dit": ["J’AI TOUTE LA LIGUE. PRESQUE. DES FOIS.",
                          "LA TOQUE, JE L’AI CONNU. IL M’A PAS CONNU.",
                          "C’EST PAS CHER, C’EST DE LA NOSTALGIE."]}},
    {"slug": "meubles", "nom": "LES MEUBLES DE GISÈLE", "vend": "meubles", "nappe": "#7a4a2a",
     "marchand": {"nom": "GISÈLE", "chandail": "#5e8a3a", "peau": "#f0c8a0", "cheveux": "#8a4a2a",
                  "dit": ["TOUT A APPARTENU À UN CURÉ. TOUT.",
                          "LE SOFA A UNE TACHE. ELLE EST À CARREAUX.",
                          "JE LIVRE DEMAIN. LE BEAU-FRÈRE A UN PICK-UP."]}},
)

#: Ce qui se vend, et comment. `ouvre_h`/`ferme_h` : l'aube à midi. `cartes_par_semaine` : combien de numéros au
#: stand de Ti-Rhéal. `prix_carte` : ⚠️ plus cher que la prime d'une carte trouvée par terre (25 $) — l'acheter,
#: c'est payer pour ne pas chercher. `rabais_meubles` : la part du prix du catalogue qu'on paie aux puces.
#: `offre` : la part du prix qu'on offre en marchandant ; `humeur` : sous tant (sur cent), le marchand accepte.
REGLE: dict = {"ouvre_h": 6, "ferme_h": 12, "cartes_par_semaine": 4, "prix_carte": 120, "rabais_meubles": 0.6,
               "offre": 0.7, "humeur": 45}

#: Le terrain : tant de tuiles de large et de haut, tout d'herbe ou de friche, libre.
LARGEUR, HAUTEUR = 8, 4
TERRAIN = (",", ";")


def poser(ville: dict, dist: dict, loin_de: list[tuple[int, int]]) -> dict | None:
    """⚠️ Une RÈGLE, pas un tirage : le terrain vague (`LARGEUR` × `HAUTEUR` d'herbe ou de friche) le plus près de la
    planque À PIED (`dist`), rien de posé dessus ni autour (`frenesies._prises`), hors d'une cour de gang ou d'un
    chantier, à six tuiles au moins de toute trouvaille (`loin_de`) ; l'égalité en ordre de lecture. Les étals sur la
    deuxième rangée, deux tuiles chacun, deux tuiles d'allée entre eux."""
    sol = ville["sol"]
    prises = frenesies._prises(ville)
    zones = ville.get("zones") or []
    cours = [z for z in zones if z.get("gang")]
    chantiers = ville.get("chantiers") or []

    def libre(x, y):
        return (0 <= y < len(sol) and 0 <= x < len(sol[y]) and sol[y][x] in TERRAIN and (x, y) not in prises
                and not any(frenesies._dans(c, x, y) for c in cours)
                and not any(frenesies._dans(c, x, y, 2) for c in chantiers))

    for (x, y), _ in sorted(dist.items(), key=lambda t: (t[1], t[0][1], t[0][0])):
        if not all(libre(x + i, y + j) for i in range(LARGEUR) for j in range(HAUTEUR)):
            continue
        if any(x - 6 <= a < x + LARGEUR + 6 and y - 6 <= b < y + HAUTEUR + 6 for a, b in loin_de):
            continue
        etals = [{"slug": e["slug"], "x": x + 1 + i * 4, "y": y + 1} for i, e in enumerate(ETALS)]
        return {"x": x, "y": y, "l": LARGEUR, "h": HAUTEUR, "etals": etals}
    return None


def exporter(place: dict | None) -> dict:
    """Ce que `/api/collections` sert du marché : les étals (qui vend quoi), la règle, et le terrain."""
    ou = {e["slug"]: e for e in (place or {}).get("etals", [])}
    etals = [{**{k: v for k, v in e.items() if k != "marchand"}, "marchand": {**e["marchand"], "dit": list(e["marchand"]["dit"])},
              **({"x": ou[e["slug"]]["x"], "y": ou[e["slug"]]["y"]} if e["slug"] in ou else {})} for e in ETALS]
    return {"titre": "LE MARCHÉ AUX PUCES", "etals": etals, "regle": dict(REGLE),
            "terrain": {k: place[k] for k in ("x", "y", "l", "h")} if place else None}
