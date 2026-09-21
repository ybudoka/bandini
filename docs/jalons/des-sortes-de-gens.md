# Des sortes de gens

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Des sortes de gens, pas des couleurs (**ajout**, taille 3)_

_Demande de Martin :_ « je veux plusieurs sortes de personnages non joueurs — des amuseurs
publics, des musiciens de rue, des exhibitionnistes. »

⚠️ **Il y a 24 archétypes, et 4 corps.** Vingt et un portent le corps du joueur avec un
échange de palette. Et sur six `metier`, **deux** déclenchent quelque chose dans le moteur
(`reclame`, `compagnie`) ; les autres sont des nombres — courage, témoin, vitesse. Une
« sorte » est donc aujourd'hui une couleur et trois chiffres, et le plan a déjà payé ce
défaut une fois : les filles de la Brume « n'étaient qu'un échange de palette sur le corps
commun » et on ne les distinguait plus de personne.

**La règle : une sorte = un corps + une routine.** Le catalogue garde ses nombres ; ce qui
fait une sorte, c'est ce qu'elle **fait** que les autres ne font pas. `metier` est le
crochet, il existe déjà — chaque sorte en apporte un, et `majPieton` gagne une routine par
métier au lieu d'une palette par slug.

**Les sortes de Martin :**

- **Le musicien de rue.** Posté à un coin, il joue — et **ça s'entend** : un bruitage court en
  boucle (M15 en a le mécanisme), ducké comme le reste sous une voix. Un chapeau devant lui :
  on y jette une pièce, ou on la lui prend (le pickpocket existe). La foule s'arrête autour
  (l'état `arret` existe pour l'homme-sandwich).
- **L'amuseur public** — mime, jongleur, statue vivante. Il attire un **attroupement**, et un
  attroupement est une **foule de témoins** : faire un coup devant lui, c'est dix témoins
  d'un seul geste. Ce n'est pas du décor, c'est du jeu — l'endroit de la rue où il ne faut
  pas sortir une arme.
- **L'exhibitionniste.** Un imperméable, qu'il ouvre au passage des dames ; elles crient et
  fuient (le cri et `fuit` existent), et **un policier qui passe l'arrête, lui** — la seule
  fois où la police s'occupe de quelqu'un d'autre que le joueur. C'est un gag, et c'est le
  gag qui rend la police crédible : elle n'existe pas que pour toi.

**Et celles qui viennent avec, parce qu'elles servent d'autres fiches :**

- **la contractuelle**, qui met des contraventions — c'est elle qui rend « mal garé »
  **visible** avant que la fourrière ne l'avale ;
- **le jogger**, écouteurs sur les oreilles : il ne témoigne de rien, il ne s'arrête pas ;
- **le touriste**, qui lève la tête devant les enseignes et photographie (un flash) — le
  témoin le plus attentif de la ville, et le plus lent ;
- **l'ivrogne**, qui zigzague, tombe, insulte, et n'a peur de rien — le seul qui ne fuit pas
  devant une arme, ce qui le rend dangereux pour lui ;
