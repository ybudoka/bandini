"""La garde-robe : des squelettes qu'on habille, pièce par pièce.

Demande de Martin (22 sept. 2026) : « les personnages doivent pouvoir avoir des chapeaux,
casquettes et plus — idéalement des squelettes qu'on habille, ce qui donne une presque
infinité d'habillement » ; « il faut plusieurs types de squelettes pour les types de
personnes ».

Python décide (quels corps, quelles pièces, quelles couleurs, qui porte quoi), JS dessine
(`static/js/garderobe.js`) — comme les devantures et les visages.

- Un **squelette** est un type de corps : `homme` est le corps de toujours (celui du joueur,
  ses 42 poses) ; `femme`, `costaud`, `vieux` et `grand` en sont DÉRIVÉS par des règles
  (élargir le torse, retirer une rangée de jambes, voûter la tête) ; `enfant` est le corps
  d'enfant. Un squelette se dessine en lettres qui disent la région : `h` les cheveux, `s` la
  peau, `c` le haut, `p` le bas, `b` les souliers.
- Une **tenue** est une fiche : le squelette, la peau, une coiffure, un chapeau, un haut (et son
  motif), un bas, des souliers, des accessoires — chacun avec sa couleur. On l'enfile sur le
  squelette : les pièces recolorent ses régions, les chapeaux se posent sur la tête que chaque
  pose montre.
- Une **garde-robe** dit, pour un archétype de passant, dans quoi on pioche. Chaque passant tire
  sa tenue à l'EMPREINTE de son identifiant (`Garderobe.tirer`) : pas un dé de `B.rng`, sinon
  toute la ville se décalerait (voir « grossir un lieu garanti déplace la ville »).
"""

from __future__ import annotations

SQUELETTES = ("homme", "femme", "costaud", "vieux", "grand", "enfant")

COIFFURES = ("courte", "rase", "chauve", "degarnie", "longue", "queue", "chignon", "bouclee",
             "crete", "meche")

#: Ce qu'on a sur la tête. Chacun a son dessin de face, de dos et de profil (`visages.js` a les
#: siens, en grand).
CHAPEAUX = ("aucun", "casquette", "casquette_arriere", "tuque", "feutre", "casque_chantier",
            "kepi", "canotier", "beret", "bandana", "cowboy", "marin", "capuche")

HAUTS = ("chandail", "tshirt", "chemise", "veston", "manteau", "coton_ouate", "camisole",
         "robe", "salopette", "tablier", "veste_travail", "sarrau")

MOTIFS = ("uni", "raye", "carreaute")

BAS = ("pantalon", "short", "jupe")

SOULIERS = ("souliers", "bottes")

ACCESSOIRES = ("lunettes", "lunettes_soleil", "barbe", "moustache", "sac_a_dos", "cravate",
               "foulard")

#: Les peaux et les cheveux que la ville connaît déjà (`pietons.CATALOGUE`), et quelques-uns de
#: plus : la garde-robe les mélange.
PEAUX = ("#f0c098", "#e8b088", "#d9a070", "#c98d66", "#a86e4a", "#7a4a2e", "#5a3420")
CHEVEUX = ("#101018", "#2a1a10", "#3a2a1a", "#6b4b2c", "#7a2a1a", "#b8862a", "#d8c07a",
           "#8a8a8a", "#c8c8c8", "#e8e8e8")
GRIS = ("#8a8a8a", "#c8c8c8", "#e8e8e8")

#: Des familles de couleurs d'habit : sobres, vives, de travail. Une garde-robe en nomme une ou
#: plusieurs.
COULEURS = {
    "sobres": ("#2a2a3a", "#3a3a4a", "#4a4a5a", "#5a4a3a", "#2c3e50", "#34495e", "#6a6a6a",
               "#7f8c8d", "#4a3a2a", "#1a1a22"),
    "vives": ("#c0392b", "#e67e22", "#f1c40f", "#2e8b57", "#2980b9", "#8e44ad", "#c9738a",
              "#16a085", "#d35400", "#e84393"),
    "pastel": ("#f5c6cb", "#c9e4de", "#fde2a7", "#cfd8f7", "#e7d3f5", "#f7e1c5"),
    "travail": ("#5a5f47", "#4a4a3a", "#7a5a2a", "#2f4f6f", "#8a6a3a", "#3a4a5a"),
    "jeans": ("#2f4f7f", "#3a5a8a", "#24385a", "#1f2f4a"),
    "terre": ("#6b4b2c", "#8a6a44", "#5a3a1a", "#9a7a5a", "#4a3020"),
    "souliers": ("#1a1a1a", "#3a2a1a", "#5a3a1a", "#6a6a6a", "#e8e8e8", "#8a4a2a"),
    "chapeaux": ("#1a1a22", "#3a2a1a", "#c0392b", "#2980b9", "#2e8b57", "#f1c40f", "#e8e8e8",
                 "#7a5a2a", "#8e44ad", "#e67e22"),
    # Les uniformes : UNE couleur chacun, celle que la rue reconnaît.
    "police": ("#16264a",),
    "garde": ("#3a3d33",),
}


