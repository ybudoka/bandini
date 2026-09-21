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
    standings: tuple[str, ...] | None
    frequence: float
    phase: int


def _p(slug, nom, chandail, cheveux, peau, pantalon, *, sprite="joueur", vitesse=1.0,
       courage=0.0, temoin=0.3, vie=60, argent=(2, 20), arme=None, gang=None,
       intouchable=False, accompagne=None, metier=None, heures=None, districts=None,
       standings=None, frequence=1.0, phase=1) -> Pieton:
    return Pieton(
        slug=slug, nom=nom, sprite=sprite,
        couleurs={"c": chandail, "h": cheveux, "s": peau, "p": pantalon},
        vitesse=vitesse, courage=courage, temoin=temoin, vie=vie, argent=argent,
        arme=arme, gang=gang, intouchable=intouchable, accompagne=accompagne,
        metier=metier, heures=heures, districts=districts, standings=standings,
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
    # ⚠️ L'ENFANT A VELO — Martin (21 sept. 2026) : « je veux aussi des enfants
    # a velo, seulement sur trottoir, casque, parc ». Un CORPS a lui (le casque
    # se voit de loin, `SPRITES.enfant_velo`), pas l'enfant repeint : a seize
    # pixels, c'est la silhouette qui nomme, pas la couleur.
    # ⚠️ Il ne descend JAMAIS sur la chaussee — pas meme sur un passage pieton :
    # le trottoir, l'abord et le parc, rien d'autre (`Entites.roulableEnfant`).
    # Intouchable comme l'enfant a pied, et il ne va rien raconter a la police
    # (`temoin=0`) : un temoin court vers l'agent, et le chemin passe par la rue.
    # ⚠️ Frequence 0 : il ne se tire pas dans la foule, il nait par son propre
    # systeme (`ENFANTS_A_VELO`) — le jour, dans les quartiers qui ont des parcs.
    _p("enfant_velo", "Enfant à vélo", "#f1c40f", "#6b4b2c", "#f0c098", "#2f6b8a",
       sprite="enfant_velo", vitesse=2.0, vie=40, argent=(0, 2), temoin=0.0,
       intouchable=True, metier="cycliste", frequence=0.0, heures=(0.33, 0.8),
       districts=("erables", "pointe", "faubourg")),
    # ⚠️ LES BAIGNEURS — Martin : « des gens s'il y a beaucoup de place ». Des
    # enfants seuls sur une plage, c'est une cour d'ecole. Le corps commun, et
    # c'est la PALETTE qui les met en maillot : lui torse nu (le chandail a la
    # couleur de la peau) et un maillot rouge, elle en maillot une piece et les
    # jambes nues (le pantalon a la couleur de la peau). Ils ne naissent que sur
    # une plage declaree (`carte.PLAGES`, frequence 0), et leur routine est celle
    # des enfants de la plage, le chateau en moins et le soleil en plus.
    # Presque rien en poche : on ne va pas a la plage avec son portefeuille.
    _p("baigneur", "Baigneur", "#e8b088", "#4a3320", "#e8b088", "#c0392b",
       vitesse=0.8, vie=60, argent=(0, 12), temoin=0.6, courage=0.1,
       metier="baigneur", frequence=0.0),
    _p("baigneuse", "Baigneuse", "#2f8fb5", "#8a5a2b", "#f0c098", "#f0c098",
       vitesse=0.8, vie=60, argent=(0, 12), temoin=0.6, courage=0.05,
       metier="baigneur", frequence=0.0),
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
    # ⚠️ LA CONDUCTRICE DU CABRIOLET ROSE : elle ne marche jamais sans sa
    # voiture (`frequence=0`, et pas de `metier` — descendue, c'est une passante
    # comme une autre : elle fuit, elle temoigne). C'est la fiche du char qui la
    # nomme (`vehicules.au_volant`), et le carjacking qui la fait naitre : elle
    # sort de SA voiture, en robe. Troisieme archetype a avoir son propre corps
    # (`conductrice` dans sprites.js) : une robe d'une seule piece, et une couleur
    # ne la distingue pas d'un chandail a douze pixels — la coupe, oui. La robe
    # est du meme rose en `c` et en `p` (une robe n'a pas de haut et de bas), et
    # ses couleurs ne se croisent nulle part ailleurs dans le catalogue.
    # Elle a de quoi payer sa voiture : la bourse est la plus lourde de la rue.
    _p("conductrice", "Dame au cabriolet", "#f7a1c4", "#d9a441", "#f0c098", "#f7a1c4",
       sprite="conductrice", vitesse=0.9, courage=0.0, vie=55, argent=(60, 180),
       temoin=0.75, frequence=0.0),
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
    # ⚠️ LES MASCOTTES DE LA FOIRE — Martin : « plein de kiosques, de vendeurs,
    # de mascottes ». Un seul CORPS (`mascotte` : une grosse tete d'ours, des
    # oreilles rondes, un noeud papillon) et trois PELAGES — c'est la palette
    # qui en fait trois, comme les seize silhouettes du corps commun. Elles ne
    # naissent que dans la foire (frequence 0), et leur routine est d'y
    # deambuler et de SALUER : les bras leves, deux images qui alternent.
    _p("mascotte", "Mascotte (ours)", "#c0392b", "#8a5a2b", "#efe0c0", "#4a3320",
       sprite="mascotte", vitesse=0.7, vie=80, argent=(0, 10), temoin=0.2,
       metier="mascotte", frequence=0.0, districts=("pointe",)),
    _p("mascotte_bleue", "Mascotte (bleue)", "#efd06a", "#3f7fc0", "#e6f0f8", "#1f3f66",
       sprite="mascotte", vitesse=0.7, vie=80, argent=(0, 10), temoin=0.2,
       metier="mascotte", frequence=0.0, districts=("pointe",)),
    _p("mascotte_rose", "Mascotte (rose)", "#2f8d6a", "#e87aa8", "#fbe3ee", "#8e3a64",
       sprite="mascotte", vitesse=0.7, vie=80, argent=(0, 10), temoin=0.2,
       metier="mascotte", frequence=0.0, districts=("pointe",)),
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
    # ⚠️ Les gens de l'HOPITAL, dedans seulement (frequence 0), comme le commis.
    # La soignante tient le triage et le poste des infirmieres : la blouse
    # blanche et le pantalon vert d'hopital, c'est ce qui dit « on est a
    # l'hopital » avant meme le lit. Le malade porte la JAQUETTE — le seul
    # vetement du catalogue qui soit le meme en haut et en bas — et il ne se
    # leve pas : `entites.peuplerInterieur` le couche dans son lit (`alite`) et
    # lui prete la tete et la peau d'un passant, pour que six malades ne soient
    # pas six fois le meme.
    _p("soignante", "Infirmière", "#eef3f1", "#3a2a1a", "#f0c098", "#7fbfa6",
       vitesse=0.8, courage=0.1, vie=60, argent=(10, 45), temoin=0.6,
       metier="soins", frequence=0.0),
    _p("malade", "Malade", "#b9d6dc", "#5a4a3a", "#e8c0a0", "#b9d6dc",
       vitesse=0.5, courage=0.0, vie=35, argent=(0, 4), temoin=0.0,
       metier="malade", frequence=0.0),
    # ⚠️ L'AVOCAT DU BROUILLARD, dedans seulement (frequence 0), comme le commis.
    # Me Desjardins tient la table du fond et on vient lui PARLER
    # (`missions.menuAvocat`) — mais la table etait vide : le jeu promettait un
    # avocat et montrait deux chaises (retour de Martin : « je ne vois pas
    # d'image de l'avocat dans le bar »). `entites.peuplerInterieur` l'assoit sur
    # sa chaise, comme le patient de l'hopital.
    # ⚠️ UN CORPS A LUI (`avocat` dans sprites.js), et pas le corps commun : un
    # complet fonce sur le corps commun, c'est une CRAVATE — la gang du Faubourg
    # assise a la table ou l'on vient nettoyer son dossier. Ce qui le nomme a
    # douze pixels, c'est la chemise blanche, la cravate rouge et les cheveux gris.
    # Frappe, il se sauve et il temoigne : c'est un avocat.
    _p("avocat", "Me Desjardins", "#3b3f4c", "#b4b4b4", "#e8b088", "#2c2f38",
       sprite="avocat", vitesse=0.8, courage=0.0, vie=60, argent=(40, 160), temoin=0.9,
       metier="avocat", frequence=0.0),
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
    # ⚠️ `standings` : QUI MARCHE DANS LA RUE dit aussi le standing (4e vague des
    # quartiers). Un touriste ne se promene pas au pied des plex du port, un
    # ivrogne ne dort pas dans la rue chic. Ca se croise avec `districts` : la
    # sorte nait la ou les DEUX sont vrais, et une sorte sans standing va partout.
    _p("touriste", "Touriste", "#f2e2a8", "#8a6a3a", "#e8b088", "#8a7a5a",
       sprite="touriste", vitesse=0.7, courage=0.0, temoin=1.0, vie=55,
       argent=(30, 90), metier="touriste", frequence=0.0,
       districts=("quais", "pointe"), standings=("cossu", "ordinaire")),
    # ⚠️ LE SEUL QUI NE FUIT PAS devant une arme — il insulte. Ce qui le rend
    # dangereux pour lui-meme, et c'est le but : une rue ou tout le monde
    # detale de la meme facon n'a qu'une reaction.
    _p("ivrogne", "Ivrogne", "#6a5a4a", "#8a8a8a", "#d8a878", "#4a4438",
       sprite="ivrogne", vitesse=0.7, courage=1.0, temoin=0.05, vie=70,
       argent=(2, 18), metier="ivrogne", frequence=0.0,
       districts=("quais", "faubourg"), standings=("pauvre",)),
    # Ecouteurs sur les oreilles : il ne temoigne de RIEN (`temoin=0.0`, le
    # seul avec l'agent) et il ne s'arrete jamais — ni pour un amuseur, ni
    # pour une pause.
    _p("jogger", "Joggeuse", "#e04a3a", "#2a2a2a", "#e8b088", "#2a2a2a",
       sprite="jogger", vitesse=1.45, courage=0.2, temoin=0.0, vie=75,
       argent=(0, 8), metier="jogger", frequence=0.0,
       districts=("erables", "pointe"), standings=("cossu", "ordinaire")),
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
    # ⚠️ LA NUIT A SES HABITUDES : LE CAMELOT DU CLAIRON. Il passe a l'AUBE, avant
    # le crieur, et il lance le journal sur les perrons, porte apres porte — sans
    # jamais entrer, comme le facteur. Le corps est celui du crieur (le sac de
    # journaux en bandouliere), repeint ; la routine est la sienne. Ses heures
    # tombent dans la nuit qu'on voit : on le croise a la lueur des lampadaires.
    _p("camelot", "Camelot", "#2f5f8a", "#3a2a1a", "#e8b088", "#2a2a3a",
       sprite="crieur", vitesse=1.15, courage=0.2, temoin=0.4, vie=60,
       argent=(2, 12), metier="camelot", frequence=0.0,
       heures=(0.19, 0.265), districts=("erables", "faubourg")),
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
       districts=("faubourg", "quais"), standings=("pauvre",)),
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
#: **LA VILLE EST COUPABLE D'ELLE-MEME.** GTA 2 le faisait deja : des choses
#: arrivent a d'AUTRES qu'au joueur, et c'est ce qui fait la difference entre
#: une ville et un decor qui attend. Le vol a la tire entre passants existe
#: depuis les sortes de gens (`majPickpocket`) ; voici le **vol de char**.
#:
#: ⚠️ **Il se voit, ou il n'a pas lieu.** Un vol hors champ est du travail
#: qu'on fait pour personne : on n'en declenche un que sur un char que le
#: joueur a sous les yeux. Rare, donc, et jamais deux a la fois.
#:
#: ⚠️ **Et ce n'est PAS le joueur qui le paie.** La police du jeu est centree
#: sur lui : signaler ce vol comme un crime lui mettrait une etoile pour le
#: geste d'un autre. Les passants s'ecartent, le voleur part avec le char, et
#: c'est tout — « ca peut te tomber dessus » est une autre histoire, et elle
#: se fera avec son propre juge.
#:
#: ⚠️ Le tirage se fait a l'EMPREINTE de la minute (`hash2`), pas au de du jeu :
#: la lecon du pilote des deux-roues, et celle du char en panne.
VOL_DE_CHAR: dict = {
    "chance_par_minute": 0.30,   # qu'un vol commence, par minute de jeu
    "rayon_px": 240,             # le char vole est a portee de vue
    "marche_images": 420,        # le temps qu'il a pour l'atteindre, sinon il renonce
    "portee_px": 20,             # ou il ouvre la portiere
    "peur": 1,                   # la gravite de ce que voient les passants
}

