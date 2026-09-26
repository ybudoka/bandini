# Le décor, les bêtes et les gens répondent

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

demande de Martin (21 sept. 2026) : « ajoute plusieurs interactions avec le décor,
l'environnement, les autres gens, et plus ».

_Ce que ça donne :_ ACTION cesse de ne servir que les portes, les chars et les comptoirs. Un
banc, une poubelle, une fontaine, une borne-fontaine, un artiste de rue et un touriste
**répondent** — six gestes qui prennent la même route que tout le reste (« on agit sur ce qu'on
regarde », `faceA`), sans un menu de plus et **sans un seul son neuf** (aucune génération
ElevenLabs : tout réemploie `argent`, `ramasse`, `nage`, `borne_cassee`, `touche`).

- **S'asseoir** (les quatre bancs) — la pose assise du corps du joueur (`assis_bas`, `assis_haut`,
  `assis_droite`, `assis_gauche`, déjà dessinées pour le patient de la salle d'attente), le souffle
  qui remonte deux fois et demie plus vite, une PV toutes les trois secondes **jusqu'à 60 % de la
  barre** — un banc repose, il ne soigne pas. Le stick, ACTION, un coup, un sprint ou l'arme nous
  lèvent ; ni avec la police aux fesses, ni en saignant.
- **Fouiller** (poubelle, ordures, bac, bac de recyclage, benne) — quelques sous, des canettes
  consignées, un reste de poutine, ou un rat qui mord (jamais à mort) ; **une fois par jour et par
  bac**, et le quartier compte : le bac d'un quartier cossu est presque vide, celui d'un quartier
  pauvre déborde.
- **Boire** (la fontaine de la place) — le souffle remonte, dix secondes avant d'avoir soif.
- **Ouvrir la borne-fontaine** (41 dans la ville) — la gerbe d'une borne défoncée, à la main : elle
  crache, elle s'entend de loin, elle se referme seule au bout de vingt secondes ou d'un
  deuxième ACTION, et on s'y rafraîchit (le souffle revient deux fois plus vite dans son rayon).
- **Un pourboire** (musicien, mime, jongleur, échassier) — un dollar dans le chapeau : la pièce
  change vraiment de poche (`e.argent`, comme celle d'un badaud), l'artiste répond d'un mot.
- **La photo du touriste** — il nous tend son appareil, on le prend, il paie **de sa poche** (2 à 5 $),
  une fois par touriste ; fauché, il dit merci quand même.

⚠️ **Le catalogue est en Python, le moteur en JS** (le principe de la maison) : `app/interactions.py`
dit quel décor donne quel geste, ce que chacun rend et les mots ; `static/js/interactions.js` les
joue et ne garde aucun nombre.

## Fiche de la deuxième vague

⚠️ **Annulé, sur demande de Martin (22 sept. 2026) : se cacher dans un buisson.** Le geste
était facile (186 buissons dans la ville, `casse: 0.9`, non solides) ; l'effet ne l'était pas —
`Police.voit(agent, x, y)` ne sait pas qui il regarde, il aurait fallu qu'il reconnaisse le
joueur caché et réduise sa portée, de l'équilibrage de la police (M11), pas un ajout de décor.
Ce couplage-là est resté sans réponse.

Et ce qui n'a pas été essayé : **arracher une affiche** « Recherché » (`police.majAffiches` les repose
sans fin tant que les étoiles durent — il faut d'abord un plafond par affiche arrachée),
**pousser un caddie**, **lire** un panneau.

## Notes

✅ **2e vague, troisième geste : vider un parcomètre** (22 sept. 2026).

- **Aucune place neuve non plus** : `parcometre` est déjà posé
  (`mobilier.MEUBLES_PAR_USAGE["commercial"]`, devant les commerces), juste jamais interactif —
  et contrairement au buisson (annulé, § plus haut), rien ici ne touche `Police.voit` : c'est
  un geste de décor ordinaire, pas de l'équilibrage.
- **C'est un DÉLIT** (`recherche.DELITS["parcometre"]`, le même gabarit qu'une distributrice
  défoncée — une étoile, `temoin: True`) : `Police.signalerCrime`/`quelqu_un_voit`, le même
  appel que pour une distributrice. Quelques dollars de monnaie, ça se raconte, ça n'alarme pas.