def _g(squelettes, coiffures, hauts, bas, *, chapeaux=(), chapeau_chance=0.0, motifs=("uni",),
       couleurs_haut=("sobres",), couleurs_bas=("sobres",), couleurs_chapeau=("chapeaux",),
       souliers=("souliers",), cheveux=CHEVEUX, peaux=PEAUX, accessoires=None):
    """Une garde-robe. Les listes sont des TIRAGES (une valeur répétée pèse plus) ;
    `accessoires` : `{nom: chance}`."""
    return {"squelettes": list(squelettes), "coiffures": list(coiffures), "hauts": list(hauts),
            "bas": list(bas), "chapeaux": list(chapeaux), "chapeau_chance": chapeau_chance,
            "motifs": list(motifs), "couleurs_haut": list(couleurs_haut),
            "couleurs_bas": list(couleurs_bas), "couleurs_chapeau": list(couleurs_chapeau),
            "souliers": list(souliers), "cheveux": list(cheveux), "peaux": list(peaux),
            "accessoires": dict(accessoires or {})}


#: Qui pioche dans quoi — par archétype de `pietons.CATALOGUE`. ⚠️ Seuls les archétypes au
#: corps commun (`sprite: "joueur"`) s'habillent : les corps dessinés à la main (la mascotte,
#: l'avocat, le jongleur…) gardent le leur. Un gang ou un uniforme garde SA couleur
#: (`couleurs_haut: ("gang",)` → `haut_fixe`) : c'est à elle qu'on le reconnaît dans la rue.
GARDE_ROBES: dict[str, dict] = {
    "passant": _g(("homme", "homme", "costaud", "grand", "vieux"),
                  ("courte", "courte", "rase", "degarnie", "chauve", "bouclee", "meche"),
                  ("chandail", "chemise", "tshirt", "veston", "manteau", "coton_ouate"),
                  ("pantalon", "pantalon", "pantalon", "short"),
                  chapeaux=("casquette", "tuque", "feutre", "beret", "casquette_arriere"),
                  chapeau_chance=0.35, motifs=("uni", "uni", "uni", "raye", "carreaute"),
                  couleurs_haut=("sobres", "vives"), couleurs_bas=("sobres", "jeans"),
                  accessoires={"lunettes": 0.15, "lunettes_soleil": 0.08, "barbe": 0.15,
                               "moustache": 0.12, "sac_a_dos": 0.08, "cravate": 0.06}),
    "passante": _g(("femme", "femme", "femme", "vieux"),
                   ("longue", "longue", "queue", "chignon", "bouclee", "meche", "courte"),
                   ("chandail", "robe", "chemise", "tshirt", "manteau", "camisole"),
                   ("jupe", "pantalon", "pantalon", "short"),
                   chapeaux=("beret", "tuque", "canotier", "bandana"), chapeau_chance=0.25,
                   motifs=("uni", "uni", "raye", "carreaute"),
                   couleurs_haut=("vives", "pastel", "sobres"), couleurs_bas=("sobres", "jeans"),
                   accessoires={"lunettes": 0.12, "lunettes_soleil": 0.12, "foulard": 0.15,
                                "sac_a_dos": 0.06}),
    "ouvrier": _g(("homme", "costaud", "costaud", "grand"), ("courte", "rase", "degarnie", "chauve"),
                  ("veste_travail", "salopette", "chemise", "tshirt"), ("pantalon",),
                  chapeaux=("casque_chantier", "casque_chantier", "casquette", "tuque"),
                  chapeau_chance=0.8, motifs=("uni", "carreaute"), couleurs_haut=("travail",),
                  couleurs_bas=("travail", "jeans"), souliers=("bottes",),
                  accessoires={"barbe": 0.25, "moustache": 0.2}),
    "ado": _g(("grand", "homme", "femme"), ("meche", "crete", "longue", "rase", "queue"),
              ("coton_ouate", "tshirt", "tshirt", "camisole"), ("pantalon", "short"),
              chapeaux=("casquette_arriere", "casquette", "capuche", "tuque"), chapeau_chance=0.5,
              couleurs_haut=("vives", "sobres"), couleurs_bas=("jeans", "sobres"),
              accessoires={"sac_a_dos": 0.35, "lunettes_soleil": 0.15}),
    "dame": _g(("vieux", "femme"), ("chignon", "bouclee", "courte"),
               ("manteau", "robe", "chandail"), ("jupe", "pantalon"),
               chapeaux=("canotier", "beret", "feutre"), chapeau_chance=0.45,
               couleurs_haut=("pastel", "sobres"), couleurs_bas=("sobres",), cheveux=GRIS,
               accessoires={"lunettes": 0.5, "foulard": 0.3}),
    "cravate": _g(("homme", "costaud", "grand"), ("courte", "rase", "chauve"), ("veston",),
                  ("pantalon",), chapeaux=("feutre",), chapeau_chance=0.6,
                  couleurs_haut=("gang",), couleurs_bas=("sobres",),
                  accessoires={"cravate": 1.0, "lunettes_soleil": 0.4, "moustache": 0.2}),
    "morue": _g(("homme", "costaud", "femme"), ("courte", "longue", "rase", "queue"),
                ("manteau", "chandail", "veste_travail"), ("pantalon",),
                chapeaux=("marin", "tuque"), chapeau_chance=0.7, couleurs_haut=("gang",),
                couleurs_bas=("sobres", "jeans"), souliers=("bottes",),
                accessoires={"barbe": 0.3}),
    "chevreuil": _g(("homme", "grand", "costaud"), ("courte", "rase", "longue"),
                    ("chemise", "coton_ouate"), ("pantalon",),
                    chapeaux=("casquette", "cowboy", "tuque"), chapeau_chance=0.7,
                    motifs=("carreaute", "carreaute", "uni"), couleurs_haut=("gang",),
                    couleurs_bas=("jeans",), souliers=("bottes",),
                    accessoires={"barbe": 0.35, "moustache": 0.2}),
    "boulonneux": _g(("homme", "costaud"), ("rase", "crete", "chauve"),
                     ("veste_travail", "camisole", "tshirt"), ("pantalon",),
                     chapeaux=("bandana", "casquette_arriere"), chapeau_chance=0.5,
                     couleurs_haut=("gang",), couleurs_bas=("sobres", "jeans"), souliers=("bottes",),
                     accessoires={"barbe": 0.3, "lunettes_soleil": 0.3}),
    "skateux": _g(("grand", "homme"), ("meche", "longue", "crete"), ("coton_ouate", "tshirt"),
                  ("short", "pantalon"), chapeaux=("casquette_arriere", "capuche", "tuque"),
                  chapeau_chance=0.7, couleurs_haut=("gang",), couleurs_bas=("jeans", "sobres"),
                  accessoires={"sac_a_dos": 0.3}),
    "docker": _g(("costaud", "costaud", "homme"), ("courte", "rase", "degarnie"),
                 ("chandail", "veste_travail", "salopette"), ("pantalon",),
                 chapeaux=("tuque", "tuque", "marin", "casquette"), chapeau_chance=0.75,
                 couleurs_haut=("travail", "sobres"), couleurs_bas=("travail", "jeans"),
                 souliers=("bottes",), accessoires={"barbe": 0.4, "moustache": 0.2}),
    "banlieusard": _g(("homme", "femme", "costaud", "grand"), ("courte", "longue", "degarnie", "queue"),
                      ("tshirt", "chemise", "chandail", "coton_ouate"), ("pantalon", "short"),
                      chapeaux=("casquette",), chapeau_chance=0.3,
                      couleurs_haut=("vives", "pastel", "sobres"), couleurs_bas=("jeans", "sobres"),
                      accessoires={"lunettes_soleil": 0.2, "moustache": 0.1}),
    "machiniste": _g(("homme", "costaud"), ("courte", "rase", "degarnie"), ("salopette", "veste_travail"),
                     ("pantalon",), chapeaux=("casquette", "casque_chantier"), chapeau_chance=0.6,
                     couleurs_haut=("travail",), couleurs_bas=("travail",), souliers=("bottes",),
                     accessoires={"lunettes": 0.3, "moustache": 0.25}),
    "promeneur": _g(("homme", "femme", "vieux"), ("courte", "longue", "degarnie", "chignon"),
                    ("manteau", "chandail", "coton_ouate"), ("pantalon",),
                    chapeaux=("tuque", "casquette", "beret"), chapeau_chance=0.5,
                    couleurs_haut=("sobres", "vives"), couleurs_bas=("sobres", "jeans"),
                    accessoires={"foulard": 0.3, "lunettes": 0.2}),
    "itinerant": _g(("homme", "vieux", "costaud"), ("longue", "degarnie", "bouclee"),
                    ("manteau", "coton_ouate", "chandail"), ("pantalon",),
                    chapeaux=("tuque", "tuque", "capuche"), chapeau_chance=0.7,
                    couleurs_haut=("terre", "travail"), couleurs_bas=("terre", "sobres"),
                    souliers=("bottes",), accessoires={"barbe": 0.7}),
    "livreur": _g(("homme", "grand"), ("courte", "rase", "meche"), ("tshirt", "veste_travail"),
                  ("pantalon", "short"), chapeaux=("casquette",), chapeau_chance=0.9,
                  couleurs_haut=("vives",), couleurs_bas=("sobres",),
                  accessoires={"sac_a_dos": 0.5}),
    "mere": _g(("femme",), ("longue", "queue", "chignon"), ("chandail", "manteau", "robe"),
               ("pantalon", "jupe"), chapeaux=("tuque",), chapeau_chance=0.2,
               couleurs_haut=("pastel", "vives"), couleurs_bas=("jeans", "sobres"),
               accessoires={"sac_a_dos": 0.2}),
    "vendeur": _g(("costaud", "homme"), ("courte", "degarnie"), ("tablier",), ("pantalon",),
                  chapeaux=("canotier", "casquette"), chapeau_chance=0.7, couleurs_haut=("vives",),
                  couleurs_bas=("sobres",), accessoires={"moustache": 0.4}),
    "commis": _g(("homme", "femme", "grand"), ("courte", "queue", "meche"), ("tablier", "chemise"),
                 ("pantalon",), couleurs_haut=("vives",), couleurs_bas=("sobres",),
                 accessoires={"lunettes": 0.2}),
    "soignante": _g(("femme", "homme"), ("chignon", "queue", "courte"), ("sarrau",), ("pantalon",),
                    couleurs_haut=("pastel",), couleurs_bas=("pastel",),
                    accessoires={"lunettes": 0.2}),
    # L'agent et le garde de sécurité : l'uniforme est fixe (`police.js` le reconnaît à sa
    # couleur), la tête et le corps varient.
    "policier": _g(("homme", "costaud", "grand"), ("courte", "rase", "degarnie"), ("chemise",),
                   ("pantalon",), chapeaux=("kepi",), chapeau_chance=1.0,
                   couleurs_haut=("gang",), couleurs_bas=("police",), couleurs_chapeau=("police",),
                   accessoires={"moustache": 0.3, "lunettes_soleil": 0.2}),
    "garde": _g(("costaud", "costaud", "homme"), ("rase", "courte", "chauve"), ("veste_travail",),
                ("pantalon",), chapeaux=("casquette",), chapeau_chance=0.8,
                couleurs_haut=("gang",), couleurs_bas=("garde",), couleurs_chapeau=("garde",),
                souliers=("bottes",), accessoires={"lunettes_soleil": 0.3, "barbe": 0.15}),
    "gardien": _g(("vieux", "costaud"), ("degarnie", "courte"), ("veste_travail",), ("pantalon",),
                  chapeaux=("casquette",), chapeau_chance=1.0, couleurs_haut=("travail",),
                  couleurs_bas=("travail",), souliers=("bottes",), cheveux=GRIS,
                  accessoires={"moustache": 0.5}),
}


