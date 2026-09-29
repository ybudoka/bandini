"""Le bus du Petit-Canton : la ligne 4 (docs/jalons/le-quartier-chinois.md, étape 2, vague B).

Du terminus au casino du Dragon d'or, par l'arche et la rue principale, et retour. ⚠️ **TRACÉE SUR LA CARTE
FINIE, APRÈS LA BANDE, SANS UN DÉ** : les trois lignes de la ville d'avant sont tracées sur son chantier, avant
la bande (`autobus.tracer`) ; celle-ci se trace avec les MÊMES outils (le réseau des voies, la boucle, les places
d'arrêt), lus sur la ville collée. Rien des trois autres ne bouge :

- **ses arrêts NEUFS prennent les numéros SUIVANTS** (les arrêts sont numérotés par leur tuile, et le
  navigateur tire des choses à l'empreinte d'un numéro d'arrêt : on n'en renumérote aucun) ; au terminus, elle
  prend l'arrêt qui existe ;
- **ses abribus et ses bancs s'ajoutent AU BOUT du décor**, et ils sont dans la bande : le navigateur les crée
  hors de la suite des numéros d'entités (`Entites.enDehorsDeLaSuite`) ;
- **ses autobus naissent hors de la suite eux aussi** (`a_part`, lu par `Autobus`).
"""

from __future__ import annotations

from . import autobus as ab
from . import devants

#: La fiche de la ligne, au format de `autobus.LIGNES`.
LIGNE: dict = {"numero": 4, "nom": "Le Petit-Canton", "couleur": "#c0392b", "passe_par": ("terminus", "nord_casino")}


class _SurLaVille:
    """Ce qu'`autobus.arret_possible` lit d'un chantier, lu sur la ville FINIE : son sol, ce qui occupe une tuile
    (le décor, les lampes), et ce qui est réservé (le devant des portes)."""

    def __init__(self, ville: dict) -> None:
        self.sol = ville["sol"]
        self.hauteur, self.largeur = len(self.sol), len(self.sol[0])
        self.occupe = {(d["x"], d["y"]) for d in ville["decor"]} | {(lp["x"], lp["y"]) for lp in ville["lampes"]}
        self.reserve = set(devants.devants(ville)[0])


def _nommer(ville: dict, neufs: dict, servis: dict) -> None:
    """Le nom d'un arrêt neuf : le lieu qu'il sert (le casino), sinon son coin de rue DANS LA BANDE — lu dans sa
    trame (`grille_nord`), et préfixé : « 3e Rue / 10e Avenue » existe aussi dans la ville d'avant. ⚠️ Unique
    contre TOUS les noms d'arrêts, pas seulement les neufs (`test_autobus` : deux arrêts du même nom)."""
    pris = {a["nom"] for a in ville["autobus"]["arrets"]}
    for t, arret in sorted(neufs.items(), key=lambda kv: kv[1]["id"]):
        nom = servis.get(t) or "Petit-Canton, " + ab.nom_de_coin(ville["grille_nord"], arret["x"], arret["y"],
                                                                  arret["sens"])
        if nom in pris:
            nom = nom + {"<": " (ouest)", ">": " (est)", "^": " (nord)", "v": " (sud)"}[arret["sens"]]
        pris.add(nom)
        arret["nom"] = nom


