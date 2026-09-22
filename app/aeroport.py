"""L'aéroport de Baie-des-Brumes : la carte grandit au sud, et elle reste fermée.

Demande de Martin (21 sept. 2026) : « aggrandit la carte au sud avec un autre
pont sur l'ile de droite. ajoute un aéroport. ca doit être bloqué par un pont en
construction et d'autre stratageme pour des missions futures. »

« L'île de droite », c'est La Pointe. L'aéroport est donc une île neuve SOUS La
Pointe, et son pont part de la rue du bord de l'eau — il prolonge la rue qui y
finit en T (`PONT`).

⚠️ **On n'agrandit pas la trame : on ajoute des rangées sous la carte.** Changer
une rangée de la trame re-tire toute la ville (le chenal du 17 sept. 2026 :
vingt-six juges sans rapport tombés d'un coup). L'île se DESSINE, comme
l'Île-aux-Corneilles (`ile.py`) et pour la même raison — c'est un lieu, et les
missions de demain ont besoin que l'aérogare soit à la même place d'une graine à
l'autre. Le plan ci-dessous est la vérité, et `poser` le recopie tuile pour tuile.

⚠️ **Posée EN TOUT DERNIER dans `generer`, sans un dé.** Tout ce qui tire une
place dans une liste de tuiles (les arbres de rue, les paquets, les
nids-de-poule) l'a déjà tirée : la ville d'avant ne bouge pas d'une tuile, ni
d'un décor. Ce qui LIT la ville finie (les lignes d'autobus, les éboueurs, le
traversier) ne la voit pas non plus, et c'est voulu : rien n'y va encore.

⚠️ **Fermé par étages** — chacun seul suffirait, et chacun est une mission à
écrire (`MISSIONS_A_VENIR`) :

1. le PONT EN CONSTRUCTION : une barricade à la tête du pont
   (`carte.BARRIERES`, `pont_aeroport`). Elle se défonce en char, et elle
   s'enjambe à pied — mais…
2. LE CHANTIER : le tablier s'arrête au-dessus de l'eau. Six piles sans rien
   dessus sur trente-deux tuiles, puis le bout du pont côté île. Un char lancé
   finit à l'eau, aucune moto ne saute ça, et à la nage il faut le café ET
   l'estomac plein ;
3. LE BARBELÉ : l'aéroport est clôturé au complet, et le barbelé ne s'enjambe
   pas (`carte.ENJAMBABLES`) ;
4. LA GUÉRITE (`aeroport`) : la seule ouverture de la clôture, au pied du pont.
   Elle ne se force pas ;
5. LE LARGE : de la plage de La Pointe à l'île, trop d'eau pour la nager, même
   avec le café et l'estomac plein. Seul le bout du tablier en laisse la chance.

⚠️ **Et on ne le voit pas venir** (`MASQUE`) : sur la mini-carte et la grande
carte, l'île est de l'eau tant que le pont n'est pas fini.

⚠️ **Pas un refuge** : l'aéroport a sa police (`AEROPORT["police"]`). L'île aux
Corneilles est l'endroit où l'on disparaît ; ici, on est surveillé.
"""

from __future__ import annotations

from . import carte, devantures, ile

#: La fiche de l'aéroport. ⚠️ `x`, `y` : le coin nord-ouest du PLAN en tuiles de
#: ville. `y` est choisi par la mesure : la terre de l'île commence quatre rangées
#: plus bas (258), à 45 tuiles d'eau de la plage de La Pointe — 172 points de
#: souffle avec le café, quand l'estomac plein n'en donne que 160 (`test_aeroport`). `x` met la rue du plan
#: (`ROUTE`) sous la rue de La Pointe que le pont prolonge.
AEROPORT: dict = {
    "slug": "aeroport",
    "nom": "Aéroport de Baie-des-Brumes",
    "x": 222,
    "y": 254,
    # Quelques voyageurs et le personnel ; aucun char ne roule (il n'y a pas une
    # voie dans le champ de direction), et deux agents — ce n'est pas un refuge.
    "pietons": 4,
    "vehicules": 0,
    "police": 2,
    "rythme": (0.3, 0.9, 0.3),
}

#: Le pont de l'aéroport. ⚠️ Il PROLONGE une rue de la trame : `rue_v` est la rue
#: nord-sud de La Pointe qui finit en T sur `rue_h`, la rue du bord de l'eau. Le
#: tablier commence sous le trottoir sud de celle-ci, et il a la coupe d'une rue
#: de la même largeur (`carte._coupe`) — trottoirs en planches, comme l'autre pont.
#:
#: `nord`  les rangées de tablier bâties depuis La Pointe ;
#: `trou`  le chantier : de l'eau, et ses piles ;
#: `piles` les rangées du trou où une pile attend son tablier, relatives au trou —
#:         une toutes les cinq tuiles, trois tuiles d'eau à chaque bout.
#: Le bout côté île va du trou jusqu'à la terre de l'île (le détroit fait 52 tuiles).
#:
#: ⚠️ **Six piles, pas deux** (demande de Martin, 21 sept. 2026 : « ajoute 4 sections
#: de plus de pont en construction », le chantier plus long). Le trou est passé de 12
#: à 32 tuiles, et c'est ce qui change le jeu : à 12, il se nageait à jeun et une moto
#: lancée sur une rampe l'aurait sauté (13 tuiles de réception, `carte.RECEPTION_DEFI`) ;
#: à 32, aucun saut, et la nage demande le café ET l'estomac plein (`test_aeroport`).
#:
#: ⚠️ Aucune FLÈCHE sur le tablier : le champ de direction (`voie`) reste vide, et
#: le trafic ne sait même pas que le pont existe. La mission qui le finit les posera.
PONT: dict = {
    "slug": "pont_aeroport",
    "nom": "Le pont de l'aéroport",
    "rue_v": 19,
    "rue_h": 11,
    "nord": 12,
    "trou": 32,
    "piles": (3, 8, 13, 18, 23, 28),
}

