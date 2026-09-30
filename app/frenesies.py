"""Les frénésies : une icône cachée, une arme, un chrono, un compte à faire (P4).

« Quatre activités que le jeu n'a pas » — la quatrième, les _rampages_ des GTA.
Martin, le 28 sept. 2026 : « la frénésie on y va ». Dans une ruelle de chaque
district dort une icône ; on marche dessus, EXPRÈS, et le chrono part : l'arme
imposée au poing (une arme du catalogue, prêtée le temps de la frénésie), tant
de membres d'une gang — ou tant de chars — avant la fin. Réussie, elle paie une
fois et ne revient plus ; ratée, elle attend qu'on revienne.

⚠️ Deux garde-fous, et ils ne sont pas négociables (la fiche) :

- **les enfants restent intouchables** — ils le sont déjà pour tout le monde
  (`Entites.blesser`), et une frénésie ne compte JAMAIS un intouchable, même si
  la règle d'en haut venait à sauter ;
- une frénésie se déclenche **exprès**, en marchant sur son icône — jamais un
  objectif qu'on reçoit au téléphone, et jamais pendant une mission ou un défi.

⚠️ Python place, le navigateur joue — comme les incendies. Ce module ne tire
AUCUN dé et ne pose rien que la ville lise : il lit la ville FINIE (après la
bande nord, dans `carte.generer`) et choisit, par une règle écrite, une ruelle
libre par district. La ville d'avant est la même à la tuile près.
"""

from __future__ import annotations

from . import carte

#: Ce que le navigateur suit. `rayon_px` : à quelle distance de l'icône on la
#: prend (on marche dessus) ; `renforts_min` : combien de membres de la gang visée
#: on garde autour du joueur pendant une frénésie de gang (ils rappliquent, hors de
#: l'écran — sinon le compte dépend de la chance d'une cour peuplée) ;
#: `renforts_cadence_s` : au plus un renfort par tant de secondes ;
#: `bonus_toutes` : la prime de plus quand la dernière tombe.
REGLE: dict = {
    "rayon_px": 12,
    "renforts_min": 4,
    "renforts_cadence_s": 1.0,
    "bonus_toutes": 500,
}

#: Une frénésie par district. `cible` : `gang` (les membres de `gang`) ou `chars`
#: (des chars détruits, n'importe lesquels — au Molotov, le seul feu qui mord la
#: tôle) ; `n` en `chrono_s` secondes, `arme` prêtée (un slug du catalogue), `prime`
#: payée une fois.
#:
#: ⚠️ Chaque prime reste AU PLUS ce que rapporte la mission médiane (juge `test_frenesies`),
#: et le bonus des huit, au plus la mieux payée : c'est du chaos, pas un métier.
FRENESIES: tuple[dict, ...] = (
    {"slug": "cravates", "district": "faubourg", "titre": "Le ménage des Cravates",
     "cible": "gang", "gang": "cravates", "arme": "pistolet", "n": 10, "chrono_s": 120, "prime": 250},
    {"slug": "chevreuils", "district": "erables", "titre": "La chasse aux Chevreuils",
     "cible": "gang", "gang": "chevreuils", "arme": "batte", "n": 8, "chrono_s": 90, "prime": 150},
    {"slug": "casse", "district": "shop", "titre": "La casse de la Shop",
     "cible": "chars", "arme": "molotov", "n": 4, "chrono_s": 120, "prime": 200},
    {"slug": "morues", "district": "quais", "titre": "La pêche aux Morues",
     "cible": "gang", "gang": "morues", "arme": "fusil", "n": 10, "chrono_s": 120, "prime": 250},
    {"slug": "skateux", "district": "pointe", "titre": "Planches cassées",
     "cible": "gang", "gang": "skateux", "arme": "couteau", "n": 8, "chrono_s": 90, "prime": 200},
    {"slug": "friches", "district": "friches", "titre": "Le nettoyage des Friches",
     "cible": "gang", "gang": "chevreuils", "arme": "mitraillette", "n": 15, "chrono_s": 120, "prime": 250},
    # ⚠️ LES MANTES (29 sept. 2026, `mantes.py`) : le Petit-Canton avait les Cravates du voisin du sud en les
    # attendant. Huit élèves de l'ÉCOLE LA MANTE, et une carabine contre leur kung-fu.
    {"slug": "canton", "district": "canton", "titre": "Kung-fu contre carabine",
     "cible": "gang", "gang": "mantes", "arme": "carabine", "n": 8, "chrono_s": 120, "prime": 250},
    # ⚠️ Pas de chars à la Gare de triage : c'est une cour de rails, sans trafic — une frénésie de
    # chars y serait impossible. Les Boulonneux, eux, descendent jusque-là.
    {"slug": "triage", "district": "gare", "titre": "Le feu au triage",
     "cible": "gang", "gang": "boulonneux", "arme": "molotov", "n": 8, "chrono_s": 120, "prime": 200},
)

#: Le sol où une icône se cache, par ordre de préférence : la RUELLE ; faute de
#: ruelle (la bande nord n'en a pas partout), la FRICHE, puis l'HERBE.
CACHETTES = ("x", ";", ",")
#: Une cachette se rejoint à pied : à ce nombre de pas au plus d'un trottoir ou d'une
#: rue, sans enjamber une clôture (une herbe au fond d'un enclos n'est pas une cachette).
PAS_JUSQU_A_LA_RUE = 24
#: Loin d'un paquet caché (en tuiles) : deux trouvailles, pas une.
LOIN_D_UN_PAQUET = 8
#: Pas collée à la cour de la gang visée (le barbelé), mais tout près.
HORS_DE_LA_COUR = 3
#: Les listes de la ville dont chaque élément tient une tuile (x, y) : une icône ne
#: se pose ni dessus, ni à côté.
POINTS = ("decor", "paquets", "scenes", "ambulants", "reclames", "points_interet", "aqueducs",
          "nids_de_poule", "amarrages", "kiosques_de_foire", "jeux_de_foire")


