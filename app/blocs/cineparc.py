"""Le ciné-parc du Belvédère, au bout des Érables (docs/jalons/le-cine-parc.md).

L'été, le soir, un film sur un écran géant à la sortie de la ville ; on y entre en char, on se gare dans
une rangée, on éteint ses phares. On le rejoint par le bord OUEST des Érables : on pousse contre le
bord, la carte fait un noir, et on est dans l'allée qui entre par le côté est du terrain.

⚠️ **UN BLOC, PAS UN TERRAIN DE PLUS EN VILLE** : un grand terrain en bord de ville aurait fait glisser
la ville (la règle « agrandir la carte sous la trame »). Derrière un fondu au noir, il ne pèse rien sur
`/api/carte`, et le trafic n'y entre pas : le bloc n'a pas une voie.

⚠️ **L'ÉCRAN, LE FILM, LES HAUT-PARLEURS ET LES SPECTATEURS SONT AU NAVIGATEUR** (`static/js/cineparc.js`) :
le plan pose le cadre de l'écran (une façade), l'asphalte, les rangées de cases, le grillage et le
casse-croûte ; le reste se peint, et vit selon la saison et l'heure.

⚠️ **PAS UNE CASE EN ARRIÈRE DE LA CABANE** (Martin, 29 sept. 2026) : derrière elle, au sud, on regarderait un
mur, pas l'écran — ses colonnes restent de l'asphalte dans les rangées d'en arrière.

⚠️ **LE CASSE-CROÛTE EST AU MILIEU DU TERRAIN** (Martin, 27 sept. 2026 : « la cabane doit être au centre »,
docs/jalons/le-casse-croute-du-cine-parc-au-centre-et-le-projecteur.md) : dans l'axe de l'écran, au milieu
de la 2e rangée de cases, comme dans un vrai ciné-parc. C'est aussi la CABINE DU PROJECTEUR : pendant la
séance, le faisceau part de sa fenêtre nord (`cabine`) et s'ouvre jusqu'à la toile (`Cineparc.faisceau`).
Sa porte, au sud, s'ouvre sur le comptoir (`magasins.COMPTOIRS["cineparc"]`, l'été, le soir).
"""

from .. import carte

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AA,,,,,,,,,,FFFFFFFFFFFFFFFFFFFF,,,,,,,,,,AA",
    "A,,,,,,,,,,,FFFFFFFFFFFFFFFFFFFF,,,,,,,,,,,A",
    "AA,,ffffffffffffffffffffffffffffffffffff,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f##################################f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f###^^^^^^^^^^^^^^^^^^^^^^^^^^^^###f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f##################################f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f###^^^^^^^^^^OOOOOOOO^^^^^^^^^^###f,,AA",
    "A,,,f#############OOOOOOOO#############f,,,A",
    "AA,,f#############FWWFDWWF#############f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f###^^^^^^^^^^########^^^^^^^^^^###f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f##################################f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f###^^^^^^^^^^########^^^^^^^^^^###f,,AA",
    "A,,,f#######################################",
    "AA,,f#######################################",
    "A,,,f#######################################",
    "AA,,f#######################################",
    "A,,,ffffffffffffffffffffffffffffffffffff,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,AA",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,AA",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
}

#: Dedans : le projecteur contre le mur nord, braqué sur l'écran par sa fenêtre (la colonne de la porte, l'axe
#: de l'écran) ; le frigo des liqueurs et l'étagère des chips ; le comptoir devant, la caissière derrière. À la mesure de la cabane : huit tuiles de
#: large, comme sa façade, et la porte au même endroit.
PIECE_CASSE_CROUTE = carte._piece("casse_croute_cineparc", "Le casse-croûte du ciné-parc", sol="u", plan="""
BBBBBBBB
Bj  mmeB
B cccc B
B      B
B      B
BWWBDWWB
""", points=(carte._pt("emplettes", 3, 2, genre="cineparc"),),
    gens=carte._gens(("commis", 3, 1), ("client", 6, 3)))

BLOC = {
    "slug": "cineparc",
    "nom": "Le ciné-parc Belvédère",
    "panneau": "CINÉ", "panneau_retour": "VILLE",
    "plan": PLAN,
    "decors": DECORS,
    # Le passage : le trottoir de ceinture du bord OUEST des Érables, un tronçon droit (94 à 98).
    # ⚠️ Il était au bord nord de La Shop : la bande nord de la ville le couvre depuis le 26 sept. 2026
    # (Martin : « déplace le ciné-parc à l'ouest et ajuste son entrée »).
    "passage": {"bord": "ouest", "de": 94, "l": 5},
    # L'allée arrive par le bord EST du terrain, ses quatre rangées d'asphalte, le long du casse-croûte :
    # on entre par le côté et on longe les rangées de cases, qui font toujours face à l'écran.
    "retour": {"bord": "est", "de": 21, "l": 4},
    "arrivee": {"x": 41, "y": 22},
    "gens": False,
    # Le casse-croûte, au milieu du terrain : sa porte, sa pièce.
    "portes": [{"x": 22, "y": 14, "interieur": "casse_croute_cineparc", "lieu": "casse_croute_cineparc"}],
    "pieces": {"casse_croute_cineparc": PIECE_CASSE_CROUTE},
    # Ses lampes : les vitrines du casse-croûte, et les deux lampadaires de l'entrée (le film, lui,
    # éclaire à part : `Cineparc.lampes`, quand il joue).
    "lampes": [{"x": 20, "y": 15, "r": 26, "c": "fenetre"}, {"x": 24, "y": 15, "r": 26, "c": "fenetre"},
               {"x": 41, "y": 20, "r": 40, "c": "lampadaire"}, {"x": 41, "y": 25, "r": 40, "c": "lampadaire"}],
    # L'écran : son cadre (la façade du plan), en tuiles — le navigateur peint la toile au-dessus.
    "ecran": {"x": 12, "y": 2, "l": 20, "h": 2},
    # La fenêtre de la cabine du projecteur : le bord nord du toit du casse-croûte, dans l'axe de l'écran
    # (en tuiles : le faisceau part de là).
    "cabine": {"x": 22, "y": 12},
}
