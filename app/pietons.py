"""Qui marche dans Baie-des-Brumes — et comment chacun reagit a un coup.

Le navigateur ne connait aucune de ces valeurs : il recoit le catalogue et fait
marcher les gens avec. Les couleurs sont des ECHANGES DE PALETTE sur le sprite
du personnage (`c` chandail, `h` cheveux, `s` peau, `p` pantalon) : un seul
dessin, seize silhouettes.

`courage` decide de tout quand on frappe quelqu'un :
    0,0  il fuit toujours          (la dame, l'ado)
    0,5  il fuit ou il riposte     (l'ouvrier)
    1,0  il fonce                  (la Cravate)

`temoin` est la probabilite qu'il aille RACONTER le crime a un policier au lieu
de seulement fuir — c'est le deuxieme canal de detection de la police (M4).
"""

from __future__ import annotations

from typing import TypedDict


class Pieton(TypedDict):
    slug: str
    nom: str
    sprite: str
    couleurs: dict[str, str]
    vitesse: float
    courage: float
    temoin: float
    vie: int
    argent: tuple[int, int]
    arme: str | None
    gang: str | None
    intouchable: bool
    accompagne: str | None
    metier: str | None
    heures: tuple[float, float] | None
    districts: tuple[str, ...] | None
    frequence: float
    phase: int


def _p(slug, nom, chandail, cheveux, peau, pantalon, *, sprite="joueur", vitesse=1.0,
       courage=0.0, temoin=0.3, vie=60, argent=(2, 20), arme=None, gang=None,
       intouchable=False, accompagne=None, metier=None, heures=None, districts=None,
       frequence=1.0, phase=1) -> Pieton:
    return Pieton(
        slug=slug, nom=nom, sprite=sprite,
        couleurs={"c": chandail, "h": cheveux, "s": peau, "p": pantalon},
        vitesse=vitesse, courage=courage, temoin=temoin, vie=vie, argent=argent,
        arme=arme, gang=gang, intouchable=intouchable, accompagne=accompagne,
        metier=metier, heures=heures, districts=districts,
        frequence=frequence, phase=phase,
    )


