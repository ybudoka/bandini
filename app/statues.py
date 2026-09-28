"""Des statues dans les parcs (P4, docs/jalons/des-statues-dans-les-parcs.md).

Demande de Martin (28 sept. 2026) : « ajoute des statues dans les parcs ». Un parc de ville
(`_Chantier._parc`, les glyphes `k` et `p` du plan — pas le bois de La Pointe) a une PLACE en
son coeur : cinq tuiles sur cinq de poussière de pierre, où ses quatre allées se rejoignent.
Elle était vide. C'est là qu'une ville pose son grand homme : une statue de bronze sur son
socle de granit, un pigeon sur la tête, et une plaque qu'on lit à ACTION (`interactions.LIRE`).

⚠️ **POSÉE APRÈS TOUT, SANS UN DÉ** — la leçon de `devants.py` et de l'aéroport : un décor de
plus pendant la construction consomme le dé commun, et toute la ville après lui change de
place. Ici, `_parc` se contente de NOTER le centre de sa place (`places_de_parc`, une liste
qu'aucun tirage ne lit) ; la statue se pose sur la ville finie, dans l'ordre des parcs, et le
modèle suit cet ordre (`MODELES[i % 3]`). La ville sans statues est la même à la tuile près.

⚠️ **ET SES NUMÉROS À PART** : un décor du démarrage prend un numéro d'entité pour toujours,
et tout ce qui se tire à l'empreinte d'un numéro (un passant, la cadence de la police) glisse
avec lui (`Entites.enDehorsDeLaSuite`). Les fiches de dessin des statues portent `horsSuite` :
`Entites.creerDecor` les numérote dans la plage de la bande nord.

**ET UN BUSTE DANS LES PETITS PARCS.** Il n'y a que trois parcs de ville ; les parcs de quartier
(`_parc_de_quartier`, le lot qu'on n'a pas bâti) sont trente, mais la plupart font quatre tuiles
sur cinq. Les plus grands (`SURFACE_MIN_BUSTE`) reçoivent un notable en buste sur sa colonne, au
BORD du sentier, à mi-chemin — un sentier de parc de quartier ne fait qu'une tuile de large, et
on ne le bouche pas.

⚠️ Le coeur de la place est une tuile RÉSERVÉE (les allées s'y rejoignent, `_allee`) : aucun
arbre, aucun banc ne s'y est posé. La statue le bouche, mais la place fait cinq tuiles de
large : on la contourne à pied comme à vélo (`Vehicules.traverseeDuParc` évite le décor).
"""

from __future__ import annotations

#: Les trois grands hommes de Baie-des-Brumes, dans l'ordre où les parcs les reçoivent. Le
#: `type` est celui du décor (`DECORS` dans sprites.js) ; `plaque`, ce qu'on lit à ACTION,
#: une ligne par pression — ⚠️ une ligne tient dans le toast du HUD (`test_statues_js`).
MODELES: tuple[dict, ...] = (
    {
        "type": "statue_fondateur",
        "plaque": (
            "SAMUEL-OVIDE BRUMAIRE, FONDATEUR (1794)",
            "IL CHERCHAIT QUÉBEC.",
            "IL S’EST ARRÊTÉ ICI POUR DEMANDER SON CHEMIN.",
            "PERSONNE NE SAVAIT. IL EST RESTÉ.",
        ),
    },
    {
        "type": "statue_cavalier",
        "plaque": (
            "LE GÉNÉRAL TRUDEL-LAFLAMME ET SON CHEVAL, PRINCESSE",
            "IL N’A GAGNÉ AUCUNE BATAILLE.",
            "MAIS IL LES A TOUTES COMMENCÉES À L’HEURE.",
            "PRINCESSE, ELLE, EN A GAGNÉ DEUX.",
        ),
    },
    {
        "type": "statue_hockeyeur",
        "plaque": (
            "GILLES « LA TOQUE » BOUCHARD, 1971",
            "LE BUT EN PROLONGATION CONTRE SOREL.",
            "LE MAIRE A PAYÉ LA STATUE.",
            "LA TOQUE A PAYÉ LA TOURNÉE.",
        ),
    },
)

