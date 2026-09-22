# M15 La ville te parle

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M15 — La ville te parle (**ajout**, taille 4) — **1re vague livrée le 14 sept. 2026**_

_Ce que ça donne :_ le jeu cesse d'être muet entre deux répliques de mission — et il
t'apprend enfin ce qu'il sait faire.

**Première vague livrée le 14 sept. 2026** — et la vague se prend en deux, pour une raison
simple : la moitié de M15 demande des **clips ElevenLabs**, donc des crédits, donc une oreille
que je n'ai pas. Cette première moitié ne demande **aucun son neuf**.

- **La rue se tait quand tu sors une arme.** L'ajout le moins cher de toute la vague, et celui
  qui se sent le plus : `Son.Rumeur` réglait déjà son volume sur le nombre de gens autour — il
  ne manquait qu'une **raison** de le faire tomber. Elle tombe d'un coup à 18 % et remonte en
  quatre secondes. ⚠️ Et **après un coup de feu, elle ne reprend pas au même endroit** : elle
  revient en **cris** (1,7 fois son volume), puis se calme. Une foule qui murmure pareil avant
  et après un mort n'est pas une foule, c'est un bruit de fond. Au volant, rien : on ne voit
  pas ce que tu tiens.
- **Les répliques : moins souvent, et jamais les mêmes.** ⚠️ `audio.VOIX` promettait « jamais
  deux fois de suite le même » — **c'était faux, et ça l'a toujours été** : le moteur tirait
  par `Math.random()` sans aucune mémoire. Sur quatre répliques par genre, une chance sur
  quatre de répéter la précédente. Le tirage écarte maintenant les dernières, **et passe par
  `B.rng()`** : tout le hasard du jeu y passe déjà, c'est ce qui rend le banc reproductible —
  donc juge. Cette ligne-là lui échappait, et c'était précisément celle qu'on voulait pouvoir
  tester.
  - ⚠️ **La mémoire est à DEUX, pas à quatre** comme la fiche l'annonçait : la plus petite
    banque en compte **trois** (le crieur). Pour en exclure quatre, il en faudrait six par
    banque — ce nombre monte le jour où les banques montent, et **un juge tient les deux
    ensemble** pour qu'on ne puisse pas bouger l'un sans l'autre.
  - **Parler devient une chance** (35 %), pas une certitude : un passant qui parle chaque fois
    qu'on le frôle rend huit répliques fatigantes bien avant qu'elles soient usées.
