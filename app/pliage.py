"""La carte pliée — la même ville, en colonnes, pour le fil (docs/jalons/charger-les-districts-autour-du-joueur.md).

⚠️ **UNE REPRÉSENTATION, PAS UNE AUTRE VILLE** (30 sept. 2026, vague 1). Le paquet de la carte touchait son
plafond (70 538 octets gzip pour 71 000), relevé onze fois en quinze jours. Presque tout son poids venait de
longues listes d'objets de même forme — 2 986 décors `{"type", "x", "y"}`, 618 lampes, 408 feux piétons —
où chaque objet répète ses clés, et où gzip voit mal que `x` monte de trois en trois. `plier` les range **en
colonnes** : une colonne par champ, les entiers en ÉCARTS au précédent, les chaînes répétées en une palette
et une lettre par objet. Le navigateur **déplie** en arrivant (`static/js/pliage.js`, dans
`Jeu.chargerDefinitions`), avant que quoi que ce soit ne lise la carte : aucun lecteur ne change, et
`deplier(plier(v)) == v`, à l'octet près une fois sérialisé (les juges le comparent).

Trois plis, reconnus à leur marque (`MARQUES` : une clé qu'aucune carte n'a jamais — `plier` le vérifie) :

- `{"~t": formes, "n": combien, "f": lettres, "c": colonnes}` — une liste d'au moins `MIN` objets. Une
  FORME est la liste triée des clés d'un objet ; `f` dit la forme de chacun (absent s'il n'y en a qu'une).
  Les colonnes suivent l'ordre des objets, chacun ne remplissant que les colonnes de sa forme ;
- `{"~p": [écarts des x, écarts des y]}` — une liste d'au moins `MIN` paires d'entiers (`[x, y]`) ;
- `{"~xy": [écarts des x, écarts des y], "v": colonne}` — un dictionnaire d'au moins `MIN` clés `"x,y"`
  (les arrêts d'autobus), dans l'ordre de ses clés.

Une COLONNE : `{"d": écarts}` (des entiers), `{"p": palette, "s": lettres}` (des chaînes répétées, une
lettre de `ALPHA` par valeur), ou `{"v": valeurs}` (le reste, plié à son tour).

⚠️ Ce qui ne gagne rien n'est pas plié : le sol et les voies restent des lignes de glyphes — gzip les tient
déjà (transposés : −1 % ; en plages : −3 % ; en écart à la rangée d'au-dessus : +7 %).
"""

from __future__ import annotations

import re
from collections.abc import Iterator

#: Les lettres d'une palette : l'ASCII imprimable de `#` à `~`, sans le guillemet ni la barre oblique inverse
#: (qu'un JSON échapperait). 90 valeurs au plus par palette.
ALPHA = "".join(chr(i) for i in range(35, 127) if chr(i) not in '\\"')
#: En dessous, plier ne rend rien : la forme et ses colonnes coûtent plus que les clés qu'elles évitent.
MIN = 8
#: Les marques des trois plis. ⚠️ Une clé `~` seule existe (l'eau, dans la légende) : c'est la marque ENTIÈRE
#: qui compte, et `plier` refuse une carte qui en porterait une.
MARQUES = frozenset({"~t", "~p", "~xy"})
_RANG = {lettre: i for i, lettre in enumerate(ALPHA)}
_XY = re.compile(r"-?\d+,-?\d+\Z")


def _entiers(valeurs: list) -> bool:
    return all(type(v) is int for v in valeurs)  # ⚠️ `type is`, pas `isinstance` : un booléen n'est pas un entier


def _ecarts(valeurs: list[int]) -> list[int]:
    return [b - a for a, b in zip([0] + valeurs, valeurs)]


def _cumuls(ecarts: list[int]) -> list[int]:
    valeurs, v = [], 0
    for e in ecarts:
        v += e
        valeurs.append(v)
    return valeurs


