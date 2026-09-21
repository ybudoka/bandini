# Le bord de l'eau et la foire

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le bord de l'eau et la foire (**ajout**, taille 4)_

_Demande de Martin (15 sept. 2026) :_ « je veux des belvédères, table à pic nic, des plages
parasol, enfants qui joue, château de sable, etc. des sea doo, ski nautique, bateau, quai.
un parc d'attraction avec grande roue, jeu d'adresse, manèges, etc. »

⚠️ **Mesuré d'abord, et c'est la même surprise que pour l'île : la plage existe déjà.** Sur la
graine livrée, le sol compte **2 507 tuiles de sable**, dont **782 touchent l'eau** — une grève
qui court tout le long de la baie, des Quais à La Pointe — et **1 818 tuiles de quai**. La
ville pose **1 701 décors**, de **treize** sortes : arbre (705), buisson, lampadaire, poubelle,
caisse, banc, débris, borne-fontaine, cabanon, corde à linge, guichet, BBQ, fontaine. Aucun
n'est une table à pique-nique, un parasol, un belvédère ou un château de sable ; **personne ne
s'assoit jamais sur les 782 tuiles de grève**, et **aucune coque n'est amarrée aux 1 818 tuiles
de quai**.

Ce qui manque n'est donc pas le terrain : c'est que **le bord de l'eau est un décor qu'on
traverse**, et la demande est d'en faire un endroit **où on va**.

**Quatre vagues, et elles ne coûtent pas du tout la même chose.** La première ne touche à aucun
moteur ; la deuxième non plus, mais elle décide de ce que les enfants ont le droit de vivre ;
la troisième attend une dette nommée depuis M3 ; la quatrième est un jalon à elle seule.

### 1re vague — la grève se meuble (taille 1, aucun moteur neuf)

Six fiches `DECORS` de plus et une passe de semis sur le sable — exactement le chemin des
terrains de banlieue (cabanon, corde à linge, BBQ, livrés le 14 sept.), et rien de plus :

- **la table à pique-nique** : deux bancs et un plateau ; vue d'en haut, c'est un **H couché**,
  et c'est ce qui la nomme à douze pixels. `casse`, comme le banc ;
- **le parasol** : la seule chose du lot qui se lise **de loin**, et la seule qu'on ne heurte
  pas — `solide: false`, on passe dessous. Rayé, sa couleur tirée par tuile ;
- **la serviette et sa glacière** : ⚠️ un **décal** au sol (`DECALS` existe pour ça), pas une
  entité. Rien ne l'arrête, rien ne la casse, et elle ne pèse rien dans le hachage spatial ;
- **le château de sable** : ⚠️ le seul du lot qui ait une **règle**. Le décor le plus fragile de
  la table (`pv` 5) — un char qui roule sur la grève le rase — et il **revient au matin** avec
  tout le reste (`reparerLeDecor()`). Un enfant qui recommence son château tous les jours, c'est
  une blague que la ville raconte sans qu'on l'écrive ;
- **la bouée** et **le poteau d'amarrage**, sur le quai ;
- **le belvédère** : un plancher de bois sur pilotis, une rambarde, deux marches, posé là où la
  terre domine l'eau — le bout de La Pointe, la tête du pont, la falaise des Érables. Il
  **arrête** (comme les kiosques) au lieu de bloquer : on y monte, on ne le traverse pas.

⚠️ **Une plage suit la côte ; elle ne suit pas une boîte.** La phrase est déjà dans `_eau()`, et
elle a coûté douze bancs de sable en pleine baie : le semis doit marcher **tuile par tuile**, en
regardant si l'eau est à deux tuiles de là — jamais sur le rectangle du bassin. Un parasol
planté au milieu d'un sentier du bois dit le contraire de ce qu'on veut.

⚠️ **`poser_decor` ne connaît pas l'eau.** Il refuse le solide, le routier, le devant de porte
et le réservé, parce qu'aucun décor n'a jamais eu à flotter. Il faut le lui apprendre une fois —
sinon la bouée est le seul décor du jeu à avoir raison de flotter, et tous les autres l'imitent.

### 2e vague — les enfants jouent (taille 1)

