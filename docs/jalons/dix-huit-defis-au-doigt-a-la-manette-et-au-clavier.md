# Dix-huit défis au doigt, à la manette et au clavier

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22-23 sept. 2026). Il a d'abord demandé « une série d'idées de défis à réussir
avec une manette ou un clavier pour avancer les missions ou les défis » ; on lui en a proposé
dix-huit. Il a répondu : « parfait, je veux tout ça sur la carte, on doit les voir selon s'il est
possible de les faire avec les doigts ou avec la manette ou le clavier. Je veux qu'ils
n'apparaissent pas tous en même temps, mais graduellement quand on passe des défis ou qu'on avance
dans l'histoire. »

**Trois choses, dans cet ordre** :

1. **Chaque défi dit avec quoi il se joue** : `appareils` dans `missions.DEFIS`, une liste parmi
   `doigts`, `manette` et `clavier`. Les dix défis déjà livrés se jouent avec les trois. Un défi neuf
   n'en exclut un que pour une raison **mécanique**, écrite à côté de lui :
   - le **clavier** est tout ou rien : il ne dose ni le gaz ni un angle (huit directions) ;
   - le **doigt**, c'est un seul stick virtuel et quatre boutons : il dose, mais il enchaîne mal les
     appels rapides qui alternent direction et bouton ;
   - la **manette** fait tout, et elle vibre.
2. **Les défis sont sur la carte** (la grande carte, touche N) : un drapeau par défi **débloqué**. Sa
   couleur dit s'il se joue avec **l'appareil qu'on tient** (`Entree.appareil`). Sur la carte, ARME
   change le filtre : l'appareil qu'on tient, puis les deux autres, puis TOUS. Un filtre d'appareil
   ne montre que les défis jouables avec lui, et l'en-tête dessine l'appareil choisi. La proposition
   du défi (COMMENCER / PAS MAINTENANT) dit aussi « SE JOUE AU DOIGT · À LA MANETTE · AU CLAVIER »,
   et prévient quand l'appareil qu'on tient n'y est pas.
3. **Ils arrivent peu à peu** : `debloque` dans le catalogue. Ce sont des conditions qui doivent
   toutes tenir : un nombre de défis réussis (`defis`), des missions faites (`missions`), des défis
   précis réussis (`apres`). Un défi débloqué s'annonce (« NOUVEAU DÉFI »), s'inscrit au journal et bat
   sur la carte tant qu'on n'a pas lu son panneau. Les dix défis de la v1 n'ont pas de `debloque` :
   on ne cache pas ce que le joueur avait déjà.

**Les dix-huit**, par vague. Chacune est jouable, jugée et atterrie avant la suivante.