#: ⚠️ **CE QUE LA CARTE NE MONTRE PAS ENCORE** (demande de Martin, 21 sept. 2026 :
#: « la carte de l'aéroport peut-elle être masquée », l'île entière, jusqu'au pont
#: fini). Sur la mini-carte et la grande carte, le rectangle de l'île — bout du pont
#: compris (`terre`) — se peint en eau, et le repère de l'aérogare n'y est pas, tant
#: que la mission `apres` n'est pas faite. `carte_h` : la hauteur de la carte qu'on
#: connaît — la grande carte s'y arrête, et la ville y garde l'échelle qu'elle avait
#: avant l'aéroport (sous elle, il n'y a que de l'eau à montrer). Python décide quoi
#: cacher et jusqu'à quand ; le navigateur (`Monde.masquee`) ne fait que le lire.
MASQUE: dict = {"apres": "a01"}

#: ⚠️ LES MISSIONS QUI OUVRIRONT L'AÉROPORT, ET QUI N'EXISTENT PAS ENCORE. Les deux
#: barrières les attendent (`apres`) : tant qu'elles ne sont pas écrites, la
#: condition ne se remplit jamais et la barrière reste fermée — c'est exactement
#: ce que la demande veut. Le juge des barrières accepte un `apres` d'ici, et
#: d'ici seulement : une faute de frappe dans un slug reste rouge. Le jour où la
#: mission s'écrit, elle sort de cette table (un juge refuse les deux à la fois).
MISSIONS_A_VENIR: dict[str, str] = {
    "a01": "Le pont de l'aéroport — l'entrepreneur est en retard (et quelqu'un le paie pour "
           "l'être) : les travées se posent sur leurs six piles, la barricade tombe, et l'île "
           "apparaît sur la carte",
    "a02": "Le laissez-passer — un badge de l'aéroport, emprunté ou fabriqué : la guérite lève "
           "sa barrière",
}