#: ⚠️ `frequence` est un POIDS, pas une probabilite : le navigateur tire
#: dedans. La somme n'a pas besoin de faire 1, et ajouter un archetype ne
#: rend donc pas les autres faux.
CATALOGUE: list[Pieton] = [
    _p("passant", "Passant", "#3a6ea5", "#3a2a1a", "#e8b088", "#2a2a3a",
       frequence=3.0, argent=(5, 25)),
    _p("passante", "Passante", "#b2558a", "#5a3a1a", "#f0c098", "#3a3a4a",
       frequence=3.0, argent=(5, 30), temoin=0.45),
    _p("ouvrier", "Ouvrier", "#d98324", "#2a2a2a", "#c98d66", "#3f4a5a",
       courage=0.5, vie=80, vitesse=0.95, frequence=2.0, argent=(10, 40), temoin=0.2),
    _p("ado", "Ado en planche", "#27ae60", "#1a1a1a", "#e8b088", "#4a4a6a",
       vitesse=1.2, frequence=1.5, argent=(2, 12), temoin=0.15),
    _p("dame", "Dame du Faubourg", "#8e44ad", "#c9c9c9", "#f0c098", "#2a2a3a",
       vitesse=0.8, frequence=1.5, argent=(15, 60), temoin=0.6),
    _p("cravate", "Cravate", "#2c3e50", "#1a1a1a", "#e8b088", "#1f2a36",
       courage=0.9, vie=90, vitesse=1.05, argent=(20, 80), arme="batte",
       gang="cravates", frequence=0.0, temoin=0.0),
    # v2 / M8 — les quatre gangs des nouveaux districts. Meme regle que les
    # Cravates : frequence 0, ils ne naissent QUE sur leur territoire.
    _p("morue", "Une Morue", "#1d6f6f", "#3a2a1a", "#c98d66", "#2a3540",
       courage=0.85, vie=95, vitesse=0.95, argent=(15, 70), arme="batte",
       gang="morues", frequence=0.0, temoin=0.0),
    _p("chevreuil", "Un Chevreuil", "#8a5a2b", "#4a3320", "#e8b088", "#3a2f22",
       courage=0.7, vie=80, vitesse=1.1, argent=(20, 90), arme="batte",
       gang="chevreuils", frequence=0.0, temoin=0.0),
    _p("boulonneux", "Un Boulonneux", "#5a5f66", "#2a2a2a", "#c98d66", "#2f3338",
       courage=0.95, vie=105, vitesse=0.9, argent=(10, 55), arme="batte",
       gang="boulonneux", frequence=0.0, temoin=0.0),
    _p("skateux", "Un Skateux", "#9b3fa8", "#1a1a1a", "#e8b088", "#2a2a3a",
       courage=0.55, vie=70, vitesse=1.3, argent=(5, 40), arme=None,
       gang="skateux", frequence=0.0, temoin=0.0),
    # ⚠️ Les passants de quartier : `districts` les ENFERME chez eux. Un
    # debardeur aux Erables, un banlieusard sur les quais, et les cinq
    # quartiers redeviennent le meme quartier repeint.
    _p("docker", "Débardeur", "#c8842a", "#2a2a2a", "#c98d66", "#38404a",
       courage=0.6, vie=90, vitesse=0.95, argent=(15, 55), temoin=0.15,
       districts=("quais",), frequence=2.4),
    _p("banlieusard", "Banlieusard", "#7f9a4e", "#5a3a1a", "#f0c098", "#454f38",
       courage=0.2, vie=65, vitesse=0.9, argent=(20, 80), temoin=0.65,
       districts=("erables",), frequence=2.4),
    _p("machiniste", "Machiniste", "#4a5a75", "#1a1a1a", "#c98d66", "#2a3240",
       courage=0.55, vie=85, vitesse=0.95, argent=(12, 50), temoin=0.2,
       districts=("shop",), frequence=2.2),
    _p("promeneur", "Promeneur de chien", "#2f8f6a", "#6b4b2c", "#e8b088", "#3a3a4a",
       courage=0.1, vie=60, vitesse=0.85, argent=(10, 45), temoin=0.55,
       districts=("pointe",), frequence=2.2),
    _p("itinerant", "Itinérant", "#6b5a48", "#6b5a48", "#c98d66", "#4a4438",
       vitesse=0.75, courage=0.2, frequence=1.0, argent=(1, 8), temoin=0.1),
    _p("livreur", "Livreur", "#c0392b", "#3a2a1a", "#c98d66", "#2a2a3a",
       vitesse=1.1, courage=0.3, vie=70, frequence=1.2, argent=(10, 35), temoin=0.25),
    # ⚠️ L'ENFANT EST INTOUCHABLE. Le jeu est adulte : on y meurt, le sang
    # coule. Un enfant, non — aucune arme ne l'atteint, aucun char ne le
    # renverse, il detale bien avant. C'est une regle du moteur
    # (`intouchable`), pas une consigne qu'on peut oublier de suivre.
    _p("enfant", "Enfant", "#f1c40f", "#6b4b2c", "#f0c098", "#2f6b8a", sprite="enfant",
       vitesse=1.15, vie=40, argent=(0, 3), temoin=0.5, intouchable=True,
       frequence=1.2),
    _p("mere", "Mère avec son petit", "#16a085", "#4a3320", "#f0c098", "#3a3a4a",
       vitesse=0.85, vie=65, argent=(10, 45), temoin=0.7, accompagne="enfant",
       frequence=1.4),
    # La Brume, la nuit : elles travaillent pres du bar et du port. Elles
    # vendent de la COMPAGNIE (voir economie.TARIFS) et rien ne se montre.
    # ⚠️ SEUL ARCHETYPE A AVOIR SON PROPRE SPRITE (`racoleuse` dans
    # sprites.js) : sur le corps commun elle n'etait qu'un chandail rose de
    # plus, et on ne la reconnaissait plus dans la foule (retour de Martin).
    # Une couleur ne distingue pas a douze pixels de large — un contour, oui.
    # Ses couleurs ne se croisent nulle part ailleurs dans le catalogue :
    # personne d'autre n'est blond platine, et personne ne porte ce rose-la.
    _p("racoleuse", "Fille de la Brume", "#ff3d8e", "#f2d27a", "#f0c098", "#c2185b",
       sprite="racoleuse", vitesse=0.9, vie=60, argent=(20, 90), temoin=0.2,
       metier="compagnie", heures=(0.78, 0.28), frequence=0.0),
    _p("vendeur", "Marchand ambulant", "#ecf0f1", "#3a2a1a", "#c98d66", "#2a3a4a",
       vitesse=0.0, vie=70, argent=(20, 70), temoin=0.5, metier="ambulant",
       frequence=0.0),
    # L'homme-sandwich : un SOLLICITEUR. Il porte l'enseigne d'un kiosque sur
    # le ventre et le dos, il fait les cent pas a quelques tuiles de son
    # commerce et il vient vers toi quand il te voit — pour te tenir le
    # crachoir et te glisser un coupon (`magasins.RECLAME`). Il ne nait jamais
    # au hasard : `carte.reclames` lui donne un poste, et `entites.peupler` l'y
    # fait naitre le jour (`heures`). ⚠️ Deuxieme archetype a avoir SON PROPRE
    # SPRITE (`homme_sandwich`) : une pancarte plus large que les epaules est un
    # contour, et c'est un contour qui se lit a douze pixels — pas une couleur.
    # Son `c` est la pancarte, pas un chandail.
    _p("homme_sandwich", "Homme-sandwich", "#f4ead2", "#4a3320", "#e8b088", "#4a4a5a",
       sprite="homme_sandwich", vitesse=0.85, vie=65, argent=(5, 30), temoin=0.35,
       metier="reclame", heures=(0.3, 0.85), frequence=0.0),
    # ⚠️ Le commis TIENT UN COMPTOIR, dedans. Il ne naît jamais dans la rue
    # (frequence 0) : `entites.peuplerInterieur` le pose derriere sa caisse
    # quand on pousse la porte. Sans lui, une piece meublee reste un musee —
    # c'est le monde derriere le comptoir qui fait qu'on est entre quelque
    # part. Sa caisse est dans ses poches : le voler est un vrai choix.
    _p("commis", "Commis", "#d8d8d0", "#4a3320", "#e8b088", "#3a3a4a",
       vitesse=0.55, courage=0.3, vie=65, argent=(25, 95), temoin=0.5,
       metier="commerce", frequence=0.0),
    # L'agent : un pieton que la police dirige quand il poursuit. Il patrouille
    # sur les trottoirs comme tout le monde, arme au ceinturon, et ne nait
    # jamais au hasard — `police.js` en place autant que la zone en demande.
    _p("policier", "Agent", "#1f3a6e", "#101018", "#e8b088", "#16264a",
       vitesse=1.0, courage=1.0, temoin=0.0, vie=100, argent=(0, 0), arme="pistolet",
       metier="police", frequence=0.0),
    # Les gars du lot : ils tiennent la grille de la fourriere et ne naissent
    # jamais ailleurs. ⚠️ Courage 1 et une batte, pas un pistolet : ils
    # RIPOSTENT quand on sort un char sans payer, ils n'abattent personne —
    # c'est la police qu'ils appellent pour ca.
    _p("gardien", "Gardien du lot", "#5a5f66", "#2a1a10", "#e8b088", "#2a2a3a",
       vitesse=1.05, courage=1.0, temoin=0.0, vie=110, argent=(5, 30), arme="batte",
       metier="gardien", frequence=0.0),
    # --- Trois sortes de gens (demande de Martin) -------------------------
    # ⚠️ UNE SORTE = UN CORPS + UNE ROUTINE. Chacune a son sprite (elles ne
    # sont pas le corps commun repeint) et son `metier`, qui est le crochet
    # que `entites.js` lit pour lui donner ce qu'elle FAIT. Une sorte sans
    # routine, c'est un costume — et le depot a deja paye ce defaut une fois
    # avec les filles de la Brume.
    #
    # `frequence=0` : elles ne naissent pas au hasard dans la foule, on les
    # POSE aux coins de rue, comme l'homme-sandwich.
    #
    # ⚠️ LES QUATRE ARTISTES TIENNENT LE CENTRE-VILLE (`districts`), et c'est
    # une demande de Martin qui repare un defaut : ils naissaient PARTOUT, donc
    # un mime dans une cour a ferraille de La Shop a 3 h du matin, devant
    # personne. Le Faubourg est le centre-ville ouvrier (`devantures.py` le dit
    # deja en toutes lettres) et le district le plus peuple de la ville. Un
    # amuseur joue la ou il y a du monde ; ailleurs, il joue pour les goelands.
    _p("musicien", "Musicien de rue", "#6b4b8a", "#3a2a1a", "#e8b088", "#2a2a3a",
       sprite="musicien", vitesse=0.0, courage=0.2, temoin=0.6, vie=70,
       argent=(15, 60), metier="musicien", frequence=0.0,
       districts=("faubourg",)),
    # ⚠️ L'amuseur attire un ATTROUPEMENT, et un attroupement est une foule de
    # temoins : faire un coup devant lui, c'est dix temoins d'un seul geste.
    # Ce n'est pas du decor, c'est l'endroit de la rue ou il ne faut pas
    # sortir une arme.
    _p("amuseur", "Amuseur public", "#efe6d0", "#2a2a2a", "#e8b088", "#1a1a22",
       sprite="amuseur", vitesse=0.0, courage=0.3, temoin=0.8, vie=70,
       argent=(10, 45), metier="amuseur", frequence=0.0,
       districts=("faubourg",)),
    # --- Deux amuseurs de plus (demande de Martin) -------------------------
    # ⚠️ « Ils ne font rien et sont ennuyants » : le mime etait le SEUL genre
    # d'amuseur, et il tenait l'image zero de son sprite du debut a la fin de
    # la partie. Le jongleur et l'echassier ne sont pas deux costumes de plus —
    # ce sont deux spectacles qu'on reconnait DE LOIN, et c'est tout leur
    # interet : on voit le spectacle avant de voir l'artiste.
    #
    # Le jongleur a TROIS BALLES DANS LES AIRS, et elles sont dans le sprite :
    # les dessiner a part aurait voulu dire un deuxieme chemin de dessin pour
    # une seule sorte, et un objet de plus a trier par `y`.
    _p("jongleur", "Jongleur", "#d4442e", "#3a2a1a", "#e8b088", "#f2c94c",
       sprite="jongleur", vitesse=0.0, courage=0.3, temoin=0.8, vie=70,
       argent=(10, 50), metier="jongleur", frequence=0.0,
       districts=("faubourg",)),
    # ⚠️ ET LUI DEPASSE LA FOULE. Son corps fait 26 pixels de haut au lieu de
    # 13 : c'est la seule sorte de la ville qu'on voit PAR-DESSUS son propre
    # attroupement, et c'est exactement pour ca qu'il existe. Un echassier a
    # hauteur d'homme serait un homme.
    _p("echassier", "Échassier", "#2f7f6f", "#5a3a1a", "#e8b088", "#c94f3a",
       sprite="echassier", vitesse=0.0, courage=0.3, temoin=0.9, vie=70,
       argent=(10, 50), metier="echassier", frequence=0.0,
       districts=("faubourg",)),
    # ⚠️ Et lui, LA POLICE L'ARRETE. C'est la seule fois ou elle s'occupe de
    # quelqu'un d'autre que le joueur — et c'est ce gag qui la rend credible :
    # elle n'existe pas que pour toi.
    _p("exhibitionniste", "L'homme au manteau", "#7a5a3a", "#4a3320", "#e8b088", "#2a2a3a",
       sprite="exhibitionniste", vitesse=0.85, courage=0.1, temoin=0.1, vie=60,
       argent=(2, 15), metier="exhibitionniste", frequence=0.0),
    # --- Les cinq qui viennent avec ---------------------------------------
    # ⚠️ MEME REGLE, et ce n'est pas du remplissage : chacune sert une fiche
    # DEJA LIVREE. Une sorte qui n'est qu'une silhouette de plus dans la rue
    # n'a pas sa place ici — c'est exactement le defaut que « une sorte = un
    # corps + une routine » a ete ecrite pour empecher.
    #
    # ⚠️ Et elles ne naissent pas au hasard non plus (`frequence=0`) : on les
    # POSE. ⚠️ Chacune a SES QUARTIERS (`districts`) — un touriste sur les
    # Quais et pas dans La Shop, un facteur aux Erables et pas au port. C'est
    # ce qui les empeche d'etre une figuration de plus partout pareille, et ce
    # qui fait qu'un quartier se reconnait aussi a qui y marche.

    # Elle rend « mal gare » VISIBLE avant que la fourriere n'avale le char :
    # jusqu'ici, un message du HUD annoncait la remorqueuse et rien, dans la
    # rue, ne disait pourquoi.
    _p("contractuelle", "Contractuelle", "#2e5f8a", "#3a2a1a", "#f0c098", "#26324a",
       sprite="contractuelle", vitesse=0.9, courage=0.4, temoin=0.9, vie=70,
       argent=(10, 40), metier="contractuelle", frequence=0.0,
       districts=("faubourg", "shop")),
    # ⚠️ LE MEILLEUR TEMOIN DE LA VILLE (`temoin=1.0`, le seul) : il regarde,
    # c'est tout ce qu'il fait. Faire un coup devant lui, c'est se faire voir a
    # coup sur — et il est lent, alors on ne le seme pas en marchant.
    _p("touriste", "Touriste", "#f2e2a8", "#8a6a3a", "#e8b088", "#8a7a5a",
       sprite="touriste", vitesse=0.7, courage=0.0, temoin=1.0, vie=55,
       argent=(30, 90), metier="touriste", frequence=0.0,
       districts=("quais", "pointe")),
    # ⚠️ LE SEUL QUI NE FUIT PAS devant une arme — il insulte. Ce qui le rend
    # dangereux pour lui-meme, et c'est le but : une rue ou tout le monde
    # detale de la meme facon n'a qu'une reaction.
    _p("ivrogne", "Ivrogne", "#6a5a4a", "#8a8a8a", "#d8a878", "#4a4438",
       sprite="ivrogne", vitesse=0.7, courage=1.0, temoin=0.05, vie=70,
       argent=(2, 18), metier="ivrogne", frequence=0.0,
       districts=("quais", "faubourg")),
    # Ecouteurs sur les oreilles : il ne temoigne de RIEN (`temoin=0.0`, le
    # seul avec l'agent) et il ne s'arrete jamais — ni pour un amuseur, ni
    # pour une pause.
    _p("jogger", "Joggeuse", "#e04a3a", "#2a2a2a", "#e8b088", "#2a2a2a",
       sprite="jogger", vitesse=1.45, courage=0.2, temoin=0.0, vie=75,
       argent=(0, 8), metier="jogger", frequence=0.0,
       districts=("erables", "pointe")),
    # Sa tournee fait battre les portes de la rue une a une — et il n'ENTRE
    # jamais. C'est toute la difference avec le flaneur qui rentre chez lui :
    # celui-la disparait derriere le battant, le facteur reste dehors.
    _p("facteur", "Facteur", "#2e6b4a", "#3a2a1a", "#e8b088", "#1f2f24",
       sprite="facteur", vitesse=1.0, courage=0.3, temoin=0.5, vie=70,
       argent=(5, 25), metier="facteur", frequence=0.0,
       districts=("erables", "faubourg")),

    # --- Troisieme vague : trois qui gagnent leur vie dans la rue ----------
    # ⚠️ Choisies pour leur CROCHET, pas pour leur costume — c'est la seule
    # regle du reservoir, et c'est celle qui fait qu'une sorte n'est pas un
    # figurant de plus.

    # ⚠️ IL HURLE CE QUE TU AS FAIT HIER. La manchette vient du Clairon
    # (`journal.py`), qui compare les statistiques d'aujourd'hui a celles
    # d'hier : tuer trois personnes un soir, c'est l'entendre crie au coin de
    # la rue le lendemain matin. C'est la boucle la moins chere du jeu, et la
    # seule qui te renvoie ton propre reflet sans menu.
    _p("crieur", "Crieur de journaux", "#c0392b", "#3a2a1a", "#e8b088", "#3a3a4a",
       sprite="crieur", vitesse=0.0, courage=0.2, temoin=0.7, vie=65,
       argent=(8, 35), metier="crieur", frequence=0.0,
       heures=(0.25, 0.55), districts=("faubourg", "shop")),
    # ⚠️ IL TRAVAILLE AU FEU ROUGE : il ne s'approche que des chars ARRETES.
    # Les feux pour pietons viennent d'etre livres — c'est la meme horloge, et
    # c'est elle qui lui donne ses quinze secondes de travail.
    _p("laveur", "Laveur de vitres", "#2f6b8a", "#2a2a2a", "#c98d66", "#3a4450",
       sprite="laveur", vitesse=0.95, courage=0.3, temoin=0.5, vie=70,
       argent=(3, 20), metier="laveur", frequence=0.0,
       districts=("shop", "faubourg")),
    # ⚠️ IL VOLE LES AUTRES. La ville coupable d'elle-meme : un crime que tu
    # n'as pas commis, une victime qui crie, et un agent qui arrete QUELQU'UN
    # D'AUTRE que toi. C'est le deuxieme apres l'homme au manteau, et les deux
    # ensemble disent la meme chose — la police n'existe pas que pour toi.
    _p("pickpocket", "Pickpocket", "#3a4450", "#1a1a1a", "#d8a878", "#26262e",
       sprite="pickpocket", vitesse=1.1, courage=0.2, temoin=0.1, vie=65,
       argent=(20, 80), metier="pickpocket", frequence=0.0,
       districts=("faubourg", "quais")),
]