**Vague 1 — le socle et les jeux debout** (`a_pied`, un nouveau module `adresse.js` : une épreuve
dessinée par-dessus la ville, qu'on joue debout devant son panneau ou son comptoir) :

| Défi | Où | Débloqué par | Appareils | Le geste |
|---|---|---|---|---|
| La roue de Madame Thibodeau | porte du kiosque | 1 défi réussi | les trois | ACTION freine la roue ; elle doit s'arrêter sur le gros lot (3 essais) |
| Le lancer d'anneaux | foire, `lance_anneaux` | 3 défis | les trois | tenir ACTION charge, relâcher dans la bande verte (5 anneaux) |
| Les ratons du kiosque à peluches | foire, `peluches` | 3 défis | les trois | trois trous sur la croix (gauche, haut, droite), taper celui du raton |
| La danse du Bonimenteur | foire, `ballons` | mission `p13` | manette, clavier | « HAUT ! GAUCHE ! FRAPPE ! » de plus en plus vite (doigt exclu : le stick doit revenir au centre entre deux appels) |
| Le mannequin à clochettes | porte du magasin de vêtements | mission `m6` | les trois | une aiguille oscille ; ACTION dans la zone verte, sinon la clochette sonne |
| La radio de la police | porte du poste | mission `m4` | les trois | gauche/droite accorde la fréquence ; la tenir jusqu'à ce que la voix sorte du grésillement |
| Le vieux camion de la cantine | porte de la cantine | mission `e01` | les trois | le moteur tousse en cadence ; ACTION sur chaque toux, cinq de suite |
| Le cadenas de l'armurier | porte de l'armurerie | mission `m53` | manette, doigt | le stick cherche un angle ; tout près, le cadenas tremble (et la manette vibre) ; on tient, la goupille tombe (clavier exclu : ses huit directions ne tombent jamais sur l'angle) |
| Le coffre du bar | porte du bar | mission `m54` et le cadenas réussi | manette, doigt | quatre directions à reproduire, puis deux goupilles au stick, en 60 s |

**Vague 2 — au volant** :

| Défi | Débloqué par | Appareils | Le geste |
|---|---|---|---|
| Le frein pile | 1 défi | les trois | lancé, s'arrêter dans une case peinte d'une tuile |
| Le démarrage au feu | mission `m1` | les trois | partir au vert ; partir avant, c'est un faux départ |
| Le créneau | mission `m3` | les trois | se garer entre deux chars en 20 s, sans toucher personne |
| Le slalom des cônes | 5 défis | les trois | une chicane de cônes ; chaque cône renversé coûte 2 s |
| Le verre de lait | la livraison réussie | manette, doigt | aller au bar sans que le lait déborde : aucun coup de gaz ni de frein brusque (clavier exclu : tout ou rien) |
| Le remorquage | mission `f08` | manette, doigt | tirer un char jusqu'à la fourrière ; un frein brusque le met en portefeuille |

**Vague 3 — dans la rue** :

| Défi | Débloqué par | Appareils | Le geste |
|---|---|---|---|
| La filature | mission `f06` | les trois | rester entre 3 et 6 tuiles de quelqu'un : trop près il se retourne, trop loin on le perd |
| L'esquive du Grand Mo | mission `f04` | les trois | 30 s contre Mo, sans frapper une seule fois : on ne fait qu'esquiver |
| Le défi du chef | le créneau, le frein pile et le slalom réussis | les trois | les trois d'un seul souffle |

⚠️ **Contraintes connues** :

- **Aucun panneau neuf ne nomme une porte neuve.** `devants.lieux_de_mission` lit `missions.DEFIS` :
  une porte que rien ne nommait élargirait son devant, et toute la ville glisserait (voir
  « Grossir un lieu garanti déplace la ville »). On ne prend que des lieux déjà nommés.
- **Un panneau neuf ne naît qu'une fois son défi débloqué**, en fin d'image. Une partie neuve ne
  crée aucune entité de plus au démarrage, et les numéros tirés à l'empreinte ne bougent pas.
- **Le défi du jour ne tourne que sur les défis sans `debloque`** : la rotation d'aujourd'hui ne
  change pas, et le serveur, qui ne connaît pas la partie, ne désigne jamais un défi encore caché.
- **La triche SAUT VERS UN DÉFI débloque le défi qu'elle vise** : c'est une triche.

## Notes

### Vague 1 — le socle et les neuf épreuves debout (23 sept. 2026)

- **Le catalogue** : `appareils` sur chaque défi (les trois par défaut, `missions.APPAREILS`) ;
  `debloque` (`defis`, `missions`, `apres`) ; `epreuve` et `regles` pour les neuf jeux debout.
  Les chiffres d'une épreuve vivent dans `regles`, pas au premier niveau, où `coups`, `canards` et
  `cibles` parlent déjà aux jeux de la foire. Les trois nouveaux jeux de la foire n'ont **pas**
  `foire: True` : ce drapeau fait le lot de la casquette, et on ne demande pas six jeux à qui l'a
  gagnée avec trois.
- **Le défi du jour** ne tourne que sur les dix défis sans `debloque` (`defi.rotation`) : la rotation
  d'avant ne bouge pas d'un jour, et le serveur ne désigne jamais un défi qu'un joueur neuf ne voit
  pas encore.
- **Le déblocage** (`Histoire.majDeblocages`, une fois par seconde, jamais dans une pièce ni pendant
  une scène) : un défi ouvert entre dans `partie.defisOuverts` (`{ jour, lu }`), s'inscrit au journal
  (« NOUVEAU DÉFI : … ») et s'annonce, en une seule ligne quand plusieurs s'ouvrent ensemble. Son
  **panneau naît à ce moment-là** (`poserPanneau`), jamais au démarrage. Deux panneaux restent à
  trois tuiles l'un de l'autre (`PANNEAUX_ECARTES`). Un défi ouvert le reste, et la triche SAUT VERS
  UN DÉFI ouvre celui qu'elle vise (nouvelle rubrique DEBOUT, et « CACHÉ » à côté d'un défi fermé).
- **La foire** apprend ses kiosques qui jouent (`Foire.comptoirs`) : le lance-anneaux, les peluches
  et les ballons. Tant que leur défi est caché, ils restent des kiosques (`defiDuComptoir`).
- **La proposition** du défi dit « SE JOUE : » avec les trois appareils dessinés (`Hud.iconeAppareil` :
  un doigt, une manette, un clavier), souligne celui qu'on tient, et prévient « PAS AVEC CE QUE TU
  TIENS ».
- **La carte** : un drapeau par défi ouvert (cyan : jouable avec le filtre ; vert : réussi ; gris :
  pas avec ce que tu tiens, en TOUS), qui bat tant qu'on n'a pas lu son panneau. En haut à gauche :
  l'appareil du filtre, le nombre de défis, et combien restent « À DÉCOUVRIR ». **ARME** tourne le
  filtre (l'appareil qu'on tient, les deux autres, TOUS) ; la carte se rouvre sur ce qu'on tient.
- **Les épreuves** (`adresse.js`) : la roue, les anneaux, les ratons, la danse, le mannequin, la
  radio, le moteur, le cadenas et le coffre. Même axe que le piratage, `B.epreuve` cloue le joueur et
  affame le combat, l'entrée en char et le décor, et ESQUIVE (COURS, B, MAJ) abandonne. Les douze
  premières images ne lisent rien : l'appui de COMMENCER y est encore neuf. Un coup reçu arrête
  l'épreuve. La boîte se dessine **sous** le joueur, parce qu'au milieu elle le cachait (capture).
- ⚠️ **Le cadenas exclut vraiment le clavier.** Chaque goupille se cache à 22,5° ± 4° d'une des huit
  directions, et la tolérance est de 9°. Un juge essaie les huit directions sur beaucoup de
  goupilles : zéro. Le stick virtuel du doigt, lui, y arrive (un autre juge le fait au pointeur).
- **Juges** : `test_defis_graduels_js.py`. Chaque épreuve se gagne au bouton avec un joueur parfait
  qui lit l'état et appuie au clavier (ou pousse le stick pour le cadenas). Chacune se rate sans rien
  faire, et se rate aussi avec un **joueur maladroit** qui appuie au mauvais moment : sans lui, une
  règle qui laisse tout passer dès qu'on appuie restait verte. S'y ajoutent l'abandon, le joueur
  figé (les quatre directions et sa vitesse, parce que face au comptoir il ne bougeait déjà pas), les
  paliers de déblocage, la sauvegarde, la carte et son filtre ARME, et le kiosque caché. Côté Python
  (`test_missions.py`) : les appareils, ce que `debloque` nomme, **aucune porte neuve**, les règles
  d'une épreuve. Vingt mutations : toutes rouges, sauf une. Pour le moteur, une toux ratée est
  rattrapée deux fois (la marge, puis « IL CALE ») : c'est une protection double, pas un juge aveugle.
- Captures Chromium : la proposition, les neuf épreuves, la carte dans ses quatre filtres.

### Vague 2 — les six au volant (23 sept. 2026)

- **`conduite.js`** joue les épreuves au volant (`conduite` et `regles` au catalogue) : le frein
  pile de l'hôpital, le démarrage du terminus, le créneau devant la planque, le slalom de l'hôtel,
  le verre de lait de Lulu (de la cantine au casse-croûte) et le remorquage de la fourrière.
- **Un bout de rue droit, sans croisement** (`pisteDroite`) : les tuiles d'une même voie à la file,
  cherchées autour du panneau, la plus proche, sans dé. Les portes ont été **choisies à la mesure** :
  une ligne droite de 12 tuiles à trois pas de l'hôpital et du terminus, 10 tuiles de voie du bord
  devant la planque, 30 tuiles à cinq pas de l'hôtel. Le créneau prend la **voie du bord**, celle
  qui n'a pas de chaussée à sa droite.
- **Les marques sont peintes au sol**, pas posées : la ligne de départ (un damier sur toute la
  voie ; plus fine, elle disparaissait sous le char arrêté dessus), la case du frein pile, la place
  du créneau, l'arrivée. **Les cônes aussi** : peints et heurtés par la géométrie, sans entité, pour
  ne prendre aucun numéro. Le feu (trois rouges, puis le vert) et les jauges (le verre, la fourche)
  se dessinent en haut de l'écran.
- **Les chars posés par une épreuve** (les deux autos du créneau, la remorqueuse, l'épave) sont
  `mission` : la ville ne les oublie pas, la fourrière ne les prend pas. Leur couleur est donnée,
  donc `Vehicules.creer` ne tire aucun dé. `Conduite.fermer` les retire à la fin, sauf celui qu'on
  conduit. ⚠️ `Entites.retirer` ne touche pas `actif` : c'est la liste qui dit si un char est encore
  là (`present`).
- **Le feu se mesure au char qu'on conduit** : son temps idéal pied au plancher (sa physique,
  `tempsIdeal`), plus un réflexe de 0,45 s, plus 20 %. Avec un chiffre fixe (2,4 s), l'autobus y
  mettait 2,3 s sans réflexe du tout, et la pelleteuse n'y arrivait jamais. Le juge le vérifie de la
  moto à la pelleteuse : un tiers de seconde de réflexe gagne, une seconde perd.
- **Le slalom** : des cônes aux 4 tuiles sur la ligne du milieu, à droite du premier, à gauche du
  suivant. Aux 3 tuiles, une auto réelle (rayon de braquage 22, volant qui se tourne) les renversait
  tous : le pilote du banc n'y arrivait pas.
- **Le verre de lait et le remorquage excluent le clavier, et la physique le dit.** Les à-coups se
  lisent **sur la commande** (`Vehicules.commandesJoueur`), pas sur la vitesse : lancée, une auto
  perd par la friction autant qu'elle gagne au gaz. Au-delà de 70 % de gaz, 60 % de frein ou d'un
  volant trop serré pour la vitesse, le verre déborde. Une touche, c'est 100 % : un départ et un
  arrêt au clavier vident le verre (juge), pendant que la gâchette à 60 % n'en renverse pas une
  goutte. Sur la fourche, un coup de frein franc **lancé** fait lâcher l'épave ; au pas, le même
  coup de frein dure trop peu pour secouer.
- **Le remorquage** : la remorqueuse attend sur la rue la plus proche (la fourrière est au fond d'une
  cour qui ne touche aucune rue), et l'épave est à 22 tuiles **de la cour**. Le klaxon l'accroche (le
  crochet existant) ; on la livre **dans la cour** (`Missions.dansLaCour`, la règle du boulot). ⚠️ Le
  même klaxon prenait aussi le **boulot** de remorquage (« LA FOURRIÈRE NE PAIE QUE LES ÉPAVES ») :
  pendant un défi, le boulot se tait.
- **Juges** : un pilote au banc qui conduit **par la manette** (les gâchettes analogiques et le
  stick de la disposition standard), qui tient sa voie et freine au pixel près (⚠️ sous 0,15 px/image,
  le frein devient la marche arrière et ralentit moins fort, et il faut le compter). Pour le frein
  pile : gagné, trop loin, trop court, refusé au pas. Pour le feu : gagné au vert, raté avant, et
  mesuré au char. Pour le créneau : la place à la mesure du char, gagné garé droit, raté en
  accrochant. Pour le slalom : gagné en zigzag, raté tout droit. Pour le verre de lait : la gâchette
  contre le clavier, et la livraison. Pour le remorquage : les deux chars posés, l'accrochage,
  « arrêté hors de la cour ne livre rien », et le coup de frein. Treize mutations : toutes rouges, une
  fois deux juges resserrés (le créneau exige « TU AS ACCROCHÉ » ; le feu a deux gardes, l'arrivée et
  le chrono, et chacune mord seule).
- Captures Chromium : les cinq épreuves qui ont une piste ou une jauge.
- ⚠️ **La vague 1 avait laissé un rouge sur `dev`** : `test_carte_du_depot` voulait
  `test_defis_graduels_js.py` dans l'arborescence de `docs/architecture.md`. Corrigé à part
  (`cf49706`), dès que la suite complète l'a montré. Les autres rouges de cette suite sont ceux déjà
  connus sur `dev` (voir le jalon des menus à onglets).