def _dans(r: dict, x: int, y: int, marge: int = 0) -> bool:
    return r["x"] - marge <= x < r["x"] + r["l"] + marge and r["y"] - marge <= y < r["y"] + r["h"] + marge


def _ecart(r: dict, x: int, y: int) -> int:
    """La distance de Tchebychev de (x, y) au rectangle `r` (0 dedans)."""
    dx = max(r["x"] - x, 0, x - (r["x"] + r["l"] - 1))
    dy = max(r["y"] - y, 0, y - (r["y"] + r["h"] - 1))
    return max(dx, dy)


def _prises(ville: dict) -> set[tuple[int, int]]:
    """Les tuiles qu'une icône ne prend pas : ce qui s'y tient déjà, une tuile autour, et le pas des portes."""
    out: set[tuple[int, int]] = set()
    for cle in POINTS:
        for o in ville.get(cle) or []:
            if isinstance(o, dict) and isinstance(o.get("x"), int) and isinstance(o.get("y"), int):
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        out.add((o["x"] + dx, o["y"] + dy))
    for p in ville.get("portes") or []:
        for dy in (1, 2):
            for dx in (-1, 0, 1):
                out.add((p["x"] + dx, p["y"] + dy))
    # ⚠️ LA PATINOIRE DU PARC (`patinoire.py`) et le tour de ses bandes : sa clairière était pleine d'arbres, donc
    # prise ; libérée, le marché aux puces s'y installait — sur la glace.
    r = ville.get("patinoire")
    if r:
        out |= {(x, y) for y in range(r["y"] - 1, r["y"] + r["h"] + 1) for x in range(r["x"] - 1, r["x"] + r["l"] + 1)}
    return out


def _atteignable(sol: list[str], x: int, y: int) -> bool:
    """De (x, y), un piéton rejoint-il un trottoir ou une rue en `PAS_JUSQU_A_LA_RUE` pas ?"""
    vus, bord = {(x, y)}, [(x, y)]
    for _pas in range(PAS_JUSQU_A_LA_RUE):
        suivant = []
        for (cx, cy) in bord:
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if (nx, ny) in vus or not (0 <= ny < len(sol) and 0 <= nx < len(sol[ny])):
                    continue
                g = sol[ny][nx]
                fiche = carte.LEGENDE.get(g, {})
                if fiche.get("trottoir") or fiche.get("route"):
                    return True
                if carte.marchable(g):
                    vus.add((nx, ny))
                    suivant.append((nx, ny))
        if not suivant:
            return False
        bord = suivant
    return False


def cachette(ville: dict, f: dict, prises: set[tuple[int, int]] | None = None) -> tuple[int, int] | None:
    """La tuile où dort l'icône de `f`, ou None si son district n'en a pas.

    ⚠️ Une RÈGLE, pas un tirage : parmi les ruelles libres du district (hors de toute
    cour de gang et de tout chantier, loin des paquets, à portée de pied d'une rue),
    celle qui est la plus proche de la cour de la gang visée — sans y être :
    `HORS_DE_LA_COUR` tuiles au moins —, ou, faute de cour, du centre du district.
    L'égalité se tranche en ordre de lecture. Sans ruelle, la friche, puis l'herbe.
    """
    zones = ville.get("zones") or []
    district = next((z for z in zones if z.get("slug") == f["district"] and not z.get("gang")), None)
    if not district:
        return None
    cours = [z for z in zones if z.get("gang")]
    cour = next((z for z in cours if z["gang"] == f.get("gang") and z.get("district") == f["district"]), None)
    chantiers = ville.get("chantiers") or []
    paquets = ville.get("paquets") or []
    prises = _prises(ville) if prises is None else prises
    sol = ville["sol"]
    cx, cy = district["x"] + district["l"] // 2, district["y"] + district["h"] // 2
    for glyphe in CACHETTES:
        candidates = []
        for y in range(district["y"], min(district["y"] + district["h"], len(sol))):
            ligne = sol[y]
            for x in range(district["x"], min(district["x"] + district["l"], len(ligne))):
                if ligne[x] != glyphe or (x, y) in prises:
                    continue
                if any(_dans(c, x, y) for c in cours):
                    continue
                if any(_dans(c, x, y, 2) for c in chantiers):
                    continue
                if any(max(abs(p["x"] - x), abs(p["y"] - y)) < LOIN_D_UN_PAQUET for p in paquets):
                    continue
                if cour:
                    e = _ecart(cour, x, y)
                    if e < HORS_DE_LA_COUR:
                        continue
                    candidates.append((e, y, x))
                else:
                    candidates.append((max(abs(x - cx), abs(y - cy)), y, x))
        for _cle, y, x in sorted(candidates):
            if _atteignable(sol, x, y):
                return x, y
    return None


def poser(ville: dict) -> list[dict]:
    """Les frénésies de la ville, chacune à sa cachette. ⚠️ Aucun dé, rien de posé dans
    une autre liste : la ville reste la même, et ce qui n'a pas de district (la ville
    d'avant n'a pas la bande nord) ou pas de ruelle libre ne se pose pas."""
    prises = _prises(ville)
    out: list[dict] = []
    for f in FRENESIES:
        ou = cachette(ville, f, prises)
        if ou is None:
            continue
        out.append({**f, "x": ou[0], "y": ou[1]})
        prises.update((ou[0] + dx, ou[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3))
    return out