L'enfant existe depuis la v1 : `intouchable`, vitesse 1,15, témoin 0,5, et il détale de **douze
tuiles** (`enfant_peur_tuiles`). Il n'a aucune routine — il marche comme tout le monde, en plus
petit et en plus vite.

⚠️ **Jouer, c'est un `metier`, pas un costume.** La règle des « sortes de gens » est écrite trois
fois dans `pietons.py`, et le dépôt l'a déjà payée une fois avec les filles de la Brume : une
sorte sans routine est un déguisement. Trois routines, toutes branchées sur ce qui existe :

- **le château** : il s'accroupit devant un décor `chateau_sable`, il y revient, et si le château
  n'y est plus il en recommence un ailleurs ;
- **la baignade** : depuis que l'eau n'est plus un mur (14 sept.), un piéton peut y entrer. Les
  enfants pataugent dans la **première tuile** et pas plus loin. ⚠️ **Un enfant ne se noie pas** :
  `intouchable` dit aujourd'hui « aucune arme, aucun char » ; il doit dire aussi « pas l'eau »,
  sinon la plage est une trappe à noyade et le jeu devient autre chose ;
- **le ballon** : deux enfants et un ballon qui va de l'un à l'autre. C'est tout, et ça suffit —
  un décor qui bouge se voit de trois écrans.

⚠️ **Une plage pleine d'enfants est une plage pleine de TÉMOINS** (0,5 chacun). C'est la seule
conséquence mécanique de la vague, et elle est bonne : la grève devient le plus mauvais endroit
de la ville pour faire un coup, exactement comme l'attroupement de l'amuseur.

### 3e vague — l'eau porte enfin quelque chose (taille 2, ⚠️ **bloquée**)

`vehicules.py` déclare déjà **la chaloupe** : `eau=True`, friction 0,995, adhérence 0,05, trois
cercles — et **`phase=2`**, « sans sprite et sans trafic », parce que l'eau demande une physique
à part. Le sea-doo et le bateau de ski ne sont pas trois dettes : c'est **la même**, payée une
fois.

⚠️ **Rien ne se met à l'eau tant que le char ne tient pas son cap sur la terre ferme.** « Le char
tourne comme son ombre » est **P1 et en cours** ; une coque qui dérape est le pire endroit du
monde où découvrir un défaut de cap.

Ce que l'eau demande une fois, et ce qui en découle ensuite :

- **une coque** : pas de freins, de la dérive, un sillage, et une vitesse qui ne tient qu'au
  moteur. La fiche de la chaloupe l'a déjà chiffrée ; il reste à la faire flotter ;
- **la mise à l'eau** : `_quai()` pose déjà une rampe de débarquement « là où un quai en porte
  vraiment une ». La porte entre les deux mondes existe — personne ne l'a jamais franchie ;
- **le sea-doo** : la moto de l'eau. Il `ejecte` comme elle, il est rapide, il ne pardonne rien,
  et c'est le seul véhicule du jeu dont la chute ne coûte que l'orgueil ;
- **le ski nautique** : ⚠️ **c'est un crochet, pas un véhicule.** La liaison existe (`crochet`,
  la remorqueuse de M9), avec une épave au bout ; ici c'est un piéton. Et elle donne à la baie
  son premier **spectacle** : un bateau qui passe au large avec quelqu'un derrière ;
- **des coques amarrées** sur les 1 818 tuiles de quai, qu'on peut prendre — et c'est ce qui rend
  **L'Île-aux-Corneilles** (fiche suivante) atteignable autrement qu'à la nage ;
