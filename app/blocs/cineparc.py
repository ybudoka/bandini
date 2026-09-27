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
"""

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
    "AA,,f###^^^^^^^^^^^^^^^^^^^^^^^^^^^^###f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f##################################f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f###^^^^^^^^^^^^^^^^^^^^^^^^^^^^###f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f##################################f,,AA",
    "A,,,f##################################f,,,A",
    "AA,,f###^^^^^^^^^^^^^^^^^^^^^^^^^^^^###f,,AA",
    "A,,,f#OOOOOO################################",
    "AA,,f#OOOOOO################################",
    "A,,,f#FWdFWF################################",
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
    # Ses lampes : les vitrines du casse-croûte, et les deux lampadaires de l'entrée (le film, lui,
    # éclaire à part : `Cineparc.lampes`, quand il joue).
    "lampes": [{"x": 7, "y": 24, "r": 26, "c": "fenetre"}, {"x": 10, "y": 24, "r": 26, "c": "fenetre"},
               {"x": 41, "y": 20, "r": 40, "c": "lampadaire"}, {"x": 41, "y": 25, "r": 40, "c": "lampadaire"}],
    # L'écran : son cadre (la façade du plan), en tuiles — le navigateur peint la toile au-dessus.
    "ecran": {"x": 12, "y": 2, "l": 20, "h": 2},
}