#: LA BAGARRE DE GANGS — l'autre moitie de « la ville est coupable d'elle-meme ».
#:
#: ⚠️ **A LEUR FRONTIERE, ET NULLE PART AILLEURS.** Une gang savait deja se
#: battre chez elle CONTRE LE JOUEUR (`attaque_joueur`, livre avec M6) ; ce
#: qu'elle ne savait pas faire, c'est se battre contre UNE AUTRE. Le seul
#: endroit ou ca a un sens est la ligne ou deux districts tenus se touchent —
#: `frontieres()` la calcule a partir des rectangles de la carte, et il n'y en a
#: qu'une poignee sur toute la ville.
#:
#: ⚠️ **Le joueur n'est ni la cause ni la cible**, et c'est ce qui a coute le
#: plus cher a ecrire : trois mecanismes du depot ne connaissaient qu'une seule
#: reponse a la violence, « s'en prendre au joueur ». `alerter` retournait
#: toute gang a portee contre lui, `blesser` faisait de meme du blesse, et
#: `majAttaque` ramenait tout piton qui finissait son coup a `attaque_joueur`.
#: Les trois sont corriges, chacun sous son juge.
#:
#: ⚠️ Le tirage se fait a l'EMPREINTE de la minute (`hash2`), jamais au de du
#: jeu : la lecon du char en panne, qui avait fait tomber quatre juges d'un
#: coup.
#:
#: ⚠️ **« PAR MINUTE DE JEU » TROMPE** — retour de Martin (16 sept. 2026) : « je
#: veux moins de bagarre de gang ». Une journee dure huit minutes
#: (`economie.JOUR_SECONDES`), donc une minute de jeu dure un TIERS DE SECONDE,
#: et `majBagarre` tire a chacun de ses passages — toutes les 30 images, deux
#: fois par seconde. A 0,12, il suffisait de rester QUATRE SECONDES en vue
#: d'une frontiere pour qu'une rixe parte : on en croisait une a chaque
#: frontiere. A 0,01, elle se fait attendre CINQUANTE secondes en moyenne — on
#: la voit si on s'attarde, plus en passant. Un juge tient l'attente, calculee
#: sur la vraie cadence du navigateur.
BAGARRE: dict = {
    "chance_par_minute": 0.01,   # a chaque tirage, deux fois par seconde (voir plus haut)
    "membres": 3,                # de chaque cote — six hommes, pas une emeute
    # ⚠️ LA FENETRE EST CALEE SUR CELLE DE LA VILLE, et les deux bornes sont
    # des mesures, pas des gouts. En dessous de `trop_pres_px` on serait a
    # l'ECRAN (la vue fait 480 x 270, donc tout ce qui est a plus de 276 px du
    # joueur est forcement dehors) : on verrait six hommes se materialiser.
    # Au-dela de `rayon_px` on serait hors de la BULLE D'OUBLI (520 px) : ils
    # naitraient pour etre effaces a l'image suivante.
    "rayon_px": 500,             # la frontiere est a portee, et la rixe survit
    "trop_pres_px": 300,         # mais personne n'apparait sous les yeux du joueur
    "ecart_px": 26,              # de combien les hommes d'un camp s'etalent
    "recul_tuiles": 6,           # jusqu'ou chercher le trottoir, depuis la ligne
    "duree_images": 1500,        # 25 s : apres, les debout s'en vont
    "rival_px": 400,             # jusqu'ou on cherche quelqu'un a qui en vouloir
    "portee_px": 22,             # a quelle distance on cesse d'avancer et on frappe
    "cadence_images": 38,        # un coup toutes les 0,6 s
    "peur": 2,                   # la gravite de ce que voient les passants
    # Deux districts qui ne se touchent que par un coin n'ont pas de rue
    # mitoyenne : ce n'est pas une frontiere, c'est un point.
    "frontiere_min_tuiles": 16,
}

