"""La carte de Baie-des-Brumes — un plan de blocs, des gabarits, un generateur.

Le Faubourg n'est pas dessine tuile par tuile : il est DECRIT par un plan de
blocs et rebati par `generer(plan, graine)`. Six lignes qu'on relit d'un coup
d'oeil valent mieux que 112 lignes de 157 glyphes.

    minuscule = quartier ordinaire   c commerces · h habitations · g gang
                                     p parc · o place · q quai · ~ eau
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

import math

from . import devantures as devantures_mod
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

#: Solidite : 0 libre, 1 mur (bloque tout), 2 eau (bloque sauf les bateaux),
#: 3 basse (bloque les vehicules, pas les pietons).
LEGENDE: dict[str, dict] = {
    ".": {"nom": "trottoir", "trottoir": True},
    ",": {"nom": "herbe", "herbe": True},
    "x": {"nom": "ruelle", "ruelle": True},
    "s": {"nom": "sable"},
    "Q": {"nom": "quai"},
    "~": {"nom": "eau", "solide": 2},
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
    "b": {"nom": "borne-fontaine", "solide": 3},
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
}

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
DISTRICTS: tuple[dict, ...] = (
    # Le Faubourg — le quartier de la v1, intact. Trame serree, blocs courts,
    # la cour des Cravates au centre. C'est ici qu'on debarque de l'autobus.
    {"slug": "faubourg", "nom": "Le Faubourg", "bx": 5, "by": 0,
     "gang": "cravates", "gang_nom": "Les Cravates", "brume": True,
     "pietons": 26, "vehicules": 12, "police": 2, "rythme": (0.35, 1.0, 1.0),
     "rares": ("sport", "luxe"),
     "plan": ("Tccchhhh",
              "cMck<hAh",
              "ccGKohhh",
              "PcBcg<hh",
              "cCcc^^hH",
              "~~qqcccc")},
    # Les Erables — la banlieue. Colonnes larges, maisons detachees sur grandes
    # parcelles, deux parcs, un depanneur, et les Chevreuils qui tournent en
    # char le soir faute de mieux.
    {"slug": "erables", "nom": "Les Érables", "bx": 0, "by": 0,
     "gang": "chevreuils", "gang_nom": "Les Chevreuils", "brume": False,
     "pietons": 14, "vehicules": 7, "police": 1, "rythme": (0.25, 1.1, 0.9),
     "rares": ("luxe",),
     "plan": ("mmmpm",
              "m<m^m",
              "Dmmmm",
              "mm<mm",
              "ccgmm",
              "mmm<m")},
    # La Shop — l'industriel. Des blocs de 2 x 2 partout : presque pas de rues,
    # des entrepots gros comme un pate de maisons, des stationnements vides.
    # Deserte la nuit, et c'est exactement ce qui la rend inquietante.
    {"slug": "shop", "nom": "La Shop", "bx": 13, "by": 0,
     "gang": "boulonneux", "gang_nom": "Les Boulonneux", "brume": False,
     "pietons": 11, "vehicules": 9, "police": 1, "rythme": (0.15, 1.3, 0.6),
     "rares": (),
     "plan": ("U<i<i<p",
              "^<^<^<^",
              "i<g<i<i",
              "^<^<^<^",
              "i<Y<i<c",
              "^<^<^<^")},
    # Les Quais — le port. Blocs LONGS d'est en ouest (des hangars de trois
    # blocs de large), une rangee de quais, l'eau au sud. Ca grouille au matin,
    # ca se vide a la noirceur — sauf la Brume.
    {"slug": "quais", "nom": "Les Quais", "bx": 0, "by": 6,
     "gang": "morues", "gang_nom": "Les Morues", "brume": True,
     "pietons": 20, "vehicules": 8, "police": 1, "rythme": (0.4, 1.4, 0.9),
     "rares": (),
     "plan": ("cc<c<<c",
              "w<<w<<c",
              "L<g<w<c",
              "w<<N<<c",
              "q<<q<<q",
              "~<<~<<~")},
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
              "^<<<<<<")},
    # La Pointe — le parc au bout de la ville. Un chenal la coupe du reste :
    # UN pont, et rien d'autre. Des bois, des sentiers, un phare, quatre
    # maisons au bout, et les Skateux qui tiennent le stationnement.
    {"slug": "pointe", "nom": "La Pointe", "bx": 14, "by": 6,
     "gang": "skateux", "gang_nom": "Les Skateux", "brume": False,
     "pietons": 12, "vehicules": 4, "police": 1, "rythme": (0.2, 0.9, 1.2),
     "rares": ("sport",),
     "plan": ("~<<<<<",
              "n<<<nc",
              "^<<<^c",
              "n<<<^V",
              "^<<<^g",
              "~<<~<<")},
)

#: ⚠️ Aucune colonne n'a la largeur de sa voisine, aucune rangee la hauteur de
#: la sienne : c'est la premiere source d'irregularite, et la moins chere. Les
#: largeurs sont groupees par district — la banlieue et le port ont des blocs
#: larges, le Faubourg les siens (inchanges), l'industriel les plus gros.
COLONNES = (16, 13, 18, 14, 17,              # Les Érables / Les Quais
            13, 9, 12, 16, 10, 14, 9, 12,    # Le Faubourg (v1, intact)
            17, 13, 19, 14, 12, 16, 13)      # La Shop / La Pointe
RANGEES = (9, 12, 8, 11, 9, 13,              # la bande nord
           11, 12, 9, 11, 8, 10)             # la bande sud

#: La largeur de chaque rue, trottoirs compris. 8 = boulevard (4 voies),
#: 6 = rue (2 voies). Il y a une rue de plus que de blocs dans chaque sens.
RUES_V = (8, 6, 6, 8, 6,
          8, 6, 8, 6, 6, 8, 6, 6, 8,
          6, 8, 6, 6, 8, 6, 8)
RUES_H = (8, 6, 8, 6, 8, 6, 8,
          6, 8, 6, 6, 6, 8)

TROTTOIR = 2
GRAINE = 20260912

#: Les ponts : les seules rues qu'on construit PAR-DESSUS l'eau. Un pont est
#: un segment de rue ("v" verticale ou "h" horizontale) designe par sa rue et
#: la rangee (ou la colonne) qu'il longe — ici le seul lien vers La Pointe.
PONTS: frozenset = frozenset({("v", 17, 6)})

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
}

FUSIONS = {"<": (-1, 0), "^": (0, -1)}

#: Les glyphes de plan qui sont de l'eau — une rue dont TOUS les blocs voisins
#: sont de l'eau est noyee : elle n'est pas batie, et personne n'y roule.
EAUX = "~"


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


class _Chantier:
    """L'echafaudage : la trame, puis les rues, puis les ilots, puis le decor."""

    def __init__(self, plan: tuple[str, ...], graine: int) -> None:
        self.plan = plan
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

        self.sol = [[","] * self.largeur for _ in range(self.hauteur)]
        self.voie = [["."] * self.largeur for _ in range(self.hauteur)]
        #: De quoi boucher une poche injoignable, par tuile (voir boucher_les_poches).
        self.bouchon = [["B"] * self.largeur for _ in range(self.hauteur)]
        self.des = Des(graine)
        self.portes: list[dict] = []
        self.points: list[dict] = []
        self.decor: list[dict] = []
        self.fourriere: dict | None = None
        #: L'empreinte du dernier batiment pose (voir `_pose_batiment`).
        self.empreinte_du_batiment = 0
        #: Les pieces qui ont deja une porte quelque part (voir
        #: `premiere_du_genre`) : c'est ce qui garantit qu'aucune famille de
        #: commerce ne reste une enseigne sans interieur.
        self.genres_ouverts: set[str] = set()
        self.lampes: list[dict] = []
        self.intersections: list[dict] = []
        self.arrets: dict[str, str] = {}
        self.reserve: set[tuple[int, int]] = set()
        self.occupe: set[tuple[int, int]] = set()
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

    def poser_porte(self, facades: list[tuple[int, int]], special: dict | None = None,
                    proba: float = 0.65, visite: dict | None = None) -> tuple[int, int] | None:
        """Une porte sur la facade la plus au sud QUI DONNE SUR DU MARCHABLE.

        ⚠️ A appeler apres avoir pose TOUS les batiments de l'ilot : une facade
        peut se retrouver nez a nez avec le toit du voisin, et une porte qui
        ouvre sur un mur est une promesse qu'on ne tient pas.
        """
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
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
            self.portes.append({"x": px, "y": py, "interieur": special["interieur"],
                                "lieu": special["slug"]})
            # ⚠️ La FAMILLE voyage avec le point : c'est elle qui donne sa
            # couleur au blip et sa ligne a la legende de la carte. Un lieu sans
            # famille n'est pas une couleur par defaut, c'est un test rouge.
            self.points.append({"type": special["slug"], "slug": special["slug"],
                                "nom": special["nom"], "x": px, "y": py + 1,
                                "famille": special["famille"]})
            if special.get("porte_garage") and (px - 2, py) in facades:
                self.sol[py][px - 2] = "G"
        else:
            # ⚠️ Le de se tire TOUJOURS, meme quand la porte s'ouvre pour de
            # vrai : c'est le de COMMUN (celui qui pose les murs). S'il ne
            # tombait que dans une branche, decider qu'un commerce se visite —
            # decision prise avec le de des devantures — decalerait toute la
            # suite du hasard et deplacerait des batiments a l'autre bout de la
            # ville. Une couche peinte ne bouge pas un mur : c'est la meme
            # regle qu'en haut du fichier, et c'est ici qu'elle se joue.
            condamnee = self.des.chance(proba)
            if visite:
                # Une porte ordinaire qui s'ouvre : pas de point d'interet (ce
                # sont les reperes de la ville, et quarante de plus n'en
                # seraient plus), mais un `lieu` UNIQUE — c'est lui qui
                # distingue deux tabagies, et par lui qu'on se souvient d'avoir
                # deja fouille ce logement-la. Le `nom` voyage sur la porte : la
                # piece est partagee, l'enseigne au-dessus ne l'est pas.
                self.visites += 1
                self.sol[py][px] = "D"
                self.portes.append({"x": px, "y": py, "interieur": visite["interieur"],
                                    "lieu": f"{visite['slug']}_{self.visites}",
                                    "nom": visite["nom"]})
            elif condamnee:
                self.sol[py][px] = "d"
            else:
                return None
        for j in (1, 2):
            self.reserve.add((px, py + j))
        return px, py

    # --- Les devantures ------------------------------------------------------

    #: Quatre tuiles par defaut (64 px, seize lettres) ; cinq seulement pour
    #: faire tenir un nom long. Au-dela, l'enseigne avale la facade du voisin
    #: et deux commerces mitoyens n'en font plus qu'un.
    ENSEIGNE_MAX = 4
    ENSEIGNE_ETIREE = 5
    ENSEIGNE_MIN = 2

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
        for k in range(len(catalogue)):
            texte, famille = catalogue[(depart + k) % len(catalogue)]
            if all(max(abs(px - x), abs(py - y)) >= devantures_mod.DISTANCE_DOUBLON
                   for px, py in self.enseignes_posees.get(texte, ())):
                return texte, famille
        return catalogue[depart]

    def poser_devanture(self, facades: list[tuple[int, int]], ancre: tuple[int, int],
                        genre: str, special: dict | None = None,
                        enseigne: tuple[str, str] | None = None) -> bool:
        """Un bandeau, un nom, des vitrines et une pancarte. Rend True si pose.

        ⚠️ Les tuiles du bandeau deviennent des VITRINES (`W`) : meme solidite
        que la facade, mais elles portent une lampe — une rue commercante
        s'allume la nuit, et c'est ce qui la distingue d'une rue d'entrepots.
        """
        ax, ay = ancre
        ensemble = set(facades)
        depart, dispo = self._bande_de_facade(ensemble, ax, ay)
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
                        genre: str) -> bool:
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
        depart, dispo = self._bande_de_facade(ensemble, ax, ay)
        if dispo < 2:
            return False
        large = min(4, dispo)
        x0 = min(max(ax - large // 2, depart), depart + dispo - large)
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
                    continue
                texte = possibles[self.des_devanture.entier(0, len(possibles) - 1)]
                self.graffitis.append({
                    "x": x, "y": y,
                    "motif": devantures_mod.MOTIFS[self.des_devanture.entier(0, len(devantures_mod.MOTIFS) - 1)],
                    "couleur": self.des_devanture.entier(0, len(devantures_mod.COULEURS_TAG) - 1),
                    "texte": texte,
                    "penche": self.des_devanture.entier(0, 1),
                })
                self.murs_tagges.add((x, y))

    def _ancre_devanture(self, facades: list[tuple[int, int]]) -> tuple[int, int] | None:
        """Ou irait la porte si ce batiment en avait une : le milieu de sa
        facade la plus au sud qui donne sur du marchable."""
        candidats = [(tx, ty) for tx, ty in facades if self.marchable_en(tx, ty + 1)]
        if not candidats:
            return None
        bas = max(ty for _, ty in candidats)
        rangee = sorted(c for c in candidats if c[1] == bas)
        return rangee[len(rangee) // 2]

    def poser_cloture(self, x: int, y: int, glyphe: str) -> bool:
        """Une tuile de cloture — sauf devant une facade ou un devant de porte.

        ⚠️ Une porte se pose sur la facade SUD d'un batiment et exige du
        marchable devant elle. Une cloture peinte la (une cour arriere qui touche
        le mur du voisin) fait rater `poser_porte` : le batiment perd sa porte,
        son enseigne et son commerce, et personne ne le voit avant de chercher
        une boutique qui n'existe plus.
        """
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        if (x, y) in self.reserve or (y > 0 and solidite(self.sol[y - 1][x]) == 1):
            return False
        self.sol[y][x] = glyphe
        return True

    def poser_decor(self, type_: str, x: int, y: int) -> bool:
        """Du decor seulement sur une tuile libre, hors route et hors devant de porte."""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        if (x, y) in self.reserve or (x, y) in self.occupe:
            return False
        proprietes = LEGENDE[self.sol[y][x]]
        if proprietes.get("solide") or proprietes.get("route"):
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

    def ilots(self) -> None:
        kiosque_pose = False
        for glyphe, x, y, largeur, hauteur in self.regions():
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
            elif glyphe == "o":
                self._place(x, y, largeur, hauteur)
            elif glyphe == "q":
                self._quai(x, y, largeur, hauteur)
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
        for k, (by, bh) in enumerate(bandes):
            self.rect(x, by, largeur, 2, "x")                      # ruelle derriere
            self.rect(x, by + bh - 2, largeur, 2, devant)           # devant
            zy, zh = by + 2, bh - 4
            if zh < 3:
                continue
            self.rect(x, zy, largeur, zh, "," if genre in ("maisons", "banlieue") else ".")
            if k == bande_vedette:
                besoin = plancher_de_la_suite(special["interieur"])
                large = min(largeur, max(3, -(-besoin // zh)))
                vedette = len(parcelles)
                parcelles.append(((x, zy, large, zh), True))
                # ⚠️ Et le reste de la bande fait UN SEUL batiment, pas une
                # rangee de petits. Le decoupage recursif, lui, laissait entre
                # ses parcelles des cours de deux tuiles que le lieu garanti —
                # qui n'a plus de marge — refermait : quarante-six tuiles
                # enclavees a murer sur une graine, quatre sur celle qu'on
                # livre. Une parcelle, un voisin, pas de cour fermee.
                if largeur - large >= mini:
                    parcelles.append(((x + large, zy, largeur - large, zh), True))
                continue
            for parcelle in self._parcelles(x, zy, largeur, zh, mini):
                parcelles.append((parcelle, parcelle[1] + parcelle[3] >= zy + zh))
            if genre == "gang":
                # Une cour cloturee, avec une entree pour les chars.
                # ⚠️ Du BARBELE : c'est la cour d'un gang, quelqu'un a paye pour
                # que personne n'entre. On y passe par l'entree des chars, pas
                # par-dessus — et cette entree est ce qui garantit que la cour
                # n'est jamais une poche fermee (juge : un seul ilot marchable).
                ouverture = self.des.entier(2, max(3, largeur - 7))
                for i in range(largeur):
                    if not ouverture <= i < ouverture + 5 and self.des.chance(0.8):
                        self.sol[by + bh - 1][x + i] = BARBELE
                for _ in range(3):
                    self.poser_decor("caisse", x + self.des.entier(0, largeur - 1),
                                     by + self.des.entier(0, 1))

        contenus = [self._contenu(genre) for _ in parcelles]
        # ⚠️ « Les Skateux tiennent le stationnement » (voir DISTRICTS) — sauf
        # que La Pointe n'en avait pas UNE tuile : la phrase etait une legende.
        # Leur bloc en porte donc un pour de bon, et c'est la que se pose leur
        # tremplin (`_tremplin_de_stationnement`).
        if genre == "gang" and parcelles and self.district_en(x, y) == "pointe":
            contenus[max(range(len(parcelles)),
                         key=lambda k: parcelles[k][0][2] * parcelles[k][0][3])] = "stationnement"
        if special and parcelles and vedette < 0:
            # ⚠️ Le batiment garanti ne peut pas dependre d'un tirage : sans
            # cette ligne, un ilot de neuf tuiles tire « terrain vague » et
            # l'armurerie n'existe pas. Il prend la plus grosse parcelle qui
            # donne sur la rue, et elle est batie quoi qu'il arrive.
            vedette = max(range(len(parcelles)),
                          key=lambda k: (parcelles[k][1], parcelles[k][0][2] * parcelles[k][0][3]))
        if vedette >= 0:
            contenus[vedette] = "bati"

        batiments: list[tuple[list, bool, int]] = []
        facades_vedette = None
        for k, ((px, py, pl, ph), devant_rue) in enumerate(parcelles):
            contenu = contenus[k]
            if contenu == "bati":
                facades = self._pose_batiment(px, py, pl, ph, genre, force=(k == vedette))
                empreinte = self.empreinte_du_batiment
                if facades and k == vedette:
                    facades_vedette = facades
                elif facades:
                    batiments.append((facades, devant_rue, empreinte))
            elif contenu == "vague":
                self._terrain_vague(px, py, pl, ph)
            elif contenu == "stationnement":
                self._stationnement(px, py, pl, ph, genre)
            else:
                self._jardin(px, py, pl, ph, genre)
        if facades_vedette:
            porte = self.poser_porte(facades_vedette, special)
            if porte:
                self.poser_devanture(facades_vedette, porte, genre, special)
        for facades, _, empreinte in batiments:
            ancre = self._ancre_devanture(facades)
            quoi, enseigne = self._a_quoi_sert(genre, ancre)
            visite = None
            # ⚠️ La piece se choisit A LA TAILLE DU BATIMENT : la plus grande
            # qui tienne dans son empreinte, et RIEN du tout si meme la petite
            # deborde — la porte reste alors condamnee. Les deux cotes ne se
            # parlaient pas : un bungalow de neuf tuiles ouvrait sur un
            # seize-par-neuf, seize fois sa surface. Le joueur, lui, compare a
            # chaque porte.
            if quoi == "commerce" and enseigne:
                ouvre = self.des_devanture.chance(self.PART_COMMERCE_VISITABLE)
                dedans = interieur_qui_tient(BOUTIQUES_PAR_TAILLE[enseigne[1]], empreinte)
                if self.premiere_du_genre(dedans):
                    ouvre = True
                if ouvre and dedans:
                    visite = {"slug": enseigne[1], "nom": enseigne[0], "interieur": dedans}
            elif quoi == "logement":
                ouvre = self.des_devanture.chance(self.PART_LOGEMENT_VISITABLE)
                dedans = interieur_qui_tient(LOGEMENTS_PAR_TAILLE, empreinte)
                if self.premiere_du_genre(dedans):
                    ouvre = True
                if ouvre and dedans:
                    visite = {"slug": "logement", "nom": "LOGEMENT", "interieur": dedans}
            porte = self.poser_porte(facades, visite=visite)
            ancre = porte or ancre
            if not ancre:
                continue
            # ⚠️ Une devanture ne suit pas la porte : un commerce a pignon sur
            # rue qu'on ne peut pas visiter reste un commerce, et une rue ou
            # seuls les trois batiments visitables ont une enseigne n'a l'air
            # d'une rue commercante nulle part.
            if quoi == "commerce":
                self.poser_devanture(facades, ancre, genre, enseigne=enseigne)
            elif quoi == "logement":
                self.poser_residence(facades, ancre, genre)
        for _ in range(max(1, largeur // 10)):
            self.poser_decor("poubelle", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, 1))

    def premiere_du_genre(self, interieur: str | None) -> bool:
        """Cette piece-la n'a encore ouvert NULLE PART : alors celle-ci ouvre.

        ⚠️ Sans cette regle, une famille de commerce peut n'ouvrir aucune porte
        de toute la ville : il faut qu'un batiment tire cette enseigne-la, qu'il
        soit assez grand pour la piece, ET qu'il gagne le de — trois chances qui
        se multiplient, et quatre familles sur dix restaient des couleurs
        d'enseigne qui ne menent jamais a rien. Le de decide du NOMBRE de portes
        qui s'ouvrent ; il n'a pas a decider qu'un pan entier de la ville
        n'existe pas. La premiere qui peut, ouvre.
        """
        if not interieur or interieur in self.genres_ouverts:
            return False
        self.genres_ouverts.add(interieur)
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
        tirage = self.des.flottant()
        if genre == "maisons":
            return "bati" if tirage < 0.74 else ("jardin" if tirage < 0.92 else "stationnement")
        if genre == "banlieue":
            return "bati" if tirage < 0.72 else ("jardin" if tirage < 0.94 else "stationnement")
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
        vitrines = {"commerces": 0.5, "maisons": 0.12, "banlieue": 0.10,
                    "hangars": 0.03, "industriel": 0.05, "gang": 0.08}.get(genre, 0.3)
        if force:
            # Un batiment garanti garde sa masse : ni cour ni coin mordu.
            tuiles = {(bx + i, by + j) for j in range(bh) for i in range(bl)}
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

    def _terrain_vague(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.rect(x, y, largeur, hauteur, ",")
        # ⚠️ Les cours de La Shop sont BARBELEES : de la ferraille derriere une
        # cloture qu'on enjambe, ca ne dit rien ; derriere du barbele, ca dit
        # « quelqu'un a paye pour que personne n'entre ». Ailleurs, c'est du
        # grillage — un terrain vague de quartier, on y passe.
        # ⚠️ Et le barbele laisse TOUJOURS une trouee : la cloture n'est qu'a
        # demi peinte (une tuile sur deux), mais « a demi » n'est pas un juge.
        # Sans trouee garantie, un terrain vague ferme devient une poche que
        # `boucher_les_poches` mure — et la ferraille disparait sans un mot.
        cloture = BARBELE if self.district_en(x, y) == "shop" else GRILLAGE
        troue = self.des_cloture.entier(0, max(0, largeur - 2))
        for i in range(largeur):
            if i in (troue, troue + 1):
                continue
            if self.des.chance(0.5):
                self.poser_cloture(x + i, y + hauteur - 1, cloture)
        for _ in range(max(1, largeur * hauteur // 12)):
            self.poser_decor("debris", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        # Un tremplin de planches sur les gravats : le terrain vague est
        # l'endroit ou une rampe se raconte toute seule. ⚠️ On COUPE la cloture
        # devant : sinon c'est un tremplin derriere un grillage, et on vient de
        # passer une heure a se debarrasser de ceux-la. Apres les debris, pour
        # ne pas en poser un au milieu de la piste.
        if largeur >= 5 and hauteur >= 4 and self.des_rampe.chance(PART_RAMPE_COUR):
            cx = x + largeur // 2
            self.proposer_rampe([(cx, y + hauteur // 2, None)],
                                cloture=(cx, y + hauteur - 1))

    def _jardin(self, x: int, y: int, largeur: int, hauteur: int,
                genre: str = "commerces") -> None:
        """Du gazon, des arbres — et, chez le monde, une cour arriere cloturee.

        ⚠️ La palissade de bois est la VARIETE que demandait Martin, et c'est
        aussi ce qui fait qu'une banlieue a l'air d'une banlieue vue d'en haut :
        des cours delimitees. Elle s'enjambe comme un grillage (solidite 4), donc
        elle ne peut pas enfermer une poche — on entre dans une cour arriere en
        passant par-dessus, c'est meme tout son interet.

        ⚠️ Une BARRIERE, toujours : un cote de la cour reste ouvert. Sans elle,
        traverser une banlieue a pied deviendrait une suite d'escalades, et le
        prix d'une cloture (une seconde, immobile) se paierait dix fois par rue.

        ⚠️ La BANLIEUE seulement (Les Erables), pas les quartiers de maisons du
        Faubourg. Mesure a l'appui : en cloturant les deux, 274 tuiles de
        palissade tombaient au milieu du vieux quartier — le carre ou l'on
        commence la partie devenait un labyrinthe de cours, et quatre juges de
        banc ne trouvaient plus une tuile libre autour du joueur. Une cour
        arriere cloturee, c'est une image de banlieue ; en ville, c'est une haie
        d'obstacles.

        ⚠️ Jamais devant une facade (`poser_cloture`) : une porte exige du
        marchable devant elle, et une palissade collee au mur du voisin fait
        disparaitre la porte, l'enseigne et le commerce avec elle.
        """
        self.rect(x, y, largeur, hauteur, ",")
        # ⚠️ La barriere s'ouvre sur du MARCHABLE, et s'il n'y en a pas, la cour
        # reste ouverte. Mesure a l'appui : une cour de 3 x 3 dont la seule sortie
        # donnait sur le mur du voisin devenait une poche, `boucher_les_poches` la
        # murait — huit tuiles, dont le devant d'une porte, et un commerce du
        # quartier se retrouvait sans entree.
        sorties = [i for i in range(1, largeur - 1) if self.marchable_en(x + i, y + hauteur)]
        if (genre == "banlieue" and largeur >= 3 and hauteur >= 3
                and sorties and self.des_cloture.chance(0.7)):
            barriere = self.des_cloture.choix(sorties)
            for i in range(largeur):
                if i != barriere:
                    self.poser_cloture(x + i, y + hauteur - 1, BOIS)
            for j in range(hauteur - 1):
                self.poser_cloture(x, y + j, BOIS)
                self.poser_cloture(x + largeur - 1, y + j, BOIS)
        for _ in range(max(1, largeur * hauteur // 10)):
            self.poser_decor(self.des.choix(("arbre", "buisson")),
                             x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))

    # --- Les rampes ---------------------------------------------------------

    def _roulable(self, x: int, y: int) -> bool:
        """Une tuile ou un char passe VRAIMENT : rien de solide, pas de decor,
        pas le devant d'une porte.

        ⚠️ Toute solidite non nulle arrete un char — une borne-fontaine (3) comme
        une cloture (4, 5), meme si un pieton passe par-dessus les deux. Une
        cloture dans l'elan, c'est un elan qui n'existe pas : c'est ce qui rendait
        les rampes de la cour des gangs injouables — on les voyait, on ne pouvait
        pas les prendre.
        """
        return (0 <= x < self.largeur and 0 <= y < self.hauteur
                and solidite(self.sol[y][x]) == 0
                and (x, y) not in self.occupe and (x, y) not in self.reserve)

    def _course(self, x: int, y: int, dx: int, dy: int, voulu: int) -> int:
        """Combien de tuiles roulables d'affilee dans cette direction."""
        n = 0
        while n < voulu and self._roulable(x + dx * (n + 1), y + dy * (n + 1)):
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
        pave = "s" if sauvage else "."
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

    def _quai(self, x: int, y: int, largeur: int, hauteur: int) -> None:
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "Q")
        for _ in range(largeur * hauteur // 14):
            self.poser_decor("caisse", x + self.des.entier(0, largeur - 1),
                             y + self.des.entier(0, hauteur - 1))
        # Une rampe de debarquement, la ou un quai en porte vraiment une.
        # ⚠️ L'eau n'est pas roulable : `poser_rampe` ne choisira jamais l'axe
        # qui envoie au fond de la baie, le saut longe le port.
        if largeur >= 10 and hauteur >= 3 and self.des_rampe.chance(PART_RAMPE_VAGUE):
            self.proposer_rampe([(x + largeur // 2, y + hauteur // 2, None)])

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
        """Un bassin a rive irreguliere : du sable qui avance et recule."""
        self.bouchon_rect(x, y, largeur, hauteur, "~")
        self.rect(x, y, largeur, hauteur, "~")
        pas = max(1, largeur // 8)
        nord = self._terre_a_cote([(x + i, y - 1) for i in range(0, largeur, pas)])
        sud = self._terre_a_cote([(x + i, y + hauteur) for i in range(0, largeur, pas)])
        pas = max(1, hauteur // 8)
        ouest = self._terre_a_cote([(x - 1, y + j) for j in range(0, hauteur, pas)])
        est = self._terre_a_cote([(x + largeur, y + j) for j in range(0, hauteur, pas)])
        # ⚠️ La rive ne mange jamais plus du tiers du bassin : sans ce plafond,
        # le sable des deux rives se rejoint au milieu d'un chenal etroit — et
        # La Pointe, qu'un pont devait seul relier, se traverse a pied.
        sable_h = min(4, hauteur // 3)
        sable_v = min(3, largeur // 3)
        profondeur = min(2, sable_h)
        for i in range(largeur):
            profondeur = max(0, min(sable_h, profondeur + self.des.entier(-1, 1)))
            for j in range(profondeur):
                if nord:
                    self.sol[y + j][x + i] = "s"
                if sud:
                    self.sol[y + hauteur - 1 - j][x + i] = "s"
        profondeur = min(2, sable_v)
        for j in range(hauteur):
            profondeur = max(0, min(sable_v, profondeur + self.des.entier(-1, 1)))
            for i in range(profondeur):
                if ouest:
                    self.sol[y + j][x + i] = "s"
                if est:
                    self.sol[y + j][x + largeur - 1 - i] = "s"

    # --- Decor de rue et finitions -----------------------------------------

    #: Ou chercher le trottoir autour d'un coin de croisement : le coin
    #: d'abord, puis ses voisines, les plus proches en premier.
    AUTOUR = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))

    def lampadaires(self) -> None:
        """Deux coins opposes par croisement : de la lumiere ou l'on tourne.

        ⚠️ Un poteau se plante sur un TROTTOIR, jamais sur un parterre. Le coin
        d'un croisement n'en est pas toujours un : devant une maison, la bande
        de devant est en gazon, et devant la fourriere, en asphalte. On cherche
        alors le trottoir a cote. Sans ca, le juge ne tenait que par chance —
        il suffisait qu'un arbre libere le coin pour qu'une lampe pousse dans
        une pelouse.
        """
        for inter in self.intersections:
            for dx, dy in ((-1, -1), (inter["l"], inter["h"])):
                x, y = inter["x"] + dx, inter["y"] + dy
                for ix, iy in self.AUTOUR:
                    cx, cy = x + ix, y + iy
                    if not (0 <= cx < self.largeur and 0 <= cy < self.hauteur):
                        continue
                    if self.sol[cy][cx] != "." or not self.poser_decor("lampadaire", cx, cy):
                        continue
                    self.lampes.append({"x": cx, "y": cy})
                    break

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
                    if glyphe != "." or not marchable(self.sol[y + 1][x]):
                        continue
                    voisins = (self.sol[y][x - 1], self.sol[y][x + 1],
                               self.sol[y - 1][x], self.sol[y + 1][x])
                    if not any(routier(v) for v in voisins):
                        continue
                elif sur == "stationnement":
                    if glyphe != "p" or self.sol[y][x + 1] != "p":
                        continue
                    if not marchable(self.sol[y + 1][x]):
                        continue
                else:  # pragma: no cover - garde-fou de relecture du catalogue
                    raise ValueError(f"support inconnu : {sur!r}")
                places.append((x, y))
        return places

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
        for inter in self.intersections:
            if not self.des.chance(0.30):
                continue
            x, y = inter["x"] + inter["l"], inter["y"] - 1
            if 0 <= x < self.largeur and 0 <= y < self.hauteur and self.sol[y][x] == ".":
                self.sol[y][x] = "b"

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
    ambulants = chantier.ambulants()
    reclames = chantier.reclames(ambulants)
    paquets = chantier.paquets()
    # ⚠️ Apres les ilots ET les ponts : on tague des murs qui existent, et on
    # ne tague pas une vitrine (les devantures ont deja reserve les leurs).
    chantier.graffitis_sur_les_murs()

    terminus = next(p for p in chantier.points if p["slug"] == "terminus")
    depart = (terminus["x"], terminus["y"])
    bouchees = chantier.boucher_les_poches(depart)
    if bouchees > chantier.largeur * chantier.hauteur // 50:
        raise ValueError(f"{bouchees} tuiles enclavees : un gabarit enferme la ville")

    return {
        "slug": "baie_des_brumes",
        "nom": "Baie-des-Brumes",
        "graine": graine,
        "districts": [{"slug": d["slug"], "nom": d["nom"], "gang": d["gang"],
                       "eau": bool(d.get("eau"))} for d in DISTRICTS],
        "largeur": chantier.largeur,
        "hauteur": chantier.hauteur,
        "tuile_px": TUILE_PX,
        "grille": {"colonnes": list(COLONNES), "rangees": list(RANGEES),
                   "rues_v": list(RUES_V), "rues_h": list(RUES_H), "trottoir": TROTTOIR},
        "sol": ["".join(ligne) for ligne in chantier.sol],
        "voie": ["".join(ligne) for ligne in chantier.voie],
        "arrets": chantier.arrets,
        "ponts": ponts,
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
        "ambulants": ambulants,
        "reclames": reclames,
        "paquets": paquets,
        "zones": chantier.zones(),
        "points_interet": chantier.points,
        "toits": chantier.toits,
        "apparition": {"joueur": {"x": depart[0], "y": depart[1]}},
        "interieurs": INTERIEURS,
        "tuiles_bouchees": bouchees,
    }

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
#: ⚠️ Sans eux, une piece meublee reste un musee : c'est le monde qui parle au
#: comptoir qui fait qu'on a l'impression d'etre entre quelque part.
QUI_DEDANS = ("commis", "client")


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
        if solidite(sol[gens["y"]][gens["x"]]) != 0:
            raise ValueError(f"{piece['slug']} : quelqu'un est ne dans un meuble")


#: Les pieces des lieux garantis (`SPECIAUX`) et des donneurs de mission.
_PIECES: tuple[dict, ...] = (
    # Le terminus : c'est ici qu'on debarque au premier matin. Deux rangees de
    # bancs, la consigne derriere le guichet, et un comptoir qui sert le cafe.
    _piece("terminus", "Terminus Baie-des-Brumes", sol="u", plan="""
BBBWWWWWBBB
Bn  kkk  nB
B cccccc  B
B         B
B hhh hhh B
B         B
B hhh hhh B
BBBWWDWWBBB
""", points=(_pt("emplettes", 4, 2, genre="service"),),
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
    _piece("poste", "Poste de police", sol="u", plan="""
BBBWWWWWBBBB
Bkkkk    n B
B     a h  B
B     a h  B
Bcccccc   nB
B          B
B hhhh     B
Bn        nB
BBBBWWDWWBBB
""", points=(_pt("casier", 3, 4),),
     gens=_gens(("commis", 3, 3), ("client", 7, 6))),

    # L'hopital : quatre lits, le carrelage, l'accueil.
    _piece("hopital", "Hôpital de Baie-des-Brumes", sol="u", plan="""
BBBWWWWWBBB
Bll  ll  nB
Bll  ll   B
B         B
B cccccc  B
B         B
B hhh   n B
BBBBWWDWWBB
""", points=(_pt("soigner", 3, 4),),
     gens=_gens(("commis", 3, 3), ("client", 7, 6))),

    # Le Brouillard : le bar, les tables, le billard — et Josee au fond.
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
""", points=(_pt("caisse", 4, 2), _pt("contact", 10, 7)),
     gens=_gens(("commis", 4, 1), ("client", 5, 4), ("client", 8, 5))),

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
)

#: ⚠️ Les commerces ORDINAIRES : une piece par famille de devanture. Sans
#: elles, les cent seize enseignes de la ville etaient des decors — une seule
#: sur sept menait quelque part, et les autres montraient une poignee doree
#: sur un mur plein. `INTERIEUR_DE_GENRE` dit quelle piece ouvre derriere
#: quelle enseigne ; le NOM affiche, lui, est celui de l'enseigne (il voyage
#: sur la porte), et c'est ce qui fait qu'on entre chez « TABAGIE DUBOIS » et
#: pas dans « Boutique ».
_BOUTIQUES: tuple[dict, ...] = (
    _piece("boutique_bouffe", "L'épicerie", plan="""
BBBBBBBBB
Bjjj eeeB
B       B
B eee eeB
B       B
Bcccc  nB
B       B
BBWWDWWBB
""", points=(_pt("emplettes", 2, 5, genre="bouffe"),), gens=_gens(("commis", 2, 4),)),

    _piece("boutique_service", "Le salon", plan="""
BBBWWWWBB
Be     nB
B       B
B hh hh B
B yy yy B
Bcccc   B
B       B
BBWWDWWBB
""", points=(_pt("salon", 2, 4),),
     gens=_gens(("commis", 5, 5), ("client", 4, 3))),

    _piece("boutique_artisan", "L'atelier", plan="""
BBBBBBBBB
BeeeeeeeB
B       B
B ee mm B
B       B
Bccccc nB
B       B
BBBWWDWBB
""", points=(_pt("emplettes", 3, 5, genre="artisan"),), gens=_gens(("commis", 3, 4),)),

    _piece("boutique_nuit", "La taverne", plan="""
BBBBBBBBB
Bj     nB
B ccccc B
B       B
B ah ah B
B ah ah B
B     aaB
BBWWDWWBB
""", points=(_pt("emplettes", 3, 2, genre="nuit"),),
     gens=_gens(("commis", 3, 1), ("client", 4, 4), ("client", 7, 5))),

    _piece("boutique_commerce", "Le magasin", plan="""
BBBWWWWBB
Be e e nB
Be e e  B
B       B
B ccccc B
B       B
Bn     yB
BBWWDWWBB
""", points=(_pt("emplettes", 3, 4, genre="commerce"),), gens=_gens(("commis", 3, 3),)),

    _piece("boutique_marine", "La criée", sol="u", plan="""
BBBBBBBBB
Bjjjj  eB
B       B
Bccccc  B
B       B
B     anB
B     a B
BBWWDWWBB
""", points=(_pt("emplettes", 3, 3, genre="marine"),), gens=_gens(("commis", 3, 2),)),

    _piece("boutique_industrie", "La quincaillerie", sol="u", plan="""
BBBBBBBBB
Bmmm mmeB
Bmmm mm B
B       B
B mmm   B
Bcccc  nB
B       B
BBBWWDWBB
""", points=(_pt("emplettes", 2, 5, genre="industrie"),), gens=_gens(("commis", 1, 4),)),

    _piece("boutique_sante", "La pharmacie", sol="u", plan="""
BBBWWWWBB
BeeeeeenB
B       B
B ee ee B
B       B
B ccccc B
B      nB
BBWWDWWBB
""", points=(_pt("emplettes", 2, 5, genre="sante"),),
     gens=_gens(("commis", 3, 4), ("client", 4, 3))),

    _piece("boutique_mode", "La boutique", plan="""
BBBWWWWBB
Be e e nB
Be e e  B
Be e e  B
B       B
Bcccc yyB
B     yyB
BBWWDWWBB
""", points=(_pt("emplettes", 2, 5, genre="mode"),), gens=_gens(("commis", 3, 4),)),

    _piece("boutique_savoir", "Le kiosque à journaux", plan="""
BBBBBBBBB
BeeeeeeeB
B       B
B eeeee B
B       B
Bcccc ahB
B      nB
BBBWWDWBB
""", points=(_pt("journal", 2, 5),),
     gens=_gens(("commis", 2, 4), ("client", 4, 2))),
)

#: Le logement d'un plex : celui du bas donne sur la rue, celui du haut se
#: gagne par l'escalier. ⚠️ On n'est PAS chez soi : il n'y a rien a acheter
#: ici, seulement des tiroirs a fouiller — et une seule fois par adresse.
_LOGEMENTS: tuple[dict, ...] = (
    _piece("logement", "Un logement", porte="maison", plan="""
BBBWWWWBBB
Bll    j B
Bll      B
B aah   /B
B aah  yyB
Bz    nyyB
BBBWWDWWBB
""", points=(_pt("fouiller", 7, 1), _pt("escalier", 8, 3, vers="logement_haut")),
     gens=_gens(("client", 3, 1),)),

    _piece("logement_haut", "Un logement, en haut", porte="maison", plan="""
BBBWWWWBBB
Bll   ll B
Bll   ll B
B        B
B e a e /B
Bn      nB
BBBBBDBBBB
""", points=(_pt("fouiller", 2, 4), _pt("escalier", 8, 4, vers="logement")),
     gens=()),
)

#: ⚠️ LES PETITES PIECES. Les 41 interieurs de la ville etaient tous autour de
#: 14 x 9, et les batiments qui les portent vont de NEUF tuiles a 252 : un
#: logement de banlieue de 3 x 3 ouvrait sur un 16 x 9, seize fois sa surface.
#: Les deux cotes ne se parlaient pas — `_pose_batiment` tire ses marges au
#: sort, `INTERIEURS` declare des pieces ecrites a la main, et personne ne
#: comparait. Le joueur, lui, compare a chaque porte.
#:
#: Il faut donc des pieces PAR TRANCHE, et la porte prend la plus grande QUI
#: TIENNE (voir `interieur_qui_tient`).
_PETITES: tuple[dict, ...] = (
    # ⚠️ LA PLUS PETITE DE TOUTES, et il en faut une : vingt-sept batiments
    # ordinaires de la ville livree ne font que NEUF tuiles. Sans elle, leurs
    # portes restaient toutes condamnees et la ville perdait un tiers de ses
    # entrees. Trois tuiles sur trois, un lit, un poele : c'est une cabane, et
    # c'est exactement ce qu'on voit du dehors.
    _piece("logement_minuscule", "Une chambre", porte="maison", plan="""
BBWBB
Bl jB
Bl  B
B  zB
BBDBB
""", points=(_pt("fouiller", 1, 1),), gens=()),

    _piece("boutique_minuscule", "Le comptoir", plan="""
BBBBB
Bcc B
B  nB
Be  B
BWDWB
""", points=(_pt("caisse", 1, 1),), gens=_gens(("commis", 2, 2),)),

    # Un logement d'une piece : le lit, le frigo, la table. C'est tout, et
    # c'est ce qu'il y a derriere une porte de bungalow.
    _piece("logement_petit", "Un petit logement", porte="maison", plan="""
BBBWWWBB
Bll   jB
Bll    B
Ba    nB
BBBWDWBB
""", points=(_pt("fouiller", 5, 1),), gens=()),

    # Une boutique d'une allee : un comptoir, une etagere, le commis derriere.
    _piece("boutique_petite", "Le petit commerce", plan="""
BBBBBBBBB
Beeeee  B
B      nB
Bccccc  B
BBBWWDWBB
""", points=(_pt("caisse", 2, 3),), gens=_gens(("commis", 2, 2),)),
)

INTERIEURS: dict[str, dict] = {p["slug"]: p for p in _PIECES + _BOUTIQUES + _LOGEMENTS + _PETITES}


def plancher_de(piece: dict) -> int:
    """Les tuiles ou l'on POSE LE PIED dans cette piece, murs deduits.

    ⚠️ On compare les planchers, pas les boites. Une piece de 15 x 10 a 13 x 8
    tuiles de plancher une fois ses murs deduits ; un batiment de 4 x 3 n'en a
    douze en tout. Comparer les boites, ou pire la PARCELLE, c'est se mentir de
    trois fois la surface : c'est le plancher contre l'empreinte qui dit la
    verite, et c'est lui que le juge mesure.
    """
    return max(0, piece["largeur"] - 2) * max(0, piece["hauteur"] - 2)


def plancher_de_la_suite(slug: str) -> int:
    """Le plus grand plancher de la SUITE — la piece et ses etages.

    ⚠️ Une porte ne donne pas sur une piece, elle donne sur tout ce qu'on peut
    atteindre en la poussant : `logement` a un escalier qui monte vers
    `logement_haut`, et les deux doivent tenir. C'est la nuance des etages :
    un batiment de N etages contient N PIECES DE SON EMPREINTE, jamais UNE
    piece N fois plus grande. C'est le nombre de pieces qui se multiplie, pas
    la surface au sol — alors on prend la PLUS GRANDE de la suite, pas la
    somme.
    """
    vus: set[str] = set()
    a_voir = [slug]
    grand = 0
    while a_voir:
        courant = a_voir.pop()
        if courant in vus or courant not in INTERIEURS:
            continue
        vus.add(courant)
        piece = INTERIEURS[courant]
        grand = max(grand, plancher_de(piece))
        a_voir += [pt["vers"] for pt in piece["points"] if pt.get("vers")]
    return grand


def interieur_qui_tient(slugs: tuple[str, ...], empreinte: int) -> str | None:
    """La plus grande piece de la liste dont la suite tient dans le batiment.

    Rend `None` quand meme la plus petite deborde — et c'est un resultat, pas
    un echec : un bungalow de trois tuiles sur trois garde sa porte, elle ne
    s'ouvre simplement pas (`poser_porte` la condamne). Une porte qui donne sur
    une piece plus grande que la maison est un mensonge ; une porte qu'on ne
    pousse pas n'en est pas un.
    """
    tiennent = [s for s in slugs
                if s in INTERIEURS and plancher_de_la_suite(s) <= empreinte]
    if not tiennent:
        return None
    return max(tiennent, key=plancher_de_la_suite)


#: Derriere quelle enseigne on entre dans quelle piece. ⚠️ Chaque famille de
#: `devantures.GENRES` doit etre ici : un genre oublie, et toutes les portes
#: de cette couleur-la ne menent nulle part (juge dans les tests).
INTERIEUR_DE_GENRE: dict[str, str] = {
    genre["slug"]: f"boutique_{genre['slug']}" for genre in devantures_mod.GENRES
}

#: Les pieces qui ouvrent derriere une enseigne, de la plus petite a la plus
#: grande. ⚠️ La petite est la MEME pour tous les genres, et c'est voulu :
#: l'identite du commerce voyage sur la PORTE (`visite["nom"]`), pas dans les
#: murs. Une boucherie de neuf tuiles reste une boucherie sur son enseigne et
#: dans le carnet ; elle a juste un comptoir au lieu de trois allees. Douze
#: petits plans de plus auraient dit la meme chose douze fois.
BOUTIQUES_PAR_TAILLE: dict[str, tuple[str, ...]] = {
    slug: ("boutique_minuscule", "boutique_petite", grand)
    for slug, grand in INTERIEUR_DE_GENRE.items()
}

#: Les pieces qui ouvrent derriere une porte de residence, de la plus petite a
#: la plus grande. ⚠️ `interieur_qui_tient` prend la plus grande QUI TIENNE
#: dans l'empreinte du batiment — c'est ca, « la porte prend la plus grande qui
#: tienne ».
INTERIEUR_LOGEMENT = "logement"
LOGEMENTS_PAR_TAILLE: tuple[str, ...] = (
    "logement_minuscule", "logement_petit", "logement")


def exporter() -> dict:
    carte = generer()
    carte["legende"] = LEGENDE
    carte["familles"] = FAMILLES_DE_LIEU
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
