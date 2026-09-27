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

import copy

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
    # ⚠️ UNE FOIS : `feux_pietons` réserve ses tuiles (`occupe`) et un deuxième appel n'en rend plus
    # aucun ; or la bande est gardée pour tout le processus (`_bande`).
    ch.feux_nord = ch.feux_pietons()
    # ⚠️ LES NOMS DE LA BANDE : `logement_1` existe déjà en ville.
    renomme = {k: (k if k.startswith("nord_") else "nord_" + k) for k in ch.pieces}
    ch.pieces = {renomme[k]: v for k, v in ch.pieces.items()}
    for p in ch.portes:
        p["interieur"] = renomme.get(p["interieur"], p["interieur"])
        p["lieu"] = renomme.get(p["lieu"], "nord_" + p["lieu"] if not p["lieu"].startswith("nord_") else p["lieu"])
    return ch


# --- La translation : toute la ville descend de `DECALAGE_NORD` rangées ------------------------------
#
# ⚠️ UNE ENTRÉE PAR CLÉ DE LA CARTE, et une clé inconnue LÈVE : une autre session qui ajoute une clé à
# `carte.generer` doit dire ici comment elle descend, sinon elle resterait 110 rangées trop haut, en silence.
# Les objets `{x, y}` descendent par `_y` (à toute profondeur) ; les PAIRES `[x, y]` et les tuples ont
# chacune leur fonction, qui dit l'index du y — lu dans le module qui les produit.

PX = carte.TUILE_PX

#: ⚠️ UN OBJET NE DESCEND QU'UNE FOIS : la ville PARTAGE des objets entre ses listes (les amarrages de l'île
#: sont aussi dans `amarrages`) ; les décaler deux fois les poserait 220 rangées plus bas. `decaler` vide ce
#: registre à chaque appel, et chaque objet ou paire décalé y inscrit son `id`.
_VUS: set[int] = set()


def _une_fois(o) -> bool:
    if id(o) in _VUS:
        return False
    _VUS.add(id(o))
    return True


def _y(o, n):
    """Tout entier sous une clé `y`, à toute profondeur."""
    if isinstance(o, dict):
        if not _une_fois(o):
            return
        for k, v in o.items():
            if k == "y" and isinstance(v, int):
                o[k] = v + n
            else:
                _y(v, n)
    elif isinstance(o, list):
        for v in o:
            _y(v, n)


def _paire(p, n, i=1):
    if _une_fois(p):
        p[i] += n


def _paires(liste, n, i=1):
    for p in liste or ():
        _paire(p, n, i)


def _rien(v, n):
    pass


def _aeroport(a, n):
    _y(a, n)
    _paire(a["plan"], n)                                 # [x0, y0, largeur, hauteur]
    for s in a["axes"]:                                  # [x0, y0, x1, y1]
        if _une_fois(s):
            s[1] += n
            s[3] += n
    _paires(a["balises"], n)
    _paires(a["peints"], n, 2)                           # [type, x, y]
    _paires(a["portes_peintes"], n)                      # [x, y, sens]
    _paires(a["pont"]["piles"], n)
    a["masque"]["carte_h"] += n                          # la hauteur de la ville au-dessus de lui


def _chantiers(liste, n):
    _y(liste, n)
    for c in liste:
        if isinstance(c.get("tranchee"), list):
            _paires(c["tranchee"], n)
        for cle in ("signaleur", "conteneur"):
            if c.get(cle):
                _paire(c[cle], n)
        for ph in c["phases"]:
            _paires(ph.get("equipe"), n)
            if isinstance(ph.get("porte"), list):
                _paire(ph["porte"], n)
            for m in ph.get("machines", ()):
                if m.get("frappe"):
                    _paire(m["frappe"], n)


def _autobus(a, n):
    _y(a, n)
    for ligne in a["lignes"]:
        _paires(ligne["trace"], n)                       # `arrets` y est [id, rang] : des indices