#: **LES ENFANTS JOUENT.** ⚠️ **Jouer, c'est un `metier`, pas un costume.** La
#: regle des sortes de gens est ecrite trois fois dans ce fichier, et le depot
#: l'a deja payee une fois avec les filles de la Brume : une sorte sans routine
#: est un deguisement. L'enfant existe depuis la v1 — `intouchable`, vite, temoin
#: a 0,5 — et il n'a jamais rien fait d'autre que marcher.
#:
#: ⚠️ **Ce n'est PAS l'archetype qu'on change, c'est l'enfant DE LA PLAGE qu'on
#: pose.** Donner un `metier` a tous les enfants de la ville les sortirait de la
#: foule (`foule()` ne compte que ce qui n'en a pas) et rendrait muette la mere
#: qui promene le sien. Ceux-ci naissent sur la greve et y restent : ils ont un
#: poste, comme l'ouvrier a son chantier et l'homme-sandwich au sien.
#:
#: ⚠️ **UN ENFANT NE SE NOIE PAS.** `intouchable` veut dire aujourd'hui « aucune
#: arme, aucun char » ; il doit dire aussi « pas l'eau ». Mesure, pour ne pas
#: s'attribuer un correctif : **aucun pieton ne se noie dans le jeu** — le
#: souffle et `noyade` n'existent que pour le joueur. La regle n'est donc pas
#: une reparation, c'est une garantie qu'on EPINGLE : ils barbotent dans la
#: PREMIERE tuile d'eau et pas plus loin, sinon la plage est une trappe a
#: noyade le jour ou quelqu'un donnera du souffle aux passants.
#:
#: ⚠️ Et une greve pleine d'enfants est une greve pleine de TEMOINS (0,5
#: chacun) : c'est la seule consequence mecanique de la vague, et elle est
#: bonne — le bord de l'eau devient le plus mauvais endroit de la ville pour
#: faire un coup, exactement comme l'attroupement de l'amuseur.
PLAGE: dict = {
    "enfants": 5,                # combien jouent sur la greve a la fois
    # ⚠️ ET DES GRANDS, depuis que les plages ont la place (`carte.PLAGES`). Ils
    # comptent A PART des enfants : un plafond commun laissait les premiers nes
    # prendre toutes les places, et la plage n'avait qu'un seul age.
    "adultes": 7,
    "adultes_archetypes": ("baigneur", "baigneuse"),
    # Se faire bronzer : on va a une serviette ou a une chaise longue libre, et
    # on y reste longtemps. C'est le jeu des grands, comme le chateau est celui
    # des petits.
    "bronzer_px": 240,
    "bronzer_images": (700, 1600),
    "rayon_px": 520,             # la bulle ou ils naissent et s'oublient
    "chateau_px": 220,           # jusqu'ou un enfant va chercher un chateau
    "accroupi_images": (200, 460),   # le temps qu'il passe a le rebatir
    # ⚠️ Jusqu'ou l'on entre dans l'eau, en tuiles. UNE, et c'est la regle qui
    # tient tout : on barbote au bord, on ne nage pas.
    "barbote_tuiles": 1,
    "barbote_images": (240, 540),
    "ballon_px": 120,            # a quelle distance deux enfants se lancent le ballon
    # ⚠️ ET PAS PLUS PRES QUE CA : deux enfants colles l'un a l'autre ne se
    # lancent rien — le ballon arrive avant d'etre parti, il fait la navette
    # sur place, et ce qu'on voit est un point qui vibre. Mesure : sans ce
    # plancher, il ne bougeait pas d'un pixel en quatre cents images.
    "ballon_min_px": 44,
    "ballon_vitesse": 2.4,
    "ballon_pause": 26,          # le temps de le ramasser avant de le relancer
    "jeu_images": (300, 720),    # puis on change de jeu
    # ⚠️ **LA NUIT, PERSONNE NE SE BAIGNE** (Martin, 21 sept. 2026). La plage
    # ouvre a 7 h 12 et ferme a 19 h 12, sur 24 h ramenees a 0..1 comme les
    # `heures` d'un metier : hors de la, personne n'y nait, et qui y est encore
    # sort de l'eau, range ses affaires et s'en va — hors de l'ecran, jamais
    # sous nos yeux. ⚠️ Ici et PAS sur l'archetype `enfant` : toute la ville
    # s'en sert, et les enfants disparaitraient de partout a la brunante. Les
    # deux heures tombent DANS le jour (`Monde.estNuit` : 6 h 24 → 19 h 53) :
    # on ferme au coucher du soleil, pas une fois la nuit tombee.
    "heures": (0.30, 0.80),
}