def _tenue(squelette, peau, cheveux, coiffure, haut, couleur_haut, bas, couleur_bas, *,
           chapeau="aucun", couleur_chapeau="#1a1a22", motif="uni", souliers="souliers",
           couleur_souliers="#1a1a1a", accessoires=(), accent="#c0392b"):
    return {"squelette": squelette, "peau": peau, "cheveux": cheveux, "coiffure": coiffure,
            "chapeau": chapeau, "couleur_chapeau": couleur_chapeau, "haut": haut,
            "couleur_haut": couleur_haut, "motif": motif, "bas": bas, "couleur_bas": couleur_bas,
            "souliers": souliers, "couleur_souliers": couleur_souliers,
            "accessoires": list(accessoires), "accent": accent}


#: Le squelette de chaque personnage : son corps, d'après sa fiche (`docs/personnages/`).
_CORPS = {"ti_guy": "costaud", "thibodeau": "vieux", "marco": "homme", "bouchard": "costaud",
          "josee": "femme", "civil": "homme", "narrateur": "grand", "tipaul": "costaud",
          "lulu": "femme", "raymonde": "femme", "ovila": "vieux", "mo": "costaud", "fern": "grand",
          "mado": "femme", "gege": "costaud", "xavier": "grand", "lachance": "grand", "gus": "costaud",
          "rosa": "femme", "ginette": "femme", "gilles": "vieux", "bonimenteur": "grand",
          "sven": "homme", "berube": "vieux"}