#: Les gangs : leur archetype, leur territoire (zone de la carte), leur humeur.
GANGS: list[dict] = [
    {"slug": "cravates", "nom": "Les Cravates", "pieton": "cravate", "zone": "cravates",
     "district": "faubourg", "membres": 8, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
    # v2 / M8 — une gang par district. Les Boulonneux sont les seuls a ne pas
    # attendre que tu sortes une arme : La Shop n'est a personne d'autre.
    {"slug": "morues", "nom": "Les Morues", "pieton": "morue", "zone": "morues",
     "district": "quais", "membres": 8, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
    {"slug": "chevreuils", "nom": "Les Chevreuils", "pieton": "chevreuil", "zone": "chevreuils",
     "district": "erables", "membres": 6, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
    {"slug": "boulonneux", "nom": "Les Boulonneux", "pieton": "boulonneux", "zone": "boulonneux",
     "district": "shop", "membres": 9, "hostile_si_arme": True,
     "hostile_toujours": True, "phase": 1},
    {"slug": "skateux", "nom": "Les Skateux", "pieton": "skateux", "zone": "skateux",
     "district": "pointe", "membres": 6, "hostile_si_arme": True,
     "hostile_toujours": False, "phase": 1},
]

#: Ce qui arrive a un pieton qu'on frappe, en images (60 par seconde).
REACTIONS = {
    "recul_images": 12,          # il titube
    "ko_images": 300,            # assomme : il se releve apres 5 s
    "fuite_secondes": 8,         # combien de temps il court avant de se calmer
    "peur_rayon_tuiles": 7,      # qui voit le coup et prend peur
    "saignement_images": 240,    # duree max d'un saignement
    "degats_saignement": 1,      # points de vie par seconde de saignement
    "pickpocket_images": 45,     # le temps de faire les poches
    "pickpocket_dos_degres": 90, # il faut etre DERRIERE lui
    "enfant_peur_tuiles": 12,    # un enfant detale de bien plus loin
    "suite_distance_px": 26,     # a quelle distance l'enfant suit sa mere
    # ⚠️ La chance qu'un ivrogne tombe tout seul, par seconde. Elle est ICI et
    # pas dans le JS pour une raison tres concrete : un juge qui attend une
    # chute a six pour cent la joue a pile ou face (vingt-cinq occasions en
    # 1500 images, une sur cinq de n'en voir aucune). En fiche, il la met a 1
    # et mesure la REGLE au lieu d'esperer le hasard.
    "ivrogne_chute": 0.06,
    # ⚠️ LA DALLE EST PRIORITAIRE (Martin, le trottoir a une tuile : « priorite
    # de marcher sur le trottoir »). L'abord — la couronne d'un bloc — se foule,
    # mais c'est un DEBORDEMENT : un flaneur sur la dalle qui s'apprete a en
    # descendre vers l'abord y renonce le plus souvent et se retourne. Il y va
    # quand meme une fois sur quatre — sinon la dalle d'une tuile serait une
    # file indienne, et c'est justement pour se croiser que l'abord existe.
    "abord_renonce": 0.75,
}

#: LE SPECTACLE DE RUE — ce que Martin a demandé : « qu'ils soient animés, et
#: qu'il y ait TOUJOURS entre 3 et 5 personnes autour ».
#:
#: ⚠️ « Toujours » est le mot qui change tout : jusqu'ici l'attroupement était
#: une CHANCE, pas une règle. `attrouper` attendait qu'un passant entre dans le
#: cercle et soit en train de flâner — dans une rue vide, il n'y avait personne,
#: et ceux qui s'arrêtaient repartaient au bout de quelques secondes sans que
#: rien ne les remplace. Le juge du banc posait lui-même quatre badauds avant de
#: mesurer, c'est-à-dire qu'il mesurait l'attroupement d'une foule qu'il avait
#: fabriquée. Un minimum est une règle : en dessous, un badaud NAÎT hors champ
#: et vient se planter dans le cercle.
#:
#: ⚠️ Et les chiffres vivent ICI, pas dans `entites.js` : le navigateur les lit,
#: il ne les invente pas. C'est ce qui permet à un juge de les relire — et à
#: Martin de dire « plutôt 6 » sans ouvrir une ligne de JavaScript.
SPECTACLE = {
    "minimum": 3,               # jamais moins de monde autour d'un artiste
    "maximum": 5,               # ni plus : au-delà, on ne voit plus le numéro
    "rayon_px": 46,             # qui, en passant, se fait prendre par le numéro
    "cercle_px": 24,            # à quelle distance du poste on se plante
    "cercle_jeu_px": 8,         # de combien le cercle est irrégulier
    "patience_images": (420, 1080),   # 7 à 18 s de spectacle, puis on repart
    # ⚠️ LA RELEVE PART AVANT QUE L'AUTRE S'EN AILLE. Un remplacant met deux a
    # quatre secondes a traverser la rue ; si on ne l'appelle qu'une fois la
    # place vide, le cercle tombe a deux le temps qu'il arrive — et « toujours
    # entre 3 et 5 » devient « la plupart du temps ». On compte donc ceux qui
    # seront ENCORE LA dans autant d'images, et on appelle du monde des que ce
    # compte-la passe sous le minimum.
    "releve_images": 240,
    "applaudit_images": 40,     # le temps d'un bravo
    "applaudit_chance": 0.5,    # un spectateur sur deux applaudit en partant
    "piece_chance": 0.45,       # et il laisse une pièce dans le chapeau
    "piece": (1, 5),            # combien il laisse — c'est la paye de l'artiste
    # ⚠️ Un badaud qui regarde un spectacle REGARDE : il témoigne mieux que le
    # même passant qui marchait en pensant à autre chose.
    "temoin_bonus": 0.4,
    # Le rythme du numéro, en images par pose. ⚠️ Le mime, le jongleur et
    # l'échassier ne marchent pas : leur animation ne peut pas venir de la
    # distance parcourue (elle est nulle), elle vient d'ICI. C'est tout le
    # défaut que Martin a vu — `imageDe` tombe sur l'image zéro pour un corps
    # immobile, et le mime a tenu la même pose toute la partie.
    # ⚠️ Le MUSICIEN n'est là qu'en repli : sa main suit le TEMPO du morceau
    # qu'il joue (`Son.Rue.surLeTemps`), pas un compteur d'images. Ces
    # chiffres-là servent quand le son est coupé ou que le navigateur retient
    # encore l'audio — il gratte quand même, et c'est ce qu'il faut : un
    # musicien immobile dans une partie muette serait le défaut d'origine.
    "images_par_pose": {"musicien": 12, "amuseur": 34, "jongleur": 7, "echassier": 26},
    # L'ENCHAINEMENT des images, par métier. ⚠️ Le jongleur fait une ronde
    # (0-1-2-3 : la case vide de l'arc tourne) ; l'échassier TANGUE, et un
    # tangage revient sur lui-même — c'est le même 0-1-0-2 que la marche du
    # jeu, et pour la même raison : il faut repasser par le milieu.
    "poses": {
        # La main descend, gratte, remonte — et repasse par le milieu.
        "musicien": [0, 1, 2, 1],
        "amuseur": [0, 1, 2, 3],
        "jongleur": [0, 1, 2, 3],
        "echassier": [0, 1, 0, 2],
    },
    # ⚠️ COMBIEN D'ARTISTES DANS LA BULLE, TOUTES SORTES CONFONDUES. C'est ce
    # qui rend « toujours 3 à 5 autour » tenable : quatre sortes à deux
    # exemplaires feraient huit artistes, donc de 24 à 40 spectateurs, pour un
    # budget de foule de 28 — la rue n'aurait plus eu un seul passant qui passe.
    # Deux, c'est aussi ce qui les garde rares, donc remarqués.
    "artistes_max": 2,
}

#: Ce que le musicien joue, et ce que le chapeau rapporte. ⚠️ Les cinq morceaux
#: sont dans `musique.py` (RUE) : ici, seulement ce qui regarde le passant.
MUSICIEN = {
    "portee_px": 260,           # d'où on commence à l'entendre
    "plein_px": 40,             # à partir d'où il joue à plein volume
    "volume": 0.75,
    # Le titre s'affiche quand on s'arrête devant lui. ⚠️ Sans ça, cinq
    # morceaux différents et rien pour dire qu'ils le sont : on n'entend pas
    # un catalogue, on entend une toune.
    "titre_px": 56,
    "titre_images": 180,
}

#: CE QUE LES SORTES DISENT — et ça vit ICI, pas dans le JavaScript.
#:
#: ⚠️ Le dépôt a payé huit fois le même défaut : « une fiche que le navigateur
#: ne lisait pas ». Le symétrique coûte aussi cher — un mot écrit en dur dans
#: `entites.js` est un mot que personne ne peut relire, corriger ni juger
#: depuis la source de vérité. `missions.py` le dit déjà pour l'histoire (« le
#: texte de chaque réplique vit ICI, et nulle part ailleurs ») ; ce qu'une
#: sorte de passant dit dans la rue n'est pas d'une autre nature.
PAROLES: dict[str, dict] = {
    # Ce qu'elle annonce en glissant le papier sous l'essuie-glace.
    "contractuelle": {"verbalise": "CONTRAVENTION"},
    # Il ne rentre pas : il ouvre, il glisse, il repart.
    "facteur": {"livre": "POSTE"},
    # ⚠️ Il n'a pas peur, il n'a rien compris : au lieu de fuir, il répond.
    # C'est le seul de la ville, et c'est ce qui le rend dangereux pour lui.
    "ivrogne": {
        "insultes": ["AYOYE", "R'GARDE OÙ TU VAS", "MON ONCLE!", "SANTÉ!"],
        "sans_peur": "PIS QUOI ENCORE",
    },
    # ⚠️ Ce qu'il crie VRAIMENT, c'est la manchette du Clairon ; celle-ci n'est
    # que son appel, pour les matins où il n'y a rien à signaler.
    "crieur": {"appel": "LE CLAIRON DE LA BAIE!"},
    "laveur": {"propose": "UN COUP DE CHIFFON?", "merci": "MERCI M'SIEUR"},
    # Le voleur ne dit rien. C'est la VICTIME qui parle — et c'est elle qu'on
    # doit entendre, sinon le vol n'est qu'une animation.
    "pickpocket": {"au_voleur": "AU VOLEUR!"},
    # --- Les amuseurs de rue ----------------------------------------------
    # ⚠️ C'est LA FOULE qui parle, pas l'artiste — et c'est exactement ce qui
    # manquait : un numéro sans un bravo n'est pas un spectacle, c'est un
    # personnage debout. `bravo` est dit par un spectateur qui s'en va content.
    "musicien": {"bravo": ["BRAVO!", "ENCORE!", "C'EST BEAU!"],
                 "chapeau": "MERCI M'SIEUR-DAME"},
    "amuseur": {"bravo": ["BRAVO!", "HA!", "IL EST BON"]},
    "jongleur": {"bravo": ["BRAVO!", "OH!", "HOP LÀ!"], "numero": "ET HOP!"},
    "echassier": {"bravo": ["BRAVO!", "R'GARDE EN HAUT!", "IL EST GRAND!"]},
}

#: Un piéton assomme rapporte ses poches ; un mort ne rapporte rien de plus.
SLUGS = tuple(p["slug"] for p in CATALOGUE)


def par_slug(slug: str) -> Pieton | None:
    for pieton in CATALOGUE:
        if pieton["slug"] == slug:
            return pieton
    return None


def ordinaires(district: str | None = None) -> list[Pieton]:
    """Ceux qui peuplent la rue (gangs et metiers apparaissent autrement).

    Sans district : ceux de partout. Avec : ceux de partout PLUS ceux de ce
    quartier-la — jamais ceux du quartier d'a cote.
    """
    return [p for p in CATALOGUE if p["frequence"] > 0 and p["gang"] is None
            and (p["districts"] is None or (district in (p["districts"] or ())))]


def de_metier(metier: str) -> list[Pieton]:
    return [p for p in CATALOGUE if p["metier"] == metier]


def travaille_a(pieton: Pieton, heure: float) -> bool:
    """`heures` = (debut, fin) sur 24 h ramenees a 0..1 ; peut passer minuit."""
    creneau = pieton["heures"]
    if not creneau:
        return True
    debut, fin = creneau
    return debut <= heure < fin if debut < fin else (heure >= debut or heure < fin)


def exporter() -> dict:
    return {
        "catalogue": CATALOGUE,
        "gangs": GANGS,
        "reactions": dict(REACTIONS),
        # ⚠️ Le spectacle de rue passe par le paquet, comme tout le reste : un
        # minimum de 3 ecrit dans `entites.js` serait un nombre que personne ne
        # peut relire ni juger depuis la source de verite.
        "spectacle": {**SPECTACLE,
                      "patience_images": list(SPECTACLE["patience_images"]),
                      "piece": list(SPECTACLE["piece"]),
                      "images_par_pose": dict(SPECTACLE["images_par_pose"]),
                      "poses": {m: list(p) for m, p in SPECTACLE["poses"].items()}},
        "musicien": dict(MUSICIEN),
        "paroles": {slug: dict(mots) for slug, mots in PAROLES.items()},
        "poids_total": round(sum(p["frequence"] for p in ordinaires()), 3),
    }
