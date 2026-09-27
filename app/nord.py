"""La ville s'agrandit au nord : les Friches, la place du Petit-Canton, la Gare de triage
(docs/jalons/la-ville-s-agrandit-au-nord.md).

Martin (26 sept. 2026) : « au nord, on décale », « comme le Faubourg », « du terrain vague et des voies
ferrées », et l'approche A — la bande est une DEUXIÈME VILLE, bâtie par le même chantier sur sa trame et sa
graine, puis collée au-dessus de la ville d'avant, qui descend de `DECALAGE_NORD` rangées sans qu'un tirage
bouge. `poser` est appelé EN TOUT DERNIER par `carte.generer`.

⚠️ LES MÊMES COLONNES que la ville : chaque rue nord-sud de la bande tombe en face d'une rue de la ville. Et
PAS DE RUE AU SUD : la dernière rue de la trame (6 de large) est le boulevard qui bordait la ville au nord ; on
la bâtit pour que les croisements s'y ouvrent, et on ne la colle pas.
"""

from __future__ import annotations

from . import carte

DECALAGE_NORD = 110
GRAINE_NORD = 20260926
RANGEES_NORD = (11, 11, 11, 12, 11, 11, 11)
RUES_H_NORD = (6, 4, 4, 6, 4, 4, 4, 6)           # la dernière : la couture, jamais collée
assert sum(RANGEES_NORD) + sum(RUES_H_NORD[:-1]) == DECALAGE_NORD

#: `z` friche, `b` terrain à bâtir, `v` voies ferrées : trois lettres de plan que seule la bande emploie
#: (`carte.USAGE_DU_PLAN` les connaît ; la ville d'avant n'en a aucune).
#: ⚠️ LES GANGS SONT CEUX DU VOISIN DU SUD, en attendant les Mantes (étape 4) : un district sans gang existe
#: (la baie), mais personne n'y marche — on n'ouvre pas ce chemin ici.
DISTRICTS_NORD: tuple[dict, ...] = (
    {"slug": "friches", "nom": "Les Friches", "bx": 0, "by": 0,
     "gang": "chevreuils", "gang_nom": "Les Chevreuils", "brume": False,
     "pietons": 4, "vehicules": 1, "police": 0, "rythme": (0.2, 1.0, 0.5), "rares": (),
     "plan": ("z<<<<", "^<<<<", "^<<<<", "z<<<<", "^<<<<", "^<<<<", "^<<<<"),
     "standing": ("-----",) * 7},
    {"slug": "canton", "nom": "Le Petit-Canton", "bx": 5, "by": 0,
     "gang": "cravates", "gang_nom": "Les Cravates", "brume": False,
     "pietons": 2, "vehicules": 2, "police": 0, "rythme": (0.2, 1.0, 0.5), "rares": (),
     "plan": ("bbbbbbbb",) * 7,
     "standing": ("========",) * 7},
    {"slug": "gare", "nom": "La Gare de triage", "bx": 13, "by": 0,
     "gang": "boulonneux", "gang_nom": "Les Boulonneux", "brume": False,
     "pietons": 3, "vehicules": 2, "police": 0, "rythme": (0.15, 1.2, 0.6), "rares": (),
     "plan": ("v<<<<<<", "^<<<<<<", "^<<<<<<", "^<<<<<<", "^<<<<<<", "w<w<w<i", "^<^<^<^"),
     "standing": ("-------",) * 7},
)
PLAN_NORD: tuple[str, ...] = carte._assembler(DISTRICTS_NORD)
TRAME_NORD = {"colonnes": carte.COLONNES, "rangees": RANGEES_NORD, "rues_v": carte.RUES_V,
              "rues_h": RUES_H_NORD, "districts": DISTRICTS_NORD,
              "standing": carte._assembler_le_standing(DISTRICTS_NORD, PLAN_NORD)}


def district(slug: str) -> dict:
    return next(d for d in DISTRICTS_NORD if d["slug"] == slug)


# --- Les trois bâtisseurs --------------------------------------------------------------------

#: Le poste d'aiguillage : des leviers (`m`), le classeur des horaires, la chaise et le poêle.
PIECE_AIGUILLAGE = carte._piece("nord_aiguillage", "Le poste d'aiguillage", porte="commerce", plan="""
BBBWWWWBB
Bmmm   kB
B       B
B h   z B
BBBBDBBBB
""")
POSTE = {"slug": "nord_aiguillage", "nom": "Le poste d'aiguillage", "interieur": "nord_aiguillage",
         "famille": "repere", "genre": "industriel"}