def tracer(ville: dict, n: int) -> None:
    """Ajoute la ligne 4 à `ville["autobus"]` : ses arrêts neufs (dans la bande, au-dessus de la rangée `n`), son
    tracé, ses abribus et ses bancs. Ne touche à rien de ce qui existe."""
    bus = ville.get("autobus")
    lieux = {p["slug"]: p for p in ville["points_interet"]}
    if not bus or any(slug not in lieux for slug in LIGNE["passe_par"]):
        return
    reseau = ab._Reseau(ville)
    chantier = _SurLaVille(ville)
    existants = {(a["x"], a["y"]): i for i, a in enumerate(bus["arrets"])}
    possibles: dict[tuple[int, int], tuple] = {}
    for y in range(n):
        for x in range(reseau.largeur):
            if reseau.voie[y][x] in ab.PAS:
                place = ab.arret_possible(reseau, chantier, x, y)
                if place:
                    possibles[(x, y)] = place

    def pres(p: dict):
        return lambda t: abs(t[0] - p["x"]) + abs(t[1] - p["y"])

    terminus, casino = lieux["terminus"], lieux["nord_casino"]
    # Au terminus, l'arrêt qui existe ; au casino, une place neuve dans la bande.
    etapes = [sorted(existants, key=pres(terminus)), sorted(possibles, key=pres(casino))]
    desservable = {**possibles, **{t: None for t in existants}}
    construite = ab._boucle(reseau, etapes,
                            lambda b: ab._plus_long_desert(b, desservable) <= 2 * ab.ARRETS["ecart"][1])
    if construite is None:
        raise ValueError("ligne 4 : pas de tracé du terminus au casino")
    boucle, fixes, retenues = construite

    # Les arrêts le long de la boucle, comme `autobus.tracer` : un arrêt qui existe d'abord, sinon une place neuve
    # (dans la bande seulement), jamais plus loin que l'écart maximal.
    taille = len(boucle)
    mini, maxi = ab.ARRETS["ecart"]
    choisis: list[int] = []
    for rang, i in enumerate(fixes):
        choisis.append(i)
        fin = fixes[rang + 1] if rang + 1 < len(fixes) else taille + fixes[0]
        dernier = i
        while fin - dernier > maxi:
            fenetre = [k for k in range(dernier + maxi, dernier + mini - 1, -1) if fin - k >= mini]
            pris = next((k for k in fenetre if boucle[k % taille] in existants), None)
            if pris is None:
                pris = next((k for k in fenetre if boucle[k % taille] in possibles), None)
            if pris is None:
                dernier += maxi // 2
                continue
            choisis.append(pris % taille)
            dernier = pris
    neufs: dict[tuple[int, int], dict] = {}
    ordre: list[tuple[int, tuple[int, int]]] = []
    for i in sorted(set(choisis)):
        t = boucle[i]
        if t not in existants and t not in neufs:
            quai, abri = possibles[t]
            neufs[t] = {"x": t[0], "y": t[1], "sens": reseau.voie[t[1]][t[0]], "quai": list(quai),
                        "abri": list(abri), "lignes": [LIGNE["numero"]]}
        ordre.append((i, t))

    # Les numéros SUIVANTS, dans l'ordre des tuiles ; les abris et les bancs au bout du décor.
    for k, (t, arret) in enumerate(sorted(neufs.items(), key=lambda kv: (kv[0][1], kv[0][0]))):
        arret["id"] = len(bus["arrets"]) + k
        ax, ay = arret["abri"]
        ville["decor"].append({"type": ab.ABRIS[arret["sens"]], "x": ax, "y": ay})
        chantier.occupe.add((ax, ay))
        dx, dy = ab.PAS[arret["sens"]]
        for s in (-1, 1):
            bx, by = ax + dx * s, ay + dy * s
            if ab._libre_pour_l_abri(chantier, bx, by, reseau.parvis):
                ville["decor"].append({"type": ab.BANCS[arret["sens"]], "x": bx, "y": by})
                chantier.occupe.add((bx, by))
                break
    _nommer(ville, neufs, {retenues[1]: casino["nom"]} if retenues[1] in neufs else {})
    bus["arrets"].extend({"nom": a["nom"], "x": a["x"], "y": a["y"]}
                         for _t, a in sorted(neufs.items(), key=lambda kv: kv[1]["id"]))
    numero = {t: (existants[t] if t in existants else neufs[t]["id"]) for _i, t in ordre}
    bus["lignes"].append({
        "numero": LIGNE["numero"], "nom": LIGNE["nom"], "couleur": LIGNE["couleur"],
        "longueur": taille,
        "autobus": max(2, round(taille / ab.HORAIRE["tuiles_par_autobus"])),
        "trace": ab.coins(boucle),
        "arrets": [[numero[t], i] for i, t in ordre],
        # ⚠️ Ses autobus naissent HORS DE LA SUITE des numéros d'entités (`Autobus.faireNaitre`).
        "a_part": True,
    })
