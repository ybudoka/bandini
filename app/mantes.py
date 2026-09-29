"""Les Mantes : l'école rivale du Petit-Canton, et le gang de ses élèves (docs/jalons/l-ecole-rivale.md).

Martin (26 sept. 2026) : « un gang qui sait se battre », dans le Petit-Canton. Les **Mantes** sont les élèves de
l'ÉCOLE LA MANTE — la mante religieuse, un vrai style de kung-fu du Sud — qui ont mal tourné : ils se croient
dans un film, se saluent le poing dans la paume avant de te sauter dessus, et ont ouvert « une école » qui ne
donne plus de cours depuis que le vieux maître a pris sa retraite en Floride.

⚠️ **Le ton** (fiche du quartier) : le quartier est à ses habitants ; l'école est UNE adresse, et le gang, ce sont
ses élèves dévoyés — le même traitement que les Cravates au Faubourg. On rit de leur frime, jamais d'un accent ni
d'une origine.

Ce module décide ; le navigateur joue (`techniques.js`, `entites.js`) :

- **L'école** (`poser`) : la pièce d'un commerce du Petit-Canton, reprise sur la carte FINIE et sans un dé — comme
  le DOJO DION au Faubourg. La plus au NORD du quartier, loin de la rue principale et du terminus.
- **Leur territoire** : un rectangle autour de l'école (`ZONE`), ajouté au BOUT de `ville["zones"]` —
  `Monde.zoneA` garde la dernière qui contient le point, donc la plus précise.
- **Leur façon de se battre** (`COMBAT`) : les techniques du répertoire (`techniques.py`), choisies à
  l'EMPREINTE, jamais par `B.rng()`.
"""

from __future__ import annotations

from . import carte, devantures

#: Le slug de l'école : sa porte, sa pièce, son lieu et son point.
SLUG = "ecole_mante"
#: ⚠️ QUINZE CARACTÈRES AU PLUS : c'est ce qui tient dans un bandeau de quatre tuiles (`devantures.tient_en`) —
#: « ÉCOLE DE LA MANTE » n'y tenait pas.
ENSEIGNE = "ÉCOLE LA MANTE"
NOM = "École de la Mante"
#: Le plus petit kwoon : deux mannequins de bois, un sac, et de quoi faire trois pas de côté.
MESURES_MIN = (8, 5)
#: La rue principale du quartier est la rue ouest de cette colonne de la trame (`canton.COLONNE_DE_LA_RUE`) : le
#: territoire des Mantes s'arrête à son trottoir — la rue commerçante est aux gens du quartier.
#: Leur territoire, en colonnes et rangées d'îlots du Petit-Canton (relatives à son coin nord-ouest) : les deux
#: colonnes à l'ouest de la rue principale, sur les deux rangées du haut. ⚠️ Loin de la couture : le terminus
#: n'est pas dans leur zone, et une partie neuve ne voit pas un Mante de plus.
ZONE = {"colonnes": (2, 4), "rangees": (0, 2)}
#: Ce que leur territoire fait naître (comme une cour de gang, `carte._Chantier.zones`).
ZONE_PIETONS = 10

#: LEUR COMBAT. Les autres gangs cognent à la batte ou aux poings de rue ; les Mantes ont le répertoire.
#: ⚠️ Toutes les durées en images (60 par seconde), les distances en pixels.
COMBAT: dict = {
    # ⚠️ Ce qu'ils SAVENT est sur leur archétype (`pietons`, `mante.techniques`) : `Techniques.sait` le lit
    # sur chaque passant, et un Mante le porte depuis sa naissance.
    # Ils frappent DE PLUS LOIN et PLUS SOUVENT : les autres partent à 18 px, un coup toutes les 40 images.
    "portee_px": 22,
    "cadence_images": 30,
    # Sur cent coups, combien de projections quand on est collé (la prise), et combien de pieds.
    "part_projection": 30,
    "part_pieds": 45,
    # Collé à ce point, un Mante peut te saisir.
    "saisie_px": 16,
    # La prise tient ce temps avant la projection : le temps d'une roulade (ESQUIVE) ou d'une parade (SAISIR, si
    # on connaît le retournement du poignet). ⚠️ Quatre images, la saisie du joueur, et on n'avait rien vu venir.
    "saisie_images": 22,
    # LA PARADE : tu armes ton coup à portée, et un Mante sur trois te retourne le poignet — puis il se repose.
    "parade_chance": 0.34,
    "parade_repos_images": 240,
    # Le joueur projeté reste couché, sans être assommé : il se relève tout seul.
    "au_sol_images": 45,
}


