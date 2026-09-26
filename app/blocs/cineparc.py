"""Le ciné-parc du Belvédère, au bout de La Shop (docs/jalons/le-cine-parc.md).

L'été, le soir, un film sur un écran géant à la sortie de la ville ; on y entre en char, on se gare dans
une rangée, on éteint ses phares. On le rejoint par le bord NORD de La Shop : on pousse contre le bord,
la carte fait un noir, et on est sur le chemin du ciné-parc.

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
    "A,,,f#OOOOOO###########################f,,,A",
    "AA,,f#OOOOOO###########################f,,AA",
    "A,,,f#FWdFWF###########################f,,,A",
    "AA,,f##################################f,,AA",
    "A,,,ffffffffffffffff####ffffffffffffffff,,,A",
    "AA,,,,,,,,,,,,,,,,,,####,,,,,,,,,,,,,,,,,,AA",
    "A,,,,,,,,,,,,,,,,,,,####,,,,,,,,,,,,,,,,,,,A",
    "AA,,,,,,,,,,,,,,,,,,####,,,,,,,,,,,,,,,,,,AA",
    "A,,,,,,,,,,,,,,,,,,,####,,,,,,,,,,,,,,,,,,,A",
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
    # Le passage : le trottoir de ceinture du bord NORD de La Shop, à l'autre bout du bord nord par
    # rapport à la clairière (aux Érables, colonnes 55 à 59).
    "passage": {"bord": "nord", "de": 350, "l": 5},
    # Le chemin arrive par le bord SUD du bloc, ses quatre colonnes d'asphalte.
    "retour": {"bord": "sud", "de": 20, "l": 4},
    "arrivee": {"x": 21, "y": 27},
    "gens": False,
    # Ses lampes : les vitrines du casse-croûte, et les deux lampadaires de l'entrée (le film, lui,
    # éclaire à part : `Cineparc.lampes`, quand il joue).
    "lampes": [{"x": 7, "y": 24, "r": 26, "c": "fenetre"}, {"x": 10, "y": 24, "r": 26, "c": "fenetre"},
               {"x": 19, "y": 26, "r": 40, "c": "lampadaire"}, {"x": 24, "y": 26, "r": 40, "c": "lampadaire"}],
    # L'écran : son cadre (la façade du plan), en tuiles — le navigateur peint la toile au-dessus.
    "ecran": {"x": 12, "y": 2, "l": 20, "h": 2},
}