#: ⚠️ LE PLAN. Une rangée de texte par rangée de tuiles, le nord en haut.
#:
#: Le sol tel quel (`SOLS`) : `~` eau, `,` herbe, `.` dalle, `#` asphalte, `X`
#: barbelé, `p` stationnement, `v` `^` cases (le nez de l'auto). ⚠️ Pas de sable :
#: « moins de plage autour » (Martin) — le sable qui touche le large est une plage
#: DÉCLARÉE (`test_greve`), et personne ne se baigne au pied d'un barbelé.
#: Du `#` au sol, mais qui DIT quelque chose au dessin :
#: `=` la piste (ses marques sont peintes : seuils, axe, 09 et 27, balises),
#: `y` l'axe jaune de la voie de circulation, `@` un avion stationné (`AVIONS`,
#: dans l'ordre de lecture).
#: Le décor PEINT dessus (`PEINTS`) : `a` arbre, `m` manche à air.
#: Les bâtiments (`BATIMENTS`) : une lettre par bâtiment, et `D` sous sa façade
#: là où est sa porte — la fiche dit quelle porte c'est.
#:
#: Au nord-est, la rue qui descend du pont passe la clôture à la guérite et
#: dessert le débarcadère de l'aérogare et son stationnement ; à l'ouest de
#: l'aérogare, l'aire de trafic et ses avions, la tour de contrôle et deux
#: hangars ; au sud, la voie de circulation et la piste 09-27, d'un bout à
#: l'autre de l'île. Tout est dans le barbelé, sauf la ceinture de sable.
PLAN: tuple[str, ...] = (
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~,,,,,,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~,,,,,~~~~~~~,,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,,,,,,,,,~~~~~~,,,,,,~~~~~~~~~~~~~~~~~~~~~,,~~~~~~~~~~,,,,,~~~~~~~~~~",
    "~~~~~~,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.##.,,,,,,,,,,,,~~~~~~",
    "~~~~~,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.##.,,,,,,,,,,,,,~~~~~",
    "~~~~,,XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.##.XXXXXXXXXXXX,,~~~~",
    "~~~~,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.##.,GGG,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,TTTT,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.##.,GDG,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,##############################################################TTTT#######AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,##############################################################TTTT#######AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,##############################################################TTTT#######AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,##############################################################TDTT#######AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,,,,,a,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,#########################################################################AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,##############@################@################@########################AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,#########################################################################AAAAAAAAAAAAAAAAAAAAAAAAAA,,,,,,,.##.,,a,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHHHHHHHHHHHHHH,,,,NNNNNNNNNNNNNNNNNNNNNN,,,,#########################################################################AAAAAAAAAAAADAAAAAAAAAAAAA,,,,,,,.##.,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,HHHHHHHHHHHDHHHHHHHHHHHH,,,,NNNNNNNNNNDNNNNNNNNNNN,,,,#######################################################################....................................##.,,,,,,,,,a,X,,~~~~",
    "~~~~,,X,,,,,############################################################################################################################,....................................##.,,,,,,,,,,,X,,,~~~",
    "~~~~,,X,,,,,############################################################################################################################,,,####################################.,,,,,,,,,,,X,,,~~~",
    "~~~~,,X,,,,,############################################################################################################################,,,####################################.,,,,,,,,,,,X,,,~~~",
    "~~~~,,X,,,,,############################################################################################################################,....................................##.,,,,,,,,,,,X,,,~~~",
    "~~~~,,X,,,,,############################################################################################################################,.pppppppppppppppppppppppppppppppppp,,,,,,,,,,,,,,,X,,,~~~",
    "~~~~,,X,,,,,############################################################################################################################,.ppvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvpp,,a,,,,,,,,,a,,X,,,~~~",
    "~~~~,,X,,,,,############################################################################################################################,.ppvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvpp,,,,,,,,,,,,,,,X,,,~~~",
    "~~~,,,X,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#y#,.pp^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^pp,,,,,,,,a,,,,,,X,,,~~~",
    "~~~,,,X,,,,,#y########################################################################################################################y#,.pp^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^pp,,,,,,,,,,,,,,,X,,,~~~",
    "~~~,,,X,,,,,#yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy#,.pppppppppppppppppppppppppppppppppp,,,,a,,,,,,,,,,X,,,~~~",
    "~~~,,,X,,,,,#y########################################################################################################################y#,.,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~,,,X,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~,,,X,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,m,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~,,,X,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~,,,X,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#y#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~,,,X,,,,===============================================================================================================================================================================,X,,~~~~",
    "~~~,,,X,,,,===============================================================================================================================================================================,X,,~~~~",
    "~~~~,,X,,,,===============================================================================================================================================================================,X,,~~~~",
    "~~~~,,X,,,,===============================================================================================================================================================================,X,,~~~~",
    "~~~~,,X,,,,===============================================================================================================================================================================,X,,~~~~",
    "~~~~,,X,,,,===============================================================================================================================================================================,X,,~~~~",
    "~~~~,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~~,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,X,,~~~~",
    "~~~~,,XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,,~~~~",
    "~~~~~,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,~~~~~",
    "~~~~~~,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,~~~~~~",
    "~~~~~~~~~~,,,,,,,~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~,,~~~~~~~~~~~~~~,,,,,,~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
)

#: Les glyphes du plan qui sont du sol tel quel.
SOLS = frozenset("~,.#Xpv^")
#: Les glyphes du plan qui sont de l'asphalte au sol, et une marque au dessin.
PISTE, AXE, AVION = "=", "y", "@"
MARQUES = frozenset((PISTE, AXE, AVION))

#: Les glyphes qui PEIGNENT un décor, et le sol qu'il y a dessous.
#:
#: ⚠️ **PEINT, pas posé** : un arbre de l'aéroport n'est pas une entité. Le jeu crée
#: tout le décor de la ville au chargement, dans l'ordre de la liste, et chaque
#: entité prend un numéro ; quinze de plus au bout décalaient le numéro de tous
#: les passants et de tous les chars nés ensuite, donc les dés — cinq juges sans
#: rapport (les vélos, le petit train, le clignotant, la plage qui ferme,
#: l'arroseuse) sont tombés, chacun selon le compte exact. Personne ne peut encore
#: s'en approcher : la mission qui ouvrira l'aéroport en fera du vrai décor, et
#: ses juges avec. `aeroport.js` les peint avec le dessin du jeu (`DECORS`).
PEINTS: dict[str, tuple[str, str]] = {
    "a": (",", "arbre"),
    "m": (",", "manche_a_air"),
}

#: La porte d'un bâtiment, sous sa façade.
PORTE = "D"

#: Les bâtiments, par leur lettre au plan.
#:
#: `toit`      la couverture (`carte.LEGENDE`) ;
#: `facade`    ce qu'est une tuile de façade : `F` (un mur) ou un motif qui se
#:             répète (`FWW` : un pilier, deux vitres) ;
#: `porte`     `lieu` (on entre, et c'est un repère de la carte) ou `condamnee` ;
#: `enseigne`  la largeur, en tuiles, du bandeau au-dessus de la porte — son nom
#:             est celui de `devantures.ENSEIGNES`, et cinq tuiles au plus, comme
#:             toutes les enseignes (`carte._Chantier.ENSEIGNE_ETIREE`) ;
#: `rideau`    la largeur de la porte peinte d'un bâtiment fermé (le rideau de
#:             tôle d'un hangar en fait trois) ;
#: `toitures`  ce que le toit porte (`FACADES.TOITURES`, sprites.js), en tuiles
#:             relatives au coin nord-ouest du bâtiment.
#:
#: ⚠️ Tout est condamné sauf l'aérogare : la tour, les hangars et la guérite ont
#: leur porte peinte et fermée. On y entrera quand une mission l'écrira.
BATIMENTS: dict[str, dict] = {
    "A": {"toit": "O", "facade": "FWW", "porte": "lieu", "slug": "aeroport",
          "nom": "Aéroport de Baie-des-Brumes", "interieur": "aerogare", "famille": "transport",
          "enseigne": 5,
          "toitures": ((3, 1, "clim"), (9, 2, "ventilation"), (15, 1, "clim"), (21, 3, "clim"),
                       (24, 1, "antenne"))},
    "T": {"toit": "O", "facade": "F", "porte": "condamnee",
          "toitures": ((1, 1, "tour_controle"),)},
    "H": {"toit": "B", "facade": "F", "porte": "condamnee", "rideau": 3,
          "toitures": ((5, 2, "ventilation"), (17, 4, "ventilation"))},
    "N": {"toit": "B", "facade": "F", "porte": "condamnee", "rideau": 3,
          "toitures": ((8, 3, "ventilation"),)},
    "G": {"toit": "O", "facade": "W", "porte": "condamnee", "toitures": ()},
}