- **le pickpocket**, qui vole les autres (M12, la ville coupable d'elle-même) ;
- **la personne âgée**, à la marchette : elle traverse lentement, et les chars attendent
  (les feux pour piétons) ;
- **le facteur**, qui fait sa tournée de porte en porte (les portes s'ouvrent).

**Première vague livrée le 14 sept. 2026** — les trois que Martin a nommées :

- **Trois corps, pas trois palettes.** Chacune a son sprite 12 × 13 (deux colonnes de plus
  que le corps commun, pour le chapeau, le manteau et la guitare) : ⚠️ à douze pixels, c'est
  la **guitare en travers du torse** qui nomme le musicien, le **melon et le visage blanc**
  qui nomment le mime, le **long manteau** qui nomme le troisième. Un juge Python refuse
  qu'une sorte porte le corps d'une autre, ou celui du joueur.
- **Et une routine chacune**, accrochée au `metier` — c'est là que la sorte existe vraiment :
  - le **musicien** et l'**amuseur** tiennent un poste (`vitesse: 0`, comme le marchand
    derrière son kiosque) et **attroupent** les passants autour d'eux ;
  - ⚠️ **un attroupement est une foule de témoins** : les badauds qui regardent un spectacle
    **regardent**, et leur `probaTemoin` monte. Faire un coup devant l'amuseur, c'est dix
    témoins d'un seul geste — c'est l'endroit de la rue où il ne faut pas sortir une arme ;
  - l'**homme au manteau** l'ouvre au passage de quelqu'un : elle crie et fuit. ⚠️ Et **un
    agent qui le voit l'arrête, LUI** — la seule fois où la police s'occupe de quelqu'un
    d'autre que le joueur, et c'est ce gag qui la rend crédible : elle n'existe pas que pour
    toi.
- ⚠️ **Une image imposée, pour un corps qui n'est pas une marche.** Les deux images du manteau
  sont « fermé » et « **ouvert** », pas deux pas — or l'animation choisit son image d'après la
  distance parcourue, et un personnage **immobile** tombe toujours sur l'image zéro. Son geste
  ne se serait jamais vu. `poseFixe` règle ça pour toutes les sortes à venir.
- ⚠️ **Un flâneur fait des pauses tout seul**, et celui qui traînait déjà à côté du jongleur
  restait le seul de la rue à ne pas le regarder : l'attroupement prend aussi les `arret`.
- ⚠️ **Elles ne naissent pas dans la foule** (`frequence: 0`, comme l'homme-sandwich) : on les
  pose aux coins de rue, hors champ, deux de chaque au plus dans la bulle.
- ⚠️ **Un juge de la Brume a dû être réparé, pas contourné** : il comptait **toutes** les voix
  entendues pendant dix secondes pour dire si la fille s'était répétée — donc un bonjour de
  passante passait pour une relance. Ajouter du monde dans la rue l'a révélé. Il ne compte
  plus que les voix **de la Brume**.
- **Juges (2 neufs)** : côté Python, chaque sorte a un corps **à elle**, un métier à elle, et
  ne naît pas au hasard ; au banc, l'amuseur arrête quatre badauds sur quatre **et en fait de
  meilleurs témoins**, le musicien ne quitte pas son coin, le manteau s'ouvre **sur la bonne
  image** pendant qu'elle crie et fuit, et un agent posé à côté le met en fuite avec le bon
  poursuivant.

**Deuxième vague livrée le 14 sept. 2026** — cinq des sept « qui viennent avec ». Le choix
n'est pas arbitraire : ce sont celles dont la routine **se branche sur une fiche déjà
livrée**. La personne âgée attend « des feux pour piétons » (P4) — sans feu, « les chars
attendent » n'a nulle part où s'accrocher — et le pickpocket est logé dans M12.

- **La contractuelle.** Elle repère le char mal garé, **y va** (un état `cap` neuf : flâner
  suit une direction, elle a un endroit où aller), se plante devant et verbalise — un papier
  blanc sous l'essuie-glace, et le HUD le dit. ⚠️ **Elle lit la règle de la fourrière, pas une
  deuxième écrite pour elle** (`Missions.malGare`) : deux règles qui disent « mal garé » se
  contrediraient le jour où l'une bouge, et on verrait une contravention sur un char que
  personne ne remorque. Ce qu'elle change : l'avertissement cesse d'être un message venu de
  nulle part.
- **Le touriste.** `temoin: 1.0` — le seul de la ville. Faire un coup devant lui, c'est se
  faire voir à coup sûr, et il est lent : on ne le sème pas en marchant. Sa routine le rend
  **visible comme témoin** : il s'arrête devant une vitrine, lève la tête, et le flash part.
- **L'ivrogne.** Il zigzague (sa direction est bonne, sa trajectoire ne l'est pas), il tombe
  tout seul, et ⚠️ **il ne fuit pas devant une arme** : il répond. C'est le seul — une rue où
  tout le monde détale de la même façon n'a qu'une réaction, et on cesse de la voir.
- **Le jogger.** Une routine **en creux** : il ne s'arrête jamais, ni pour souffler ni pour
  regarder un amuseur, et `temoin: 0.0`. Ce qu'une sorte ne fait pas la nomme aussi.
- **Le facteur.** De porte en porte, il fait battre le battant — et ⚠️ **il n'entre pas** :
  c'est toute la différence avec le flâneur qui rentre chez lui, celui-là disparaît derrière
  le battant.

⚠️ **Chacune a ses quartiers** (`districts`). Huit sortes qui naissent partout, ce n'est plus
de la variété, c'est de la figuration : on les croise toutes dans la même rue et on cesse de
les voir. Un touriste sur les Quais et pas dans La Shop, un facteur aux Érables et pas au
port — un quartier se reconnaît à ses enseignes, à ses toits, à sa gang, et aussi **à qui y
marche**. Et **une seule** de chaque dans la bulle quand elle marche (deux restent pour les
deux spectacles, qui sont plantés quelque part).

⚠️ **Ce qu'une sorte dit vit en Python** (`pietons.PAROLES`). Le dépôt a payé huit fois « une
fiche que le navigateur ne lisait pas » ; le symétrique coûte aussi cher — un mot écrit en dur
dans `entites.js` est un mot que personne ne peut relire ni juger depuis la source de vérité.

**Trois défauts trouvés par les juges neufs**, et aucun n'était dans la fiche :

- ⚠️ **`e.t % 60` ne tombe jamais.** `majSortes` ne tourne qu'une image sur quinze et `e.t`
  compte depuis la **naissance** : les deux ne coïncident que si l'on est né sur un multiple
  de quinze. Un ivrogne né du mauvais pied n'aurait jamais trébuché de sa vie — et rien ne
  l'aurait dit, parce que « il tombe rarement » et « il ne tombe jamais » se ressemblent
  beaucoup. Chaque routine a maintenant **son compte à elle**.
- ⚠️ **L'homme au manteau ignorait qui était arrêté.** Exactement la leçon déjà payée pour
  l'attroupement (« un flâneur fait des pauses tout seul »), et corrigée à un seul endroit :
  celle qui s'arrêtait pile devant lui était la seule de la rue à ne rien voir.
- ⚠️ **On naissait dans quelqu'un** (corrigé à la fiche des pièces, le même jour) : `placeLibre`
  ne lit que l'index de la foule, et l'index ne se refait qu'une fois par image.

⚠️ **Et un juge d'à côté mesurait la mesure du jour, pas la règle** : « la foule ne se traverse
plus » exigeait moins d'un pixel de chevauchement à **toute** image. Or deux passants qui se
croisent de face se rapprochent de quatre pixels en une image, et la séparation les défait à
la suivante : l'exiger sous un pixel revenait à exiger que personne ne se croise jamais de
face. Il mesure maintenant ce que « se traverser » veut dire — la **durée** d'un chevauchement
(jamais plus d'une image) et **combien** dépassent le pixel (au plus cinq en 960 images) —
et le défaut d'origine (1032 paires, 9,9 px, tenues) le fait rougir des trois côtés.

**Troisième vague livrée le 14 sept. 2026** — trois de ceux qui « gagnent leur vie dans la
rue », prises pour leur **crochet** et pas pour leur costume :

- **Le crieur de journaux** hurle la manchette du Clairon. ⚠️ C'est **ce que tu as fait
  hier** : `journal.py` compare tes statistiques du jour à celles de la veille, et trois
  morts un soir s'entendent crier au coin de la rue le lendemain matin. La boucle la moins
  chère du jeu, et la seule qui te renvoie ton reflet sans passer par un menu. ⚠️ Il **lit**
  `derniereManchette` et ne la recalcule pas : `manchetteDuJour()` remet le compteur d'hier à
  zéro au passage, et un crieur qui l'appellerait effacerait la mémoire du journal à chaque
  cri.
- **Le laveur de vitres** ne s'approche que des chars **arrêtés**, sur la chaussée. Même
  horloge que les feux qu'on vient de livrer : un feu rouge, c'est quinze secondes de
  travail ; un char qui repart le laisse le chiffon en l'air. Sans cette contrainte, il
  laverait des pare-brise à soixante à l'heure — une animation, pas un métier.
- **Le pickpocket** vole **les autres**. ⚠️ **L'argent change de poche pour de vrai** — sinon
  le vol n'est qu'une animation, et fouiller le volé rapporterait quand même. Il aborde
  **dans le dos**, au même angle que le joueur (`pickpocket_dos_degres`, lu dans la fiche),
  la victime crie AU VOLEUR et le désigne **lui** comme menace, et un agent qui passe
  l'arrête. C'est le deuxième après l'homme au manteau, et les deux disent la même chose :
  **la police n'existe pas que pour toi**.

⚠️ **Un défaut qu'on n'aurait pas vu** : le pickpocket marche 10 % plus vite qu'un passant,
donc il gagnait **cinq centièmes de pixel par image** et mettait une minute et demie à
couvrir trente pixels. Il ne volait jamais personne — et de loin, ça ressemblait à quelqu'un
qui suit. Celui qui **rattrape** quelqu'un court (`capVite`).

**Le réservoir** — « je veux plein d'idées ». Chacune avec ce qu'elle _fait_ ; celles qui
n'ont qu'un costume n'y sont pas. On y pige par vagues, jamais tout d'un coup.

- _Ceux qui gagnent leur vie dans la rue_ : le **laveur de vitres** au feu rouge, qui
  s'approche des chars arrêtés, essuie et tend la main — refuser, c'est un pare-brise sale ;
  le **crieur de journaux**, qui hurle la manchette du matin (celle de `journal.py`, donc ce
  que **tu** as fait hier) ; le **distributeur de tracts**, qui te colle un papier — et un
  tract, c'est une chose de plus à ramasser ; le **cireur de chaussures** sur sa caisse ; le
  **chauffeur de taxi** qui attend assis sur son capot, et qui témoigne de tout ce qui se
  passe à son coin ; la **vendeuse de fleurs**.
- _Ceux qui font du bruit_ : le musicien, mais **par instrument** — guitare, accordéon,
  saxophone, et le **joueur de cuillères**, parce que c'est ici ; le **prédicateur** du coin
  qui harangue, et le **fou de la place** ; le **cracheur de feu** la nuit — une lampe qui
  bouge ; une **petite manif** avec ses pancartes, qui bloque un trottoir : une entrave
  piétonne, avec un policier qui la surveille.
- _Ceux qui sont là pour toi_ : l'**arnaqueur au bonneteau** — trois gobelets, on peut
  jouer, on perd, et si on le frappe, ses deux compères sortent de la foule ; le **mendiant**
  qui te suit trois pas et lâche ; le **dealer** au coin, qui ouvre M10 ; le **fan** qui te
  suit quand tu es célèbre, et qui gêne ; le **journaliste** qui débarque après un gros coup
  et photographie — le lendemain, c'est en manchette.
- _Ceux qui font la ville_ : le **brigadier scolaire**, le matin devant l'école, qui arrête
  les chars pour faire traverser les enfants — un char qui ne s'arrête pas, c'est deux
  étoiles ; le **déneigeur** à la pelle devant sa porte, l'hiver ; l'**employé de parc** qui
  ramasse ; le **camion-balai** de nuit, et son gars ; l'**ouvrier de chantier** sur ses
  entraves (M12).
- _Ceux qui ne vont nulle part_ : le **vieux sur son banc**, qui nourrit les goélands ; les
  **enfants qui jouent au hockey dans la rue** — ils crient « CAR ! » et tassent leur but
  quand un char arrive, et **ils sont intouchables**, comme les autres enfants ; le
  **couple qui se chicane** sur un pas de porte ; les **fêtards** qui sortent du bar en
  groupe, bruyants, la nuit — la seule foule qui ne fuit pas tout de suite.
- _Ceux qui te jugent_ : le **badaud qui filme** avec son téléphone — le témoin moderne, et
  la vidéo vaut une étoile de plus si on ne la lui prend pas ; et **la madame au balcon**,
  qui voit tout depuis sa fenêtre : un témoin qu'on **ne peut ni acheter ni rattraper**, et
  la raison de regarder en l'air avant de faire un coup dans une ruelle.

- ⚠️ **Chaque sorte a SON corps, ou elle n'existe pas.** C'est la leçon des filles de la
  Brume. Un corps coûte peu — 12 × 16, quatre directions, trois poses — mais l'atlas et le
  paquet grossissent, et le paquet est à 92 % de son budget brut. Un juge interdit toute
  sorte nouvelle sur `sprite: 'joueur'`.
- ⚠️ **Une routine coûte par image.** Un musicien qui joue est une boucle audio ; dix
  musiciens font dix boucles. Chaque sorte a un **plafond dans la bulle** — un musicien, un
  amuseur, un exhibitionniste à la fois — et c'est ce qui les garde rares, donc remarqués.
- **Elles ont un quartier et une heure.** Le champ `districts` existe (le débardeur ne quitte
  pas les Quais) et le rythme aussi : un musicien au Carré le soir, un touriste sur les Quais
  le matin, un exhibitionniste au parc — et personne de tout ça à La Shop à 3 h.
- **Juges** : toute sorte a son corps ; toute sorte a une routine **mesurable au banc** (elle
  fait quelque chose qu'un passant ne fait pas) ; le musicien s'entend et se tait sous une
  voix ; l'amuseur attroupe (N piétons en `arret` autour de lui) ; l'exhibitionniste finit
  arrêté par un agent qui passe, sans une étoile pour le joueur ; et jamais plus de son
  plafond d'une sorte dans la bulle.

## Notes

demande de Martin (« des amuseurs publics, des musiciens de rue, des exhibitionnistes ») :
la ville avait **24 archétypes pour 4 corps** — vingt et un portaient celui du joueur
repeint — et sur six `metier`, **deux** faisaient quelque chose. Une sorte était une couleur
et trois chiffres. Règle posée : **une sorte = un corps + une routine**. Les trois que
Martin a nommées ont chacune son sprite 12×13 et sa routine : le **musicien** et
l'**amuseur** tiennent un poste et **attroupent** (et un attroupement est une **foule de
témoins**), l'**homme au manteau** l'ouvre au passage d'une dame — qui crie et fuit — et ⚠️
**un agent l'arrête, lui**. Le réservoir de la fiche reste à piger, par vagues