- **Le geste** (`interactions.PARCOMETRE`, `Interactions.forcerLeParcometre`) : la même route
  que `manger`/`fouiller` — 4 à 9 $, une fois par jour et par parcomètre (encore la même case
  `partie.fouilles`, préfixée `parc:`). Calibré entre les deux voisins : au moins autant que le
  meilleur tirage d'une poubelle (4 $), toujours sous une distributrice défoncée (22 $) et sous
  le dixième de la plus petite prime de mission.
- **Juges** (`test_interactions.py`, `test_interactions_js.py`) : le délit existe et suit le
  gabarit de la distributrice, la fourchette d'argent tient sa place entre poubelle et
  distributrice ; au banc : une fois par jour (même schéma que le barbecue), et le délit est
  bien signalé une fois (mutation vérifiée rouge — l'appel à `Police.signalerCrime` retiré).
- **Restent** : l'affiche arrachée, le caddie, le panneau.

✅ **2e vague, deuxième geste : caresser le chat** (22 sept. 2026).

- **Le chat SEUL a une confiance** (`pietons.BETES["chat"]["confiance_px"]`, 16 px) : au pas
  (pas d'`esquive` tenue), sans arme (`j.arme` à `'poings'` ou vide — ⚠️ `'poings'` est la
  valeur du joueur au repos, pas une chaîne vide : un premier `!j.arme` seul aurait laissé la
  confiance ne jamais s'activer), `Entites.majBete` réduit son `fuite_px` (74) à cette
  distance-là. Sprinter, sortir une arme ou monter en char, et il redevient aussi farouche que
  le goéland — qui n'a jamais cette clé (`test_interactions.py`).
- ⚠️ **LA FENÊTRE ÉTAIT TROP ÉTROITE POUR ÊTRE JOUABLE, ET LE PREMIER CHIFFRE LE PROUVAIT** :
  `confiance_px` à 20 px pour une portée d'ACTION (`interactions.CARESSER["portee_px"]`) de
  22 px ne laissait que 2 px entre « il fuit encore » et « trop loin pour caresser ». Ramené à
  16 px (6 px de marge), avec un juge qui verrouille la marge (≥ 5 px) pour que ça ne se reproduise
  pas — et l'inverse tient toujours : même confiant, 16 px reste au-dessus des 12 px d'un poing
  (`armes.par_slug("poings")`), l'invariant « on ne touche jamais une bête » ne bouge pas.
- **Le geste** (`interactions.CARESSER`, `Interactions.caresserLeChat`) : sa propre place dans la
  chaîne d'ACTION — ni les gens (`Combat.otageSousLaMain` ne voit jamais une bête), ni le décor
  (elle bouge, elle vit dans `B.betes` pas `B.entites`) — entre le bouclier humain et le décor.
  ⚠️ **Le seul des huit gestes qui ne rapporte rien** : pas de PV, pas de souffle, pas d'argent,
  juste un mot au HUD (`Hud.message`, pas une bulle — `dessinerBetes` n'en dessine aucune, en
  poser une par `Entites.bulle` ne se serait jamais vue).
- **Juges** (`test_interactions.py`, `test_interactions_js.py`, `test_betes_js.py`) : le chat ne
  rapporte rien, la marge jouable et l'invariant du poing sont verrouillés ; au banc : au pas et
  sans arme il laisse approcher (mutation vérifiée rouge — confiance forcée à faux), au sprint ou
  armé il fuit comme avant, ACTION près d'un chat confiant caresse sans rien gagner ni perdre et
  sans le faire fuir (mutation vérifiée rouge sur `utiliserSurLesBetes`), et loin d'un chat ACTION
  ne caresse rien.
- **Restent** : l'affiche arrachée, le parcomètre, le caddie, le panneau (le buisson est
  annulé, voir « Fiche de la deuxième vague »).

✅ **2e vague, premier geste : manger au barbecue** (22 sept. 2026).

- **Pourquoi celui-là en premier** : le seul des six restants qui n'a besoin d'aucune place
  neuve en ville — `bbq` existe déjà (`carte.DECOR_SOLIDE`, posé devant les maisons de
  banlieue, `poser_decor("bbq", x, y)`), juste jamais servi. Le chat suit juste après (une
  confiance à écrire, voir plus haut) ; l'affiche arrachée attend d'abord un plafond — celle-là
  reste (le buisson, lui, est annulé, voir « Fiche de la deuxième vague »).
- **Le geste** (`interactions.BARBECUE`, `Interactions.manger`) : la même route que `boire` —
  8 PV, 15 de souffle (`Missions.soigner`/`nourrir`), une fois par jour et par barbecue
  (la même case `partie.fouilles`, préfixée `bbq:` pour ne jamais collider avec une poubelle
  voisine). ⚠️ **Toujours sous le hot-dog acheté** (25 PV/40 de souffle, `economie.TARIFS`) :
  un juge le vérifie — on grignote, on n'achète rien.
- **Aucun son neuf** : `Son.SFX.ramasse()` (déjà celui d'un reste de poutine trouvé) et
  `Son.SFX.erreur()` pour le refus, comme les six premiers gestes.
- **Juges** (`test_interactions.py`, `test_interactions_js.py`) : le catalogue voyage dans le
  paquet, un décor ne donne qu'un seul geste, le barbecue reste sous le hot-dog, une portée
  d'une main ; au banc : on mange, une fois par jour (mutation vérifiée rouge sur le vrai
  garde — `refus`, pas la porte de secours redondante dans `manger()`, la même que
  `fouiller`/`boire` portent déjà), et manger à pleine vie ne fait pas déborder la barre.
- **Restent** (au moment de cette livraison) : le chat, le buisson, l'affiche arrachée, le
  parcomètre, le caddie, le panneau — le chat est livré juste au-dessus, à sa suite ; le
  buisson a depuis été annulé (voir « Fiche de la deuxième vague »).

✅ **Livré** (21 sept. 2026), première vague : les six gestes, sans un son neuf.

- ⚠️ **ACTION garde son ordre**, et c'est le point délicat de tout le jalon. `Missions.interagir` finit par
  le bouclier humain (« ce que le bouton fait quand il n'a rien d'autre à faire »), et `Combat.maj`
  enchaîne ensuite l'arme par terre, la porte et le **pickpocket**. Deux places, deux raisons :
  **les gens qui travaillent dans la rue** (pourboire, photo) passent **avant** le bouclier — il prend
  n'importe quel passant, il aurait pris le musicien ; **le décor** passe **tout à la fin** et se
  retire de lui-même devant une porte, une arme par terre, un char sous la main ou **quelqu'un dont les
  poches se prennent** (`Combat.victimeDesPoches`) — sans quoi un banc volait le geste du pickpocket
  à qui n'a que ses poings.
- ⚠️ **`Combat.pochesAPrendre` extrait** du pickpocket (la règle « derrière lui, ou assommé, et il a de
  l'argent ») : le pourboire ne s'y donne **pas** quand l'artiste a le dos tourné et de l'argent — c'est
  le geste du pickpocket. Une règle dite une fois, lue par les deux.
- ⚠️ **Une pression, un geste** (`j.gesteT`) : `Vehicules.maj` rappelle `interagir` **dans la même
  image** quand un char est sous la main (« la porte gagne sur la portière »). Sans le garde, un
  pourboire partait deux fois, et la pression montait dans le char après avoir payé l'artiste. Aucun
  appel direct de la fonction ne le voit — c'est un juge **par le bouton** qui l'a montré.
- ⚠️ **Assis, c'est le lit de l'hôpital** (`j.alite`) : une pose, `Entites.majJoueur` qui rend la main
  au stick (`Interactions.majAssis`), `cede()` qui ne pousse plus le joueur, quatre gardes de plus
  dans `Combat` (roue d'armes, cible, saisie, attaque). On se **sauvegarde là où l'on se tenait** :
  le banc est solide, et un joueur rechargé dedans ne saurait pas en sortir. La pression d'ACTION qui
  nous lève est **dépensée** (`Entree.videPresse`) : sinon `Combat.maj`, plus loin dans la même image,
  en faisait un pickpocket ou nous rasseyait aussitôt. **Refusé en saignant** : assis, `majJoueur`
  ne passe plus par `saigner`, et un banc qui arrête le sang est un banc qui rend les soins inutiles.
- **Le corps se dessine dans le bon ordre** (capture de Chromium, quatre bancs) : sur le banc de face,
  par-dessus ; sur le banc vu de dos, **avant** lui (`y` plus petit) pour que le dossier lui couvre
  les jambes ; sur les deux bancs de profil, par-dessus (`y` plus grand), sinon l'assise lui coupait
  le corps en deux.
- Les bacs fouillés vivent dans `partie.fouilles` (la clé `rue:tx,ty`, la valeur est le **jour**), à côté
  des tiroirs : une partie rechargée ne remplit pas les poubelles. Le pourboire, la photo et la soif
  d'une fontaine ne se sauvegardent pas.
- **Rien ne remplace une mission** (`test_interactions.py`) : le plus gros butin d'un bac reste sous
  le dixième de la plus petite prime (100 $), l'espérance d'une fouille sous 2 $, et un banc ne soigne
  ni plus d'une PV toutes les deux secondes ni au-delà de 60 % de la barre.
- **Deux fichiers de tests** : `test_interactions.py` (12 juges : le catalogue et ses bornes) et
  `test_interactions_js.py` (20 juges **par le bouton** : chaque geste, l'invite qui dit ce que ACTION
  fait, le dos tourné qui ne fait rien, la porte / l'arme par terre / le char qui passent avant le banc,
  le pickpocket qui garde ses poches, le char sous la main qui ne double pas le pourboire, le coup
  donné, le sprint ou l'arme qui nous lèvent, la pression du lever qui n'ouvre pas la machine d'à côté).
- ⚠️ **Vingt mutations** (retirer chaque règle, une par une : le regard, les poches, « une pression, un
  geste », la pression du lever, la porte, l'arme et le char séparément, le refus de la police, une
  fois par jour, la morsure qui ne tue pas, la sauvegarde assise, la gerbe, le quartier, le coup reçu, la
  photo une fois, le touriste qui paie de sa poche) **font rougir un juge chacune**. ⚠️ **Deux mutants
  ont d'abord survécu** — la porte/l'arme/le char (le juge de la porte posait le joueur devant une
  porte où AUCUN banc n'était : il jugeait le vide) et la pression du lever : quatre juges de plus.
- ⚠️ **Deux juges étaient déjà rouges avant ce jalon** et le restent, à l'identique sur la base sans lui
  (`test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`, « ils arrivent de hors de
  l'écran » ; `test_la_foule_ne_se_traverse_plus`, 333 chevauchements creusés) : pas de ce jalon, à
  reprendre à part. Le reste — 132 fichiers de la suite et les 38 juges Chromium — est vert.
- ⚠️ **Deux pièges de banc** à savoir avant de reprendre : `o.frame(1)` **ne fait pas toujours avancer
  la simulation d'un pas** (l'accumulateur d'images), donc deux gestes « à une image d'écart » tombent
  parfois dans la même image de jeu et le garde « une pression, un geste » en avale un — le juge attend
  que `B.t` ait bougé (`suivant()`) ; et un **sprint tapé est une roulade**, qui bloque ACTION tant que
  `j.roule` court.

✅ **2e vague : arracher une affiche « Recherché »** (26 sept. 2026).

- **Le plafond d'abord**, comme la fiche l'exigeait : chaque affiche arrachée en est une de moins que la
  police recolle (`affiches_max` moins `recherche.affichesArrachees`) jusqu'à la fin de la poursuite ; sous
  deux étoiles, les murs se vident et le compte repart à zéro.
- **Ce que ça donne** : ta face est sur les affiches, c'est pour ça que le STOOL te reconnaît — en
  arracher une lui laisse soixante secondes de plus (`interactions.AFFICHE`, `repit_stool_s`). Ce n'est pas
  un délit.
- **Le geste** : ACTION devant une affiche (« ARRACHER L'AFFICHE »), avant le reste du décor
  (`Interactions.afficheSousLaMain` ; une affiche est une entité à part, hors de l'index des décors).
- **Juges** (`tests/test_affiche_arrachee_js.py`, au bouton) : l'invite, l'affiche partie, le stool qui
  attend ; aucune recollée tant que la poursuite dure, le compte remis à zéro après. Trois mutations.
- **Restent le caddie et le panneau — à préciser par Martin** : le caddie de la ville est COUCHÉ (un décor
  renversé, cassable) — le redresser et le pousser, ou le fouiller ? Et le seul panneau qu'on vise est
  celui d'un défi, qui a déjà son ACTION — lire le nom de la rue (`adresse.js` le sait), ou les panneaux
  « À LOUER » des chantiers ?