#: Les avions stationnés, dans l'ordre de lecture des `@` du plan. ⚠️ PEINTS,
#: pas des véhicules : personne ne peut encore s'en approcher, et un avion qu'on
#: vole est une mission — le jour où elle s'écrit, ils entrent au catalogue des
#: véhicules comme le chalutier y est entré. `cap` : où pointe le nez.
AVIONS: tuple[dict, ...] = (
    {"modele": "bimoteur", "livree": "brumes", "cap": "N"},
    {"modele": "bimoteur", "livree": "gaspesie", "cap": "N"},
    {"modele": "monomoteur", "livree": "aeroclub", "cap": "N"},
)

#: Les balises de la piste : une tous les tant de tuiles, sur les deux bords.
#: ⚠️ Ce sont des LAMPES (`sorte: balise`) : la nuit, la piste se lit de La Pointe.
BALISES_TOUS_LES = 8

#: La pièce de l'aérogare. ⚠️ À la mesure de son bâtiment, murs compris : 26 × 8
#: dehors, donc 28 × 10 dedans, et la porte en face de la sienne.
#: Les comptoirs d'enregistrement et leurs commis, deux rangées de sièges, le
#: carrousel à bagages, les deux portiques de sécurité, deux machines. Personne
#: n'y entre encore : c'est la pièce que les missions de l'arc A attendent.
PIECES: dict[str, dict] = {
    "aerogare": carte._piece("aerogare", "Aéroport de Baie-des-Brumes", sol="u", plan="""
BBBBWWWWWBBBBBBBBBBWWWWWBBBB
B                    e e ejB
B cccccc  cccccc           B
B                          B
B   hhhhh   hhhhh   mmmm  nB
B                   mmmm   B
B   hhhhh   hhhhh     b  b B
Bn                         B
B      mm         mm      nB
BBBBBBBBBBBBBDBBBBBBBBBBBBBB
""", points=(carte._pt("distributrice", 22, 6, sorte="liqueur"),
             carte._pt("distributrice", 25, 6, sorte="cafe")),
        gens=carte._gens(("commis", 3, 1), ("commis", 11, 1), ("client", 6, 3), ("client", 14, 7))),
}


def boite() -> tuple[int, int, int, int]:
    """Le rectangle du plan, en tuiles de ville : x, y, largeur, hauteur."""
    return AEROPORT["x"], AEROPORT["y"], len(PLAN[0]), len(PLAN)


def _batiments() -> dict[str, set[tuple[int, int]]]:
    """Les tuiles de chaque bâtiment, relatives au plan, portes comprises."""
    tuiles: dict[str, set[tuple[int, int]]] = {}
    for y, ligne in enumerate(PLAN):
        for x, glyphe in enumerate(ligne):
            if glyphe in BATIMENTS:
                tuiles.setdefault(glyphe, set()).add((x, y))
    for y, ligne in enumerate(PLAN):
        for x, glyphe in enumerate(ligne):
            if glyphe == PORTE:
                tuiles[PLAN[y - 1][x]].add((x, y))
    return tuiles


def _colonne_de_la_route() -> int:
    """La colonne du plan où la rue du pont touche la terre : le premier
    `.##.` du plan (trottoir, deux voies, trottoir). Le plan la DESSINE ; le
    pont vérifie qu'elle tombe sous sa rue (`poser`)."""
    for ligne in PLAN:
        if ".##." in ligne:
            return ligne.index(".##.")
    raise ValueError("aéroport : le plan n'a pas de rue")


