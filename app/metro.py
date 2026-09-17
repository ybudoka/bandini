"""Le métro de Baie-des-Brumes : une ligne sous la ville, six stations, un horaire.

Demande de Martin (16 sept. 2026) : « je veux aussi un métro », puis, au choix :
**souterrain**, comme à Montréal.

⚠️ **On ne dessine pas de tunnel dans la ville.** Le métro n'a en surface que
ses ÉDICULES — une entrée vitrée et son « M » sur l'abord d'une rue. Le reste
est dessous : le QUAI et la RAME sont deux pièces du catalogue (`carte.INTERIEURS`,
`metro_quai` et `metro_rame`), partagées par toutes les stations ; ce qui change
d'une station à l'autre, c'est le nom qu'on lit en descendant et l'édicule par
où l'on remonte. `metro.js` fait passer la rame à quai, défiler le tunnel et
remonter à la bonne station.

⚠️ **La ligne est une BOUCLE, dans un seul sens** : Faubourg, Hôpital, La Shop,
La Pointe, puis sous la baie jusqu'aux Quais, Les Érables, et retour au
Faubourg. Une boucle n'a ni terminus ni quai « direction » à choisir : on monte,
et on descend à la bonne. Et c'est la seule façon d'aller à La Pointe sans
passer par le pont.

⚠️ **Un édicule n'est pas une porte de bâtiment.** Les portes de la ville sont des
tuiles de façade (« D ») avec leur vitrine, et quatre juges y tiennent. Les
édicules ont donc leur liste à eux (`ville["metro"]["stations"]`), un décor
solide dans `decor`, et rien d'autre ne bouge : ni un mur, ni une tuile de sol.

⚠️ **En tout dernier, dans son propre ordre** : après les lignes d'autobus, avant
le mobilier de rue (qui laisse ainsi de la place autour d'un édicule).
"""

from __future__ import annotations

#: La ligne, dans l'ordre de la boucle : (le lieu garanti près duquel on descend,
#: le nom de la station). ⚠️ Des lieux garantis : ils existent d'une graine à
#: l'autre, et une station doit toujours avoir où se poser.
LIGNE: dict = {
    "nom": "Ligne jaune",
    "couleur": "#f1c40f",
    "stations": (
        ("terminus", "Faubourg"),
        ("hopital", "Hôpital"),
        ("electronique", "La Shop"),
        ("phare", "La Pointe"),
        ("cantine", "Les Quais"),
        ("depanneur", "Les Érables"),
    ),
}

#: L'horaire. `images_par_tuile` : la rame file (un peu plus de cinq pixels par
#: image, trois fois l'autobus) ; `trajet_min` : même deux stations voisines sont
#: à sept secondes — un quai qu'on quitte et un autre qui arrive, il faut le
#: temps de voir le tunnel ; `arret_images` : les portes restent ouvertes cinq
#: secondes ; `rames` : combien tournent sur la boucle ; `approche_images` : le
#: temps qu'une rame met à entrer en station et à en sortir, qu'on voit au quai.
HORAIRE: dict = {
    "images_par_tuile": 3,
    "trajet_min": 420,
    "arret_images": 300,
    "rames": 3,
    "approche_images": 90,
    "tarif": 3,
}

#: Jusqu'où, autour du lieu, on cherche la place d'un édicule, en tuiles.
RAYON = 16

#: Le dessin de l'édicule selon le côté du trottoir : on y entre depuis la rue.
EDICULES = {1: "edicule", -1: "edicule_nord"}


def _place(chantier, ville: dict, lieu: dict, nus: set) -> tuple[int, int, int] | None:
    """(x, y, côté du trottoir) de l'édicule le plus proche du lieu, ou None.

    Une tuile d'abord qui longe UN trottoir au nord ou au sud, avec la chaussée
    juste derrière ; ni réservée, ni occupée, ni à côté de quoi que ce soit — et
    jamais là où elle fermerait un passage à pied (`mobilier._ne_coupe_rien`)."""
    from . import carte, mobilier

    solides = {(d["x"], d["y"]) for d in chantier.decor if d["type"] in carte.DECOR_SOLIDE}
    meilleure = None
    for y in range(max(2, lieu["y"] - RAYON), min(chantier.hauteur - 2, lieu["y"] + RAYON + 1)):
        for x in range(max(1, lieu["x"] - RAYON), min(chantier.largeur - 1, lieu["x"] + RAYON + 1)):
            if chantier.sol[y][x] != "_" or (x, y) in nus:
                continue
            cotes = [d for d in (1, -1)
                     if chantier.sol[y + d][x] == "." and ville["voie"][y + 2 * d][x] != "."]
            if len(cotes) != 1:
                continue
            if any((x + i, y + j) in chantier.reserve or (x + i, y + j) in chantier.occupe
                   for i in (-1, 0, 1) for j in (-1, 0, 1)):
                continue
            if not mobilier._ne_coupe_rien(chantier, x, y, solides):
                continue
            ecart = (abs(x - lieu["x"]) + abs(y - lieu["y"]), y, x)
            if meilleure is None or ecart < meilleure[0]:
                meilleure = (ecart, (x, y, cotes[0]))
    return meilleure[1] if meilleure else None


def trajets(stations: list[dict]) -> list[int]:
    """Les images de chaque trajet, de la station i à la suivante (la dernière
    ramène à la première) — la même règle que `Metro.horaire` relit."""
    h = HORAIRE
    sortie = []
    for i, a in enumerate(stations):
        b = stations[(i + 1) % len(stations)]
        distance = ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5
        sortie.append(max(h["trajet_min"], round(distance * h["images_par_tuile"])))
    return sortie


def creuser(chantier, ville: dict) -> dict:
    """Les stations de la ligne, prêtes pour le paquet. Pose les édicules dans
    `chantier.decor`."""
    from . import autobus

    lieux = {p["slug"]: p for p in ville["points_interet"]}
    nus = autobus.parvis(ville)
    stations = []
    for slug, nom in LIGNE["stations"]:
        place = _place(chantier, ville, lieux[slug], nus)
        if place is None:
            raise ValueError(f"métro : pas de place pour l'édicule de la station {nom}")
        x, y, cote = place
        if not chantier.poser_decor(EDICULES[cote], x, y):
            raise ValueError(f"métro : l'édicule de la station {nom} ne se pose pas")
        stations.append({"nom": nom, "x": x, "y": y})
    return {
        "nom": LIGNE["nom"],
        "couleur": LIGNE["couleur"],
        "stations": stations,
        "trajets": trajets(stations),
        "horaire": {k: HORAIRE[k] for k in ("arret_images", "rames", "approche_images", "tarif")},
    }


def sortie(ville: dict, rang: int) -> tuple[int, int]:
    """La tuile de trottoir devant l'édicule : là où l'on attend pour descendre,
    et là où l'on remonte."""
    s = ville["metro"]["stations"][rang]
    cote = 1 if ville["sol"][s["y"] + 1][s["x"]] == "." else -1
    return s["x"], s["y"] + cote