- ⚠️ **la police n'a pas de bateau.** Deux sorties, et il faut en choisir une **exprès** : au
  large, les étoiles **descendent** (comme sur l'île), ou la Sûreté a une vedette et c'est un
  jalon de plus. Le plan choisit la première — et l'île a déjà écrit pourquoi : un endroit sûr
  qui n'a qu'un chemin de retour n'est pas un endroit sûr, c'est un piège qu'on choisit.

### 4e vague — la foire de La Pointe (taille 2)

**Où.** La Pointe est le district-parc, et son plan porte **deux grandes taches de bois** de
quatre blocs de large sur deux de haut. La foire en prend **une**. ⚠️ On n'agrandit pas la
grille : la leçon de l'île vaut ici aussi — la ville a la place, il faut la **dépenser**. Un
glyphe de plan de plus (`f`), un `_foire()` à côté de `_parc()` et `_place()`, une allée
centrale en terre battue, et la grève juste en dessous.

- **La grande roue** — la seule vraie idée de la vague. ⚠️ **Ce n'est pas un manège, c'est un
  belvédère qui tourne.** On paie, le fondu des portes joue (livré), la caméra monte, et la ville
  est là, en dessous, avec ses lumières si c'est le soir. Ce qu'on redescend avec : **les paquets
  cachés qu'on n'a pas trouvés clignotent sur la mini-carte jusqu'au soir**. Les vingt paquets
  existent, ils ne sont marqués nulle part, et `carte.paquets()` dit en toutes lettres que « les
  trouver doit faire visiter la ville » — un point de vue qui montre la ville est exactement la
  bonne façon de les donner. Une fois par jour, et ça se paie.
- **Les manèges** (carrousel, tasses, chaises volantes) : ⚠️ **du décor animé, et on n'y monte
  pas.** Un manège où l'on monte et qui ne donne rien est un décor cher ; un manège qui tourne
  avec du monde dessus est une ville qui vit. C'est l'étage 1 des machines de chantier, mot pour
  mot : une articulation, pas dix — un socle cuit une fois, des nacelles peintes par-dessus à
  chaque image.
- **Les jeux d'adresse** : ⚠️ **un jeu d'adresse est un défi, pas un moteur.** `missions.DEFIS`
  en porte trois depuis la v1 (le saut, le tour, la livraison) : un lieu, un compte, un chrono,
  une prime, un texte en majuscules. Trois de plus sur les mêmes rails — **la galerie de tir**
  (les armes existent, une cible est un décor avec des `pv`), **le marteau de force** (marteler
  ACTION contre un chrono : aucune statistique neuve, c'est le bouton qui fait la force), et **la
  pêche aux canards**, qu'on peut gagner mais pas voler. La prime : de l'argent, et au troisième
  palier une **casquette de la foire** — le vestiaire existe (`magasins.TENUES`) et ne demande
  rien à personne.
- **Le son, et ce n'est pas un détail** : ⚠️ une foire muette est une peinture. L'orgue de manège,
  les cris, les vagues et le moteur du sea-doo sont quatre pistes ElevenLabs de plus
  (`app/audio.py`, `app/musique.py`). Le chemin est déjà tracé : **le musicien de rue est « une
  musique qui sort de QUELQU'UN »**, avec son gain à lui, par-dessus l'ambiance du district et
  sans prendre le rang de personne. L'orgue de la foire est **une musique qui sort d'un
  ENDROIT** — le même code, une source fixe. Surtout pas une ambiance de district de plus.

**Ce que ça coûte ailleurs**, et il faut le dire avant de dessiner : six à dix fiches `DECORS`
(du JS, pas du paquet), un glyphe de plan, un `metier` de plus, trois défis, quatre pistes audio
— et ⚠️ **aucun juge de géométrie ne parle du sable**. Un décor de plage vit à deux tuiles de
l'eau, là où aucun décor n'allait jamais ; c'est une ligne de juge à écrire **exprès**, pas à
découvrir.

**Juges** : aucun décor de plage à plus de trois tuiles du sable, et aucun sur l'eau ; un château
de sable se casse et revient au matin ; un enfant ne dépasse jamais la première tuile d'eau et
rien ne le tue ; la foire tient dans son bloc et n'avale aucune rue ; on ne monte dans la grande
roue qu'en payant, une fois par jour, et ce qu'elle révèle s'éteint le soir ; aucun manège n'est
montable ; un défi de foire ne paie pas mieux à l'heure qu'une mission (la règle des paliers de
boulot) ; aucune coque ne roule sur la terre et aucun char ne flotte ; et un enfant reste
intouchable, sur la grève comme ailleurs.

## Notes

demande de Martin : « des belvédères, table à pic nic, des plages parasol, enfants qui joue,
château de sable, etc. des sea doo, ski nautique, bateau, quai. un parc d'attraction avec
grande roue, jeu d'adresse, manèges, etc. »

- ⚠️ **Mesuré : la plage existe déjà** — 2 507 tuiles de sable (dont 782 au bord de l'eau),
  1 818 tuiles de quai, 1 701 décors de treize sortes, et pas un parasol, pas une table, pas
  une coque amarrée. Quatre vagues : **la grève se meuble** (six `DECORS`, aucun moteur
  neuf) ; **les enfants jouent** (un `metier`, trois routines — et ⚠️ un enfant ne se noie
  pas) ; **l'eau porte enfin quelque chose** (⚠️ **bloqué** : la chaloupe est `phase=2` et
  « Le char tourne comme son ombre » est P1 en cours ; le ski nautique est un `crochet`, pas
  un véhicule) ; **la foire de La Pointe** dans un de ses deux blocs de bois — la grande
  roue est un **belvédère qui tourne** (elle montre les paquets cachés), les manèges sont du
  décor animé qu'on ne monte pas, les jeux d'adresse sont des `DEFIS`.

✅ **1re vague livrée** (16 sept. 2026) — *la grève se meuble*, à la demande de Martin (« je
veux que tu fasses la plage »). Six fiches `DECORS` et un semis, **aucun moteur neuf** :
table à pique-nique (un **H couché** vu d'en haut), parasol, serviette et sa glacière,
château de sable, bouée, poteau d'amarrage, belvédère — **174 meubles** sur la graine
livrée.

- ⚠️ **Une plage suit la côte ; elle ne suit pas une boîte** : le semis marche tuile par
  tuile et ne meuble que du sable qui a l'eau à trois tuiles.
- ⚠️ **Le château est le seul du lot qui ait une règle** — `pv: 5`, le décor le plus fragile
  du jeu, rasé par un char et **revenu au matin**.
- ⚠️ **Le parasol est le seul qu'on ne heurte pas** : on passe dessous.
- ⚠️ **La bouée est le premier décor du jeu à flotter**, et ça a demandé deux choses :
  `poser_decor` refuse le solide et l'eau **en est** (`solide: 2`) — on le lui accorde par
  demande explicite (`sur_eau`) plutôt qu'en ouvrant l'eau à tout le catalogue ; et le juge
  de M1 « tout décor est sur une tuile marchable » l'a arrêtée net. **Ce juge a raison sur
  le fond — ce n'est pas lui qu'on jette, c'est l'exception qu'on déclare** :
  `carte.FLOTTANTS` vit en Python, le paquet la porte, et un juge de banc vérifie que le
  `flotte` des fiches de dessin dit exactement la même chose.
- ⚠️ **Mesure qui a tout réorienté** : le glyphe `Q` n'est pas un ponton, c'est le **pavage
  du district des Quais** — **16 de ses 1 818 tuiles touchent l'eau**. Un poteau semé « sur
  le quai » se plantait six tuiles à l'intérieur des terres, ou nulle part (0 poteau, 0
  bouée au premier essai). Ce qui amarre un bateau n'est pas un glyphe, c'est une **rive** :
  une tuile où l'on marche, ni sable ni route, avec l'eau devant — 222 tuiles, dont **199 de
  trottoir**. Et le trottoir ne porte pas `terre` dans la légende : tester la propriété au
  lieu de la marchabilité laissait dehors 199 des 222.
- ⚠️ **Un crochet de variante par tuile** : le décor est cuit **une fois par type**, donc
  sans lui tous les parasols de la ville sont du même rouge. Le mécanisme existait pour les
  `DECALS` (`d.v`) ; c'est la première fiche de décor à en avoir besoin — et la variante se
  tire à l'**empreinte de la tuile**, jamais au dé du jeu.
- ⚠️ **Deux dessins jetés après les avoir REGARDÉS** (rendus au navigateur, pas devinés) :
  le château était une **motte beige** — tours et courtine du même sable — et le belvédère
  une **caisse**. Ce qui nomme un belvédère vu d'en haut, c'est la rambarde sur **trois**
  côtés et la trouée du sud par où l'on monte : un plancher fermé est une boîte, un plancher
  ouvert d'un côté est un endroit où l'on va.
- ⚠️ **Et une précaution nommée comme telle** : le semis passe après `boucher_les_poches`
  (on ne meuble pas un terrain que la ville va retirer), mais **mesuré sur huit graines et
  1 139 meubles, semer avant n'en noie aujourd'hui aucun** — le juge n'y répare rien, il
  épingle l'ordre. 13 juges neufs, rouge-avant prouvé deux fois, et le juge de l'écart en a
  attrapé un troisième en vol (un belvédère posé contre un parasol) ; 1659 tests.

✅ **2e vague livrée** (16 sept. 2026) — *les enfants jouent*.

- ⚠️ **Jouer, c'est un `metier`, pas un costume** : l'enfant existait depuis la v1 et
  n'avait jamais rien fait d'autre que marcher. Trois routines branchées sur ce qui existe —
  le **château** (il y revient, et s'il n'y est plus il s'en cherche un autre), la
  **baignade**, le **ballon** entre deux enfants.
- ⚠️ Ce ne sont **pas** tous les enfants de la ville : ceux-là naissent sur la grève et y
  restent. Donner un `metier` à l'archétype les aurait tous sortis de la foule et aurait
  rendu muette la mère qui promène le sien.
- ⚠️ **UN ENFANT NE SE NOIE PAS** — et mesure, pour ne pas s'attribuer un correctif :
  **aucun piéton ne se noie dans le jeu**, le souffle et `noyade` n'existent que pour le
  joueur. Le juge n'y répare rien, il **épingle** la garantie.
- ⚠️ Et ce qui la tient n'est **aucun des deux gardes écrits pour ça** : c'est qu'on ne
  donne jamais à un enfant de destination au-delà de la première tuile, et qu'il
  s'immobilise dès qu'il y a le pied — neutraliser l'un ou l'autre ne fait tomber aucun
  juge, et les deux sont commentés comme des **ceintures**.
- ⚠️ **Le juge qui passait à vide** : il annonçait « il ne dépasse jamais la première
  tuile » et il passait sur une plage où **personne n'entrait jamais dans l'eau** — `cap`
  s'arrête à 12 px de son but (un palier écrit pour le pickpocket) et une tuile en fait 16,
  donc l'enfant s'immobilisait *avant* de se mouiller les pieds. Une ligne de plus au juge
  (« il faut qu'ils y soient entrés »), et le défaut est tombé tout seul.
- ⚠️ **Et la leçon des dés, payée une troisième fois cette semaine** : la naissance des
  enfants tirait quarante couples dans `B.rng()` — **le pickpocket a cessé de voler**, et le
  budget de la foule a sauté. Un juge qui ne parle pas de plage, tombé parce que chaque dé
  consommé décale tous ceux qui suivent. Le semis balaie maintenant la bulle en spirale, le
  choix du jeu se tire à l'empreinte de l'enfant, et **plus un seul dé**.
- ⚠️ **Le ballon vole dans la boucle des entités, pas dans la routine** : les routines
  battent une image sur quinze — mesuré, le ballon ne bougeait que 13 images sur 400 et
  sautait par à-coups d'un quart de seconde. Et il lui faut de la **distance** : deux
  enfants collés ne se lancent rien, la balle arrive avant d'être partie.
- ⚠️ **Un enfant oublié emporte son ballon**, sinon la balle vole toute seule pour toujours.
- ⚠️ **Un juge existant resserré plutôt qu'affaibli** : « aucun passant ne se met à l'eau »
  a raison sur le fond — une flânerie qui mène à la baie ne se voit qu'en jeu —, donc ce
  n'est pas lui qu'on jette, c'est l'exception qu'on **nomme**.
- ⚠️ **Et un défaut de la 1re vague trouvé par le juge du PONT** : une serviette et deux
  bouées s'étaient posées à une tuile du tablier de La Pointe, et un char lancé les
  accrochait — le juge a vu la carrosserie tomber à 90 sur 100 *après* l'ouverture du pont
  et en a conclu que le pont coûtait encore. Un quai n'est pas une plage, et le pied d'un
  pont non plus (`FERMETURES` le disait déjà pour les rues barrées). 5 juges neufs,
  rouge-avant prouvé trois fois ; 1669 tests.

✅ **3e vague livrée** (16 sept. 2026) — *l'eau porte enfin quelque chose*, **la dette de
M3**.

- ⚠️ « Phase 2 » voulait dire « sans sprite et sans trafic », et le plan annonçait une
  **physique à part** : mesuré, il n'en fallait aucune. La fiche de la chaloupe existait
  depuis M3 (eau, friction 0,995, adhérence 0,05, trois cercles) et `majNoyade` l'exemptait
  déjà du naufrage depuis que l'eau n'est plus un mur. Il manquait **un dessin et une règle
  de tuile**.
- ⚠️ **Un char et une coque ne sont pas arrêtés par les mêmes choses**, et c'est toute la
  différence entre les deux mondes : le char est arrêté par les murs et **passe** sur l'eau
  (il coule, c'est son affaire) ; la coque est arrêtée par **tout ce qui n'est pas de
  l'eau**. Une ligne dans `tuileInterdite`, pas une classe — un masque est une liste de ce
  qui bloque, et la règle du bateau est l'inverse : une liste de ce qui laisse passer, et
  elle n'a qu'une entrée.
- ⚠️ **18 amarrages** contre la rive **bâtie**, jamais le sable (on amarre à un quai, on
  n'amarre pas à une plage — on y échoue) et jamais au pied d'un pont, la règle que le juge
  du pont avait déjà trouvée pour le mobilier de grève. Elle ne naît **pas dans le trafic**
  (`frequence: 0`) : une chaloupe sur la rue Principale est exactement ce que la règle de
  tuile interdit.
- ⚠️ **La leçon des dés, une cinquième fois** : les coques tiraient un dé pour leur couleur,
  et **onze juges sans rapport sont tombés d'un coup**. Empreinte de l'amarrage, comme la
  panne, le pilote des deux-roues et les enfants de la grève.
- ⚠️ Et une heure perdue à chasser huit défauts **qui n'étaient pas les miens** :
  `app/carte.py` portait la vague « terrains vagues et parcs » d'une autre session, et c'est
  elle qui déplaçait le mobilier de plage. La leçon du dossier partagé : **avant d'accuser
  son propre code, vérifier à qui appartient le diff**. 5 juges neufs (`test_bateau.py`), 4
  juges existants resserrés plutôt qu'affaiblis (le parc n'a plus de phase 2 ; une coque ne
  se juge pas au gaz sur l'asphalte ; son élévation est mesurée comme celle des autres) ;
  1687 tests.

🔨 **4e vague en cours** (16 sept. 2026) — *la foire de La Pointe*. ✅ **Le terrain est
posé** : ⚠️ **on n'agrandit pas la grille, on la DÉPENSE** — la leçon de l'île vaut ici
aussi. Une des trois taches de bois de La Pointe devient la foire (un glyphe `n` du plan
devient `f`), et la grève est juste au-dessus.

- ⚠️ **Une foire est une ALLÉE bordée de choses, pas une place** : c'est ce qui la distingue
  du parc d'à côté, qui est un centre avec des allées en baïonnette. On marche entre deux
  rangs de manèges, et **la grande roue est au bout** — on la voit de l'entrée, et c'est
  elle qui dit où l'on va.
- ⚠️ **Du décor animé, et on n'y monte pas** : le carrousel, les tasses et les chaises
  volantes tournent par `anime` + `variantes` — chaque pose est cuite **une fois** et reste
  en cache, donc un manège qui tourne coûte quatre canevas, pas un par image. C'est l'étage
  1 des machines de chantier, mot pour mot.
- ⚠️ **L'empreinte de la roue est celle de son PORTIQUE, pas de sa jante** : la roue est en
  l'air, on passe dessous — et le juge de `PORTEE_DECOR` l'a dit avant moi (son coin tombait
  à 29 px pour une portée de recherche de 24, donc on serait entré dedans sans que rien ne
  le voie).
- ⚠️ Et deux réflexes qui ont payé : `poser_decor` refuse une tuile **réservée**, donc
  réserver le pied de la roue avant de la poser revenait à lui interdire sa propre place —
  elle ne se posait jamais, en silence ; et la foire **déclare son rectangle** au lieu de le
  laisser deviner, parce que mon premier juge supposait « une trentaine de tuiles » et
  accusait d'un débordement qui n'existait pas (le bloc en fait 69). La foire a son propre
  dé. 7 juges neufs ; 1780 tests.

✅ **Refaite** (16 sept. 2026) — retour de Martin, capture à l'appui, en six phrases :
« c'est assez décevant », « une foire, c'est beaucoup de choses et beaucoup de monde »,
« plein de kiosques, de vendeurs, de mascottes », « de l'exagération », « clôturée — pas un
carré, des clôtures asymétriques — et une entrée avec une arche, et ça doit coûter quelque
chose d'entrer », « plus compacte ».

- ⚠️ **La première version écrivait « une allée bordée de choses » dans son commentaire et
  faisait l'inverse dans son code** : sept objets tirés uniformément sur 80 × 33 tuiles de
  gazon, une roue de 44 px perdue au milieu, tout éteint à 21 h 50. Ce qu'il y a
  maintenant : **une enceinte compacte** (50 × 21) calée à l'ouest du bloc ; **23
  comptoirs** qui bordent l'allée des deux côtés, un tous les trois pas — vingt kiosques de
  neuf sortes (dont la **poutine** et les **queues de castor** : c'est une foire au Québec)
  et les trois jeux d'adresse glissés dans le rang ; **un vendeur peint derrière chaque
  kiosque**, pas une entité (vingt vendeurs à vingt entités mangeraient le budget d'images
  de la rue pour des gens immobiles), son visage tiré à l'empreinte de la tuile ; **les
  manèges en double** juste derrière les comptoirs et une **grande roue de 84 × 92** au bout
  de l'allée ; **des guirlandes en damier** ; **45 forains et 4 mascottes** (un ours, une
  bleue, une rose — un corps, trois pelages) qui naissent DANS l'enceinte, vont d'un kiosque
  à l'autre, et saluent les bras levés.
- ⚠️ **L'arche se paie** : 15 $, un billet par JOUR (pas par passage — une foire qui
  refacture l'aller-retour au hot-dog d'en face est un péage), on ressort librement, et
  c'est une barrière comme les autres (`payer`, dans `carte.BARRIERES`).
- ⚠️ **Resquiller coûte une étoile** : la clôture s'enjambe comme toutes celles du jeu (un
  mur qui ment serait pire), mais la retombée dans la foire sans billet coûte ce que coûte
  de forcer l'arche.
- ⚠️ **Six défauts trouvés en chemin, et presque tous par des juges qui ne parlaient pas de
  foire.** (1) **Un trou dans la clôture** : elle se posait en dernier et sautait toute
  tuile déjà occupée — une table sur le bord laissait une tuile de gazon, et on entrait sans
  payer ; trouvé par un juge qui cherchait où sauter. L'anneau est réservé avant tout le
  reste, et **un juge remplit l'intérieur pour vérifier qu'on n'en sort que par l'arche**.
  (2) **La clôture s'effaçait toute seule** : en 4-voisinage les marches ne se touchaient
  plus que par un coin, et `elaguer_les_clotures` coupait chaque morceau droit comme « une
  barre qui ne clôt rien » — 78 tuiles sur 159. (3) En 8-voisinage, elle faisait des
  **carrés de 2 × 2** (un juge du dépôt tient qu'une clôture fait une tuile d'épais) :
  4-voisinage, un raccord en L à chaque marche, et un amincissement qui ne retire une tuile
  que si la clôture reste étanche. (4) **Le plafond de lumières** : une lampe par kiosque
  dépassait les 50 du rendu, et les feux du carrefour d'à côté se seraient éteints — une
  guirlande sur deux, au halo plus large, en **damier** (la parité de pose allumait tout le
  rang sud et aucun kiosque du nord). (5) **La foule effacée à l'image suivante** : elle
  naissait au bout de la foire, hors de la bulle d'oubli — six forains sur trente. (6) **La
  clôture dans l'élan du pont** : centrée, l'enceinte tombait pile dans l'axe de sortie du
  pont de La Pointe, et un char lancé s'y écrasait après douze tuiles de gazon — le juge du
  pont a vu sa carrosserie tomber à 60.
- ⚠️ **Trois juges existants resserrés plutôt qu'affaiblis** : la clôture est en
  **grillage** et non en palissade (la palissade de bois est l'image de la banlieue des
  Érables, et une foire se clôt de panneaux temporaires) ; une guirlande n'est pas un
  lampadaire planté ; une table de la cour à manger n'est pas du mobilier de plage. 15 juges
  (`test_foire.py`), dont un qui prouve que le détecteur de trou **voit** un trou (le trou
  d'origine a disparu avec le déplacement des tables : remettre le défaut ne suffisait plus
  à rougir) ; 1837 tests. **Restait les trois défis** (galerie de tir, marteau de force,
  pêche aux canards) et les quatre pistes audio — livrés le 17 sept. par la 5e vague.

✅ **5e vague livrée** (17 sept. 2026) — *les trois défis et l'audio*.

- ⚠️ **Un jeu d'adresse est un DÉFI, pas un moteur.** La galerie de tir, le marteau de force
  et la pêche aux canards tiennent sur les rails de `missions.DEFIS` (un lieu, un compte, un
  chrono, une prime, un texte en majuscules) : trois fiches de plus, `a_pied` — on les joue
  DEBOUT devant un comptoir, pas au volant. `ou: foire:<jeu>`, et aucun panneau ne se plante
  : c'est le comptoir qu'on lit. La prime est petite (règle des paliers de boulot), et les
  trois ensemble rapportent dix fois le billet d'entrée — au troisième, la **casquette de la
  foire** (`magasins.TENUES`), rien d'autre ne la donne.
  - La **galerie de tir** : les cibles sont des décors `cible_foire` avec des `pv`, « ce
    qu'on mesure, c'est ce qui est TOMBÉ » — une balle, une bille, n'importe quoi qui les
    crève. On recule pour tirer (rayon large), et le forain relève ses cibles avant qu'on
    tire — une galerie jouée deux fois dans la journée ne doit pas devenir un défi impossible.
  - Le **marteau de force** : marteler ACTION contre un chrono, aucune statistique neuve —
    le compte est en coups, pas en muscles. `Son.SFX.maillet` (un coup mat sur un plateau de
    bois) et `cloche` (le seul son du jeu qui dise « tu as gagné » avant le HUD).
  - La **pêche aux canards** : on la GAGNE, on ne la VOLE pas (`vole_pas`) — un comptoir
    défoncé met fin au jeu. Le canard ne s'accroche que quand il passe sous le crochet, et
    c'est le DESSIN qui le dit (`canardAuCrochet` lit `Entites.poseDuDecor`, la même pose
    que celle qui se peint) — un chrono inventé et une animation qui tourne de son côté, ce
    serait un jeu d'adresse où l'adresse ne sert à rien.
  - ⚠️ **La chaîne d'action affame ce qui suit** : `actionDeDefi` passe AVANT le reste,
    sinon marteler devant le comptoir ouvrirait le menu du comptoir à chaque coup.
- ⚠️ **Les quatre pistes sont générées et posées** (`audio.py`, `musique.py` + une séance
  ElevenLabs) : les **vagues** (boucle dont le volume suit la distance à l'eau), les **cris
  de la foire** (ce qu'on entend avant de voir la palissade), le **moteur de la coque** (un
  hors-bord cogne et crachote, il ne roule pas au ralenti d'une auto), et **l'orgue du
  manège** — une MUSIQUE qui sort d'un ENDROIT, le code du musicien de rue avec une source
  fixe au milieu de l'allée, pas une ambiance de district de plus. Chaque boucle a son repli
  synthétisé, exactement ce que fait un vrai maître d'œuvre sourd.

- ⚠️ **Le district se tait dans la foire.** Mesuré : l'ambiance de La Pointe jouait
  **dessous** l'orgue — deux musiques à la fois, alors que la fiche de l'orgue dit noir sur
  blanc qu'il est « une musique qui sort d'un ENDROIT », PAR-DESSUS l'ambiance. `Chef.voulu`
  coupe l'ambiance du district dans l'enceinte (`Monde.dansLaFoire`), **mais APRÈS** la
  poursuite et la bagarre : se cacher sous un comptoir ne rend pas la ville sourde à la
  police. Un juge le tient (`test_son_js.py`), à pied, recherché et au bord de la
  palissade.
- ⚠️ **Reste ouvert, mesuré et nommé** : à la lisière de la palissade, l'ambiance de La
  Pointe revient **d'un coup** alors que l'orgue (460 px de portée) s'entend encore. C'est
  voulu — dehors, c'est La Pointe — mais la bascule est plus sèche qu'aux frontières de
  district, qui ont leur hystérésis (`hysteresis_px`). **Idée à reprendre** si Martin trouve
  la couture trop brusque en sortant de la foire : la même hystérésis qu'à une frontière de
  district, appliquée au bord de l'enceinte.