def _verifier_le_plan() -> None:
    """Le plan se juge au chargement du module, comme celui de l'île.

    ⚠️ Un glyphe inconnu, une rangée trop courte, une porte sous rien, un
    bâtiment qui n'est pas un rectangle, un nombre d'`@` qui n'est pas celui
    d'`AVIONS` : ça lève ICI, avant le premier test.
    """
    largeur = len(PLAN[0])
    connus = SOLS | MARQUES | set(PEINTS) | set(BATIMENTS) | {PORTE}
    for y, ligne in enumerate(PLAN):
        if len(ligne) != largeur:
            raise ValueError(f"aéroport : la rangée {y} fait {len(ligne)} tuiles au lieu de {largeur}")
        inconnus = set(ligne) - connus
        if inconnus:
            raise ValueError(f"aéroport : glyphes inconnus {sorted(inconnus)} rangée {y}")
    if set(PLAN[0] + PLAN[-1]) != {"~"} or any(ligne[0] != "~" or ligne[-1] != "~" for ligne in PLAN):
        raise ValueError("aéroport : de la terre sur le pourtour du plan")
    for y, ligne in enumerate(PLAN):
        for x, glyphe in enumerate(ligne):
            if glyphe == PORTE and PLAN[y - 1][x] not in BATIMENTS:
                raise ValueError(f"aéroport : une porte en {(x, y)} sous aucun bâtiment")
    for lettre, tuiles in _batiments().items():
        xs = [t[0] for t in tuiles]
        ys = [t[1] for t in tuiles]
        if len(tuiles) != (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1):
            raise ValueError(f"aéroport : le bâtiment {lettre} n'est pas un rectangle")
        portes = [t for t in tuiles if PLAN[t[1]][t[0]] == PORTE]
        if len(portes) != 1 or portes[0][1] != max(ys):
            raise ValueError(f"aéroport : le bâtiment {lettre} doit avoir une porte, sous sa façade")
        fiche = BATIMENTS[lettre]
        if fiche["porte"] == "lieu":
            piece = PIECES[fiche["interieur"]]
            if (piece["largeur"], piece["hauteur"]) != (max(xs) - min(xs) + 3, max(ys) - min(ys) + 3):
                raise ValueError(f"aéroport : la pièce {fiche['interieur']} n'a pas les mesures de son bâtiment")
            if piece["sortie"]["x"] != portes[0][0] - min(xs) + 1:
                raise ValueError(f"aéroport : la porte de {fiche['interieur']} n'est pas en face de la sienne")
    avions = sum(ligne.count(AVION) for ligne in PLAN)
    if avions != len(AVIONS):
        raise ValueError(f"aéroport : {avions} avions au plan, {len(AVIONS)} dans la fiche")
    if not set(MISSIONS_A_VENIR) or any(not s.startswith("a") for s in MISSIONS_A_VENIR):
        raise ValueError("aéroport : les missions à venir sont celles de l'arc A")
    if not all(0 < r < PONT["trou"] - 1 for r in PONT["piles"]):
        raise ValueError("aéroport : une pile hors du chantier")


_verifier_le_plan()

#: La colonne de la rue, dans le plan.
ROUTE = _colonne_de_la_route()


def _rect_de(glyphe: str) -> tuple[int, int, int, int]:
    """Le rectangle (x, y, l, h) d'un glyphe du plan, en tuiles de ville."""
    x0, y0 = AEROPORT["x"], AEROPORT["y"]
    cases = [(i, j) for j, ligne in enumerate(PLAN) for i, g in enumerate(ligne) if g == glyphe]
    xs = [c[0] for c in cases]
    ys = [c[1] for c in cases]
    return x0 + min(xs), y0 + min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


def _segments_de(glyphe: str) -> list[list[int]]:
    """Les tuiles d'un glyphe, en SEGMENTS [x0, y0, x1, y1] : les rangées d'abord,
    puis les colonnes de ce qui reste seul dans sa rangée. Moins d'octets dans le
    paquet qu'une liste de tuiles, et le dessin trace une ligne par segment."""
    x0, y0 = AEROPORT["x"], AEROPORT["y"]
    cases = {(i, j) for j, ligne in enumerate(PLAN) for i, g in enumerate(ligne) if g == glyphe}
    segments, prises = [], set()
    for j, ligne in enumerate(PLAN):
        i = 0
        while i < len(ligne):
            if (i, j) in cases and (i + 1, j) in cases:
                debut = i
                while (i + 1, j) in cases:
                    i += 1
                segments.append([x0 + debut, y0 + j, x0 + i, y0 + j])
                prises |= {(k, j) for k in range(debut, i + 1)}
            i += 1
    for i in range(len(PLAN[0])):
        j = 0
        while j < len(PLAN):
            if (i, j) in cases and (i, j) not in prises:
                debut = j
                while (i, j + 1) in cases and (i, j + 1) not in prises:
                    j += 1
                segments.append([x0 + i, y0 + debut, x0 + i, y0 + j])
            j += 1
    return segments


def zones(hauteur_avant: int, largeur: int) -> list[dict]:
    """Le large (les rangées d'eau neuves) puis l'aéroport — dans cet ordre :
    `Monde.zoneA` garde la dernière zone qui contient le point.

    ⚠️ La zone de l'aéroport part du BOUT DU PONT côté île, pas du plan : celui
    qui a nagé la travée manquante est déjà chez eux."""
    tx, ty, tl, th = terre()
    large = {"slug": "large", "nom": "Le large", "district": "baie",
             "x": 0, "y": hauteur_avant, "l": largeur, "h": AEROPORT["y"] + len(PLAN) - hauteur_avant,
             "gang": None, "brume": False, "pietons": 0, "vehicules": 0, "police": 0,
             "rythme": [1.0, 1.0, 1.0], "rares": []}
    aeroport = {"slug": AEROPORT["slug"], "nom": AEROPORT["nom"], "district": AEROPORT["slug"],
                "x": tx, "y": ty, "l": tl, "h": th,
                "gang": None, "brume": False, "pietons": AEROPORT["pietons"],
                "vehicules": AEROPORT["vehicules"], "police": AEROPORT["police"],
                "rythme": list(AEROPORT["rythme"]), "rares": []}
    return [large, aeroport]