#: LE DÉFI (29 sept. 2026, tranché par Martin — docs/jalons/les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md) :
#: sur LEUR territoire, un Mante qui te voit de près vient te défier même à MAINS NUES, une réplique en bulle — ils se
#: croient dans un film. Hors de leur territoire, ils font comme les autres gangs (l'arme au poing, ou un coup).
#: ⚠️ Aucun dé (`Entites.defier`) : le Mante qui provoque est le premier dont le tour de regard tombe (le même tic
#: que l'arme au poing), et sa réplique se tire à l'empreinte de son numéro et du compte des défis.
#: ⚠️ Ce qui rend ça juste, chaque garde-fou a son chiffre :
PROVOCATION: dict = {
    "gang": "mantes",
    # « De près » : cinq tuiles, et il doit te VOIR (une ligne libre). L'arme au poing se voit de six.
    "portee_px": 80,
    # On sort d'une porte (l'école, un commerce) : le temps de voir où l'on est avant qu'on vienne nous chercher.
    "sortie_images": 360,
    # Un défi à la fois, puis ce délai avant qu'un DEUXIÈME ne remette ça — compté depuis le premier. Et un Mante
    # ne défie qu'une fois dans sa vie : battu ou semé, il a eu son film.
    "delai_images": 1800,
    # LE SALUT : il s'arrête, se tourne vers toi, dit sa réplique, et ne part qu'après — le temps de lire la bulle et
    # de choisir entre la garde et les jambes.
    "salut_images": 50,
    "bulle_images": 150,
    # ⚠️ Frimeurs, pas caricatures : on rit du gars qui se prend pour un héros de film de kung-fu (et de son maître
    # parti en Floride), jamais d'un accent ni d'une origine (docs/ecrire-drole.md). Courtes : une bulle, une ligne.
    "repliques": [
        "TON KUNG-FU EST FAIBLE!",
        "ATTENDS, J’PRENDS LA POSE.",
        "PREMIÈRE LEÇON : GRATIS.",
        "T’AS PAS SALUÉ, TOÉ.",
        "UN CONTRE UN, LE GRAND.",
        "MONTRE-MOÉ TON STYLE!",
        "LE MAÎTRE EST EN FLORIDE.",
        "ICITTE, C’EST NOTRE COIN.",
    ],
}


def zone(ch, district: dict, n: int) -> dict:
    """Le territoire des Mantes, lu dans la trame de la bande (`ch`) — aucune tuile, aucun dé."""
    c0, c1 = (district["bx"] + c for c in ZONE["colonnes"])
    r0, r1 = (district["by"] + r for r in ZONE["rangees"])
    x0 = ch.xr[c0]
    x1 = ch.xr[c1]                                    # le trottoir ouest de la rue principale : exclu
    y0 = 0 if r0 == 0 else ch.yr[r0]
    y1 = ch.yr[r1]
    return {"slug": "mantes", "nom": "Les Mantes", "district": district["slug"], "x": x0, "y": y0,
            "l": x1 - x0, "h": min(y1, n) - y0, "gang": "mantes", "brume": False,
            "pietons": ZONE_PIETONS, "vehicules": 3, "police": 0, "rythme": list(district["rythme"]),
            "rares": list(district.get("rares", ()))}


