"""La navette de l'Île-aux-Corneilles : Les Quais ↔ l'île, à l'heure (docs/jalons/l-ile-aux-corneilles.md,
troisième vague — « le traversier y accoste »).

⚠️ **UN DEUXIÈME BATEAU, PAS UNE TROISIÈME ESCALE.** Le traversier des Quais à La Pointe porte la fin m99 (le
capitaine Bérubé, son quai, son horaire) et une dizaine de juges : lui ajouter l'île changeait sa route et son
heure. La navette est la même coque et le même code (`static/js/traversier.js` est une fabrique), sa propre
route et son horaire DÉCALÉ d'une heure — elle quitte les Quais aux heures impaires, quand le traversier en
arrive : les deux ne partent pas ensemble.

⚠️ **LU SUR LA CARTE FINIE, SANS DÉ**, après la bande (tout est à sa place définitive). Aux Quais, les places du
traversier (`traversier._quais`) ; à l'île, qui n'a pas une rue, une place le long de sa JETÉE de planches (`Q`)
— on débarque sur le quai de l'île. Rien ne se pose et rien ne se déplace : on ne retient qu'un débarcadère
déjà libre de tout décor, et un couloir qui ne croise ni celui du traversier ni son débarcadère.
"""

from __future__ import annotations

from . import ile as ile_mod
from . import traversier as tr

#: L'horaire : celui du traversier, décalé d'une heure (`decalage_h`, lu par `Traversier.etatA`).
HORAIRE: dict = dict(tr.HORAIRE, decalage_h=1.0)


class _Baie(tr._Baie):
    """La baie vue par la navette : elle VA à l'île — sa ceinture d'eau ne lui est pas interdite (la terre, si)."""

    def __init__(self, ville: dict) -> None:
        super().__init__(ville)
        self.ile = None


def _quais_de_l_ile(baie: _Baie, ville: dict) -> list[dict]:
    """Les places d'accostage le long de la jetée de l'île : de l'eau profonde pour la coque, et au moins
    `ACCES_MIN` planches de quai (`Q`) contre le pont."""
    fiche = ville.get("ile")
    if not fiche:
        return []
    m = tr.LONGUEUR + 2
    out = []
    for y0 in range(max(1, fiche["y"] - m), min(baie.h - tr.LARGEUR, fiche["y"] + fiche["h"] + m)):
        for x0 in range(max(1, fiche["x"] - m), min(baie.l - tr.LONGUEUR, fiche["x"] + fiche["l"] + m)):
            if not baie.eau(x0, y0, x0 + tr.LONGUEUR - 1, y0 + tr.LARGEUR - 1):
                continue
            for cote in ("nord", "ouest", "est"):
                rive = [t for t in tr.acces(x0, y0, cote) if baie.carrossable(*t)]
                planches = [t for t in rive if ville["sol"][t[1]][t[0]] == "Q"]
                if len(planches) >= tr.ACCES_MIN and len(rive) == len(planches):
                    out.append({"x": x0, "y": y0, "cote": cote, "acces": [list(t) for t in rive]})
    return out


def tracer(ville: dict) -> dict | None:
    """Les deux escales de la navette et son horaire, prêts pour le paquet — ou None."""
    traversier = ville.get("traversier")
    if not traversier or not ville.get("ile"):
        return None
    baie = _Baie(ville)
    occupees = {(d["x"], d["y"]) for d in ville["decor"]}
    interdit = set().union(*(tr.debarcadere(q) for q in traversier["escales"]))
    a0, b0 = traversier["escales"]
    interdit |= {(x, y) for x0, y0, x1, y1 in tr.balayage(a0, b0)
                 for x in range(x0 - 1, x1 + 2) for y in range(y0 - 1, y1 + 2)}

    def libre(q: dict) -> bool:
        zone = tr.debarcadere(q)
        return not (zone & occupees) and not (zone & interdit)

    quais = [q for q in tr._quais(baie, ville, tr.ESCALES[0]) if libre(q)]
    ile = [q for q in _quais_de_l_ile(baie, ville) if libre(q)]
    paires = sorted((abs(b["x"] - a["x"]) + abs(b["y"] - a["y"]), a["y"], a["x"], b["y"], b["x"], i, j)
                    for i, a in enumerate(quais) for j, b in enumerate(ile))
    for *_, i, j in paires:
        a, b = quais[i], ile[j]
        couloir = tr.balayage(a, b)
        if all(baie.libre(*r) or _contre(r, a, b) for r in couloir) and not any(
                (x, y) in interdit for x0, y0, x1, y1 in couloir for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)):
            noms = {d["slug"]: d["nom"] for d in ville.get("districts", [])}
            escales = [dict(a, district=tr.ESCALES[0], nom=noms.get(tr.ESCALES[0], tr.ESCALES[0])),
                       dict(b, district=ile_mod.ILE["slug"], nom=ile_mod.ILE["nom"])]
            # ⚠️ NI LA COQUE NI L'HORAIRE : ceux du traversier (le navigateur les reprend), plus le décalage — la
            # carte était au ras de ses plafonds, et les recopier coûtait deux cents octets.
            return {"escales": escales, "decalage_h": HORAIRE["decalage_h"]}
    return None


def _contre(r: tuple[int, int, int, int], a: dict, b: dict) -> bool:
    """Un rectangle du couloir qui EST une des deux coques à quai : `libre` y refuse l'amarrage voisin (la
    chaloupe du quai de l'île), mais c'est là que la navette accoste."""
    return any((r[0], r[1]) == (q["x"], q["y"]) for q in (a, b))