def terre() -> tuple[int, int, int, int]:
    """Le rectangle de la terre de l'aéroport : le plan, et le bout du pont côté
    île au-dessus. Un groupe marchable qui y tient entier est de l'aéroport
    (`carte.composantes_par_terre`)."""
    x0, y0, largeur, hauteur = boite()
    debut_sud = _pont_y0() + PONT["nord"] + PONT["trou"]
    return x0, debut_sud, largeur, y0 + hauteur - debut_sud


def _pont_y0() -> int:
    """La première rangée du tablier : sous le trottoir sud de `rue_h`."""
    return sum(carte.RUES_H[k] + carte.RANGEES[k] for k in range(PONT["rue_h"])) + carte.RUES_H[PONT["rue_h"]]


def _pont_x0() -> int:
    """La première colonne du tablier : celle de `rue_v`."""
    return sum(carte.RUES_V[k] + carte.COLONNES[k] for k in range(PONT["rue_v"]))


def poser(chantier, ville: dict) -> dict:
    """Pose l'aéroport et son pont sous la ville déjà bâtie. Rend sa fiche pour le paquet.

    ⚠️ Lève ValueError si le pont ne part pas d'un trottoir, s'il passe ailleurs
    que sur l'eau, ou si sa rue ne tombe pas sur celle du plan : le jour où la
    rive de La Pointe bouge, on le sait à la construction.
    """
    x0, y0, largeur, hauteur = boite()
    hauteur_avant = chantier.hauteur
    if y0 <= hauteur_avant:
        raise ValueError("aéroport : le plan doit commencer sous la carte")

    # 1. La carte grandit au sud : de l'eau jusqu'au bas du plan.
    for _ in range(y0 + hauteur - hauteur_avant):
        chantier.sol.append(["~"] * chantier.largeur)
        chantier.voie.append(["."] * chantier.largeur)
        chantier.bouchon.append(["B"] * chantier.largeur)
    chantier.hauteur = y0 + hauteur

    # 2. Le pont : la coupe d'une rue de sa largeur, sur l'eau, sauf le trou.
    px, py = _pont_x0(), _pont_y0()
    coupe = carte._coupe(carte.RUES_V[PONT["rue_v"]], True)
    if px != x0 + ROUTE:
        raise ValueError(f"aéroport : la rue du plan ({x0 + ROUTE}) n'est pas sous le pont ({px})")
    if any(chantier.sol[py - 1][px + d] != "." for d in range(len(coupe))):
        raise ValueError("aéroport : le pont ne part pas du trottoir de La Pointe")
    debut_sud = py + PONT["nord"] + PONT["trou"]
    fin = y0 + next(j for j, ligne in enumerate(PLAN) if ligne[ROUTE] != "~")
    dessous: dict[tuple[int, int], str] = {}
    for y in range(py, fin):
        if PONT["nord"] <= y - py < PONT["nord"] + PONT["trou"]:
            continue
        for d, (glyphe, _fleche) in enumerate(coupe):
            # ⚠️ De l'eau, ou le SABLE de la rive : d'une graine à l'autre, la plage
            # de La Pointe descend parfois jusque sous le tablier (graines 3, 7, 777).
            if chantier.sol[y][px + d] not in RIVE:
                raise ValueError(f"aéroport : le pont passe sur autre chose que l'eau en {(px + d, y)}")
            dessous[(px + d, y)] = chantier.sol[y][px + d]
            chantier.sol[y][px + d] = "Q" if glyphe == "." else glyphe
    _degager_le_pied(chantier, ville, dessous, px, len(coupe))
    piles = [[px + d, py + PONT["nord"] + r] for r in PONT["piles"] for d in (0, len(coupe) - 1)]

    # 3. Le plan : le sol d'abord, les bâtiments, puis le décor.
    for j, ligne in enumerate(PLAN):
        for i, glyphe in enumerate(ligne):
            x, y = x0 + i, y0 + j
            if glyphe == "~" and chantier.sol[y][x] != "~":
                continue                       # le bout du pont, déjà posé
            if glyphe in SOLS:
                chantier.sol[y][x] = glyphe
            elif glyphe in MARQUES:
                chantier.sol[y][x] = "#"
            elif glyphe in PEINTS:
                chantier.sol[y][x] = PEINTS[glyphe][0]
    # ⚠️ LA LISTE DU DÉCOR DE LA VILLE EST LA VÉRITÉ, ici : le lot du poste et la
    # porte du garage (`poser_les_lots_et_les_rideaux`) dégagent leur devant en
    # RÉASSIGNANT celle du chantier, et c'est celle de la ville que les étapes
    # suivantes ont tenue à jour. On la rend au chantier : le pied du pont y
    # déplace ce qui traîne (l'île l'a mesuré : une liste détachée, 337 décors perdus).
    chantier.decor = ville["decor"]
    for liste, cle in ((chantier.portes, "portes"), (chantier.lampes, "lampes"), (chantier.toits, "toits"),
                       (chantier.points, "points_interet"), (chantier.devantures, "devantures")):
        if ville[cle] is not liste:
            raise ValueError(f"aéroport : la liste « {cle} » du chantier n'est plus celle de la ville")
    tuiles = _batiments()
    lampes_avant = len(chantier.lampes)
    portes_peintes: list[list[int]] = []
    for lettre in sorted(tuiles):
        _batir(chantier, lettre, tuiles[lettre], portes_peintes)
    peints = [[PEINTS[g][1], x0 + i, y0 + j] for j, ligne in enumerate(PLAN) for i, g in enumerate(ligne)
              if g in PEINTS]
    piste = _rect_de(PISTE)
    balises = []
    for x in range(piste[0], piste[0] + piste[2], BALISES_TOUS_LES):
        for y in (piste[1], piste[1] + piste[3] - 1):
            balises.append([x, y])
            chantier.lampes.append({"x": x, "y": y, "r": 14, "c": "balise"})
    avions = [{**fiche, "x": x0 + i, "y": y0 + j}
              for fiche, (i, j) in zip(AVIONS, [(i, j) for j, ligne in enumerate(PLAN)
                                                for i, g in enumerate(ligne) if g == AVION])]

    # 4. La ville : ses rangées (les neuves, et celles que le pont traverse), ses
    # listes. ⚠️ Même règle que l'île : la ville et le chantier partagent leurs
    # LISTES, et on n'en réassigne aucune.
    for y in range(py, hauteur_avant):
        ville["sol"][y] = "".join(chantier.sol[y])
    for y in range(hauteur_avant, chantier.hauteur):
        ville["sol"].append("".join(chantier.sol[y]))
        ville["voie"].append("".join(chantier.voie[y]))
    ville["hauteur"] = chantier.hauteur
    ville["interieurs"].update(PIECES)
    ville["zones"].extend(zones(hauteur_avant, chantier.largeur))
    ville["barrieres"].extend(_barrieres(px, py, len(coupe)))
    tx, ty, tl, th = terre()
    return {"slug": AEROPORT["slug"], "nom": AEROPORT["nom"], "x": tx, "y": ty, "l": tl, "h": th,
            "plan": [x0, y0, largeur, hauteur],
            "piste": {"x": piste[0], "y": piste[1], "l": piste[2], "h": piste[3]},
            "axes": _segments_de(AXE), "avions": avions, "balises": balises,
            "peints": peints, "portes_peintes": portes_peintes,
            "pont": {"x": px, "y": py, "l": len(coupe), "nord": PONT["nord"], "trou": PONT["trou"],
                     "sud": fin - debut_sud, "piles": piles},
            "masque": {"x": tx, "y": ty, "l": tl, "h": th, "apres": MASQUE["apres"], "carte_h": hauteur_avant},
            "lampes": len(chantier.lampes) - lampes_avant}