#: **LES ENFANTS A VELO** — combien, et de quelles couleurs.
#:
#: ⚠️ Les couleurs se lisent A L'EMPREINTE de la tuile ou il nait, pas au de :
#: un casque tire au sort decalerait tout ce qui nait apres lui. Et c'est le
#: CASQUE qui change le plus d'un enfant a l'autre — c'est lui qu'on voit.
ENFANTS_A_VELO: dict = {
    "combien": 2,                # dans la bulle du joueur, au plus
    "rayon_px": 480,             # ils naissent hors champ, dans cette bulle
    "casques": ("#e03a2e", "#2f7fd8", "#f1c40f", "#27ae60", "#ff77b7", "#f39c12"),
    "cadres": ("#27ae60", "#c0392b", "#2980b9", "#8e44ad", "#e8e8e8", "#16a085"),
    "chandails": ("#f1c40f", "#e74c3c", "#3a6ea5", "#9b59b6", "#1abc9c", "#ecf0f1"),
}

#: **LES GOELANDS ET LES CHATS.** La vie qui n'est pas humaine.
#:
#: ⚠️ **ILS NE COMPTENT POUR RIEN, et c'est precisement ce qui les rend
#: vivants : ils ne sont la que pour etre la.** Ni temoins, ni victimes, ni
#: foule — on ne peut pas les frapper, ils n'entrent dans aucun index de
#: personnes, la police ne les voit pas et le journal ne les compte pas. Un
#: goeland qu'on pourrait tuer serait une CIBLE, et une cible demande un score,
#: un crime, un juge ; un goeland qui s'envole est un decor qui a peur de vous.
#:
#: ⚠️ **Chacun chez soi**, sinon ce ne sont pas deux betes mais deux sprites :
#: le goeland vit au bord de l'eau (sable, quai, rive) — la ou la 1re vague du
#: bord de l'eau vient de poser des serviettes et des chateaux ; le chat vit
#: dans les RUELLES, entre les hangars.
#:
#: ⚠️ Et **ils partent AVANT qu'on les touche** : leur distance de fuite est
#: plus grande que tout ce qui pourrait les atteindre. C'est ce qui evite
#: d'avoir a repondre a la question « que se passe-t-il si je lui roule
#: dessus » — on n'y arrive pas.
BETES: dict = {
    "goeland": {
        "combien": 6,            # au plus, dans la bulle du joueur
        "fuite_px": 90,          # il s'envole bien avant qu'on l'atteigne
        "envol_images": 150,     # le temps qu'il met a sortir du champ
        "envol_vitesse": 1.9,
        "montee_px": 34,         # de combien il s'eleve pendant son envol
        "pas": 0.22,             # sa demarche, quand il se promene
        "picore_images": (60, 200),
        "marche_images": (40, 140),
    },
    "chat": {
        "combien": 3,
        "fuite_px": 74,
        "detale_images": 120,
        "detale_vitesse": 2.6,
        "pas": 0.5,
        "assis_images": (120, 420),
        "marche_images": (60, 200),
    },
    # ⚠️ LA NUIT A SES HABITUDES : LE RATON LAVEUR. Il ne sort que la nuit
    # (`heures`), dans les ruelles comme le chat, et c'est lui qui sort de la
    # poubelle qu'on fouille a trois heures du matin (`interactions.FOUILLER`).
    # Plus lent que le chat, et il se laisse approcher de plus pres : il a
    # l'habitude des poubelles, pas des gens. Et la nuit, les goelands dorment.
    "raton": {
        "combien": 2,
        "fuite_px": 52,
        "detale_images": 150,
        "detale_vitesse": 2.1,
        "pas": 0.35,
        "assis_images": (100, 320),
        "marche_images": (60, 180),
        "heures": (0.83, 0.26),
    },
    "goeland_dort": True,
    # ⚠️ La bulle des betes est plus PETITE que celle des gens (520) : une bete
    # ne sert a rien qu'on ne la voie pas, et elle ne doit surtout pas peser sur
    # le budget d'images de la rue.
    "rayon_px": 380,
    "oubli_px": 460,
}