def _eboueurs(e, n):
    _paires(e["trace"], n)
    _paires(e["points"], n, 2)                           # [rang, x, y]


def _tramway(t, n):
    _paires(t["trace"], n)
    _paires(t["arrets"], n, 2)                           # [rang, x, y, nom]


def _neige(v, n):
    _paires(v["charrue"]["trace"], n)
    for paires in v["deneigement"]["panneaux"].values():
        _paires(paires, n)


def _traversier(t, n):
    _y(t, n)
    for e in t["escales"]:
        _paires(e["acces"], n)


def _train(t, n):
    _paires(t["voie"], n)
    _paire(t["quai"], n, 2)                              # [x0, x1, y]


def _montagne_russe(m, n):
    _paires(m["voie"], n * PX)                           # [x, y, z] en PIXELS
    _paires(m["supports"], n, 2)                         # [rang, x, y]
    _y(m["zone"], n)


def _relief(r, n):
    r["montagnes"]["h"] += n                             # elles montent jusqu'en haut de la bande


def _foire_enclos(v, n):
    _paires(v, n, 0)                                     # [y, x0, x1]


def _mouillages(v, n):
    _y(v, n * PX)                                        # en PIXELS, eux aussi


DECALAGES = {
    "aeroport": _aeroport, "amarrages": _y, "ambulants": _y, "apparition": _y, "aqueduc": _rien,
    "aqueducs": _y, "arrets": None, "autobus": _autobus, "barrieres": _y, "chantiers": _chantiers,
    "chemins_des_bois": _paires, "decalage_nord": _rien, "decor": _y, "decor_solide": _rien,
    "devant": _rien, "devantures": _y, "districts": _rien, "eboueurs": _eboueurs, "entrave": _rien,
    "entraves": _y, "fermeture": _rien, "fermetures": _y, "feux_pietons": _y, "flottants": _rien, "foire": _y,
    "foire_enclos": _foire_enclos, "fourriere": _y, "graffitis": _y, "graine": _rien, "grille": None,
    "grille_nord": _rien, "hauteur": None, "ile": _y, "incendies": _y, "interieurs": _rien,
    "intersections": _y, "jeux_de_foire": _y, "kiosques_de_foire": _y, "lampes": _y, "lave_auto": _y, "largeur": _rien,
    "metro": _y, "montagne_russe": _montagne_russe, "mouillages": _mouillages, "neige": _neige,
    "nids_de_poule": _y, "nom": _rien, "paquets": _y, "plages": _y, "points_interet": _y, "ponts": _y,
    "portes": _y, "portes_garage": _y, "rampes": _y, "reclames": _y, "relief": _relief, "residences": _y,
    "roue": _y, "scenes": _y, "slug": _rien, "sol": None, "stationnement_du_poste": _y, "toits": _y,
    "train_de_foire": _train, "tramway": _tramway, "traversier": _traversier, "tuile_px": _rien,
    "tuiles_bouchees": _rien, "voie": None, "zones": _y,
}


def decaler(ville: dict, n: int) -> None:
    """Toute la ville descend de `n` rangées ; les `n` rangées du haut restent inertes (`M`) en attendant la
    bande. ⚠️ Une clé que `DECALAGES` ne connaît pas LÈVE, en la nommant."""
    inconnues = sorted(set(ville) - set(DECALAGES))
    if inconnues:
        raise KeyError(f"nord.decaler ne sait pas décaler {inconnues} : ajoute-les à nord.DECALAGES")
    _VUS.clear()
    try:
        for cle, f in DECALAGES.items():
            if f is not None and cle in ville:
                f(ville[cle], n)
    finally:
        _VUS.clear()
    ville["arrets"] = {f"{k.split(',')[0]},{int(k.split(',')[1]) + n}": v for k, v in ville["arrets"].items()}
    ville["sol"][:0] = ["M" * ville["largeur"]] * n
    ville["voie"][:0] = ["." * ville["largeur"]] * n
    ville["hauteur"] += n
    ville["grille"]["y0"] = n
    ville["decalage_nord"] = n