def piece_d_ecole(slug: str, largeur: int, hauteur: int, porte: int) -> dict:
    """L'ÉCOLE LA MANTE aux mesures d'une part de bâtiment : un plancher de bois nu, deux mannequins de bois aux
    coins du fond, le sac, les CASIERS des élèves (qu'on fouille — sous leurs yeux : ils le voient), les
    plantes, un banc de chaises le long du mur, et les élèves qui s'y entraînent. ⚠️ Sans un dé : les mêmes
    mesures donnent la même école."""
    grille = [[" "] * largeur for _ in range(hauteur)]
    for x in range(1, largeur - 1):
        grille[0][x] = "k"
    grille[0][0], grille[0][largeur - 1] = "%", "%"
    grille[0][1], grille[0][largeur - 2] = "n", "n"
    grille[0][largeur // 2] = "@"
    casiers = [(x, 0) for x in range(largeur) if grille[0][x] == "k"]
    # Le banc des élèves, le long du mur opposé à la porte : là où l'on attend son tour de frimer.
    cote = 0 if porte > largeur / 2 else largeur - 1
    for y in range(1, hauteur - 2):
        grille[y][cote] = "h"
    # Le point : fouiller les casiers (`Missions.fouiller`). ⚠️ `garde` : les Mantes présents le voient faire et
    # te tombent dessus — on vole des élèves, dans leur école.
    points = [carte._poser_le_point(grille, "fouiller", None, porte, casiers, garde="mantes")]
    pris: set[tuple[int, int]] = set()
    eleves = [carte._quelqu_un(grille, "mante", autour, porte, pris)
              for autour in ((1, 1), (largeur - 2, 1), (largeur // 2, hauteur // 2))]
    return carte._piece(slug, ENSEIGNE, carte._plan_de(grille, porte), sol="t", points=tuple(points),
                        gens=carte._gens(*[e for e in eleves if e]))


def poser(ville: dict, ch, district: dict, n: int) -> dict | None:
    """Reprend la pièce d'un commerce du Petit-Canton et en fait l'école ; ajoute le territoire au bout des zones.
    Rend `{"porte": [x, y]}`, ou None si aucune façade ne convient (rien ne plante).

    Le choix est une MESURE : une porte de commerce du quartier (ni le casino, ni un logement), à l'ouest de la
    rue principale, à l'intérieur du territoire, assez grande, dont l'enseigne tient — la plus au nord, à égalité
    la plus à l'ouest (la plus loin de la rue principale).
    """
    z = zone(ch, district, n)
    meilleure = None
    for porte in ville["portes"]:
        if not (z["x"] <= porte["x"] < z["x"] + z["l"] and z["y"] <= porte["y"] < z["y"] + z["h"]):
            continue
        it = porte.get("interieur") or ""
        dedans = ville["interieurs"].get(it)
        if not dedans or not it.startswith("nord_") or "logement" in it or porte.get("lieu") != it:
            continue
        largeur, hauteur = dedans["largeur"] - 2, dedans["hauteur"] - 2
        if largeur < MESURES_MIN[0] or hauteur < MESURES_MIN[1]:
            continue
        devanture = next((d for d in ville["devantures"] if d["y"] == porte["y"]
                          and d["x"] <= porte["x"] < d["x"] + d["l"]), None)
        if not devanture or not devantures.tient_en(ENSEIGNE, devanture["l"]):
            continue
        cle = (porte["y"], porte["x"])
        if meilleure is None or cle < meilleure[0]:
            meilleure = (cle, porte, devanture, dedans)
    ville["zones"].append(z)
    if not meilleure:
        return None
    _, porte, devanture, dedans = meilleure
    ancienne = porte["interieur"]
    ville["interieurs"].pop(ancienne, None)
    ville["interieurs"][SLUG] = piece_d_ecole(SLUG, dedans["largeur"] - 2, dedans["hauteur"] - 2,
                                              dedans["sortie"]["x"])
    porte.update({"interieur": SLUG, "lieu": SLUG, "nom": ENSEIGNE})
    devanture["texte"] = ENSEIGNE
    devanture["genre"] = devantures.genre_index("savoir")
    ville["points_interet"].append({"type": SLUG, "slug": SLUG, "nom": NOM, "x": porte["x"], "y": porte["y"] + 1,
                                    "famille": "service"})
    return {"porte": [porte["x"], porte["y"]]}


def exporter() -> dict:
    return {**COMBAT, "provocation": PROVOCATION}
