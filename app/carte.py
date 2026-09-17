"""La carte de Baie-des-Brumes — un plan de blocs, des gabarits, un generateur.

Le Faubourg n'est pas dessine tuile par tuile : il est DECRIT par un plan de
blocs et rebati par `generer(plan, graine)`. Six lignes qu'on relit d'un coup
d'oeil valent mieux que 112 lignes de 157 glyphes.

    minuscule = quartier ordinaire   c commerces · h habitations · g gang
                                     p parc · o place · q quai · ~ eau
                                     j quai SUR l'eau (il a avale la baie)
    MAJUSCULE = batiment garanti     T terminus · M armurerie · A vetements
                                     G garage · K planque · P poste · H hopital
                                     B bar · C casse-croute
    < et ^    = ce bloc est AVALE par son voisin de l'ouest ou du nord

⚠️ **Rien n'est regulier, et c'est voulu.** Une ville en damier parfait n'a pas
de reperes : tous les coins s'y ressemblent et on s'y perd sans jamais la
connaitre. Trois sources d'irregularite se combinent ici :

1. **La trame** : chaque colonne de blocs a sa largeur, chaque rangee sa
   hauteur, chaque rue sa largeur (8 = boulevard a 4 voies, 6 = rue a 2 voies).
2. **Les superblocs** : `<` et `^` fusionnent des blocs, ce qui EFFACE la rue
   entre eux — d'ou des rues qui s'arretent en T, un parc a cheval sur deux
   blocs, une cour de gang qui en occupe quatre.
3. **Les parcelles** : l'interieur d'un ilot est redecoupe au hasard (BSP) en
   parcelles inegales ; chacune recoit un batiment a la profondeur variable
   (parfois en U autour d'une cour), un terrain vague, un stationnement ou un
   jardin. Deux ilots ne se ressemblent jamais.

Le champ `voie` dit ou va un vehicule depuis chaque tuile : `> < ^ v` une voie,
`+` un croisement (on en sort par ou on veut, sauf a contresens), `S` une ligne
d'arret — sa direction est dans `arrets`, pas dans le glyphe — et `.` pas de
route.

⚠️ Les rues du pourtour ne sont jamais avalees : chaque tuile de rue du bord
tombe donc dans un croisement, et AUCUNE fleche ne pointe hors carte. C'est ce
qui rend les voies fortement connexes (juge `voies_bloquees`).

Forme servie (`exporter()`) :
    largeur, hauteur, tuile_px   en tuiles
    sol                          lignes de glyphes (LEGENDE)
    voie                         lignes de direction routiere (VOIES)
    arrets                       "x,y" -> direction de la ligne d'arret
    intersections                boites de croisement (feux, plus tard)
    legende                      glyphe -> proprietes (solide, route, ...)
    portes, lampes, decor        listes de positions en tuiles
    zones                        rectangles nommes (district, gang, port)
    points_interet               lieux nommes (planque, hopital, magasins...)
    apparition                   ou le joueur commence
    interieurs                   petites cartes, meme forme, par slug
"""

from __future__ import annotations

import bisect
import math

from . import devantures as devantures_mod
from . import economie
from . import magasins
from . import missions
from . import vehicules

TUILE_PX = 16

#: Ce qu'il faut AUTOUR d'une rampe pour qu'elle serve, en tuiles : de l'ELAN
#: avant le pied, de la RECEPTION apres la levre.
#: ⚠️ C'est la mesure de « accessible », et elle ne se choisit pas au gout :
#: elle se CALCULE sur la physique. Le defi du Grand Saut demande 60 px de vol
#: en moto ; or une moto partie d'arret vole 54 px avec sept tuiles d'elan et
#: 68 px avec dix (mesure : `vehicules.PHYSIQUE`, rampe_impulsion 0,42 et
#: gravite 0,18). A sept, on aurait donc pose des tremplins sur lesquels le
#: defi du jeu est IMPOSSIBLE. La reception, elle, doit couvrir le vol : 68 px
#: font quatre tuiles et demie.
def _elan_du_defi() -> int:
    """L'elan garanti devant une rampe, en tuiles : ce qu'il faut a la moto,
    partie d'arret, pour que *Le Grand Saut* soit possible.

    ⚠️ Lui non plus ne se choisit plus. Il valait 10, mesure sur l'ancienne
    impulsion (0,42) ou la moto peinait a voler 60 px. L'impulsion a monte pour
    que le saut SE VOIE, donc l'elan necessaire a baisse — et une rampe qui
    exigeait dix tuiles d'elan n'en trouvait plus au stationnement de La Pointe,
    la ou les Skateux ont pourtant droit au leur.
    """
    defi = next(d for d in missions.DEFIS if d["slug"] == "saut")
    px = vehicules.elan_pour_voler(vehicules.par_slug(defi["vehicule"]), defi["vol_px"])
    return math.ceil(px / TUILE_PX)


ELAN_RAMPE = _elan_du_defi()


def _reception(slug: str) -> int:
    """Ce qu'il faut de ROULABLE apres la levre, en tuiles, pour que ce char-la
    retombe sur la route et non dans un mur.

    ⚠️ La reception ne se choisit plus en tuiles : elle se DEDUIT du saut
    (`vehicules.saut`). L'ancien 6 avait ete mesure sur une moto PARTIE
    D'ARRET — 68 px de vol — alors que le code encourage exactement le
    contraire : « l'elan n'a pas a tenir dans le terrain, il continue dans la
    rue, on arrive lance au lieu de partir d'arret ». Lancee, la meme moto
    volait 126 px pour 96 px de degage. On mesurait donc une chose et on en
    jouait une autre.
    """
    saut = vehicules.saut(vehicules.par_slug(slug))
    return math.ceil(saut["degage"] / TUILE_PX)


#: ⚠️ Toute rampe recoit **l'auto**, la reference du catalogue (« l'auto est la
#: reference, vitesse 100 % »). Exiger la moto partout ne laisserait que trois
#: tremplins dans la ville : une regle si dure qu'elle supprime la chose
#: qu'elle protege n'est plus une regle, c'est un veto.
RECEPTION_RAMPE = _reception("auto")

#: ⚠️ Sauf celle du Grand Saut : le defi EXIGE la moto, donc la rampe qui porte
#: son panneau doit recevoir une moto lancee. Une rampe de defi sur laquelle le
#: defi se termine dans un mur, c'est le bug que Martin a nomme.
RECEPTION_DEFI = _reception("moto")

#: Ou l'on PROPOSE un tremplin. ⚠️ Ces trois parts etaient trois nombres nus
#: perdus dans trois methodes ; elles sont ici parce qu'elles se lisent
#: ensemble avec `ELAN_RAMPE` et `RECEPTION_RAMPE` : proposer et accepter sont
#: les deux moities de la meme decision. Le juge compte les rampes POSEES,
#: jamais les rampes proposees.
PART_RAMPE_COUR = 0.45
PART_RAMPE_STATIONNEMENT = 0.35
PART_RAMPE_VAGUE = 0.5

#: --- Ce qu'on jette sur un terrain vague ------------------------------------
#: ⚠️ Une liste A POIDS, pas un choix uniforme : ce qu'on voit d'abord dans un
#: lot abandonne, c'est du gravat et des sacs eventres — un baril rouille, on en
#: voit un, pas un par dix tuiles. Un terrain ou chaque saloperie est aussi rare
#: que les autres n'a pas l'air abandonne, il a l'air rempli.
#: ⚠️ Le `pneu` est le seul du lot qui ne soit pas solide : il est couche, on
#: marche dessus. Les trois autres arretent un pieton comme une caisse.
DECHETS = ("debris", "debris", "debris", "debris",
           "ordures", "ordures", "ordures",
           "pneu", "pneu", "baril", "caisse")

#: Une tuile sur COMBIEN porte un dechet. ⚠️ Mesure du 16 sept. 2026 : le terrain
#: vague semait un gravat par douze tuiles et n'en posait qu'un par DIX-SEPT (le
#: reste tombait sur du reserve ou de l'occupe) — 53 objets sur 922 tuiles, et
#: treize lots sur quatorze qu'on traversait sans rien contourner.
#: ⚠️ **DIX, PAS SIX.** Une sur six a ete essaye et Martin l'a renvoye : « il y
#: a trop de salete partout ». C'est vrai en deux sens — a l'oeil, un lot ou
#: l'on contourne quelque chose a chaque pas n'a plus l'air abandonne, il a
#: l'air d'un depot ; et au pied, la moitie de ces objets ARRETENT un pieton
#: (`DECOR_SOLIDE`), donc a cette densite-la un terrain vague se referme sur
#: lui-meme. Une sur dix se traverse en zigzaguant, ce qui etait tout ce qu'on
#: voulait.
PART_DECHET = 10

#: Et les mauvaises herbes, qui sont l'autre moitie de l'abandon : ce qui pousse
#: quand plus personne ne tond. Moins denses que les dechets — un buisson est
#: large (16 px), et une friche qu'on ne voit plus n'est plus une friche.
#: ⚠️ Un buisson, lui, ne ferme rien : on passe dessus. Il baisse quand meme,
#: parce qu'a l'oeil il compte autant que le reste.
PART_MAUVAISE_HERBE = 18

#: --- Le port ----------------------------------------------------------------
#: La profondeur du TABLIER d'un quai sur l'eau, en tuiles ; ce qui depasse dans
#: la region est la baie. ⚠️ DIX, c'est-a-dire exactement ce que le quai faisait
#: quand il etait un bloc a lui : on ne change pas la surface du port, on change
#: ce qu'il y a devant.
QUAI_TABLIER = 10

#: Ce qu'il faut d'eau devant un quai pour qu'un bateau y vienne. En dessous, la
#: region n'a pas avale de baie et le quai reste du plancher plein — c'est le
#: cas des deux quais du Faubourg : la baie est dans un autre district, ils ne
#: peuvent pas l'avaler, et c'est la RUE noyee sous eux qui leur donne l'eau.
QUAI_TIRANT_MIN = 6

#: Les appontements : largeur, longueur, et l'ecart entre deux voisins. ⚠️ Ils
#: PARTENT du tablier et avancent dans la baie ; une jetee qui ne touche pas la
#: terre est une ile, et personne n'y va.
APPONTEMENT = {"largeur": (2, 3), "longueur": (5, 10), "ecart": 11}

#: L'ECART entre deux bornes d'amarrage, en tuiles. ⚠️ Un ECART, pas « une tuile
#: sur six » : la levre d'un quai n'est pas une ligne droite (elle contourne les
#: appontements et les darses), et compter une tuile sur six le long d'une liste
#: posait deux bornes COLLEES des que la levre tournait le coin.
#: ⚠️ **ONZE, PAS SIX.** Retour de Martin : « impossible d'aller sur une partie
#: du quai, il est **cloture** ». Une borne d'amarrage ARRETE un pieton, et la
#: rangee du bord donnait `QpQQAQQAQQQpQQQQQAQQpQQpQQAQQA` — une borne ou un
#: pneu tous les trois pas sur soixante tuiles. Vu d'en haut, ce n'est plus un
#: quai, c'est une palissade. Un vrai quai amarre tous les dix a vingt metres.
ECART_BORNE_AMARRAGE = 11
#: Les pneus en DEFENSE, pendus au bord pour que la coque ne cogne pas le bois.
#: ⚠️ Ils ne sont PAS solides (on marche dessus) — ils ne ferment donc rien, et
#: c'est ce qui permet d'en garder. Ils restent rares : une defense tous les
#: trois pas est un mur de pneus.
CHANCE_DEFENSE = 0.10

#: L'APRON : la bande du bord de l'eau ou l'on TRAVAILLE. ⚠️ C'est la que se
#: joue tout le reste : elle reste degagee de cargaison, parce que c'est par la
#: qu'on longe le quai a pied et qu'on decharge. Une caisse posee sur l'apron,
#: c'est une caisse entre le bateau et le camion.
QUAI_APRON = 2
#: Le FOND : la bande du cote de la rue, ou la cargaison s'empile — c'est de la
#: que les camions arrivent. ⚠️ **Elle etait semee sur TOUT le tablier** (une
#: caisse par dix tuiles d'arriere, soit une soixantaine de caisses SOLIDES sur
#: dix rangees de profondeur) : un plancher d'entrepot, pas un quai. Tout ce qui
#: est entre l'apron et le fond reste vide, et c'est ce vide qui se marche.
QUAI_FOND = 3
#: Une tuile de fond sur combien porte quelque chose.
PART_CARGAISON = 7

#: Le MOUILLAGE du cargo : la part du quai que ferme sa barriere (`BARRIERES`,
#: « le quai du cargo »), en demi-largeur et en profondeur depuis la rue.
#: ⚠️ **UN MOUILLAGE, PAS UN QUAI.** La barriere prenait toute la region de quai
#: ou se tient le contrebandier — et depuis que le quai a avale la baie, cette
#: region faisait 61 x 26 tuiles, eau comprise. De jour, tout le quai ouest etait
#: donc sous la chaine. Retour de Martin : « impossible d'aller sur une partie du
#: quai, il est cloture, sans chemin a pied ». Elle ferme maintenant l'enclos ou
#: l'on decharge, et ⚠️ **jamais l'apron** : on longe le quai par le bord de
#: l'eau, cargo ou pas.
MOUILLAGE = {"demi_largeur": 7, "profondeur": 6}

#: Solidite : 0 libre, 1 mur (bloque tout), 2 eau (bloque sauf les bateaux),
#: 3 basse (bloque les vehicules, pas les pietons).
LEGENDE: dict[str, dict] = {
    ".": {"nom": "trottoir", "trottoir": True},
    # ⚠️ L'ABORD : la couronne d'un bloc bati, entre ses murs et le trottoir. Ni
    # route ni obstacle, donc un pieton y marche — mais c'est un DEBORDEMENT,
    # pas un deuxieme trottoir : le flaneur prefere la dalle, et c'est ici que
    # le mobilier (lampadaires, bornes, kiosques) se range pour laisser la
    # seule tuile de trottoir libre. Il est ne le jour ou le trottoir est passe
    # a une tuile : deux passants de 12 px ne se croisent pas sur 16, et Martin a
    # tranche qu'on se croise en debordant sur le terrain plutot qu'en
    # elargissant la rue.
    "_": {"nom": "abord", "abord": True},
    # ⚠️ `terre` : on peut y planter un arbre sans rien decouper. C'est ce qui
    # decide, dans le navigateur, si un arbre a besoin d'une FOSSE a son pied
    # (`Monde.carte.fosses`) — un arbre plante dans le beton en a une, un arbre
    # sur le gazon n'en a pas. La liste vit ICI et pas dans le dessin : c'est
    # une propriete du SOL, pas une couleur.
    ",": {"nom": "herbe", "herbe": True, "terre": True},
    # ⚠️ LA FRICHE D'UN TERRAIN VAGUE, ET PAS DU GAZON. Un lot laisse a
    # l'abandon se peignait avec l'herbe des cours et des parcs : vu d'en haut,
    # de la ferraille derriere un barbele avait exactement la surface d'un
    # parterre de banlieue, et Martin a nomme ce qu'il voyait — un CHAMP. Ce
    # n'est pas la meme terre : elle perce, l'herbe y est seche, et c'est cette
    # surface-la qui dit d'un coup d'oeil que personne ne l'entretient.
    # ⚠️ PAS DE `herbe` DANS SA FICHE, et ce n'est pas un oubli : la mini-carte
    # peint le vert avec cette propriete-la (`couleurMini`, monde.js). Une
    # friche verte sur la carte, c'est un parc de plus — soit l'inverse de ce
    # qu'on vient de dessiner. Elle tombe donc dans la couleur de terre, avec le
    # sable et l'allee de parc.
    # ⚠️ `terre` : un arbre pousse dans une friche sans qu'on lui creuse une
    # fosse. Une fosse de beton au milieu des gravats, c'est un arbre de rue.
    ";": {"nom": "friche", "terre": True, "friche": True},
    "x": {"nom": "ruelle", "ruelle": True},
    "s": {"nom": "sable", "terre": True},
    # ⚠️ La POUSSIERE DE PIERRE d'une allee de parc, et pas du trottoir. Un
    # parc de ville se peignait avec le beton de la rue : quatre allees de
    # deux tuiles et une place de 5 x 5 au coeur, ca fait pres de la moitie
    # d'un ilot — vu d'en haut, ce n'etait pas un parc avec des sentiers,
    # c'etait une dalle avec du gazon dessus. Ce n'est pas non plus du sable
    # (`s`) : la plage borde l'eau, l'allee traverse la pelouse, et les
    # confondre mettrait une plage au milieu du Faubourg.
    # ⚠️ `g` minuscule — `G` majuscule est une porte de garage. Meme piege
    # que `w` / `W` deux ecrans plus bas, et meme parade : les deux ne vivent
    # jamais dans le meme genre de plan (l'un est du SOL, l'autre du BATI).
    "g": {"nom": "allée de poussière de pierre", "terre": True},
    # ⚠️ LA VOIE DU PETIT TRAIN DE LA FOIRE. On y marche (on la traverse pour
    # entrer), mais c'est un GLYPHE et pas du decor : la voie se cuit avec le
    # sol, une fois par morceau, au lieu de se repeindre a chaque image. Chaque
    # tuile lit ses voisines pour savoir si elle est droite ou en courbe
    # (`rail`, `Monde.varianteDeRail`) — la meme lecture que la cloture.
    # ⚠️ `T` majuscule : `t` minuscule est un plancher. Les deux ne vivent
    # jamais dans le meme genre de plan (l'un dehors, l'autre dedans).
    "T": {"nom": "voie du petit train", "rail": True},
    "Q": {"nom": "quai"},
    "~": {"nom": "eau", "solide": 2},
    # ⚠️ UNE PISCINE DE BANLIEUE N'EST PAS LA BAIE. Hors terre, on y entre
    # debout et on ne s'y noie pas : solidite 3, comme un meuble — un pieton la
    # traverse, une auto non, et aucun juge de connexite ne s'en emeut. Elle
    # n'est donc PAS de l'eau au sens de `MASQUE_NAGEUR` : on n'y nage pas, on
    # y barbote, et c'est tout ce qu'on lui demande.
    # ⚠️ `bloc` : chaque tuile lit ses voisines pour savoir quel QUART de la
    # piscine elle porte. Sans ca, quatre tuiles font quatre carres avec quatre
    # margelles — ce que Martin a vu tout de suite — au lieu d'un seul rond.
    "o": {"nom": "piscine hors terre", "solide": 3, "piscine": True, "bloc": True},
    "#": {"nom": "asphalte", "route": True},
    "-": {"nom": "ligne de voie est-ouest", "route": True},
    "|": {"nom": "ligne de voie nord-sud", "route": True},
    "+": {"nom": "ligne centrale est-ouest", "route": True},
    "*": {"nom": "ligne centrale nord-sud", "route": True},
    "=": {"nom": "passage piéton est-ouest", "route": True, "trottoir": True},
    ":": {"nom": "passage piéton nord-sud", "route": True, "trottoir": True},
    "p": {"nom": "stationnement", "route": True, "stationnement": True},
    # ⚠️ Les quatre glyphes de CASE vivent dans `sol`, pas dans `voie` : ici la
    # fleche ne dit pas ou roule un char, elle dit ou pointe le NEZ de l'auto
    # garee. Le fond de la case est donc du cote de la fleche, et l'allee de
    # manoeuvre de l'autre.
    "^": {"nom": "case de stationnement, nez au nord", "route": True,
          "stationnement": True, "case": "N"},
    "v": {"nom": "case de stationnement, nez au sud", "route": True,
          "stationnement": True, "case": "S"},
    "<": {"nom": "case de stationnement, nez a l'ouest", "route": True,
          "stationnement": True, "case": "O"},
    ">": {"nom": "case de stationnement, nez a l'est", "route": True,
          "stationnement": True, "case": "E"},
    "I": {"nom": "ilot de stationnement", "trottoir": True},
    # ⚠️ Une rampe, c'est DEUX tuiles : le PIED ou l'on monte et la LEVRE
    # d'ou l'on decolle. Le dessin lit la paire pour savoir dans quel sens
    # ca grimpe (`varianteDeRampe`, monde.js) — un glyphe seul ne dirait rien,
    # et c'est pour ca que l'ancienne rampe n'avait l'air de rien.
    "R": {"nom": "pied de rampe", "route": True, "rampe": True},
    "J": {"nom": "lèvre de rampe", "route": True, "rampe": True},
    "B": {"nom": "toit de tole", "solide": 1, "toit": True},
    "E": {"nom": "toit d'ardoise", "solide": 1, "toit": True},
    "O": {"nom": "toit de gravier", "solide": 1, "toit": True},
    # ⚠️ Le seul toit qui n'est pas plat : deux versants et une ligne de faite.
    # Le dessin ne le sait pas d'avance — il COMPTE les tuiles de toit au nord
    # et au sud pour savoir sur quel versant il est (`varianteDePente`,
    # monde.js). Une banlieue de bungalows vue d'en haut, c'est ca.
    "P": {"nom": "toit à deux versants", "solide": 1, "toit": True, "pente": True},
    "F": {"nom": "façade", "solide": 1},
    "W": {"nom": "vitrine", "solide": 1, "lampe": True},
    "D": {"nom": "porte", "solide": 1, "porte": True},
    "d": {"nom": "porte condamnée", "solide": 1},
    "G": {"nom": "porte de garage", "solide": 1, "garage": True},
    # --- Les deux clotures --------------------------------------------------
    # ⚠️ Une cloture n'arretait QUE les chars : `f` etait solide 3, donc le
    # masque des pietons ne la voyait pas et on la traversait en COURANT. C'est
    # ce qui la rendait muette. Elles ont maintenant leur solidite a elles :
    #   4 — le grillage : on l'ENJAMBE, une seconde en haut, immobile et sans
    #       rien pouvoir faire. C'est ce prix-la qui fait d'une cloture un
    #       choix — couper par la cour, ou faire le tour.
    #   5 — le barbele : personne ne passe, ni a pied ni en char. Il se met la
    #       ou quelqu'un a paye pour que personne n'entre.
    # ⚠️ Ni l'un ni l'autre n'est solide 1 : on VOIT a travers une cloture, donc
    # un cone de police la traverse (`ligneLibre` ne s'arrete qu'au 1).
    "f": {"nom": "grillage", "solide": 4, "cloture": "grillage"},
    # ⚠️ `w` minuscule — `W` majuscule est une vitrine. Les deux se confondent a
    # la relecture, alors ils ne vivent jamais dans le meme genre de plan : une
    # vitrine est BATIE (solidite 1), une palissade est une CLOTURE (4).
    "w": {"nom": "palissade de bois", "solide": 4, "cloture": "bois"},
    "X": {"nom": "barbelé", "solide": 5, "cloture": "barbele"},
    # --- Dedans : les planchers et les meubles ------------------------------
    # ⚠️ Un MEUBLE est solide 3, comme la borne-fontaine et la cloture : il
    # arrete un char, pas un piéton. C'est ce qui permet d'en poser partout
    # sans jamais murer un coin de piece — `composantes_marchables` compte le
    # 3 comme marchable, et le juge d'habitabilite reste vrai par
    # construction. Un meuble qui bloquerait le joueur serait un piege a
    # sauvegarde : on entre, on se coince, et la partie est finie.
    "t": {"nom": "plancher de bois", "dedans": True},
    "u": {"nom": "carrelage", "dedans": True},
    # ⚠️ `bloc` : un meuble qui vient en BLOCS de tuiles (un lit de 2 × 2, un
    # billard de 4 × 2, un tapis de 3 × 3, une presse) et que le navigateur
    # peint PAR SES VOISINES (`varianteDeBloc`, monde.js) : une tete de lit,
    # un chant de plateau, un galon, un boulon ne vont qu'aux bords du bloc.
    # Sans ca, chaque tuile etait un meuble entier — quatre lits d'une
    # place, huit tabourets, trois chemins de couloir. Le corollaire, juge
    # dans les plans : deux blocs du meme glyphe ne se touchent jamais.
    "y": {"nom": "tapis", "dedans": True, "bloc": True},
    "c": {"nom": "comptoir", "solide": 3, "meuble": True},
    "e": {"nom": "étagère", "solide": 3, "meuble": True},
    "a": {"nom": "table", "solide": 3, "meuble": True, "bloc": True},
    "h": {"nom": "chaise", "solide": 3, "meuble": True},
    "l": {"nom": "lit", "solide": 3, "meuble": True, "bloc": True},
    "j": {"nom": "frigo", "solide": 3, "meuble": True},
    "m": {"nom": "machine", "solide": 3, "meuble": True, "bloc": True},
    "n": {"nom": "plante", "solide": 3, "meuble": True},
    "k": {"nom": "classeur", "solide": 3, "meuble": True},
    "z": {"nom": "poêle", "solide": 3, "meuble": True},
    # ⚠️ « / » et pas une lettre : l'escalier est le seul meuble qui MENE
    # quelque part (un point `escalier` par-dessus), et la barre oblique se
    # reconnait d'un coup d'oeil dans un plan de piece.
    "/": {"nom": "escalier", "solide": 3, "meuble": True},
    # --- L'hopital, et la machine du coin -----------------------------------
    # ⚠️ Quatre lettres, et ce sont les DERNIERES minuscules libres de la
    # legende : `b`, `i`, `q`, `r`. L'hopital etait la chambre de la planque
    # avec du carrelage — deux lits de bois, trois chaises — et rien dans la
    # piece ne disait qu'on y soignait quelqu'un. Ce qui le dit, c'est le
    # materiel : un lit a barreaux, la potence du solute, l'ecran qui trace.
    #
    # ⚠️ Le LIT D'HOPITAL n'est pas le lit (`l`) : un lit de chambre fait deux
    # places et se peint en bois, celui-ci fait UNE place, un cadre de metal et
    # des draps blancs. Il vient en bloc (une tuile sur deux, la tete au nord),
    # et c'est dans sa tuile de tete que se couche le MALADE (`QUI_DEDANS`).
    "r": {"nom": "lit d'hôpital", "solide": 3, "meuble": True, "bloc": True},
    "i": {"nom": "soluté", "solide": 3, "meuble": True},
    "q": {"nom": "moniteur", "solide": 3, "meuble": True},
    # ⚠️ La DISTRIBUTRICE D'UNE SALLE D'ATTENTE est un meuble, pas un decor :
    # dedans, il n'y a ni index de decor ni char pour la defoncer. Elle porte
    # un point `distributrice` (sa sorte dit ce qu'elle vend) ; sa cousine de
    # la rue, elle, est un DECOR cassable (`distributrices()`).
    "b": {"nom": "distributrice", "solide": 3, "meuble": True},
}

#: Les glyphes de facade qu'on POUSSE (ou qu'on a condamnes) : une porte, une porte
#: murée, une porte de garage. Rien ne se plante devant, ni juste a cote.
PORTES_DE_FACADE = frozenset("DdG")

#: Les trois clotures, par leur glyphe. ⚠️ Toute la difference de JEU tient dans
#: la legende (solidite 4 contre 5) : le grillage et la palissade de bois
#: s'enjambent, le barbele ne se passe pas. Le bois ne change rien aux regles —
#: c'est de la VARIETE, et elle a sa place : une banlieue dont les cours arriere
#: sont en grillage industriel n'a pas l'air d'une banlieue.
GRILLAGE, BOIS, BARBELE = "f", "w", "X"
CLOTURES = frozenset({GRILLAGE, BOIS, BARBELE})
#: Ce qui s'enjambe (une seconde en haut), par opposition au barbele.
ENJAMBABLES = frozenset({GRILLAGE, BOIS})

#: Les glyphes qui ne vivent QUE dans une piece. ⚠️ Un juge les interdit dans
#: la ville : un lit sur un trottoir voudrait dire qu'un plan d'interieur a
#: ete peint sur la carte par erreur, et personne ne le verrait avant de
#: tomber dessus en jouant.
DEDANS = frozenset(g for g, p in LEGENDE.items() if p.get("dedans") or p.get("meuble"))

# ⚠️ Ces quatre-la se lisent avec la legende, et ils sont ICI parce que le
# module s'en sert des l'import : un plan de piece est juge au chargement
# (`_piece`), pas au premier test.


def solidite(glyphe: str) -> int:
    return int(LEGENDE.get(glyphe, {}).get("solide", 0))


def marchable(glyphe: str) -> bool:
    """Ce qu'un pieton peut FOULER : du sol libre, ou un obstacle bas qu'il
    contourne d'un pas (borne-fontaine, meuble).

    ⚠️ Pas une cloture : on ne se tient pas SUR une cloture. On l'enjambe
    (grillage, solidite 4) ou on ne passe pas du tout (barbele, 5) — c'est
    `franchissable` qui le dit.
    """
    return solidite(glyphe) in (0, 3)


def franchissable(glyphe: str) -> bool:
    """Ce qu'un pieton peut TRAVERSER a pied, en enjambant s'il le faut.

    ⚠️ C'est la connexite qui se juge ici, pas le placement : une cour derriere
    un grillage fait partie de la ville (on y entre par-dessus, au prix d'une
    seconde), une cour derriere du barbele n'en fait pas partie. C'est pour ca
    que le juge « tout ce qui est marchable est relie » est du meme coup la
    garantie qu'un barbele ne referme jamais une poche.
    """
    return solidite(glyphe) in (0, 3, 4)


def routier(glyphe: str) -> bool:
    return bool(LEGENDE.get(glyphe, {}).get("route"))


def composantes_marchables(carte: dict) -> list[set[tuple[int, int]]]:
    """Les groupes de tuiles marchables reliees entre elles (4-connexite).

    ⚠️ On passe PAR-DESSUS le grillage : il se franchit, donc les deux cotes
    d'une cloture sont le meme groupe. Le barbele, lui, coupe — et c'est tout
    son sens. Une tuile de cloture n'est jamais DANS un groupe (on ne s'y tient
    pas) : elle n'est qu'un pont.
    """
    sol = carte["sol"]
    vues: set[tuple[int, int]] = set()
    groupes = []
    for y, ligne in enumerate(sol):
        for x, glyphe in enumerate(ligne):
            if not marchable(glyphe) or (x, y) in vues:
                continue
            groupe: set[tuple[int, int]] = set()
            # ⚠️ `visites` compte AUSSI les tuiles de cloture : elles ne sont
            # jamais dans le groupe (on ne s'y tient pas), et sans elles la
            # pile ferait l'aller-retour cloture <-> voisine pour toujours.
            visites: set[tuple[int, int]] = set()
            pile = [(x, y)]
            while pile:
                cx, cy = pile.pop()
                if (cx, cy) in visites or not (0 <= cy < len(sol) and 0 <= cx < len(sol[cy])):
                    continue
                if not franchissable(sol[cy][cx]):
                    continue
                visites.add((cx, cy))
                # Une cloture n'est qu'un pont : elle relie ses voisines sans
                # jamais compter comme du sol.
                if marchable(sol[cy][cx]):
                    groupe.add((cx, cy))
                pile.extend(((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)))
            vues |= visites
            groupes.append(groupe)
    return groupes


def composantes_par_terre(carte: dict) -> dict[str, list[set[tuple[int, int]]]]:
    """Les groupes marchables, rangés par TERRE FERME : `ville`, et l'île.

    ⚠️ « Un seul îlot marchable » était le juge de toute la géographie — la
    preuve qu'aucun trottoir n'est enclavé. Le jour où l'île existe, il devient
    faux sans que rien ne soit cassé : l'île est un îlot, et c'est tout son
    sens. Il devient donc « **un îlot par terre ferme** », et il faut le changer
    EXPRÈS, pas le découvrir. Un groupe est de l'île s'il tient entier dans son
    rectangle (`carte["ile"]`) ; tout le reste est la ville — et une poche
    enclavée en ville reste un deuxième groupe de la ville, donc un juge rouge.
    """
    ile = carte.get("ile")
    terres: dict[str, list[set[tuple[int, int]]]] = {"ville": []}
    if ile:
        terres[ile["slug"]] = []
    for groupe in composantes_marchables(carte):
        dedans = ile and all(ile["x"] <= x < ile["x"] + ile["l"] and ile["y"] <= y < ile["y"] + ile["h"]
                             for x, y in groupe)
        terres[ile["slug"] if dedans else "ville"].append(groupe)
    return terres



VOIES = {".", ">", "<", "^", "v", "+", "S"}

#: Le gabarit d'un stationnement, en tuiles. Une case fait UNE tuile de large et
#: DEUX de creux : c'est exactement l'auto (32 x 16 px), pare-chocs compris.
#: Une allee de manoeuvre en fait deux — de quoi se croiser et braquer.
CASE_CREUX = 2
ALLEE = 2

PAS = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}

#: Les couvertures, par genre de batiment. ⚠️ `des.choix(TOITS)` tirait au
#: hasard dans les trois : un entrepot heritait de l'ardoise et un bungalow du
#: gravier goudronne. Un toit se lit d'abord a sa MATIERE, et la matiere se
#: choisit sur le batiment — de la tole sur un hangar, du gravier sur un
#: entrepot, de l'ardoise en ville, deux versants sur une maison.
TOITS = "BEOP"
TOIT_PENTE = "P"
COUVERTURES = {
    "maisons": "PPE",           # deux versants, presque toujours
    "banlieue": "PPP",          # le bungalow : jamais autre chose
    "hangars": "BBO",           # de la tole, du gravier
    "industriel": "BOO",
    "gang": "BO",
    "commerces": "EEO",         # l'ardoise de la vieille ville
}

#: L'equipement de toit : ce qui rend un toit credible vu d'en haut. ⚠️ Ce
#: n'est PAS du decor — `poser_decor` refuse les tuiles solides, et il a raison :
#: le decor est une entite qu'on heurte. Ce qui est sur un toit n'est heurte par
#: personne, c'est du DESSIN : ca voyage dans le paquet et s'indexe par morceau,
#: comme les devantures et les graffitis.
#:
#: `poids` : combien de tuiles de toit il faut, en moyenne, pour en poser un.
EQUIPEMENTS_DE_TOIT = (
    {"type": "ventilation", "poids": 8, "genres": ()},
    {"type": "clim", "poids": 14, "genres": ("commerces", "industriel", "hangars", "gang")},
    {"type": "cheminee", "poids": 10, "genres": ("maisons", "banlieue", "commerces")},
    {"type": "cage", "poids": 26, "genres": ("commerces", "industriel", "hangars")},
    {"type": "reservoir", "poids": 30, "genres": ("commerces", "industriel")},
    {"type": "antenne", "poids": 16, "genres": ()},
    # ⚠️ Le clocher n'est JAMAIS tire : aucun ilot n'est du genre « chapelle ».
    # Il est pose a la main sur la chapelle de l'ile (`ile.BATIMENTS`), et il est
    # ici pour que le juge des toits le connaisse.
    {"type": "clocher", "poids": 1, "genres": ("chapelle",)},
)

#: ⚠️ Les genres d'ilot qui ont pignon sur rue. Pas les maisons ni la banlieue
#: (on n'accroche pas une enseigne sur un bungalow), pas les cours de gang.
GENRES_COMMERCANTS = frozenset({"commerces", "hangars", "industriel"})

# --- Les cinq districts -----------------------------------------------------

#: ⚠️ La ville est UNE SEULE grille de blocs (20 colonnes, 12 rangees) ; un
#: district en occupe un rectangle. C'est ce qui la garde d'un seul tenant : les
#: arteres traversent les frontieres, aucune rue ne s'arrete parce qu'on a
#: change de quartier, et il n'y a rien a charger en roulant. Un district se
#: reconnait a trois choses, et aucune n'est un decor : la LARGEUR de ses
#: colonnes, ses FUSIONS (`<` `^`, qui effacent les rues et font les gros
#: blocs), et le CONTENU de ses ilots.
#:
#: ⚠️ Un district ne fusionne JAMAIS par-dessus sa frontiere : pas de `<` en
#: premiere colonne, pas de `^` en premiere rangee (juge `_assembler`). Sans
#: cette regle, deplacer un quartier en casserait un autre.
#: ⚠️ `rares` : les chars du haut de gamme qui peuvent NAITRE dans ce
#: district. C'est ici, et pas dans le catalogue, que se joue leur rarete —
#: un char rare qu'on croise partout n'est plus rare, et c'est tout ce qui
#: fait qu'on le VEUT. La Shop n'en a aucun : on ne laisse pas une
#: decapotable dans une cour a ferraille.
#: ⚠️ `standing` : QUI A LES MOYENS, bloc par bloc, a cote du `plan` et de la
#: meme forme (`STANDINGS`). Le plan dit ce qu'on fait la (l'usage), le standing
#: dit qui en a les moyens — une rue commercante peut etre chic ou miteuse. Il
#: est ECRIT, pas tire : c'est une decision de ville, elle ne consomme aucun de,
#: et elle ne suit pas le district (le Faubourg a sa rue chic et son coin pauvre).
DISTRICTS: tuple[dict, ...] = (
    # Le Faubourg — le quartier de la v1, intact. Trame serree, blocs courts,
    # la cour des Cravates au centre. C'est ici qu'on debarque de l'autobus.
    {"slug": "faubourg", "nom": "Le Faubourg", "bx": 5, "by": 0,
     "gang": "cravates", "gang_nom": "Les Cravates", "brume": True,
     # ⚠️ LE CENTRE-VILLE EST LE PLUS PEUPLE, ET IL DOIT SE SENTIR (demande de
     # Martin : « plus de gens en centre-ville et moins en peripherie »). Il
     # demande PLUS que la bulle ne peut tenir (`MAX_PIETONS`), et c'est voulu :
     # c'est le seul quartier de la ville a etre plein a ras bord a toute heure
     # du jour. Les quatre autres ont baisse pour le payer — le budget d'image
     # n'a pas bouge, c'est la REPARTITION qui change.
     "pietons": 34, "vehicules": 12, "police": 2, "rythme": (0.35, 1.0, 1.0),
     "rares": ("sport", "luxe"),
     # ⚠️ **`jj`, PAS `qq`** — retour de Martin, capture a l'appui : « il y a
     # encore des quais entre deux routes ». Les deux quais du Faubourg etaient
     # du plancher plein ENTOURE DE RUES : une rue de chaque cote, et en
     # dessous un boulevard a quatre voies, une plage, puis la baie — le meme
     # defaut que les Quais, un bloc plus a l'est. Ils ne peuvent pas AVALER la
     # baie comme ceux des Quais (elle est dans un autre district, et une
     # fusion ne passe jamais une frontiere) ; mais `j` est de l'eau pour la
     # trame (`EAUX`), et c'est suffisant : une rue qui ne longe que de l'eau
     # et du quai est noyee. Le boulevard sous eux devient la baie, la rue
     # entre eux une darse, la rue vers l'etang un bras d'eau ; celle du nord,
     # qui longe des immeubles, reste la rue de service.
     "plan": ("Tccchhhh",
              "cMck<hAh",
              "ccGKohhh",
              "PcBcg<hh",
              "cCcc^^hH",
              "~~jjcccc"),
     # ⚠️ Sa rue chic va du Terminus a la place, par le parc ; son coin pauvre
     # tient la cour des Cravates, le garage de l'oncle, la planque et le bar
     # — c'est la que Rocco s'est endette, pas sur la rue des boutiques.
     "standing": ("=+++====",
                  "+=+++=+=",
                  "==--+===",
                  "==----==",
                  "=-----==",
                  "~~--====")},
    # Les Erables — la banlieue. Colonnes larges, maisons detachees sur grandes
    # parcelles, deux parcs, un depanneur, et les Chevreuils qui tournent en
    # char le soir faute de mieux.
    {"slug": "erables", "nom": "Les Érables", "bx": 0, "by": 0,
     "gang": "chevreuils", "gang_nom": "Les Chevreuils", "brume": False,
     "pietons": 10, "vehicules": 7, "police": 1, "rythme": (0.25, 1.1, 0.9),
     "rares": ("luxe",),
     "plan": ("mmmpm",
              "m<m^m",
              "Dmmmm",
              "mm<mm",
              "ccgmm",
              "mmm<m"),
     # Cossus, sauf la rangee commercante contre la cour des Chevreuils.
     "standing": ("+++++",
                  "+++++",
                  "+++++",
                  "+++++",
                  "===++",
                  "+++++")},
    # La Shop — l'industriel. Des blocs de 2 x 2 partout : presque pas de rues,
    # des entrepots gros comme un pate de maisons, des stationnements vides.
    # Deserte la nuit, et c'est exactement ce qui la rend inquietante.
    {"slug": "shop", "nom": "La Shop", "bx": 13, "by": 0,
     "gang": "boulonneux", "gang_nom": "Les Boulonneux", "brume": False,
     "pietons": 8, "vehicules": 9, "police": 1, "rythme": (0.15, 1.3, 0.6),
     "rares": (),
     "plan": ("U<i<i<p",
              "^<^<^<^",
              "i<g<E<i",
              "^<^<^<^",
              "i<Y<i<c",
              "^<^<^<^"),
     # Pauvre presque partout ; le parc, la fourriere municipale et le seul
     # bloc de commerces tiennent l'ordinaire.
     "standing": ("------=",
                  "------=",
                  "-------",
                  "-------",
                  "--==--=",
                  "--==--=")},
    # Les Quais — le port. Blocs LONGS d'est en ouest (des hangars de trois
    # blocs de large), une rangee de quais, l'eau au sud. Ca grouille au matin,
    # ca se vide a la noirceur — sauf la Brume.
    {"slug": "quais", "nom": "Les Quais", "bx": 0, "by": 6,
     "gang": "morues", "gang_nom": "Les Morues", "brume": True,
     "pietons": 18, "vehicules": 8, "police": 1, "rythme": (0.4, 1.4, 0.9),
     "rares": (),
     # ⚠️ **LA RANGEE D'EAU EST AVALEE PAR LE QUAI** (`^`), et c'est tout le
     # correctif du 16 sept. 2026. Elles etaient deux blocs separes, et la trame
     # met une rue entre deux blocs : il y avait donc un BOULEVARD A QUATRE
     # VOIES et une plage de sable entre le port et la baie — 16 des 1 818
     # tuiles de quai touchaient l'eau (0,9 %). Retour de Martin, capture a
     # l'appui : « il y a une route entre le quai et l'eau ». Le mecanisme des
     # superblocs efface la rue ; `j` dit que la region porte la baie.
     "plan": ("cc<c<<c",
              "w<<w<<c",
              "L<g<w<c",
              "w<<N<<c",
              "j<<j<<j",
              "^<<^<<^"),
     # Pauvres, sauf la rangee commercante du nord.
     "standing": ("=======",
                  "-------",
                  "-------",
                  "-------",
                  "-------",
                  "-------")},
    # La baie — pas un quartier : l'eau. Un seul bloc fusionne de 7 x 6, ce qui
    # efface toutes les rues qui la traverseraient. Le traversier y passera (v2,
    # M12) ; pour l'instant on la longe.
    {"slug": "baie", "nom": "La baie", "bx": 7, "by": 6, "eau": True,
     "gang": None, "gang_nom": None, "brume": False,
     "pietons": 0, "vehicules": 0, "police": 0, "rythme": (1.0, 1.0, 1.0),
     "rares": (),
     "plan": ("~<<<<<<",
              "^<<<<<<",
              "^<<<<<<",
              "^<<<<<<",
              "^<<<<<<",
              "^<<<<<<"),
     "standing": ("~~~~~~~",
                  "~~~~~~~",
                  "~~~~~~~",
                  "~~~~~~~",
                  "~~~~~~~",
                  "~~~~~~~")},
    # La Pointe — le parc au bout de la ville. Un chenal la coupe du reste :
    # UN pont, et rien d'autre. Des bois, des sentiers, un phare, quatre
    # maisons au bout, et les Skateux qui tiennent le stationnement.
    {"slug": "pointe", "nom": "La Pointe", "bx": 14, "by": 6,
     "gang": "skateux", "gang_nom": "Les Skateux", "brume": False,
     "pietons": 9, "vehicules": 4, "police": 1, "rythme": (0.2, 0.9, 1.2),
     "rares": ("sport",),
     # ⚠️ Une des trois taches de bois devient la FOIRE (`f`) : on n'agrandit pas
     # la grille, on la DEPENSE — la lecon de l'ile. Celle-ci borde le chenal ;
     # les plages sont a l'ouest et au sud, face au large (`PLAGES`).
     "plan": ("~<<<<<",
              "f<<<nc",
              "^<<<^c",
              "n<<<^V",
              "^<<<^g",
              "~<<~<<"),
     "standing": ("~~~~~~",
                  "======",
                  "======",
                  "======",
                  "======",
                  "~~~~~~")},
)

#: ⚠️ Aucune colonne n'a la largeur de sa voisine, aucune rangee la hauteur de
#: la sienne : c'est la premiere source d'irregularite, et la moins chere. Les
#: largeurs sont groupees par district — la banlieue et le port ont des blocs
#: larges, le Faubourg les siens (inchanges), l'industriel les plus gros.
#: ⚠️ Chaque bloc a GRANDI DE DEUX TUILES le 15 sept. 2026 : ce sont les deux
#: tuiles de trottoir que chaque rue a perdues (une par cote). Martin a tranche
#: « on agrandit les terrains et non les rues » — le nombre de voies ne bouge
#: pas, la ville garde sa taille a deux tuiles pres, et la couronne de chaque
#: bloc devient un abord ou l'on marche.
COLONNES = (18, 15, 20, 16, 19,              # Les Érables / Les Quais
            15, 11, 14, 18, 12, 16, 11, 14,  # Le Faubourg (v1, elargi de 2)
            19, 15, 21, 16, 14, 18, 15)      # La Shop / La Pointe
#: ⚠️ SAUF LA RANGEE DU PONT (la premiere de la bande sud) : elle est restee a
#: 11, et ses deux tuiles sont allees a la suivante. Le chenal que le pont
#: enjambe est de l'eau, pas un terrain — a treize tuiles, il coutait 104
#: points de souffle sur 100 et l'eau redevenait un mur (`test_eau`). Le pari
#: de la traversee ne bouge donc pas, et la trame garde sa somme.
RANGEES = (11, 14, 10, 13, 11, 15,           # la bande nord
           11, 16, 11, 13, 10, 12)           # la bande sud

#: La largeur de chaque rue, trottoirs compris. 6 = boulevard (4 voies),
#: 4 = rue (2 voies). Il y a une rue de plus que de blocs dans chaque sens.
#: ⚠️ Deux de moins qu'avant, exactement ce que `TROTTOIR` a perdu de chaque
#: cote : une rue de 6 fait toujours deux voies, un boulevard de 8 toujours
#: quatre. Un juge le tient (`test_trottoir`).
RUES_V = (6, 4, 4, 6, 4,
          6, 4, 6, 4, 4, 6, 4, 4, 6,
          4, 6, 4, 4, 6, 4, 6)
RUES_H = (6, 4, 6, 4, 6, 4, 6,
          4, 6, 4, 4, 4, 6)

#: ⚠️ UNE TUILE, et ce n'est pas un reglage : `_coupe()` la lit pour decouper
#: chaque rue, la traverse d'un croisement en fait la profondeur, et les
#: croisements se calculent avec. Passee de 2 a 1 le 15 sept. 2026 (demande de
#: Martin : « les trottoirs ne devraient etre que d'une tuile de large »). Les
#: deux tuiles liberees par chaque rue ne reviennent PAS aux voies : elles vont
#: aux blocs (`COLONNES` et `RANGEES` ont grandi d'autant), et la couronne de
#: chaque bloc bati devient un ABORD marchable — voir `ilots()`.
TROTTOIR = 1
GRAINE = 20260912

#: Les ponts : les seules rues qu'on construit PAR-DESSUS l'eau. Un pont est
#: un segment de rue ("v" verticale ou "h" horizontale) designe par sa rue et
#: la rangee (ou la colonne) qu'il longe — ici le seul lien vers La Pointe.
PONTS: frozenset = frozenset({("v", 17, 6)})

#: Les nids-de-poule. ⚠️ **Deux lignes, et toute la ville prend un accent** :
#: une tuile de chaussee qui secoue la camera et coute deux points de
#: carrosserie (`vehicules.PHYSIQUE`). C'est du decor qu'on SENT, pas un piege.
#:
#: ⚠️ **Jamais dans un croisement** — on y freine deja, on y regarde le feu, et
#: une secousse au milieu d'un virage se lit comme un bogue de collision. Jamais
#: sur une ligne d'arret non plus : c'est la qu'on est immobile. Et jamais deux
#: cote a cote (`ecart`) : deux nids colles ne font pas un nid-de-poule, ils
#: font une rue defoncee, et le joueur croit a un chantier.
#: **LES ENTRAVES DU JOUR.** ⚠️ La ville change d'un jour a l'autre sans qu'on
#: regenere une seule tuile : Python calcule UNE FOIS la liste des entraves
#: possibles, le paquet la transporte, et la graine du jour en tire une.
#:
#: ⚠️ **Une entrave ne coupe jamais la ville en deux**, et c'est la seule chose
#: qui compte. Celle-ci ne le peut pas PAR CONSTRUCTION : elle ferme UNE VOIE
#: d'une rue qui en a deux dans le meme sens — le champ de direction ne bouge
#: pas d'une fleche, donc `voies_bloquees` rend exactement ce qu'il rendait.
#: C'est ce qui permet de s'en passer ici : le juge de connexite coute 14 ms,
#: et en valider cent doublerait le temps de construction de la ville. La rue
#: ENTIERE barrée, elle, l'exigera — elle viendra avec son panneau DETOUR.
#:
#: ⚠️ Jamais dans un croisement ni sur une ligne d'arret : on y freine deja, et
#: des cones au milieu d'une boite se lisent comme un accident, pas comme un
#: chantier.
ENTRAVES: dict = {
    "longueur": (3, 6),      # ce qu'une voie fermee couvre, en tuiles
    "par_ville": (10, 60),   # les CANDIDATES ; la graine du jour en tire une
    "ecart": 20,             # deux chantiers ne se voisinent pas
    "raison": "TRAVAUX — UNE VOIE FERMÉE",
    "degats": 8,             # ce qu'on laisse en poussant les cones
}

#: **LA RUE BARREE.** L'autre visage de l'entrave, et le seul qui PEUT couper
#: la ville : on ferme la chaussee ENTIERE sur quelques tuiles. Le champ de
#: direction perd donc des fleches, et `voies_bloquees` doit encore rendre deux
#: ensembles vides — c'est le juge de M1, et il tranche ici, une fois, a la
#: construction.
#:
#: ⚠️ **Elle couvre TOUT LE TRONCON, d'un croisement a l'autre** — et ce n'est
#: pas une largesse de dessin, c'est la seule forme qui marche. Mesure : barrer
#: la moitie d'un troncon laisse l'autre moitie en CUL-DE-SAC dans les deux
#: sens (la voie qui monte n'a plus d'entree, celle qui descend n'a plus de
#: sortie) — le juge de connexite refusait les vingt-six premieres candidates,
#: toutes pour cette raison. Fermee en entier, la rue disparait du graphe et la
#: grille route autour : c'est d'ailleurs ce que « rue barree » veut dire.
#:
#: ⚠️ Elle part donc d'un croisement, ce qui fait aussi que **le trafic n'y
#: entre jamais** : une sortie barree n'est pas une sortie (`peutSortir`), donc
#: les chars tournent AVANT, au croisement, comme devant un vrai detour.
#:
#: ⚠️ `candidates` borne ce qu'on ESSAIE : le juge de connexite coute 14 ms, et
#: en tester deux cents doublerait le temps de batir la ville.
FERMETURES: dict = {
    "long_max": 26,          # au-dela, ce n'est plus une rue barree, c'est un quartier
    "candidates": 20,        # ce qu'on soumet au juge, au plus
    "par_ville": (1, 8),     # ce qu'on en garde
    "ecart": 40,
    "raison": "RUE BARRÉE — DÉTOUR",
    "degats": 14,            # une barricade, ca coute plus cher que des cones
}

#: **LA FOIRE DE LA POINTE.** ⚠️ On n'agrandit pas la grille : la lecon de l'ile
#: vaut ici aussi — la ville a la place, il faut la DEPENSER. La foire prend une
#: des taches de bois du district-parc (un glyphe `n` du plan devient `f`).
#:
#: ⚠️ **UNE FOIRE, C'EST BEAUCOUP DE CHOSES ET BEAUCOUP DE MONDE** — retour de
#: Martin, capture a l'appui (« c'est assez decevant », « plein de kiosques, de
#: vendeurs, de mascottes », « de l'exageration »). La premiere version posait
#: SEPT objets tires au hasard sur 80 x 33 tuiles de gazon : elle ecrivait « une
#: allee bordee de choses » dans son commentaire et faisait l'inverse dans son
#: code. Ce qu'on voyait etait un terrain vague avec une roue perdue au milieu.
#:
#: ⚠️ Ce qui fait une foire, dans l'ordre ou l'oeil le lit :
#:   1. **l'allee BORDEE des deux cotes**, un kiosque tous les `pas_kiosque` pas,
#:      sans un trou — c'est la densite qui dit « foire », pas les objets ;
#:   2. **un vendeur derriere CHAQUE comptoir** — peint dans le kiosque, pas une
#:      entite : trente vendeurs a trente entites mangeraient le budget d'images
#:      de toute la rue pour des gens qui ne bougent pas ;
#:   3. **les manèges EN DOUBLE** derriere les kiosques, et la grande roue en
#:      point de repere au bout de l'allee ;
#:   4. **la lumiere la nuit** : une guirlande a chaque kiosque, et chaque manège
#:      eclaire — une foire eteinte a 21 h 50 est exactement la capture de Martin ;
#:   5. **la foule et les mascottes** (`pietons.FOIRE`), qui naissent DANS la
#:      foire au lieu d'y passer par hasard.
FOIRE: dict = {
    "allee": 3,               # la largeur de l'allee centrale, en tuiles
    # ⚠️ COMPACTE : l'enceinte ne prend pas le bloc entier (80 x 33), elle en
    # prend le milieu — le reste redevient le bois de La Pointe.
    # ⚠️ Mesure a l'ecran, pas au gout : a 54 x 24 le fond nord restait un grand
    # gazon noir derriere les kiosques. A 50 x 21, les manèges sont JUSTE
    # derriere les comptoirs, et l'ecran (30 x 17 tuiles) montre la foire entiere.
    # ⚠️ PUIS 52 x 31, et ce n'est pas la foire qui s'etale : Martin a demande
    # « un petit train qui fait le tour de la foire et une enorme montagne
    # russe ». Le train veut une rangee de voie de chaque cote (a trois tuiles
    # du bord : la palissade rentre de deux) ; la montagne russe veut cinq rangs
    # au nord, derriere les manèges. Rien d'autre ne s'ecarte : l'allee, les
    # comptoirs et les manèges gardent leurs pas. Et on ne s'etend ni a l'est
    # (l'elan du pont) ni au-dela du bloc (33 rangs, une tuile de marge).
    "enceinte": (52, 31),
    "marge_ouest": 3,         # l'enceinte se cale a l'ouest : l'est est l'elan du pont
    "pas_kiosque": 3,         # un kiosque tous les trois pas, des deux cotes
    # ⚠️ Neuf kiosques a manger ou a gagner, et les trois jeux d'adresse. La
    # POUTINE et les QUEUES DE CASTOR ne sont pas du decor exotique : c'est ce
    # qu'on mange dans une foire au Quebec.
    "kiosques": ("barbe_a_papa", "hot_dogs", "pop_corn", "limonade", "poutine",
                 "queues_de_castor", "ballons", "peluches", "lance_anneaux"),
    "jeux": ("galerie_tir", "marteau_force", "peche_canards"),
    # ⚠️ Du DECOR ANIME, et on n'y monte PAS : un manège ou l'on monte et qui ne
    # donne rien est un decor cher ; un manège qui tourne avec du monde dessus
    # est une ville qui vit. EN DOUBLE : l'exageration est le propos.
    "manèges": ("carrousel", "tasses", "chaises_volantes",
                "chaises_volantes", "carrousel", "tasses"),
    "pas_manege": 7,          # l'espacement des manèges, juste derriere les kiosques
    "tables": 9,              # la cour a manger, pres de l'arche
    "arbres": 40,             # ce qui reste du bois, autour de la palissade
    # Les guirlandes : trois couleurs qui alternent d'un kiosque a l'autre.
    "lampes": ("foire_jaune", "foire_rose", "foire_bleue"),
    "rayon_lampe": 56,
    "rayon_manege": 58,
    # ⚠️ **LE PETIT TRAIN FAIT LE TOUR DE LA FOIRE** — Martin. Une voie fermee,
    # une tuile d'epais, a `retrait` tuiles du bord de l'enceinte : la palissade
    # rentre de 0 a 2, donc la voie ne la touche jamais, et elle COUPE l'allee
    # d'entree — la premiere chose qu'on voit en passant l'arche, c'est le train.
    # ⚠️ Il S'ARRETE devant quelqu'un et siffle : un train de foire ne renverse
    # personne. Et on ne passe pas A TRAVERS un wagon (`Foire.bloquer`).
    # ⚠️ **ON Y MONTE** (Martin : « qu'on puisse y faire un tour ») : il marque
    # l'arret a sa GARE a chaque tour, le quai au nord de la voie, a l'ouest de
    # l'allee d'entree — la locomotive s'arrete `gare_recul` tuiles a l'ouest de
    # l'arche, et son dernier wagon reste hors de l'allee. On monte a ACTION,
    # on fait le tour, on descend au meme quai.
    "train": {
        "retrait": 3,
        "wagons": 4,
        "vitesse": 0.8,         # px par image : le pas d'un enfant qui court
        "reprise": 0.02,        # ce qu'il reprend par image apres un arret
        # ⚠️ 20 et non plus 15 : les wagons sont des machines de 16 px de long
        # (la locomotive 20), plus des grilles de 12 — a 15, ils se chevauchaient.
        "ecart_px": 20,         # d'un wagon au suivant, attelage compris
        "regard_px": 34,        # ce que la locomotive surveille devant elle
        "sifflet_images": 150,  # pas deux coups de sifflet en deux secondes et demie
        "gare_recul": 9,        # la locomotive en gare, en tuiles a l'ouest de l'arche
        "gare_images": 360,     # six secondes a quai : le temps de monter
        "rayon_monter_px": 22,  # d'un wagon arrete, on y monte
    },
    # ⚠️ **L'ENORME MONTAGNE RUSSE** — Martin. La plus haute chose de la ville :
    # la grande roue fait 92 px de haut, le sommet de la chaine en fait 150, et
    # elle est plus LARGE que l'ecran (30 tuiles). Un aller et un retour a
    # quatre rangs l'un de l'autre, un looping, une bosse, et la gare a l'ouest.
    # ⚠️ ELLE EST EN L'AIR : on passe dessous, et seuls ses PIEDS arretent
    # (`pied_montagne_russe`, un par tuile). ⚠️ Python trace la voie entiere
    # (x, y, z) et la juge — hauteur, looping, pieds sous chaque metre en l'air ;
    # le navigateur ne fait que la peindre et y faire rouler les chariots.
    "montagne_russe": {
        "largeur": 38,          # tuiles, virages compris
        "rangs": 5,             # de l'aller au retour, virages compris
        "hauteur_px": 150,      # le sommet de la chaine
        "boucle_px": 44,        # le rayon du looping
        "pas_px": 4,            # la voie exportee, un point tous les 4 px (en 3D)
        "pied_px": 32,          # un pied tous les deux metres de voie en l'air
        "pied_des_px": 14,      # sous cette hauteur, la voie pose sur son lit
        "chariots": 4,
        # ⚠️ 17 et non plus 13 : les chariots sont des machines de 14 px de long
        # (`FOIRE_EN_VOLUME.chariot`), plus des grilles de 11 — et cernes de noir, a
        # 16 ils se touchaient et le train se lisait comme une seule bete.
        "ecart_px": 17,
        # ⚠️ **ON Y MONTE** (Martin : « pareil pour la montagne russe ») : a quai,
        # a ACTION pres d'un chariot, pour un tour complet — et on descend a la gare.
        "rayon_monter_px": 22,
        # ⚠️ Des px par image, et la gravite en px par image au carre :
        # v²/2 + g·z se conserve. Du sommet (150) au creux (26), elle file a
        # plus de quatre px et demi par image — huit fois la chaine.
        # ⚠️ Le frottement est TOUT PETIT, et c'est mesure : a 0,0006 le chariot
        # arrivait en haut du looping a la vitesse plancher — il ne l'aurait pas
        # passe sans elle. A 0,0002, il y passe encore a 2,4.
        # ⚠️ `vitesse_chaine` et pas `chaine` : `chaine` est la TRANCHE de voie
        # (des indices) dans le paquet, et la fiche l'ecrasait en s'y fusionnant.
        "vitesse_chaine": 0.55,
        "depart": 1.0,
        "gravite": 0.085,
        "frottement": 0.0002,
        "vitesse_min": 0.7,
        "vitesse_max": 6.0,
        "gare_images": 240,     # quatre secondes en gare
    },
}

def voie_de_montagne_russe(tx0: int, ty0: int, fiche: dict | None = None) -> dict:
    """La voie ENTIERE de la montagne russe dont le coin nord-ouest est la tuile
    (tx0, ty0), dans le sens ou roulent les chariots.

    Rend `voie` — des points [x, y, z] en pixels du monde, un tous les `pas_px`
    MESURES EN 3D : une chaine qui grimpe a 45° n'est pas plus courte qu'une
    allee, et le navigateur en tire la vitesse par l'energie —, les tranches
    `gare`, `chaine` et `boucle` en indices, et `supports` : [indice, tx, ty],
    le point de voie que porte chaque pied et la tuile ou il pose.

    ⚠️ LE HAUT DERRIERE, LE BAS DEVANT — et c'est ce que le premier dessin
    faisait a l'envers. En trois-quarts, ce qui monte monte VERS LE HAUT DE
    L'ECRAN : la chaine posee sur la ligne de devant (au sud) traversait le
    looping et la ligne du fond en diagonale, et on voyait un noeud au lieu
    d'une montagne russe. La chaine est donc au NORD (le retour du dessin
    d'avant), et le looping et la bosse au SUD, devant elle.

    Dans le sens de la marche : la gare au bout ouest de la ligne sud ; le
    virage de l'ouest au ras du sol ; la CHAINE au nord, vers l'est, jusqu'au
    sommet ; la plongee dans le virage de l'est, qui remonte ; la ligne sud vers
    l'ouest — une descente, le LOOPING, une bosse — et le frein de la gare.
    ⚠️ Le looping est dans le plan x-z : vu en trois-quarts, c'est un cercle
    debout — la meme lecture que la grande roue, et c'est ce qui dit « montagne
    russe » a deux cents pixels. Il DERIVE de `derive` px en un tour : l'entree
    et la sortie ne tombent pas au meme endroit, comme sur une vraie."""
    f = fiche or FOIRE["montagne_russe"]
    haut, rayon = f["hauteur_px"], f["boucle_px"]
    y_nord = ty0 * TUILE_PX + 12
    y_sud = (ty0 + f["rangs"] - 1) * TUILE_PX + 12
    rv = (y_sud - y_nord) / 2                         # le rayon des virages
    y_mil = (y_nord + y_sud) / 2
    x_ouest = tx0 * TUILE_PX + 8 + rv
    x_est = (tx0 + f["largeur"] - 1) * TUILE_PX + 8 - rv
    long_ = x_est - x_ouest
    derive = 24

    def profil(points: tuple, u: float) -> float:
        for (u0, z0), (u1, z1) in zip(points, points[1:]):
            if u <= u1:
                return z0 + (z1 - z0) * (u - u0) / (u1 - u0)
        return points[-1][1]

    # Les hauteurs le long de chaque ligne, de 0 (son debut) a 1 (sa fin).
    devant = ((0.0, 64), (0.16, 12), (0.22, 8), (0.50, 8), (0.62, 42), (0.74, 8),
              (0.80, 4), (1.0, 4))
    fond = ((0.0, 6), (0.08, 8), (0.12, 12), (0.62, haut - 8), (0.66, haut), (0.72, haut),
            (0.95, 20), (1.0, 26))
    u_boucle = 0.34

    bruts: list[tuple[float, float, float, str]] = []
    x, x_boucle, bouclee = x_est, x_est - u_boucle * long_, False
    while x > x_ouest:                                # 1. devant, vers l'ouest
        u = (x_est - x) / long_
        if not bouclee and x <= x_boucle:
            k = int(2 * math.pi * rayon)
            for i in range(k):
                phi = 2 * math.pi * i / k
                bruts.append((x_boucle - rayon * math.sin(phi) - derive * phi / (2 * math.pi),
                               y_sud, 8 + rayon * (1 - math.cos(phi)), "boucle"))
            x, bouclee = x_boucle - derive, True
            continue
        bruts.append((x, y_sud, profil(devant, u), "gare" if 0.82 <= u <= 0.97 else ""))
        x -= 1
    m = int(math.pi * rv)
    for i in range(m):                                # 2. le virage de l'ouest, au ras du sol
        a = math.pi / 2 + math.pi * i / m
        bruts.append((x_ouest + rv * math.cos(a), y_mil + rv * math.sin(a), 4 + 2 * i / m, "virage"))
    n = int(long_)
    for i in range(n):                                # 3. le fond, vers l'est : la chaine
        u = i / n
        bruts.append((x_ouest + i * long_ / n, y_nord, profil(fond, u),
                      "chaine" if 0.12 <= u <= 0.64 else ""))
    for i in range(m):                                # 4. le virage de l'est, qui remonte
        a = -math.pi / 2 + math.pi * i / m
        bruts.append((x_est + rv * math.cos(a), y_mil + rv * math.sin(a),
                      26 + (64 - 26) * i / m, "virage"))

    # ⚠️ ON ARRONDIT LES CASSURES, pas le looping : les hauteurs sont posees par
    # segments droits, et un segment droit qui rencontre un palier fait un
    # angle — un chariot qui y passe decolle a l'oeil. Une moyenne glissante
    # sur deux dizaines de pixels, en rond (la voie est fermee), et le looping
    # (deja lisse) ne se melange pas a ses voisins.
    nb = len(bruts)
    lisses = []
    for i, (bx, by, bz, quoi) in enumerate(bruts):
        if quoi == "boucle":
            lisses.append((bx, by, bz, quoi))
            continue
        voisins = [bruts[(i + d) % nb][2] for d in range(-12, 13) if bruts[(i + d) % nb][3] != "boucle"]
        lisses.append((bx, by, sum(voisins) / len(voisins), quoi))

    # Le reechantillonnage, tous les `pas_px` en 3D.
    cumul = [0.0]
    for i in range(nb):
        a, b = lisses[i], lisses[(i + 1) % nb]
        cumul.append(cumul[-1] + math.dist(a[:3], b[:3]))
    total = cumul[-1]
    voie: list[list[float]] = []
    etiquettes: list[str] = []
    j = 0
    for k in range(int(total // f["pas_px"])):
        cible = k * f["pas_px"]
        while cumul[j + 1] < cible:
            j += 1
        a, b = lisses[j], lisses[(j + 1) % nb]
        t = (cible - cumul[j]) / max(1e-9, cumul[j + 1] - cumul[j])
        # ⚠️ En pixels ENTIERS : le dessin arrondit de toute facon, et une
        # decimale coutait 700 octets gzip au paquet (sur un plafond de 70 Ko).
        voie.append([round(a[i] + (b[i] - a[i]) * t) for i in range(3)])
        etiquettes.append(a[3])

    def tranche(quoi: str) -> list[int]:
        indices = [i for i, e in enumerate(etiquettes) if e == quoi]
        return [indices[0], indices[-1]]

    # ⚠️ LES PIEDS : un tous les `pied_px` de voie en l'air, et seulement la ou
    # la voie passe AU-DESSUS du centre d'une tuile (a trois px pres) — un pied
    # d'acier est d'aplomb, pas en biais. Dans le looping, seuls les flancs du
    # bas en ont : le haut du cercle ne repose sur rien.
    supports: list[list[int]] = []
    dernier = -10**9
    for i, (px, py, pz) in enumerate(voie):
        if pz <= f["pied_des_px"] or i * f["pas_px"] - dernier < f["pied_px"]:
            continue
        if etiquettes[i] == "boucle" and pz > 8 + rayon:
            continue
        tx, ty = int(px // TUILE_PX), int((py - 4) // TUILE_PX)
        if math.hypot(px - (tx * TUILE_PX + 8), py - (ty * TUILE_PX + 12)) > 3:
            continue
        supports.append([i, tx, ty])
        dernier = i * f["pas_px"]
    return {"voie": voie, "gare": tranche("gare"), "chaine": tranche("chaine"),
            "boucle": tranche("boucle"), "supports": supports,
            "zone": {"x": tx0, "y": ty0, "l": f["largeur"], "h": f["rangs"]}}


#: **LES AMARRAGES.** Ou une chaloupe attend. ⚠️ La coque est passee en phase 1
#: le 16 sept. 2026 (la dette de M3) : il lui fallait un endroit ou la trouver,
#: sinon un vehicule de plus dans le catalogue ne change rien a la ville.
#:
#: ⚠️ **Sur l'eau, contre la rive BATIE** — pas contre le sable. On amarre a un
#: quai, a un trottoir du port, a une allee ; on ne s'amarre pas a une plage, on
#: y echoue. C'est la meme mesure que les poteaux d'amarrage de la greve : 222
#: tuiles de rive batie sur toute la ville, dont 199 de trottoir.
AMARRAGES: dict = {
    "par_ville": (6, 18),
    "ecart": 26,              # deux chaloupes ne se collent pas bord a bord
}

#: **LES PLAGES : PEU, MAIS LARGES.** Retour de Martin : « moins de plage autour,
#: et des accessoires de plage et des gens s'il y a beaucoup de place, pas juste
#: des petits morceaux de plage ».
#:
#: ⚠️ **Mesure, sur la graine livree** : 1 754 tuiles de sable en **65 morceaux**,
#: dont **41 de moins de dix tuiles**. `_eau()` bordait CHAQUE cote de chaque
#: bassin d'une bande de zero a quatre tuiles qui avancait et reculait au hasard
#: — jusque dans le chenal de La Pointe, des deux rives. Ce qu'on voyait etait
#: un liseré dechiquete autour de toute l'eau, et les 104 meubles de plage
#: tombaient tous sur ces bandes etroites : une serviette sur trois tuiles de
#: sable entre un trottoir et la baie n'est pas une plage.
#:
#: ⚠️ **Une plage demande DU LARGE devant elle** : jamais dans un chenal, ou le
#: sable des deux rives finirait par se toucher (le pont de La Pointe doit rester
#: le seul chemin). La profondeur qu'un bassin peut donner est donc un tiers de
#: sa largeur quand il y a une rive en face, la moitie quand il n'y en a pas — et
#: sous `profondeur[0]`, ce cote n'a pas de plage du tout.
#:
#: ⚠️ **Et du RIVAGE derriere elle** : le plus long bout de cote d'un seul tenant,
#: pas la somme des bouts. Ailleurs, la ville touche l'eau sans sable — un
#: trottoir au bord de l'eau, comme au quai.
PLAGES: dict = {
    "profondeur": (5, 8),     # en tuiles, au milieu de la plage
    "longueur": (26, 44),     # le long de la cote
    "rampe": 5,               # les deux bouts s'amincissent sur tant de tuiles
    # ⚠️ Ce qu'une plage doit compter de tuiles pour exister. En dessous, le
    # cote reste sans sable : c'est « beaucoup de place », ecrit en chiffres.
    "place": 120,
}

#: **LA GREVE SE MEUBLE.** ⚠️ Mesure d'abord, et c'est elle qui a decide de la
#: vague : la ville pose deja **2 507 tuiles de sable** (dont 782 touchent
#: l'eau) et **1 818 tuiles de quai** — et personne ne s'y assoit jamais. Ce qui
#: manquait n'etait pas le terrain, c'etait que le bord de l'eau soit un endroit
#: **ou l'on va** au lieu d'un decor qu'on traverse.
#:
#: ⚠️ **UNE PLAGE SUIT LA COTE ; ELLE NE SUIT PAS UNE BOITE.** La phrase est
#: deja dans `_eau()`, et elle y a coute douze bancs de sable en pleine baie. Le
#: semis marche donc **tuile par tuile**, et il ne meuble une tuile de sable que
#: si l'eau est a `bord` tuiles de la — jamais sur le rectangle d'un bassin. Un
#: parasol plante au milieu d'un sentier du bois dit le contraire de ce qu'on
#: veut.
#:
#: ⚠️ **Et il passe APRES `boucher_les_poches`** : on ne meuble pas un terrain
#: que la ville va encore retirer — ce bouchage-la noie les bancs de sable
#: isoles, un par un. Mesure : semer avant n'en noie aujourd'hui aucun (huit
#: graines, 1 139 meubles). C'est donc une precaution, pas un correctif, et elle
#: ne coute rien.
#: ⚠️ **CE QUI A LE DROIT DE FLOTTER, ecrit en PYTHON.** La bouee est le premier
#: decor du jeu pose sur l'eau, et le juge qui tient depuis M1 — « tout decor est
#: sur une tuile marchable » — l'a arretee net. Ce juge a raison sur le fond (un
#: decor ne bouche ni la rue ni les portes) : ce n'est pas lui qu'on jette, c'est
#: l'exception qu'on DECLARE. Elle vit ici, le paquet la porte, et un juge de banc
#: verifie que le `flotte` des fiches de dessin dit exactement la meme chose —
#: sinon on aurait deux listes et, un jour, deux verites.
FLOTTANTS: tuple[str, ...] = ("bouee",)

GREVE: dict = {
    # A quelle distance de l'eau le sable est une GREVE. ⚠️ Toute la profondeur
    # d'une plage (`PLAGES`) : a trois tuiles, le fond d'une plage de huit
    # restait nu, et on revenait aux petits morceaux par l'autre bout.
    "bord": PLAGES["profondeur"][1],
    "ecart": 3,              # deux meubles de plage ne se collent pas
    # Ce qu'on seme, et sa chance par tuile de greve. ⚠️ Seulement sur une plage
    # DECLAREE (`PLAGES`) — c'est la que Martin veut « des accessoires ». Le
    # parasol se lit de loin, donc il ne domine pas : une grève qui en porte un
    # tous les trois pas n'est pas une plage, c'est un stationnement de parasols.
    # ⚠️ Le chateau PASSE EN PREMIER : il ne se tire que sur le sable mouille
    # (`chateau_bord`), et tire en dernier il ne gagnait presque jamais — deux
    # chateaux pour cinq plages, et les enfants n'avaient rien a rebatir.
    "chances": {
        "chateau_sable": 0.060,
        "parasol": 0.050,
        "serviette": 0.060,
        "chaise_longue": 0.050,
        "table_pique_nique": 0.030,
        "kayak": 0.015,
    },
    # ⚠️ LA CHAISE DU SAUVETEUR : une par plage, au milieu, et posee AVANT le
    # semis — c'est elle qui dit « on se baigne ici » d'un bout a l'autre de
    # l'ecran, et le semis s'en ecarte tout seul.
    "sauveteur": "chaise_sauveteur",
    # ⚠️ Le chateau se batit AU BORD, la ou le sable est mouille — a deux
    # tuiles de l'eau, pas a huit. C'est la seule des quatre a le demander.
    "chateau_bord": 2,
    # Le quai : une bouee a l'eau, un poteau d'amarrage sur les planches.
    # ⚠️ Un poteau tous les quelques pas n'est pas un quai, c'est une palissade :
    # ces deux chances-la ne valent que sur le BORD du quai, la ou l'eau touche.
    "quai_poteau": 0.06,
    "quai_bouee": 0.07,
    # ⚠️ ET ESPACES, DEPUIS QUE LA RIVE EST NUE. Tant qu'une bande de sable
    # longeait toute l'eau, presque aucun trottoir ne la touchait ; sans elle,
    # le chenal de La Pointe s'est couvert d'un poteau tous les trois pas
    # (mesure : (387, 121), (393, 121), (396, 121), (399, 121)) — la palissade
    # que le quai a deja appris a ne pas planter. Une borne ARRETE un pieton,
    # et le trottoir n'a qu'une tuile.
    "poteau_ecart": 11,
    "bouee_ecart": 6,
    # Le belvedere : la ou la terre DOMINE l'eau. On en veut peu, et espaces.
    "belvederes": (3, 9),
    "belvedere_ecart": 40,
    # ⚠️ Le pied d'un pont n'est pas une plage : un char lance qui traverse
    # accroche ce qui traine a cote du tablier, et le juge du pont l'a vu
    # avant nous (la carrosserie tombait a 90 apres l'ouverture du pont).
    "pont_ecart": 3,
}

#: Tout ce qui se pose AU BORD DE L'EAU, d'ou que ca vienne — c'est la liste que
#: lit la regle d'ecart. ⚠️ Elle existe parce que la greve n'est plus seule a
#: meubler la rive : depuis que le quai touche l'eau, `_meubler_le_quai` pose
#: ses bornes d'amarrage le long de la levre bien AVANT le passage de la greve,
#: et `greve()` ne comptait que ses propres poses. Deux bornes se sont
#: retrouvees collees — (5, 181) et (6, 182) — sans qu'aucun des deux semis ne
#: l'ait fait tout seul, et le juge « deux meubles de plage ne se collent pas »
#: est tombe sur une paire dont personne n'etait responsable.
MEUBLES_DU_BORD = ("parasol", "serviette", "table_pique_nique", "chateau_sable",
                   "chaise_longue", "kayak", "chaise_sauveteur",
                   "poteau_amarrage", "bouee", "belvedere", "pneu")

#: Le decor qui ARRETE UN PIETON. ⚠️ La solidite d'un decor vit dans sa fiche de
#: DESSIN (`DECORS`, sprites.js) — le generateur, lui, ne la connaissait pas, et
#: c'est ce qui lui a permis de murer une partie de la ville sans s'en
#: apercevoir : 191 tuiles de quai inatteignables a pied, en une quarantaine de
#: poches, derriere des caisses et des bornes d'amarrage. Retour de Martin :
#: « impossible d'aller sur une partie du quai, il est cloture, sans chemin a
#: pied ».
#:
#: ⚠️ **DEUX VERITES, DONC UN JUGE** — meme parade que `FLOTTANTS` : la liste
#: vit ici, le paquet la porte, et un juge de banc verifie qu'elle dit
#: exactement ce que disent les fiches de dessin. Une liste qu'on oublie de
#: tenir a jour est pire que pas de liste : elle laisserait `degager_le_decor`
#: croire qu'on passe la ou l'on ne passe pas.
DECOR_SOLIDE = frozenset({
    # L'edicule du metro : une entree vitree sur l'abord, qu'on contourne.
    "edicule", "edicule_nord",
    # Le mobilier de rue : un banc et un abribus REGARDENT la rue, donc ils ont
    # un dessin par cote du trottoir (`mobilier.BANCS_PAR_COTE`, `autobus.ABRIS`).
    "banc_nord", "banc_est", "banc_ouest",
    "abribus", "abribus_nord", "abribus_est", "abribus_ouest",
    "arbre", "banc", "baril", "bbq", "belvedere", "borne_fontaine", "cabanon",
    "caisse", "carrousel", "chaise_sauveteur", "chaises_volantes", "distributrice_cafe",
    "distributrice_grignotines", "distributrice_liqueur", "fontaine", "galerie_tir",
    "grande_roue", "guichet", "lampadaire", "marteau_force", "ordures",
    "peche_canards", "poteau_amarrage", "poubelle", "table_pique_nique", "tasses",
    # Les neuf kiosques de la foire : un comptoir, ca arrete un pieton.
    "ballons", "barbe_a_papa", "hot_dogs", "lance_anneaux", "limonade", "peluches",
    "pop_corn", "poutine", "queues_de_castor",
    # Le pied d'acier de la montagne russe : la voie est en l'air, lui non.
    "pied_montagne_russe",
    # Des quartiers qu'on reconnait : la poubelle qui deborde (pauvre), le bac a
    # fleurs (cossu), le caddie renverse au pied des plex. Le matelas, couche a
    # plat, ne l'est pas : on marche dessus, comme sur le pneu.
    "bac_fleurs", "caddie", "poubelle_pleine",
    # Le mobilier de l'usage (2e vague) : la benne et les palettes arretent un
    # pieton. ⚠️ Le parcometre, la boite aux lettres et le bac de recyclage, non :
    # des poteaux et des bacs bas qu'on frole — un abord ou l'on reste coince sur
    # un poteau tous les huit pas n'est plus un endroit ou l'on deborde.
    "benne", "palettes",
})

#: **LE BRIS D'AQUEDUC.** Le troisieme visage de l'entrave, et le seul qui ne
#: soit ni prevu ni pose par personne : une conduite lache sous la chaussee, la
#: rue gicle, et la ville met presque une heure a fermer la vanne.
#:
#: ⚠️ **Ce n'est pas un chantier, et c'est tout le point.** L'entrave du jour et
#: la rue barree sont tirees a l'aube et tiennent la journee ; celui-ci arrive a
#: une HEURE, comme le char en panne — on roulait, la rue etait libre, elle ne
#: l'est plus. Ni cones, ni panneau DETOUR : une gerbe d'eau et un trou.
#:
#: ⚠️ **Un bris ne coupe jamais la ville, et il ne le peut pas PAR
#: CONSTRUCTION** — c'est l'argument des entraves, repris tel quel. Le trou ne
#: couvre QU'UNE tuile, et cette tuile a une voisine PARALLELE qui va dans le
#: meme sens : le champ de direction ne bouge pas d'une fleche, `voies_bloquees`
#: rend exactement ce qu'il rendait, et on se passe du juge de connexite (14 ms
#: piece) a la construction. La flaque, elle, deborde sur les tuiles d'a cote —
#: mais elle ne fait que se VOIR : on roule dedans, on marche dedans.
#:
#: ⚠️ Et la gerbe n'est pas un dessin de plus : c'est le `jet_eau` de la
#: borne-fontaine defoncee, celui qui crache ses gouttes et TIENT son souffle
#: (`Son.SFX.borne_jet`, une fois par image, a distance). Un bris d'aqueduc est
#: cette gerbe-la, en pleine rue et pour une heure.
AQUEDUCS: dict = {
    "par_ville": (8, 30),      # les CANDIDATES ; la graine de l'heure en tire une
    "ecart": 30,               # deux bris ne se voisinent pas
    "chance_par_heure": 0.30,  # qu'une conduite lache, par heure de jeu
    "minutes": 55,             # ce que la ville met a fermer la vanne
    "flaque": 2,               # le rayon de l'eau repandue, en tuiles — du DESSIN
    "raison": "BRIS D'AQUEDUC",
    "degats": 6,               # ce qu'on laisse dans le trou en passant quand meme
}

NIDS_DE_POULE: dict = {
    "par_ville": (30, 90),   # ce qu'une ville en compte — un juge le compte
    "ecart": 7,              # en tuiles, entre deux nids
}

#: Les zones conditionnelles. ⚠️ **UNE BARRIERE EST UNE FICHE, PAS UN CAS.** La
#: ville est ouverte en entier depuis M1 et elle le restera : ce qu'une
#: barriere ajoute n'est pas une cloture, c'est une RAISON — un endroit qu'on
#: regarde trois jours avant d'y entrer. Chaque entree dit :
#:
#:   `ou`        un rectangle de tuiles, resolu par le chantier : le tablier
#:               d'un `pont`, la `grille` d'un lot, le batiment d'un `lieu`
#:               garanti (plus `marge` tuiles de cour), le `quai` qui porte un
#:               ambulant ;
#:   `arrete`    ce qu'elle arrete — `pieton`, `vehicule`, ou les deux. ⚠️ C'est
#:               la cle qui evite la moitie des pieges : un pont ferme aux
#:               CHARS mais pas aux JAMBES bloque sans jamais enfermer ;
#:   `condition` quand elle est FERMEE : `apres` (fermee tant qu'une mission
#:               n'est pas faite), `heure` (« jour » = ouverte le jour, fermee
#:               la nuit ; « nuit » l'inverse), `jour_tire` (la graine du jour,
#:               par ou les entraves de M12 entreront), `payer` (le comptoir
#:               d'un lieu — la guerite, deja ecrite) ;
#:   `forcer`    ce que ca coute de passer quand meme : `etoiles`, `degats` ;
#:               `None` pour ce qui ne se force pas ;
#:   `raison`    la ligne, en majuscules, qui s'affiche quand on s'y bute — et
#:               que le carnet liste.
#:
#: Seule la couronne du rectangle arrete, et seulement QUAND ON VIENT DE
#: L'EXTERIEUR : qui est dedans quand elle se ferme en sort librement. Un char
#: lance pousse les cones (`forcer.degats`) ; a pied, pousser une seconde puis
#: enjamber, et l'etoile tombe a la retombee. Le navigateur lit tout ca dans le
#: paquet (`Monde.barriereBloque`) ; rien n'y est ecrit en dur.
#:
#: ⚠️ Le juge qui compte (`test_barrieres`) : aucune combinaison de barrieres
#: fermees n'enferme la planque ni ne rend un lieu de mission inatteignable a
#: pied. ⚠️ `existant` : la guerite de la fourriere est deja jouee par
#: `majFourriere` (la geometrie du lot suffit) — la fiche la DECLARE, un juge
#: tient ses etoiles d'accord avec `economie.FOURRIERE`, et le navigateur ne la
#: rejoue pas une deuxieme fois.
#:
#: ⚠️ Le pont attend p02 (M16) : en attendant, il s'ouvre apres m2 — le fuyard
#: qu'on rattrape est deja une affaire de La Pointe. Les zones de gang et les
#: barrages a 5★ ne sont PAS ici : l'un est une menace, l'autre un char en
#: travers — ni l'un ni l'autre n'est un mur a condition.
BARRIERES: tuple[dict, ...] = (
    {"slug": "pont", "nom": "Le pont de La Pointe", "ou": {"pont": ("v", 17, 6)},
     "arrete": ("vehicule",), "condition": {"apres": "m2"},
     "forcer": {"degats": 12, "etoiles": 0}, "raison": "LES SKATEUX TIENNENT LE PONT",
     "decor": "cones"},
    {"slug": "fourriere", "nom": "La guérite de la fourrière", "ou": {"grille": "fourriere"},
     "arrete": ("vehicule",), "condition": {"payer": "fourriere"},
     "forcer": {"etoiles": economie.FOURRIERE["etoiles_vol"]}, "raison": "ON PAIE AU COMPTOIR",
     "decor": None, "existant": True},
    # ⚠️ `marge: 2` : la couronne passe a DEUX tuiles du mur, pour que la cour
    # (la ruelle devant, l'abord a cote) soit DEDANS — c'est la qu'on retombe
    # quand on enjambe, et c'est de la qu'on pousse la porte.
    {"slug": "usine", "nom": "La cour de l'usine Prévost", "ou": {"lieu": "usine", "marge": 2},
     "arrete": ("pieton", "vehicule"), "condition": {"heure": "jour"},
     "forcer": {"etoiles": 1}, "raison": "L’USINE EST FERMÉE LA NUIT", "decor": "chaine"},
    {"slug": "cargo", "nom": "Le quai du cargo", "ou": {"quai": "contrebande"},
     "arrete": ("pieton", "vehicule"), "condition": {"heure": "nuit"},
     "forcer": {"etoiles": 1}, "raison": "LE QUAI DÉCHARGE LA NUIT", "decor": "chaine"},
    # ⚠️ **L'ARCHE DE LA FOIRE** — Martin : « une entree avec une arche, et ca
    # doit couter quelque chose d'entrer ». Le billet vaut pour la JOURNEE
    # (`B.partie.billets`), et on ressort librement (`dedans` : le cote nord de
    # l'ouverture est la foire). Resquiller par la palissade coute l'etoile de
    # `forcer` a la retombee — la palissade s'enjambe comme les autres clotures.
    {"slug": "foire", "nom": "L'arche de la foire", "ou": {"foire": "entree"},
     "arrete": ("pieton", "vehicule"), "condition": {"payer": "foire"},
     "forcer": {"etoiles": economie.FOIRE["etoiles_resquille"]},
     "raison": f"LA FOIRE : {economie.FOIRE['entree']} $ L'ENTRÉE",
     "decor": None, "prix": economie.FOIRE["entree"], "dedans": "N"},
)

#: Les batiments garantis : un par majuscule du plan. `interieur` doit exister
#: dans INTERIEURS (juge `test_les_portes_menent_a_un_interieur`).
#: Les familles de lieux : une couleur, et le mot qui l'explique sur la carte.
#:
#: ⚠️ **La legende de la carte se construit d'ICI**, elle ne se recopie pas a la
#: main — sinon elle mentirait des le prochain lieu ajoute. La preuve etait deja
#: la : `COULEUR_BLIP` (hud.js) declarait dix lieux, la ville en compte seize, et
#: les six autres — depanneur, hotel, cantine, usine, phare, fourriere — tombaient
#: tous sur le meme gris par defaut. M8 en a ajoute cinq, M9 un sixieme, et
#: personne n'a touche a la table.
#:
#: ⚠️ Les couleurs sont des DONNEES, pas du dessin : elles descendent avec les
#: lieux (`Python decide, JS calcule`). Et un juge exige que chaque lieu declare
#: sa famille : ajouter un lieu sans couleur fait rougir le test, pas le joueur.
FAMILLES_DE_LIEU: dict[str, dict] = {
    "tes_places": {"couleur": "#e8b33c", "libelle": "TES PLACES"},
    "magasin": {"couleur": "#8ad26a", "libelle": "MAGASINS"},
    "manger": {"couleur": "#e8925a", "libelle": "MANGER"},
    "service": {"couleur": "#6f9fd8", "libelle": "SERVICES"},
    "soins": {"couleur": "#d86f7f", "libelle": "SOINS"},
    "transport": {"couleur": "#cdc6e6", "libelle": "TRANSPORT"},
    "travail": {"couleur": "#9a8fb0", "libelle": "TRAVAIL"},
    "repere": {"couleur": "#7fd4d0", "libelle": "REPÈRES"},
}

SPECIAUX: dict[str, dict] = {
    "T": {"slug": "terminus", "nom": "Terminus Baie-des-Brumes", "interieur": "terminus",
          "famille": "transport"},
    "M": {"slug": "armurerie", "nom": "Chez Gus", "interieur": "armurerie",
          "famille": "magasin"},
    "A": {"slug": "vetements", "nom": "Boutique Rosa", "interieur": "vetements",
          "famille": "magasin"},
    "G": {"slug": "garage", "nom": "Garage Rocco Bandini", "interieur": "garage",
          "porte_garage": True, "famille": "tes_places"},
    "K": {"slug": "planque", "nom": "La planque de Rocco", "interieur": "planque",
          "famille": "tes_places"},
    "P": {"slug": "poste", "nom": "Poste de police", "interieur": "poste",
          "famille": "service"},
    "H": {"slug": "hopital", "nom": "Hôpital de Baie-des-Brumes", "interieur": "hopital",
          "famille": "soins"},
    "B": {"slug": "bar", "nom": "Bar Le Brouillard", "interieur": "bar",
          "famille": "tes_places"},
    "C": {"slug": "casse_croute", "nom": "Casse-croûte du Faubourg", "interieur": "casse_croute",
          "famille": "manger"},
    # v2 / M8 — un point d'arret par district : on ne traverse pas la ville
    # pour un hot-dog ou pour sauver sa partie.
    "D": {"slug": "depanneur", "nom": "Dépanneur Chez Ti-Paul", "interieur": "depanneur",
          "genre": "banlieue", "famille": "magasin"},
    "L": {"slug": "hotel", "nom": "Hôtel Bandini", "interieur": "hotel",
          "famille": "tes_places"},
    "N": {"slug": "cantine", "nom": "Cantine des Quais", "interieur": "cantine",
          "genre": "hangars", "famille": "manger"},
    "U": {"slug": "usine", "nom": "Usine Prévost", "interieur": "usine",
          "genre": "industriel", "famille": "travail"},
    "V": {"slug": "phare", "nom": "Le phare de La Pointe", "interieur": "phare",
          "genre": "banlieue", "famille": "repere"},
    # v2 / M9 — le lot de la fourriere. Ce n'est pas un ilot bati : c'est une
    # cour d'asphalte cloturee avec une guerite, et `_fourriere()` la pose.
    "Y": {"slug": "fourriere", "nom": "Fourrière municipale", "interieur": "fourriere",
          "genre": "industriel", "famille": "service"},
    # v2 / M11 — le seul lieu neuf de la deuxieme vague. Une reparation de
    # televisions sur un lot d'entrepot de La Shop, avec une arriere-boutique.
    # ⚠️ C'est le TRAJET qui fait le risque : La Shop tombe a 0,15 la nuit, et
    # y aller quand il travaille, c'est y aller seul. Un comptoir de plus au
    # bar n'aurait rien coute a personne.
    "E": {"slug": "electronique", "nom": "Électronique Turcotte", "interieur": "electronique",
          "genre": "industriel", "famille": "service"},
}

FUSIONS = {"<": (-1, 0), "^": (0, -1)}

#: Les glyphes de plan qui sont de l'eau — une rue dont TOUS les blocs voisins
#: sont de l'eau est noyee : elle n'est pas batie, et personne n'y roule.
#:
#: ⚠️ **`j` EN FAIT PARTIE**, et ce n'est pas un abus de langage. Un quai sur
#: l'eau a AVALE la rangee d'eau sous lui : les deux tiers de sa hauteur sont la
#: baie, et le tiers qui reste est un TABLIER, pas une rue. Une rue qui ne
#: longerait que des blocs `j` est donc soit dans la baie (celle du pourtour
#: sud), soit en travers du port — et un quai ne se traverse pas en char, on y
#: descend depuis le boulevard de service qui le borde au nord. Les rues
#: verticales qui coupaient le quai deviennent ainsi des DARSES : de l'eau
#: entre deux appontements, ce qui est exactement ce qu'on veut y voir.
EAUX = "~j"

#: Les glyphes de plan qui font un QUAI — le plancher plein (`q`, qu'aucun
#: district n'emploie plus : un quai entoure de rues etait justement le defaut) et
#: le quai sur l'eau (`j`). ⚠️ Ce qui cherche « le quai » dans la ville
#: (la cale du contrebandier, entre autres) doit trouver les deux : le jour ou
#: `j` est ne, la barriere du cargo a cesse d'exister en silence.
QUAIS = "qj"


def _assembler(districts: tuple[dict, ...]) -> tuple[str, ...]:
    """Le plan de la ville : les districts poses cote a cote sur la grille.

    Leve ValueError si deux districts se marchent dessus, s'il reste un trou,
    ou si une fusion sort d'un district (elle irait chercher son maitre chez le
    voisin, et deplacer un quartier en casserait un autre).
    """
    nc = max(d["bx"] + len(d["plan"][0]) for d in districts)
    nr = max(d["by"] + len(d["plan"]) for d in districts)
    grille: list[list[str | None]] = [[None] * nc for _ in range(nr)]
    for district in districts:
        plan = district["plan"]
        largeur = len(plan[0])
        for j, ligne in enumerate(plan):
            if len(ligne) != largeur:
                raise ValueError(f"{district['slug']} : plan pas rectangulaire")
            for i, glyphe in enumerate(ligne):
                if glyphe == "<" and i == 0:
                    raise ValueError(f"{district['slug']} : fusion vers l'ouest hors du district")
                if glyphe == "^" and j == 0:
                    raise ValueError(f"{district['slug']} : fusion vers le nord hors du district")
                x, y = district["bx"] + i, district["by"] + j
                if grille[y][x] is not None:
                    raise ValueError(f"deux districts sur le bloc {(x, y)}")
                grille[y][x] = glyphe
    for y, ligne in enumerate(grille):
        for x, glyphe in enumerate(ligne):
            if glyphe is None:
                raise ValueError(f"aucun district sur le bloc {(x, y)}")
    return tuple("".join(ligne) for ligne in grille)


PLAN: tuple[str, ...] = _assembler(DISTRICTS)


def district_par_slug(slug: str) -> dict | None:
    for district in DISTRICTS:
        if district["slug"] == slug:
            return district
    return None


class Des:
    """Un generateur minuscule (LCG) — deterministe et lisible, sans `random`.

    Le hasard de la ville doit donner LA MEME ville a chaque demarrage du
    serveur : `random` suit un etat global que n'importe quel import pourrait
    bouger. Ici, la graine entre et rien d'autre.
    """

    def __init__(self, graine: int) -> None:
        self.etat = graine & 0xFFFFFFFF

    def suivant(self) -> int:
        self.etat = (self.etat * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.etat

    def flottant(self) -> float:
        return self.suivant() / 4294967296.0

    def entier(self, a: int, b: int) -> int:
        """Entre a et b, bornes comprises."""
        if b <= a:
            return a
        return a + self.suivant() % (b - a + 1)

    def chance(self, p: float) -> bool:
        return self.flottant() < p

    def choix(self, options):
        return options[self.suivant() % len(options)]

    def brule(self, combien: int) -> None:
        """Avance le de de `combien` tirages, sans rien en faire.

        ⚠️ Ce n'est pas du remplissage : c'est ce qui permet de changer une
        decision sans DECALER tout ce qui vient apres. Le de principal porte
        toute la suite du hasard (`batiment_forme` l'ecrit deja : « un tirage de
        moins (ou de plus) dans ce de-la decalerait toute la suite ») : qui cesse de
        tirer decale les gabarits, les parcelles et le decor de TOUT ce qui se
        genere apres lui, a l'autre bout de la ville. Mesure a l'appui, en
        supprimant les tirages du barbele et du terrain vague : douze scenes
        d'amuseur disparaissaient du Faubourg et le juge « un amuseur nait au
        centre-ville » tombait — pour une histoire de cloture.

        On brule donc ce qu'on ne tire plus, et on le dit ici plutot que de
        laisser une boucle morte sur place.
        """
        for _ in range(combien):
            self.suivant()


def _coupe(largeur: int, vertical: bool) -> list[tuple[str, str]]:
    """La coupe d'une rue : (glyphe, fleche) pour chaque tuile de sa largeur.

    ⚠️ Le marquage se peint sur le BORD de la tuile : la ligne centrale tombe
    donc ENTRE les deux sens, et non au milieu d'une voie.
    """
    voies = largeur - 2 * TROTTOIR
    moitie = voies // 2
    sortie = []
    for d in range(largeur):
        if d < TROTTOIR or d >= largeur - TROTTOIR:
            sortie.append((".", "."))
            continue
        k = d - TROTTOIR
        if vertical:
            glyphe = "#" if k == 0 else ("*" if k == moitie else "|")
            sortie.append((glyphe, "v" if k < moitie else "^"))
        else:
            glyphe = "#" if k == 0 else ("+" if k == moitie else "-")
            sortie.append((glyphe, "<" if k < moitie else ">"))
    return sortie


def regions_du_plan(plan: tuple[str, ...]) -> dict[tuple[int, int], tuple[int, int]]:
    """Pour chaque bloc, le bloc « maitre » de sa region (lui-meme, ou celui
    qui l'a avale). Leve ValueError si une fusion ne fait pas un rectangle."""
    maitre: dict[tuple[int, int], tuple[int, int]] = {}
    for by, ligne in enumerate(plan):
        for bx, glyphe in enumerate(ligne):
            if glyphe in FUSIONS:
                dx, dy = FUSIONS[glyphe]
                voisin = (bx + dx, by + dy)
                if voisin not in maitre:
                    raise ValueError(f"fusion sans voisin en {(bx, by)}")
                maitre[(bx, by)] = maitre[voisin]
            else:
                maitre[(bx, by)] = (bx, by)
    groupes: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for cellule, chef in maitre.items():
        groupes.setdefault(chef, []).append(cellule)
    for chef, cellules in groupes.items():
        xs = {c[0] for c in cellules}
        ys = {c[1] for c in cellules}
        if len(cellules) != len(xs) * len(ys) or max(xs) - min(xs) + 1 != len(xs) \
                or max(ys) - min(ys) + 1 != len(ys):
            raise ValueError(f"la region {chef} n'est pas un rectangle : {sorted(cellules)}")
    return maitre


#: Les trois standings, par leur lettre dans `DISTRICTS[].standing`. ⚠️ Le `~`
#: n'en est pas un : c'est la lettre OBLIGEE d'un bloc d'eau, ou personne
#: n'habite. Tout autre bloc declare le sien — pas de defaut silencieux, sinon
#: un quartier oublie serait ordinaire sans que personne l'ait decide.
STANDINGS: dict[str, str] = {"+": "cossu", "=": "ordinaire", "-": "pauvre"}
#: Ce que portent une devanture et une residence qui ne sont pas ordinaires.
STANDING_LETTRE: dict[str, str] = {"cossu": "+", "pauvre": "-"}
SANS_STANDING = "~"


def _assembler_le_standing(districts: tuple[dict, ...], plan: tuple[str, ...]) -> tuple[str, ...]:
    """La grille de standing de la ville, bloc par bloc, alignee sur `plan`.

    Leve ValueError si une grille n'a pas la forme de son plan, si un bloc bati
    ne declare rien (ou l'eau quelque chose), ou si un bloc avale ne dit pas la
    meme chose que son maitre : un superbloc est UN lot, il n'a qu'un standing.
    """
    grille = [[""] * len(plan[0]) for _ in plan]
    for district in districts:
        standing = district.get("standing")
        if standing is None or len(standing) != len(district["plan"]) \
                or any(len(a) != len(b) for a, b in zip(standing, district["plan"])):
            raise ValueError(f"{district['slug']} : le standing n'a pas la forme du plan")
        for j, ligne in enumerate(standing):
            for i, lettre in enumerate(ligne):
                grille[district["by"] + j][district["bx"] + i] = lettre
    maitre = regions_du_plan(plan)
    for (bx, by), (mx, my) in maitre.items():
        lettre, du_maitre = grille[by][bx], grille[my][mx]
        if plan[my][mx] == "~":
            if lettre != SANS_STANDING:
                raise ValueError(f"le bloc d'eau {(bx, by)} declare un standing ({lettre!r})")
        elif lettre not in STANDINGS:
            raise ValueError(f"le bloc {(bx, by)} ne declare pas son standing ({lettre!r})")
        if lettre != du_maitre:
            raise ValueError(f"le bloc {(bx, by)} dit {lettre!r}, son maitre {(mx, my)} dit {du_maitre!r}")
    return tuple("".join(ligne) for ligne in grille)


STANDING: tuple[str, ...] = _assembler_le_standing(DISTRICTS, PLAN)

#: Les USAGES — ce qu'on fait la (des quartiers qu'on reconnait, 2e vague). ⚠️ On
#: n'invente pas de zonage : les lettres du `plan` en sont deja un, et l'usage
#: d'un bloc se DEDUIT de sa lettre (`usage_du_glyphe`). Ce qui est ecrit ici, ce
#: sont les couleurs du calque et les mots de la legende — des DONNEES qui
#: descendent avec la carte, comme `FAMILLES_DE_LIEU`. `lettre` : ce que porte la
#: grille du paquet (`grille.usage`), un caractere par bloc.
USAGES: dict[str, dict] = {
    "commercial": {"lettre": "c", "couleur": "#d0874a", "libelle": "COMMERCES"},
    "residentiel": {"lettre": "r", "couleur": "#c9b55a", "libelle": "RÉSIDENCES"},
    "industriel": {"lettre": "i", "couleur": "#8b8f9c", "libelle": "INDUSTRIE"},
    "parc": {"lettre": "p", "couleur": "#4c9a4a", "libelle": "PARCS"},
    "port": {"lettre": "q", "couleur": "#5f8fbf", "libelle": "PORT"},
    "eau": {"lettre": "~", "couleur": "#2a5a80", "libelle": "EAU"},
}

#: L'usage de chaque lettre de plan qui n'est pas un lieu garanti. ⚠️ La cour de
#: gang est INDUSTRIELLE : barbele, asphalte et ferraille, c'est une cour, pas une
#: rue ou l'on habite. La place et la foire sont des parcs : on y va, on n'y vit pas.
USAGE_DU_PLAN: dict[str, str] = {
    "c": "commercial", "h": "residentiel", "m": "residentiel",
    "w": "industriel", "i": "industriel", "g": "industriel",
    "p": "parc", "k": "parc", "n": "parc", "f": "parc", "o": "parc",
    "q": "port", "j": "port", "~": "eau",
}

#: Et celui d'un lieu garanti, par le GENRE d'ilot qui le batit (`SPECIAUX`) : le
#: phare est bati en banlieue, l'usine en industriel, le reste en commerces.
USAGE_DU_GENRE: dict[str, str] = {
    "commerces": "commercial", "maisons": "residentiel", "banlieue": "residentiel",
    "hangars": "industriel", "industriel": "industriel", "gang": "industriel",
}


def empreinte_de_tuile(x: int, y: int) -> float:
    """Un tirage STABLE dans [0, 1) pour cette tuile, sans consommer un de : le
    `hash2` de base.js, en 32 bits. ⚠️ Pour ce qui se decide a la position (une
    vitrine placardee, un lampadaire en panne) : changer un bloc de standing ne
    rebat pas le reste de la ville."""
    h = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 0x100000000


def usage_du_glyphe(glyphe: str) -> str:
    """L'usage d'une lettre de plan. Leve KeyError pour une lettre inconnue :
    un bloc sans usage serait un trou dans la legende."""
    if glyphe in SPECIAUX:
        return USAGE_DU_GENRE[SPECIAUX[glyphe].get("genre", "commerces")]
    return USAGE_DU_PLAN[glyphe]


def grille_des_usages(plan: tuple[str, ...]) -> tuple[str, ...]:
    """La lettre d'usage de chaque bloc — celle de son MAITRE : un superbloc est un lot."""
    maitre = regions_du_plan(plan)
    return tuple("".join(USAGES[usage_du_glyphe(plan[maitre[(bx, by)][1]][maitre[(bx, by)][0]])]["lettre"]
                         for bx in range(len(ligne)))
                 for by, ligne in enumerate(plan))


USAGE_DE_LA_LETTRE: dict[str, str] = {fiche["lettre"]: usage for usage, fiche in USAGES.items()}


class _Chantier:
    """L'echafaudage : la trame, puis les rues, puis les ilots, puis le decor."""

    def __init__(self, plan: tuple[str, ...], graine: int) -> None:
        self.plan = plan
        # ⚠️ Un plan d'essai n'a pas de standing ecrit : il est ordinaire partout
        # ou il y a du sol. La ville, elle, lit la grille de `DISTRICTS`.
        self.standing = STANDING if plan == PLAN else tuple(
            "".join(SANS_STANDING if g == "~" else "=" for g in ligne) for ligne in plan)
        self.usage = grille_des_usages(plan)
        self.nc = len(plan[0])
        self.nr = len(plan)
        if len(COLONNES) != self.nc or len(RANGEES) != self.nr:
            raise ValueError("COLONNES/RANGEES ne collent pas au plan")
        if len(RUES_V) != self.nc + 1 or len(RUES_H) != self.nr + 1:
            raise ValueError("il faut une rue de plus que de blocs dans chaque sens")
        self.maitre = regions_du_plan(plan)

        # La trame : ou commence chaque rue et chaque bloc.
        self.xr, self.xb = [], []
        x = 0
        for i in range(self.nc):
            self.xr.append(x)
            x += RUES_V[i]
            self.xb.append(x)
            x += COLONNES[i]
        self.xr.append(x)
        self.largeur = x + RUES_V[self.nc]
        self.yr, self.yb = [], []
        y = 0
        for j in range(self.nr):
            self.yr.append(y)
            y += RUES_H[j]
            self.yb.append(y)
            y += RANGEES[j]
        self.yr.append(y)
        self.hauteur = y + RUES_H[self.nr]
        #: Ou commence chaque colonne (et chaque rangee) de blocs pour
        #: `standing_en` : au MILIEU de la rue qui la precede.
        self._coupes_x = [0] + [self.xr[i] + RUES_V[i] // 2 for i in range(1, self.nc)]
        self._coupes_y = [0] + [self.yr[j] + RUES_H[j] // 2 for j in range(1, self.nr)]

        self.sol = [[","] * self.largeur for _ in range(self.hauteur)]
        self.voie = [["."] * self.largeur for _ in range(self.hauteur)]
        #: De quoi boucher une poche injoignable, par tuile (voir boucher_les_poches).
        self.bouchon = [["B"] * self.largeur for _ in range(self.hauteur)]
        self.des = Des(graine)
        self.portes: list[dict] = []
        self.points: list[dict] = []
        #: La boite (x, y, largeur, hauteur) du batiment de chaque lieu garanti — pour `barrieres`.
        self.lots: dict[str, tuple[int, int, int, int]] = {}
        self.decor: list[dict] = []
        self.fourriere: dict | None = None
        #: L'empreinte du dernier batiment pose (voir `_pose_batiment`).
        self.empreinte_du_batiment = 0
        #: Sa boite (x, y, largeur, hauteur) — voir `_terrain_de_banlieue`.
        self.boite_du_batiment = (0, 0, 0, 0)
        #: Et ses TUILES : c'est d'elles que chaque vitrine tire sa part, et de
        #: sa part que sa piece tire ses mesures (`poser_la_piece`).
        self.tuiles_du_batiment: set[tuple[int, int]] = set()
        #: Les pieces POSEES a la mesure des batiments, par slug. ⚠️ Elles
        #: voyagent avec la ville (`generer`), pas avec le module : deux villes
        #: de graines differentes n'ont pas les memes commerces.
        self.pieces: dict[str, dict] = {}
        #: Combien de pieces posees — c'est ce qui rend leur slug unique, et ce
        #: qui decale leur mobilier pour que deux voisines ne soient pas la meme.
        self.posees = 0
        #: Les pieces qui ont deja une porte quelque part (voir
        #: `premiere_du_genre`) : c'est ce qui garantit qu'aucune famille de
        #: commerce ne reste une enseigne sans interieur.
        self.genres_ouverts: set[str] = set()
        self.lampes: list[dict] = []
        self.intersections: list[dict] = []
        self.arrets: dict[str, str] = {}
        self.reserve: set[tuple[int, int]] = set()
        self.occupe: set[tuple[int, int]] = set()
        #: Les portes PEINTES (`P`) des devantures et des logements. Elles ne
        #: sont pas dans `sol` — le mur reste un mur, on ne la pousse pas — mais
        #: a l'oeil c'est une porte, et on ne plante rien devant (`est_une_porte`).
        self.portes_peintes: set[tuple[int, int]] = set()
        #: Les tuiles que SEULE une porte peinte reserve. ⚠️ La piste d'une
        #: rampe a le droit d'y passer (`_course`) : elle se garde vide, donc
        #: elle ne bouche rien, et personne ne sort d'une porte peinte.
        self.devants_peints: set[tuple[int, int]] = set()
        #: Les tuiles d'ENTREE percees vers un stationnement enclave
        #: (`_percer_l_entree`) : de l'asphalte comme le lot, mais qui n'est pas
        #: le lot — on y entre, on ne s'y gare pas.
        self.entrees: set[tuple[int, int]] = set()
        #: Les devantures (bandeau + nom + vitrines + pancarte) et les tags.
        #: ⚠️ Ce sont des COUCHES PEINTES : elles ne changent aucune solidite,
        #: donc aucun juge de circulation ni de connexite ne depend d'elles.
        self.devantures: list[dict] = []
        #: Les residences : meme genre de couche peinte que les devantures, mais
        #: pour ce qui n'est pas un commerce — des etages, des fenetres et
        #: l'escalier exterieur des plex.
        self.residences: list[dict] = []
        #: Ou l'on a deja pose chaque nom d'enseigne, pour ne jamais en voir
        #: deux pareilles du meme trottoir (`choisir_enseigne`).
        self.enseignes_posees: dict[str, list[tuple[int, int]]] = {}
        #: Combien de portes ordinaires ouvertes : elles ont besoin d'un `lieu`
        #: unique (le juge `test_les_portes_menent_a_un_interieur` l'exige).
        self.visites = 0
        self.graffitis: list[dict] = []
        self.murs_tagges: set[tuple[int, int]] = set()
        #: Ou le terrain vague a JETE quelque chose (`DECHETS`). ⚠️ Le type ne
        #: suffit pas a le dire : une caisse de quai est de la cargaison, un pneu
        #: de greve une defense. C'est ce que `salete.deplacer` a le droit de
        #: deplacer, et rien d'autre.
        self.dechets_semes: set[tuple[int, int]] = set()
        #: ⚠️ Les devantures tirent dans LEUR PROPRE de. Avec le de commun, choisir
        #: un nom d'enseigne decalait toute la suite du hasard et deplacait des
        #: arbres a l'autre bout de la ville : une couche peinte ne doit pas
        #: bouger un seul mur. Cette graine-ci peut changer sans rien casser.
        self.des_devanture = Des(graine ^ 0x5EA51)
        #: Les rampes, meme regle du de separe : un tremplin de plus ne doit
        #: pas deplacer un arbre a l'autre bout de la ville.
        self.des_rampe = Des(graine ^ 0x5A17E)
        #: Les toits, meme regle du de separe : leur matiere et leur equipement
        #: sont une couche PEINTE, et une couche peinte ne deplace pas un mur a
        #: l'autre bout de la ville.
        self.des_toit = Des(graine ^ 0x701A5)
        self.toits: list[dict] = []
        #: Les clotures, meme regle — et la lecon a ete payee : en tirant la
        #: trouee d'un terrain vague et la barriere d'une cour dans le de commun,
        #: toute la suite du hasard se decalait. La ville livree changeait de
        #: gabarits, une dent creuse se refermait sur le devant d'une porte, et
        #: huit tuiles se faisaient boucher a l'autre bout de la carte.
        self.des_cloture = Des(graine ^ 0xC107E)
        #: Les hommes-sandwichs, meme regle : un solliciteur de plus ne doit pas
        #: deplacer un paquet cache a l'autre bout de la ville.
        self.des_reclame = Des(graine ^ 0x5A4D1)
        # Les guichets tirent dans le leur : en poser un de plus ne deplace pas un arbre.
        self.des_guichet = Des(graine ^ 0x6C1C4E7)
        # Les distributrices aussi : une machine de plus ne deplace pas un paquet.
        self.des_distributrice = Des(graine ^ 0xD157B1)
        # Les nids tirent dans le leur : en creuser un de plus ne deplace pas un arbre.
        self.des_nid = Des(graine ^ 0x141D5)
        self.des_entrave = Des(graine ^ 0xE47A7E)
        self.des_fermeture = Des(graine ^ 0xFE47E3)
        self.des_aqueduc = Des(graine ^ 0xA9DEC5)
        self.des_greve = Des(graine ^ 0x67EE7)
        # ⚠️ Les plages ont LEUR de : leur forme ne doit rien deplacer d'autre
        # dans la ville (voir `_eau`, qui brule ce que l'ancienne rive tirait).
        self.des_plage = Des(graine ^ 0x9A6E5)
        self.plages: list[dict] = []
        self._ponts_poses: list[dict] = []
        self.des_foire = Des(graine ^ 0xF01BE)
        self.roue: dict | None = None
        self.foire: dict | None = None
        self.jeux: list[dict] = []
        self.kiosques: list[dict] = []
        self.foire_entree: tuple[int, int, int, int] | None = None
        self.foire_enclos: list[list[int]] = []
        self.train_de_foire: dict | None = None
        self.montagne_russe: dict | None = None
        # ⚠️ SON PROPRE DE. Piger les scenes dans le de commun decalerait tout
        # ce qui vient apres — la ville livree changerait de gabarits, et le
        # depanneur perdrait son enseigne (la lecon est ecrite dans
        # `batiment_forme` depuis M8).
        self.des_scene = Des(graine ^ 0x5CE4E)
        # ⚠️ SON PROPRE DE, ET POUR LA MEME RAISON, mesuree cette fois : le
        # terrain vague et le parc de quartier sement BIEN PLUS que le gazon nu
        # qu'ils remplacent. Tires dans le de commun, leurs tirages de plus
        # decalaient tout ce qui vient apres — dix juges sont tombes d'un coup,
        # et pas un ne parle de terrain vague : une barriere d'usine dont la
        # couronne passait sur une case de stationnement, une table a
        # pique-nique de parc que le juge de la greve trouvait loin de l'eau,
        # un buisson que la balle du banc ne rencontrait plus. On BRULE donc ce
        # que l'ancien semis tirait (`Des.brule`), et on seme ici : la ville
        # livree ne bouge que dans les lots qu'on redessine.
        self.des_dechet = Des(graine ^ 0xDEC4E7)
        # ⚠️ Et le port le sien : le quai s'est mis a semer des bornes, des
        # pneus et des barils la ou il ne posait que des caisses. Meme lecon,
        # meme parade (voir `des_dechet`).
        self.des_port = Des(graine ^ 0x9041)
        #: Chaque batiment pose, tel qu'il est sorti de `batiment_forme`. ⚠️ Le
        #: noter ne tire AUCUN de : c'est ce qui permet aux chantiers (voir
        #: `app/chantiers.py`) de choisir ou demolir sans deplacer la ville.
        self.batiments: list[dict] = []
        self.rampes: list[dict] = []
        self.rampes_proposees: list[dict] = []

    # --- Trame --------------------------------------------------------------

    def glyphe_bloc(self, bx: int, by: int) -> str:
        """Le glyphe qui REGNE sur ce bloc : le sien, ou celui qui l'a avale."""
        mx, my = self.maitre[(bx, by)]
        return self.plan[my][mx]

    def _noyee(self, voisins: list[tuple[int, int]]) -> bool:
        """Une rue dont TOUS les blocs voisins sont de l'eau : elle n'existe pas.

        ⚠️ C'est la regle qui fait la geographie. Une baie fermee par un
        superbloc n'aurait pas suffi : il faut aussi que la rue du pourtour
        s'arrete au bord de l'eau, et que le chenal de La Pointe coupe VRAIMENT
        le quartier. Une rue le long d'une rive (eau d'un bord, terre de
        l'autre) reste une rue — c'est le boulevard du bassin.
        """
        return all(self.glyphe_bloc(*bloc) in EAUX for bloc in voisins)

    def rue_v_existe(self, i: int, j: int) -> bool:
        """La rue verticale `i` longe-t-elle la rangee de blocs `j` ?"""
        if ("v", i, j) in PONTS:
            return True                      # un pont : la rue passe SUR l'eau
        voisins = ([(i - 1, j)] if i > 0 else []) + ([(i, j)] if i < self.nc else [])
        if self._noyee(voisins):
            return False
        if i <= 0 or i >= self.nc:
            return True                      # les rues du pourtour, jamais avalees
        return self.maitre[(i - 1, j)] != self.maitre[(i, j)]

    def rue_h_existe(self, i: int, j: int) -> bool:
        if ("h", i, j) in PONTS:
            return True
        voisins = ([(i, j - 1)] if j > 0 else []) + ([(i, j)] if j < self.nr else [])
        if self._noyee(voisins):
            return False
        if j <= 0 or j >= self.nr:
            return True
        return self.maitre[(i, j - 1)] != self.maitre[(i, j)]

    def bras(self, i: int, j: int) -> tuple[bool, bool, bool, bool]:
        """Les quatre bras du croisement (i, j) : nord, sud, ouest, est."""
        return (j > 0 and self.rue_v_existe(i, j - 1),
                j < self.nr and self.rue_v_existe(i, j),
                i > 0 and self.rue_h_existe(i - 1, j),
                i < self.nc and self.rue_h_existe(i, j))

    def eaux(self) -> None:
        """L'eau AVANT les rues : ce qu'aucune rue ne recouvrira reste mouille.

        Les segments noyes et les croisements entierement cernes d'eau sont
        peints ici ; `rues()` et `croisements()` repeignent par-dessus tout ce
        qui existe pour de vrai.
        """
        for j in range(self.nr):
            for i in range(self.nc + 1):
                if self.rue_v_existe(i, j):
                    continue
                voisins = ([(i - 1, j)] if i > 0 else []) + ([(i, j)] if i < self.nc else [])
                if not self._noyee(voisins):
                    continue                 # avalee par un superbloc : pas de l'eau
                self.rect(self.xr[i], self.yb[j], RUES_V[i], RANGEES[j], "~")
                self.bouchon_rect(self.xr[i], self.yb[j], RUES_V[i], RANGEES[j], "~")
        for j in range(self.nr + 1):
            for i in range(self.nc):
                if self.rue_h_existe(i, j):
                    continue
                voisins = ([(i, j - 1)] if j > 0 else []) + ([(i, j)] if j < self.nr else [])
                if not self._noyee(voisins):
                    continue
                self.rect(self.xb[i], self.yr[j], COLONNES[i], RUES_H[j], "~")
                self.bouchon_rect(self.xb[i], self.yr[j], COLONNES[i], RUES_H[j], "~")
        for j in range(self.nr + 1):
            for i in range(self.nc + 1):
                coins = [(bx, by) for bx, by in ((i - 1, j - 1), (i, j - 1), (i - 1, j), (i, j))
                         if 0 <= bx < self.nc and 0 <= by < self.nr]
                if not self._noyee(coins):
                    continue
                self.rect(self.xr[i], self.yr[j], RUES_V[i], RUES_H[j], "~")
                self.bouchon_rect(self.xr[i], self.yr[j], RUES_V[i], RUES_H[j], "~")

    def ponts(self) -> list[dict]:
        """Le tablier des ponts — repose APRES les ilots.

        ⚠️ L'ordre n'est pas negociable : un bloc d'eau fusionne repeint TOUT
        son rectangle, rues avalees comprises, et le pont se retrouverait au
        fond du chenal (vu en plein visage : la chaussee etait de l'eau, les
        fleches par-dessus, et La Pointe injoignable a pied).

        On ne touche qu'au SOL : les fleches et les lignes d'arret de `rues()`
        sont deja les bonnes, et les repeindre effacerait les `S`.
        """
        sortie = []
        for sens, i, j in sorted(PONTS):
            vertical = sens == "v"
            if vertical:
                x, y, largeur, hauteur = self.xr[i], self.yb[j], RUES_V[i], RANGEES[j]
                coupe = _coupe(largeur, True)
            else:
                x, y, largeur, hauteur = self.xb[i], self.yr[j], COLONNES[i], RUES_H[j]
                coupe = _coupe(hauteur, False)
            for dy in range(hauteur):
                for dx in range(largeur):
                    glyphe = coupe[dx if vertical else dy][0]
                    # Les trottoirs du pont sont des planches : on y marche,
                    # et ca ne ressemble pas a une rue ordinaire.
                    self.sol[y + dy][x + dx] = "Q" if glyphe == "." else glyphe
            sortie.append({"x": x, "y": y, "l": largeur, "h": hauteur, "sens": sens})
        return sortie

    def regions(self) -> list[tuple[str, int, int, int, int]]:
        """(glyphe, x, y, largeur, hauteur) de chaque ilot, rues avalees comprises."""
        groupes: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for cellule, chef in self.maitre.items():
            groupes.setdefault(chef, []).append(cellule)
        sortie = []
        for (bx, by), cellules in sorted(groupes.items()):
            bx1 = max(c[0] for c in cellules)
            by1 = max(c[1] for c in cellules)
            x0, y0 = self.xb[bx], self.yb[by]
            largeur = self.xb[bx1] + COLONNES[bx1] - x0
            hauteur = self.yb[by1] + RANGEES[by1] - y0
            sortie.append((self.plan[by][bx], x0, y0, largeur, hauteur))
        return sortie

    # --- Poser des tuiles ---------------------------------------------------

    def rect(self, x: int, y: int, largeur: int, hauteur: int, glyphe: str) -> None:
        for j in range(max(0, y), min(y + hauteur, self.hauteur)):
            for i in range(max(0, x), min(x + largeur, self.largeur)):
                self.sol[j][i] = glyphe

    def bouchon_rect(self, x: int, y: int, largeur: int, hauteur: int, glyphe: str) -> None:
        for j in range(max(0, y), min(y + hauteur, self.hauteur)):
            for i in range(max(0, x), min(x + largeur, self.largeur)):
                self.bouchon[j][i] = glyphe

    def marchable_en(self, x: int, y: int) -> bool:
        """Une tuile ou un pieton peut se TENIR (voir `marchable`) : c'est ce
        que demande un placement — un devant de porte, un bandeau, une bouche
        d'escalier."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        return marchable(self.sol[y][x])

    def franchissable_en(self, x: int, y: int) -> bool:
        """Une tuile qu'un pieton peut TRAVERSER, cloture comprise (il
        l'enjambe). ⚠️ C'est ce que demande une question de connexite — « est-ce
        qu'on peut aller la ? » — jamais un placement."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        return franchissable(self.sol[y][x])

    def batiment_forme(self, tuiles: set[tuple[int, int]], vitrines: float = 0.0,
                       genre: str = "commerces") -> list[tuple[int, int]]:
        """Peint un batiment de forme QUELCONQUE et rend ses tuiles de facade.

        ⚠️ La regle est purement locale : toute tuile dont la voisine du sud
        n'appartient pas au batiment est une facade. C'est ce qui fait marcher
        les formes en U et en L sans un seul cas particulier — on voit toujours
        le mur avant, jamais le dos d'un toit.

        ⚠️ La COUVERTURE, elle, appartient au batiment entier et se choisit sur
        son genre (`COUVERTURES`) : le bruit d'un toit se tire par tuile, mais
        une matiere qui changerait d'une tuile a l'autre ne serait plus un toit.
        C'est ici aussi qu'on l'encombre — l'equipement a besoin de connaitre
        TOUT l'ensemble des tuiles, pas chacune a son tour.
        """
        # ⚠️ Le de COMMUN, comme avant : `batiment_forme` tirait deja sa
        # couverture ici, et un tirage de moins (ou de plus) dans ce de-la
        # decalerait toute la suite du hasard — la ville livree changerait de
        # gabarits, et le depanneur perdrait son enseigne. Seul l'EQUIPEMENT,
        # qui n'existait pas, passe par le de des toits.
        toit = self.des.choix(COUVERTURES.get(genre, TOITS))
        # ⚠️ Jamais la MEME couverture qu'un voisin colle. Deux batiments
        # mitoyens couverts pareil n'en font plus qu'un vu d'en haut : le bord
        # se lit dans le voisinage (« ma voisine n'est pas le meme toit »), et
        # entre deux toits identiques il n'y a pas de bord a trouver. Le choix
        # se CORRIGE sans tirer de nouveau — un de de plus decalerait la ville.
        voisines = {self.sol[y][x] for x, y in self._autour(tuiles)}
        if toit in voisines:
            for autre in COUVERTURES.get(genre, TOITS) + TOITS:
                if autre not in voisines:
                    toit = autre
                    break
        facades = []
        for tx, ty in sorted(tuiles):
            if (tx, ty + 1) in tuiles:
                self.sol[ty][tx] = toit
            else:
                facades.append((tx, ty))
        self.equiper_le_toit(tuiles, facades, genre)
        for tx, ty in facades:
            coin = (tx - 1, ty) not in tuiles or (tx + 1, ty) not in tuiles
            self.sol[ty][tx] = "W" if (not coin and self.des.chance(vitrines)) else "F"
        self.batiments.append({"tuiles": sorted(tuiles), "genre": genre})
        return facades

    def _autour(self, tuiles: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Les tuiles collees au batiment, hors du batiment."""
        bord = set()
        for x, y in tuiles:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                vx, vy = x + dx, y + dy
                if (vx, vy) in tuiles or not (0 <= vx < self.largeur and 0 <= vy < self.hauteur):
                    continue
                bord.add((vx, vy))
        return bord

    def equiper_le_toit(self, tuiles: set[tuple[int, int]], facades: list[tuple[int, int]],
                        genre: str) -> None:
        """Ce que le toit PORTE : ventilation, climatisation, cheminee, cage
        d'escalier, reservoir, antennes.

        ⚠️ Jamais sur une tuile de BORD — un equipement au ras du parapet se lit
        comme un morceau de mur, et c'est le bord qui doit se voir. Jamais colle
        a un autre non plus : deux boites cote a cote font une tache. Et jamais
        sur une facade, une vitrine ou une porte : ce qui est sur un toit est
        derriere le mur avant, pas dessus.
        """
        avant = set(facades)
        # Une tuile de PLEIN toit : ses quatre voisines appartiennent au
        # batiment et aucune n'est une facade.
        dedans = sorted(
            (x, y) for x, y in tuiles
            if (x, y) not in avant
            and all((x + dx, y + dy) in tuiles and (x + dx, y + dy) not in avant
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        )
        if not dedans:
            return
        choix = [e for e in EQUIPEMENTS_DE_TOIT if not e["genres"] or genre in e["genres"]]
        if not choix:
            return
        occupe: set[tuple[int, int]] = set()
        for x, y in dedans:
            if any((x + dx, y + dy) in occupe for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                continue
            fiche = choix[self.des_toit.entier(0, len(choix) - 1)]
            if not self.des_toit.chance(1 / fiche["poids"]):
                continue
            occupe.add((x, y))
            self.toits.append({"x": x, "y": y, "type": fiche["type"]})

    def est_une_porte(self, x: int, y: int) -> bool:
        """Une porte A L'OEIL : poussee, condamnee, de garage — ou peinte.

        ⚠️ Le joueur ne distingue pas une porte peinte d'une porte condamnee.
        Demander `sol` seulement, c'est oublier une porte sur quatre : c'est
        comme ca qu'une distributrice s'est plantee devant la PIZZERIA NAPOLI.
        """
        if (x, y) in self.portes_peintes:
            return True
        return 0 <= x < self.largeur and 0 <= y < self.hauteur and self.sol[y][x] in PORTES_DE_FACADE

    def degager_le_devant(self, px: int, py: int, peinte: bool = False) -> None:
        """Les deux tuiles devant une porte : reservees, et videes.

        Retour de Martin, capture a l'appui (16 sept. 2026) : « jamais rien
        devant la porte d'une maison, d'un commerce ou autre ». ⚠️ Ca vaut pour
        TOUTES les portes, peintes comprises (`est_une_porte`).
        """
        for j in (1, 2):
            if peinte and (px, py + j) not in self.reserve:
                self.devants_peints.add((px, py + j))
            elif not peinte:
                self.devants_peints.discard((px, py + j))
            self.reserve.add((px, py + j))
            # ⚠️ ET ON DEGAGE CE QUI Y ETAIT DEJA. `poser_decor` refuse une tuile
            # reservee, mais le decor d'un terrain vague se seme AVANT que les
            # portes de l'ilot ne soient posees : une poubelle ou des debris
            # tombaient donc sur un pas de porte, et rien ne les enlevait. Deux
            # par ville — c'est peu, et c'est exactement le genre de chose qu'on
            # ne voit qu'en restant coince contre sa propre porte.
            self.occupe.discard((px, py + j))
            self.decor = [d for d in self.decor if (d["x"], d["y"]) != (px, py + j)]

    def poser_porte(self, facades: list[tuple[int, int]], special: dict | None = None,
                    proba: float = 0.65, visite: dict | None = None,
                    bande: tuple[int, int, int] | None = None) -> tuple[int, int] | None:
        """Une porte sur la facade la plus au sud QUI DONNE SUR DU MARCHABLE.

        ⚠️ A appeler apres avoir pose TOUS les batiments de l'ilot : une facade
        peut se retrouver nez a nez avec le toit du voisin, et une porte qui
        ouvre sur un mur est une promesse qu'on ne tient pas.

        ⚠️ `bande` restreint la porte a UNE VITRINE (`decouper_la_facade`) : un
        batiment a autant de portes que sa facade porte de commerces, et chacune
        doit tomber chez elle. Sans bande, c'est toute la facade — le kiosque et
        les lieux garantis, qui n'ont qu'une entree.
        """
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
        if bande:
            x0, large, rangee = bande
            candidats = [(tx, ty) for tx, ty in candidats
                         if ty == rangee and x0 <= tx < x0 + large]
        if not candidats and special:
            # Un batiment garanti DOIT s'ouvrir : on lui degage son devant.
            tx, ty = max(facades, key=lambda t: (t[1], t[0]))
            if ty + 1 < self.hauteur:
                self.sol[ty + 1][tx] = "."
                candidats = [(tx, ty)]
        if not candidats:
            return None
        bas = max(ty for _, ty in candidats)
        rangee = sorted(c for c in candidats if c[1] == bas)
        px, py = rangee[len(rangee) // 2]
        if special:
            self.sol[py][px] = "D"
            bande_speciale = bande or (min(t[0] for t in facades),
                                       max(t[0] for t in facades) - min(t[0] for t in facades) + 1)
            self.portes.append({"x": px, "y": py, "interieur": special["interieur"],
                                "lieu": special["slug"],
                                "vitrine": [bande_speciale[0], bande_speciale[1]]})
            # ⚠️ La FAMILLE voyage avec le point : c'est elle qui donne sa
            # couleur au blip et sa ligne a la legende de la carte. Un lieu sans
            # famille n'est pas une couleur par defaut, c'est un test rouge.
            self.points.append({"type": special["slug"], "slug": special["slug"],
                                "nom": special["nom"], "x": px, "y": py + 1,
                                "famille": special["famille"]})
            if special.get("porte_garage") and (px - 2, py) in facades:
                self.sol[py][px - 2] = "G"
        else:
            # ⚠️ LE DE DES DEVANTURES, et pas le de commun. Une porte — vraie ou
            # condamnee — est une COUCHE PEINTE : elle ne deplace pas un mur.
            # Elle se tirait au de commun quand il y avait une porte par
            # batiment ; depuis qu'il y en a une par VITRINE, ce serait le
            # nombre de commerces d'une rue qui deciderait ou tombent les
            # batiments de l'autre bout de la ville.
            condamnee = self.des_devanture.chance(proba)
            if visite:
                # Une porte ordinaire qui s'ouvre : pas de point d'interet (ce
                # sont les reperes de la ville, et quarante de plus n'en
                # seraient plus), mais un `lieu` UNIQUE — c'est lui qui
                # distingue deux tabagies, et par lui qu'on se souvient d'avoir
                # deja fouille ce logement-la. Le `nom` voyage sur la porte : la
                # piece est partagee, l'enseigne au-dessus ne l'est pas.
                self.visites += 1
                self.sol[py][px] = "D"
                # ⚠️ La porte transporte SA VITRINE (x, largeur) : c'est la part
                # de batiment qui lui appartient, et donc les mesures de la
                # piece derriere. Sans elle, personne — pas meme un juge — ne
                # peut plus dire de quel morceau de mur cette porte-la repond.
                self.portes.append({"x": px, "y": py, "interieur": visite["interieur"],
                                    "lieu": f"{visite['slug']}_{self.visites}",
                                    "nom": visite["nom"],
                                    "vitrine": [bande[0], bande[1]] if bande else [px, 1]})
            elif condamnee:
                self.sol[py][px] = "d"
            else:
                return None
        self.degager_le_devant(px, py)
        # ⚠️ ET LA MARCHE PAVE L'ABORD JUSQU'A LA DALLE. Depuis le trottoir a une
        # tuile, la couronne du bloc se glisse entre le devant du batiment et le
        # trottoir : sans ca, on sortait d'un commerce sur deux dalles, puis une
        # tuile de paves, puis le trottoir — et le juge des sentiers de banlieue
        # s'arretait sur les paves. On pave jusqu'a la chaussee, et rien d'autre
        # que l'abord : l'herbe d'une cour reste de l'herbe.
        for j in range(1, 12):
            if py + j >= self.hauteur:
                break
            glyphe = self.sol[py + j][px]
            if LEGENDE[glyphe].get("route"):
                break
            if glyphe == "_":
                self.sol[py + j][px] = "."
            elif glyphe not in (",", "."):
                break
        return px, py

    # --- Les devantures ------------------------------------------------------

    #: Quatre tuiles par defaut (64 px, seize lettres) ; cinq seulement pour
    #: faire tenir un nom long. Au-dela, l'enseigne avale la facade du voisin
    #: et deux commerces mitoyens n'en font plus qu'un.
    ENSEIGNE_MAX = 4
    ENSEIGNE_ETIREE = 5
    ENSEIGNE_MIN = 2

    def standing_en(self, x: int, y: int) -> str | None:
        """`cossu`, `ordinaire` ou `pauvre` ; `None` sur l'eau. ⚠️ Une rue se
        coupe en deux, comme entre deux districts (`rect_district`) : chaque
        trottoir est du standing du bloc qu'il borde."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return None
        bx = bisect.bisect_right(self._coupes_x, x) - 1
        by = bisect.bisect_right(self._coupes_y, y) - 1
        return STANDINGS.get(self.standing[by][bx])

    def usage_en(self, x: int, y: int) -> str | None:
        """`commercial`, `residentiel`, `industriel`, `parc`, `port` ou `eau` —
        avec la meme coupe au milieu des rues que `standing_en`."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return None
        bx = bisect.bisect_right(self._coupes_x, x) - 1
        by = bisect.bisect_right(self._coupes_y, y) - 1
        return USAGE_DE_LA_LETTRE[self.usage[by][bx]]

    def district_en(self, x: int, y: int) -> str:
        """Le quartier d'une tuile — il decide des noms sur les enseignes."""
        for district in DISTRICTS:
            dx, dy, dl, dh = self.rect_district(district)
            if dx <= x < dx + dl and dy <= y < dy + dh:
                return district["slug"]
        return DISTRICTS[0]["slug"]

    def _bande_de_facade(self, facades: set[tuple[int, int]],
                         ax: int, ay: int) -> tuple[int, int]:
        """Les facades d'un seul tenant autour de `ax` sur la rangee `ay`.

        ⚠️ Sur la MEME rangee et contigues : une facade en L a des morceaux de
        mur a deux hauteurs, et un bandeau a cheval sur les deux flotterait sur
        le toit.
        """
        gauche = ax
        while (gauche - 1, ay) in facades:
            gauche -= 1
        droite = ax
        while (droite + 1, ay) in facades:
            droite += 1
        return gauche, droite - gauche + 1

    def choisir_enseigne(self, x: int, y: int) -> tuple[str, str]:
        """Un nom pour ce mur-la — jamais celui du commerce d'a cote.

        ⚠️ On parcourt TOUT le catalogue du quartier a partir d'un cran tire au
        sort, et on prend le premier nom qu'on n'a pas deja pose a moins de
        `DISTANCE_DOUBLON` tuiles. Un simple tirage au sort donnait sept
        « FERRAILLE » a La Shop, parfois deux cote a cote : une rue ou le meme
        commerce revient tous les trois murs ne se lit plus comme une rue, elle
        se lit comme un papier peint.
        """
        catalogue = devantures_mod.commerces_du_district(self.district_en(x, y))
        depart = self.des_devanture.entier(0, len(catalogue) - 1)

        def plus_proche(texte: str) -> int:
            return min((max(abs(px - x), abs(py - y))
                        for px, py in self.enseignes_posees.get(texte, ())), default=10 ** 6)

        for k in range(len(catalogue)):
            texte, famille = catalogue[(depart + k) % len(catalogue)]
            if plus_proche(texte) >= devantures_mod.DISTANCE_DOUBLON:
                return texte, famille
        # ⚠️ ET QUAND LE CATALOGUE EST EPUISE, le plus LOIN — pas celui du
        # tirage. La Shop a vingt-six noms pour trente-six murs : a partir du
        # vingt-septieme, la question n'est plus « lequel est libre » mais
        # « lequel a sa copie la plus loin d'ici ». Rendre le nom tire au sort
        # posait deux « FERRAILLE » a trente tuiles l'une de l'autre alors
        # qu'un autre nom en offrait cent vingt.
        return max((catalogue[(depart + k) % len(catalogue)] for k in range(len(catalogue))),
                   key=lambda nom: plus_proche(nom[0]))

    def poser_devanture(self, facades: list[tuple[int, int]], ancre: tuple[int, int],
                        genre: str, special: dict | None = None,
                        enseigne: tuple[str, str] | None = None,
                        bande: tuple[int, int] | None = None) -> bool:
        """Un bandeau, un nom, des vitrines et une pancarte. Rend True si pose.

        ⚠️ Les tuiles du bandeau deviennent des VITRINES (`W`) : meme solidite
        que la facade, mais elles portent une lampe — une rue commercante
        s'allume la nuit, et c'est ce qui la distingue d'une rue d'entrepots.
        """
        ax, ay = ancre
        ensemble = set(facades)
        # ⚠️ L'enseigne reste CHEZ ELLE : sans la bande de sa vitrine, elle
        # prendrait toute la facade d'un seul tenant et deborderait sur le
        # commerce d'a cote — deux noms pour un mur, ou un nom sur deux portes.
        depart, dispo = bande or self._bande_de_facade(ensemble, ax, ay)
        if dispo < self.ENSEIGNE_MIN:
            return False
        large = min(self.ENSEIGNE_MAX, dispo)
        # Centree sur la porte, puis ramenee dans la bande.
        x0 = min(max(ax - large // 2, depart), depart + dispo - large)

        if special is not None:
            choix = devantures_mod.enseigne_speciale(special["slug"], special["nom"])
            if choix is None:
                return False
            texte, genre_visuel = choix
        else:
            texte, famille = enseigne or self.choisir_enseigne(ax, ay)
            genre_visuel = devantures_mod.genre_index(famille)
        # ⚠️ Un nom trop long pour la bande n'est pas coupe : on elargit tant
        # qu'on peut, et si ca ne rentre toujours pas on renonce a l'enseigne
        # plutot que d'afficher « QUINCAILLE ».
        while (not devantures_mod.tient_en(texte, large, TUILE_PX)
               and large < min(dispo, self.ENSEIGNE_ETIREE)):
            large += 1
            x0 = min(max(ax - large // 2, depart), depart + dispo - large)
        if not devantures_mod.tient_en(texte, large, TUILE_PX):
            return False

        for i in range(large):
            tx = x0 + i
            if self.sol[ay][tx] == "F":
                self.sol[ay][tx] = "W"

        # La pancarte pend a un bout du bandeau, du cote ou il y a du trottoir.
        # ⚠️ Tiree au sort parmi les bouts possibles : en prenant toujours le
        # premier, toutes les pancartes de la ville pendaient a gauche.
        cotes = [sens for bout, sens in ((x0, -1), (x0 + large - 1, 1))
                 if self.marchable_en(bout, ay + 1)]
        pancarte = cotes[self.des_devanture.entier(0, len(cotes) - 1)] if cotes else 0

        # ⚠️ Ce qu'il y a SOUS le bandeau, tuile par tuile : « W » vitrine,
        # « D » porte, « d » porte condamnee, « G » porte de garage. Sans ce
        # masque, le peintre couvrait toute la bande de vitrine et la porte
        # disparaissait — on voyait le nom du commerce mais plus par ou entrer.
        motifs = "".join(self.sol[ay][x0 + i] for i in range(large))
        # ⚠️ Un commerce sans porte du tout n'existe pas. Un tiers des bandes
        # n'en avaient aucune (le batiment a tire « pas de porte ») : on en
        # PEINT une, marquee « P ». Elle ne touche pas au sol — c'est une porte
        # fermee, comme les « d », et elle ne promet donc rien qu'on ne tienne.
        if not set(motifs) & set("DdG"):
            # Contre le trottoir : on peint la porte la ou le joueur passe.
            visibles = [i for i in range(large) if self.marchable_en(x0 + i, ay + 1)]
            ou = visibles[len(visibles) // 2] if visibles else large // 2
            motifs = motifs[:ou] + "P" + motifs[ou + 1:]
            # ⚠️ Peinte, mais une porte : son devant se degage comme celui d'une
            # vraie. Sans ca, la machine distributrice la prenait pour une vitrine.
            self.portes_peintes.add((x0 + ou, ay))
            self.degager_le_devant(x0 + ou, ay, peinte=True)
        self.devantures.append({
            "x": x0, "y": ay, "l": large, "genre": genre_visuel,
            "texte": texte, "pancarte": pancarte, "motifs": motifs,
            # `porte` = on se visite. ⚠️ Ce n'est plus reserve aux lieux
            # garantis : depuis qu'un commerce ordinaire sur cinq ouvre pour
            # de vrai, c'est le masque qui dit la verite.
            "porte": 1 if (special is not None or "D" in motifs) else 0,
        })
        self.enseignes_posees.setdefault(texte, []).append((ax, ay))
        # ⚠️ Une vitrine eclaire le trottoir. Sans ca, la rue commercante et la
        # rangee d'entrepots sont le meme noir a minuit, et tout le travail des
        # enseignes disparaît la moitie du temps de jeu. Lueur BASSE et courte :
        # c'est un reflet sur le trottoir, pas un lampadaire.
        self.lampes.append({"x": x0 + large // 2, "y": ay + 1,
                            "r": 20 + 4 * large, "c": "vitrine"})
        for i in range(large):
            self.murs_tagges.add((x0 + i, ay))       # pas de graffiti sur une vitrine
        return True

    # --- Les residences ------------------------------------------------------

    #: Combien d'etages, par genre d'ilot. ⚠️ C'est la seule chose qui distingue
    #: un quartier d'un autre EN HAUTEUR, et elle compte autant que la trame :
    #: le Faubourg est une rue de plex a escalier, la banlieue une rangee de
    #: bungalows, et on le voit sans lire un nom de quartier.
    ETAGES = {"maisons": (2, 3), "banlieue": (1, 2), "commerces": (2, 3)}

    #: La part des batiments d'un ilot commercant qui sont des LOGEMENTS et pas
    #: des commerces. ⚠️ Retour de Martin : cent seize devantures pour une ville
    #: de cette taille, c'est une ville ou personne n'habite. Au-dessus d'un
    #: commerce sur trois, on n'a plus de rue commercante ; en dessous d'un sur
    #: cinq, on ne voit pas la difference.
    PART_LOGEMENT = 0.30

    #: Et la part des residences dont la porte s'ouvre pour de vrai.
    PART_LOGEMENT_VISITABLE = 0.22

    #: La part des commerces ordinaires (ceux qui ne sont pas un lieu garanti)
    #: dont la porte s'ouvre : un sur cinq. ⚠️ Toutes les ouvrir coutait deux
    #: fois rien en paquet, mais rendait la ville plate — une enseigne qui ne
    #: mene nulle part reste un decor utile, et c'est le contraste qui fait
    #: qu'on pousse une porte.
    PART_COMMERCE_VISITABLE = 0.20

    def poser_residence(self, facades: list[tuple[int, int]], ancre: tuple[int, int],
                        genre: str, bande: tuple[int, int] | None = None,
                        etages: int | None = None) -> bool:
        """Des etages, des fenetres, un escalier : un batiment ou l'on HABITE.

        ⚠️ Meme contrat que la devanture : une COUCHE PEINTE. Elle ne deplace
        pas une tuile et ne change aucune solidite — `motifs` dit seulement ce
        qu'il y a dessous, tuile par tuile, pour que le peintre ne couvre pas
        une porte. Ce qui change, c'est ce qu'on lit : un mur nu de trois
        tuiles ne dit rien, trois etages de fenetres et un escalier de fer
        disent « il y a du monde qui vit ici ».
        """
        ax, ay = ancre
        ensemble = set(facades)
        depart, dispo = bande or self._bande_de_facade(ensemble, ax, ay)
        if dispo < 2:
            return False
        large = min(4, dispo)
        x0 = min(max(ax - large // 2, depart), depart + dispo - large)
        if etages is None:
            bas, haut = self.ETAGES.get(genre, (1, 2))
            etages = self.des_devanture.entier(bas, haut)

        motifs = "".join(self.sol[ay][x0 + i] for i in range(large))
        porte = None
        if set(motifs) & set("DdG"):
            porte = x0 + next(i for i, c in enumerate(motifs) if c in "DdG")
        else:
            visibles = [i for i in range(large) if self.marchable_en(x0 + i, ay + 1)]
            ou = visibles[len(visibles) // 2] if visibles else large // 2
            motifs = motifs[:ou] + "P" + motifs[ou + 1:]
            porte = x0 + ou
            self.portes_peintes.add((porte, ay))
            self.degager_le_devant(porte, ay, peinte=True)

        # ⚠️ L'escalier exterieur pend du cote ou il y a du trottoir, comme la
        # pancarte d'un commerce : accroche a un mur mitoyen, il monterait dans
        # le mur du voisin. Zero = tout droit devant la porte.
        cotes = [sens for i, sens in ((0, -1), (large - 1, 1))
                 if self.marchable_en(x0 + i, ay + 1)]
        escalier = 0
        if etages >= 2 and cotes:
            escalier = cotes[self.des_devanture.entier(0, len(cotes) - 1)]
        self.residences.append({
            "x": x0, "y": ay, "l": large, "etages": etages, "motifs": motifs,
            "escalier": escalier, "porte": porte - x0,
            "mur": self.des_devanture.entier(0, len(devantures_mod.MURS) - 1),
            "balcon": 1 if (etages >= 2 and self.des_devanture.chance(0.45)) else 0,
        })
        # ⚠️ Une fenetre allumee sur trois, pas plus : la lueur est une lampe de
        # plus a composer par image (elles sont plafonnees a vingt-cinq), et une
        # rue ou TOUTES les fenetres brillent a trois heures du matin ment.
        if self.des_devanture.chance(0.34):
            self.lampes.append({"x": x0 + large // 2, "y": ay, "r": 14 + 3 * large,
                                "c": "fenetre"})
        for i in range(large):
            self.murs_tagges.add((x0 + i, ay))
        return True

    # --- Les graffitis -------------------------------------------------------

    def graffitis_sur_les_murs(self) -> None:
        """Des tags sur les murs nus. Le gang du coin signe chez lui.

        ⚠️ Jamais sur une devanture : un commerce lave sa vitrine. Les tags
        vont sur les facades restees nues (`F`) et sur les portes condamnees —
        c'est-a-dire exactement les murs dont personne ne s'occupe.
        """
        cours = [(z["x"], z["y"], z["l"], z["h"], z["gang"])
                 for z in self.zones() if z.get("gang")]

        def gang_proche(x: int, y: int) -> str | None:
            for zx, zy, zl, zh, gang in cours:
                if zx - 6 <= x < zx + zl + 6 and zy - 6 <= y < zy + zh + 6:
                    return gang
            return None

        for y in range(self.hauteur):
            for x in range(self.largeur):
                if self.sol[y][x] not in ("F", "d"):
                    continue
                if (x, y) in self.murs_tagges:
                    continue
                # Un mur ne se tague que s'il se VOIT : il faut pouvoir se
                # planter devant.
                if not self.marchable_en(x, y + 1):
                    continue
                gang = gang_proche(x, y)
                #: Trois murs sur cent en ville, un sur cinq au pied d'une cour
                #: de gang : un tag partout ne marque plus rien.
                chance = 0.20 if gang else 0.03
                if not self.des_devanture.chance(chance):
                    continue
                if gang and self.des_devanture.chance(0.75):
                    mots = devantures_mod.TAGS_GANG.get(gang, devantures_mod.TAGS_LIBRES)
                else:
                    mots = devantures_mod.TAGS_LIBRES
                self.taguer(x, y, mots, self.des_devanture)

    def mur_taggable(self, x: int, y: int) -> bool:
        """Un mur nu (`F`) ou condamne (`d`), pas encore tague, et qui se VOIT :
        il faut pouvoir se planter devant."""
        return (0 <= y < self.hauteur - 1 and 0 <= x < self.largeur
                and self.sol[y][x] in ("F", "d") and (x, y) not in self.murs_tagges
                and self.marchable_en(x, y + 1))

    def taguer(self, x: int, y: int, mots: tuple[str, ...], des: Des) -> bool:
        """Un tag sur ce mur, tire dans `mots` avec `des`. Faux s'il n'y tient pas."""
        # ⚠️ Un tag long deborde sur les murs voisins : on compte
        # d'abord la place REELLE (jusqu'a trois tuiles de mur d'un
        # seul tenant), puis on ne tire que parmi les mots qui y
        # tiennent. Sans ca, « LA VILLE DORT » finissait ecrit en
        # travers d'un trottoir ou d'une vitrine.
        place = 1
        while place < 3 and x + place < self.largeur \
                and self.sol[y][x + place] in ("F", "d") \
                and (x + place, y) not in self.murs_tagges:
            place += 1
        possibles = [m for m in mots
                     if devantures_mod.tient_en(m, place, TUILE_PX, marge=0)]
        if not possibles:
            return False
        texte = possibles[des.entier(0, len(possibles) - 1)]
        self.graffitis.append({
            "x": x, "y": y,
            "motif": devantures_mod.MOTIFS[des.entier(0, len(devantures_mod.MOTIFS) - 1)],
            "couleur": des.entier(0, len(devantures_mod.COULEURS_TAG) - 1),
            "texte": texte,
            "penche": des.entier(0, 1),
        })
        self.murs_tagges.add((x, y))
        return True

    #: La largeur d'une VITRINE, en tuiles. ⚠️ Une facade de soixante tuiles
    #: n'est pas un commerce, c'est une rangee de commerces — et une seule porte
    #: pour toute une face de bloc obligeait la piece derriere a faire cinquante
    #: tuiles de large, ou bien a mentir de treize pour cent (demande de Martin,
    #: 14 sept. 2026 : « plusieurs portes, plusieurs commerces »). Huit tuiles,
    #: c'est la largeur d'un magasin de rue : de quoi poser une enseigne, une
    #: porte et deux vitrines.
    VITRINE = 8
    #: Et jamais plus etroit que ca : en dessous, l'enseigne ne tient plus et la
    #: piece derriere n'est plus qu'un couloir.
    VITRINE_MIN = 4

    #: Ce qui ne se decoupe PAS : un entrepot est une seule affaire, pas une
    #: rangee de commerces. Sa facade de vingt tuiles porte un nom et une porte,
    #: et derriere il y a un entrepot de vingt tuiles de large — c'est la meme
    #: regle de proportion, appliquee a un batiment qui n'a qu'un occupant.
    D_UN_SEUL_TENANT = frozenset({"hangars", "industriel"})

    def decouper_la_facade(self, facades: list[tuple[int, int]],
                           genre: str = "commerces") -> list[tuple[int, int, int]]:
        """Les vitrines d'un batiment : (x, largeur, rangee), d'ouest en est.

        La rangee la plus au sud qui donne sur du marchable — la meme que celle
        ou `poser_porte` posait son unique porte — coupee en morceaux de la
        largeur d'un commerce. ⚠️ Les morceaux se prennent sur les suites
        CONTIGUES : une facade en L a des trous, et une vitrine a cheval sur un
        trou vendrait a travers le mur du voisin.
        """
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
        if not candidats:
            return []
        bas = max(ty for _, ty in candidats)
        rangee = sorted(tx for tx, ty in candidats if ty == bas)
        suites: list[tuple[int, int]] = []
        debut = precedent = rangee[0]
        for tx in rangee[1:]:
            if tx != precedent + 1:
                suites.append((debut, precedent - debut + 1))
                debut = tx
            precedent = tx
        suites.append((debut, precedent - debut + 1))
        vitrines = []
        for x0, long_ in suites:
            if genre in self.D_UN_SEUL_TENANT:
                vitrines.append((x0, long_, bas))
                continue
            combien = max(1, min(round(long_ / self.VITRINE), long_ // self.VITRINE_MIN))
            base, reste = divmod(long_, combien)
            x = x0
            for i in range(combien):
                large = base + (1 if i < reste else 0)
                vitrines.append((x, large, bas))
                x += large
        return vitrines

    def part_du_batiment(self, bande: tuple[int, int, int]) -> set[tuple[int, int]]:
        """Les tuiles de batiment qu'une vitrine POSSEDE : celles au-dessus
        d'elle.

        ⚠️ C'est la regle qui partage un batiment entre ses commerces, et elle
        tient en une phrase : chacun a ce qu'on voit depuis sa vitrine. Un
        batiment en L ou en U se partage donc tout seul, colonne par colonne, et
        une colonne dont la facade regarde ailleurs n'appartient a personne.
        """
        x0, large, _ = bande
        return {(tx, ty) for tx, ty in self.tuiles_du_batiment if x0 <= tx < x0 + large}

    def _ancre_devanture(self, facades: list[tuple[int, int]]) -> tuple[int, int] | None:
        """Ou irait la porte si ce batiment en avait une : le milieu de sa
        facade la plus au sud qui donne sur du marchable."""
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
        if not candidats:
            return None
        bas = max(ty for _, ty in candidats)
        rangee = sorted(c for c in candidats if c[1] == bas)
        return rangee[len(rangee) // 2]

    def cloture_possible(self, x: int, y: int) -> bool:
        """Si une tuile de cloture a le droit de se poser ici.

        ⚠️ Une porte se pose sur la facade SUD d'un batiment et exige du
        marchable devant elle. Une cloture peinte la (une cour arriere qui touche
        le mur du voisin) fait rater `poser_porte` : le batiment perd sa porte,
        son enseigne et son commerce, et personne ne le voit avant de chercher
        une boutique qui n'existe plus.

        ⚠️ Et une cloture ne remplace NI UN MUR NI UNE CHAUSSEE. Tant qu'elle ne
        se posait qu'a la tuile, personne n'en avait besoin ; du jour ou l'on
        ceinture un terrain (`clore`), l'enceinte passe la ou il y a deja
        quelque chose — et elle l'ecrasait. Mesure a l'appui : le barbele de la
        cour des Skateux mangeait deux colonnes de leur stationnement, et « il y
        a un tremplin a La Pointe a tout coup » redevenait une legende. On ne
        cloture donc que du SOL : ni bati, ni eau, ni asphalte, ni case.
        """
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        if (x, y) in self.reserve or (y > 0 and solidite(self.sol[y - 1][x]) == 1):
            return False
        # ⚠️ NI PAR-DESSUS UN DECOR. Le decor n'est pas une tuile, c'est une
        # entite (`occupe`), donc `solidite` ne le voit pas : une palissade de
        # cour arriere se peignait a travers un cabanon, et le juge « le decor
        # ne bouche ni la rue ni les portes » l'a attrape — un cabanon pose sur
        # une tuile qu'on ne foule pas.
        if (x, y) in self.occupe:
            return False
        glyphe = self.sol[y][x]
        return not (solidite(glyphe) or routier(glyphe))

    def poser_cloture(self, x: int, y: int, glyphe: str) -> bool:
        """Une tuile de cloture — sauf devant une facade ou un devant de porte."""
        if not self.cloture_possible(x, y):
            return False
        self.sol[y][x] = glyphe
        return True

    def cloture_en(self, x: int, y: int) -> bool:
        """Une tuile de cloture ici ? (hors carte : non)"""
        return (0 <= x < self.largeur and 0 <= y < self.hauteur
                and self.sol[y][x] in CLOTURES)

    #: Ce qu'il y a DEHORS, par cote du rectangle.
    DEHORS = {"N": (0, -1), "S": (0, 1), "O": (-1, 0), "E": (1, 0)}

    def cote_deja_longe(self, t: tuple[int, int], cote: str) -> bool:
        """Si une cloture longe DEJA ce cote-la, juste dehors.

        ⚠️ Pas une tuile isolee qui passe par la : une COURSE, qui continue le
        long du cote. Une cloture perpendiculaire qui vient buter contre le
        terrain n'en cloture pas le flanc — elle le touche.
        """
        dx, dy = self.DEHORS[cote]
        tx, ty = t[0] + dx, t[1] + dy
        if not self.cloture_en(tx, ty):
            return False
        px, py = (0, 1) if cote in "OE" else (1, 0)
        return self.cloture_en(tx + px, ty + py) or self.cloture_en(tx - px, ty - py)

    #: Ce qu'il faut pouvoir poser d'une enceinte pour que ca vaille la peine de
    #: la poser. ⚠️ En dessous, on n'en pose AUCUNE tuile : trois quarts d'une
    #: cloture, c'est une cloture ; la moitie, c'est une barre sur un terrain.
    PART_ENCEINTE = 0.75

    #: Les quatre cotes d'un rectangle, par leur lettre.
    COTES = "NSEO"

    def clore(self, x: int, y: int, largeur: int, hauteur: int, glyphe: str, *,
              cotes: str = COTES, ouverture: int = 2, cote_ouvert: str = "S") -> int:
        """Ceinture un terrain de cloture, avec une TROUEE. Rend le nombre de
        tuiles posees — zero si l'enceinte n'a pas pu se faire.

        ⚠️ **Une cloture cloture un terrain, ou elle n'est pas la.** C'est la
        regle entiere, et le depot la violait partout : le terrain vague peignait
        UN cote, UNE tuile sur deux ; la cour de `_jardin` posait son U tuile par
        tuile et `poser_cloture` en refusait en silence. Mesure a l'appui, sur la
        ville livree : 361 tuiles de cloture en 80 morceaux, dont **69 sans un
        seul coin** (216 tuiles de barre droite) et **24 toutes seules**. Vu du
        jeu, ce n'etait pas une banlieue cloturee, c'etait des palissades posees
        sur du gazon — ce que Martin a nomme d'un coup d'oeil.

        Trois regles, et elles se tiennent :

        1. **Tout ou rien.** On regarde d'abord ce que `cloture_possible` accepte
           de l'enceinte entiere. En dessous de `PART_ENCEINTE`, on ne pose rien
           du tout : mieux vaut un terrain ouvert qu'un moignon de cloture.
        2. **Une trouee, toujours.** Sans elle, une enceinte fermee est une poche
           que `boucher_les_poches` murerait — et le terrain disparait avec.
        3. **Aucune tuile seule.** Ce que les refus laissent d'isole s'enleve
           apres coup, jusqu'a ce qu'il ne reste que des courses qui se tiennent.
        """
        if largeur < 2 or hauteur < 2:
            return 0
        voulues: list[tuple[int, int]] = []
        #: Le ou les cotes du rectangle dont chaque tuile voulue fait partie —
        #: un coin en tient deux.
        cotes_de: dict[tuple[int, int], set[str]] = {}

        def veut(tuiles: list[tuple[int, int]], cote: str) -> None:
            voulues.extend(tuiles)
            for tuile_ in tuiles:
                cotes_de.setdefault(tuile_, set()).add(cote)

        if "N" in cotes:
            veut([(x + i, y) for i in range(largeur)], "N")
        if "S" in cotes:
            veut([(x + i, y + hauteur - 1) for i in range(largeur)], "S")
        haut = 0 if "N" in cotes else 1
        bas = hauteur - 1 if "S" in cotes else hauteur
        if "O" in cotes:
            veut([(x, y + j) for j in range(haut, bas)], "O")
        if "E" in cotes:
            veut([(x + largeur - 1, y + j) for j in range(haut, bas)], "E")
        if not voulues:
            return 0

        # La trouee : `ouverture` tuiles d'affilee sur un cote. ⚠️ Elle s'ouvre
        # sur du MARCHABLE quand c'est possible — une barriere qui donne sur le
        # mur du voisin n'est pas une barriere, et une cour dont la seule sortie
        # est murée redevient la poche que `boucher_les_poches` efface.
        def tuile(k: int) -> tuple[int, int]:
            if cote_ouvert == "N":
                return (x + k, y)
            if cote_ouvert == "S":
                return (x + k, y + hauteur - 1)
            if cote_ouvert == "O":
                return (x, y + k)
            return (x + largeur - 1, y + k)

        dehors = self.DEHORS[cote_ouvert]
        long_cote = largeur if cote_ouvert in "NS" else hauteur
        ouverture = min(ouverture, max(1, long_cote - 2))
        departs = list(range(max(1, long_cote - ouverture)))
        donnent = [d for d in departs
                   if all(self.marchable_en(tuile(d + k)[0] + dehors[0],
                                            tuile(d + k)[1] + dehors[1])
                          for k in range(ouverture))]
        depart = self.des_cloture.choix(donnent or departs)
        trouee = {tuile(depart + k) for k in range(ouverture)}
        voulues = [t for t in voulues if t not in trouee]

        # ⚠️ **Deux voisins, UNE cloture.** Elle se pose sur la ligne mitoyenne,
        # pas de chaque cote d'elle. Deux cours voisines ceinturaient chacune la
        # sienne, et il en sortait DEUX palissades collees l'une a l'autre —
        # « je ne devrais pas voir de double clotures d'epais comme ca ». Ce
        # n'est pas qu'une laideur : c'est deux tuiles a enjamber la ou il y en
        # a une, donc deux secondes immobile pour passer d'une cour a l'autre,
        # et une banlieue qu'on traverse deux fois moins vite.
        #
        # Un cote que LONGE DEJA une cloture est un cote cloture : on ne repose
        # rien dessus, le terrain reste ferme par celle du voisin, une tuile
        # plus loin. ⚠️ Les COINS se posent quand meme — un coin tient deux
        # cotes a la fois, et c'est lui qui fait TOURNER la course que cherche
        # `elaguer_les_clotures` ; sans lui, ce qui reste tombe a l'elagage.
        # ⚠️ Et le compte se fait sur ce qui reste a poser : une tuile que le
        # voisin tient deja n'est pas une tuile refusee, donc elle ne doit pas
        # peser dans `PART_ENCEINTE` et faire renoncer a l'enceinte entiere.
        voulues = [t for t in voulues
                   if len(cotes_de[t]) > 1
                   or not self.cote_deja_longe(t, next(iter(cotes_de[t])))]

        possibles = [t for t in voulues if self.cloture_possible(*t)]
        if not voulues or len(possibles) < self.PART_ENCEINTE * len(voulues):
            return 0

        # ⚠️ On ENLEVE avant de poser : une tuile sans voisine ne se rattrape
        # pas apres coup, elle se retire. La boucle tourne jusqu'a ce que plus
        # rien ne tombe — retirer une tuile peut en isoler une autre.
        #
        # ⚠️ « Sans voisine » se compte SUR LA VILLE, pas sur la seule enceinte
        # qu'on pose. Du jour ou deux voisins partagent une cloture, le coin
        # d'une cour ne touche plus rien DE SON ENCEINTE — sa suite est chez le
        # voisin, deja au sol — et il tombait ici : la cour perdait son coin, la
        # colonne mitoyenne n'avait plus de tournant, et `elaguer_les_clotures`
        # l'emportait a son tour. Deux palissades collees devenaient AUCUNE.
        garde = set(possibles)
        while True:
            seules = {t for t in garde
                      if not any((t[0] + dx, t[1] + dy) in garde
                                 or self.cloture_en(t[0] + dx, t[1] + dy)
                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
            if not seules:
                break
            garde -= seules
        for tx, ty in sorted(garde):
            self.poser_cloture(tx, ty, glyphe)
        return len(garde)

    #: Ce qu'on remet a la place d'une cloture qu'on enleve. ⚠️ Jamais de la
    #: route : une palissade effacee qui laisserait de l'asphalte ferait rouler
    #: des chars au milieu d'une cour.
    SOLS_NUS = (",", ".", "x", "_")

    def rendre_au_sol(self, x: int, y: int) -> None:
        """Remet du SOL a la place d'une cloture qu'on enleve : celui d'a cote.

        ⚠️ `sorted`, ET C'EST TOUT LE CONTRAIRE D'UN DETAIL. C'etait
        `max(set(nus), key=nus.count)` : sur une EGALITE — deux voisines de
        glyphes differents, une chacune — `max` rend la premiere que l'ensemble
        lui donne, et un ensemble de CHAINES s'itere dans l'ordre de leurs
        empreintes, que Python randomise a chaque processus. La ville n'etait
        donc pas reproductible : une poignee de tuiles changeaient d'un
        lancement a l'autre, et avec elles le decor, les kiosques, les feux
        pietons et les paquets caches.

        ⚠️ Ce n'est pas qu'une curiosite : c'est ce qui rendait la CI PILE OU
        FACE. Trois juges du banc tombaient une fois sur deux sans qu'aucune
        ligne n'ait bouge, et chaque session les mettait sur le dos des autres.
        `sorted` tranche l'egalite toujours pareil, et ne coute rien : `nus`
        fait quatre elements au plus.
        """
        voisins = [self.sol[y + dy][x + dx]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                   if 0 <= x + dx < self.largeur and 0 <= y + dy < self.hauteur]
        nus = [g for g in voisins if g in self.SOLS_NUS]
        self.sol[y][x] = max(sorted(set(nus)), key=nus.count) if nus else ","

    def degager_les_doubles(self, x: int, y: int, largeur: int, hauteur: int) -> int:
        """Enleve la cloture qui longe DEJA ce rectangle par dehors, avant d'en
        peindre une dessus. Rend le nombre de tuiles enlevees.

        ⚠️ Le pendant de `cote_deja_longe` pour une enceinte qui n'a pas le
        choix. La fourriere DOIT avoir sa cloture entiere — elle n'a qu'UNE
        grille, c'est tout son lot — donc elle ne peut pas partager celle du
        voisin comme le fait une cour arriere : c'est au voisin de s'effacer.
        Sans ca, le terrain vague d'a cote posait son barbele contre le
        grillage du lot (`_terrain_vague` passe AVANT, par `_ilot_bati`) et
        c'etait la meme double palissade, en pire : deux tuiles a enjamber dont
        une qui ne s'enjambe pas.

        ⚠️ On releve tout AVANT d'enlever quoi que ce soit : `cote_deja_longe`
        demande une course, et une course qu'on defait sous ses pieds laisse sa
        derniere tuile toute seule.
        """
        bords = ([((x + i, y), "N") for i in range(largeur)]
                 + [((x + i, y + hauteur - 1), "S") for i in range(largeur)]
                 + [((x, y + j), "O") for j in range(hauteur)]
                 + [((x + largeur - 1, y + j), "E") for j in range(hauteur)])
        doubles = {(t[0] + self.DEHORS[cote][0], t[1] + self.DEHORS[cote][1])
                   for t, cote in bords if self.cote_deja_longe(t, cote)}
        for tx, ty in sorted(doubles):
            self.rendre_au_sol(tx, ty)
        return len(doubles)

    def elaguer_les_clotures(self) -> int:
        """Enleve ce qui reste d'une cloture quand elle ne cloture plus rien.

        ⚠️ C'est le DERNIER MOT de la regle de `clore` — « une cloture cloture un
        terrain, ou elle n'est pas la ». `clore` la tient a la pose ; ce qu'elle
        ne peut pas tenir, c'est ce que la ville mange ENSUITE : un batiment qui
        avale un coin, une rampe qui coupe une course en deux, une rue qui passe
        par la. Ce qui survit en BARRE DROITE n'enferme plus rien, et une barre
        droite au milieu d'un gazon est exactement ce que Martin a nomme.

        Le critere tient en une phrase : **une course de cloture qui ne tourne
        jamais ne cloture rien**. Une tuile seule n'a meme pas de course.

        ⚠️ Avant `boucher_les_poches` : on n'enleve que de la solidite, donc ca
        n'ouvre que des chemins — mais le juge des poches doit voir la ville
        telle qu'on la livre, pas telle qu'elle etait deux passes plus tot.
        """
        tuiles = {(x, y) for y in range(self.hauteur) for x in range(self.largeur)
                  if self.sol[y][x] in CLOTURES}
        vus: set[tuple[int, int]] = set()
        enleves = 0
        for depart in sorted(tuiles):
            if depart in vus:
                continue
            course, pile = [], [depart]
            vus.add(depart)
            while pile:
                x, y = pile.pop()
                course.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    voisine = (x + dx, y + dy)
                    if voisine in tuiles and voisine not in vus:
                        vus.add(voisine)
                        pile.append(voisine)
            dedans = set(course)
            tourne = any(
                (((x + 1, y) in dedans or (x - 1, y) in dedans)
                 and ((x, y + 1) in dedans or (x, y - 1) in dedans))
                for x, y in course)
            if tourne:
                continue
            for x, y in course:
                self.rendre_au_sol(x, y)
                enleves += 1
        return enleves

    def retirer_decor(self, x: int, y: int) -> bool:
        """Enleve le decor pose sur cette tuile, et la rend libre."""
        for i, d in enumerate(self.decor):
            if (d["x"], d["y"]) == (x, y):
                del self.decor[i]
                self.occupe.discard((x, y))
                return True
        return False

    def degager_le_decor(self, x: int, y: int, largeur: int, hauteur: int) -> int:
        """Aucune tuile de cette boite ne reste enfermee par du DECOR.

        ⚠️ **Le pendant de `boucher_les_poches`, pour le mobilier.** Celui-la
        mure les poches du SOL ; personne ne regardait celles que le decor
        SOLIDE referme — et un semis un peu genereux suffit a couper un quai en
        quarante morceaux. Mesure du 16 sept. 2026 : **191 tuiles de quai
        inatteignables a pied**, derriere des caisses et une ligne de bornes
        d'amarrage. Retour de Martin : « impossible d'aller sur une partie du
        quai, il est cloture, sans chemin a pied ».

        ⚠️ **On ENLEVE, on ne deplace pas.** Un decor qu'on decale se retrouve a
        fermer autre chose, et il faudrait recommencer ; un decor qu'on enleve
        ne ferme plus rien. C'est aussi ce qui rend la boucle finie : chaque
        tour en retire au moins un.

        ⚠️ Et on part de DEHORS : une boite dont tout l'interieur communique
        mais dont aucune entree n'est libre est murée tout autant. Rend le
        nombre de decors retires.
        """
        boite = {(i, j)
                 for j in range(max(0, y - 1), min(self.hauteur, y + hauteur + 1))
                 for i in range(max(0, x - 1), min(self.largeur, x + largeur + 1))
                 if self.marchable_en(i, j)}
        dedans = {(i, j) for i, j in boite if x <= i < x + largeur and y <= j < y + hauteur}
        dehors = boite - dedans
        enleves = 0
        for _ in range(len(dedans) + 1):
            bloque = {(d["x"], d["y"]) for d in self.decor
                      if d["type"] in DECOR_SOLIDE and (d["x"], d["y"]) in boite}
            libres = boite - bloque
            departs = [t for t in sorted(dehors - bloque)] or [t for t in sorted(libres)]
            if not departs:
                return enleves
            vus = {departs[0]}
            pile = [departs[0]]
            for d in departs:                      # toutes les entrees a la fois
                if d not in vus:
                    vus.add(d)
                    pile.append(d)
            while pile:
                i, j = pile.pop()
                for voisin in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                    if voisin in libres and voisin not in vus:
                        vus.add(voisin)
                        pile.append(voisin)
            poches = (dedans - bloque) - vus
            if not poches:
                return enleves
            # Le decor qui touche la poche : c'est lui qui la ferme.
            i, j = min(poches)
            ferme = [v for v in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)) if v in bloque]
            if not ferme:
                # La poche ne touche aucun decor : c'est le SOL qui l'enferme,
                # et `boucher_les_poches` a deja son mot a dire la-dessus.
                return enleves
            for v in ferme:
                if self.retirer_decor(*v):
                    enleves += 1
        return enleves

    def poser_decor(self, type_: str, x: int, y: int, sur_eau: bool = False) -> bool:
        """Du decor seulement sur une tuile libre, hors route et hors devant de porte.

        ⚠️ `sur_eau` : l'eau est SOLIDE dans la legende (`solide: 2`), et c'est
        pour ca qu'aucun decor n'a jamais flotte. La bouee est le premier qui ait
        raison de le faire — on le lui accorde ICI, une fois et par demande
        explicite, plutot que d'ouvrir l'eau a tout le catalogue : sinon le jour
        ou quelqu'un seme des poubelles un peu large, elles flottent.
        """
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        if (x, y) in self.reserve or (x, y) in self.occupe:
            return False
        proprietes = LEGENDE[self.sol[y][x]]
        if sur_eau:
            if self.sol[y][x] != "~":
                return False
        elif proprietes.get("solide") or proprietes.get("route"):
            return False
        self.occupe.add((x, y))
        self.decor.append({"type": type_, "x": x, "y": y})
        return True

    # --- Les rues -----------------------------------------------------------

    def rues(self) -> None:
        """Chaque rue est posee SEGMENT PAR SEGMENT : un segment avale par un
        superbloc n'est simplement pas peint."""
        for i in range(self.nc + 1):
            coupe = _coupe(RUES_V[i], True)
            for j in range(self.nr):
                if not self.rue_v_existe(i, j):
                    continue
                for y in range(self.yb[j], self.yb[j] + RANGEES[j]):
                    for d, (glyphe, fleche) in enumerate(coupe):
                        self.sol[y][self.xr[i] + d] = glyphe
                        self.voie[y][self.xr[i] + d] = fleche
        for j in range(self.nr + 1):
            coupe = _coupe(RUES_H[j], False)
            for i in range(self.nc):
                if not self.rue_h_existe(i, j):
                    continue
                for d, (glyphe, fleche) in enumerate(coupe):
                    y = self.yr[j] + d
                    for x in range(self.xb[i], self.xb[i] + COLONNES[i]):
                        self.sol[y][x] = glyphe
                        self.voie[y][x] = fleche

    def croisements(self) -> None:
        for j in range(self.nr + 1):
            for i in range(self.nc + 1):
                nord, sud, ouest, est = self.bras(i, j)
                x0, y0, lv, lh = self.xr[i], self.yr[j], RUES_V[i], RUES_H[j]

                if not (nord or sud or ouest or est):
                    continue                      # entierement avale par un superbloc
                if not (ouest or est):            # la rue verticale passe tout droit
                    for dy in range(lh):
                        for dx, (glyphe, fleche) in enumerate(_coupe(lv, True)):
                            self.sol[y0 + dy][x0 + dx] = glyphe
                            self.voie[y0 + dy][x0 + dx] = fleche
                    continue
                if not (nord or sud):
                    for dy, (glyphe, fleche) in enumerate(_coupe(lh, False)):
                        for dx in range(lv):
                            self.sol[y0 + dy][x0 + dx] = glyphe
                            self.voie[y0 + dy][x0 + dx] = fleche
                    continue

                for dy in range(lh):
                    for dx in range(lv):
                        sur_x = TROTTOIR <= dx < lv - TROTTOIR
                        sur_y = TROTTOIR <= dy < lh - TROTTOIR
                        if sur_x and sur_y:
                            glyphe, fleche = "#", "+"
                        elif sur_y:               # la rue est-ouest traverse le trottoir
                            bras = ouest if dx < TROTTOIR else est
                            glyphe, fleche = ("=", "+") if bras else (".", ".")
                        elif sur_x:
                            bras = nord if dy < TROTTOIR else sud
                            glyphe, fleche = (":", "+") if bras else (".", ".")
                        else:
                            glyphe, fleche = ".", "."
                        self.sol[y0 + dy][x0 + dx] = glyphe
                        self.voie[y0 + dy][x0 + dx] = fleche
                self.intersections.append({"x": x0 + TROTTOIR, "y": y0 + TROTTOIR,
                                           "l": lv - 2 * TROTTOIR, "h": lh - 2 * TROTTOIR,
                                           "bras": "".join(c for c, present in
                                                           zip("NSOE", (nord, sud, ouest, est)) if present)})
                self._lignes_arret(i, j, nord, sud, ouest, est)

    def _lignes_arret(self, i: int, j: int, nord: bool, sud: bool,
                      ouest: bool, est: bool) -> None:
        """Une ligne d'arret juste avant chaque entree du croisement."""
        x0, y0, lv, lh = self.xr[i], self.yr[j], RUES_V[i], RUES_H[j]
        voies_h = lh - 2 * TROTTOIR
        voies_v = lv - 2 * TROTTOIR
        approches = []
        for k in range(voies_h // 2, voies_h):            # vers l'est, arrive de l'ouest
            if ouest:
                approches.append((x0 - 1, y0 + TROTTOIR + k, ">"))
        for k in range(voies_h // 2):                     # vers l'ouest, arrive de l'est
            if est:
                approches.append((x0 + lv, y0 + TROTTOIR + k, "<"))
        for k in range(voies_v // 2):                     # vers le sud, arrive du nord
            if nord:
                approches.append((x0 + TROTTOIR + k, y0 - 1, "v"))
        for k in range(voies_v // 2, voies_v):            # vers le nord, arrive du sud
            if sud:
                approches.append((x0 + TROTTOIR + k, y0 + lh, "^"))
        for x, y, direction in approches:
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                continue
            if self.voie[y][x] != direction:
                continue
            self.voie[y][x] = "S"
            self.arrets[f"{x},{y}"] = direction

    # --- Les ilots ----------------------------------------------------------

    #: Les blocs qui recoivent une couronne d'abord : tout ce qui se BATIT. Un
    #: parc, une place, un quai ou l'eau se foulent (ou se longent) deja.
    #: ⚠️ La fourriere (`Y`) aussi : c'est une cour cloturee avec une guerite,
    #: et sa porte ouvrait droit sur la chaussee sans sa couronne.
    A_ABORD = frozenset("chmwig") | frozenset(SPECIAUX)

    def ilots(self) -> None:
        kiosque_pose = False
        for glyphe, x, y, largeur, hauteur in self.regions():
            # ⚠️ LA COURONNE D'ABORD, avant de batir : une tuile tout autour du
            # bloc, et le bloc se batit A L'INTERIEUR. C'est la ou sont allees
            # les deux tuiles que chaque rue a perdues — pas aux voies, aux
            # terrains, et on y marche. Sans elle, un batiment pose au bord du
            # bloc ne laisserait qu'une tuile de trottoir entre son mur et la
            # chaussee, et deux passants ne s'y croiseraient plus.
            if glyphe in self.A_ABORD and largeur > 4 and hauteur > 4:
                self.rect(x, y, largeur, hauteur, "_")
                x, y, largeur, hauteur = x + 1, y + 1, largeur - 2, hauteur - 2
            if glyphe == "Y":
                self._fourriere(x, y, largeur, hauteur, SPECIAUX["Y"])
            elif glyphe in SPECIAUX:
                special = SPECIAUX[glyphe]
                self._ilot_bati(x, y, largeur, hauteur,
                                genre=special.get("genre", "commerces"), special=special)
            elif glyphe == "c":
                self._ilot_bati(x, y, largeur, hauteur)
            elif glyphe == "h":
                self._ilot_bati(x, y, largeur, hauteur, genre="maisons")
            elif glyphe == "m":
                self._ilot_bati(x, y, largeur, hauteur, genre="banlieue")
            elif glyphe == "w":
                self._ilot_bati(x, y, largeur, hauteur, genre="hangars")
            elif glyphe == "i":
                self._ilot_bati(x, y, largeur, hauteur, genre="industriel")
            elif glyphe == "g":
                self._ilot_bati(x, y, largeur, hauteur, genre="gang")
            elif glyphe == "k":
                self._parc(x, y, largeur, hauteur, kiosque=not kiosque_pose)
                kiosque_pose = True
            elif glyphe == "p":
                self._parc(x, y, largeur, hauteur)
            elif glyphe == "n":
                self._parc(x, y, largeur, hauteur, sauvage=True)
            elif glyphe == "f":
                self._foire(x, y, largeur, hauteur)
            elif glyphe == "o":
                self._place(x, y, largeur, hauteur)
            elif glyphe == "q":
                self._quai(x, y, largeur, hauteur)
            elif glyphe == "j":
                self._quai(x, y, largeur, hauteur, sur_eau=True)
            elif glyphe == "~":
                self._eau(x, y, largeur, hauteur)
            else:  # pragma: no cover - garde-fou de relecture du plan
                raise ValueError(f"glyphe de plan inconnu : {glyphe!r}")

    def _bandes(self, y: int, hauteur: int, genre: str = "commerces") -> list[tuple[int, int]]:
        """Un ilot profond se coupe en bandes : ruelle, batiments, devant.

        Sans cela, un superbloc de 28 tuiles de haut serait un seul batiment
        monstrueux ; avec, il a un coeur de ruelles comme un vrai pate de
        maisons.
        """
        if genre in ("hangars", "industriel"):
            # Un entrepot mange son ilot : une bande jusqu'a 26 tuiles de fond.
            nombre = 1 if hauteur <= 26 else 2
        else:
            nombre = 1 if hauteur <= 15 else (2 if hauteur <= 28 else 3)
        base, reste = divmod(hauteur, nombre)
        bandes, cy = [], y
        for k in range(nombre):
            h = base + (1 if k < reste else 0)
            bandes.append((cy, h))
            cy += h
        return bandes

    def _parcelles(self, x: int, y: int, largeur: int, hauteur: int,
                   mini: int = 5, profondeur: int = 0) -> list[tuple[int, int, int, int]]:
        """Decoupe recursive (BSP) en parcelles INEGALES.

        ⚠️ La coupe se tire au sort entre `mini` et le reste : des parcelles de
        meme taille donneraient exactement ce qu'on veut eviter, une rangee de
        batiments identiques.
        """
        peut_v = largeur >= mini * 2
        peut_h = hauteur >= mini * 2
        if profondeur >= 3 or not (peut_v or peut_h):
            return [(x, y, largeur, hauteur)]
        vertical = peut_v if not peut_h else (peut_v and (largeur > hauteur or self.des.chance(0.35)))
        if vertical:
            coupe = self.des.entier(mini, largeur - mini)
            return (self._parcelles(x, y, coupe, hauteur, mini, profondeur + 1)
                    + self._parcelles(x + coupe, y, largeur - coupe, hauteur, mini, profondeur + 1))
        coupe = self.des.entier(mini, hauteur - mini)
        return (self._parcelles(x, y, largeur, coupe, mini, profondeur + 1)
                + self._parcelles(x, y + coupe, largeur, hauteur - coupe, mini, profondeur + 1))

    #: Le fond d'une bande ordinaire : deux tuiles de ruelle, deux de devant, et
    #: trois de batiment. En dessous, `_pose_batiment` rend `None`.
    BANDE_MIN = 7

    def _bande_a_la_mesure(self, y: int, hauteur: int, bandes: list[tuple[int, int]],
                           vedette: int, voulu: int) -> list[tuple[int, int]]:
        """Rend les bandes avec celle du lieu garanti assez profonde pour lui."""
        autres = len(bandes) - 1
        voulu = max(bandes[vedette][1], min(voulu, hauteur - autres * self.BANDE_MIN))
        if voulu <= bandes[vedette][1] or not autres:
            return [(y, hauteur)] if not autres and voulu > bandes[vedette][1] else bandes
        base, reste = divmod(hauteur - voulu, autres)
        neuves, cy, k = [], y, 0
        for i in range(len(bandes)):
            h = voulu if i == vedette else base + (1 if k < reste else 0)
            if i != vedette:
                k += 1
            neuves.append((cy, h))
            cy += h
        return neuves

    def _ilot_bati(self, x: int, y: int, largeur: int, hauteur: int, *,
                   genre: str = "commerces", special: dict | None = None) -> None:
        devant = {"maisons": ",", "banlieue": ","}.get(genre, ".")
        #: Des parcelles d'autant plus grandes que le batiment l'est : une
        #: maison de banlieue tient sur son terrain, un entrepot sur le sien.
        mini = {"maisons": 4, "banlieue": 7, "hangars": 9, "industriel": 10}.get(genre, 5)
        parcelles: list[tuple[tuple[int, int, int, int], bool]] = []
        vedette = -1
        # ⚠️ LA PARCELLE DU LIEU GARANTI SE TAILLE A LA MESURE DE SA PIECE, et
        # avant le decoupage — pas apres. Le decoupage tire ses coupes au sort :
        # lui demander ensuite la plus grosse parcelle, c'est esperer que le
        # hasard ait fait un terrain de la bonne taille, et le garage Bandini
        # se retrouvait sur vingt-sept tuiles pour une piece qui en veut cent
        # vingt. On lui reserve donc SA bande — la plus profonde — et dedans une
        # largeur calculee ; le reste de la bande se decoupe normalement.
        bandes = list(self._bandes(y, hauteur, genre))
        bande_vedette = (max(range(len(bandes)), key=lambda k: bandes[k][1])
                         if special and bandes else -1)
        if bande_vedette >= 0:
            # ⚠️ ET LA BANDE SE TAILLE AUSSI. Les bandes se partagent l'ilot en
            # parts egales ; la plus profonde d'un ilot de seize tuiles en fait
            # huit, dont quatre de ruelle et de devant — quatre tuiles de fond
            # pour l'hotel Bandini, qui en veut huit. Le lieu garanti prend donc
            # la profondeur de sa piece, et ce qui reste se partage entre les
            # autres bandes (jamais moins de sept : une ruelle, un devant, et
            # trois tuiles de batiment).
            bandes = self._bande_a_la_mesure(
                y, hauteur, bandes, bande_vedette,
                mesures_de_la_suite(special["interieur"])[1] + 4)
        # ⚠️ LES SKATEUX TIENNENT LE STATIONNEMENT — tout entier, pas un coin.
        # Leur bande ne se decoupe donc pas : c'est une PISTE. Un terrain de
        # sept tuiles tire au sort n'en laisse que cinq d'elan une fois la
        # rampe posee, et il en faut sept : La Pointe se retrouvait sans
        # tremplin des que le decoupage bougeait d'une tuile, et « il y en a un
        # a tout coup » redevenait une legende — celle-la meme que M8 avait
        # deja corrigee une fois.
        bande_skateux = (max(range(len(bandes)), key=lambda k: bandes[k][1])
                         if genre == "gang" and bandes and self.district_en(x, y) == "pointe"
                         else -1)
        parcelle_skateux = -1
        #: Les bandes a ceinturer de barbele (`genre == "gang"`). ⚠️ On les met
        #: de cote au lieu de les clore tout de suite : les batiments se posent
        #: APRES la boucle des bandes, et ils ecrasaient les colonnes est et
        #: ouest de l'enceinte — il en restait deux bouts verticaux de deux
        #: tuiles, exactement le genre de moignon qu'on vient de bannir.
        cours: list[tuple[int, int, int, int]] = []
        for k, (by, bh) in enumerate(bandes):
            self.rect(x, by, largeur, 2, "x")                      # ruelle derriere
            self.rect(x, by + bh - 2, largeur, 2, devant)           # devant
            zy, zh = by + 2, bh - 4
            if zh < 3:
                continue
            self.rect(x, zy, largeur, zh, "," if genre in ("maisons", "banlieue") else ".")
            if k == bande_vedette:
                # ⚠️ A LA BOITE DE SA PIECE, pas seulement a sa surface. Viser
                # la surface donnait a la cantine un batiment de 58 x 7 pour une
                # piece de 14 x 9 : la bonne quantite de tuiles, la mauvaise
                # forme, et une piece deux fois plus profonde que le batiment
                # qui la porte. Un lieu garanti garde son plan dessine a la
                # main — c'est son BATIMENT qui se taille a lui.
                besoin_l, besoin_h = mesures_de_la_suite(special["interieur"])
                large = min(largeur, max(3, besoin_l))
                # ⚠️ ET IL MANGE SON DEVANT, ET SA RUELLE S'IL LE FAUT. Une
                # bande garde quatre tuiles pour elles deux ; les ilots qui
                # portent l'hotel et le depanneur font neuf et huit tuiles de
                # fond, donc quatre ou cinq de batiment pour des pieces qui en
                # veulent huit et six. Un lieu garanti occupe son terrain —
                # c'est vrai d'un poste de police comme d'une usine — et sa
                # facade donne alors sur le trottoir, ce qui est bien ou l'on
                # veut une porte.
                profond = min(bh, max(3, besoin_h))
                vedette = len(parcelles)
                parcelles.append(((x, by + bh - profond, large, profond), True))
                # ⚠️ Et le reste de la bande fait UN SEUL batiment, pas une
                # rangee de petits. Le decoupage recursif, lui, laissait entre
                # ses parcelles des cours de deux tuiles que le lieu garanti —
                # qui n'a plus de marge — refermait : quarante-six tuiles
                # enclavees a murer sur une graine, quatre sur celle qu'on
                # livre. Une parcelle, un voisin, pas de cour fermee.
                if largeur - large >= mini:
                    parcelles.append(((x + large, zy, largeur - large, zh), True))
                continue
            if k == bande_skateux:
                parcelle_skateux = len(parcelles)
                parcelles.append(((x, zy, largeur, zh), True))
            else:
                for parcelle in self._parcelles(x, zy, largeur, zh, mini):
                    parcelles.append((parcelle, parcelle[1] + parcelle[3] >= zy + zh))
            if genre == "gang":
                cours.append((x, by, largeur, bh))
                self.des.brule(1 + max(0, largeur - 5))   # l'ouverture, puis quatre tuiles sur cinq
                for _ in range(3):
                    self.poser_decor("caisse", x + self.des.entier(0, largeur - 1),
                                     by + self.des.entier(0, 1))

        contenus = [self._contenu(genre) for _ in parcelles]
        # ⚠️ « Les Skateux tiennent le stationnement » (voir DISTRICTS) — sauf
        # que La Pointe n'en avait pas UNE tuile : la phrase etait une legende.
        # Leur bloc en porte donc un pour de bon, et c'est la que se pose leur
        # tremplin (`_tremplin_de_stationnement`).
        if parcelle_skateux >= 0:
            contenus[parcelle_skateux] = "stationnement"
        if special and parcelles and vedette < 0:
            # ⚠️ Le batiment garanti ne peut pas dependre d'un tirage : sans
            # cette ligne, un ilot de neuf tuiles tire « terrain vague » et
            # l'armurerie n'existe pas. Il prend la plus grosse parcelle qui
            # donne sur la rue, et elle est batie quoi qu'il arrive.
            vedette = max(range(len(parcelles)),
                          key=lambda k: (parcelles[k][1], parcelles[k][0][2] * parcelles[k][0][3]))
        if vedette >= 0:
            contenus[vedette] = "bati"

        def entree_du_lot(px: int, py: int, pl: int, ph: int) -> list[list] | None:
            """Par ou l'on entre dans un stationnement : une liste VIDE s'il
            donne deja sur la rue, les chemins a paver s'il faut lui percer une
            entree, `None` s'il n'y a pas moyen d'y entrer du tout.

            Un terrain donne sur la rue s'il touche un BORD de sa bande : la
            ruelle derriere, la couronne d'abord a gauche ou a droite, le
            trottoir du devant. Au milieu d'une bande, il n'a que des voisins.
            """
            # La couronne d'abord : des paves qui bordent le trottoir, et l'on
            # entre dans le lot de plain-pied depuis la rue.
            if px == x or px + pl == x + largeur:
                return []
            for by, bh in bandes:
                zy, zh = by + 2, bh - 4
                if not zy <= py < zy + zh:
                    continue
                if py == zy:
                    return []                     # la ruelle derriere : on y roule
                if py + ph < zy + zh:
                    return None                   # au milieu de la bande : rien que des voisins
                if devant == ".":
                    return []                     # le trottoir du devant
                # ⚠️ Le devant d'un bloc de maisons est du GAZON, et un lot qui
                # s'arrete dans l'herbe ne mene nulle part. Celui-la se perce
                # d'une entree jusqu'a la rue, comme une cour de banlieue.
                chemins = [self._chemin_vers_la_rue(cx, py + ph, 0, 1, self.RUE_DU_LOT)
                           for cx in range(px, px + pl)]
                return [chemin for chemin in chemins if chemin] or None
            return None

        # ⚠️ UN STATIONNEMENT TOUCHE LA RUE, AU MOINS UNE FOIS — demande de
        # Martin, et c'est la regle du dessin d'un lot (« toute rangee touche
        # une allee ») d'un cran plus haut : un terrain ou aucune auto ne peut
        # entrer n'est pas un stationnement, c'est un carre d'asphalte. Sur la
        # graine livree, un terrain de 4 x 4 tirait « stationnement » au milieu
        # des cours arriere d'un bloc de maisons du Faubourg — quatre cases, une
        # allee, un ilot, et rien que du gazon tout autour.
        # ⚠️ Et le terrain ou meme l'entree ne passe pas redevient ce que son
        # genre aurait dessine a la place : on ne laisse pas un lot mure.
        entrees: dict[int, list[list]] = {}
        for k, contenu in enumerate(contenus):
            if contenu != "stationnement":
                continue
            chemins = entree_du_lot(*parcelles[k][0])
            if chemins is None:
                # ⚠️ UN PARC N'A PAS BESOIN D'ENTREE DE CHAR, et c'est
                # exactement ce qui le rend bon ici : le lot qu'on vient de
                # refuser au stationnement est enclave au milieu d'une bande.
                # Un terrain vague au meme endroit serait une friche cloturee
                # que personne ne verra jamais.
                contenus[k] = "parc" if genre in ("maisons", "banlieue") else "vague"
            elif chemins:
                entrees[k] = chemins

        batiments: list[tuple[list, bool, set, tuple, tuple]] = []
        facades_vedette = None
        for k, ((px, py, pl, ph), devant_rue) in enumerate(parcelles):
            contenu = contenus[k]
            if contenu == "bati":
                facades = self._pose_batiment(px, py, pl, ph, genre, force=(k == vedette))
                tuiles = self.tuiles_du_batiment
                boite = self.boite_du_batiment
                if facades and k == vedette:
                    facades_vedette = facades
                    if special:
                        self.lots[special["slug"]] = boite
                elif facades:
                    batiments.append((facades, devant_rue, tuiles, (px, py, pl, ph), boite))
            elif contenu == "vague":
                self._terrain_vague(px, py, pl, ph)
            elif contenu == "parc":
                self._parc_de_quartier(px, py, pl, ph, genre)
            elif contenu == "stationnement":
                self._stationnement(px, py, pl, ph, genre)
                # ⚠️ APRES le lot : l'entree sort d'une ALLEE, et les allees
                # n'existent qu'une fois les rangees posees.
                self._percer_l_entree(entrees.get(k), (px, py, pl, ph))
            else:
                raise ValueError(f"contenu de parcelle inconnu : {contenu!r}")
        if facades_vedette:
            porte = self.poser_porte(facades_vedette, special)
            if porte:
                self.poser_devanture(facades_vedette, porte, genre, special)
        for facades, _, tuiles, parcelle, boite in batiments:
            self.tuiles_du_batiment = tuiles
            porte_du_batiment = None
            # ⚠️ UNE VITRINE, UN COMMERCE, UNE PIECE. Un batiment n'a plus une
            # porte au milieu de sa facade : il a autant de vitrines que sa
            # facade porte de commerces, et chacune possede les tuiles au-dessus
            # d'elle. C'est cette PART qui donne ses mesures a la piece — la
            # piece a la taille de ce qu'on voit de la rue, ni plus (ce serait
            # un mensonge) ni beaucoup moins (c'etait treize pour cent).
            for bande in self.decouper_la_facade(facades, genre):
                x0, large, ay = bande
                part = self.part_du_batiment(bande)
                ancre = (x0 + large // 2, ay)
                quoi, enseigne = self._a_quoi_sert(genre, ancre)
                visite = None
                if quoi == "commerce" and enseigne:
                    famille = enseigne[1]
                    ouvre = self.des_devanture.chance(self.PART_COMMERCE_VISITABLE)
                    if mesures_de_la_part(part) and self.premiere_du_genre(famille):
                        ouvre = True
                    # La piece suit le standing du bloc (3e vague) : son CONTENU,
                    # pas ses mesures — rien d'autre dans la ville n'en depend.
                    dedans = (self.poser_la_piece(famille, part, ancre, standing=self.standing_en(*ancre))
                              if ouvre else None)
                    if dedans:
                        visite = {"slug": famille, "nom": enseigne[0], "interieur": dedans}
                elif quoi == "logement":
                    bas, haut = self.ETAGES.get(genre, (1, 2))
                    etages = self.des_devanture.entier(bas, haut)
                    ouvre = self.des_devanture.chance(self.PART_LOGEMENT_VISITABLE)
                    if mesures_de_la_part(part) and self.premiere_du_genre("logement"):
                        ouvre = True
                    dedans = (self.poser_la_piece("logement", part, ancre, etages=etages)
                              if ouvre else None)
                    if dedans:
                        visite = {"slug": "logement", "nom": "LOGEMENT", "interieur": dedans}
                porte = self.poser_porte(facades, visite=visite, bande=bande)
                repere = porte or ancre
                porte_du_batiment = porte_du_batiment or porte
                # ⚠️ Une devanture ne suit pas la porte : un commerce a pignon
                # sur rue qu'on ne peut pas visiter reste un commerce, et une
                # rue ou seuls les trois batiments visitables ont une enseigne
                # n'a l'air d'une rue commercante nulle part.
                if quoi == "commerce":
                    self.poser_devanture(facades, repere, genre, enseigne=enseigne,
                                         bande=(x0, large))
                elif quoi == "logement":
                    self.poser_residence(facades, repere, genre, bande=(x0, large),
                                         etages=etages)
            # ⚠️ APRES LA PORTE : le sentier part d'elle. Le terrain se meuble
            # une fois qu'on sait par ou l'on entre — sinon le cabanon se pose
            # sur le pas de la porte, et la piscine coupe le chemin.
            if genre == "banlieue":
                self._terrain_de_banlieue(parcelle, boite, porte_du_batiment)
        # ⚠️ Le barbele des cours de gang EN DERNIER, une fois les batiments
        # poses : c'est la seule place ou l'enceinte ne se fait pas manger. Du
        # BARBELE, et sur TROIS cotes — quelqu'un a paye pour que personne
        # n'entre, et une ligne pointillee sur la seule rangee du sud (ce
        # qu'elle etait) laissait entrer par les cotes sans rien enjamber. Le
        # NORD reste ouvert sur la ruelle : c'est par la que la cour respire, et
        # c'est ce qui garantit qu'elle n'est jamais une poche fermee.
        for cx, cy, cl, ch in cours:
            self.clore(cx, cy, cl, ch, BARBELE, cotes="SEO", ouverture=5)
        for _ in range(max(1, largeur // 10)):
            self.poser_decor("poubelle", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, 1))

    def poser_la_piece(self, quoi: str, part: set[tuple[int, int]],
                       ancre: tuple[int, int], *, etages: int = 1,
                       standing: str | None = None) -> str | None:
        """Une piece aux mesures de cette part de batiment. `None` si trop petit.

        ⚠️ `None` est un RESULTAT, pas un echec : un bout de batiment de six
        tuiles garde sa porte, elle ne s'ouvre simplement pas. Une porte qui
        donne sur plus grand que la maison est un mensonge ; une porte qu'on ne
        pousse pas n'en est pas un.
        """
        mesures = mesures_de_la_part(part)
        if not mesures:
            return None
        largeur, hauteur = mesures
        # ⚠️ La porte tombe DEDANS la ou elle est DEHORS : on entre par la meme
        # place qu'on a poussee. Une porte au milieu du mur alors que la vitrine
        # est au bout de la facade se sent, meme sans savoir pourquoi.
        porte = min(max(ancre[0] - min(x for x, _ in part) + 1, 1), largeur)
        self.posees += 1
        slug = f"{quoi}_{self.posees}"
        if quoi == "logement":
            #: Un etage, c'est une piece de plus de la MEME empreinte — jamais
            #: une piece plus grande (voir `piece_de_logement`).
            en_haut = f"{slug}_haut" if etages >= 2 else None
            if en_haut:
                bas = piece_de_logement(slug, largeur, hauteur, porte,
                                        etage=en_haut, variante=self.posees)
                haut = piece_de_logement(en_haut, largeur, hauteur, porte, etage=slug,
                                         haut=True, variante=self.posees)
                # ⚠️ LES DEUX ESCALIERS OU AUCUN : un escalier qui ne redescend
                # pas laisse le joueur pris en haut (la porte du bas est la
                # seule sortie). Une piece trop petite pour poser une marche
                # hors de portee de sa porte n'a donc pas d'etage du tout.
                if all(any(pt["type"] == "escalier" for pt in piece["points"])
                       for piece in (bas, haut)):
                    self.pieces[slug], self.pieces[en_haut] = bas, haut
                    return slug
            self.pieces[slug] = piece_de_logement(slug, largeur, hauteur, porte,
                                                  variante=self.posees)
        else:
            self.pieces[slug] = piece_de_commerce(
                slug, quoi, largeur, hauteur, porte, variante=self.posees, standing=standing)
        return slug

    def premiere_du_genre(self, famille: str | None) -> bool:
        """Cette famille-la n'a encore ouvert NULLE PART : alors celle-ci ouvre.

        ⚠️ Sans cette regle, une famille de commerce peut n'ouvrir aucune porte
        de toute la ville : il faut qu'un batiment tire cette enseigne-la, qu'il
        soit assez grand pour la piece, ET qu'il gagne le de — trois chances qui
        se multiplient, et quatre familles sur dix restaient des couleurs
        d'enseigne qui ne menent jamais a rien. Le de decide du NOMBRE de portes
        qui s'ouvrent ; il n'a pas a decider qu'un pan entier de la ville
        n'existe pas. La premiere qui peut, ouvre.
        """
        if not famille or famille in self.genres_ouverts:
            return False
        self.genres_ouverts.add(famille)
        return True

    def _a_quoi_sert(self, genre: str, ancre: tuple[int, int] | None) -> tuple[str | None, tuple | None]:
        """Ce batiment-ci : un commerce (avec quelle enseigne), un logement, rien.

        ⚠️ C'est ici que se joue la demande de Martin : « plus de variete de
        commerces, ou bien enleve des devantures pour mettre des residences ».
        Les deux, en fait — un ilot commercant garde ses enseignes, mais
        `PART_LOGEMENT` d'entre elles deviennent des immeubles a logements.
        Une rue ou CHAQUE batiment est un commerce n'est pas une rue
        commercante : c'est un catalogue.
        """
        if ancre is None:
            return None, None                      # pas de facade sur rue : rien a peindre
        if genre in ("maisons", "banlieue"):
            return "logement", None
        if genre not in GENRES_COMMERCANTS:
            return None, None
        if genre == "commerces" and self.des_devanture.chance(self.PART_LOGEMENT):
            return "logement", None
        return "commerce", self.choisir_enseigne(*ancre)

    def _contenu(self, genre: str) -> str:
        """Ce qu'une parcelle porte. ⚠️ UN SEUL TIRAGE, et il ne bouge pas.

        ⚠️ **`jardin` devient `parc`, UNE SORTE POUR UNE SORTE**, et pas une
        part de plus ni de moins. Le gazon nu etait le « champ » que Martin a
        nomme ; ce qui le remplace est un parc de quartier. La part de bati, la
        part de stationnement, et surtout **le tirage** ne bougent pas d'un
        centieme.

        ⚠️ **Et c'est pour ca qu'on ne met pas de terrain vague a la place.**
        Mesure du 16 sept. 2026 : en envoyant une partie de ces lots vers
        `vague`, le semis du terrain vague (un dechet par six tuiles) remplacait
        celui du gazon (un arbre par dix) — pas le meme nombre de tirages dans
        le meme de, donc **toute la ville se rebattait**. Dix juges sont tombes
        d'un coup, et pas un ne parlait de terrain vague : une barriere d'usine
        dont la couronne passait sur une case de stationnement, un buisson que
        la balle du banc ne rencontrait plus, deux enfants qui ne jouaient plus
        au ballon. Les terrains vagues restent donc exactement ou ils etaient —
        ils changent de SURFACE (de la friche, des dechets), pas de place.
        """
        tirage = self.des.flottant()
        if genre == "maisons":
            return "bati" if tirage < 0.74 else ("parc" if tirage < 0.92 else "stationnement")
        if genre == "banlieue":
            return "bati" if tirage < 0.72 else ("parc" if tirage < 0.94 else "stationnement")
        if genre == "hangars":
            return "bati" if tirage < 0.80 else ("stationnement" if tirage < 0.95 else "vague")
        if genre == "industriel":
            # La Shop, c'est autant d'asphalte vide que de tole : des cours de
            # manoeuvre, des terrains de ferraille, et trois entrepots dedans.
            return "bati" if tirage < 0.60 else ("stationnement" if tirage < 0.88 else "vague")
        if genre == "gang":
            return "bati" if tirage < 0.70 else ("stationnement" if tirage < 0.85 else "vague")
        return "bati" if tirage < 0.88 else ("vague" if tirage < 0.95 else "stationnement")

    def _pose_batiment(self, px: int, py: int, pl: int, ph: int, genre: str,
                       force: bool = False) -> list | None:
        """Un batiment dans sa parcelle, avec des marges tirees au sort.

        Les marges sont ce qui cree les ruelles, les cours et les dents creuses
        entre deux immeubles colles.

        ⚠️ Il retient aussi son EMPREINTE (`self.empreinte_du_batiment`) : c'est
        elle, et pas la parcelle, qu'on compare au plancher de la piece qui
        s'ouvre derriere. Une parcelle de 6 x 5 peut ne porter qu'un batiment
        de 3 x 3 une fois ses marges tirees — comparer a la parcelle, c'est se
        mentir de trois fois la surface.
        """
        if force:
            # ⚠️ UN LIEU GARANTI PREND SA PARCELLE EN ENTIER : pas de marge, pas
            # de cour, pas de coin mordu. Parce qu'une porte impose une taille
            # minimale a son batiment — le garage Bandini doit rentrer dans le
            # garage Bandini — et parce que c'est vrai : un poste de police, une
            # fourriere, une usine occupent leur terrain. Les marges tirees au
            # sort, elles, font les ruelles entre les immeubles ORDINAIRES.
            ouest = est = nord = sud = 0
        elif genre == "maisons":
            ouest, est = self.des.entier(0, 2), self.des.entier(0, 2)
            nord, sud = self.des.entier(0, 3), self.des.entier(0, 2)
        elif genre == "banlieue":
            # ⚠️ La banlieue se reconnait au VIDE autour des maisons, pas aux
            # maisons : des marges larges, et le gazon qu'on voit entre deux.
            ouest, est = self.des.entier(1, 4), self.des.entier(1, 4)
            nord, sud = self.des.entier(1, 5), self.des.entier(1, 3)
        elif genre in ("hangars", "industriel"):
            ouest = est = 1 if self.des.chance(0.35) else 0
            nord, sud = self.des.entier(0, 2), self.des.entier(0, 1)
        else:
            # ⚠️ Un immeuble de centre-ville colle a son voisin : la marge est
            # l'exception (une ruelle, une dent creuse), pas la regle.
            ouest = 1 if self.des.chance(0.22) else 0
            est = 1 if self.des.chance(0.22) else 0
            nord = 1 if self.des.chance(0.35) else 0
            sud = 1 if self.des.chance(0.25) else 0
        # ⚠️ Les marges cedent avant le batiment : une parcelle mince ne doit
        # pas rendre un batiment de deux tuiles — ou pas de batiment du tout.
        while pl - ouest - est < 3 and (ouest or est):
            if est:
                est -= 1
            else:
                ouest -= 1
        while ph - nord - sud < 3 and (nord or sud):
            if nord:
                nord -= 1
            else:
                sud -= 1
        bx, by = px + ouest, py + nord
        bl, bh = pl - ouest - est, ph - nord - sud
        if bl < 3 or bh < 3:
            return None
        tuiles = {(bx + i, by + j) for j in range(bh) for i in range(bl)}
        if force:
            pass
        elif bl >= 9 and bh >= 6 and self.des.chance(0.32):
            # Un U autour d'une cour ouverte au sud.
            cl = self.des.entier(2, bl - 6)
            cx = bx + self.des.entier(2, bl - cl - 2)
            ch = self.des.entier(2, bh - 3)
            tuiles -= {(cx + i, by + bh - 1 - j) for j in range(ch) for i in range(cl)}
        elif bl >= 6 and bh >= 5 and self.des.chance(0.30):
            # Un L : on mord un coin au sud.
            cl, ch = self.des.entier(2, bl // 2), self.des.entier(2, bh // 2)
            coin = bx if self.des.chance(0.5) else bx + bl - cl
            tuiles -= {(coin + i, by + bh - 1 - j) for j in range(ch) for i in range(cl)}
        self.empreinte_du_batiment = len(tuiles)
        #: Et sa BOITE : c'est elle qui dit ou passe l'entree de voiture et ou
        #: tient la piscine. L'empreinte dit combien, la boite dit ou.
        self.boite_du_batiment = (bx, by, bl, bh)
        vitrines = {"commerces": 0.5, "maisons": 0.12, "banlieue": 0.10,
                    "hangars": 0.03, "industriel": 0.05, "gang": 0.08}.get(genre, 0.3)
        if force:
            # Un batiment garanti garde sa masse : ni cour ni coin mordu.
            tuiles = {(bx + i, by + j) for j in range(bh) for i in range(bl)}
        self.tuiles_du_batiment = tuiles
        return self.batiment_forme(tuiles, vitrines, genre)

    # --- La fourriere (M9) --------------------------------------------------

    #: La cour, en tuiles. ⚠️ Elle ne prend PAS tout l'ilot : un bloc fusionne
    #: de La Shop fait 39 x 24 tuiles, et une fourriere de cette taille serait
    #: un quartier a elle seule. Le lot prend le sud-est, le reste redevient de
    #: l'industriel ordinaire — et la cour garde des voisins, ce qui est bien
    #: le genre d'endroit ou on la met.
    LOT_L, LOT_H = 22, 16
    #: Une place : un char de 48 px (l'autobus) tient dans trois tuiles, et il
    #: faut de quoi ouvrir la portiere a cote.
    PLACE_L, PLACE_H = 4, 3
    #: La guerite, et la grille — la seule ouverture de la cloture.
    GUERITE_L, GUERITE_H, GRILLE_L = 6, 4, 4

    def _fourriere(self, x: int, y: int, largeur: int, hauteur: int, special: dict) -> None:
        """Une cour d'asphalte cloturee, une guerite, UNE grille.

        ⚠️ Tout le lot tient sur une propriete de la cloture : le GRILLAGE
        s'enjambe (solidite 4) et arrete les chars. C'est ce qui fait les deux
        facons de reprendre son char sans une ligne de code pour les
        distinguer : par la grille, en payant au comptoir ; ou par-dessus la
        cloture, a pied — une seconde en haut, et le lot appelle.

        ⚠️ Et c'est du grillage, PAS du barbele, alors qu'un vrai lot municipal
        serait barbele : « on le reprend par-dessus la cloture » est la moitie de
        ce qui rend la fourriere interessante. Du barbele la, et il ne reste
        qu'une caisse a payer.

        ⚠️ Et il n'y a QU'UNE grille. Deux ouvertures, et sortir son char sans
        payer ne demanderait plus rien a personne.
        """
        lot_l, lot_h = min(largeur, self.LOT_L), min(hauteur, self.LOT_H)
        lx, ly = x + largeur - lot_l, y + hauteur - lot_h
        if lx - x >= 10:
            self._ilot_bati(x, y, lx - x, hauteur, genre="industriel")
        else:
            lx, lot_l = x, largeur
        if ly - y >= 8:
            self._ilot_bati(lx, y, lot_l, ly - y, genre="industriel")
        else:
            ly, lot_h = y, hauteur

        self.rect(lx, ly, lot_l, 2, "x")                        # ruelle derriere
        self.rect(lx, ly + lot_h - 2, lot_l, 2, ".")            # trottoir devant
        zy, zh = ly + 2, lot_h - 4
        if zh < 10 or lot_l < 16:  # pragma: no cover - garde-fou de relecture du plan
            raise ValueError(f"le lot de la fourriere ne tient pas : {lot_l} x {zh}")
        self.rect(lx, zy, lot_l, zh, "p")
        # ⚠️ La cour se range EN CASES, comme tous les autres stationnements de
        # la ville. Elle etait un rectangle d'asphalte avec des places
        # calculees a la main : des chars saisis ranges de travers dans un lot
        # municipal, c'est exactement le defaut qu'on a corrige partout
        # ailleurs. `_stationnement` pose les rangees, les allees et l'ilot de
        # beton — mais PAS son tremplin.
        self._stationnement(lx + 1, zy + 1 + self.GUERITE_H,
                            lot_l - 2, zh - 2 - self.GUERITE_H,
                            genre="industriel", tremplin=False)
        # La guerite, au coin nord-ouest : elle donne sur la cour, pas sur la
        # rue — on entre par la grille, comme tout le monde.
        guerite = {(lx + 1 + i, zy + 1 + j)
                   for i in range(self.GUERITE_L) for j in range(self.GUERITE_H)}
        facades = self.batiment_forme(guerite)
        # ⚠️ Avant la premiere tuile de grillage : ce que le voisin a deja pose
        # le long du lot s'en va. Une cloture par ligne mitoyenne, et celle-ci
        # n'est pas negociable.
        self.degager_les_doubles(lx, zy, lot_l, zh)
        gx = lx + lot_l - self.GRILLE_L - 2
        for i in range(lot_l):
            if not gx <= lx + i < gx + self.GRILLE_L:
                self.sol[zy + zh - 1][lx + i] = GRILLAGE
            self.sol[zy][lx + i] = GRILLAGE
        for j in range(zh):
            self.sol[zy + j][lx] = GRILLAGE
            self.sol[zy + j][lx + lot_l - 1] = GRILLAGE
        for tx, ty in guerite:                                  # la guerite reste batie
            if self.sol[ty][tx] == GRILLAGE:
                self.sol[ty][tx] = "F"
        porte = self.poser_porte(facades, special)
        # ⚠️ Les places se LISENT dans les cases, elles ne s'inventent plus.
        # Une place est le FOND d'une case (la tuile qui porte le pare-chocs) :
        # c'est la meme regle que `placeStationnee` cote navigateur, et c'est
        # ce qui garantit qu'un char saisi tombe dans ses lignes au pixel pres.
        places = []
        for ty in range(zy + 1, zy + zh - 1):
            for tx in range(lx + 1, lx + lot_l - 1):
                sens = LEGENDE.get(self.sol[ty][tx], {}).get("case")
                if not sens:
                    continue
                dx, dy = PAS[{"N": "^", "S": "v", "O": "<", "E": ">"}[sens]]
                if self.sol[ty + dy][tx + dx] == self.sol[ty][tx]:
                    continue                      # pas le fond de la case
                places.append({"x": tx, "y": ty, "sens": sens})
        for _ in range(3):
            self.poser_decor("debris",
                             lx + self.des.entier(self.GUERITE_L + 3, lot_l - 3),
                             zy + self.des.entier(1, self.GUERITE_H))
        self.fourriere = {
            "x": lx, "y": zy, "largeur": lot_l, "hauteur": zh,
            "grille": {"x": gx, "y": zy + zh - 1, "largeur": self.GRILLE_L},
            "porte": {"x": porte[0], "y": porte[1]} if porte else None,
            "places": places,
        }

    @staticmethod
    def _tirages_de_semis(largeur: int, hauteur: int) -> int:
        """Combien de tirages coute UNE pose au hasard dans une boite.

        ⚠️ `Des.entier(a, b)` rend `a` SANS TIRER quand `b <= a` : une boite
        large d'une tuile ne consomme pas de de pour son abscisse. Le compte
        doit le savoir, sinon ce qu'on brule ne vaut pas ce qu'on tirait — et
        « brule ce que tu ne tires plus » ne veut plus rien dire.
        """
        return (1 if largeur > 1 else 0) + (1 if hauteur > 1 else 0)

    def _terrain_vague(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Un lot laisse a l'abandon : de la friche, des dechets, une cloture.

        ⚠️ **DE LA FRICHE, PAS DU GAZON** — demande de Martin (« mets des
        terrains vague un peu salle et avec des deches »), et il a nomme un
        vrai defaut : ce terrain-ci se peignait avec `,`, l'herbe des parcs et
        des cours de banlieue. Mesure du 16 sept. 2026 : quatorze lots,
        922 tuiles de pelouse, et **un gravat pose par dix-sept tuiles** — de
        loin, un carre de gazon avec trois points dessus. On y marche
        aujourd'hui sur de la terre seche (`;`), et ce qu'on contourne en le
        traversant n'est plus le gravat tout seul mais tout ce que le quartier
        y a jete (`DECHETS`).
        """
        self.rect(x, y, largeur, hauteur, ";")
        # ⚠️ Les cours de La Shop sont BARBELEES : de la ferraille derriere une
        # cloture qu'on enjambe, ca ne dit rien ; derriere du barbele, ca dit
        # « quelqu'un a paye pour que personne n'entre ». Ailleurs, c'est du
        # grillage — un terrain vague de quartier, on y passe.
        # ⚠️ ET IL EST CEINTURE, pas borde. Le terrain vague peignait UN cote —
        # le sud — et encore, une tuile sur deux : une ligne pointillee d'ou
        # rien ne suivait, et c'est elle qui faisait le gros des 216 tuiles de
        # barre droite mesurees dans `clore`. Un terrain vague, c'est justement
        # ce qu'on a ferme et laisse a l'abandon ; sans les quatre cotes, rien
        # ne dit qu'il est a quelqu'un. La trouee, elle, reste garantie : sans
        # elle, l'enceinte fermee devient une poche que `boucher_les_poches`
        # mure, et la ferraille disparait sans un mot.
        cloture = BARBELE if self.district_en(x, y) == "shop" else GRILLAGE
        # ⚠️ TROIS COTES, ouvert au NORD sur la ruelle : c'est par la qu'on
        # entre dans un terrain vague, et c'est aussi ce qui garantit qu'il
        # n'est jamais une poche.
        self.clore(x, y, largeur, hauteur, cloture, cotes="SEO")
        self.des.brule(max(0, largeur - 2))   # une tuile sur deux hors trouee, autrefois
        # ⚠️ ET ON BRULE LE VIEUX SEMIS : un gravat par douze tuiles, deux
        # tirages chacun. Sans ca, la ville entiere se rebat (voir `des_dechet`).
        self.des.brule(self._tirages_de_semis(largeur, hauteur) * max(1, largeur * hauteur // 12))
        # ⚠️ Le TIRAGE DE LA SORTE D'ABORD, la place ensuite, et toujours les
        # deux : `poser_decor` refuse une tuile reservee ou deja prise, et si le
        # refus sautait le tirage de la sorte, le semis se decalerait selon ce
        # qu'il rencontre — deux terrains vagues de la meme taille n'auraient
        # plus le meme nombre de tirages, et le lot d'a cote changerait avec eux.
        for _ in range(max(2, largeur * hauteur // PART_DECHET)):
            quoi = self.des_dechet.choix(DECHETS)
            dx, dy = x + self.des_dechet.entier(0, largeur - 1), y + self.des_dechet.entier(0, hauteur - 1)
            if self.poser_decor(quoi, dx, dy):
                self.dechets_semes.add((dx, dy))
        for _ in range(max(1, largeur * hauteur // PART_MAUVAISE_HERBE)):
            self.poser_decor("buisson", x + self.des_dechet.entier(0, largeur - 1),
                             y + self.des_dechet.entier(0, hauteur - 1))
        # Un tremplin de planches sur les gravats : le terrain vague est
        # l'endroit ou une rampe se raconte toute seule. ⚠️ On COUPE la cloture
        # devant : sinon c'est un tremplin derriere un grillage, et on vient de
        # passer une heure a se debarrasser de ceux-la. Apres les debris, pour
        # ne pas en poser un au milieu de la piste.
        if largeur >= 5 and hauteur >= 4 and self.des_rampe.chance(PART_RAMPE_COUR):
            cx = x + largeur // 2
            self.proposer_rampe([(cx, y + hauteur // 2, None)],
                                cloture=(cx, y + hauteur - 1))
        # ⚠️ **ET ON DEGAGE** : la moitie de ce qu'on vient de jeter la arrete un
        # pieton (`DECOR_SOLIDE`), et un lot qu'on ne traverse pas est un lot
        # qui n'existe pas.
        self.degager_le_decor(x, y, largeur, hauteur)

    #: Ce qu'un chemin TRAVERSE pour rejoindre la rue : de l'herbe, la dalle,
    #: la couronne d'abord. ⚠️ L'ABORD AUSSI : depuis le trottoir a une tuile, la
    #: couronne du bloc se glisse entre la bande de devant et la dalle. Il se
    #: foule comme l'herbe ; l'exclure rendait la liste vide, et plus une seule
    #: cour de banlieue n'avait d'entree ni de sentier. Tout le reste — du bati,
    #: une cloture, une piscine — arrete.
    VERS_LA_RUE = (",", ".", "_")

    #: Jusqu'ou l'on va la chercher. ⚠️ DIX tuiles, pas six : les marges de
    #: banlieue vont jusqu'a cinq tuiles, plus deux de bande de devant, la
    #: couronne et le trottoir. A six, la fenetre s'arretait juste avant la
    #: chaussee et rendait la liste vide — quinze portes sur vingt-sept
    #: restaient sans sentier, et rien ne le disait sinon le juge.
    PORTEE_VERS_LA_RUE = 10

    #: Ce qui compte comme LA RUE quand on y rattache un STATIONNEMENT : ce sur
    #: quoi on roule (la chaussee, la ruelle) et ce sur quoi on marche depuis la
    #: rue (le trottoir, et la couronne d'abord qui le borde — des paves, pas
    #: une cour). ⚠️ Une entree de cour, elle, ne vise que la chaussee : on
    #: arrive chez les gens par la rue, pas par le fond du terrain.
    RUE_DU_LOT = ("route", "ruelle", "trottoir", "abord")

    def _chemin_vers_la_rue(self, x: int, y: int, dx: int, dy: int,
                            arrivee: tuple[str, ...] = ("route",)) -> list[tuple[int, int]]:
        """Les tuiles a paver depuis (x, y) — comprise — jusqu'a la rue, exclue.

        ⚠️ UN TERRAIN NE TOUCHE PAS LA RUE : entre les deux il y a la bande de
        devant — deux rangees de GAZON en banlieue, parce que « la banlieue se
        reconnait au vide » — puis la couronne d'abord et le trottoir. Un chemin
        qui s'arrete au bord du terrain s'arrete donc dans l'herbe, a trois
        tuiles de la rue : il ne mene nulle part, et une entree qui fait pareil
        n'est pas une entree, c'est un carre d'asphalte. On va jusqu'a la rue,
        ou on ne fait rien — c'est ce que dit la liste vide.

        `arrivee` : ce qui compte comme la rue, en champs de la LEGENDE. Une
        entree de cour ne vise que la chaussee ; un stationnement se contente de
        tout ce qui borde la rue (`RUE_DU_LOT`) — ce qu'il vise en premier, il
        le traverserait sinon, et l'entree mangerait la dalle.
        """
        chemin: list[tuple[int, int]] = []
        for _ in range(self.PORTEE_VERS_LA_RUE):
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                return []
            glyphe = self.sol[y][x]
            fiche = LEGENDE[glyphe]
            if any(fiche.get(quoi) for quoi in arrivee):
                return chemin                     # arrive : la rue est la
            if glyphe not in self.VERS_LA_RUE:
                return []                         # du bati, une cloture : pas de passage
            chemin.append((x, y))
            x, y = x + dx, y + dy
        return []

    #: Une entree de voiture sur trois porte une CASE, donc une auto garee.
    #: ⚠️ Pas toutes : si chaque bungalow en porte une, la banlieue se remplit
    #: de chars stationnes et le budget d'entites y passe. Les autres restent de
    #: l'asphalte nu — ce qui est aussi la vraie vie.
    PART_ENTREE_AVEC_CASE = 0.33

    def _terrain_de_banlieue(self, parcelle: tuple[int, int, int, int],
                             boite: tuple[int, int, int, int],
                             porte: tuple[int, int] | None) -> None:
        """Un terrain de banlieue : une entree, un sentier, une cour derriere.

        ⚠️ M8 a eu raison sur le principe — « la banlieue se reconnait au VIDE
        autour des maisons » — et ce vide etait litteralement vide : du gazon,
        un arbre par dix tuiles, pose au sort. Or un terrain de banlieue est le
        CONTRAIRE du vide : il est plein des traces de la vie de quelqu'un.

        ⚠️ L'ORDRE compte, et c'est tout le travail : le sentier part de la
        PORTE, donc il se trace apres elle ; la piscine et le cabanon se posent
        apres le sentier, donc ils ne le coupent pas. Pose dans l'autre sens, un
        cabanon se retrouve sur le pas de la porte.
        """
        px, py, pl, ph = parcelle
        bx, by, bl, bh = boite
        if bl <= 0 or bh <= 0:
            return
        occupe: set[tuple[int, int]] = set()

        def jusqu_a_la_rue(x: int, depart: int) -> list[int]:
            """Les rangees a paver depuis `depart` jusqu'a la chaussee, exclue.

            ⚠️ La ruelle ne compte PAS : une entree de cour va au chemin par ou
            l'on arrive chez les gens, pas au fond du terrain. Le reste de la
            regle — ce qu'on traverse, jusqu'ou l'on cherche, et pourquoi une
            liste vide vaut « pas d'entree » — vit dans `_chemin_vers_la_rue`,
            ou le stationnement la lit aussi.
            """
            return [y for _, y in self._chemin_vers_la_rue(x, depart, 0, 1)]

        # --- Le sentier de la porte a la rue --------------------------------
        # ⚠️ Sans lui, on marche sur le gazon pour entrer chez les gens — et
        # c'est precisement ce qui donne l'impression du « pas fini ».
        if porte:
            sx = porte[0]
            for sy in jusqu_a_la_rue(sx, porte[1] + 1):
                # ⚠️ L'abord se pave comme l'herbe : le sentier traverse la
                # couronne du bloc jusqu'a la dalle, sinon il s'arrete une tuile
                # avant le trottoir — et un juge le suivait a la trace.
                if self.sol[sy][sx] in (",", "_"):
                    self.sol[sy][sx] = "."
                occupe.add((sx, sy))

        # --- L'entree de voiture, et l'auto dedans --------------------------
        # ⚠️ Une entree TOUCHE LA RUE, toujours. Meme regle que « toute rangee
        # de stationnement touche une allee » : une entree qui ne rejoint pas la
        # chaussee n'est pas une entree, c'est un carre d'asphalte.
        cotes = [x for x in (bx - 1, bx + bl) if px <= x < px + pl]
        cotes = [x for x in cotes if not any((x, y) in occupe for y in range(by, py + ph + 4))]
        if cotes:
            ex = self.des.choix(cotes)
            hautes = [y for y in range(by, py + ph) if self.sol[y][ex] == ","]
            basses = jusqu_a_la_rue(ex, py + ph)
            # ⚠️ Rien si le chemin ne va pas jusqu'au bout : une entree qui ne
            # rejoint pas la chaussee n'est pas une entree.
            if hautes and basses and hautes[-1] == py + ph - 1:
                bande = [(ex, y) for y in hautes + basses]
                for (x, y) in bande:
                    self.sol[y][x] = "p"
                    occupe.add((x, y))
                # La case regarde la maison : le nez au NORD.
                if len(bande) >= CASE_CREUX and self.des.chance(self.PART_ENTREE_AVEC_CASE):
                    for (x, y) in bande[:CASE_CREUX]:
                        self.sol[y][x] = "^"

        # --- La cour derriere : piscine, cabanon, corde a linge -------------
        cour = [(x, y) for y in range(py, by) for x in range(px, px + pl)
                if self.sol[y][x] == "," and (x, y) not in occupe and (x, y) not in self.reserve]
        if len(cour) >= 6 and self.des.chance(0.30):
            # ⚠️ Une piscine se pose d'un bloc de deux sur deux, jamais en L :
            # une piscine en L n'est pas une piscine, c'est une flaque.
            for (x, y) in cour:
                carre = [(x + i, y + j) for j in (0, 1) for i in (0, 1)]
                if all(c in cour for c in carre):
                    for (cx, cy) in carre:
                        self.sol[cy][cx] = "o"
                        occupe.add((cx, cy))
                    break
        for quoi, chance in (("cabanon", 0.45), ("corde_a_linge", 0.35)):
            libres = [c for c in cour if c not in occupe]
            if libres and self.des.chance(chance):
                x, y = self.des.choix(libres)
                if self.poser_decor(quoi, x, y):
                    occupe.add((x, y))

        # --- Le BBQ, devant, du cote de la porte ----------------------------
        # --- Et la cour arriere se CLOTURE ---------------------------------
        # ⚠️ « Des cours delimitees » : le plan le promet depuis M8, et seuls les
        # terrains VIDES le tenaient (`_jardin`). Une banlieue ou les maisons
        # n'ont pas de cour cloturee et ou les terrains vacants en ont une, c'est
        # l'inverse de ce qu'on voit par la fenetre. Trois cotes — le sud reste
        # ouvert sur la maison, et c'est ce qui garantit qu'une cour arriere
        # n'est jamais une poche. La barriere, elle, donne sur la ruelle.
        # ⚠️ APRES la piscine et le cabanon : `cloture_possible` refuse ce qui
        # est deja solide, donc une palissade ne peut pas leur passer dessus.
        # ⚠️ **DEUX TUILES DE FOND SUFFISENT, ET LA CHANCE MONTE**, parce que
        # c'est ICI que vit maintenant la palissade de bois. Mesure du
        # 16 sept. 2026 : sur 36 terrains de banlieue, SIX seulement avaient
        # trois tuiles derriere la maison, deux ont appele `clore`, et il
        # restait ONZE tuiles de palissade dans toute la ville. L'image de
        # « cours delimitees » que M8 promet tenait donc aux LOTS VIDES
        # (l'ancien `_jardin` en cloturait un sur deux) — c'est-a-dire a
        # l'exact inverse de ce qu'on voit par la fenetre, et son propre
        # commentaire le disait deja. Les lots vides sont devenus des parcs, et
        # un parc ne se cloture pas : la palissade revient donc aux cours, ou
        # elle a toujours du etre.
        if by - py >= 2 and pl >= 3 and self.des_cloture.chance(0.8):
            self.clore(px, py, pl, by - py, BOIS, cotes="NEO", cote_ouvert="N", ouverture=1)

        devanture = [(x, y) for y in range(by + bh, py + ph) for x in range(px, px + pl)
                     if self.sol[y][x] == "," and (x, y) not in occupe
                     and (x, y) not in self.reserve]
        if devanture and self.des.chance(0.30):
            x, y = self.des.choix(devanture)
            if self.poser_decor("bbq", x, y):
                occupe.add((x, y))

    #: Le sentier d'un parc de quartier, et sa largeur. ⚠️ UNE tuile, pas deux
    #: (les allees de `_parc` en font deux) : un lot de 7 x 7 avec une allee de
    #: deux tuiles, c'est 28 % du parc en poussiere de pierre — une dalle avec
    #: du gazon autour, exactement le reproche fait au parc de ville avant lui.
    SENTIER_DE_PARC = "g"

    #: Une tuile de sentier sur combien porte un banc a cote. Un banc tous les
    #: quatre pas, c'est un parc ; un banc par lot, c'est un banc.
    PART_BANC_DE_PARC = 4

    #: Un arbre par combien de tuiles. ⚠️ Le gazon nu qu'on remplace en posait
    #: un par DIX (arbre ou buisson, et il n'en tenait qu'un par seize) : de la
    #: rue, on voyait trois piquets sur une pelouse. Un parc de ville en met un
    #: par quatorze, un bois un par sept ; un parc de quartier tient entre les
    #: deux — assez serre pour faire une masse verte, assez clair pour qu'on
    #: voie le sentier au travers.
    PART_ARBRE_DE_PARC = 8
    PART_BUISSON_DE_PARC = 12

    #: ⚠️ **PAS DE TABLE A PIQUE-NIQUE**, et c'est un juge qui l'a tranche :
    #: « tout ce qui meuble la greve est au bord de l'eau » (`test_greve`) lit
    #: le TYPE du decor, pas l'endroit — une table dans un parc de quartier, a
    #: quatre-vingts tuiles de la baie, le fait tomber. Le juge a raison sur le
    #: fond (une table posee loin de l'eau, sur la greve, serait un defaut), et
    #: la table a pique-nique est aujourd'hui un meuble de PLAGE. Un banc fait
    #: le meme travail ici, et il est deja de la ville.

    def _parc_de_quartier(self, x: int, y: int, largeur: int, hauteur: int,
                          genre: str = "commerces") -> None:
        """Le lot qu'on n'a pas bati et dont le quartier a fait quelque chose.

        ⚠️ **IL REMPLACE `_jardin`**, qui posait du gazon et quatre arbres —
        et c'est de ces lots-la que Martin parlait : « au lieu des champs [...]
        aussi des parcs ». Mesure du 16 sept. 2026 : dix lots, 406 tuiles de
        pelouse, **25 objets en tout** (un par seize tuiles), et en banlieue une
        palissade autour. Une cour arriere sans maison, cloturee, vide : de haut,
        un champ.

        ⚠️ **CE QUI FAIT UN PARC, C'EST LE SENTIER**, pas les arbres. Un carre
        de gazon plante d'arbres reste un terrain ; le jour ou quelque chose le
        TRAVERSE, c'est un endroit ou l'on va. C'est aussi lui qui range le
        reste : les bancs le bordent (un banc au hasard sur la pelouse regarde
        un buisson), et sa reserve garantit qu'aucun arbre ne le bouche —
        la lecon de `_allee`, payee une fois pour toutes dans `_parc`.

        ⚠️ **Et il ne se cloture pas.** Une cour se ferme, un parc s'ouvre : la
        palissade que `_jardin` posait une fois sur deux en banlieue disait
        « c'est a quelqu'un », ce qui est le contraire de ce qu'on veut lire ici.
        """
        self.rect(x, y, largeur, hauteur, ",")
        # --- Ce que le gazon nu tirait, et qu'on ne tire plus ---------------
        # ⚠️ Il tirait UNE CLOTURE en banlieue (`des_cloture` : la chance, puis
        # la trouee de `clore`) et un arbre ou un buisson par dix tuiles
        # (`des` : la sorte, puis les deux coordonnees). On brule les deux dans
        # LEUR de, exactement dans l'ordre et sous les memes conditions —
        # autrement la palissade de la cour d'a cote change de place et la
        # ville se rebat (voir `des_dechet`).
        sorties = [i for i in range(1, largeur - 1) if self.marchable_en(x + i, y + hauteur)]
        if (genre == "banlieue" and largeur >= 3 and hauteur >= 3
                and sorties and self.des_cloture.chance(0.7)):
            self.des_cloture.brule(1)          # la trouee que `clore` aurait tiree
        self.des.brule((1 + self._tirages_de_semis(largeur, hauteur))
                       * max(1, largeur * hauteur // 10))
        # --- Le sentier, d'un bord a l'autre, dans le sens long -------------
        dans_la_largeur = largeur >= hauteur
        if dans_la_largeur:
            sy = y + hauteur // 2
            sentier = [(cx, sy) for cx in range(x, x + largeur)]
            cotes = ((0, -1), (0, 1))
        else:
            sx = x + largeur // 2
            sentier = [(sx, cy) for cy in range(y, y + hauteur)]
            cotes = ((-1, 0), (1, 0))
        for cx, cy in sentier:
            self.sol[cy][cx] = self.SENTIER_DE_PARC
            self.reserver(cx, cy, 1, 1)
        # --- Les bancs, LE LONG du sentier ----------------------------------
        bords = [(cx + dx, cy + dy) for cx, cy in sentier for dx, dy in cotes
                 if x <= cx + dx < x + largeur and y <= cy + dy < y + hauteur]
        for _ in range(max(1, len(sentier) // self.PART_BANC_DE_PARC)):
            if not bords:
                break
            self.poser_decor("banc", *self.des_dechet.choix(bords))
        # --- Les arbres et les buissons, partout ailleurs -------------------
        for _ in range(max(2, largeur * hauteur // self.PART_ARBRE_DE_PARC)):
            self.poser_decor("arbre", x + self.des_dechet.entier(0, largeur - 1),
                             y + self.des_dechet.entier(0, hauteur - 1))
        for _ in range(max(1, largeur * hauteur // self.PART_BUISSON_DE_PARC)):
            self.poser_decor("buisson", x + self.des_dechet.entier(0, largeur - 1),
                             y + self.des_dechet.entier(0, hauteur - 1))

    # --- Les rampes ---------------------------------------------------------

    def _roulable(self, x: int, y: int, piste: bool = False) -> bool:
        """Une tuile ou un char passe VRAIMENT : rien de solide, pas de decor,
        pas le devant d'une porte.

        ⚠️ Toute solidite non nulle arrete un char — une borne-fontaine (3) comme
        une cloture (4, 5), meme si un pieton passe par-dessus les deux. Une
        cloture dans l'elan, c'est un elan qui n'existe pas : c'est ce qui rendait
        les rampes de la cour des gangs injouables — on les voyait, on ne pouvait
        pas les prendre.

        ⚠️ `piste` : l'elan et la reception passent sur le devant d'une porte
        PEINTE (`devants_peints`). Ils se gardent vides — rien ne s'y plante
        apres eux —, et c'est tout ce que ce devant demande. Le pied et la
        levre, eux, sont une chose posee : jamais devant une porte.
        """
        return (0 <= x < self.largeur and 0 <= y < self.hauteur
                and solidite(self.sol[y][x]) == 0
                and (x, y) not in self.occupe
                and ((x, y) not in self.reserve or (piste and (x, y) in self.devants_peints)))

    def _course(self, x: int, y: int, dx: int, dy: int, voulu: int) -> int:
        """Combien de tuiles roulables d'affilee dans cette direction."""
        n = 0
        while n < voulu and self._roulable(x + dx * (n + 1), y + dy * (n + 1), piste=True):
            n += 1
        return n

    def _libre_pour_rampe(self, x: int, y: int) -> bool:
        """Ou une rampe a le droit de se poser.

        ⚠️ Jamais sur une voie de circulation : le trafic roule sur des rails,
        et un tremplin au milieu de sa trajectoire enverrait un char dans le
        decor a chaque tour.

        ⚠️ Jamais sur un TROTTOIR non plus, et c'est la vraie lecon du retour de
        Martin : les anciennes rampes avaient de l'elan — vingt et une tuiles !
        — mais uniquement le long du trottoir, entre un grillage et des murs.
        De l'elan qu'on ne peut prendre qu'en roulant sur le trottoir n'est pas
        de l'elan, c'est un couloir. Une rampe se pose la ou les chars passent
        deja : asphalte, stationnement, cour, quai, terrain vague.
        """
        return (self._roulable(x, y) and self.voie[y][x] == "."
                and not LEGENDE[self.sol[y][x]].get("trottoir"))

    def proposer_rampe(self, essais: list[tuple[int, int, tuple[int, int] | None]],
                       cloture: tuple[int, int] | None = None) -> None:
        """Une rampe A ESSAYER quand la ville sera finie : chaque essai est un
        (x, y, axe), et le premier qui tient gagne.

        ⚠️ Meme lecon que les graffitis (« apres les ilots, on tague des murs
        qui existent ») : un tremplin pose pendant les ilots voyait sa
        reception muree par la parcelle d'a cote, batie trois lignes plus tard.
        Mesure avant correctif : trois rampes sur onze retombaient sur un mur.
        """
        self.rampes_proposees.append({"essais": essais, "cloture": cloture})

    def poser_les_rampes(self) -> None:
        """Le tour des propositions, sur la ville FINIE."""
        for proposition in self.rampes_proposees:
            cloture = proposition["cloture"]
            if cloture:
                # Le trou dans le grillage se fait meme si le tremplin ne tient
                # pas : un terrain vague avec sa cloture percee, c'est une
                # image juste de toute facon.
                cx, cy = cloture
                for i in (-1, 0, 1):
                    if 0 <= cx + i < self.largeur and self.sol[cy][cx + i] in CLOTURES:
                        self.sol[cy][cx + i] = ","
            for x, y, axe in proposition["essais"]:
                if self.poser_rampe(x, y, axe):
                    break

    def poser_rampe(self, x: int, y: int, sens: tuple[int, int] | None = None) -> bool:
        """Une rampe de deux tuiles en (x, y) : le pied, puis la levre.

        ⚠️ On ne CHOISIT pas le sens, on le MESURE : les quatre axes sont
        essayes, le plus long gagne, et aucun ne passe sans son elan et sa
        reception. Rien de pose vaut mieux qu'un tremplin contre un mur — un
        tremplin qu'on ne peut pas prendre n'est pas un decor, c'est une
        enigme.
        """
        meilleur = None
        for dx, dy in ([sens] if sens else [(1, 0), (-1, 0), (0, 1), (0, -1)]):
            if not (self._libre_pour_rampe(x, y) and self._libre_pour_rampe(x + dx, y + dy)):
                continue
            # ⚠️ On mesure BIEN AU-DELA du minimum exige : plafonnee au
            # minimum, la mesure donnait la meme note aux quatre axes et « le
            # plus long gagne » ne voulait plus rien dire — l'est gagnait
            # toujours, par ordre de la liste.
            elan = self._course(x, y, -dx, -dy, ELAN_RAMPE * 3)
            reception = self._course(x + dx, y + dy, dx, dy, RECEPTION_RAMPE * 3)
            if elan < ELAN_RAMPE or reception < RECEPTION_RAMPE:
                continue
            if meilleur is None or elan + reception > meilleur[0]:
                meilleur = (elan + reception, dx, dy, reception)
        if meilleur is None:
            return False
        _, dx, dy, reception = meilleur
        self.sol[y][x] = "R"
        self.sol[y + dy][x + dx] = "J"
        # ⚠️ La piste se RESERVE : un arbre pose plus tard au milieu de l'elan
        # rendrait la rampe inutilisable sans qu'aucun juge ne bronche.
        for k in range(-ELAN_RAMPE, RECEPTION_RAMPE + 2):
            self.occupe.add((x + dx * k, y + dy * k))
        # ⚠️ `defi` : cette rampe-ci recoit une MOTO lancee, pas seulement
        # l'auto de reference. Le Grand Saut exige la moto ; son panneau ne se
        # pose que sur une rampe marquee, sinon le defi finit dans un mur et
        # rien nulle part ne le dirait.
        self.rampes.append({"x": x, "y": y, "dx": dx, "dy": dy,
                            "reception": reception, "defi": reception >= RECEPTION_DEFI})
        return True

    # --- Stationnements -----------------------------------------------------

    def _percer_l_entree(self, chemins: list[list] | None,
                         parcelle: tuple[int, int, int, int]) -> None:
        """L'ENTREE d'un lot enclave : de l'asphalte, du bord du terrain
        jusqu'a la rue, large d'une allee.

        ⚠️ ELLE SORT D'UNE ALLEE quand le lot en offre une sur ce bord-la :
        debouchant sur le fond d'une case, elle ferait entrer les autos par le
        pare-chocs de celle qui est deja garee. Quand le bord n'est qu'une
        rangee, on perce quand meme — on traverse une place pour entrer, ce qui
        vaut toujours mieux qu'un lot ou personne n'entre.

        ⚠️ Elle fait DEUX tuiles, comme une allee (de quoi se croiser), et
        tombe le plus pres possible du milieu du lot : c'est la que sa
        circulation passe.
        """
        if not chemins:
            return
        px, py, pl, ph = parcelle
        par_colonne = {chemin[0][0]: chemin for chemin in chemins}
        bord = py + ph - 1                              # la derniere rangee du lot
        allees = [cx for cx in par_colonne if self.sol[bord][cx] == "p"]
        colonnes = sorted(allees or par_colonne)
        paires = [(cx, cx + 1) for cx in colonnes if cx + 1 in colonnes]
        milieu = px + (pl - 1) / 2
        entree = min(paires or [(cx,) for cx in colonnes],
                     key=lambda p: abs(sum(p) / len(p) - milieu))
        for cx in entree:
            for (ex, ey) in par_colonne[cx]:
                self.sol[ey][ex] = "p"
                # ⚠️ RESERVEE, donc libre pour toujours : une entree large de
                # deux tuiles est aussi une place de camion-restaurant aux yeux
                # des `ambulants`, et un camion gare dans l'entree referme le
                # lot qu'on vient d'ouvrir. Meme raison pour un lampadaire ou
                # une borne — rien ne se pose sur le seul chemin qui entre.
                self.entrees.add((ex, ey))
                self.reserver(ex, ey, 1, 1)

    def _bandes_stationnement(self, creux: int) -> list[tuple[str, int]]:
        """Decoupe l'axe PROFOND d'un stationnement en bandes : « R » une
        rangee de cases, « A » une allee de manoeuvre.

        ⚠️ La regle qui tient tout le dessin : TOUTE rangee touche une allee.
        Sans elle on peint de belles cases ou aucune auto ne peut entrer, et
        le stationnement redevient un champ d'asphalte raye au hasard.

        Le motif est donc « R A (R R A)* [R] » : une rangee contre le bord, son
        allee, puis des rangees DOS A DOS qui se partagent l'allee suivante —
        exactement le dessin des vrais. Il faut 4 tuiles pour une rangee, 6
        pour deux, 10 pour trois, 12 pour quatre. Ce qui reste elargit les
        allees, puis longe le bord en voie de contournement.
        """
        rangees = 1
        while 2 * (rangees + 1) + ALLEE * ((rangees + 2) // 2) <= creux:
            rangees += 1
        bandes = [("R", CASE_CREUX), ("A", ALLEE)]
        paires, seule = divmod(rangees - 1, 2)
        for _ in range(paires):
            bandes += [("R", CASE_CREUX), ("R", CASE_CREUX), ("A", ALLEE)]
        if seule:
            bandes.append(("R", CASE_CREUX))
        # ⚠️ Une rangee de plus vaut mieux qu'une allee large, mais une allee
        # de plus de quatre tuiles n'est plus une allee : c'est une place
        # publique. Au-dela, le reste longe le bord — la voie de contournement
        # par ou les autos entrent.
        reste = creux - sum(taille for _, taille in bandes)
        for i, (type_, taille) in enumerate(bandes):
            if type_ == "A" and reste:
                ajout = min(reste, 4 - taille)
                bandes[i] = ("A", taille + ajout)
                reste -= ajout
        if reste:
            bandes.append(("A", reste))
        return bandes

    @staticmethod
    def _nez_au_debut(bandes: list[tuple[str, int]], i: int) -> bool:
        """De quel cote une rangee tourne-t-elle son PARE-CHOCS ?

        Le fond de la case va contre ce qui ferme : le bord du terrain d'abord,
        le dos de la rangee voisine ensuite — et si les deux cotes sont des
        allees, contre la plus etroite, pour laisser la grande a la
        circulation.
        """
        def ferme(k: int) -> int:
            if not 0 <= k < len(bandes):
                return 10                       # le bord du terrain : le mieux
            return 5 if bandes[k][0] == "R" else -bandes[k][1]

        return ferme(i - 1) >= ferme(i + 1)

    def _stationnement(self, x: int, y: int, largeur: int, hauteur: int,
                       genre: str = "commerces", tremplin: bool = True) -> None:
        """Un vrai stationnement : des rangees de cases, des allees pour y
        entrer, et un ilot de beton au bout des rangees.

        Une case fait UNE tuile de large et DEUX de creux — exactement le
        gabarit d'une auto (32 x 16 px), pour qu'une auto garee tombe dans ses
        lignes au pixel pres.

        ⚠️ Avant, une parcelle de stationnement etait un rectangle de « p » et
        le peintre posait une ligne toutes les trois tuiles : de loin, un
        code-barres ; de pres, des places de travers, sans allee et sans
        entree. Le dessin se decide ICI, ou l'on connait la forme du terrain.
        """
        self.rect(x, y, largeur, hauteur, "p")
        # Les allees suivent le GRAND cote : des rangees en travers du long,
        # c'est deux fois moins d'asphalte perdu en manoeuvres.
        debout = largeur >= hauteur
        creux = hauteur if debout else largeur
        longueur = largeur if debout else hauteur
        if creux < CASE_CREUX + 2 or longueur < 3:
            return          # une cour de service, pas un stationnement : nue
        bandes = self._bandes_stationnement(creux)
        allees: list[tuple[int, int]] = []
        d = 0
        for i, (type_, taille) in enumerate(bandes):
            if type_ == "A":
                allees.append((d, taille))
                d += taille
                continue
            vers_le_debut = self._nez_au_debut(bandes, i)
            if debout:
                self.rect(x, y + d, largeur, taille, "^" if vers_le_debut else "v")
            else:
                self.rect(x + d, y, taille, hauteur, "<" if vers_le_debut else ">")
            # Un ilot de beton au bout de la rangee, et un lampadaire une
            # rangee sur deux (deux lampes cote a cote sur le meme ilot, ca
            # eclaire deux fois moins bien et ca coute deux fois plus cher).
            # ⚠️ L'ilot n'est PAS du trottoir : un kiosque a hot-dogs se pose
            # sur le trottoir, et il se poserait au milieu de l'asphalte, sur
            # le pied du lampadaire.
            if genre not in ("hangars", "industriel") and longueur >= 8:
                bouts = [longueur - 1] if longueur < 12 else [0, longueur - 1]
                for k, bout in enumerate(bouts):
                    if debout:
                        ix, iy, il, ih = x + bout, y + d, 1, taille
                    else:
                        ix, iy, il, ih = x + d, y + bout, taille, 1
                    self.rect(ix, iy, il, ih, "I")
                    if i % 2 == 0 and k == 0:
                        if self.poser_decor("lampadaire", ix, iy):
                            self.lampes.append({"x": ix, "y": iy})
            d += taille
        # ⚠️ `tremplin=False` pour la cour de la fourriere : un tremplin dans
        # une allee y serait une sortie PAR-DESSUS LA CLOTURE sans payer, et
        # toute l'idee du lot tombe.
        if tremplin:
            self._tremplin_de_stationnement(x, y, debout, longueur, allees)

    def _tremplin_de_stationnement(self, x: int, y: int, debout: bool,
                                   longueur: int, allees: list[tuple[int, int]]) -> None:
        """Le tremplin se pose dans une ALLEE : c'est l'axe ou l'on roule deja,
        et le seul qui offre une piste droite — en travers des cases, on
        arriverait de biais et on ne decollerait pas.

        ⚠️ Dans La Pointe, il y en a un a tout coup : « les Skateux tiennent le
        stationnement » (voir DISTRICTS). C'est ce qui fait de leur coin autre
        chose qu'un decor, et ca donne au joueur une raison de traverser le
        pont.
        """
        if not allees:
            return
        if self.district_en(x, y) != "pointe" and not self.des_rampe.chance(PART_RAMPE_STATIONNEMENT):
            return
        # ⚠️ TOUTES les allees, celle du milieu d'abord. « A tout coup » ne
        # tenait que tant que l'allee centrale se trouvait convenir : le jour ou
        # le decoupage a bouge, La Pointe s'est retrouvee sans tremplin et les
        # Skateux sans terrain — une promesse ecrite trois lignes plus haut,
        # tenue par chance. On essaie les autres avant d'abandonner.
        milieu = len(allees) // 2
        ordre = sorted(range(len(allees)), key=lambda k: abs(k - milieu))
        essais = []
        for k in ordre:
            d, taille = allees[k]
            # ⚠️ Une allee fait DEUX tuiles de large, et les deux ne se valent
            # pas : dans La Pointe, celle du fond longe le grillage du voisin —
            # aucun elan — pendant que l'autre ouvre sur le gazon. On ne prenait
            # que le milieu, arrondi vers le fond, et les Skateux perdaient leur
            # tremplin des que le terrain glissait de cinq tuiles.
            for centre in sorted(range(d, d + taille), key=lambda v: abs(v - (d + taille // 2))):
                # ⚠️ L'elan n'a pas a tenir dans le terrain : il continue dans
                # la rue, et c'est tant mieux — on arrive lance au lieu de
                # partir d'arret.
                # ⚠️ Les trois quarts d'abord — c'est la que le tremplin est le
                # mieux —, PUIS les autres tuiles de l'allee. On ajoute des
                # recours APRES, jamais avant : un essai glisse en tete
                # deplacerait des tremplins qui tiennent tres bien.
                dabord = [max(1, longueur * part // 4) for part in (3, 2, 1)]
                for le_long in dabord + [m for m in range(longueur - 1, 0, -1) if m not in dabord]:
                    cx, cy = (x + le_long, y + centre) if debout else (x + centre, y + le_long)
                    for sens in (((1, 0), (-1, 0)) if debout else ((0, 1), (0, -1))):
                        essais.append((cx, cy, sens))
        self.proposer_rampe(essais)

    # --- Parc, place, port --------------------------------------------------

    def _parc(self, x: int, y: int, largeur: int, hauteur: int, kiosque: bool = False,
              sauvage: bool = False) -> None:
        """Un parc de ville, ou — `sauvage` — le bois de La Pointe : les memes
        allees, mais en terre battue, et des arbres au lieu des bancs."""
        # ⚠️ Le bois de La Pointe garde son SABLE (des sentiers de plage, on y
        # arrive par la greve) ; un parc de ville a de la poussiere de pierre.
        pave = "s" if sauvage else "g"
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, ",")
        centre = (x + largeur // 2, y + hauteur // 2)
        # Des allees en baionnette depuis les quatre bords vers le coeur.
        for bord in range(4):
            if bord == 0:
                depart = (x + self.des.entier(2, largeur - 3), y)
            elif bord == 1:
                depart = (x + self.des.entier(2, largeur - 3), y + hauteur - 1)
            elif bord == 2:
                depart = (x, y + self.des.entier(2, hauteur - 3))
            else:
                depart = (x + largeur - 1, y + self.des.entier(2, hauteur - 3))
            self._allee(depart, centre, pave)
        self.rect(centre[0] - 2, centre[1] - 2, 5, 5, pave)
        # Un etang, toujours a plus de trois tuiles du bord : il ne doit
        # enfermer aucun coin de pelouse.
        if largeur >= 16 and hauteur >= 12:
            el = self.des.entier(5, min(9, largeur // 3))
            eh = self.des.entier(3, min(6, hauteur // 3))
            ex = x + self.des.entier(3, largeur - el - 4)
            ey = y + self.des.entier(3, hauteur - eh - 4)
            for j in range(eh):
                for i in range(el):
                    bord = i == 0 or j == 0 or i == el - 1 or j == eh - 1
                    if self.sol[ey + j][ex + i] == pave:
                        continue
                    self.sol[ey + j][ex + i] = "s" if bord else "~"
        if kiosque:
            kx = x + largeur - self.des.entier(7, 9)
            ky = y + hauteur - 5
            facades = self.batiment_forme({(kx + i, ky + j) for j in range(3) for i in range(4)}, 0.6)
            self.poser_porte(facades, {"slug": "kiosque", "interieur": "kiosque",
                                       "nom": "Kiosque de Madame Thibodeau",
                                       "famille": "tes_places"})
        for _ in range(largeur * hauteur // (7 if sauvage else 14)):
            self.poser_decor("arbre", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        for _ in range(largeur * hauteur // (90 if sauvage else 40)):
            self.poser_decor("banc", x + self.des.entier(1, largeur - 2),
                             y + self.des.entier(1, hauteur - 2))
        for _ in range(largeur * hauteur // (18 if sauvage else 30)):
            self.poser_decor("buisson", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    def _allee(self, depart: tuple[int, int], arrivee: tuple[int, int], pave: str = ".") -> None:
        """Une allee de deux tuiles, avec un coude au hasard — jamais tout droit.

        ⚠️ Elle se RESERVE en se tracant, et ce n'est pas une precaution de
        confort : `_parc` seme ses arbres, ses bancs et ses buissons **sur tout
        le rectangle** du parc, au hasard, et `poser_decor` ne refuse que le
        solide, le routier, l'occupe et le reserve. Une allee est du pave (ou
        de la terre battue) : marchable, pas routiere — rien ne la protegeait.
        Un arbre y tombait donc, et un arbre est SOLIDE (rayon 5) : le sentier
        qu'on a dessine pour dire « passe par ici » se retrouvait a moitie
        bouche par ses propres arbres.

        La reserve regle les trois d'un coup — le banc et le buisson tombaient
        par le meme chemin, et le banc est solide lui aussi. Un banc A COTE de
        l'allee reste possible : on reserve l'allee, pas ses bords.
        """
        dx, dy = depart
        ax, ay = arrivee
        coude = dx + (ax - dx) * self.des.entier(2, 8) // 10
        for x in range(min(dx, coude), max(dx, coude) + 1):
            self.rect(x, dy, 1, 2, pave)
            self.reserver(x, dy, 1, 2)
        for y in range(min(dy, ay), max(dy, ay) + 1):
            self.rect(coude, y, 2, 1, pave)
            self.reserver(coude, y, 2, 1)
        for x in range(min(coude, ax), max(coude, ax) + 1):
            self.rect(x, ay, 1, 2, pave)
            self.reserver(x, ay, 1, 2)

    def reserver(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Ces tuiles-la resteront libres : rien ne s'y posera (voir
        `poser_decor`). C'est ce qui tient le devant des portes depuis M1 ; les
        sentiers s'en servent maintenant aussi."""
        for j in range(max(0, y), min(self.hauteur, y + hauteur)):
            for i in range(max(0, x), min(self.largeur, x + largeur)):
                self.reserve.add((i, j))
                self.devants_peints.discard((i, j))

    def _foire(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """**LA FOIRE DE LA POINTE** — voir `FOIRE` pour ce qui la fait.

        ⚠️ **COMPACTE, DANS UNE ENCEINTE** — Martin : « la foire doit etre plus
        compacte », « cloturee, pas un carre, des clotures asymetriques, et une
        entree avec une arche ». Elle ne remplit plus le bloc : elle tient dans
        une palissade EN ESCALIER posee au milieu, et le reste du bloc redevient
        le bois de La Pointe. Une foire qu'on voit de l'exterieur, derriere sa
        palissade, est une foire ou l'on a envie d'entrer.

        ⚠️ Tout se pose sur une GRILLE DE CASES, jamais au hasard : c'etait le
        defaut de la premiere version (sept objets tires uniformement sur 80 x 33
        tuiles). Le de de la foire ne decide que de l'ORDRE des kiosques et des
        marches de la palissade — jamais de la place d'une chose.
        """
        fiche = FOIRE
        des = self.des_foire
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, ",")

        # --- 0. L'enceinte, au milieu du bloc, plus petite que lui.
        el = min(largeur - 12, fiche["enceinte"][0])
        eh = min(hauteur - 2, fiche["enceinte"][1])
        # ⚠️ A L'OUEST DU BLOC, et pas au milieu. Le pont de La Pointe atterrit a
        # l'EST de ce bloc : centree, l'enceinte tombait pile dans l'axe de sa
        # sortie, et un char lance qui descendait du pont filait douze tuiles
        # sur le gazon et s'ecrasait dans la cloture — le juge du pont a vu sa
        # carrosserie tomber a 60 sur 100 apres l'ouverture du pont. On ne pose
        # pas un mur dans l'elan d'un pont.
        ex = x + fiche["marge_ouest"]
        ey = y + (hauteur - eh) // 2
        self.foire = {"x": ex, "y": ey, "l": el, "h": eh}
        allee = fiche["allee"]
        retrait = fiche["train"]["retrait"]
        # ⚠️ L'ALLEE SE PLACE DEPUIS LE SUD, plus au milieu. Au sud, tout a son
        # pas : les comptoirs (+2), la cour a manger (+4), les manèges (+6), la
        # voie du train (+8), puis la palissade. Ce qui reste au NORD est pour
        # les manèges du nord et la montagne russe derriere eux.
        a1 = ey + eh - 1 - retrait - 8                 # la derniere rangee de l'allee
        a0 = a1 - allee + 1                            # la premiere
        gx = ex + el // 3                              # l'arche, sur la palissade sud

        # ⚠️ LA PALISSADE EN ESCALIER : chaque cote rentre de 0 a 2 tuiles par
        # marches de quelques pas. C'est ce qui la rend ASYMETRIQUE — un
        # rectangle avec des coins mordus, jamais deux fois le meme — sans
        # jamais mordre sur l'allee ni sur un kiosque (les marches restent dans
        # la bande de 3 tuiles du pourtour).
        def marches(n: int, pas: int) -> list[int]:
            out, v = [], 0
            for i in range(n):
                if i % pas == 0:
                    v = des.suivant() % 3
                out.append(v)
            return out
        nord, sud = marches(el, 7), marches(el, 9)
        ouest, est = marches(eh, 5), marches(eh, 6)
        for i in range(max(0, gx - ex - 4), min(el, gx - ex + 5)):
            sud[i] = 0                                 # la palissade est droite a l'arche

        def dedans(tx: int, ty: int) -> bool:
            if not (ex <= tx < ex + el and ey <= ty < ey + eh):
                return False
            return (ty >= ey + nord[tx - ex] and ty <= ey + eh - 1 - sud[tx - ex]
                    and tx >= ex + ouest[ty - ey] and tx <= ex + el - 1 - est[ty - ey])

        # ⚠️ L'ANNEAU DE LA PALISSADE EST RESERVE AVANT TOUT LE RESTE. Premiere
        # version : la palissade se posait en dernier et SAUTAIT toute tuile
        # deja occupee par un decor — une table de la cour a manger posee sur le
        # bord laissait un TROU d'une tuile dans la cloture, et on entrait dans
        # la foire sans passer par l'arche. Un juge l'a trouve en cherchant ou
        # sauter ; personne ne l'aurait vu a l'oeil. On reserve donc le pourtour
        # d'abord (`poser_decor` refuse une tuile reservee), sauf l'ouverture.
        bas_arche = ey + eh - 1
        ouverture = {(gx - 1, bas_arche), (gx, bas_arche), (gx + 1, bas_arche)}
        # ⚠️ L'ANNEAU TIENT D'UN SEUL MORCEAU, ET FAIT UNE TUILE D'EPAIS — les deux
        # a la fois, et il a fallu deux essais pour l'apprendre :
        #   - en 8-voisinage, il epaississait certains coins en carres de 2 x 2
        #     (un juge du depot tient qu'une cloture fait UNE tuile d'epais) ;
        #   - en 4-voisinage, les marches ne se touchaient plus que par un COIN,
        #     et `elaguer_les_clotures` coupait chaque morceau droit comme « une
        #     barre qui ne clot rien » : il restait 78 tuiles sur 159, et des trous.
        # On prend donc le 4-voisinage, et a chaque marche on pose UN raccord en
        # L — celui qui ne ferme pas un carre de 2 x 2.
        anneau: set[tuple[int, int]] = set()
        for ty in range(ey, ey + eh):
            for tx in range(ex, ex + el):
                if not dedans(tx, ty) or (tx, ty) in ouverture:
                    continue
                if any(not dedans(tx + dx, ty + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    anneau.add((tx, ty))

        def carre(t: tuple[int, int], tuiles: set[tuple[int, int]]) -> bool:
            x0, y0 = t
            return any(all((x0 + ox + i, y0 + oy + j) in tuiles for i in (0, 1) for j in (0, 1))
                       for ox in (-1, 0) for oy in (-1, 0))
        for tx, ty in sorted(anneau):
            for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (tx + dx, ty + dy) not in anneau:
                    continue
                a, b = (tx + dx, ty), (tx, ty + dy)
                if a in anneau or b in anneau:
                    continue                          # deja raccordes
                choix = [t for t in (a, b) if dedans(*t) and t not in ouverture]
                choix.sort(key=lambda t: carre(t, anneau | {t}))
                if choix:
                    anneau.add(choix[0])
        # ⚠️ ET ON AMINCIT CE QUI RESTE EN CARRE. Une marche qui tombe pile sur
        # le bord sud (mesure : graine 1, une seule fois) fait encore un carre de
        # 2 x 2. On y retire une tuile — mais SEULEMENT si la cloture reste
        # etanche : un amincissement qui rouvre un passage est pire que le carre.
        def fuit(tuiles: set[tuple[int, int]]) -> bool:
            depart = next((t for t in ((tx, ty) for ty in range(ey, ey + eh)
                                       for tx in range(ex, ex + el))
                           if dedans(*t) and t not in tuiles and t not in ouverture), None)
            if depart is None:
                return False
            vus, pile = {depart}, [depart]
            while pile:
                cx, cy = pile.pop()
                for vx, vy in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    v = (vx, vy)
                    if v in vus or v in tuiles or v in ouverture:
                        continue
                    if not dedans(vx, vy):
                        return True
                    vus.add(v)
                    pile.append(v)
            return False
        for _passe in range(8):
            carres = [(cx, cy) for cx, cy in anneau
                      if all((cx + i, cy + j) in anneau for i in (0, 1) for j in (0, 1))]
            if not carres:
                break
            cx, cy = carres[0]
            for t in ((cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1)):
                if not fuit(anneau - {t}):
                    anneau.discard(t)
                    break
            else:
                break
        pourtour = sorted(anneau)
        for tx, ty in pourtour:
            self.reserver(tx, ty, 1, 1)

        # ⚠️ LA VOIE DU PETIT TRAIN, reservee juste apres la palissade et pour
        # la meme raison : rien ne doit s'y poser, ni kiosque ni table. Un
        # rectangle a `retrait` tuiles du bord, dans le sens des aiguilles d'une
        # montre (le train roule dans l'ordre de la liste). La palissade rentre
        # de deux tuiles au plus : la voie est donc TOUJOURS dedans.
        vx0, vy0 = ex + retrait, ey + retrait
        vx1, vy1 = ex + el - 1 - retrait, ey + eh - 1 - retrait
        voie = ([(tx, vy0) for tx in range(vx0, vx1)] + [(vx1, ty) for ty in range(vy0, vy1)]
                + [(tx, vy1) for tx in range(vx1, vx0, -1)] + [(vx0, ty) for ty in range(vy1, vy0, -1)])
        for tx, ty in voie:
            if not dedans(tx, ty):
                raise ValueError(f"la voie du train sort de l'enceinte en ({tx}, {ty})")
            self.reserver(tx, ty, 1, 1)

        # Le sol de la foire : de la terre battue a l'interieur de l'enceinte.
        for ty in range(ey, ey + eh):
            for tx in range(ex, ex + el):
                if dedans(tx, ty):
                    self.sol[ty][tx] = ","
        # L'allee centrale, d'un bout de la voie a l'autre. ⚠️ Elle partait de
        # `ex + 1` : la ou la palissade rentre, sa premiere tuile tombait DEHORS.
        self.rect(vx0 + 1, a0, vx1 - vx0 - 1, allee, "g")
        # L'allee d'entree, de l'arche jusqu'a l'allee centrale.
        self.rect(gx - 1, a1 + 1, 3, bas_arche - a1, "g")
        # Une traverse au milieu : on passe entre les rangs pour aller aux manèges.
        # ⚠️ Elle s'arrete a une tuile de la voie, des deux cotes : une allee qui
        # finit SUR les rails invite a y attendre, et le train attendrait.
        tv = ex + el // 2 + 2
        self.rect(tv, vy0 + 2, 2, vy1 - vy0 - 3, "g")
        interdits = {tv - 1, tv, tv + 1, tv + 2}
        # La voie, par-dessus les allees : elle COUPE l'allee d'entree, et c'est
        # la premiere chose qu'on voit en passant l'arche.
        for tx, ty in voie:
            self.sol[ty][tx] = "T"
        # ⚠️ LA GARE DU PETIT TRAIN, sur la ligne sud, ou il roule vers l'ouest :
        # la locomotive s'arrete a `gare_recul` tuiles de l'arche, ses quatre
        # wagons derriere elle, a l'est — et le dernier ne mord pas l'allee
        # d'entree. Le QUAI est une allee de pierre le long de la voie, au nord,
        # qui part de l'allee d'entree : on voit ou l'on attend le train.
        gare_x = gx - fiche["train"]["gare_recul"]
        if (gare_x, vy1) not in voie or gare_x - 2 < vx0:
            raise ValueError(f"la gare du petit train tombe hors de la ligne sud en ({gare_x}, {vy1})")
        quai = [gare_x + 1, gx - 2, vy1 - 1]
        for tx in range(quai[0], quai[1] + 1):
            if not dedans(tx, quai[2]) or self.sol[quai[2]][tx] != ",":
                raise ValueError(f"le quai du petit train tombe sur ({tx}, {quai[2]})")
            self.sol[quai[2]][tx] = "g"
        self.train_de_foire = {"voie": [[tx, ty] for tx, ty in voie], "gare": voie.index((gare_x, vy1)), "quai": quai}

        # --- 1. La grande roue, au bout de l'allee, cote nord.
        rx, ry = vx1 - 4, a0 - 1
        self.roue = {"x": rx, "y": ry}
        self.poser_decor("grande_roue", rx, ry)
        self.lampes.append({"x": rx, "y": ry - 3, "r": fiche["rayon_manege"] + 20, "c": "foire_jaune"})
        self.reserver(rx - 3, ry - 5, 7, 6)

        # --- 1 bis. LA MONTAGNE RUSSE, au nord, derriere les manèges : elle
        # prend les rangs entre la voie du train (+2) et le haut des manèges du
        # nord. Ses PIEDS se posent ici — un decor solide par tuile ; la voie
        # elle-meme est en l'air, et le navigateur la peint.
        # ⚠️ Pas de pied sur la traverse : on passe dessous, pas au travers.
        mr = FOIRE["montagne_russe"]
        mx0 = vx0 + 2
        mx0 = min(mx0, vx1 - 1 - mr["largeur"])
        self.montagne_russe = voie_de_montagne_russe(mx0, vy0 + 2, mr)
        pieds: set[tuple[int, int]] = set()
        gardes = []
        for i, tx, ty in self.montagne_russe["supports"]:
            if self.sol[ty][tx] != "," or not dedans(tx, ty):
                continue
            if (tx, ty) not in pieds and not self.poser_decor("pied_montagne_russe", tx, ty):
                continue
            pieds.add((tx, ty))
            gardes.append([i, tx, ty])
        self.montagne_russe["supports"] = gardes

        # --- 2. L'allee bordee des DEUX cotes, serree. Le de ne choisit que l'ordre.
        sortes = list(fiche["kiosques"]) + list(fiche["jeux"])
        melange: list[str] = []
        restant = sortes[:]
        while restant:
            melange.append(restant.pop(des.suivant() % len(restant)))
        n = 0
        jeux_poses: set[str] = set()
        for kx in range(vx0 + 2, vx1 - 3, fiche["pas_kiosque"]):
            if kx in interdits:
                continue
            for ky in (a0 - 1, a1 + 2):
                if ky == a1 + 2 and abs(kx - gx) <= 2:
                    continue                           # on ne bouche pas l'entree
                if ky == a0 - 1 and kx >= rx - 3:
                    continue                           # ni le pied de la roue
                quoi = melange[n % len(melange)]
                n += 1
                if quoi in fiche["jeux"] and quoi in jeux_poses:
                    quoi = fiche["kiosques"][n % len(fiche["kiosques"])]
                if not self.poser_decor(quoi, kx, ky):
                    continue
                self.kiosques.append({"slug": quoi, "x": kx, "y": ky, "nord": ky < a0})
                if quoi in fiche["jeux"]:
                    jeux_poses.add(quoi)
                    self.jeux.append({"slug": quoi, "x": kx, "y": ky})
                # ⚠️ Une guirlande tous les DEUX kiosques, au halo plus large : le
                # rendu tient un plafond de 50 lumieres (lampadaires + feux de
                # circulation + projecteur), et une lampe par comptoir les
                # depassait — les feux du carrefour d'a cote se seraient eteints.
                # ⚠️ EN DAMIER, pas une sur deux dans l'ordre de pose : on pose
                # nord puis sud a chaque colonne, et la parite de l'ordre allumait
                # TOUT le rang sud et AUCUN kiosque du nord — un juge l'a vu.
                case = (kx - ex) // fiche["pas_kiosque"] + (0 if ky < a0 else 1)
                if case % 2 == 0:
                    lampe = fiche["lampes"][(case // 2) % len(fiche["lampes"])]
                    self.lampes.append({"x": kx, "y": ky - 1, "r": fiche["rayon_lampe"], "c": lampe})

        # --- 3. Les manèges en double, JUSTE derriere les kiosques.
        # ⚠️ La rangee sud est a `a1 + 6` et non plus `+ 7` : depuis que l'anneau
        # de la palissade est reserve d'abord, `+ 7` tombait dessus et deux
        # manèges sur six ne se posaient plus. Et on laisse la place de la cour a
        # manger de part et d'autre de l'allee d'entree (`abs(mx - gx) <= 10`).
        m = 0
        for ligne, depart in ((a0 - 5, vx0 + 2), (a1 + 6, vx0 + 2)):
            for mx in range(depart, vx1 - 6, fiche["pas_manege"]):
                if m >= len(fiche["manèges"]):
                    break
                if any(abs(mx - t) <= 2 for t in interdits):
                    continue
                if ligne == a1 + 6 and abs(mx - gx) <= 10:
                    continue
                if ligne == a0 - 5 and mx >= rx - 4:
                    continue
                if not dedans(mx, ligne) or not self.poser_decor(fiche["manèges"][m], mx, ligne):
                    continue
                self.lampes.append({"x": mx, "y": ligne - 1, "r": fiche["rayon_manege"],
                                    "c": fiche["lampes"][m % len(fiche["lampes"])]})
                m += 1

        # --- 4. La cour a manger, de part et d'autre de l'allee d'entree : c'est
        # la premiere chose qu'on voit en passant l'arche.
        for i in range(fiche["tables"]):
            cote = 1 if i % 2 == 0 else -1
            tx = gx + cote * (3 + (i // 2) * 3)
            ty = a1 + 4
            if vx0 < tx < vx1 and dedans(tx, ty):
                self.poser_decor("table_pique_nique", tx, ty)

        # --- 5. LA CLOTURE, sur l'anneau reserve au depart. ⚠️ Du GRILLAGE et
        # non de la palissade : la palissade de bois est l'image de la banlieue
        # des Erables (un juge le tient), et une foire se clot de panneaux de
        # grillage temporaires — c'est ce qu'on voit autour d'une vraie. Posee
        # DIRECTEMENT : `poser_cloture` refuse certaines tuiles sans rien dire
        # (le defaut des terrains de banlieue, « le U de `_jardin` se posait
        # pendant que `poser_cloture` en refusait en silence ») — ici, un refus
        # silencieux est une entree gratuite.
        for tx, ty in pourtour:
            self.sol[ty][tx] = "f"
        self.foire_entree = (gx - 1, bas_arche, 3, 1)
        # L'arche, a cheval sur l'ouverture ; elle ne bloque rien.
        self.poser_decor("portique_foire", gx, bas_arche)
        self.lampes.append({"x": gx, "y": bas_arche - 2, "r": fiche["rayon_lampe"] + 10, "c": "foire_rose"})
        # La montagne russe, la nuit : la gare et le looping. ⚠️ EN DERNIER dans
        # la liste : le rendu n'allume que les 25 premieres lampes a l'ecran, et
        # ce sont les kiosques qu'il ne faut jamais eteindre.
        mr_voie = self.montagne_russe["voie"]
        for tranche, couleur, monte in (("gare", "foire_rose", 1), ("boucle", "foire_bleue", 3)):
            i = sum(self.montagne_russe[tranche]) // 2
            self.lampes.append({"x": int(mr_voie[i][0] // TUILE_PX), "y": int(mr_voie[i][1] // TUILE_PX) - monte,
                                "r": fiche["rayon_manege"] + 14, "c": couleur})
        # L'interieur, en bandes par rangee, pour le navigateur.
        for ty in range(ey, ey + eh):
            debut = None
            for tx in range(ex, ex + el + 1):
                libre = tx < ex + el and dedans(tx, ty) and self.sol[ty][tx] != "f"
                if libre and debut is None:
                    debut = tx
                elif not libre and debut is not None:
                    self.foire_enclos.append([ty, debut, tx - 1])
                    debut = None

        # --- 6. Un liseré de bois AUTOUR de la cloture, et pas sur tout le bloc :
        # la foire est dans un parc, mais la pelouse de l'est reste degagee — un
        # arbre plante dans l'elan du pont serait le meme piege que la cloture.
        for i in range(fiche["arbres"]):
            u = des.suivant()
            tx = ex - 3 + u % (el + 6)
            ty = ey - 3 + (u >> 8) % (eh + 6)
            if ex - 1 <= tx <= ex + el and ey - 1 <= ty <= ey + eh:
                continue
            if not (x < tx < x + largeur - 1 and y < ty < y + hauteur - 1):
                continue
            self.poser_decor("arbre", tx, ty)

    def _place(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Une place publique : du pave, une fontaine, des bancs. Pas une rue."""
        self.bouchon_rect(x, y, largeur, hauteur, ".")
        self.rect(x, y, largeur, hauteur, ".")
        self.rect(x + 1, y + 1, largeur - 2, hauteur - 2, ".")
        fx, fy = x + largeur // 2, y + hauteur // 2
        self.poser_decor("fontaine", fx, fy)
        for coin in ((x + 1, y + 1), (x + largeur - 2, y + 1),
                     (x + 1, y + hauteur - 2), (x + largeur - 2, y + hauteur - 2)):
            self.poser_decor("arbre", *coin)
        for _ in range(max(2, largeur // 4)):
            self.poser_decor("banc", x + self.des.entier(1, largeur - 2),
                             y + self.des.entier(1, hauteur - 2))
        if self.poser_decor("lampadaire", fx - 2, fy - 2):
            self.lampes.append({"x": fx - 2, "y": fy - 2})

    def _quai(self, x: int, y: int, largeur: int, hauteur: int,
              sur_eau: bool = False) -> None:
        """Le port. `sur_eau` : la region a AVALE la baie sous elle.

        ⚠️ **UN QUAI TOUCHE L'EAU, OU CE N'EST PAS UN QUAI.** Retour de Martin,
        capture a l'appui : « c'est le quai ?! je ne savais meme pas que c'etait
        un quai — il y a une route entre le quai et l'eau ». Mesure du
        16 sept. 2026 : **16 des 1 818 tuiles de quai touchaient l'eau (0,9 %)**,
        et la coupe du port du nord au sud donnait un boulevard, dix tuiles de
        planches, **un deuxieme boulevard a quatre voies**, une plage de sable,
        puis la baie. Un debardeur traversait une autoroute et une plage pour
        rejoindre son cargo.

        ⚠️ **Et la cause n'etait pas dans cette methode, elle etait dans le
        PLAN** : la rangee de quai et la rangee d'eau etaient deux blocs, et la
        trame met une rue entre deux blocs. Le chiffre dormait pourtant depuis
        la 1re vague du bord de l'eau (« le glyphe `Q` n'est pas un ponton,
        c'est le pavage du district des Quais ») — on avait corrige le semis des
        poteaux d'amarrage au lieu de la geographie. C'est la rangee d'eau qui
        se fait avaler (`^`), et `j` dit que la region la porte.

        La coupe, maintenant : le boulevard de service, le TABLIER, la levre,
        la baie. Rien entre les deux.
        """
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "Q")
        if sur_eau and hauteur >= QUAI_TABLIER + QUAI_TIRANT_MIN:
            self.rect(x, y + QUAI_TABLIER, largeur, hauteur - QUAI_TABLIER, "~")
            self._appontements(x, y + QUAI_TABLIER, largeur, hauteur - QUAI_TABLIER)
        self._meubler_le_quai(x, y, largeur, hauteur)
        # Une rampe de debarquement, la ou un quai en porte vraiment une.
        # ⚠️ L'eau n'est pas roulable : `poser_rampe` ne choisira jamais l'axe
        # qui envoie au fond de la baie, le saut longe le port.
        if largeur >= 10 and hauteur >= 3 and self.des_rampe.chance(PART_RAMPE_VAGUE):
            self.proposer_rampe([(x + largeur // 2, y + QUAI_TABLIER // 2, None)])

    def _appontements(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Des jetees qui avancent dans la baie, depuis la levre du tablier.

        ⚠️ Elles PARTENT du quai : une jetee qui ne le touche pas est une ile,
        et `boucher_les_poches` la murerait — ou pire, la laisserait la, hors
        d'atteinte. Elles sont aussi ce qui donne au port sa dentelure : une
        levre parfaitement droite sur soixante tuiles se lit comme un mur, pas
        comme un port.
        """
        poses: list[int] = []
        for _ in range(max(1, largeur // APPONTEMENT["ecart"])):
            large = self.des_port.entier(*APPONTEMENT["largeur"])
            longue = min(self.des_port.entier(*APPONTEMENT["longueur"]), hauteur - 2)
            px = x + self.des_port.entier(1, max(1, largeur - large - 2))
            if longue < 2 or any(abs(px - q) < APPONTEMENT["ecart"] for q in poses):
                continue
            poses.append(px)
            self.rect(px, y, large, longue, "Q")

    #: Ce qui attend d'etre charge sur un quai. ⚠️ Une liste A POIDS, comme les
    #: dechets d'un terrain vague : ce qu'on voit d'abord sur un quai, c'est des
    #: caisses — le baril est ce qu'on remarque parce qu'il est rare.
    CARGAISON = ("caisse", "caisse", "caisse", "baril", "ordures")

    def _meubler_le_quai(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Ce qui fait qu'un quai a l'air d'un quai : ce qu'on y amarre et ce
        qu'on y empile.

        ⚠️ **La LEVRE et l'ARRIERE ne portent pas la meme chose**, et c'est tout
        ce qui distingue un port d'un plancher : au bord, ce qui sert au bateau
        (la borne ou l'on attache, le pneu qui amortit la coque) ; en arriere,
        ce qui attend d'etre charge. Semees au hasard sur toute la surface, les
        bornes se retrouvaient au milieu du quai — une borne d'amarrage a six
        tuiles de l'eau ne veut rien dire.
        """
        levre, fond, apron = [], [], set()
        for cy in range(y, min(y + hauteur, self.hauteur)):
            for cx in range(x, min(x + largeur, self.largeur)):
                if self.sol[cy][cx] != "Q":
                    continue
                if any(self.eau_en(cx + dx, cy + dy)
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    levre.append((cx, cy))
        # ⚠️ L'apron se mesure DEPUIS LA LEVRE, pas depuis le bord de la boite :
        # un appontement avance dans la baie, et son apron avance avec lui.
        for cx, cy in levre:
            for j in range(-QUAI_APRON, QUAI_APRON + 1):
                for i in range(-QUAI_APRON, QUAI_APRON + 1):
                    if abs(i) + abs(j) <= QUAI_APRON:
                        apron.add((cx + i, cy + j))
        for cy in range(y, min(y + hauteur, self.hauteur)):
            for cx in range(x, min(x + largeur, self.largeur)):
                if self.sol[cy][cx] != "Q" or (cx, cy) in apron:
                    continue
                if cy - y < QUAI_FOND:                 # la bande du cote de la rue
                    fond.append((cx, cy))
        poses: list[tuple[int, int]] = []

        def assez_loin(cx: int, cy: int, combien: int) -> bool:
            return all(abs(px - cx) + abs(py - cy) >= combien for px, py in poses)

        for cx, cy in levre:
            if assez_loin(cx, cy, ECART_BORNE_AMARRAGE):
                quoi = "poteau_amarrage"
            elif assez_loin(cx, cy, GREVE["ecart"]) and self.des_port.chance(CHANCE_DEFENSE):
                quoi = "pneu"
            else:
                continue
            if self.poser_decor(quoi, cx, cy):
                poses.append((cx, cy))
        for _ in range(len(fond) // PART_CARGAISON):
            if not fond:
                break
            cx, cy = fond[self.des_port.suivant() % len(fond)]
            self.poser_decor(self.des_port.choix(self.CARGAISON), cx, cy)
        # ⚠️ **ET ON DEGAGE.** Le semis ne sait pas ce qu'il referme ; cette
        # ligne-la est la garantie, et pas un reglage de plus.
        self.degager_le_decor(x, y, largeur, hauteur)

    def eau_en(self, x: int, y: int) -> bool:
        """De l'eau, ou hors carte — le large compte comme de l'eau. Sans ca,
        la levre d'un quai colle au bord du monde n'en serait pas une."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return True
        return self.sol[y][x] == "~"

    def _terre_a_cote(self, tuiles: list[tuple[int, int]]) -> bool:
        """Y a-t-il de la terre le long de ce bord ? Hors carte : non.

        ⚠️ Une plage au fond d'une baie, de l'autre bord de l'eau, personne ne
        la verra jamais — et `boucher_les_poches` la noierait de toute facon.
        On ne dessine une rive que la ou il y a un rivage.
        """
        for x, y in tuiles:
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                return False
            if self.sol[y][x] != "~":
                return True
        return False

    def _eau(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        """Un bassin, et ses plages — peu, mais larges (voir `PLAGES`)."""
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "~")
        # ⚠️ ON BRULE CE QUE L'ANCIENNE RIVE TIRAIT DANS LE DE COMMUN : un tirage
        # par colonne et par rangee du bassin. La forme des plages se tire dans
        # `des_plage` ; sans cette brulure, tous les ilots poses apres la baie
        # changeaient de gabarits pour une histoire de sable.
        self.des.brule(largeur + hauteur)
        pas = max(1, largeur // 8)
        nord = self._terre_a_cote([(x + i, y - 1) for i in range(0, largeur, pas)])
        sud = self._terre_a_cote([(x + i, y + hauteur) for i in range(0, largeur, pas)])
        pas = max(1, hauteur // 8)
        ouest = self._terre_a_cote([(x - 1, y + j) for j in range(0, hauteur, pas)])
        est = self._terre_a_cote([(x + largeur, y + j) for j in range(0, hauteur, pas)])
        for cote, rivage, en_face in (("nord", nord, sud), ("sud", sud, nord),
                                      ("ouest", ouest, est), ("est", est, ouest)):
            if rivage:
                self._plage(x, y, largeur, hauteur, cote, en_face)

    def _plage(self, x: int, y: int, largeur: int, hauteur: int, cote: str,
               en_face: bool) -> None:
        """Une plage le long d'un cote du bassin — ou rien, s'il n'a pas la place.

        ⚠️ **Une plage suit la cote ; elle ne suit pas une boite.** Le rivage se
        verifie TUILE PAR TUILE (`_terre_a_cote`) : premiere version de la rive,
        une seule tuile de terre quelque part le long du cote faisait courir le
        sable sur toute sa longueur, et douze bancs de sable flottaient en pleine
        baie. On prend donc le plus long bout de cote d'un seul tenant.
        """
        fiche = PLAGES
        le_long = largeur if cote in ("nord", "sud") else hauteur
        en_travers = hauteur if cote in ("nord", "sud") else largeur

        def tuile(i: int, j: int) -> tuple[int, int]:
            """La tuile `i` le long du cote, `j` tuiles vers le large."""
            if cote == "nord":
                return x + i, y + j
            if cote == "sud":
                return x + i, y + hauteur - 1 - j
            if cote == "ouest":
                return x + j, y + i
            return x + largeur - 1 - j, y + i

        def terre(i: int) -> bool:
            tx, ty = tuile(i, 0)
            dx, dy = {"nord": (0, -1), "sud": (0, 1), "ouest": (-1, 0), "est": (1, 0)}[cote]
            return self._terre_a_cote([(tx + dx, ty + dy)])

        # ⚠️ Du large devant : un tiers du bassin s'il y a une rive en face (le
        # sable des deux bords ne se touche jamais), la moitie sinon.
        fond = en_travers // (3 if en_face else 2)
        mini, maxi = fiche["profondeur"]
        if fond < mini:
            return
        rivage, debut = (0, 0), None
        for i in range(le_long + 1):
            if i < le_long and terre(i):
                debut = i if debut is None else debut
            elif debut is not None:
                if i - debut > rivage[1]:
                    rivage = (debut, i - debut)
                debut = None
        depart, place = rivage
        court, long = fiche["longueur"]
        if place < court:
            return
        longueur = min(place, self.des_plage.entier(court, long))
        depart += self.des_plage.entier(0, place - longueur)
        profondeur = min(fond, self.des_plage.entier(mini, maxi))
        rampe = fiche["rampe"]
        bruit = 0
        profil: list[int] = []
        for k in range(longueur):
            # Les deux bouts s'amincissent ; le milieu avance et recule d'une
            # tuile — c'est le bruit qui fait une ligne d'eau, pas une regle.
            bout = min(k + 1, longueur - k)
            base = profondeur if bout >= rampe else max(1, profondeur * bout // rampe)
            bruit = max(-1, min(1, bruit + self.des_plage.entier(-1, 1)))
            profil.append(max(1, min(fond, base + bruit)))
        # ⚠️ Pas la place : pas de plage. On ne pose pas un mouchoir de sable.
        if sum(profil) < fiche["place"]:
            return
        tuiles: list[tuple[int, int]] = []
        for k, creux in enumerate(profil):
            for j in range(creux):
                tx, ty = tuile(depart + k, j)
                self.sol[ty][tx] = "s"
                tuiles.append((tx, ty))
        xs = [t[0] for t in tuiles]
        ys = [t[1] for t in tuiles]
        self.plages.append({"x": min(xs), "y": min(ys), "l": max(xs) - min(xs) + 1,
                            "h": max(ys) - min(ys) + 1, "cote": cote})

    # --- Decor de rue et finitions -----------------------------------------

    #: Ou chercher le trottoir autour d'un coin de croisement : le coin
    #: d'abord, puis ses voisines, les plus proches en premier.
    AUTOUR = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))

    #: A quelle distance du coin un lampadaire se plante, en tuiles.
    #: ⚠️ ZERO, AVANT : il se plantait SUR le coin — exactement la ou va le mat
    #: du feu. Tant qu'il n'y avait que deux mats par croisement et qu'aucune
    #: lanterne n'etait peinte, ca ne se voyait pas ; depuis qu'un tricolore ne
    #: montre qu'une rue, il y a QUATRE mats, un par coin, et le lampadaire
    #: leur disputait la place. Le coin d'un croisement est la place du FEU :
    #: c'est lui qu'on doit voir en arrivant. Le lampadaire s'ecarte le long du
    #: trottoir — ou il eclaire d'ailleurs mieux, entre deux croisements
    #: plutot que dessus.
    ECART_LAMPADAIRE = 3

    def _coins_reserves_aux_feux(self) -> set[tuple[int, int]]:
        """Les tuiles que les mats des feux se gardent : les quatre coins de
        chaque croisement a feux, et l'anneau d'une tuile autour — `coinLibre`,
        cote navigateur, peut ecarter un mat d'une tuile quand le coin est pris.
        """
        pris: set[tuple[int, int]] = set()
        for inter in self.intersections:
            if len(inter["bras"]) < 4:
                continue
            coins = ((inter["x"] + inter["l"], inter["y"] - 1),
                     (inter["x"] - 1, inter["y"] + inter["h"]),
                     (inter["x"] - 1, inter["y"] - 1),
                     (inter["x"] + inter["l"], inter["y"] + inter["h"]))
            for cx, cy in coins:
                for ix in (-1, 0, 1):
                    for iy in (-1, 0, 1):
                        pris.add((cx + ix, cy + iy))
        return pris

    def lampadaires(self) -> None:
        """Deux coins opposes par croisement, mais A L'ECART du coin : de la
        lumiere le long de la rue, et le coin laisse au feu.

        ⚠️ Un poteau se plante sur un TROTTOIR, jamais sur un parterre. Le coin
        d'un croisement n'en est pas toujours un : devant une maison, la bande
        de devant est en gazon, et devant la fourriere, en asphalte. On cherche
        alors le trottoir a cote. Sans ca, le juge ne tenait que par chance —
        il suffisait qu'un arbre libere le coin pour qu'une lampe pousse dans
        une pelouse.

        ⚠️ On s'eloigne LE LONG DE LA RUE, pas n'importe ou : d'abord dans le
        sens nord-sud, puis est-ouest. Un lampadaire qui recule en diagonale
        finit au milieu d'un parterre, loin des deux trottoirs qu'il devait
        eclairer.
        """
        reserves = self._coins_reserves_aux_feux()
        for inter in self.intersections:
            for dx, dy in ((-1, -1), (inter["l"], inter["h"])):
                x, y = inter["x"] + dx, inter["y"] + dy
                ecart = self.ECART_LAMPADAIRE
                loin_x = x + (-ecart if dx < 0 else ecart)
                loin_y = y + (-ecart if dy < 0 else ecart)
                if self._poser_un_lampadaire(((x, loin_y), (loin_x, y)), reserves):
                    continue

    def _poser_un_lampadaire(self, departs, reserves) -> bool:
        """Essaie chaque depart, et autour de lui, jusqu'a une place tenable."""
        for bx, by in departs:
            for ix, iy in self.AUTOUR:
                cx, cy = bx + ix, by + iy
                if not (0 <= cx < self.largeur and 0 <= cy < self.hauteur):
                    continue
                if (cx, cy) in reserves:
                    continue
                # ⚠️ SUR L'ABORD, jamais sur la seule tuile de trottoir : un poteau
                # plante sur une dalle d'une tuile de large la bouche entierement,
                # et le coin de rue devient un cul-de-sac pour la foule.
                if self.sol[cy][cx] != "_" or not self.poser_decor("lampadaire", cx, cy):
                    continue
                self.lampes.append({"x": cx, "y": cy})
                return True
        return False

    def ambulants(self) -> list[dict]:
        """Les commerces sans porte : kiosques sur le trottoir, camions au
        stationnement. On les espace : trois kiosques a hot-dogs au meme coin,
        c'est une file d'attente, pas une ville."""
        poses: list[dict] = []
        ecart = 22
        for commerce in magasins.AMBULANTS:
            candidats = self._places_ambulantes(commerce["sur"], commerce.get("districts"))
            if not candidats:
                continue
            for _ in range(commerce["nombre"]):
                choisi = None
                for _essai in range(60):
                    x, y = candidats[self.des.suivant() % len(candidats)]
                    if any(abs(p["x"] - x) + abs(p["y"] - y) < ecart for p in poses):
                        continue
                    if (x, y) in self.occupe or (x, y) in self.reserve:
                        continue
                    choisi = (x, y)
                    break
                if not choisi:
                    continue
                self.occupe.add(choisi)
                poses.append({"slug": commerce["slug"], "x": choisi[0], "y": choisi[1]})
        return poses

    def _places_ambulantes(self, sur: str,
                           districts: tuple[str, ...] | None = None) -> list[tuple[int, int]]:
        """Une place est bonne si on peut s'y arreter ET etre servi devant.

        `districts` enferme le commerce chez lui : la cabane a fruits de mer
        ne se pose qu'aux Quais et a La Pointe — c'est le port qu'on mange.
        """
        places = []
        for y in range(1, self.hauteur - 2):
            for x in range(1, self.largeur - 1):
                if districts and self.district_en(x, y) not in districts:
                    continue
                glyphe = self.sol[y][x]
                if sur == "trottoir":
                    # ⚠️ SUR L'ABORD, contre le mur, et SERVI DEPUIS LA DALLE : la
                    # tuile au sud est le trottoir, et c'est la que le client se
                    # tient. Un kiosque pose sur la seule tuile de trottoir la
                    # bouchait — la fiche du trottoir a une tuile le disait
                    # (« les kiosques et roulottes cherchent du '.' »).
                    if glyphe != "_" or self.sol[y + 1][x] != ".":
                        continue
                elif sur == "stationnement":
                    if glyphe != "p" or self.sol[y][x + 1] != "p":
                        continue
                    if not marchable(self.sol[y + 1][x]):
                        continue
                    # ⚠️ PAS DANS L'ENTREE d'un lot : une entree large de deux
                    # tuiles ressemble a une place de camion, et un camion gare
                    # dedans referme le seul chemin par ou l'on entre.
                    if (x, y) in self.entrees or (x + 1, y) in self.entrees:
                        continue
                elif sur == "quai":
                    # Sur les planches, avec deux tuiles de quai devant pour s'y
                    # tenir et y garer un char — pas au bord de l'eau : on ne
                    # vend pas les pieds dans la baie.
                    if glyphe != "Q" or self.sol[y + 1][x] != "Q" or self.sol[y + 2][x] != "Q":
                        continue
                else:  # pragma: no cover - garde-fou de relecture du catalogue
                    raise ValueError(f"support inconnu : {sur!r}")
                places.append((x, y))
        return places

    def guichets(self) -> int:
        """Les guichets automatiques : SOUS UNE VITRINE, sur l'abord, servis
        depuis la dalle (`economie.GUICHET`). Rend combien on en a pose.

        ⚠️ Sous une vitrine, pas n'importe ou contre un mur : un guichet est
        encastre dans la devanture d'un commerce, c'est ce qui le fait lire
        comme un guichet et pas comme une boite grise. Et sur l'abord, comme
        les kiosques : la dalle reste la dalle. Ils s'espacent (`ecart`) —
        deux guichets au meme coin, c'est un mur de banque, pas une ville.
        Ils tirent dans LEUR de : un guichet de plus ne deplace rien d'autre.
        """
        fiche = economie.GUICHET
        vitrines = {(d["x"] + i, d["y"])
                    for d in self.devantures for i, m in enumerate(d["motifs"]) if m == "W"}
        candidats = sorted(
            (x, y + 1) for x, y in vitrines
            if y + 2 < self.hauteur and self.sol[y + 1][x] == "_" and self.sol[y + 2][x] == "."
            and (x, y + 1) not in self.occupe and (x, y + 1) not in self.reserve
        )
        poses: list[tuple[int, int]] = []
        for _essai in range(400):
            if not candidats or len(poses) >= fiche["par_ville"][1]:
                break
            x, y = candidats[self.des_guichet.suivant() % len(candidats)]
            if any(abs(px - x) + abs(py - y) < fiche["ecart"] for px, py in poses):
                continue
            if self.poser_decor("guichet", x, y):
                poses.append((x, y))
        return len(poses)

    #: Ou se pose une machine, et ce qui doit rester devant elle : l'abord ou
    #: la dalle du parvis. ⚠️ DEUX rangees, pas une : la machine prend celle du
    #: mur et la suivante reste a la foule. Mesure du 16 sept. 2026 — sous les
    #: 313 facades de commerce, 265 donnent sur un parvis de dalle et 35
    #: seulement sur l'abord ; la regle du guichet (l'abord, puis la dalle) ne
    #: laissait que cinq machines dans toute la ville.
    DEVANT_UNE_MACHINE = frozenset("_.")

    def distributrices(self) -> int:
        """Les machines distributrices : CONTRE UNE DEVANTURE, sur l'abord, servies
        depuis la dalle (`economie.DISTRIBUTRICE`). Rend combien on en a pose.

        ⚠️ Le patron du guichet, a trois nuances pres. (1) Sous la facade d'un
        commerce, vitrine ou mur plein — jamais sous une porte NI A COTE : une
        machine plantee devant l'entree la bouche, et une machine collee a
        l'entree lui VOLE ACTION (on se tient devant la porte, a moins de 22 px
        de la machine, et l'invite disait MACHINE A CAFE au lieu d'ENTRER — un
        juge des interieurs l'a vu le jour meme). (2) Sa SORTE vient de la devanture
        (`magasins.sortes_devant`) : du cafe devant la soudure, de la liqueur
        devant la taverne. (3) Pas collee a un guichet : a portee de la meme
        main, ACTION ne saurait pas lequel on vise.

        ⚠️ APRES les paquets, les scenes et la reclame, et dans son propre de :
        elle prend des places que personne d'autre ne cherche plus, donc en
        poser une de plus ne deplace rien d'autre dans la ville.
        """
        fiche = economie.DISTRIBUTRICE
        guichets = [(d["x"], d["y"]) for d in self.decor if d["type"] == "guichet"]
        familles: dict[tuple[int, int], str] = {}
        for devanture in self.devantures:
            famille = devantures_mod.GENRES[devanture["genre"]]["slug"]
            for i, motif in enumerate(devanture["motifs"]):
                # ⚠️ Pas sous un « P » : une porte peinte est une porte.
                if motif == "W":
                    familles[(devanture["x"] + i, devanture["y"] + 1)] = famille
        candidats = sorted(
            (x, y) for x, y in familles
            if y + 1 < self.hauteur and self.sol[y][x] in self.DEVANT_UNE_MACHINE
            and self.sol[y + 1][x] in self.DEVANT_UNE_MACHINE
            and (x, y) not in self.occupe and (x, y) not in self.reserve
            and all(abs(gx - x) + abs(gy - y) >= fiche["ecart_guichet"] for gx, gy in guichets)
            and not any(self.est_une_porte(x + dx, y - 1) for dx in (-1, 1))
        )
        poses: list[tuple[int, int]] = []
        #: ⚠️ UN PLAFOND PAR DISTRICT. Sans lui, les machines suivaient les
        #: devantures : La Shop et les Quais en prenaient trente-cinq sur
        #: quarante-huit, et les Erables une seule — « partout dans la ville »
        #: voulait dire deux quartiers.
        par_district: dict[str, int] = {}
        for _essai in range(800):
            if not candidats or len(poses) >= fiche["par_ville"][1]:
                break
            x, y = candidats[self.des_distributrice.suivant() % len(candidats)]
            if any(abs(px - x) + abs(py - y) < fiche["ecart"] for px, py in poses):
                continue
            district = self.district_en(x, y)
            if par_district.get(district, 0) >= fiche["par_district"]:
                continue
            sortes = magasins.sortes_devant(familles[(x, y)]) or tuple(magasins.DISTRIBUTRICES)
            sorte = sortes[self.des_distributrice.suivant() % len(sortes)]
            if self.poser_decor(magasins.DISTRIBUTRICES[sorte]["decor"], x, y):
                poses.append((x, y))
                par_district[district] = par_district.get(district, 0) + 1
        return len(poses)

    def entraves(self) -> list[dict]:
        """Les voies qu'on peut fermer un jour sans couper la ville.

        Une candidate : `longueur` tuiles d'affilee sur la MEME fleche, dont
        chacune a une voisine PARALLELE qui va dans le meme sens — c'est elle
        qui restera ouverte, et c'est pour ca que le champ de direction ne
        bouge pas. Hors croisement, hors ligne d'arret, et espacees.
        """
        fiche = ENTRAVES
        voie, arrets = self.voie, {tuple(int(n) for n in c.split(",")) for c in self.arrets}
        boites = [(i["x"], i["y"], i["l"], i["h"]) for i in self.intersections]
        pas = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}

        def libre(x: int, y: int, fleche: str) -> bool:
            if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                return False
            if voie[y][x] != fleche or (x, y) in arrets:
                return False
            if any(bx <= x < bx + bl and by <= y < by + bh for bx, by, bl, bh in boites):
                return False
            # Une voisine parallele qui va dans le meme sens : la voie d'a cote.
            dx, dy = pas[fleche]
            return any(0 <= x + nx < self.largeur and 0 <= y + ny < self.hauteur
                       and voie[y + ny][x + nx] == fleche
                       for nx, ny in ((-dy, dx), (dy, -dx)))

        mini, maxi = fiche["longueur"]
        candidats: list[dict] = []
        for y in range(self.hauteur):
            for x in range(self.largeur):
                fleche = voie[y][x]
                if fleche not in pas:
                    continue
                dx, dy = pas[fleche]
                n = 0
                while n < maxi and libre(x + dx * n, y + dy * n, fleche):
                    n += 1
                if n < mini:
                    continue
                candidats.append({"x": min(x, x + dx * (n - 1)), "y": min(y, y + dy * (n - 1)),
                                  "l": abs(dx) * (n - 1) + 1, "h": abs(dy) * (n - 1) + 1,
                                  "sens": fleche})
        poses: list[dict] = []
        for _essai in range(6000):
            if not candidats or len(poses) >= fiche["par_ville"][1]:
                break
            c = candidats[self.des_entrave.suivant() % len(candidats)]
            if any(abs(p["x"] - c["x"]) + abs(p["y"] - c["y"]) < fiche["ecart"] for p in poses):
                continue
            poses.append(c)
        return sorted(poses, key=lambda c: (c["y"], c["x"]))

    def fermetures(self, ponts: list[dict]) -> list[dict]:
        """Les rues qu'on peut barrer en entier sans couper la ville.

        Chacune part d'un croisement et court sur `longueur` tuiles ; on retire
        ses fleches et on redemande au juge de M1 (`voies_bloquees`) si les rues
        sont encore fortement connexes. ⚠️ Jamais un pont : c'est le seul lien
        carrossable vers La Pointe, et le juge le dirait — autant ne pas le
        proposer.
        """
        fiche = FERMETURES
        tabliers = [(p["x"], p["y"], p["l"], p["h"]) for p in ponts]
        boites = [(i["x"], i["y"], i["l"], i["h"]) for i in self.intersections]

        def dans_une_boite(x: int, y: int) -> bool:
            return any(bx <= x < bx + bl and by <= y < by + bh for bx, by, bl, bh in boites)
        vers = {"N": (0, -1), "S": (0, 1), "O": (-1, 0), "E": (1, 0)}
        carte = {"voie": self.voie, "arrets": self.arrets}

        def sur_un_pont(x: int, y: int) -> bool:
            return any(px <= x < px + pl and py <= y < py + ph for px, py, pl, ph in tabliers)

        candidats: list[dict] = []
        for inter in self.intersections:
            for bras, (dx, dy) in vers.items():
                if bras not in inter["bras"]:
                    continue
                # Le bord de la boite, du bon cote, puis on s'eloigne.
                x0 = inter["x"] + (inter["l"] if dx > 0 else -1 if dx < 0 else 0)
                y0 = inter["y"] + (inter["h"] if dy > 0 else -1 if dy < 0 else 0)
                large = inter["l"] if dx == 0 else inter["h"]
                # ⚠️ ON VA JUSQU'AU BOUT : le troncon court jusqu'au croisement
                # suivant (ou jusqu'a ce que la rue s'arrete). S'arreter avant,
                # c'est laisser un cul-de-sac derriere soi.
                tuiles: list[tuple[int, int]] = []
                #: ⚠️ **A-T-ON VRAIMENT ATTEINT LE CROISEMENT SUIVANT ?** La
                #: boucle avait trois facons de finir et n'en distinguait
                #: qu'une : le croisement (bien), un pont ou un bord de carte
                #: (rejete), et `long_max` EPUISE — ce dernier gardait un
                #: troncon qui s'arrete au milieu de la rue. Le commentaire
                #: ci-dessous disait pourtant deja la regle : « on va jusqu'au
                #: bout, s'arreter avant c'est laisser un cul-de-sac derriere
                #: soi ». Un tel troncon n'a pas de rue transversale a son
                #: extremite, donc pas de detour a montrer — et le juge « chaque
                #: bout parle » est tombe dessus le 16 sept. 2026, des que la
                #: carte a change et que le de est retombe ailleurs.
                jusqu_au_croisement = False
                for n in range(fiche["long_max"]):
                    bande = [(x0 + dx * n + (k if dx == 0 else 0), y0 + dy * n + (k if dy == 0 else 0))
                             for k in range(large)]
                    if any(dans_une_boite(x, y) for x, y in bande):
                        jusqu_au_croisement = True
                        break                      # le croisement suivant : le troncon est complet
                    if not all(0 <= x < self.largeur and 0 <= y < self.hauteur
                               and self.voie[y][x] != "." and not sur_un_pont(x, y)
                               for x, y in bande):
                        tuiles = []                # un pont, un bord de carte : on laisse
                        break
                    tuiles.extend(bande)
                if not jusqu_au_croisement or len(tuiles) < large * 3:
                    continue
                candidats.append({"x": min(t[0] for t in tuiles), "y": min(t[1] for t in tuiles),
                                  "l": max(t[0] for t in tuiles) - min(t[0] for t in tuiles) + 1,
                                  "h": max(t[1] for t in tuiles) - min(t[1] for t in tuiles) + 1,
                                  "tuiles": list(tuiles)})
        gardees: list[dict] = []
        essais = 0
        while candidats and essais < fiche["candidates"] and len(gardees) < fiche["par_ville"][1]:
            c = candidats[self.des_fermeture.suivant() % len(candidats)]
            if any(abs(g["x"] - c["x"]) + abs(g["y"] - c["y"]) < fiche["ecart"] for g in gardees):
                candidats.remove(c)
                continue
            essais += 1
            # ⚠️ LE JUGE DE M1, ici, une fois : on retire les fleches et on
            # redemande si les rues sont encore fortement connexes.
            voie = [list(ligne) for ligne in self.voie]
            for x, y in c["tuiles"]:
                voie[y][x] = "."
            carte["voie"] = ["".join(ligne) for ligne in voie]
            sans_aller, sans_retour = voies_bloquees(carte)
            if not sans_aller and not sans_retour:
                gardees.append({k: v for k, v in c.items() if k != "tuiles"})
            candidats.remove(c)
        return sorted(gardees, key=lambda c: (c["y"], c["x"]))

    def chaussee_a_nids(self) -> list[tuple[int, int]]:
        """Ou un nid-de-poule peut se creuser : de la chaussee, hors croisement
        et hors ligne d'arret."""
        boites = [(i["x"], i["y"], i["l"], i["h"]) for i in self.intersections]
        # ⚠️ `self.arrets` est indexe par "x,y" : le lire comme un ensemble de
        # couples ne trouvait jamais rien, et on creusait des nids sur les lignes d'arret.
        arrets = {tuple(int(n) for n in cle.split(",")) for cle in self.arrets}
        return [
            (x, y)
            for y in range(1, self.hauteur - 1)
            for x in range(1, self.largeur - 1)
            if LEGENDE[self.sol[y][x]].get("route") and not LEGENDE[self.sol[y][x]].get("trottoir")
            and (x, y) not in arrets
            and not any(bx <= x < bx + bl and by <= y < by + bh for bx, by, bl, bh in boites)
        ]

    def nids_de_poule(self) -> list[dict]:
        """Les tuiles defoncees : de la chaussee, hors croisement, espacees."""
        fiche = NIDS_DE_POULE
        candidats = self.chaussee_a_nids()
        poses: list[tuple[int, int]] = []
        for _essai in range(4000):
            if not candidats or len(poses) >= fiche["par_ville"][1]:
                break
            x, y = candidats[self.des_nid.suivant() % len(candidats)]
            if any(abs(px - x) + abs(py - y) < fiche["ecart"] for px, py in poses):
                continue
            poses.append((x, y))
        return [{"x": x, "y": y} for x, y in sorted(poses)]

    def _eau_a_portee(self, x: int, y: int, portee: int) -> bool:
        """De l'eau a `portee` tuiles d'ici ? ⚠️ En CROIX et pas en carre : une
        grève se mesure vers le large, et un coin de diagonale ferait passer
        pour riverain un carre de sable qui touche l'eau par la pointe."""
        for d in range(1, portee + 1):
            for cx, cy in ((x + d, y), (x - d, y), (x, y + d), (x, y - d)):
                if 0 <= cx < self.largeur and 0 <= cy < self.hauteur and self.sol[cy][cx] == "~":
                    return True
        return False

    def greve(self, ponts: list[dict] | None = None) -> int:
        """Meuble le bord de l'eau : parasols, serviettes, tables, chateaux de
        sable, et ce qui s'amarre au quai. Rend le nombre de meubles poses.

        ⚠️ **Tuile par tuile, et jamais sur une boite.** Une plage suit la cote.
        On ne regarde donc que le SOL sous ses pieds (du sable, du quai) et la
        distance a l'eau — jamais le rectangle d'un bassin.
        """
        fiche = GREVE
        # ⚠️ **LE QUAI S'EST DEJA MEUBLE** : on amorce la regle d'ecart avec ce
        # qui est deja au bord (voir `MEUBLES_DU_BORD`).
        poses: list[tuple[int, int]] = [(d["x"], d["y"]) for d in self.decor
                                        if d["type"] in MEUBLES_DU_BORD]
        # ⚠️ **JAMAIS AU PIED D'UN PONT**, et `FERMETURES` le disait deja pour les
        # rues barrees. Mesure : une serviette et deux bouees s'etaient posees a
        # une tuile du tablier de La Pointe, et un char lance qui traversait les
        # accrochait — le juge du pont a vu la carrosserie tomber a 90 sur 100
        # *apres* l'ouverture du pont, et a conclu que le pont coutait encore.
        # Un quai n'est pas une plage, et le pied d'un pont non plus.
        garde = fiche["pont_ecart"]
        tabliers = [(p["x"] - garde, p["y"] - garde, p["l"] + 2 * garde, p["h"] + 2 * garde)
                    for p in (ponts or [])]

        def sous_un_pont(x: int, y: int) -> bool:
            return any(px <= x < px + pl and py <= y < py + ph for px, py, pl, ph in tabliers)

        def assez_loin(x: int, y: int, ecart: int) -> bool:
            return all(abs(px - x) + abs(py - y) >= ecart for px, py in poses)

        # ⚠️ **SEULEMENT SUR UNE PLAGE QUI A LA PLACE** (`PLAGES`). Le sable qui
        # borde un etang de parc n'en est pas une : trois parasols autour d'une
        # flaque, c'etait exactement « les petits morceaux de plage ».
        sable = {(tx, ty) for p in self.plages
                 for ty in range(p["y"], p["y"] + p["h"])
                 for tx in range(p["x"], p["x"] + p["l"])
                 if self.sol[ty][tx] == "s"}
        for p in self.plages:
            cx, cy = p["x"] + p["l"] // 2, p["y"] + p["h"] // 2
            milieu = sorted((t for t in sable
                             if p["x"] <= t[0] < p["x"] + p["l"] and p["y"] <= t[1] < p["y"] + p["h"]),
                            key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), t))
            for tx, ty in milieu:
                if sous_un_pont(tx, ty) or not assez_loin(tx, ty, fiche["ecart"]):
                    continue
                if self.poser_decor(fiche["sauveteur"], tx, ty):
                    poses.append((tx, ty))
                    break

        for y in range(self.hauteur):
            for x in range(self.largeur):
                glyphe = self.sol[y][x]
                proprietes = LEGENDE[glyphe]
                # Ni l'eau, ni un mur, ni la chaussee : le reste est de la rive.
                if glyphe == "~" or proprietes.get("solide") or proprietes.get("route"):
                    continue
                if sous_un_pont(x, y):
                    continue
                if glyphe == "s":
                    if (x, y) not in sable or not self._eau_a_portee(x, y, fiche["bord"]):
                        continue
                    au_bord = self._eau_a_portee(x, y, fiche["chateau_bord"])
                    for quoi, chance in fiche["chances"].items():
                        if quoi == "chateau_sable" and not au_bord:
                            continue
                        if self.des_greve.chance(chance) and assez_loin(x, y, fiche["ecart"]):
                            if self.poser_decor(quoi, x, y):
                                poses.append((x, y))
                            break
                else:
                    # ⚠️ ON AMARRE SUR LA RIVE BATIE, et il a fallu la mesurer
                    # pour le savoir : le glyphe `Q` n'est pas un ponton, c'est
                    # le PAVAGE du district des Quais — **16 de ses 1 818 tuiles
                    # touchent l'eau**. Un poteau seme « sur le quai » se serait
                    # donc plante six tuiles a l'interieur des terres, ou nulle
                    # part. Ce qui amarre un bateau n'est pas un glyphe, c'est
                    # une rive : une tuile ou l'on marche, qui n'est ni du sable
                    # ni de la route, avec l'eau juste devant — 222 tuiles, dont
                    # 199 de TROTTOIR. ⚠️ Et le trottoir ne porte pas `terre` dans
                    # la legende : tester la propriete au lieu de la marchabilite
                    # laissait dehors 199 des 222, et il ne s'amarrait rien nulle
                    # part.
                    if not self._eau_a_portee(x, y, 1):
                        continue
                    # Le poteau tient sur les planches ; la bouee flotte a cote.
                    # ⚠️ **SAUF SUR LE QUAI, QUI AMARRE CHEZ LUI** (`_meubler_le_quai`).
                    # Depuis qu'il touche l'eau il a six cents tuiles de levre, et
                    # les DEUX semis y posaient des bornes — le quai a onze tuiles
                    # d'ecart, la greve a trois : une borne ou un pneu tous les
                    # trois pas. Une borne ARRETE un pieton ; ce n'etait plus un
                    # quai, c'etait une palissade. Le tirage reste, pour que le de
                    # de la greve ne se decale pas ; seule la pose saute. La greve
                    # garde le reste de la rive, et ses bouees au pied du quai.
                    amarre = self.des_greve.chance(fiche["quai_poteau"])
                    if amarre and self.sol[y][x] != "Q" and assez_loin(x, y, fiche["poteau_ecart"]):
                        if self.poser_decor("poteau_amarrage", x, y):
                            poses.append((x, y))
                            continue
                    if not self.des_greve.chance(fiche["quai_bouee"]):
                        continue
                    for cx, cy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if not (0 <= cx < self.largeur and 0 <= cy < self.hauteur):
                            continue
                        if self.sol[cy][cx] != "~" or not assez_loin(cx, cy, fiche["bouee_ecart"]):
                            continue
                        if sous_un_pont(cx, cy):
                            continue
                        # ⚠️ `sur_eau` : `poser_decor` refuse le solide, et l'eau
                        # en est (`solide: 2`). La bouee est le seul decor du jeu
                        # qui ait raison de flotter — on le lui dit une fois,
                        # explicitement, plutot que d'ouvrir l'eau a tous.
                        if self.poser_decor("bouee", cx, cy, sur_eau=True):
                            poses.append((cx, cy))
                        break
        poses += self._belvederes(poses, sous_un_pont)
        return len(poses)

    def _belvederes(self, deja: list[tuple[int, int]], sous_un_pont) -> list[tuple[int, int]]:
        """Un plancher de bois sur pilotis, la ou la terre DOMINE l'eau.

        ⚠️ Ce n'est pas « pres de l'eau » : c'est une tuile de terre ferme — ni
        sable, ni quai, ni route — qui a l'eau juste devant. Un belvedere pose
        sur la grève regarde le sable ; celui qu'on veut regarde le large.
        """
        fiche = GREVE
        mini, maxi = fiche["belvederes"]
        candidats: list[tuple[int, int]] = []
        for y in range(1, self.hauteur - 1):
            for x in range(1, self.largeur - 1):
                proprietes = LEGENDE[self.sol[y][x]]
                if not proprietes.get("terre") or self.sol[y][x] == "s":
                    continue
                if not self._eau_a_portee(x, y, 2) or sous_un_pont(x, y):
                    continue
                candidats.append((x, y))
        poses: list[tuple[int, int]] = []
        for _essai in range(2000):
            if not candidats or len(poses) >= maxi:
                break
            x, y = candidats[self.des_greve.suivant() % len(candidats)]
            if any(abs(px - x) + abs(py - y) < fiche["belvedere_ecart"] for px, py in poses):
                continue
            # ⚠️ ET IL SE TIENT A L'ECART DE TOUT LE RESTE, pas seulement de ses
            # semblables : un belvedere colle a un parasol, c'est une terrasse
            # posee sur une serviette. Le juge de l'ecart l'a attrape.
            if any(abs(px - x) + abs(py - y) < fiche["ecart"] for px, py in deja):
                continue
            if self.poser_decor("belvedere", x, y):
                poses.append((x, y))
        return poses

    def la_baie(self) -> set[tuple[int, int]]:
        """Les tuiles d'eau reliees au LARGE : le plus grand plan d'eau de la
        ville. Ce qui n'en fait pas partie est un etang, une mare de parc ou un
        bassin ferme — de l'eau ou l'on nage, pas ou l'on navigue."""
        vus: set[tuple[int, int]] = set()
        plus_grand: set[tuple[int, int]] = set()
        for y in range(self.hauteur):
            for x in range(self.largeur):
                if self.sol[y][x] != "~" or (x, y) in vus:
                    continue
                corps, pile = {(x, y)}, [(x, y)]
                vus.add((x, y))
                while pile:
                    cx, cy = pile.pop()
                    for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if (0 <= n[0] < self.largeur and 0 <= n[1] < self.hauteur
                                and n not in vus and self.sol[n[1]][n[0]] == "~"):
                            vus.add(n)
                            corps.add(n)
                            pile.append(n)
                if len(corps) > len(plus_grand):
                    plus_grand = corps
        return plus_grand

    def amarrages(self) -> list[dict]:
        """Les tuiles d'eau ou une chaloupe peut attendre : contre la rive
        BATIE, espacees, et jamais au pied d'un pont (un char lance qui traverse
        n'a pas a trouver une coque en travers).

        ⚠️ **DANS LA BAIE, ET D'ABORD LE LONG DES QUAIS.** Mesure du
        16 sept. 2026 : **8 des 18 chaloupes ne mouillaient pas dans la baie** —
        trois dans l'etang du Faubourg, trois dans le chenal de La Pointe, et
        deux dans des MARES DE PARC de deux et six tuiles, d'ou une coque ne
        sort jamais. La cause etait l'ORDRE : le semis parcourait la carte du
        nord au sud et s'arretait a dix-huit, il remplissait donc les mares du
        nord avant d'atteindre le port — le seul endroit construit pour les
        bateaux, et depuis que le quai touche l'eau, six cents tuiles de levre.
        L'eau doit rejoindre le large (`la_baie`), et les rives de quai passent
        avant les autres rives baties.
        """
        fiche = AMARRAGES
        garde = GREVE["pont_ecart"]
        tabliers = [(p["x"] - garde, p["y"] - garde, p["l"] + 2 * garde, p["h"] + 2 * garde)
                    for p in self._ponts_poses]
        baie = self.la_baie()
        au_quai: list[tuple[int, int]] = []
        ailleurs: list[tuple[int, int]] = []
        for y in range(1, self.hauteur - 1):
            for x in range(1, self.largeur - 1):
                if (x, y) not in baie or (x, y) in self.occupe:
                    continue
                if any(px <= x < px + pl and py <= y < py + ph for px, py, pl, ph in tabliers):
                    continue
                # Une rive batie juste a cote : ni sable, ni route, ni mur.
                rive = quai = False
                for cx, cy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    glyphe = self.sol[cy][cx]
                    proprietes = LEGENDE[glyphe]
                    if glyphe in ("~", "s") or proprietes.get("solide") or proprietes.get("route"):
                        continue
                    rive = True
                    quai = quai or glyphe == "Q"
                if rive:
                    (au_quai if quai else ailleurs).append((x, y))
        poses: list[tuple[int, int]] = []
        for x, y in au_quai + ailleurs:
            if any(abs(px - x) + abs(py - y) < fiche["ecart"] for px, py in poses):
                continue
            poses.append((x, y))
            if len(poses) >= fiche["par_ville"][1]:
                break
        return [{"x": x, "y": y} for x, y in sorted(poses)]

    def aqueducs(self) -> list[dict]:
        """Les tuiles ou une conduite peut lacher.

        De la chaussee DIRIGEE (une fleche), hors croisement, hors ligne
        d'arret, espacees — et jamais sans voie de rechange : la tuile doit
        avoir une voisine PARALLELE qui va dans le meme sens. C'est ce qui rend
        le bris inoffensif pour la connexite, et c'est le meme argument que les
        entraves du jour, a ceci pres qu'ici le trou ne fait qu'UNE tuile.
        """
        fiche = AQUEDUCS
        voie = self.voie
        arrets = {tuple(int(n) for n in cle.split(",")) for cle in self.arrets}
        boites = [(i["x"], i["y"], i["l"], i["h"]) for i in self.intersections]
        pas = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}
        candidats: list[tuple[int, int]] = []
        for y in range(1, self.hauteur - 1):
            for x in range(1, self.largeur - 1):
                fleche = voie[y][x]
                if fleche not in pas or (x, y) in arrets:
                    continue
                if any(bx <= x < bx + bl and by <= y < by + bh for bx, by, bl, bh in boites):
                    continue
                dx, dy = pas[fleche]
                # La voie d'a cote, dans le meme sens : celle qui restera ouverte.
                if any(voie[y + ny][x + nx] == fleche for nx, ny in ((-dy, dx), (dy, -dx))):
                    candidats.append((x, y))
        poses: list[tuple[int, int]] = []
        for _essai in range(4000):
            if not candidats or len(poses) >= fiche["par_ville"][1]:
                break
            x, y = candidats[self.des_aqueduc.suivant() % len(candidats)]
            if any(abs(px - x) + abs(py - y) < fiche["ecart"] for px, py in poses):
                continue
            poses.append((x, y))
        return [{"x": x, "y": y} for x, y in sorted(poses)]

    def barrieres(self, ambulants: list[dict], ponts: list[dict]) -> list[dict]:
        """Chaque barriere de `BARRIERES`, resolue en rectangle de tuiles."""
        sortie = []
        for fiche in BARRIERES:
            ou = fiche["ou"]
            if "pont" in ou:
                sens, i, j = ou["pont"]
                pont = next(p for p in ponts if p["sens"] == sens and (p["x"], p["y"]) == (
                    (self.xr[i], self.yb[j]) if sens == "v" else (self.xb[i], self.yr[j])))
                rect = (pont["x"], pont["y"], pont["l"], pont["h"])
            elif "grille" in ou:
                g = self.fourriere["grille"]
                rect = (g["x"], g["y"], g["largeur"], 1)
            elif "lieu" in ou:
                bx, by, bl, bh = self.lots[ou["lieu"]]
                m = ou.get("marge", 1)
                rect = (bx - m, by - m, bl + 2 * m, bh + 2 * m)
            elif "foire" in ou:
                if not self.foire_entree:
                    continue
                rect = self.foire_entree
            elif "quai" in ou:
                a = next(a for a in ambulants if a["slug"] == ou["quai"])
                g, rx, ry, rl, rh = next((g, rx, ry, rl, rh) for g, rx, ry, rl, rh in self.regions()
                                         if g in QUAIS and rx <= a["x"] < rx + rl
                                         and ry <= a["y"] < ry + rh)
                # ⚠️ Le tablier seulement : un quai sur l'eau porte la baie sous
                # lui, et une chaine tendue dans la baie ne ferme rien.
                tablier = QUAI_TABLIER if g == "j" else rh
                profondeur = min(MOUILLAGE["profondeur"], tablier - QUAI_APRON - 1)
                x0 = max(rx, a["x"] - MOUILLAGE["demi_largeur"])
                x1 = min(rx + rl, a["x"] + MOUILLAGE["demi_largeur"] + 1)
                rect = (x0, ry, x1 - x0, profondeur)
            else:  # pragma: no cover - garde-fou de relecture de la fiche
                raise ValueError(f"barriere sans lieu : {fiche['slug']}")
            x, y, largeur, hauteur = rect
            sortie.append({"slug": fiche["slug"], "nom": fiche["nom"], "x": x, "y": y, "l": largeur, "h": hauteur,
                           "arrete": list(fiche["arrete"]), "condition": dict(fiche["condition"]),
                           "forcer": dict(fiche["forcer"]) if fiche["forcer"] else None,
                           "raison": fiche["raison"], "decor": fiche.get("decor"),
                           "existant": bool(fiche.get("existant")),
                           "prix": fiche.get("prix"), "dedans": fiche.get("dedans")})
        return sortie

    def reclames(self, ambulants: list[dict]) -> list[dict]:
        """Le poste de chaque homme-sandwich : un bout de trottoir a quelques
        tuiles du kiosque pour lequel il crie (`magasins.RECLAME`).

        ⚠️ Pas DEVANT le kiosque : un solliciteur qui te coupe la route a la
        porte du commerce, ce n'est plus de la reclame, c'est un bouchon. Et
        pas trop loin non plus : le coupon qu'il donne expire, il faut que le
        kiosque soit a portee de marche. On tire dans les places de trottoir
        (les memes que les kiosques), dans le meme district, entre `mini` et
        `maxi` tuiles ; un kiosque sans place ne recrute personne.
        """
        mini, maxi = magasins.RECLAME["poste_tuiles"]
        trottoirs = self._places_ambulantes("trottoir")
        postes: list[dict] = []
        for pose in ambulants:
            commerce = magasins.ambulant(pose["slug"])
            if not commerce or not commerce.get("reclame"):
                continue
            district = self.district_en(pose["x"], pose["y"])
            candidats = [
                (x, y) for x, y in trottoirs
                if mini <= abs(x - pose["x"]) + abs(y - pose["y"]) <= maxi
                and self.district_en(x, y) == district
                and (x, y) not in self.occupe and (x, y) not in self.reserve
            ]
            if not candidats:
                continue
            x, y = candidats[self.des_reclame.suivant() % len(candidats)]
            postes.append({"commerce": pose["slug"], "x": x, "y": y,
                           "kiosque": {"x": pose["x"], "y": pose["y"]}})
        return postes

    #: OU UN AMUSEUR S'INSTALLE, par ordre de preference. ⚠️ Un amuseur ne
    #: choisit pas un coin de rue au hasard : il se met LA OU LE MONDE PASSE ET
    #: S'ARRETE. Jusqu'ici, `naitreLesSortes` le posait sur la premiere tuile
    #: marchable venue hors de l'ecran — c'est-a-dire souvent dans une ruelle,
    #: devant un mur de hangar, entre deux poubelles. Le numero etait bon,
    #: l'endroit ne l'etait pas, et personne ne venait le voir.
    #:
    #: `genre` de l'ilot -> ce que ca vaut. La PLACE d'abord (c'est fait pour
    #: ca : du pave, une fontaine, des bancs), le parc ensuite, puis le
    #: terminus d'autobus — ou tout le monde debarque — et enfin le trottoir
    #: devant les commerces.
    SCENES_PAR_ILOT: dict[str, int] = {"o": 4, "p": 3, "T": 3, "c": 1}

    #: De combien de tuiles LIBRES un numero a besoin autour de lui. ⚠️ Trois a
    #: cinq spectateurs font un cercle d'une tuile et demie de rayon ; une scene
    #: sans cette place est une scene ou l'attroupement se met dans le mur, et
    #: `placeDansLeCercle` renonce tuile apres tuile.
    SCENE_DEGAGEMENT = 2

    #: A quelle distance minimale deux scenes se posent, en tuiles. ⚠️ Sans
    #: ecart, un parc de vingt tuiles en donnerait deux cents collees, et deux
    #: amuseurs poses dessus joueraient coude a coude — deux numeros a trois
    #: tuiles l'un de l'autre ne font pas deux spectacles, ils font une cohue,
    #: et leurs deux cercles se disputent les memes passants.
    SCENES_ECART = 7
    #: Combien de scenes au plus par ilot : une place en merite plusieurs, une
    #: bande de trottoir une seule. ⚠️ C'est aussi ce qui tient le paquet : la
    #: liste brute en faisait NEUF CENTS, soit cinquante kilo-octets pour dire
    #: cinquante fois le meme coin de parc.
    SCENES_PAR_REGION = 3

    def scenes(self) -> list[dict]:
        """Les endroits ou un amuseur de rue peut planter son numero.

        ⚠️ Une scene n'est pas une tuile marchable de plus : c'est une tuile
        DEGAGEE sur deux tuiles a la ronde, dans un ilot ou les gens passent, et
        A L'ECART des autres scenes. Sans le degagement, le cercle de badauds
        n'a nulle part ou se mettre — et « toujours entre 3 et 5 personnes
        autour » devient un voeu.
        """
        sortie: list[dict] = []
        for glyphe, x0, y0, largeur, hauteur in self.regions():
            valeur = self.SCENES_PAR_ILOT.get(glyphe)
            if not valeur:
                continue
            district = self.district_en(x0, y0)
            candidats = [(x, y)
                         for y in range(y0, y0 + hauteur)
                         for x in range(x0, x0 + largeur)
                         if self._scene_possible(x, y)]
            if not candidats:
                continue
            # ⚠️ Tirees, pas prises dans l'ordre : les premieres d'une liste
            # balayee du nord-ouest au sud-est sont toutes dans le meme coin.
            posees: list[tuple[int, int]] = []
            for _ in range(self.SCENES_PAR_REGION):
                libres = [c for c in candidats
                          if all(abs(c[0] - p[0]) + abs(c[1] - p[1]) >= self.SCENES_ECART
                                 for p in posees)]
                if not libres:
                    break
                posees.append(libres[self.des_scene.suivant() % len(libres)])
            for x, y in posees:
                sortie.append({"x": x, "y": y, "district": district,
                               "ilot": glyphe, "valeur": valeur})
        return sortie

    def _scene_possible(self, x: int, y: int) -> bool:
        """Degage sur `SCENE_DEGAGEMENT` tuiles, et jamais sur la chaussee."""
        if (x, y) in self.occupe or (x, y) in self.reserve:
            return False
        marge = self.SCENE_DEGAGEMENT
        for j in range(y - marge, y + marge + 1):
            for i in range(x - marge, x + marge + 1):
                if not self.marchable_en(i, j):
                    return False
                # ⚠️ Un amuseur au milieu de la rue se fait faucher, et son
                # public avec. `routier` couvre la chaussee ET les traverses :
                # une scene au bord d'un passage clouté bloquerait le seul
                # endroit ou l'on traverse.
                if routier(self.sol[j][i]):
                    return False
        return True

    def paquets(self, nombre: int = 20) -> list[dict]:
        """Vingt paquets caches dans les recoins : ruelles, terrains vagues,
        coins de parc, quais. Jamais sur une rue, jamais devant une porte,
        et espaces — les trouver doit faire visiter la ville."""
        recoins = [(x, y) for y in range(1, self.hauteur - 1) for x in range(1, self.largeur - 1)
                   if self.sol[y][x] in "x,Qs" and (x, y) not in self.reserve and (x, y) not in self.occupe]
        poses: list[dict] = []
        for _essai in range(4000):
            if len(poses) >= nombre or not recoins:
                break
            x, y = recoins[self.des.suivant() % len(recoins)]
            if any(abs(p["x"] - x) + abs(p["y"] - y) < 18 for p in poses):
                continue
            self.occupe.add((x, y))
            poses.append({"numero": len(poses), "x": x, "y": y})
        return poses

    def feux_pietons(self) -> list[dict]:
        """Un feu a CHAQUE BOUT de chaque traverse, et seulement aux croisements
        qui ont des feux (quatre bras).

        ⚠️ Un par bout, jamais un par tuile : une traverse fait deux tuiles de
        large, et huit poteaux par croisement disent deja tout ce qu'il y a a
        dire. Le piueton qui attend au nord ne voit pas celui du sud — il en
        faut donc deux, et deux suffisent.

        ⚠️ Et le SENS voyage avec le poteau : « = » barre une rue est-ouest (on
        la traverse du nord au sud), « : » barre une rue nord-sud. Sans lui, le
        navigateur devrait redeviner a quel feu chaque poteau obeit, et il se
        tromperait une fois sur deux — c'est exactement le genre de chose qui
        se lit une fois, ici, et plus jamais.
        """
        aFeux = [i for i in self.intersections if len(i["bras"]) >= 4]
        boites = set()
        for inter in aFeux:
            for y in range(inter["y"] - 3, inter["y"] + inter["h"] + 3):
                for x in range(inter["x"] - 3, inter["x"] + inter["l"] + 3):
                    boites.add((x, y))
        vus: set[tuple[int, int]] = set()
        feux: list[dict] = []
        for (x, y) in sorted(boites):
            if (x, y) in vus or not (0 <= x < self.largeur and 0 <= y < self.hauteur):
                continue
            glyphe = self.sol[y][x]
            if glyphe not in ("=", ":"):
                continue
            # Le bloc de traverse, d'un seul tenant.
            bloc, pile = {(x, y)}, [(x, y)]
            while pile:
                cx, cy = pile.pop()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) in bloc or not (0 <= nx < self.largeur and 0 <= ny < self.hauteur):
                        continue
                    if self.sol[ny][nx] != glyphe:
                        continue
                    bloc.add((nx, ny))
                    pile.append((nx, ny))
            vus |= bloc
            xs = sorted({p[0] for p in bloc})
            ys = sorted({p[1] for p in bloc})
            if glyphe == "=":            # on la traverse du nord au sud
                bouts = [(xs[len(xs) // 2], ys[0] - 1), (xs[len(xs) // 2], ys[-1] + 1)]
            else:                        # on la traverse d'ouest en est
                bouts = [(xs[0] - 1, ys[len(ys) // 2]), (xs[-1] + 1, ys[len(ys) // 2])]
            for bx, by in bouts:
                if not (0 <= bx < self.largeur and 0 <= by < self.hauteur):
                    continue
                # ⚠️ Sur le TROTTOIR, jamais sur la chaussee : un poteau plante
                # dans la rue se fait faucher a la premiere auto, et il cache la
                # ligne d'arret.
                if self.sol[by][bx] != "." or (bx, by) in self.reserve:
                    continue
                # ⚠️ Et jamais dans un lampadaire ni sur une borne : `occupe`
                # est le registre de ce qui tient deja la place, et deux objets
                # sur la meme tuile, c'est un seul objet qu'on voit mal.
                if (bx, by) in self.occupe:
                    continue
                self.occupe.add((bx, by))
                feux.append({"x": bx, "y": by, "sens": glyphe})
        return feux

    def bornes(self) -> None:
        """Une borne-fontaine sur trois coins de rue environ.

        ⚠️ C'ETAIT UNE TUILE, ce sont maintenant des DECORS. Une tuile ne se
        casse pas : elle ne pouvait ni tomber sous un char, ni cracher son eau.
        En decor, elle a une fiche (`DECORS.borne_fontaine`), donc une masse,
        une resistance et un bris — et le jet avec.

        ⚠️ Et elle ne prend plus le coin du croisement : c'est la place du mat
        du feu, comme pour le lampadaire. Elle se pose une tuile plus loin, le
        long du trottoir.
        """
        reserves = self._coins_reserves_aux_feux()
        for inter in self.intersections:
            if not self.des.chance(0.30):
                continue
            x, y = inter["x"] + inter["l"], inter["y"] - 1
            for dy in (-1, -2, 1):
                cx, cy = x, y + dy
                if (cx, cy) in reserves:
                    continue
                if 0 <= cx < self.largeur and 0 <= cy < self.hauteur and self.sol[cy][cx] == ".":
                    if self.poser_decor("borne_fontaine", cx, cy):
                        break

    def boucher_les_poches(self, depart: tuple[int, int]) -> int:
        """Bouche toute poche marchable qu'on ne peut pas rejoindre a pied.

        ⚠️ C'est le FILET du generateur. Un gabarit qui referme une cour, deux
        batiments qui se rejoignent sur une ruelle : au lieu d'un juge rouge et
        d'un ilot injouable, la poche redevient du bati (ou de l'eau dans un
        parc). Si elle en bouche beaucoup, c'est un gabarit qu'il faut revoir,
        et `generer()` le dit tout haut.
        """
        # ⚠️ On cherche par `franchissable_en`, pas `marchable_en` : une cour
        # derriere un grillage se rejoint en l'enjambant, elle n'est donc PAS une
        # poche. Avec `marchable_en`, la cour de la fourriere, celle du gang et
        # tous les terrains vagues se faisaient murer d'un coup.
        vus = {depart}
        pile = [depart]
        while pile:
            cx, cy = pile.pop()
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if (nx, ny) in vus or not self.franchissable_en(nx, ny):
                    continue
                vus.add((nx, ny))
                pile.append((nx, ny))
        bouchees = 0
        for y in range(self.hauteur):
            for x in range(self.largeur):
                if marchable(self.sol[y][x]) and (x, y) not in vus:
                    self.sol[y][x] = self.bouchon[y][x]
                    bouchees += 1
        if bouchees:
            self.decor = [d for d in self.decor
                          if marchable(self.sol[d["y"]][d["x"]])]
            # ⚠️ Une rampe prise dans une poche bouchee n'existe plus : la
            # laisser dans la liste, c'est promettre au defi du Grand Saut un
            # tremplin qui n'est plus la.
            self.rampes = [r for r in self.rampes if self.sol[r["y"]][r["x"]] == "R"]
        return bouchees

    def rect_district(self, district: dict) -> tuple[int, int, int, int]:
        """Le rectangle de tuiles d'un district — chaque rue frontiere coupee
        en deux, pour qu'un char sur le boulevard appartienne a un quartier et
        a un seul."""
        bx, by = district["bx"], district["by"]
        bx1, by1 = bx + len(district["plan"][0]), by + len(district["plan"])
        x0 = 0 if bx == 0 else self.xr[bx] + RUES_V[bx] // 2
        y0 = 0 if by == 0 else self.yr[by] + RUES_H[by] // 2
        x1 = self.largeur if bx1 == self.nc else self.xr[bx1] + RUES_V[bx1] // 2
        y1 = self.hauteur if by1 == self.nr else self.yr[by1] + RUES_H[by1] // 2
        return x0, y0, x1 - x0, y1 - y0

    def zones(self) -> list[dict]:
        """Les districts d'abord, leurs cours de gang ensuite : `Monde.zoneA`
        garde la DERNIERE qui contient le point, donc la plus precise."""
        sortie = []
        for district in DISTRICTS:
            x, y, largeur, hauteur = self.rect_district(district)
            sortie.append({"slug": district["slug"], "nom": district["nom"],
                           "district": district["slug"], "x": x, "y": y, "l": largeur, "h": hauteur,
                           "gang": None, "brume": bool(district.get("brume")),
                           "pietons": district["pietons"], "vehicules": district["vehicules"],
                           "police": district["police"], "rythme": list(district["rythme"]),
                           "rares": list(district.get("rares", ()))})
        for district in DISTRICTS:
            if not district.get("gang"):
                continue
            cour = self._enveloppe("g", district)
            if not cour:
                continue
            sortie.append({**cour, "slug": district["gang"], "nom": district["gang_nom"],
                           "district": district["slug"], "gang": district["gang"], "brume": False,
                           "pietons": 10, "vehicules": 3, "police": 0,
                           "rythme": list(district["rythme"]),
                           # ⚠️ Une cour de gang herite des rares de son
                           # district : `Monde.zoneA` rend la zone la PLUS
                           # PRECISE, et sans ca un coupe ne naitrait jamais
                           # dans le seul coin ou l'on se bat pour eux.
                           "rares": list(district.get("rares", ()))})
        bassin = self._enveloppe("~q", district_par_slug("faubourg"))
        if bassin:
            sortie.append({**bassin, "slug": "port", "nom": "Le bassin", "district": "faubourg",
                           "gang": None, "brume": True, "pietons": 6, "vehicules": 2,
                           "police": 1, "rythme": [0.4, 1.0, 1.0], "rares": []})
        return sortie

    def _enveloppe(self, glyphes: str, district: dict | None = None) -> dict | None:
        """Le rectangle qui contient tous les ilots de ces types, rues comprises."""
        borne = self.rect_district(district) if district else None
        rects = []
        for glyphe, x, y, largeur, hauteur in self.regions():
            if glyphe not in glyphes:
                continue
            if borne and not (borne[0] <= x and x + largeur <= borne[0] + borne[2]
                              and borne[1] <= y and y + hauteur <= borne[1] + borne[3]):
                continue
            rects.append((x, y, largeur, hauteur))
        if not rects:
            return None
        x0 = min(r[0] for r in rects)
        y0 = min(r[1] for r in rects)
        x1 = max(r[0] + r[2] for r in rects)
        y1 = max(r[1] + r[3] for r in rects)
        marge = 2 * TROTTOIR
        x0, y0 = max(0, x0 - marge), max(0, y0 - marge)
        x1 = min(self.largeur, x1 + marge)
        y1 = min(self.hauteur, y1 + marge)
        return {"x": x0, "y": y0, "l": x1 - x0, "h": y1 - y0}


def generer(plan: tuple[str, ...] = PLAN, graine: int = GRAINE) -> dict:
    chantier = _Chantier(plan, graine)
    chantier.eaux()
    chantier.rues()
    chantier.croisements()
    chantier.ilots()
    ponts = chantier.ponts()
    chantier.lampadaires()
    chantier.bornes()
    # ⚠️ Apres les ilots, les ponts et le decor : une rampe se juge sur la ville
    # FINIE. Avant les paquets et les ambulants, pour que la piste d'elan soit
    # reservee quand ils cherchent leur place.
    chantier.poser_les_rampes()
    # ⚠️ ICI et pas plus tot : la rampe est la derniere chose qui COUPE une
    # cloture. Ce que la ville a mange des enceintes se voit maintenant, et ce
    # qui n'enferme plus rien s'enleve avant que quiconque le juge.
    chantier.elaguer_les_clotures()
    # Les guichets AVANT les kiosques : une place prise ne se prend pas deux fois.
    chantier.guichets()
    ambulants = chantier.ambulants()
    barrieres = chantier.barrieres(ambulants, ponts)
    reclames = chantier.reclames(ambulants)
    # ⚠️ Apres les ambulants et la reclame : une scene se veut DEGAGEE, et un
    # kiosque pose apres coup au milieu d'un attroupement en ferait un couloir.
    scenes = chantier.scenes()
    paquets = chantier.paquets()
    # ⚠️ Apres les paquets : les machines prennent ce qui reste, et une de plus
    # ne deplace ni un paquet, ni une scene, ni un kiosque.
    chantier.distributrices()
    # ⚠️ Apres les ilots ET les ponts : on tague des murs qui existent, et on
    # ne tague pas une vitrine (les devantures ont deja reserve les leurs).
    chantier.graffitis_sur_les_murs()

    terminus = next(p for p in chantier.points if p["slug"] == "terminus")
    depart = (terminus["x"], terminus["y"])
    bouchees = chantier.boucher_les_poches(depart)
    if bouchees > chantier.largeur * chantier.hauteur // 50:
        raise ValueError(f"{bouchees} tuiles enclavees : un gabarit enferme la ville")
    # ⚠️ LA GREVE SE MEUBLE EN DERNIER : on ne meuble pas un terrain que la ville
    # va encore retirer. `boucher_les_poches` NOIE les bancs de sable isoles, un
    # par un — un parasol pose avant lui peut se retrouver sur l'eau sans que
    # personne l'y ait mis.
    # ⚠️ Mesure, pour ne pas faire passer une precaution pour un correctif : sur
    # huit graines et 1 139 meubles, semer AVANT n'en noie aujourd'hui aucun. Ce
    # qui tient l'ordre n'est donc pas un defaut observe, c'est le principe — et
    # un juge le pin, pour que le jour ou `boucher_les_poches` noiera plus large,
    # ca ne passe pas en silence.
    chantier._ponts_poses = ponts
    chantier.greve(ponts)

    ville = {
        "slug": "baie_des_brumes",
        "nom": "Baie-des-Brumes",
        "graine": graine,
        "districts": [{"slug": d["slug"], "nom": d["nom"], "gang": d["gang"],
                       "eau": bool(d.get("eau"))} for d in DISTRICTS],
        "largeur": chantier.largeur,
        "hauteur": chantier.hauteur,
        "tuile_px": TUILE_PX,
        "grille": {"colonnes": list(COLONNES), "rangees": list(RANGEES),
                   "rues_v": list(RUES_V), "rues_h": list(RUES_H), "trottoir": TROTTOIR,
                   # ⚠️ Douze lignes de glyphes, pas un rectangle par bloc : le
                   # paquet voyage a mille octets de son plafond (`test_definitions`).
                   "standing": list(chantier.standing), "usage": list(chantier.usage)},
        "sol": ["".join(ligne) for ligne in chantier.sol],
        "voie": ["".join(ligne) for ligne in chantier.voie],
        "arrets": chantier.arrets,
        "ponts": ponts,
        # ⚠️ Les plages DECLARENT leur rectangle : le navigateur n'y fait naitre
        # des baigneurs que la, et le deviner d'apres le sable serait une
        # deuxieme verite (le sable d'un etang de parc n'est pas une plage).
        "plages": [{k: p[k] for k in ("x", "y", "l", "h")} for p in chantier.plages],
        "intersections": chantier.intersections,
        "portes": chantier.portes,
        "lampes": chantier.lampes,
        "feux_pietons": chantier.feux_pietons(),
        "decor": chantier.decor,
        "rampes": chantier.rampes,
        "devantures": chantier.devantures,
        "residences": chantier.residences,
        "graffitis": chantier.graffitis,
        "fourriere": chantier.fourriere,
        "barrieres": barrieres,
        "nids_de_poule": chantier.nids_de_poule(),
        "entraves": chantier.entraves(),
        # ⚠️ La fiche A COTE de la liste : « entraves » est ce que la ville
        # PEUT fermer, « entrave » est ce qu'une entrave coute et ce qu'elle
        # dit. Deux noms, deux choses — le navigateur lisait la liste en
        # croyant y trouver la raison.
        "entrave": {"raison": ENTRAVES["raison"], "degats": ENTRAVES["degats"]},
        "fermetures": chantier.fermetures(ponts),
        "fermeture": {"raison": FERMETURES["raison"], "degats": FERMETURES["degats"]},
        "flottants": list(FLOTTANTS),
        "decor_solide": sorted(DECOR_SOLIDE),
        "amarrages": chantier.amarrages(),
        "foire": chantier.foire,
        "roue": chantier.roue,
        "jeux_de_foire": chantier.jeux,
        "kiosques_de_foire": chantier.kiosques,
        # ⚠️ L'INTERIEUR de la palissade, en bandes par rangee [y, x0, x1] : la
        # foule y nait et y reste, et resquiller se juge a la retombee DEDANS.
        "foire_enclos": chantier.foire_enclos,
        # Le petit train et la montagne russe : la GEOMETRIE vient du chantier,
        # la CONDUITE de la fiche — le navigateur n'invente ni l'une ni l'autre.
        "train_de_foire": chantier.train_de_foire and {**chantier.train_de_foire, **FOIRE["train"]},
        "montagne_russe": chantier.montagne_russe and {
            **chantier.montagne_russe,
            **{k: v for k, v in FOIRE["montagne_russe"].items()
               if k in ("pas_px", "chariots", "ecart_px", "vitesse_chaine", "depart", "gravite",
                        "frottement", "vitesse_min", "vitesse_max", "gare_images", "hauteur_px",
                        "rayon_monter_px")}},
        "aqueducs": chantier.aqueducs(),
        "aqueduc": {"raison": AQUEDUCS["raison"], "degats": AQUEDUCS["degats"],
                    "chance_par_heure": AQUEDUCS["chance_par_heure"],
                    "minutes": AQUEDUCS["minutes"], "flaque": AQUEDUCS["flaque"]},
        "ambulants": ambulants,
        "reclames": reclames,
        # ⚠️ OU UN AMUSEUR S'INSTALLE. Jusqu'ici il naissait sur la premiere
        # tuile marchable venue hors de l'ecran — c'est-a-dire souvent dans une
        # ruelle, devant un mur de hangar. Le numero etait bon, l'endroit ne
        # l'etait pas, et personne ne venait le voir.
        "scenes": scenes,
        "paquets": paquets,
        "zones": chantier.zones(),
        "points_interet": chantier.points,
        "toits": chantier.toits,
        "apparition": {"joueur": {"x": depart[0], "y": depart[1]}},
        # ⚠️ LES PIECES DESSINEES **ET** LES POSEES. Les seize lieux garantis
        # sont les memes d'une graine a l'autre (on ecrit des missions dedans) ;
        # les commerces et logements ordinaires, eux, sont poses aux mesures de
        # leur batiment et n'existent que dans CETTE ville-la.
        "interieurs": {**INTERIEURS, **chantier.pieces},
        "tuiles_bouchees": bouchees,
    }
    # ⚠️ L'ILE APRES LA VILLE, AVANT LES CHANTIERS. Apres le filet, qui la
    # noierait (on ne la rejoint pas a pied) ; apres les amarrages et les zones,
    # auxquels elle s'ajoute au bout sans rien deplacer ; et avant les chantiers,
    # les autobus et le mobilier, qui posent leur decor APRES le sien — leurs
    # juges comparent la ville avec et sans eux par le debut de la liste.
    from . import ile as ile_mod
    ville["ile"] = ile_mod.poser(chantier, ville)
    # ⚠️ LES CHANTIERS EN TOUT DERNIER, sur la ville FINIE, et dans leur propre
    # de : ils ne choisissent que ce qui ne sert a rien d'autre, et ne deplacent
    # ni un arbre ni une enseigne. Import paresseux : `chantiers` lit `carte`.
    from . import chantiers as chantiers_mod
    ville["chantiers"] = chantiers_mod.tirer(ville, chantier.batiments, graine)
    # ⚠️ LES LIGNES D'AUTOBUS, APRES LES CHANTIERS : leurs abribus se posent
    # sur la ville finie et ne deplacent rien de ce qui precede. Le trace lit les
    # entraves, les rues barrees et les barrieres — il les contourne toutes.
    from . import autobus as autobus_mod
    ville["autobus"] = autobus_mod.tracer(chantier, ville)
    # ⚠️ LE METRO, apres les autobus et avant le mobilier : ses edicules prennent
    # leur place sur l'abord, et les arbres de rue leur laissent de l'air.
    from . import metro as metro_mod
    ville["metro"] = metro_mod.creuser(chantier, ville)
    # ⚠️ LA SALETE SE DEPLACE, APRES LES LIGNES ET LE METRO, AVANT LE MOBILIER :
    # ce qu'elle enleve et ce qu'elle pose ne deplace ni un abribus, ni un edicule,
    # ni un chantier, et les arbres de rue plantent autour de ce qu'elle a laisse.
    from . import salete as salete_mod
    salete_mod.deplacer(chantier, ville, graine)
    # ⚠️ LES COMMERCES MONTENT ET DESCENDENT SUR LA VILLE FINIE (3e vague) : un nom
    # d'enseigne, des planches sur une vitrine, le standing d'une facade — rien qui
    # deplace une tuile. Tires pendant la construction, les noms changeaient la
    # largeur des bandeaux et les portes peintes : dix juges sont tombes, rampes
    # et barriere du cargo comprises.
    from . import vitrines as vitrines_mod
    vitrines_mod.monter_et_descendre(chantier, ville)
    # ⚠️ LE MOBILIER DE RUE EN TOUT DERNIER, dans son propre de : un arbre de
    # plus ne deplace ni un abribus, ni un paquet, ni une enseigne.
    from . import mobilier as mobilier_mod
    mobilier_mod.semer(chantier, ville, graine)
    # ⚠️ LA TOURNEE DES EBOUEURS, sur la ville FINIE (M12) : elle lit le decor, les
    # abribus et les portes pour poser ses bacs a cote, et ne pose RIEN — les bacs
    # naissent dans le navigateur. Aucun de.
    from . import eboueurs as eboueurs_mod
    ville["eboueurs"] = eboueurs_mod.tracer(ville)
    # ⚠️ LE TRAVERSIER, sur la ville FINIE lui aussi (M12) : il cherche deux quais et
    # le couloir d'eau libre entre eux, et ne pose rien. Aucun de.
    from . import traversier as traversier_mod
    ville["traversier"] = traversier_mod.tracer(ville)
    # ⚠️ LE TRAMWAY, APRES LE TRAVERSIER (M12) : son terminus des Quais est la
    # correspondance du quai. Il trace sa voie double et ses arrets, et ne pose rien.
    from . import tramway as tramway_mod
    ville["tramway"] = tramway_mod.tracer(ville)
    # ⚠️ LA NEIGE (M12) : l'horaire des tempetes, leurs effets et la tournee de la
    # charrue. Elle ne pose rien, ne tire aucun de, et ne tombe que si l'option le veut.
    from . import neige as neige_mod
    ville["neige"] = neige_mod.tracer(ville)
    return ville

# --- Les interieurs ---------------------------------------------------------

#: ⚠️ Une piece se DESSINE ; elle ne se genere pas. Les seize interieurs de la
#: v1 sortaient tous du meme `_salle()` : quatre murs, un comptoir, deux
#: points. On poussait une porte pour trouver une piece vide et un comptoir —
#: la meme, seize fois, avec un autre nom en haut de l'ecran. Ici chaque
#: interieur est un PLAN, une ligne de texte par rangee de tuiles, et c'est ce
#: qui permet qu'un depanneur ait ses allees, qu'un bar ait son billard et
#: qu'un plex ait son escalier.
#:
#: Dans un plan : l'ESPACE est le plancher (celui que dit `sol`), `B` un mur,
#: `W` une fenetre, `D` la porte — une seule, sur le mur du bas. Le reste est
#: un meuble de LEGENDE (`c` comptoir, `e` etagere, `a` table, `h` chaise,
#: `l` lit, `j` frigo, `m` machine, `n` plante, `k` classeur, `z` poele,
#: `/` escalier).

#: Les gens qu'on trouve dedans. `commis` tient le comptoir (il ne bouge pas
#: de son poste) ; `client` est tire au sort dans les passants du quartier.
#: A l'hopital : `soignant` tient le triage comme un commis, mais en blouse ;
#: `patient` attend ASSIS sur une chaise de la salle d'attente, et `malade` est
#: COUCHE dans un lit d'hopital (`ASSIS_OU_COUCHE`). Au Brouillard, `avocat` est
#: Me Desjardins, ASSIS a la table du fond ou l'on vient lui parler.
#: ⚠️ Sans eux, une piece meublee reste un musee : c'est le monde qui parle au
#: comptoir qui fait qu'on a l'impression d'etre entre quelque part.
QUI_DEDANS = ("commis", "client", "patient", "malade", "soignant", "avocat")

#: ⚠️ Les seuls gens qui naissent DANS un meuble, et chacun dans le sien : le
#: PATIENT attend assis sur une chaise de la salle d'attente, l'AVOCAT tient la
#: chaise de sa table, le MALADE est couche dans la tuile de tete d'un lit
#: d'hopital. Partout ailleurs, naitre dans un meuble reste une faute de plan —
#: on le juge ici, au chargement.
ASSIS_OU_COUCHE = {"patient": "h", "avocat": "h", "malade": "r"}


def _gens(*gens: tuple[str, int, int]) -> tuple[dict, ...]:
    return tuple({"qui": qui, "x": x, "y": y} for qui, x, y in gens)


def _pt(type_: str, x: int, y: int, **extra) -> dict:
    return {"type": type_, "x": x, "y": y, **extra}


#: Ce qu'on entend en poussant la porte d'une piece : le bois et la serrure
#: d'un logement, ou la vitre et la porte d'un commerce (`son.js`,
#: `SFX.porte`). ⚠️ C'est la piece qui le dit, pas le JS : un logement qui
#: sonnait comme un depanneur, c'est ce qu'on entendait avant.
GENRES_DE_PORTE = ("maison", "commerce")


def _piece(slug: str, nom: str, plan: str, *, sol: str = "t",
           points: tuple = (), gens: tuple = (), porte: str = "commerce") -> dict:
    """Une piece dessinee a la main, verifiee ICI et pas trois fichiers plus loin.

    ⚠️ Le plan est la verite : la sortie est le « D », l'apparition la tuile
    juste au-dessus. Un plan qui n'est pas rectangulaire, qui n'a pas
    exactement une porte, dont un coin est mure ou dont un point n'est pas
    atteignable leve ici — au chargement du module, avant meme le premier
    test. Une piece ou l'on entre sans pouvoir toucher le comptoir serait une
    porte qu'on ouvre pour rien.
    """
    lignes = [ligne.replace(" ", sol) for ligne in plan.strip("\n").split("\n")]
    largeur, hauteur = len(lignes[0]), len(lignes)
    for y, ligne in enumerate(lignes):
        if len(ligne) != largeur:
            raise ValueError(f"{slug} : la rangee {y} fait {len(ligne)} tuiles au lieu de {largeur}")
        inconnus = set(ligne) - set(LEGENDE)
        if inconnus:
            raise ValueError(f"{slug} : glyphes inconnus {sorted(inconnus)}")
    portes = [(x, y) for y, ligne in enumerate(lignes)
              for x, glyphe in enumerate(ligne) if glyphe == "D"]
    if len(portes) != 1:
        raise ValueError(f"{slug} : {len(portes)} portes, il en faut exactement une")
    px, py = portes[0]
    if py != hauteur - 1:
        raise ValueError(f"{slug} : la porte doit etre sur le mur du bas")
    if not marchable(lignes[py - 1][px]):
        raise ValueError(f"{slug} : on entre dans un mur")
    if porte not in GENRES_DE_PORTE:
        raise ValueError(f"{slug} : « {porte} » n'est pas une porte ({GENRES_DE_PORTE})")
    piece = {
        "slug": slug, "nom": nom, "largeur": largeur, "hauteur": hauteur,
        # ⚠️ Le plancher voyage avec la piece : un meuble ne couvre pas toute sa
        # tuile (une chaise laisse voir le bois autour), et le peintre a besoin
        # de savoir quoi mettre DESSOUS. Sans lui, chaque table etait un trou
        # noir dans le plancher — c'etait visible a l'oeil nu.
        "plancher": sol,
        "sol": lignes, "sortie": {"x": px, "y": py},
        "apparition": {"x": px, "y": py - 1},
        "points": [dict(p) for p in points],
        "gens": [dict(g) for g in gens],
        "porte": porte,
    }
    _verifier_piece(piece)
    return piece


#: Le rayon ou ACTION attrape un point d'action (`pointSousLaMain`,
#: missions.js), en tuiles. ⚠️ Il est ICI parce que c'est ici qu'on peut le
#: juger : un point pose a moins que ca de la tuile de sortie VOLE la porte —
#: ACTION sert le comptoir, toujours, et on ne ressort plus. Six pieces etaient
#: dans ce cas (« chez Ti-Paul, il est impossible de sortir »), et le point du
#: journal du depanneur etait PILE sur la tuile de sortie. Le jeu, lui, fait
#: maintenant passer la porte avant le comptoir ; ce juge-ci empeche de
#: redessiner le piege.
RAYON_POINT = 1.6


def _verifier_piece(piece: dict) -> None:
    groupes = composantes_marchables(piece)
    if len(groupes) != 1:
        raise ValueError(f"{piece['slug']} : {len(groupes)} morceaux de plancher separes")
    atteignable = groupes[0]
    sol = piece["sol"]
    for point in piece["points"]:
        x, y = point["x"], point["y"]
        if not (0 < x < piece["largeur"] - 1 and 0 < y < piece["hauteur"] - 1):
            raise ValueError(f"{piece['slug']} : le point {point['type']} est dans le mur")
        if (x, y) not in atteignable:
            raise ValueError(f"{piece['slug']} : le point {point['type']} n'est pas atteignable")
        # ⚠️ Un point POSE SUR un meuble (le lit, l'escalier) est bon ; encore
        # faut-il pouvoir se planter a cote pour l'utiliser.
        if not any(solidite(sol[y + dy][x + dx]) == 0
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            raise ValueError(f"{piece['slug']} : le point {point['type']} est inaccessible")
        # ⚠️ Et il ne vole pas la porte : voir RAYON_POINT.
        sortie = piece["apparition"]
        ecart = math.hypot(x - sortie["x"], y - sortie["y"])
        if ecart < RAYON_POINT:
            raise ValueError(
                f"{piece['slug']} : le point {point['type']} est a {ecart:.2f} tuile de la "
                f"sortie (minimum {RAYON_POINT}) — il volerait ACTION a la porte")
    for gens in piece["gens"]:
        if gens["qui"] not in QUI_DEDANS:
            raise ValueError(f"{piece['slug']} : « {gens['qui']} » n'est pas quelqu'un")
        glyphe = sol[gens["y"]][gens["x"]]
        meuble = ASSIS_OU_COUCHE.get(gens["qui"])
        if meuble:
            if glyphe != meuble:
                raise ValueError(f"{piece['slug']} : le {gens['qui']} en {gens['x']},{gens['y']} "
                                 f"n'est pas sur « {meuble} » ({LEGENDE[meuble]['nom']})")
            # Couche la tete au NORD : la tuile de tete d'un lit est celle qui
            # n'a pas de lit au-dessus d'elle.
            if gens["qui"] == "malade" and sol[gens["y"] - 1][gens["x"]] == meuble:
                raise ValueError(f"{piece['slug']} : le malade en {gens['x']},{gens['y']} "
                                 "est couche au pied du lit")
        elif solidite(glyphe) != 0:
            raise ValueError(f"{piece['slug']} : quelqu'un est ne dans un meuble")


#: Les pieces des lieux garantis (`SPECIAUX`) et des donneurs de mission.
_PIECES: tuple[dict, ...] = (
    # Le terminus : c'est ici qu'on debarque au premier matin. Deux rangees de
    # bancs, la consigne derriere le guichet, et un comptoir qui sert le cafe.
    # ⚠️ Et la distributrice a liqueur dans le coin : c'est la premiere piece
    # du jeu, et un terminus d'autobus sans machine n'en est pas un.
    _piece("terminus", "Terminus Baie-des-Brumes", sol="u", plan="""
BBBWWWWWBBB
Bn  kkk  bB
B cccccc  B
B         B
B hhh hhh B
B         B
B hhh hhh B
BBBWWDWWBBB
""", points=(_pt("emplettes", 4, 2, genre="service"), _pt("distributrice", 9, 1, sorte="liqueur")),
     gens=_gens(("commis", 3, 1), ("client", 2, 3), ("client", 8, 5))),

    # La planque de Rocco : un lit, un coffre, une garde-robe, et de quoi se
    # faire un cafe. C'est petit, c'est a nous, et ca sauve la partie.
    _piece("planque", "La planque de Rocco", porte="maison", plan="""
BBBWWWBBBBB
Bll   k  nB
Bll   k  mB
B ah yyy  B
B ah yyy  B
B    yyy eB
Bj z    n B
BBBBWWDWWBB
""", points=(_pt("lit", 2, 2), _pt("coffre", 6, 1), _pt("garde_robe", 9, 5)),
     gens=()),

    # Le garage : deux ponts, un mur d'outils, des pneus empiles.
    _piece("garage", "Garage Rocco Bandini", sol="u", plan="""
BBBWWWWBBB
Bee   mm B
B  aaa   B
B  aaa   B
Bccccc   B
Bn      nB
BBBBWWDWBB
""", points=(_pt("vendre", 3, 4), _pt("reparer", 7, 1), _pt("repeindre", 3, 2)),
     gens=_gens(("commis", 2, 5),)),

    # Chez Gus : pas une fenetre, des rateliers pleins, une cible au fond.
    _piece("armurerie", "Chez Gus", plan="""
BBBBBBBBBBB
BeeeeeeeeeB
B         B
B ccccccc B
B         B
Bm       kB
Bn       nB
BBBBWWDWWBB
""", points=(_pt("acheter", 5, 3),), gens=_gens(("commis", 5, 2),)),

    # Boutique Rosa : trois portants, une cabine au tapis.
    _piece("vetements", "Boutique Rosa", plan="""
BBBWWWWWBBB
Be e e   nB
Be e e   yB
Be e e   yB
B         B
B ccccc   B
Bn        B
BBBWWDWWBBB
""", points=(_pt("acheter", 3, 5),),
     gens=_gens(("commis", 4, 4), ("client", 2, 4))),

    # Le poste : le comptoir, les classeurs, le banc de ceux qui attendent.
    # ⚠️ Et la machine a cafe du mur est : un poste de police sans sa machine
    # a cafe, personne n'y croirait.
    _piece("poste", "Poste de police", sol="u", plan="""
BBBWWWWWBBBB
Bkkkk    n B
B     a h  B
B     a h  B
Bcccccc   bB
B          B
B hhhh     B
Bn        nB
BBBBWWDWWBBB
""", points=(_pt("casier", 3, 4), _pt("distributrice", 10, 4, sorte="cafe")),
     gens=_gens(("commis", 3, 3), ("client", 7, 6))),

    # L'hopital, en bas : l'URGENCE. Le triage et ses classeurs, un lit
    # d'examen entre son solute et son moniteur, la salle d'attente — deux
    # rangees de chaises, du monde assis dessus — et les deux machines du mur
    # est. L'escalier monte aux chambres.
    # ⚠️ Plus grand en PROFONDEUR et en etage, pas en largeur : l'ilot de
    # l'hopital fait douze tuiles de large, et une piece a exactement les
    # mesures de son batiment (`test_la_piece_a_les_mesures_de_son_batiment`).
    _piece("hopital", "Hôpital de Baie-des-Brumes", sol="u", plan="""
BBBWWWWBBWWWBB
Bkk   n irq /B
B ccccc  r   B
B            B
B hhhh hhhh bB
B            B
B hhhh hhhh bB
B            B
Bn          nB
BBBBBWWDWWBBBB
""", points=(_pt("soigner", 4, 3), _pt("escalier", 12, 1, vers="hopital_soins"),
             _pt("distributrice", 12, 4, sorte="cafe"),
             _pt("distributrice", 12, 6, sorte="grignotines")),
     gens=_gens(("soignant", 4, 1), ("malade", 9, 1),
                ("patient", 2, 4), ("patient", 4, 4), ("patient", 8, 4),
                ("patient", 3, 6), ("patient", 9, 6), ("patient", 10, 6),
                ("client", 6, 7))),

    # L'hopital, en haut : les CHAMBRES. Six lits en deux rangees, chacun entre
    # la potence de son solute et l'ecran de son moniteur, et un malade dans
    # chacun. Le poste des infirmieres au milieu.
    _piece("hopital_soins", "Hôpital — l'étage des soins", sol="u", porte="maison", plan="""
BBWWWBBWWWBBBB
Birqirqirq  /B
B r  r  r    B
B            B
Bk  cccc    nB
B            B
Birqirqirq   B
B r  r  r    B
Bn          nB
BBBBBBBBBBDBBB
""", points=(_pt("soigner", 5, 5), _pt("escalier", 12, 1, vers="hopital")),
     gens=_gens(("soignant", 5, 3),
                ("malade", 2, 1), ("malade", 5, 1), ("malade", 8, 1),
                ("malade", 2, 6), ("malade", 5, 6), ("malade", 8, 6),
                ("client", 10, 3))),

    # Le Brouillard : le bar, les tables, le billard — Josee au fond, et Me
    # Desjardins assis a la table de gauche. ⚠️ Son point est SA CHAISE, pas la
    # table : on vise l'homme qu'on voit. Pose sur la table, il ne s'attrapait
    # pas du pas d'a cote de lui (deux tuiles, `RAYON_POINT` en tient 1,6).
    _piece("bar", "Bar Le Brouillard", plan="""
BBBBBBBBBBBB
Bj        eB
B ccccccc  B
B          B
B ah  ah   B
B ah  ah   B
B          B
Baaaa    ahB
BBBBWWDWWBBB
""", points=(_pt("caisse", 4, 2), _pt("contact", 10, 7), _pt("avocat", 3, 5)),
     gens=_gens(("commis", 4, 1), ("client", 5, 4), ("client", 8, 5), ("avocat", 3, 5))),

    # Le casse-croute : la cuisine, les tabourets, les banquettes du fond.
    _piece("casse_croute", "Casse-croûte du Faubourg", sol="u", plan="""
BBBBBBBBB
Bzj  ee B
B       B
Bccccc aB
Bhhhhh hB
Baah    B
BBWWDWWBB
""", points=(_pt("hotdog", 3, 3), _pt("sergent", 7, 4)),
     gens=_gens(("commis", 3, 2), ("client", 6, 4))),

    # Le kiosque de Madame Thibodeau : trois pas de large, tout est a portee.
    _piece("kiosque", "Kiosque de Mme Thibodeau", plan="""
BBBBBB
Be enB
Bccc B
B    B
BBWDWB
""", points=(_pt("caisse", 1, 2), _pt("journal", 3, 1)),
     gens=_gens(("commis", 2, 1),)),

    # Chez Ti-Paul : deux allees, les frigos au fond, la caisse a l'entree.
    _piece("depanneur", "Dépanneur Chez Ti-Paul", plan="""
BBBBBBBBBBB
Bjjj  eee B
B         B
B eeee eeeB
B         B
Bccccc  n B
B         B
BBBWWDWWBBB
""", points=(_pt("emplettes", 3, 5, genre="bouffe"), _pt("journal", 9, 5)),
     gens=_gens(("commis", 3, 4), ("client", 8, 2))),

    # L'Hotel Bandini : le hall, le tapis, et l'escalier vers les chambres.
    _piece("hotel", "Hôtel Bandini", plan="""
BBBBWWWWWWWBBBBBB
Bkk            /B
B  ccccccc     /B
B     yyyy      B
B  h  yyyy  h   B
B     yyyy      B
Bn           n  B
B               B
Bn             nB
BBBBBBWWDWWBBBBBB
""", points=(_pt("caisse", 4, 3), _pt("escalier", 15, 2, vers="hotel_chambre")),
     gens=_gens(("commis", 4, 1), ("client", 8, 6))),

    # La chambre de l'Hotel Bandini : un lit, une fenetre sur la baie.
    _piece("hotel_chambre", "Chambre de l'Hôtel Bandini", porte="maison", plan="""
BBBWWWWWBBBBB
Bll       n B
Bll      k  B
B           B
B  a h   e  B
B  a h      B
Bn         /B
BBBBBBDBBBBBB
""", points=(_pt("lit", 2, 1), _pt("escalier", 11, 6, vers="hotel")),
     gens=()),

    # La cantine des Quais : on y mange debout, la fenetre donne sur l'eau.
    _piece("cantine", "Cantine des Quais", sol="u", plan="""
BBBBWWWWWBBBBB
Bz  j     ee B
B            B
Bcccccccccc  B
B            B
B  ah  ah   nB
B  ah  ah    B
Bn           B
BBBBWWDWWBBBBB
""", points=(_pt("hotdog", 4, 4), _pt("emplettes", 9, 4, genre="marine")),
     gens=_gens(("commis", 4, 2), ("client", 10, 5))),

    # L'usine Prevost : les grandes machines, l'etabli, le magasin d'outils.
    _piece("usine", "Usine Prévost", sol="u", plan="""
BBBBWWWWWWWBBBBBB
Bmmmm   mmmm   kB
Bmmmm   mmmm    B
B               B
B  mmmm   mmmm  B
B  mmmm   mmmm  B
B               B
Bcccc       eee B
B               B
BBBBBBWWDWWBBBBBB
""", points=(_pt("emplettes", 2, 8, genre="industrie"),),
     gens=_gens(("commis", 2, 6), ("client", 10, 3))),

    # La fourriere : un comptoir, un classeur, et la cour derriere la vitre.
    # Electronique Turcotte : la vitrine repare des televisions ; l'arriere-
    # boutique fait autre chose. ⚠️ Le mur du fond n'est pas de la decoration :
    # on ne voit pas de la rue ce qui se passe derriere, et c'est tout le
    # personnage.
    _piece("electronique", "Électronique Turcotte", plan="""
BBBBBBBBBBB
Bm  k  m  B
B         B
BBBBB BBBBB
B         B
Beee   eeeB
B ccccc  nB
Bn        B
BBBWWDWWBBB
""", points=(_pt("hacker", 1, 1),),
     gens=_gens(("commis", 5, 5),)),

    _piece("fourriere", "Fourrière municipale", sol="u", plan="""
BBBWWWBB
Bkk   nB
B      B
Bcccc  B
B      B
BBWWDWBB
""", points=(_pt("fourriere", 2, 3),), gens=_gens(("commis", 2, 2),)),

    # Le phare : rond, etroit, et il sent le diesel.
    _piece("phare", "Le phare de La Pointe", porte="maison", plan="""
BBBWWWBBBBB
Bll      nB
Bll       B
B   a h   B
B         B
Bz j    e B
BBBWWDWWBBB
""", points=(_pt("lit", 2, 1), _pt("journal", 3, 4)),
     gens=_gens(("commis", 8, 4),)),

    # --- Le metro : un quai et une rame, pour toutes les stations -------------
    # ⚠️ PARTAGES, comme la piece d'une porte ordinaire : ce qui change d'une
    # station a l'autre est le NOM qu'on lit en descendant et l'edicule par ou
    # l'on remonte (`metro.py`, `metro.js`), pas les murs.
    #
    # Le quai : les deux rangees du haut sont le TUNNEL et sa voie, que
    # `metro.js` peint par-dessus a chaque image (la rame qui entre, s'arrete et
    # repart) ; la rangee de vitres est la barriere du quai et ses portes
    # palieres. Des bancs, deux machines, et l'escalier qui remonte a la rue.
    _piece("metro_quai", "Métro", sol="u", plan="""
BBBBBBBBBBBBB
BBBBBBBBBBBBB
BWWWWWWWWWWWB
B           B
B hhh   hhh B
B           B
Bnb   k   bnB
Bn         nB
BBBBBBDBBBBBB
""", points=(_pt("rame", 6, 3), _pt("distributrice", 2, 6, sorte="cafe"),
             _pt("distributrice", 10, 6, sorte="liqueur")),
     gens=_gens(("client", 3, 5), ("client", 9, 3))),

    # La rame : des banquettes le long des vitres, les coffres techniques aux bouts, et le
    # tunnel qui defile dans les fenetres (`metro.js`). ⚠️ Sa porte du bas est
    # celle de la VOITURE : elle ne s'ouvre qu'en station, et elle mene au quai,
    # jamais a la rue.
    _piece("metro_rame", "Rame de métro", sol="u", plan="""
BWWWWBWWWWBWWWWB
Bhhhh hhhh hhhhB
Bk            kB
B              B
Bhhhh      hhhhB
BBBBBBBDBBBBBBBB
""", points=(_pt("rame", 7, 2),),
     gens=_gens(("client", 4, 2), ("client", 11, 3))),
)

#: ⚠️ LES PIECES DESSINEES, et elles seules. Les dix boutiques de famille, les
#: deux logements et les quatre petites pieces ont vecu une journee : ils
#: repondaient a « une piece ne depasse pas son batiment » par des TAILLES, et
#: trois tailles ne couvrent pas des batiments allant de neuf tuiles a trois
#: cent quatre-vingts dans toutes les formes. Ce qu'ils disaient de bon — une
#: epicerie a des frigos et des allees, une taverne des tables — est passe dans
#: `MOBILIER`, et les pieces se POSENT maintenant a la mesure (voir plus bas).
#: Restent ici les endroits qui ne se generent pas : les lieux garantis et les
#: pieces ou se tiennent les donneurs de mission.
INTERIEURS: dict[str, dict] = {p["slug"]: p for p in _PIECES}


def mesures_de(piece: dict) -> tuple[int, int]:
    """Les mesures du PLANCHER d'une piece, murs deduits."""
    return max(0, piece["largeur"] - 2), max(0, piece["hauteur"] - 2)


def suite_de(slug: str, pieces: dict[str, dict] | None = None) -> list[str]:
    """La piece et tout ce qu'on atteint en poussant sa porte (les etages).

    ⚠️ `pieces` permet de lire les pieces d'UNE VILLE (dessinees et posees
    melees) et pas seulement le catalogue du module : un logement pose a la
    mesure d'un plex n'est pas dans `INTERIEURS`, il n'existe que la-bas.
    """
    catalogue = INTERIEURS if pieces is None else pieces
    vus: set[str] = set()
    a_voir = [slug]
    while a_voir:
        courant = a_voir.pop()
        if courant in vus or courant not in catalogue:
            continue
        vus.add(courant)
        a_voir += [pt["vers"] for pt in catalogue[courant]["points"] if pt.get("vers")]
    return sorted(vus)


def mesures_de_la_suite(slug: str, pieces: dict[str, dict] | None = None) -> tuple[int, int]:
    """La boite qu'il faut au BATIMENT pour porter cette piece et ses etages.

    ⚠️ La plus grande largeur et la plus grande profondeur de la suite, pas leur
    somme : un batiment de N etages contient N pieces de son empreinte, jamais
    UNE piece N fois plus grande. Et c'est la BOITE, pas la surface — viser la
    surface donnait a la cantine 58 x 7 pour une piece de 14 x 9.
    """
    catalogue = INTERIEURS if pieces is None else pieces
    mesures = [mesures_de(catalogue[s]) for s in suite_de(slug, catalogue)] or [(0, 0)]
    return max(m[0] for m in mesures), max(m[1] for m in mesures)


# --- Les pieces POSEES A LA MESURE ------------------------------------------

#: ⚠️ CE QUI SE DESSINE, ET CE QUI SE POSE. Les seize lieux garantis et les
#: pieces de mission se DESSINENT (plus haut) : le billard du Brouillard, les
#: lits de l'hopital et les ponts du garage sont des endroits, pas des gabarits.
#: Les commerces et les logements ORDINAIRES, eux, se POSENT aux mesures de
#: leur batiment. Trois tailles dessinees ne peuvent pas couvrir des batiments
#: qui vont de neuf tuiles a trois cent quatre-vingts dans toutes les formes :
#: on ouvrait un bloc de 59 x 8 sur une piece de 9 x 8 — treize pour cent — et
#: un batiment de quatre tuiles de profond sur une piece qui en fait six.
#:
#: La FAMILLE dit quoi meubler, la MESURE dit combien. Une piece posee passe
#: par `_piece()` comme les autres : meme validation, memes juges, et une piece
#: impossible leve PENDANT la generation au lieu de s'ouvrir en jeu.

#: Le mobilier d'une famille de commerce : le motif du FOND (le mur du fond),
#: celui des ALLEES, le plancher, le nom generique et ce que sert le comptoir.
#: ⚠️ Un motif se lit comme un bout de plan et se repete sur la largeur — ses
#: TROUS sont ce qui fait qu'une allee est une allee et pas un mur de meubles.
#: Et un motif ne colle jamais deux tuiles d'un meme `bloc` (`a` la table, `y`
#: le tapis, `m` la machine) autrement qu'en rectangle : c'est la regle des
#: meubles peints par leurs voisines, et elle se juge sur les pieces posees
#: comme sur les dessinees.
MOBILIER: dict[str, dict] = {
    "bouffe": {"nom": "L'épicerie", "sol": "t", "fond": "jjj ", "allee": "eee ",
               "point": ("emplettes", "bouffe")},
    "service": {"nom": "Le salon", "sol": "t", "fond": "ee n", "allee": "hh yy ",
                "point": ("salon", None)},
    "artisan": {"nom": "L'atelier", "sol": "t", "fond": "eeee ", "allee": "mm ee ",
                "point": ("emplettes", "artisan")},
    "nuit": {"nom": "La taverne", "sol": "t", "fond": "cc j ", "allee": "ah ",
             "point": ("emplettes", "nuit")},
    "commerce": {"nom": "Le magasin", "sol": "t", "fond": "e e n", "allee": "ee ee ",
                 "point": ("emplettes", "commerce")},
    "marine": {"nom": "La criée", "sol": "u", "fond": "jjjj ", "allee": "ee aa ",
               "point": ("emplettes", "marine")},
    "industrie": {"nom": "La quincaillerie", "sol": "u", "fond": "mm mm ",
                  "allee": "ee mm ", "point": ("emplettes", "industrie")},
    "sante": {"nom": "La pharmacie", "sol": "u", "fond": "eeeee ", "allee": "ee ee ",
              "point": ("emplettes", "sante")},
    "mode": {"nom": "La boutique", "sol": "t", "fond": "e e e ", "allee": "ee yy ",
             "point": ("emplettes", "mode")},
    "savoir": {"nom": "Le kiosque à journaux", "sol": "t", "fond": "eeeee ",
               "allee": "ee ee ", "point": ("journal", None)},
}

#: Le plus petit plancher qu'on ose ouvrir : trois sur trois. En dessous, la
#: porte reste condamnee — c'etait deja la regle, et elle ne change pas.
PLANCHER_MIN = 3


def mesures_de_la_part(tuiles: set[tuple[int, int]]) -> tuple[int, int] | None:
    """Les mesures du plancher qu'on peut poser derriere cette part de batiment.

    La boite de ce qu'on VOIT de la rue, ramenee au besoin sous l'empreinte —
    un batiment en L ne remplit pas sa boite, et une piece ne ment pas.

    ⚠️ C'est la PROFONDEUR qui cede la premiere : la largeur d'une vitrine est
    ce que le joueur compare en poussant la porte, la profondeur est ce qu'il ne
    pouvait pas voir du trottoir.
    """
    if not tuiles:
        return None
    xs = [x for x, _ in tuiles]
    ys = [y for _, y in tuiles]
    largeur, hauteur = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    empreinte = len(tuiles)
    while largeur * hauteur > empreinte and hauteur > PLANCHER_MIN:
        hauteur -= 1
    while largeur * hauteur > empreinte and largeur > PLANCHER_MIN:
        largeur -= 1
    if largeur < PLANCHER_MIN or hauteur < PLANCHER_MIN or largeur * hauteur > empreinte:
        return None
    return largeur, hauteur


def _mur_de_devant(largeur: int, porte: int) -> str:
    """Le mur de la rue : la porte, et des vitrines de chaque cote."""
    lettres = []
    for i in range(largeur + 2):
        if i == porte:
            lettres.append("D")
        elif 1 <= i <= largeur and 1 <= abs(i - porte) <= 2:
            lettres.append("W")
        else:
            lettres.append("B")
    return "".join(lettres)


def _plan_de(grille: list[list[str]], porte: int) -> str:
    """Les murs autour d'un interieur meuble, et la porte au bon rang."""
    largeur = len(grille[0])
    lignes = ["B" * (largeur + 2)]
    lignes += ["B" + "".join(rangee) + "B" for rangee in grille]
    lignes.append(_mur_de_devant(largeur, porte))
    return "\n".join(lignes)


def _repeter(motif: str, largeur: int, decalage: int = 0) -> list[str]:
    """Un motif repete sur toute la largeur, a partir d'un cran donne."""
    return [motif[(i + decalage) % len(motif)] for i in range(largeur)]


def _libre(grille: list[list[str]], x: int, y: int) -> bool:
    return grille[y][x] == " "


def _poser_le_point(grille: list[list[str]], type_: str, genre: str | None,
                    porte: int, prefere: list[tuple[int, int]],
                    garder: tuple = (), **extra) -> dict:
    """Un point d'action sur un meuble — le plus LOIN possible de la sortie.

    ⚠️ Deux regles s'affrontent, et c'est ici qu'on les tient toutes les deux :
    un comptoir pose a moins de `RAYON_POINT` de la tuile d'entree VOLE ACTION a
    la porte (« chez Ti-Paul, il est impossible de sortir »), et un point qu'on
    ne peut pas toucher n'est pas un comptoir. On prend donc le meuble le plus
    loin qui ait une tuile de plancher a cote — et s'il n'en a pas, on lui en
    degage une plutot que de reculer.
    """
    largeur, hauteur = len(grille[0]), len(grille)
    sortie = (porte - 1, hauteur - 1)

    def du_plus_loin(tuiles):
        return sorted((c for c in dict.fromkeys(tuiles) if grille[c[1]][c[0]] != " "),
                      key=lambda c: -math.hypot(c[0] - sortie[0], c[1] - sortie[1]))

    # ⚠️ Le comptoir D'ABORD, le reste en recours : un point `emplettes` pose
    # sur l'etagere du fond parce qu'elle est plus loin ne serait plus un
    # comptoir, et le commis se retrouverait a servir de dos.
    reste = [(x, y) for y in range(hauteur) for x in range(largeur)]
    for x, y in du_plus_loin(prefere) + du_plus_loin(reste):
        if math.hypot(x - sortie[0], y - sortie[1]) < RAYON_POINT:
            continue
        voisines = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= x + dx < largeur and 0 <= y + dy < hauteur]
        if not any(_libre(grille, *v) for v in voisines):
            # ⚠️ On DEGAGE une voisine plutot que de reculer — reculer d'un
            # meuble donnerait un point plus pres de la porte, et c'est l'autre
            # regle qu'on casserait. Mais jamais la tuile d'un BLOC : un lit a
            # qui l'on enleve un coin n'est plus un rectangle, donc plus un lit.
            # ⚠️ Ni un BLOC, ni une tuile qui porte deja un point : degager
            # l'escalier pour atteindre un tiroir, c'est effacer l'escalier —
            # il restait un point `escalier` sur une tuile de plancher nu.
            degageables = [v for v in voisines
                           if not LEGENDE[grille[v[1]][v[0]]].get("bloc") and v not in garder]
            if not degageables:
                continue
            vx, vy = max(degageables, key=lambda v: math.hypot(v[0] - sortie[0],
                                                               v[1] - sortie[1]))
            grille[vy][vx] = " "
        return _pt(type_, x + 1, y + 1, **({"genre": genre} if genre else {}), **extra)
    raise ValueError(f"aucune place pour un point {type_} dans {largeur} x {hauteur}")


#: Ce qu'une piece doit montrer de meubles : un dixieme de sa boite, et deux
#: SORTES (juge `une piece est meublee` — « on ouvre une porte et il n'y a
#: jamais rien »). On vise un peu au-dessus pour ne pas raser le seuil.
PART_MEUBLEE = 0.12


def _completer_les_meubles(grille: list[list[str]], porte: int, petits: str,
                           proteges: tuple = ()) -> None:
    """Ajoute de petits meubles tant que la piece a l'air vide.

    ⚠️ Les petites pieces sont celles qui en ont besoin : une chambre de trois
    sur trois n'a qu'UN coin, et si le sort lui donne le tapis elle n'a aucun
    meuble du tout (un tapis ne compte pas — on marche dessus). On remplit
    depuis le FOND : ce qu'on ajoute doit se voir en entrant, pas barrer la
    porte.
    """
    largeur, hauteur = len(grille[0]), len(grille)
    boite = (largeur + 2) * (hauteur + 2)
    libres = sorted(((x, y) for y in range(hauteur) for x in range(largeur)
                     if _libre(grille, x, y) and (x, y) != (porte - 1, hauteur - 1)),
                    key=lambda t: -math.hypot(t[0] - (porte - 1), t[1] - (hauteur - 1)))
    #: ⚠️ Ce qui ne doit JAMAIS se retrouver mure : les tuiles qui portent un
    #: point d'action. Un point sans une tuile de plancher a cote est
    #: injoignable — `_verifier_piece` le refuse, et il a raison : on verrait le
    #: comptoir sans pouvoir le toucher.
    def enferme(x: int, y: int) -> bool:
        for mx, my in proteges:
            if abs(mx - x) + abs(my - y) != 1:
                continue
            autour = [(mx + dx, my + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                      if 0 <= mx + dx < largeur and 0 <= my + dy < hauteur]
            if sum(1 for v in autour if _libre(grille, *v)) <= 1:
                return True
        return False

    poses = 0
    for x, y in libres:
        meubles = [g for ligne in grille for g in ligne if LEGENDE.get(g, {}).get("meuble")]
        if len(meubles) >= boite * PART_MEUBLEE and len(set(meubles)) >= 2:
            return
        if enferme(x, y):
            continue
        grille[y][x] = petits[poses % len(petits)]
        poses += 1


def _quelqu_un(grille: list[list[str]], qui: str, autour: tuple[int, int],
               porte: int, pris: set[tuple[int, int]]) -> tuple | None:
    """Une tuile de PLANCHER libre pres d'un endroit — personne ne nait dans un
    meuble, ni sur le pas de la porte."""
    largeur, hauteur = len(grille[0]), len(grille)
    places = sorted(((x, y) for y in range(hauteur) for x in range(largeur)
                     if _libre(grille, x, y) and (x, y) not in pris
                     and (x, y) != (porte - 1, hauteur - 1)),
                    key=lambda p: math.hypot(p[0] - autour[0], p[1] - autour[1]))
    if not places:
        return None
    pris.add(places[0])
    return (qui, places[0][0] + 1, places[0][1] + 1)


def piece_de_commerce(slug: str, famille: str, largeur: int, hauteur: int,
                      porte: int, variante: int = 0, standing: str | None = None) -> dict:
    """Un commerce POSE : le fond, les allees, le comptoir, et du monde dedans.

    Trois rangees qui ne changent pas, quelle que soit la taille : le FOND
    contre le mur du fond, le COMPTOIR a l'avant-derniere rangee, et la derniere
    rangee LIBRE — c'est celle ou l'on entre, et un comptoir colle a la porte se
    sert tout seul. Entre les deux, une allee une rangee sur deux : c'est ce qui
    fait qu'un magasin de dix de profond est un magasin, et pas un hangar avec
    un comptoir au fond.
    """
    fiche = MOBILIER[famille]
    grille = [[" "] * largeur for _ in range(hauteur)]
    for x, glyphe in enumerate(_repeter(fiche["fond"], largeur, variante)):
        grille[0][x] = glyphe
    for k, y in enumerate(range(2, hauteur - 3, 2)):
        for x, glyphe in enumerate(_repeter(fiche["allee"], largeur, variante + k)):
            grille[y][x] = glyphe
    # Le comptoir : la moitie de la largeur, du cote oppose a la porte.
    rangee = hauteur - 2
    long_ = max(2, min(largeur - 1, (largeur + 1) // 2))
    # ⚠️ Le standing se voit en entrant (3e vague) : le comptoir d'un commerce
    # pauvre barre presque toute la piece — on est servi de loin, comme chez un
    # preteur sur gages ; un commerce cossu a une plante de chaque cote de la porte.
    if standing == "pauvre":
        long_ = max(2, min(largeur - 1, (3 * largeur + 3) // 4))
    debut = 0 if porte > largeur / 2 else largeur - long_
    comptoir = [(x, rangee) for x in range(debut, debut + long_)]
    for x, y in comptoir:
        grille[y][x] = "c"
    # Une plante a l'entree, du cote ou il reste de la place — deux en cossu,
    # aucune en pauvre.
    plantes = {"cossu": 2, "pauvre": 0}.get(standing, 1)
    for x in (0, largeur - 1):
        if plantes and abs(x + 1 - porte) >= 2 and _libre(grille, x, hauteur - 1):
            grille[hauteur - 1][x] = "n"
            plantes -= 1
    type_, genre = fiche["point"]
    points = [_poser_le_point(grille, type_, genre, porte, list(reversed(comptoir)))]
    _completer_les_meubles(grille, porte, "enk",
                           tuple((p["x"] - 1, p["y"] - 1) for p in points))
    pris: set[tuple[int, int]] = set()
    gens = [_quelqu_un(grille, "commis", (comptoir[0][0], rangee - 1), porte, pris)]
    for k in range(min(2, (largeur * hauteur) // 30)):
        gens.append(_quelqu_un(grille, "client", (largeur // 2, max(0, hauteur - 2 - 2 * k)),
                               porte, pris))
    return _piece(slug, fiche["nom"], _plan_de(grille, porte), sol=fiche["sol"],
                  points=tuple(points), gens=_gens(*[g for g in gens if g]))


#: Les coins d'un logement, dans l'ordre ou on les pose. ⚠️ Un grand logement
#: n'est pas un grand vide : c'est PLUS de coins meubles, pas un lit perdu au
#: milieu de vingt-quatre tuiles. Chacun tient dans deux tuiles sur deux, et les
#: coins sont assez espaces pour que deux blocs du meme meuble ne se touchent
#: jamais (un lit colle a un lit serait peint comme UN lit de quatre de large —
#: voir `varianteDeLit`).
COINS_DE_LOGEMENT = ("lit", "table", "cuisine", "tapis", "rangement")

#: Le pas des coins : deux tuiles de meuble, et de quoi passer entre.
COIN_L, COIN_H = 5, 3


def _meubler_le_coin(grille: list[list[str]], x0: int, y0: int, quoi: str) -> None:
    """Un coin de logement dans son carre de deux sur deux."""
    largeur, hauteur = len(grille[0]), len(grille)
    place = [(x, y) for y in range(y0, min(y0 + 2, hauteur - 1))
             for x in range(x0, min(x0 + 2, largeur))]
    if not place:
        return
    if quoi in ("lit", "table", "tapis"):
        glyphe = {"lit": "l", "table": "a", "tapis": "y"}[quoi]
        for x, y in place:
            grille[y][x] = glyphe
        if quoi == "table":
            for _, y in place:
                cx = x0 + 2
                if cx < largeur and _libre(grille, cx, y):
                    grille[y][cx] = "h"
        return
    meubles = {"cuisine": "jze", "rangement": "kee"}[quoi]
    for i, (x, y) in enumerate(place):
        grille[y][x] = meubles[i % len(meubles)]


def piece_de_logement(slug: str, largeur: int, hauteur: int, porte: int,
                      *, etage: str | None = None, haut: bool = False,
                      variante: int = 0) -> dict:
    """Un logement POSE : des coins meubles, et de quoi fouiller.

    ⚠️ L'ETAGE est la nuance des plex : un batiment de N etages contient N
    pieces de son EMPREINTE, jamais UNE piece N fois plus grande. Celle du haut
    a donc les memes mesures que celle du bas, d'autres coins (on y dort), et un
    escalier qui redescend — sans quoi on serait pris en haut.
    """
    grille = [[" "] * largeur for _ in range(hauteur)]
    #: ⚠️ La derniere rangee reste LIBRE : c'est celle ou l'on entre, et un
    #: meuble devant la porte se lit comme une piece ou l'on ne rentre pas.
    coins = [(x, y) for y in range(0, hauteur - 1, COIN_H)
             for x in range(0, largeur, COIN_L)]
    for x0, y0 in coins:
        # ⚠️ Le rang tient compte de la RANGEE de coins, sinon un logement large
        # de vingt tuiles montre quatre fois la meme colonne de meubles : le pas
        # des coins et la longueur du cycle tombent juste, et ca se voit.
        k = x0 // COIN_L + 2 * (y0 // COIN_H)
        # ⚠️ LE PREMIER COIN EST TOUJOURS LE LIT. Sans ca, un logement d'une
        # seule piece tirait « la table » et on entrait chez quelqu'un qui n'a
        # pas de lit — c'est la premiere chose qu'on regarde en poussant la
        # porte d'un appartement. La variante ne fait tourner que la SUITE.
        rang = "lit" if k == 0 else COINS_DE_LOGEMENT[(k + variante) % len(COINS_DE_LOGEMENT)]
        if haut:
            # En haut, on dort : un lit un coin sur deux.
            rang = "lit" if k % 2 == 0 else COINS_DE_LOGEMENT[(k // 2 + 1) % len(COINS_DE_LOGEMENT)]
        _meubler_le_coin(grille, x0, y0, rang)
    for x in (largeur - 1, 0):
        if _libre(grille, x, hauteur - 1) and abs(x + 1 - porte) >= 2:
            grille[hauteur - 1][x] = "n"
            break
    points = []
    if etage:
        # ⚠️ L'escalier prend une tuile LIBRE, jamais un coin de bloc (un lit a
        # qui l'on enleve un coin n'est plus un lit), et jamais a portee de la
        # sortie — il volerait ACTION a la porte. Dans une cabane de trois sur
        # trois il n'y a pas de place pour les deux : la piece n'a alors PAS
        # d'etage, et c'est `poser_la_piece` qui s'en apercoit.
        marches = [(x, y) for y in range(hauteur - 1) for x in range(largeur)
                   if _libre(grille, x, y)
                   and math.hypot(x - (porte - 1), y - (hauteur - 1)) >= RAYON_POINT]
        if marches:
            marche = max(marches, key=lambda t: math.hypot(t[0] - (porte - 1),
                                                           t[1] - (hauteur - 1)))
            grille[marche[1]][marche[0]] = "/"
            points.append(_pt("escalier", marche[0] + 1, marche[1] + 1, vers=etage))
    fouille = [(x, y) for y in range(hauteur) for x in range(largeur)
               if grille[y][x] in ("l", "k", "e", "j", "z")]
    points.append(_poser_le_point(grille, "fouiller", None, porte, fouille,
                                  garder=tuple((p["x"] - 1, p["y"] - 1) for p in points)))
    # ⚠️ Deux points ne se marchent pas dessus : `pointSousLaMain` prend le plus
    # proche dans une tuile et demie, et l'un des deux serait injoignable.
    if len(points) == 2 and max(abs(points[0]["x"] - points[1]["x"]),
                                abs(points[0]["y"] - points[1]["y"])) < 2:
        points.pop()
    _completer_les_meubles(grille, porte, "jznk",
                           tuple((p["x"] - 1, p["y"] - 1) for p in points))
    gens = []
    if not haut and largeur * hauteur >= 24:
        gens.append(_quelqu_un(grille, "client", (largeur // 2, 1), porte, set()))
    nom = "Un logement, en haut" if haut else "Un logement"
    return _piece(slug, nom, _plan_de(grille, porte), sol="t", porte="maison",
                  points=tuple(points), gens=_gens(*[g for g in gens if g]))


def exporter() -> dict:
    carte = generer()
    carte["legende"] = LEGENDE
    # ⚠️ L'ORDRE D'UNE TABLE VOYAGE EN CLAIR (`rang`). Le paquet trie ses cles
    # (`definitions._json`) : une legende « dans l'ordre de la table » s'affichait
    # dans l'ordre ALPHABETIQUE — MAGASINS, MANGER, REPERES — et le juge ne le
    # voyait pas, parce qu'il relisait la table dans ce meme paquet trie.
    carte["familles"] = {nom: {**fiche, "rang": i} for i, (nom, fiche) in enumerate(FAMILLES_DE_LIEU.items())}
    carte["zonage"] = {nom: {**fiche, "rang": i} for i, (nom, fiche) in enumerate(USAGES.items())}
    return carte


# --- Outils de verification (les juges des tests) ---------------------------


def direction_voie(carte: dict, x: int, y: int) -> tuple[int, int] | None:
    """Le sens impose a cette tuile, ou None (croisement ou hors route)."""
    fleche = carte["voie"][y][x]
    if fleche in PAS:
        return PAS[fleche]
    if fleche == "S":
        return PAS.get(carte["arrets"].get(f"{x},{y}", ""))
    return None


def suivre_voie(carte: dict, x: int, y: int) -> list[tuple[int, int]]:
    """Les tuiles ou peut aller un vehicule qui respecte les fleches.

    Sur une voie : la tuile suivante. Sur un croisement : les quatre voisines
    routieres, SAUF celles qui pointent vers nous (on n'entre pas a contresens).
    """
    voie = carte["voie"]
    hauteur, largeur = len(voie), len(voie[0])
    if voie[y][x] == ".":
        return []
    pas = direction_voie(carte, x, y)
    if pas:
        candidats = [(x + pas[0], y + pas[1])]
    else:
        candidats = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    sorties = []
    for cx, cy in candidats:
        if not (0 <= cx < largeur and 0 <= cy < hauteur) or voie[cy][cx] == ".":
            continue
        if pas is None:
            voisine = direction_voie(carte, cx, cy)
            if voisine and (cx + voisine[0], cy + voisine[1]) == (x, y):
                continue
        sorties.append((cx, cy))
    return sorties


def tuiles_voie(carte: dict) -> list[tuple[int, int]]:
    return [(x, y) for y, ligne in enumerate(carte["voie"])
            for x, fleche in enumerate(ligne) if fleche != "."]


def voies_bloquees(carte: dict) -> tuple[set, set]:
    """(tuiles qu'on ne peut pas atteindre, tuiles d'ou l'on ne revient pas).

    Les deux ensembles vides = les rues sont FORTEMENT connexes : depuis
    n'importe quelle tuile de rue on rejoint n'importe quelle autre. Un sens
    interdit pose a l'envers, une bretelle sans sortie, un croisement muet :
    tout cela se voit ici avant de se voir a l'ecran.
    """
    toutes = tuiles_voie(carte)
    if not toutes:
        return set(), set()
    depart = toutes[0]
    avant: dict[tuple[int, int], list] = {}
    arriere: dict[tuple[int, int], list] = {}
    for tuile in toutes:
        avant[tuile] = suivre_voie(carte, *tuile)
    for tuile, sorties in avant.items():
        for sortie in sorties:
            arriere.setdefault(sortie, []).append(tuile)

    def parcourir(graphe):
        vues = {depart}
        pile = [depart]
        while pile:
            courant = pile.pop()
            for voisin in graphe.get(courant, ()):
                if voisin not in vues:
                    vues.add(voisin)
                    pile.append(voisin)
        return vues

    ensemble = set(toutes)
    return ensemble - parcourir(avant), ensemble - parcourir(arriere)