# --- La pose : décaler, coller, coudre ---------------------------------------------------------------

_CACHE: dict = {}


def _bande() -> _ChantierNord:
    """La bande ne dépend que de sa trame et de sa graine : bâtie une fois par processus."""
    if "bande" not in _CACHE:
        _CACHE["bande"] = batir_la_bande()
    return _CACHE["bande"]


def colonnes_de_la_couture() -> list[int]:
    """Les x où une voie nord-sud de la bande débouche sur le boulevard de la couture."""
    ch = _bande()
    return [x for x in range(ch.largeur) if ch.voie[DECALAGE_NORD - 1][x] != "."]


def poser(ville: dict) -> None:
    """Toute la ville descend de `DECALAGE_NORD` rangées, et la bande se colle au-dessus. Sans un dé de la
    ville : ce qui suit ne lit que la ville finie et la bande, bâtie avec sa graine à elle."""
    n, ch = DECALAGE_NORD, _bande()
    decaler(ville, n)
    est = ville["sol"][n][ch.largeur:]                   # la falaise et les montagnes de l'est
    for y in range(n):
        ville["sol"][y] = "".join(ch.sol[y]) + est
        ville["voie"][y] = "".join(ch.voie[y]) + "." * len(est)
    # LA COUTURE : là où une voie de la bande débouche, le trottoir nord du boulevard s'ouvre comme un
    # croisement — la rangée 110 de la bande, qui l'a bâti ouvert — et le croisement gagne son bras nord.
    couture = colonnes_de_la_couture()
    for x in couture:
        for cle, grille in (("sol", ch.sol), ("voie", ch.voie)):
            ligne = ville[cle][n]
            ville[cle][n] = ligne[:x] + grille[n][x] + ligne[x + 1:]
    for inter in ville["intersections"]:
        if (inter["y"] <= n + carte.TROTTOIR < inter["y"] + inter["h"]
                and any(inter["x"] <= x < inter["x"] + inter["l"] for x in couture)):
            inter["bras"] = "".join(c for c in "NSOE" if c in inter["bras"] or c == "N")
    def haut(o):
        return o["y"] < n
    for cle, source in (("portes", ch.portes), ("decor", ch.decor), ("lampes", ch.lampes),
                        ("residences", ch.residences), ("devantures", ch.devantures), ("toits", ch.toits),
                        ("points_interet", ch.points), ("intersections", ch.intersections),
                        ("feux_pietons", ch.feux_nord)):
        # ⚠️ DES COPIES : la bande est bâtie une fois par processus (`_bande`), et la ville qu'on rend
        # est à qui la lit (le paquet la modifie) ; partager ses objets rendait le deuxième paquet autre.
        ville[cle].extend(copy.deepcopy([o for o in source if haut(o)]))
    ville["arrets"].update({k: v for k, v in ch.arrets.items() if int(k.split(",")[1]) < n})
    ville["interieurs"].update(copy.deepcopy(ch.pieces))
    slugs = {d["slug"] for d in DISTRICTS_NORD}
    ville["zones"].extend(copy.deepcopy({**z, "h": min(z["h"], n - z["y"])}) for z in ch.zones()
                          if z["district"] in slugs and not z.get("gang"))
    ville["districts"].extend({"slug": d["slug"], "nom": d["nom"], "gang": d["gang"], "eau": False}
                              for d in DISTRICTS_NORD)
    ville["grille_nord"] = {"colonnes": list(carte.COLONNES), "rangees": list(RANGEES_NORD),
                            "rues_v": list(carte.RUES_V), "rues_h": list(RUES_H_NORD),
                            "trottoir": carte.TROTTOIR, "standing": list(ch.standing),
                            "usage": list(ch.usage), "y0": 0}
