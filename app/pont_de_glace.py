"""Le pont de glace (docs/jalons/le-pont-de-glace.md).

Au grand froid de l'hiver (`calendrier`), la baie prend entre La Pointe et l'Île-aux-Corneilles : un
chemin balisé de sapins, sur la glace, qu'on fait en char. Au dégel, la glace craque — un char arrêté
trop longtemps passe au travers.

⚠️ **ON NE GÈLE RIEN ICI.** La ville garde son eau (`test_eau`, `test_ile` : l'île ne se rejoint pas à
pied, l'eau ne se marche pas). Ce module LIT la ville finie et dit OÙ passe le chemin et QUAND il tient ;
c'est le navigateur (`static/js/pont.js`) qui rend ces tuiles praticables le temps du grand froid, comme
le traversier pose sa passerelle, et les rend à l'eau au dégel.

⚠️ **DERRIÈRE L'OPTION DE LA NEIGE** : l'hiver du jeu, c'est la neige de M12 (« NEIGE (ESSAI) ») ;
sans elle, pas de grand froid — le jeu d'avant, octet pour octet.
"""

from __future__ import annotations

#: Le grand froid : ces jours de l'année (`calendrier`, fin janvier - début février). Le dernier, la
#: glace craque à partir de `degel_h` ; un char arrêté dessus plus de `craque_s` secondes passe au travers.
FROID = {"jours": [3, 4, 5, 6], "degel_h": 12.0, "craque_s": 3.0}

#: Le chemin : `largeur` rangées de glace, et on le cherche là où, à l'est, une ROUTE attend à moins de
#: `route_a` tuiles de la rive (on y va en char). Les sapins, toutes les `sapin_tous_les` tuiles.
CHEMIN = {"largeur": 3, "route_a": 10, "sapin_tous_les": 4}

#: Ce que le Clairon écrit : la veille, et le premier matin.
CLAIRON = {
    "veille": "GRAND FROID DEMAIN : LA BAIE VA PRENDRE. ON POURRA ALLER À L'ÎLE EN CHAR.",
    "pendant": "LE PONT DE GLACE EST OUVERT : SUIVEZ LES SAPINS JUSQU'À L'ÎLE-AUX-CORNEILLES.",
}


def _route(ville: dict, legende: dict, x: int, y: int) -> bool:
    return legende.get(ville["sol"][y][x], {}).get("route", False)


def chemin(ville: dict, legende: dict) -> dict | None:
    """Les tuiles d'eau du chemin (`tuiles`, [x, y]), ses sapins (`sapins`), et ses deux bouts — ou None.

    Les `largeur` rangées d'eau entre la rive est de l'île et la terre d'en face, les plus courtes, parmi
    celles où une route attend de l'autre côté. Sans dé : deux joueurs ont le même."""
    ile = ville.get("ile")
    if not ile:
        return None
    sol, c = ville["sol"], CHEMIN
    largeur = len(sol[0])

    def traversee(y: int) -> tuple[int, int] | None:
        """(x0, x1) : les tuiles d'eau de la rangée `y`, de la rive de l'île à la terre d'en face."""
        # ⚠️ La boite de l'ile deborde sur l'eau : on recule d'abord jusqu'a sa vraie rive.
        x = ile["x"] + ile["l"] - 1
        while x > ile["x"] and sol[y][x] == "~":
            x -= 1
        while x < largeur and sol[y][x] != "~":
            x += 1
        x0 = x
        while x < largeur and sol[y][x] == "~":
            x += 1
        if x >= largeur or x == x0:
            return None
        # La terre d'en face mène à une route, à moins de `route_a` tuiles.
        if not any(_route(ville, legende, x + k, y) for k in range(c["route_a"]) if x + k < largeur):
            return None
        return (x0, x - 1)

    meilleur = None
    for y in range(ile["y"], ile["y"] + ile["h"] - c["largeur"] + 1):
        rangs = [traversee(y + k) for k in range(c["largeur"])]
        if not all(rangs):
            continue
        long = max(x1 - x0 + 1 for x0, x1 in rangs)
        if meilleur is None or long < meilleur[0]:
            meilleur = (long, y, rangs)
    if not meilleur:
        return None
    _, y0, rangs = meilleur
    tuiles = [[x, y0 + k] for k, (x0, x1) in enumerate(rangs) for x in range(x0, x1 + 1)]
    x_min, x_max = min(r[0] for r in rangs), max(r[1] for r in rangs)
    sapins = [[x, y] for x in range(x_min + 1, x_max, c["sapin_tous_les"])
              for y in (y0 - 1, y0 + c["largeur"]) if sol[y][x] == "~"]
    # Les deux bouts, sur la rangee du milieu : la terre juste avant et juste apres sa glace.
    milieu = c["largeur"] // 2
    return {"tuiles": tuiles, "sapins": sapins,
            "ouest": {"x": rangs[milieu][0] - 1, "y": y0 + milieu}, "est": {"x": rangs[milieu][1] + 1, "y": y0 + milieu}}


def pour_le_navigateur(ville: dict, legende: dict) -> dict:
    """⚠️ Le chemin voyage en RANGEES (`[y, x0, x1]`), pas en tuiles : 87 paires pesaient 1,4 Ko dans un
    paquet sans marge ; le navigateur les deplie (`Pont.tuiles`)."""
    c = chemin(ville, legende)
    if c:
        rangs: dict[int, list[int]] = {}
        for x, y in c["tuiles"]:
            r = rangs.setdefault(y, [x, x])
            r[0], r[1] = min(r[0], x), max(r[1], x)
        c = {**{k: v for k, v in c.items() if k != "tuiles"}, "rangs": [[y, a, b] for y, (a, b) in sorted(rangs.items())]}
    return {"froid": dict(FROID), "chemin": c, "clairon": dict(CLAIRON)}