#: **LA FOULE DE LA FOIRE.** ⚠️ « Une foire, c'est beaucoup de choses et BEAUCOUP
#: DE MONDE » — Martin, devant une foire a trois passants. La foule de la rue ne
#: suffit pas : elle nait au hasard dans la bulle du joueur et PASSE par la foire
#: sans s'y arreter. Celle-ci nait DANS la foire, y reste, et y fait ce qu'on fait
#: dans une foire : aller d'un kiosque a l'autre, s'arreter devant, regarder.
#:
#: ⚠️ **Jouer, c'est un `metier`, pas un costume** : `forain` a une routine (le
#: kiosque, l'arret, le kiosque suivant), et `mascotte` aussi (deambuler, saluer).
#: Ils ne comptent pas dans la foule de la rue — ils ont un poste, comme l'ouvrier
#: a son chantier — sinon trente forains de plus passeraient par-dessus le
#: plafond de passants de tout le quartier.
FOULE_DE_FOIRE: dict = {
    # ⚠️ Mesure a l'ecran : a trente, la foule s'etalait sur toute l'enceinte et
    # l'ecran n'en montrait qu'une dizaine — « beaucoup de monde » se voyait peu.
    "forains": 45,               # l'exageration est le propos
    "mascottes": 4,
    "par_battement": 6,          # combien en naissent a la fois : la foire se remplit vite
    "rayon_px": 620,             # a quelle distance du bord de la foire elle se peuple
    "arret_images": (100, 320),  # le temps qu'on reste devant un kiosque
    "salut_images": 14,          # la cadence du salut d'une mascotte
}

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
    # ⚠️ ET LE SURSIS : en dessous de tant d'images de patience, un badaud est
    # un PARTANT — on le retient si le cercle tomberait sous le minimum sans
    # lui. Il vaut deux tours de `majSortes` (une image sur quinze), parce
    # qu'une minuterie qui passe sous quinze entre deux tours s'en va sans
    # qu'on l'ait vue venir.
    "sursis_images": 30,
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
    # Il ne crie pas la manchette : il la LANCE. Un mot, de temps en temps.
    "camelot": {"lance": "LE CLAIRON!"},
    "laveur": {"propose": "UN COUP DE CHIFFON?", "merci": "MERCI M'SIEUR"},
    # Le voleur ne dit rien. C'est la VICTIME qui parle — et c'est elle qu'on
    # doit entendre, sinon le vol n'est qu'une animation.
    # ⚠️ Le VOL DE CHAR dit le meme mot : c'est la rue qui parle, pas le
    # voleur, et « au voleur » est deja exactement ce qu'elle crie. Une
    # replique de plus pour le meme cri serait une replique que personne ne
    # peut relier a une sorte — et un juge l'interdit.
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


