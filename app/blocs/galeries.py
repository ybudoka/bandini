"""Les Galeries de la Baie, le centre d'achat hanté (docs/jalons/le-centre-d-achat-hante.md).

Le jour, un centre d'achat ordinaire : des boutiques, un comptoir, l'aire de restauration. La NUIT, il
est vide, et il ne dort pas : les lumières s'éteignent une à une, une musique d'ascenseur joue pour
personne, et une voix au haut-parleur — « annonceur centre d'achat 2 », générée pour ça et jamais
utilisée — sait où tu es. Un gardien qui n'est peut-être pas un gardien. Drôle d'abord, inquiétant
ensuite, jamais gore (`static/js/galeries.js`).

⚠️ **UN BLOC**, comme le ciné-parc et la cabane : une grande pièce de plus EN VILLE aurait fait glisser la
ville. On y entre par le bord OUEST des Érables ; on arrive par l'entrée du stationnement.
"""

from .. import carte

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,OOOOOOOOOOOOOOOOOOOOOOOOOOOO,,,,,A",
    "A,,,,,FWWFWWFWWFWWFDFFWWFWWFWWFWWF,,,,,A",
    "A,,,................................,,,A",
    "####################################,,,A",
    "####################################,,,A",
    "#######^^^^^^^^^^^^^^^^^^^^^^^^^^^##,,,A",
    "####################################,,,A",
    "A,,,################################,,,A",
    "A,,,################################,,,A",
    "A,,,###^^^^^^^^^^^^^^^^^^^^^^^^^^^##,,,A",
    "A,,,################################,,,A",
    "A,,,################################,,,A",
    "A,,,################################,,,A",
    "A,,,###^^^^^^^^^^^^^^^^^^^^^^^^^^^##,,,A",
    "A,,,################################,,,A",
    "A,,,################################,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
}

#: Dedans : les boutiques au mur du haut (leurs étagères), deux comptoirs, l'escalier roulant arrêté
#: (`/`) et la fontaine (`o`) au milieu, l'aire de restauration en bas ; au fond à gauche, l'étagère du
#: « rayon 4 », où quelqu'un a oublié quelque chose (`galeries.js`, la nuit).
#: ⚠️ `vide_la_nuit` : ses gens ne naissent pas la nuit (`Entites.peuplerInterieur`).
PIECE = carte._piece("galeries", "Les Galeries de la Baie", sol="u", plan="""
BBBBBBBBBBBBBBBBBBBBBBBB
BeeeBeeeBeeeBeeeBeeeBjjB
B                      B
B  c     //    oo   c  B
B        //    oo      B
B                      B
Bh aa           aa  h  B
Bh aa           aa  h  B
B                      B
Be                    eB
BBBBBBBBBBBWDWBBBBBBBBBB
""", points=(carte._pt("emplettes", 3, 3, genre="commerce"), carte._pt("emplettes", 20, 3, genre="service")),
    gens=carte._gens(("commis", 3, 2), ("commis", 20, 2), ("client", 12, 5), ("client", 6, 8)))
PIECE["vide_la_nuit"] = True
#: Le rayon 4 : la tuile devant l'étagère du fond, où l'objet perdu attend (la nuit).
PIECE["trouvaille"] = {"x": 2, "y": 9}

#: LA VOIX AU HAUT-PARLEUR (la nuit) : ce qu'elle dit, et quand (`galeries.js`). Drôle d'abord, inquiétant
#: ensuite, jamais gore. `quand` : `entree` (on entre la nuit), `lumiere` (une lumière s'éteint), les
#: coins qu'elle « voit » (`fontaine`, `escalier`, `rayon`), `gardien` (il est apparu), `trouvaille`.
VOIX = "annonceur centre d'achat 2"
ANNONCES: tuple[dict, ...] = (
    {"cle": "entree", "texte": "Bonsoir, et bienvenue aux Galeries de la Baie. Les Galeries sont fermées. Bon magasinage.",
     "jeu": "[calm] Bonsoir, et bienvenue aux Galeries de la Baie. [mysteriously] Les Galeries sont fermées… Bon magasinage."},
    {"cle": "lumiere", "texte": "Nous éteignons les lumières. Pour votre sécurité, restez dans la lumière.",
     "jeu": "[calm] Nous éteignons les lumières. [softly] Pour votre sécurité… restez dans la lumière."},
    {"cle": "lumiere_2", "texte": "Encore une. Ne vous inquiétez pas, ça arrive.",
     "jeu": "[deadpan] Encore une. [softly] Ne vous inquiétez pas… ça arrive."},
    {"cle": "fontaine", "texte": "Client près de la fontaine. Oui, vous. Ne vous retournez pas.",
     "jeu": "[calm] Client près de la fontaine. [quietly] Oui, vous. [mysteriously] Ne vous retournez pas."},
    {"cle": "escalier", "texte": "L'escalier roulant est en panne depuis mil neuf cent quatre-vingt-sept. Prenez votre temps.",
     "jeu": "[matter-of-fact] L'escalier roulant est en panne depuis mil neuf cent quatre-vingt-sept. [calm] Prenez votre temps."},
    {"cle": "rayon", "texte": "Client en rayon quatre. Votre mère vous attend.",
     "jeu": "[calm] Client en rayon quatre… [mysteriously] Votre mère vous attend."},
    {"cle": "gardien", "texte": "Nous rappelons à notre aimable clientèle que le gardien n'est pas un gardien.",
     "jeu": "[calm] Nous rappelons à notre aimable clientèle que le gardien… [deadpan] n'est pas un gardien."},
    {"cle": "trouvaille", "texte": "Merci d'avoir retrouvé l'article perdu. On vous garde une place.",
     "jeu": "[warmly] Merci d'avoir retrouvé l'article perdu. [mysteriously] On vous garde une place."},
)

#: La hantise, réglée ici : une lumière s'éteint toutes les `lumiere_s` secondes (jusqu'à `lumieres`), le
#: gardien se montre dès la deuxième éteinte, loin du joueur, et s'évanouit quand on s'approche à
#: `gardien_px` ; l'objet perdu du rayon 4 rapporte `recompense`, une fois par nuit.
HANTISE = {"lumiere_s": 7, "lumieres": 4, "gardien_px": 48, "gardien_revient_s": 8, "recompense": 40,
           "objet": "UN TOUTOU EN PELUCHE… QUELQU'UN LE CHERCHAIT."}


def pour_le_navigateur() -> dict:
    """Ce que le navigateur doit savoir de la hantise : ses réglages, et le TEXTE de chaque annonce (le
    sous-titre de la voix)."""
    return {"hantise": dict(HANTISE), "annonces": {a["cle"]: a["texte"] for a in ANNONCES}}


BLOC = {
    "slug": "galeries",
    "nom": "Les Galeries de la Baie",
    "plan": PLAN,
    "decors": DECORS,
    "panneau": "GALERIES", "panneau_retour": "VILLE",
    # Le passage : le trottoir de ceinture du bord OUEST des Érables (rangées 60 à 64), au nord du chalet
    # (164 à 168).
    "passage": {"bord": "ouest", "de": 60, "l": 5},
    "retour": {"bord": "ouest", "de": 11, "l": 4},
    "arrivee": {"x": 2, "y": 12},
    "gens": False,
    "portes": [{"x": 19, "y": 9, "interieur": "galeries", "lieu": "galeries"}],
    "pieces": {"galeries": PIECE},
    "lampes": [{"x": 10, "y": 10, "r": 40, "c": "lampadaire"}, {"x": 29, "y": 10, "r": 40, "c": "lampadaire"}],
}