#: Du portrait à la rue : ce que `visages.py` dit de sa tête, la rue le porte aussi.
_COIFFURE_DE = {"courte": "courte", "brosse": "rase", "degarnie": "degarnie", "chauve": "chauve",
                "gominee": "courte", "meche": "meche", "longue": "longue", "queue": "queue",
                "chignon": "chignon", "permanente": "bouclee", "bouclee": "bouclee",
                "carre": "longue", "hirsute": "bouclee"}
_CHAPEAU_DE = {"aucun": "aucun", "police": "kepi", "casquette": "casquette", "tuque": "tuque",
               "canotier": "canotier", "marin": "marin", "coiffe": "bandana"}
_HAUT_DE = {"chandail": "chandail", "chemise_police": "chemise", "sarrau": "sarrau",
            "veston": "veston", "veste": "veste_travail", "uniforme": "chemise",
            "tablier": "tablier", "blouse": "chemise", "col_roule": "chandail", "gilet": "veston"}


def tenue_du_personnage(slug: str) -> dict:
    """La tenue de rue d'un personnage, tirée de son portrait (`visages.VISAGES`) et de ses
    couleurs (`PERSONNAGES`). Une seule source pour sa tête : le chapeau du portrait est celui
    qu'il porte dans la rue."""
    from . import missions, visages
    p = next(q for q in missions.PERSONNAGES if q["slug"] == slug)
    v = visages.VISAGES[slug]
    c = p["couleurs"]
    acc = []
    if v["pilosite"] in ("barbe", "barbe_courte", "bouc"):
        acc.append("barbe")
    elif v["pilosite"] in ("moustache", "moustache_epaisse"):
        acc.append("moustache")
    if v["lunettes"] != "aucunes":
        acc.append("lunettes")
    if "noeud_pap" in v["signes"] or v["habit"] == "veston":
        acc.append("cravate")
    chapeau = _CHAPEAU_DE[v["chapeau"]]
    femme = p["genre"] == "femme"
    return _tenue(_CORPS.get(slug, "femme" if femme else "homme"), c["s"], c["h"],
                  _COIFFURE_DE[v["coiffure"]], _HAUT_DE[v["habit"]], c["c"],
                  "jupe" if femme and v["habit"] in ("blouse", "tablier") else "pantalon", c["p"],
                  chapeau=chapeau, couleur_chapeau=v["extra"].get("t", "#1a1a22"),
                  souliers="bottes" if slug in ("gege", "mo", "sven", "gilles", "ovila", "berube") else "souliers",
                  accessoires=acc, accent="#e8b33c" if chapeau == "kepi" else "#c0392b")


def exporter() -> dict:
    """Ce que `garderobe.js` reçoit : les listes (il les connaît en dessin), les couleurs, les
    garde-robes des archétypes et la tenue de chaque personnage."""
    from . import missions, pietons
    robes = {}
    for arch in pietons.CATALOGUE:
        g = GARDE_ROBES.get(arch["slug"])
        if not g:
            continue
        g = dict(g)
        # Le gang — ou l'uniforme — garde SA couleur : celle que l'archétype porte déjà (`couleurs.c`).
        if "gang" in g["couleurs_haut"]:
            g["couleurs_haut"] = []
            g["haut_fixe"] = arch["couleurs"]["c"]
        robes[arch["slug"]] = g
    return {
        "squelettes": list(SQUELETTES), "coiffures": list(COIFFURES), "chapeaux": list(CHAPEAUX),
        "hauts": list(HAUTS), "motifs": list(MOTIFS), "bas": list(BAS), "souliers": list(SOULIERS),
        "accessoires": list(ACCESSOIRES), "couleurs": {k: list(v) for k, v in COULEURS.items()},
        "garde_robes": robes,
        "personnages": {p["slug"]: tenue_du_personnage(p["slug"]) for p in missions.PERSONNAGES},
    }