def _mitoyenne(ra: dict, rb: dict, minimum: int) -> dict | None:
    """Le segment de tuiles que deux rectangles partagent, bord a bord.

    `inverse` dit que c'est `rb` qui est du petit cote (ouest ou nord) : celui
    qui appelle s'en sert pour ranger les deux gangs dans le bon ordre.
    """
    for gauche, droit, inverse in ((ra, rb, False), (rb, ra, True)):
        if gauche["x"] + gauche["l"] != droit["x"]:
            continue
        y0 = max(gauche["y"], droit["y"])
        y1 = min(gauche["y"] + gauche["h"], droit["y"] + droit["h"])
        if y1 - y0 >= minimum:
            return {"axe": "v", "x": droit["x"], "y": y0, "long": y1 - y0, "inverse": inverse}
    for haut, bas, inverse in ((ra, rb, False), (rb, ra, True)):
        if haut["y"] + haut["h"] != bas["y"]:
            continue
        x0 = max(haut["x"], bas["x"])
        x1 = min(haut["x"] + haut["l"], bas["x"] + bas["l"])
        if x1 - x0 >= minimum:
            return {"axe": "h", "x": x0, "y": bas["y"], "long": x1 - x0, "inverse": inverse}
    return None


def frontieres(ville: dict) -> list[dict]:
    """La ou DEUX gangs se touchent : la ligne qui separe leurs districts.

    ⚠️ Elle tient des DEUX fiches et d'aucune seule. Les rectangles viennent de
    `carte`, qui ne sait pas qui tient quoi ; les gangs viennent d'ici, qui ne
    sait pas ou sont les rectangles. C'est `definitions.assembler` qui les marie,
    une fois, au demarrage — et le navigateur n'a plus qu'a lire.

    Une frontiere est une ligne de tuiles : `axe` 'v' (verticale, a la colonne
    `x`, depuis la rangee `y`, sur `long` tuiles) ou 'h' (horizontale, a la
    rangee `y`, depuis la colonne `x`). ⚠️ `a` est TOUJOURS la gang du petit
    cote — l'ouest pour une verticale, le nord pour une horizontale — et `b`
    celle du grand : le navigateur pose chaque camp sur SON bord de la rue, et
    sans cette convention il aurait fallu qu'il le devine a chaque fois.

    ⚠️ Une frontiere trop courte n'en est pas une : deux districts qui ne se
    touchent que par un coin de quelques tuiles n'ont pas de rue mitoyenne, et
    on n'y ferait naitre personne.
    """
    minimum = BAGARRE["frontiere_min_tuiles"]
    rects = {z["slug"]: z for z in ville.get("zones", ()) if not z.get("gang")}
    tenus = [(g["slug"], rects[g["district"]]) for g in GANGS if g["district"] in rects]
    sortie: list[dict] = []
    for rang, (premier, ra) in enumerate(tenus):
        for second, rb in tenus[rang + 1:]:
            ligne = _mitoyenne(ra, rb, minimum)
            if ligne is None:
                continue
            petit, grand = (second, premier) if ligne.pop("inverse") else (premier, second)
            sortie.append({"a": petit, "b": grand, **ligne})
    return sortie