#: Ce qu'un tablier a le droit de recouvrir : l'eau, et le sable de la rive.
RIVE = frozenset("~s")


def _degager_le_pied(chantier, ville: dict, dessous: dict[tuple[int, int], str], px: int, large: int) -> None:
    """Le pied d'un pont n'est pas une plage : ce qui traînait sous le tablier — ou
    juste à côté, dans l'élan d'un char qui en descend — déménage sur la tuile libre
    la plus proche de la même nature : le sable pour une serviette, l'eau pour une
    bouée.

    ⚠️ DÉPLACÉ, pas retiré : la liste du décor garde sa longueur et son ordre (la
    leçon de `devants.py`). Sans un dé : la plus proche en anneaux, dans l'ordre de
    lecture. Sur la ville livrée, il n'y a rien à déplacer.
    """
    rangees = {y for _, y in dessous}
    pied = set(dessous) | {(x, y) for y in rangees for x in (px - 1, px + large)}
    for d in ville["decor"]:
        if (d["x"], d["y"]) not in pied:
            continue
        nature = dessous.get((d["x"], d["y"])) or chantier.sol[d["y"]][d["x"]]
        place = None
        for r in range(1, 12):
            anneau = [(d["x"] + i, d["y"] + j) for j in range(-r, r + 1) for i in range(-r, r + 1)
                      if max(abs(i), abs(j)) == r]
            libres = [(x, y) for x, y in sorted(anneau, key=lambda t: (t[1], t[0]))
                      if 0 <= y < chantier.hauteur and 0 <= x < chantier.largeur
                      and chantier.sol[y][x] == nature and not px - 2 <= x < px + large + 2
                      and (x, y) not in chantier.occupe and (x, y) not in chantier.reserve]
            if libres:
                place = libres[0]
                break
        if place is None:
            raise ValueError(f"aéroport : le {d['type']} du pied du pont n'a nulle part où aller")
        chantier.occupe.discard((d["x"], d["y"]))
        chantier.occupe.add(place)
        d["x"], d["y"] = place


