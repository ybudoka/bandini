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

**Ce qui reste, et pourquoi la première vague ne l'a pas pris** — deux gestes ont été écartés
**exprès**, parce que chacun demande de toucher à un mécanisme qui n'est pas le sien :

- **Caresser le chat des ruelles** — le chat **fuit à 74 px** (`pietons.BETES.chat.fuite_px`) et le
  bras d'ACTION porte à 22 : on n'atteint jamais un chat. Il faut une **confiance** (un chat qui
  laisse approcher qui marche doucement et sans arme) dans `Entites.majBete`, ce qui change le
  juge des bêtes (`test_betes_js.py` : « elle part avant qu'on la touche »). Le goéland,
  lui, doit rester farouche.
- **Se cacher dans un buisson** (186 dans la ville, `casse: 0.9`, non solides) — le geste est
  facile ; l'**effet** ne l'est pas : `Police.voit(agent, x, y)` ne sait pas qui il regarde, il
  faudrait qu'il reconnaisse le joueur caché et réduise sa portée. C'est de l'équilibrage de la
  police (M11), pas un ajout de décor. À faire avec un juge de poursuite (semer un agent en se
  cachant, et jamais à moins de N pixels).

Et ce qui n'a pas été essayé : **arracher une affiche** « Recherché » (`police.majAffiches` les repose
sans fin tant que les étoiles durent — il faut d'abord un plafond par affiche arrachée),
**vider un parcomètre** (un délit de plus dans `recherche.DELITS`), **pousser un caddie**, **manger
au barbecue** d'un parc (12 dans la ville), **lire** un panneau.

## Notes

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
