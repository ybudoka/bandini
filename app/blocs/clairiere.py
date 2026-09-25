"""Le bloc d'essai : la clairière du lac, au nord des Érables (vague 1 des blocs de carte).

Un bloc minuscule — un lac, sa grève, un quai de bois, des arbres — pour prouver le
passage lui-même : on pousse contre le bord nord de la ville sur le trottoir de ceinture
des Érables, la carte fait un noir, la clairière se charge, et on revient par le chemin du
sud. Rien à y faire encore : c'est la porte qu'on juge, pas la pièce.
"""

#: ⚠️ LE PLAN EST LA VÉRITÉ, comme celui de l'île (`app/ile.py`) : les glyphes de la
#: `carte.LEGENDE`, plus ceux de `DECORS` (un décor posé sur un sol).
PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AA,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A",
    "A,,A,A,,A,A,AA,sssssssssss,AA,,,,,A,,AAA",
    "AAA,,,,,,,,,ssss~~~~~~~~~ssss,,,,,,,,,,A",
    "A,,,,,,,,,sss~~~~~~~~~~~~~~~sss,,,,,,,AA",
    "AA,,,,,,,ss~~~~~~~~~~~~~~~~~~~ss,,,,,,,A",
    "A,A,,,,,ss~~~~~~~~~~~~~~~~~~~~~ss,,,,,AA",
    "AA,,,,,sss~~~~~~~~~~~~~~~~~~~~~sss,,,,,A",
    "A,,,,,,ss~~~~~~~~~~~~~~~~~~~~~~~ss,,,,AA",
    "AA,,,,,sss~~~~~~~~~~~~~~~~~~~~~sssb,,A,A",
    "A,A,,,,,ss~~~~~~~~~~~~~~~~~~~~~ss,,,,,AA",
    "AA,,,,,,,ss~~~~~~~~~~~~~~~~~~~ss,,,,,A,A",
    "A,A,,,,,b,sss~~~~~~~~~~~~~~~sss,,,,,,,AA",
    "AA,,,,,,,,,,ssss~~~QQQ~~~ssss,,,,,,,,A,A",
    "A,A,,,b,,,,,,,,ssssgggssss,,,,,,,,,b,,AA",
    "AA,,,,b,,,,,,,,,,,,ggg,,,,,,,,,bb,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,AAA",
    "AAA,,,,,,,,,,,b,,,,ggg,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,b,,b,,,,,,ggg,,,,,,,,,,,,,,,,AA",
    "AA,,,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,b,,b,,ggg,,,,,,,,,,,,,,,,AA",
    "AAA,,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,ggg,,,,,,,,,,,,,,,,AA",
    "AAA,A,A,,A,,A,,,,,,ggg,,,,,,,,AAA,,AA,,A",
    "A,A,A,A,A,A,A,A,A,,ggg,,A,A,A,A,A,A,A,AA",
    "AAAAAAAAAAAAAAAAAA,ggg,AAAAAAAAAAAAAAAAA",
)

#: Un décor posé sur un sol : `glyphe du plan -> (sol dessous, type de décor)`.
DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
    "b": (",", "buisson"),
}

BLOC = {
    "slug": "clairiere",
    "nom": "La clairière du lac",
    # Les deux panneaux de bois : au passage en ville, et au chemin du retour. Courts : la
    # police pixel fait quatre pixels par lettre.
    "panneau": "LAC", "panneau_retour": "VILLE",
    "plan": PLAN,
    "decors": DECORS,
    # ⚠️ LE PASSAGE, DES DEUX CÔTÉS. Dans la ville : le trottoir de ceinture du bord nord,
    # au milieu des Érables (colonnes 55 à 59) — on y POUSSE contre le haut de la carte ; le
    # longer ne déclenche rien. Dans le bloc : le chemin du bord sud, ses trois colonnes.
    "passage": {"bord": "nord", "de": 55, "l": 5},
    "retour": {"bord": "sud", "de": 19, "l": 3},
    # Où l'on apparaît en arrivant : sur le chemin, trois tuiles au-dessus du bord (on
    # ne repart pas d'un pas en arrière).
    "arrivee": {"x": 20, "y": 22},
    # Personne n'y naît : une clairière, pas un coin de rue (la vague 3 peuplera les blocs).
    "gens": False,
}