#: Les notables des petits parcs, en buste sur une colonne. Même règle : l'ordre des parcs.
BUSTES: tuple[dict, ...] = (
    {
        "type": "buste_mairesse",
        "plaque": (
            "ROSE-AIMÉE PARADIS, MAIRESSE (1952-1968)",
            "ELLE A FAIT ASPHALTER LA RUE.",
            "LA SIENNE.",
        ),
    },
    {
        "type": "buste_cure",
        "plaque": (
            "L’ABBÉ NAPOLÉON CÔTÉ, CURÉ DE LA PAROISSE",
            "IL A BÉNI LE PONT DE LA POINTE.",
            "ON ATTEND ENCORE LE RESTE DU PONT.",
        ),
    },
    {
        "type": "buste_inventeur",
        "plaque": (
            "OMER GAUTHIER, INVENTEUR",
            "IL A INVENTÉ LA SOUFFLEUSE À NEIGE,",
            "DEUX JOURS APRÈS L’AUTRE.",
        ),
    },
)

#: Un parc de quartier assez grand pour un buste, en tuiles : sept sur cinq. En dessous, c'est un
#: carré de gazon avec un sentier, et un monument y aurait l'air d'une pierre tombale.
SURFACE_MIN_BUSTE = 35

TYPES: tuple[str, ...] = tuple(m["type"] for m in MODELES + BUSTES)

#: Ce qui ne se pose jamais sous une statue : une tuile déjà prise par l'une de ces couches.
COUCHES_PRISES = ("decor", "paquets", "scenes", "ambulants", "reclames", "points_interet")


def poser(chantier, ville: dict) -> list[dict]:
    """Une statue au coeur de la place de chaque parc de ville ; rend celles qu'on a posées.

    ⚠️ Sur la ville finie : la tuile doit être encore de la place (`g`) et libre de toute couche
    (un meuble que `devants.py` aurait fait glisser là, un paquet). Sinon, pas de statue — on ne
    la pousse pas ailleurs : une statue à côté du centre de la place n'est plus un monument, c'est
    un meuble oublié.
    """
    prises = {(o["x"], o["y"]) for cle in COUCHES_PRISES for o in ville.get(cle) or []}
    posees = []

    def poser_une(type_: str, x: int, y: int) -> None:
        statue = {"type": type_, "x": x, "y": y}
        ville["decor"].append(statue)
        prises.add((x, y))
        posees.append(statue)

    for i, (x, y) in enumerate(chantier.places_de_parc):
        if ville["sol"][y][x] == "g" and (x, y) not in prises:
            poser_une(MODELES[i % len(MODELES)]["type"], x, y)
    grands = [s for s in chantier.sentiers_de_parc if s[2] >= SURFACE_MIN_BUSTE]
    for i, (milieu, cotes, _surface) in enumerate(grands):
        place = _bord_du_sentier(chantier, ville, milieu, cotes, prises)
        if place:
            poser_une(BUSTES[i % len(BUSTES)]["type"], *place)
    return posees


def _bord_du_sentier(chantier, ville: dict, milieu: tuple[int, int], cotes: tuple,
                     prises: set) -> tuple[int, int] | None:
    """La tuile de gazon au bord du sentier, à mi-chemin : d'un côté, de l'autre, puis un pas plus
    loin dans un sens et dans l'autre. Ni un banc, ni un arbre, ni le devant d'une porte — et rien de
    COLLÉ à lui : un buste adossé à un banc se lit comme un meuble de plus, pas comme un monument."""
    (mx, my), (dx, dy) = milieu, cotes[1]
    long_x, long_y = dy, dx                      # le sens du sentier, perpendiculaire à ses bords
    for pas in (0, 1, -1):
        for cx, cy in cotes:
            x, y = mx + long_x * pas + cx, my + long_y * pas + cy
            if not (0 <= y < len(ville["sol"]) and 0 <= x < len(ville["sol"][y])):
                continue
            if ville["sol"][y][x] != "," or (x, y) in prises or (x, y) in chantier.reserve:
                continue
            if any((x + vx, y + vy) in prises for vx, vy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            return x, y
    return None


def sans_statues(decor: list[dict]) -> list[dict]:
    """Le décor sans les statues. ⚠️ Pour les juges « ce module ne déplace rien » qui lisent ce qu'un module
    AJOUTE au bout du décor (`avec[len(sans):]`) : les statues se posent après tout le monde, donc au bout,
    et tomberaient dans la tranche d'un autre. Elles sont les mêmes des deux côtés, on les retire des deux."""
    return [d for d in decor if d["type"] not in TYPES]


def exporter() -> dict:
    """Les plaques, par type de décor, telles que le navigateur les lit (`Interactions`)."""
    return {m["type"]: list(m["plaque"]) for m in MODELES + BUSTES}