def _barrieres(px: int, py: int, large: int) -> list[dict]:
    """Les deux barrières de l'aéroport, résolues en rectangles de tuiles.

    ⚠️ La fiche vit dans `carte.BARRIERES` (une barrière est une fiche, pas un
    cas) ; `carte._Chantier.barrieres` les saute, et c'est ICI qu'elles se
    résolvent — le pont et la guérite n'existent qu'une fois l'aéroport posé.
    """
    x0, y0 = AEROPORT["x"], AEROPORT["y"]
    cloture = next(j for j, ligne in enumerate(PLAN) if "X" in ligne)
    ou = {"pont": (px, py, large, 1), "guerite": (x0 + ROUTE, y0 + cloture, large, 1)}
    sortie = []
    for fiche in carte.BARRIERES:
        cle = fiche["ou"].get("aeroport")
        if not cle:
            continue
        x, y, largeur, hauteur = ou[cle]
        sortie.append({"slug": fiche["slug"], "nom": fiche["nom"], "x": x, "y": y, "l": largeur, "h": hauteur,
                       "arrete": list(fiche["arrete"]), "condition": dict(fiche["condition"]),
                       "forcer": dict(fiche["forcer"]) if fiche["forcer"] else None,
                       "raison": fiche["raison"], "decor": fiche.get("decor"),
                       "existant": bool(fiche.get("existant")),
                       "prix": fiche.get("prix"), "dedans": fiche.get("dedans")})
    return sortie


def _poser_l_enseigne(chantier, fiche: dict, px: int, py: int, gauche: int, large: int) -> None:
    """Le bandeau et son nom au-dessus de la porte, comme une devanture de la ville
    (`carte._Chantier.poser_devanture`) — mais SANS UN DÉ : centré sur la porte, pas
    de pancarte, les piliers sous le bandeau deviennent des vitres, et sa lampe."""
    texte, genre = devantures.enseigne_speciale(fiche["slug"], fiche["nom"])
    bandeau = fiche["enseigne"]
    if not devantures.tient_en(texte, bandeau, carte.TUILE_PX):
        raise ValueError(f"aéroport : « {texte} » ne tient pas sur {bandeau} tuiles")
    x0 = min(max(px - bandeau // 2, gauche), gauche + large - bandeau)
    for i in range(bandeau):
        if chantier.sol[py][x0 + i] == "F":
            chantier.sol[py][x0 + i] = "W"
    chantier.devantures.append({"x": x0, "y": py, "l": bandeau, "genre": genre, "texte": texte, "pancarte": 0,
                                "motifs": "".join(chantier.sol[py][x0 + i] for i in range(bandeau)), "porte": 1})
    # Une vitrine éclaire son trottoir, la nuit : la même lueur que les commerces.
    chantier.lampes.append({"x": x0 + bandeau // 2, "y": py + 1, "r": 20 + 4 * bandeau, "c": "vitrine"})
    for i in range(bandeau):
        chantier.murs_tagges.add((x0 + i, py))


def _batir(chantier, lettre: str, relatives: set[tuple[int, int]], portes_peintes: list[list[int]]) -> None:
    """Un bâtiment de l'aéroport : son toit, sa façade, sa porte, ce que son toit porte.

    ⚠️ La règle de `ile._batir` — une tuile dont la voisine du sud n'est pas au
    bâtiment est une façade —, sans un dé. Et pas dans `chantier.batiments` :
    c'est la liste où les chantiers choisissent quoi démolir.

    ⚠️ Une porte CONDAMNÉE est PEINTE (`portes_peintes`, dessinée par
    `aeroport.js`), pas un `d` au sol : le jeu tire au hasard dans toutes les
    portes `d` de la ville (`carte.portesFermees`, d'où sortent les passants), et
    quatre de plus au bout de la liste changeaient la porte tirée partout ailleurs.
    Seule l'aérogare a une vraie porte.
    """
    fiche = BATIMENTS[lettre]
    x0, y0 = AEROPORT["x"], AEROPORT["y"]
    tuiles = {(x0 + x, y0 + y) for x, y in relatives}
    gauche = min(t[0] for t in tuiles)
    haut = min(t[1] for t in tuiles)
    for tx, ty in sorted(tuiles):
        if (tx, ty + 1) in tuiles:
            chantier.sol[ty][tx] = fiche["toit"]
        else:
            motif = fiche["facade"]
            chantier.sol[ty][tx] = motif[(tx - gauche) % len(motif)]
    for dx, dy, sorte in fiche["toitures"]:
        chantier.toits.append({"x": gauche + dx, "y": haut + dy, "type": sorte})
    px, py = next((x0 + x, y0 + y) for x, y in relatives if PLAN[y][x] == PORTE)
    large = max(t[0] for t in tuiles) - gauche + 1
    if fiche["porte"] == "lieu":
        chantier.sol[py][px] = "D"
        chantier.portes.append({"x": px, "y": py, "interieur": fiche["interieur"], "lieu": fiche["slug"],
                                "vitrine": [gauche, large]})
        chantier.points.append({"type": fiche["slug"], "slug": fiche["slug"], "nom": fiche["nom"],
                                "x": px, "y": py + 1, "famille": fiche["famille"]})
        if fiche.get("enseigne"):
            _poser_l_enseigne(chantier, fiche, px, py, gauche, large)
    else:
        chantier.sol[py][px] = fiche["facade"][(px - gauche) % len(fiche["facade"])]
        portes_peintes.append([px, py, fiche.get("rideau", 1)])
    ile._reserver_le_devant(chantier, px, py)