- **Le repli du Clairon enseigne.** Six leçons, une par matin calme : le klaxon des boulots,
  la fourrière, le café, le garage, les propriétés, les clôtures qui s'enjambent. ⚠️ **On
  n'enseigne que ce que le joueur n'a pas fait** (chaque leçon dit par quelle statistique on
  prouve qu'on sait déjà), **jamais deux fois la même** (la partie retient), et quand il n'y a
  plus rien à apprendre le repli **redevient** « rien à signaler » — ce qui est une bonne
  nouvelle. Le narrateur les lit comme une manchette. ✅ **Les six mp3 existent depuis le 16 sept. 2026**
  et l'encadré a sa voix : `exporter()` les déclare tout seul, **sans une ligne de code** —
  la porte ouverte par la 1re vague s'est refermée d'elle-même le jour où les fichiers sont
  arrivés.

⚠️ **Deux défauts trouvés en chemin, et le second ne se voyait pas du tout :**

- **Un enfant naissait dans le mur.** Le petit d'une mère naît à côté d'elle (`x + 10`), et
  **personne ne vérifiait la tuile** : une mère née au ras d'une façade posait son enfant
  dedans — et de là il ne pouvait plus sortir, le masque du piéton ne laissant pas sortir d'un
  mur plus qu'il n'y laisse entrer.
- **`Rumeur.maj` ne tourne qu'une image sur quinze**, et le compteur de peur se décrémentait
  de **un** par appel : 240 images de peur en duraient 3 600. La rue ne revenait jamais — et
  ça ne se voit pas, ça ressemble juste à une ville silencieuse. Les deux minuteries sont
  maintenant des **échéances** en `B.t` : une échéance ne se trompe pas de cadence.

## Fiche de la deuxième vague

✅ **La radio parle vraiment, et la police aussi** (21 sept. 2026) — voir les notes. ⬜ **En cours** : le souffle du joueur, les bruits de quartier. **Restent** : le bulletin de nouvelles, les répliques par contexte.

**Ce qui reste, et ce que ça coûte** : la radio qui parle (animateur, pubs, bulletin), la
police à la radio, les bruits de quartier, le souffle du joueur, et les banques de répliques
par contexte — une cinquantaine de clips ElevenLabs. C'est la deuxième vague, et elle demande
les crédits de Martin **et son oreille** : aucun juge ne dit qu'un son est le BON son.

⚠️ **Cette vague ne dépend de rien.** C'est celle qu'on prend quand on veut un gain rapide :
les trois morceaux passent par des pièces déjà en place (le narrateur de M7, le journal de
M5, les voix de M6), et aucun ne touche à la physique ni à la carte.

- **Le journal du matin t'apprend à jouer.** Le jeu a maintenant des boulots au klaxon, une
  fourrière, un marché noir, des propriétés, trois défis — et **rien n'explique rien** : M1
  apprend à marcher et à voler un char, et après ça le joueur est tout seul. Or `journal.py`
  trie déjà ses règles du plus grave au plus banal et finit par un repli « rien à signaler ».
  Ce repli devient **un encadré qui enseigne une chose** — « Saviez-vous qu'un coup de klaxon
  dans un taxi vous trouve un client? ». Une par jour, lue à voix haute par le narrateur qui
  existe déjà, **sans une seule fenêtre de plus**.
  - ⚠️ On n'enseigne que ce que le joueur n'a **pas encore fait** : `p.stats` le sait. Un jeu
    qui explique le taxi à quelqu'un qui a fait trente courses n'explique rien, il agace.
  - Jamais deux fois la même : la partie garde ce qui a été lu. Quand il n'y a plus rien à
    apprendre, le repli redevient « rien à signaler » — et c'est une bonne nouvelle.
- **La radio parle.** Les trois stations sont des boucles instrumentales ; or l'âme d'une
  radio, c'est ce qui se dit **entre** les tounes. Tout le mécanisme est là : `Son.Voix`, le
  ducking, le filtre du combiné. Un clip toutes les deux ou trois boucles, en trois sortes :
  - **un animateur par station** — feutré à La Brume, jovial au Taxi-Radio, et personne au
    Choc : juste un jingle, c'est le propos de la station ;
  - **des pubs** pour des commerces qui existent (Chez Gus, Boutique Rosa, le Dépanneur
    Ti-Paul). ⚠️ **La pub change quand tu achètes le commerce** — c'est cette ligne-là qui
    fait que ça vaut la peine, et pas une autre ;
  - **un bulletin de nouvelles** qui rejoue la manchette de `journal.py` : la radio parle
    donc de **ce que tu as fait hier**, dans un char que tu viens de voler.
  - Une vingtaine de clips à 40 Ko : 800 Ko, largement sous le plafond de 3 Mo des voix. Et
    la règle de `audio.py` tient toujours — `exporter()` ne déclare que les fichiers
    présents, une station sans animateur joue simplement sa musique.
- **Les passants : plus de choses, moins souvent, et jamais les mêmes** — demande de
  Martin, et **pour moitié un correctif** : « plus de choses » est un ajout, « jamais les
  mêmes » répare une promesse écrite dans le code et jamais tenue.
  Aujourd'hui il y a **huit** répliques — quatre par genre. Un passant parle dès qu'il passe
  à 30 px, avec un temps mort global de 4 secondes, et la réplique est tirée par un
  `Math.random()` **sans aucune mémoire**. Sur quatre choix, une chance sur quatre de répéter
  la précédente : dans une rue passante, on entend « Fait frette, hein? » trois fois en vingt
  secondes. ⚠️ Le commentaire d'`audio.VOIX` promet pourtant « jamais deux fois de suite le
  même » — **c'est faux**, et ça l'a toujours été : un tirage au hasard peut sortir deux fois
  le même, c'est même sa définition.
  - **Plus de choses.** La banque grossit, et elle grossit **deux fois** : `audio.VOIX` gagne
    un champ `quand` (`normal`, `peur`, `celebre`, `nuit`), et chaque contexte a ses
    répliques. La ville se met à te reconnaître au lieu de te dire bonjour pendant que tu
    saignes.
  - **Moins souvent.** Le temps mort monte, et surtout **parler devient une chance, pas une
    certitude** : la plupart des gens qu'on croise ne disent rien, comme dans la vraie vie.
    Un passant qui parle à chaque fois qu'on le frôle, c'est ce qui rend huit répliques
    fatigantes bien avant qu'elles soient usées.
  - **Jamais les mêmes.** Le moteur garde les **quatre dernières** répliques dites et les
    exclut du tirage. ⚠️ **Ça impose une taille minimale à chaque banque** : pour en exclure
    quatre, il en faut au moins six, sinon il ne reste rien à tirer et la règle se retourne
    contre elle-même. C'est un test, pas une intention — et une banque trop courte retombe
    sur `normal` plutôt que de se répéter.
  - ⚠️ **Et le tirage passe par `B.rng()`**, pas par `Math.random()`. Tout le hasard du jeu
    y passe déjà — c'est ce qui rend le banc reproductible et donc juge. Cette ligne-là lui
    échappe, et c'est précisément celle qu'on veut pouvoir tester.
  - Le compte : 4 contextes × 2 genres × 6 répliques = **48 clips**, soit environ 1,2 Mo —
    sous le plafond de 3 Mo des voix. Et la règle d'`audio.py` tient : `exporter()` ne
    déclare que les fichiers présents, une banque vide se rabat sur `normal`.
- **Le silence quand tu sors une arme.** C'est l'ajout le moins cher de toute la vague et
  celui qui se sent le plus. `Son.Rumeur.maj(gens)` règle déjà le volume de la foule sur le
  nombre de personnes autour — **il ne manque qu'une raison de le faire tomber**. Une rue qui
  se tait d'un coup dit « ils t'ont vu » mieux qu'une étoile de plus, et elle le dit avant que
  tu regardes le HUD. Elle remonte quand la peur passe.
  - ⚠️ Et le contraire compte autant : après un coup de feu, la rumeur ne reprend **pas** au
    même endroit — elle revient en cris, puis se calme. Une foule qui murmure pareil avant et
    après un mort n'est pas une foule, c'est un bruit de fond.
- **La police se parle à la radio.** On voit les cônes, on voit les blips, on n'entend rien —
  alors qu'une poursuite est ce qu'il y a de plus tendu dans le jeu. Cinq répliques courtes
  suffisent : _il l'a repéré_, _la poursuite commence_, _on l'a perdu_, _un barrage se pose_,
  _l'hélico décolle_. Filtrées comme le combiné du téléphone (le filtre existe depuis M6),
  elles rendent la police **lisible à l'oreille** — on sait ce qui va nous tomber dessus sans
  quitter la route des yeux.
  - ⚠️ Elles passent **au-dessus** de la musique de poursuite dans l'échelle ci-dessus, sinon
    elles arrivent pile quand on ne peut plus les entendre.
- **Les bruits de quartier, ponctuels.** Distincts de la musique de district : ce ne sont pas
  des nappes, ce sont des **événements** — une mouette et une corne de brume aux Quais, un
  martèlement lointain à La Shop, une tondeuse et des oiseaux aux Érables, le vent dans les
  arbres à La Pointe. Trois ou quatre par district, tirés rarement, et un quartier s'entend
  avant de se voir. Beaucoup moins cher qu'une piste : ce sont des bruitages, pas de la
  musique.
- **Le souffle du joueur.** Il sprinte, il s'essouffle, et on n'entend rien. Un halètement qui
  monte avec la dépense, et une inspiration quand le souffle repart : ça rend la barre
  d'endurance lisible **sans la regarder**, et ça vaut double depuis que le sprint est devenu
  une ressource qu'on dépense par bouffées.
- **Juges** : une leçon ne se donne qu'une fois et jamais sur ce qui est déjà fait ; un clip
  de radio ne coupe jamais une réplique de mission (le ducking a déjà sa file d'attente) ;
  la pub d'un commerce possédé n'est plus celle d'un commerce à visiter ; **aucune des quatre dernières
  répliques dites ne peut ressortir**, et toute banque où l'on tire en contient au moins six
  (quatre à exclure, deux pour que ça reste un tirage) ; le tirage passe par `B.rng()`, donc
  le banc peut jouer mille rencontres et compter les répétitions — il doit en trouver zéro.

## Notes

tout ce qui ne demandait **aucun son neuf**.

- ⚠️ **La rue se tait quand tu sors une arme** — `Son.Rumeur` réglait déjà son volume sur le
  nombre de gens autour, il ne manquait qu'une **raison** de le faire tomber ; elle tombe
  d'un coup, remonte en quatre secondes, et **crie** après un coup de feu.
- ⚠️ **Les répliques : moins souvent et jamais les mêmes** — `audio.VOIX` promettait
  « jamais deux fois de suite le même » et le moteur tirait par `Math.random()` **sans
  mémoire** ; le tirage passe maintenant par `B.rng()` (donc reproductible, donc jugeable)
  et écarte les dernières. **Parler devient une chance** (35 %), pas une certitude.
- ⚠️ **Le repli du Clairon enseigne** : un matin calme apprend une chose que tu n'as **pas
  encore faite**, jamais deux fois la même, et quand il n'y a plus rien à apprendre il
  redevient « rien à signaler ». ✅ **Les six leçons ont leur voix** (16 sept. 2026, 350
  Ko) : `exporter()` les déclare tout seul, sans une ligne de code. **Reste à générer**
  (crédits + une oreille) : la radio qui parle, la police à la radio, les bruits de
  quartier, le souffle du joueur, et les banques de répliques par contexte.
- ⚠️ **Deux choses mesurées en chemin, à savoir avant de reprendre** : (1) le **budget
  audio** (950 Ko) est la vraie contrainte de la 2e vague — 18 clips l'ont fait sauter à
  1,16 Mo, et il faudra soit le relever, soit générer en 22 kHz comme les répliques de
  passants ; (2) « la pub change quand tu achètes le commerce » **ne peut viser que ce qui
  s'achète** — Chez Gus et Boutique Rosa existent mais ne se vendent pas ; les quatre
  propriétés sont le kiosque, le bar, le garage et l'hôtel. 11 juges neufs

✅ **2e vague, première partie : la radio parle vraiment, et la police aussi** (21 sept. 2026).

- ⚠️ **LA RADIO NE PARLAIT PAS.** Le commit du 16 sept. (`f3ed153`) annonçait « la radio parle enfin » : ses douze
  clips (trois animateurs de La Brume, trois de Taxi-Radio, six pubs) étaient générés, déclarés, et **téléchargés au
  démarrage** — mais aucune ligne du jeu ne les jouait. `grep radio_` dans `static/js/` ne rendait rien. `Son.Ondes`
  les fait passer : la première voix vingt secondes après avoir allumé la station, puis une toutes les 80 à 125 s
  (deux ou trois tounes de 45 s), l'animateur et les pubs en alternance. Le Choc et les stations du camion se taisent.
- ⚠️ **LA PUB QUI CHANGE QUAND TU ACHÈTES ne pouvait jamais changer** : ses trois jumelles « à toi » annonçaient Chez
  Gus, Boutique Rosa et Ti-Paul, qu'aucun joueur ne peut acheter. Elles sont parties (trois mp3), Gus, Rosa et Ti-Paul
  gardent leur pub, et les jumelles vont au **kiosque, au bar et au garage** — six clips neufs, `propriete` les y
  attache, un juge refuse une jumelle qui vise ce qui ne se vend pas. L'hôtel (phase 2) attendra la sienne.
- **La police au scanner** : cinq événements tirés du vrai chemin de `police.js` — **repéré** (la première étoile),
  **poursuite** (le palier où les autos s'en mêlent ; un saut de zéro à trois dit « poursuite », le plus grave),
  **perdu** (la dernière étoile qui tombe), **barrage**, **hélico** — deux répliques chacun, dites à tour de rôle, dans
  la bande du téléphone. Deux voix du compte que personne n'avait : Caroline en répartitrice, Alexandre Boutin en
  agent. Six secondes entre deux messages, trente avant de redire le même événement : sinon le scanner devient une
  alarme.
- ⚠️ **Une seule bande pour les deux**, et une réplique de mission passe devant tout le monde : `Voix.parler` coupe
  les ondes, et les ondes attendent qu'elle finisse. Ce qui passe baisse la musique comme une réplique (le ducking
  sait maintenant qu'on peut parler sur les ondes pendant qu'une mission se tait, et l'inverse).
- ⚠️ **À tour de rôle, jamais `B.rng()`** : un bruit de fond qui tire un dé décale tout le hasard du jeu
  (`ecrire-drole.md`, règle 8). Un juge fait tourner dix minutes de radio en comptant les dés : zéro.
- ⚠️ **Le texte des ondes ne voyage plus** : rien ne l'affiche, et le paquet des définitions est au-dessus de son
  plafond depuis ce matin (44 559 octets gzip sur la base pour 44 000). Vingt-cinq répliques ajoutées, et le paquet
  **descend** à 44 397 — toujours au-dessus : relever le plafond reste une décision de Martin. (Et la **carte**, elle,
  est passée à 50 294 octets pour un plafond de 50 000 avec l'aéroport, le même jour.)
- **Seize voix** (≈ 1 220 crédits), toutes à −19,6 LUFS ± 0,3, masters dans
  `~/elevenlabs-audio/bandini-voix-v3-masters-2026-09-16/`. ⚠️ **Personne ne les a écoutées** : c'est à Martin
  (`--refaire <slug>` pour une prise ratée).
- **Juges** (`test_ondes.py`, 14 ; seize mutations, toutes rouges) : les stations qui parlent ont de quoi dire, deux
  tounes entre deux voix, une jumelle vise ce qui s'achète, deux répliques par événement de police et des voix que
  la rue n'a pas, le paquet porte ce que les ondes lisent (et pas leur texte) ; au banc : la radio parle entre les
  tounes sans tirer un dé, par la vraie boucle du jeu aussi, le Choc se tait, l'animateur attend la fin d'une
  réplique de mission, la pub de ton bar dit que c'est le tien, la police parle par le vrai chemin des étoiles, du
  barrage et de l'hélico, le scanner n'est pas une alarme, et une réplique de mission coupe les ondes — avec du son,
  ce qui passe atteint la sortie.