#: Ce qu'on a laissé rouiller dans les Friches, en plus des déchets d'un terrain vague.
EPAVES = ("carcasse", "carcasse", "cabanon", "pneu", "baril", "caddie")


def _friche(ch, x, y, largeur, hauteur):
    """Des herbes hautes, un sentier de terre battue en croix, et dans chaque quart un terrain vague de la
    ville (`_terrain_vague` : terre sèche, clôture percée, déchets) ; entre eux, des épaves. Les dés sont ceux
    de la BANDE (`GRAINE_NORD`) : la ville d'avant n'en perd pas un."""
    ch.rect(x, y, largeur, hauteur, ",")
    mx, my = x + largeur // 2, y + hauteur // 2
    ch.rect(x, my - 1, largeur, 2, ";")                  # le sentier est-ouest
    ch.rect(mx - 1, y, 2, hauteur, ";")                  # et le nord-sud
    for qx, ql in ((x + 2, mx - x - 5), (mx + 3, x + largeur - mx - 5)):
        for qy, qh in ((y + 2, my - y - 5), (my + 3, y + hauteur - my - 5)):
            if ql > 6 and qh > 6:
                ch._terrain_vague(qx, qy, ql, qh)
    for _ in range(max(6, largeur * hauteur // 120)):
        quoi = ch.des.choix(EPAVES)
        ch.poser_decor(quoi, x + ch.des.entier(1, largeur - 2), y + ch.des.entier(1, hauteur - 2))


def _terrain_a_batir(ch, x, y, largeur, hauteur):
    """Une palissade tout autour, ouverte au sud ; du gravier dedans ; la pancarte « À BÂTIR » devant
    l'entrée. ⚠️ En attendant le Petit-Canton (étape 2), qui y posera ses bâtiments sans toucher ses rues."""
    ch.rect(x, y, largeur, hauteur, "g")
    ch.clore(x, y, largeur, hauteur, carte.BOIS, cote_ouvert="S", ouverture=2)
    ch.poser_decor("pancarte_a_batir", x + largeur // 2 + 1, y + hauteur)


def _voies_ferrees(ch, x, y, largeur, hauteur):
    """Des voies tous les trois rangs, des wagons (un toit de tôle long de six, posé sur la voie), et le poste
    d'aiguillage au coin sud-ouest, sa porte au sud."""
    for j in range(hauteur):
        ch.rect(x, y + j, largeur, 1, "," if j % 3 else "T")
    for j in range(0, hauteur, 3):
        for i in range(2 + (j * 5) % 11, largeur - 8, 17):
            ch.rect(x + i, y + j, 6, 1, "B")
    px, py = x + 2, y + hauteur - 6
    ch.rect(px - 1, py - 1, 7, 7, ",")                   # le poste a son terrain
    ch.rect(px, py, 5, 3, "O")
    facades = [(px + i, py + 3) for i in range(5)]
    for fx, fy in facades:
        ch.sol[fy][fx] = "F"
    ch.rect(px, py + 4, 5, 1, ".")
    ch.poser_porte(facades, special=POSTE)


class _ChantierNord(carte._Chantier):
    BATISSEURS = {"z": _friche, "b": _terrain_a_batir, "v": _voies_ferrees}
    A_ABORD = carte._Chantier.A_ABORD | {"b"}


def batir_la_bande() -> _ChantierNord:
    """La bande, bâtie à part : 419 × 116 (ses rangées 110 à 115 sont le boulevard de la couture)."""
    ch = _ChantierNord(PLAN_NORD, GRAINE_NORD, trame=TRAME_NORD)
    for etape in ("eaux", "rues", "croisements", "ilots", "ponts", "lampadaires", "bornes"):
        getattr(ch, etape)()
    ch.pieces["nord_aiguillage"] = PIECE_AIGUILLAGE
    # ⚠️ LES NOMS DE LA BANDE : `logement_1` existe déjà en ville.
    renomme = {k: (k if k.startswith("nord_") else "nord_" + k) for k in ch.pieces}
    ch.pieces = {renomme[k]: v for k, v in ch.pieces.items()}
    for p in ch.portes:
        p["interieur"] = renomme.get(p["interieur"], p["interieur"])
        p["lieu"] = renomme.get(p["lieu"], "nord_" + p["lieu"] if not p["lieu"].startswith("nord_") else p["lieu"])
    return ch
