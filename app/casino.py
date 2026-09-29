"""Le casino du Dragon d'or, au Petit-Canton (docs/jalons/le-casino-du-petit-canton.md).

Martin (28 sept. 2026) : « je veux un grand casino dans le quartier Petit-Canton » — un casino légal qu'on
voit de la rue ET un tripot au sous-sol ; les machines à sous, le blackjack, la roulette et le vidéopoker ; la
maison gagne, mais on peut tricher. La place, il me l'a laissée.

⚠️ **LA PLACE : l'îlot juste au nord de la place du marché**, deux colonnes fusionnées sur UNE rangée
(`nord.DISTRICTS_NORD`, la lettre `CASINO_DU_PLAN`). Pas deux rangées : un lieu garanti se pose dans la bande
la plus PROFONDE de son îlot et ouvre sur son devant — dans un îlot de deux rangées, la bande du nord
l'emporte et sa porte donnait sur la ruelle de l'autre. Sur une rangée, sa façade de trente-deux tuiles
regarde la rue qui longe la place, et la place devient son parvis, fontaine comprise.

⚠️ **UN LIEU GARANTI DE LA BANDE, PAS DE `SPECIAUX`** : la ville d'avant n'en sait rien. La lettre a son
bâtisseur (`nord._ChantierNord.BATISSEURS`), qui appelle le bâtisseur des lieux garantis de la ville avec
cette fiche ; l'îlot se bâtit avec SES dés, comme tout le Petit-Canton (`_a_ses_des`). Le slug commence par
`nord_`, comme tout ce que la bande nomme (`test_nord`).

⚠️ **LA SALLE À LA MESURE DU BÂTIMENT** : trente-deux tuiles sur neuf, murs en plus (`test_carte`, la pièce
a les mesures de son bâtiment). Le bâtiment se taille à elle (`_ilot_bati` lit ses mesures dans les pièces
du chantier, où `nord.batir_la_bande` la pose avant de bâtir).
"""

from __future__ import annotations

from . import carte, tripot

#: La lettre du casino dans le plan du Petit-Canton (`nord.DISTRICTS_NORD`). ⚠️ Pas une lettre de
#: `SPECIAUX` : c'est un bâtisseur de la bande. Un symbole peu courant, pour qu'aucune autre session ne la
#: prenne pour un de ses lieux (« Glyphes libres disputés entre sessions »).
CASINO_DU_PLAN = "¤"

#: Les cinq tables de la salle (vague 2) : leur jeu, et la colonne du milieu de leur feutre — le croupier s'y
#: tient au nord, le point d'ACTION est sur le bord sud.
TABLES: tuple[tuple[str, int], ...] = (("blackjack", 4), ("roulette", 11), ("poker", 17), ("baccara", 23),
                                       ("sic_bo", 29))

#: La fiche du lieu garanti, au format de `carte.SPECIAUX`.
CASINO: dict = {"slug": "nord_casino", "nom": "Casino du Dragon d'or", "interieur": "nord_casino",
                "famille": "repere"}

#: LA GRANDE SALLE. Le long du mur du nord, huit machines à sous (`$`) et quatre vidéopokers (`S`), un
#: tabouret (`h`) entre deux ; le bar du fond (`c`). Au milieu, les CINQ TABLES (`!`, vague 2 :
#: `tables_de_jeu.py`), d'ouest en est le blackjack, la roulette, le poker à trois cartes, le baccara et le sic
#: bo — le croupier derrière, au nord, le joueur devant, au sud, où ACTION attrape le point posé sur le bord du
#: feutre. Et au sud, deux îlots de cinq machines, loin de la porte. ⚠️ UNE MACHINE SUR DEUX TUILES, et deux
#: tables jamais collées (deux blocs du même glyphe se peindraient comme un seul) : deux tuiles entre elles.
#: ⚠️ La salle garde ses 32 × 9 : la grossir ferait glisser la ville (« Grossir un lieu garanti »).
#: ⚠️ VAGUE 4 : le coin du sud-est est muré d'un pan (`B`) et cache l'ESCALIER du sous-sol (`/`), derrière la
#: porte que garde un gros bras (`PIECE["barrieres"]`) ; Irène Lam se tient au bout du bar (`point:irene`).
PIECE = carte._piece("nord_casino", "Casino du Dragon d'or", sol="u", plan="""
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
B$h$h$h$h$h$h$h$ ShShShS  ccccc nB
B                                B
Bn                              nB
B !!!!!  !!!!!  !!!  !!!!!  !!!  B
B !!!!!  !!!!!  !!!  !!!!!  !!!  B
B                                B
B                                B
B  $h$h$h$h$         $h$h$h$h$ B B
Bn                             B/B
BBBBBBBBBBBBBBWWDWWBBBBBBBBBBBBBBB
""", points=tuple([carte._pt("machine_a_sous", x, 1) for x in range(1, 16, 2)]
                  + [carte._pt("machine_a_sous", x, 8) for x in (3, 5, 7, 9, 11, 21, 23, 25, 27, 29)]
                  + [carte._pt("videopoker", x, 1) for x in (17, 19, 21, 23)]
                  + [carte._pt(jeu, x, 5) for jeu, x in TABLES]
                  # Vague 4 : Irène Lam au bout du bar, et l'escalier du sous-sol, dans son coin.
                  + [carte._pt("irene", 31, 1), carte._pt("escalier", 32, 9, vers=tripot.PIECE["slug"], descend=True)]),
    gens=carte._gens(*[("croupier", x, 3) for _, x in TABLES],
                     ("client", 6, 7), ("client", 20, 2), ("client", 25, 9), ("commis", 28, 2),
                     ("gros_bras", 31, 7)))

#: ⚠️ LA PORTE DU SOUS-SOL (vague 4) : une barrière de la pièce (`tripot.PORTE`), sur la tuile qui mène à
#: l'escalier — fermée tant que la mission d'Irène n'est pas faite. Un gros bras du Pouce la garde.
PIECE["barrieres"] = [dict(tripot.PORTE)]


def batir(ch, x: int, y: int, largeur: int, hauteur: int) -> None:
    """Le bâtisseur de la lettre `CASINO_DU_PLAN` : le lieu garanti de la ville, avec la fiche du casino."""
    ch._ilot_bati(x, y, largeur, hauteur, genre="commerces", special=CASINO)