def _colonne(valeurs: list) -> dict:
    if _entiers(valeurs):
        return {"d": _ecarts(valeurs)}
    if all(type(v) is str for v in valeurs):
        palette = sorted(set(valeurs))
        if len(palette) <= len(ALPHA) and 2 * len(palette) < len(valeurs):
            rang = {s: i for i, s in enumerate(palette)}
            return {"p": palette, "s": "".join(ALPHA[rang[v]] for v in valeurs)}
    return {"v": [plier(v) for v in valeurs]}


def _decolonne(c: dict) -> list:
    if "d" in c:
        return _cumuls(c["d"])
    if "p" in c:
        return [c["p"][_RANG[lettre]] for lettre in c["s"]]
    return [deplier(v) for v in c["v"]]


def _table(objets: list[dict]) -> dict:
    formes: list[list[str]] = []
    rang: dict[tuple[str, ...], int] = {}
    lettres: list[str] = []
    colonnes: dict[str, list] = {}
    for o in objets:
        forme = tuple(sorted(o))
        if forme not in rang:
            rang[forme] = len(formes)
            formes.append(list(forme))
        lettres.append(ALPHA[rang[forme]])
        for cle in forme:
            colonnes.setdefault(cle, []).append(o[cle])
    table = {"~t": formes, "n": len(objets), "c": {cle: _colonne(v) for cle, v in colonnes.items()}}
    if len(formes) > 1:
        table["f"] = "".join(lettres)
    return table


def _detable(t: dict) -> list[dict]:
    colonnes: dict[str, Iterator] = {cle: iter(_decolonne(c)) for cle, c in t["c"].items()}
    formes = t["~t"]
    lettres = t.get("f") or ALPHA[0] * t["n"]
    return [{cle: next(colonnes[cle]) for cle in formes[_RANG[lettre]]} for lettre in lettres]


def plier(v):
    """La même valeur, pliée là où ça rend (voir le module). ⚠️ Rien n'est modifié en place."""
    if isinstance(v, list):
        if len(v) >= MIN and all(isinstance(o, dict) for o in v) and len({tuple(sorted(o)) for o in v}) <= len(ALPHA):
            return _table(v)
        if len(v) >= MIN and all(isinstance(p, list) and len(p) == 2 and _entiers(p) for p in v):
            return {"~p": [_ecarts([p[0] for p in v]), _ecarts([p[1] for p in v])]}
        return [plier(o) for o in v]
    if isinstance(v, dict):
        marquees = MARQUES.intersection(v)
        assert not marquees, f"une clé de la carte est la marque d'un pli : {sorted(marquees)}"
        # ⚠️ Dans l'ordre TRIÉ des clés, celui du JSON qui voyageait avant (`definitions._json` trie) : le
        # navigateur rebâtit le dictionnaire dans l'ordre des colonnes, et `Object.keys` le relit tel quel.
        cles = sorted(v)
        if len(cles) >= MIN and all(_XY.match(cle) for cle in cles):
            xs = [int(cle.split(",")[0]) for cle in cles]
            ys = [int(cle.split(",")[1]) for cle in cles]
            # ⚠️ Une clé « 01,2 » ou « -0,3 » ne se réécrirait pas pareil : on ne plie que ce qui revient identique.
            if [f"{x},{y}" for x, y in zip(xs, ys)] == cles:
                return {"~xy": [_ecarts(xs), _ecarts(ys)], "v": _colonne([v[cle] for cle in cles])}
        return {cle: plier(x) for cle, x in v.items()}
    return v


def deplier(v):
    """L'inverse de `plier` — le même travail que `Pliage.deplier` dans le navigateur."""
    if isinstance(v, list):
        return [deplier(o) for o in v]
    if isinstance(v, dict):
        if "~t" in v:
            return _detable(v)
        if "~p" in v:
            return [[x, y] for x, y in zip(_cumuls(v["~p"][0]), _cumuls(v["~p"][1]))]
        if "~xy" in v:
            cles = [f"{x},{y}" for x, y in zip(_cumuls(v["~xy"][0]), _cumuls(v["~xy"][1]))]
            return dict(zip(cles, _decolonne(v["v"])))
        return {cle: deplier(x) for cle, x in v.items()}
    return v