def exporter() -> dict:
    return {
        "catalogue": CATALOGUE,
        "gangs": GANGS,
        "reactions": dict(REACTIONS),
        "vol_de_char": dict(VOL_DE_CHAR),
        "bagarre": dict(BAGARRE),
        "foule_de_foire": {**FOULE_DE_FOIRE,
                           "arret_images": list(FOULE_DE_FOIRE["arret_images"])},
        "betes": {"rayon_px": BETES["rayon_px"], "oubli_px": BETES["oubli_px"],
                  "goeland": {**BETES["goeland"],
                              "picore_images": list(BETES["goeland"]["picore_images"]),
                              "marche_images": list(BETES["goeland"]["marche_images"])},
                  "chat": {**BETES["chat"],
                           "assis_images": list(BETES["chat"]["assis_images"]),
                           "marche_images": list(BETES["chat"]["marche_images"])},
                  "raton": {**BETES["raton"],
                            "assis_images": list(BETES["raton"]["assis_images"]),
                            "marche_images": list(BETES["raton"]["marche_images"]),
                            "heures": list(BETES["raton"]["heures"])},
                  "goeland_dort": BETES["goeland_dort"]},
        "enfants_a_velo": {**ENFANTS_A_VELO,
                           "casques": list(ENFANTS_A_VELO["casques"]),
                           "cadres": list(ENFANTS_A_VELO["cadres"]),
                           "chandails": list(ENFANTS_A_VELO["chandails"])},
        "plage": {**PLAGE,
                  "adultes_archetypes": list(PLAGE["adultes_archetypes"]),
                  "bronzer_images": list(PLAGE["bronzer_images"]),
                  "accroupi_images": list(PLAGE["accroupi_images"]),
                  "barbote_images": list(PLAGE["barbote_images"]),
                  "jeu_images": list(PLAGE["jeu_images"]),
                  "heures": list(PLAGE["heures"])},
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
