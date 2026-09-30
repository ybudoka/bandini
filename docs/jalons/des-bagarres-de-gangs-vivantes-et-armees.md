# Des bagarres de gangs vivantes, et armées

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 30 sept. 2026 : « revise les bagarres de gang pour que ce soit dynamique et réaliste,
aussi des armes à feu »._

_Ce que ça donne :_ une bagarre de gangs qui bouge — ils encerclent, reculent, s'abritent derrière un char,
tirent par salves, rechargent, fuient blessés, appellent du renfort — et chaque gang se reconnaît à son arme.

**Aujourd'hui** :
- **La rixe à la frontière** (`entites.js`, état `bagarre`) : trois contre trois ; chacun marche droit sur le
  rival le plus proche, se plante à 22 px et frappe au bâton au métronome (`e.t % 38`), 25 s, puis les
  debout s'en vont.
- **Un gang contre toi** (état `attaque_joueur`) : il court en ligne droite, frappe toutes les 40 images à
  18 px. Ni cercle, ni recul, ni abri.
- **Aucun membre de gang n'a d'arme à feu** (`pietons.py` : `batte`, ou rien). Le seul PNJ qui tire est
  l'agent (`police.js`), et `Combat.tirer` d'un PNJ vise **toujours le joueur**.
- Le joueur, lui, a treize armes ; la balle s'arrête au décor (`mordreLeDecor`) — l'abri existe déjà.

**Tranché avec Martin (30 sept. 2026)** :
- **Les deux bagarres** : un seul cerveau de combat sert la rixe gang contre gang ET le gang qui te tombe
  dessus.
- **Un arsenal par gang**, porté par **un membre sur trois** ; les autres gardent leur arme blanche :

  | Gang | Arme signature | Sa façon de se battre |
  |---|---|---|
  | Cravates (Faubourg) | pistolet | propre, précis, mi-distance |
  | Morues (Quais) | fusil à pompe | foncent, tirent de près |
  | Chevreuils (Érables) | carabine | restent loin, lents et justes |
  | Boulonneux (La Shop) | mitraillette | rafales qui s'ouvrent, les plus dangereux |
  | Skateux (La Pointe) | cocktail Molotov | lancent et courent, mettent le feu |
  | Mantes (Petit-Canton) | **aucune** | l'école : les techniques, pas les balles |

- **Les quatre comportements** : la tactique au contact, la fusillade, le moral et les blessés, les renforts.
- **L'approche A** : un module neuf, livré en quatre vagues.

### L'architecture

- **`app/rixes.py`** — la fiche, envoyée au paquet sous `B.defs.rixes` : `ARSENAL` (gang → arme), `PART_ARMEE`
  (1/3), la **distance de tir** de chaque arme (le fusil de près, la carabine de loin), et les réglages de
  chaque vague (`CONTACT`, `FUSILLADE`, `MORAL`, `RENFORTS`). Rien n'est codé en dur dans le navigateur.
- **`static/js/rixe.js`** — le cerveau : `Rixe.maj(e, cible)`. Il connaît trois **rôles**, lus sur l'arme en
  main : `melee` (bâton, couteau, poings), `tireur` (type `tir` sans cloche), `lanceur` (la cloche du
  Molotov). L'état du combattant tient dans `e.rixe` (`posture`, `minuterie`, `abri`, `salve`, `chargeur`).
- **`entites.js`** ne fait plus que **déléguer** : la branche `bagarre` passe le rival (`rivalDe`), la branche
  `attaque_joueur` passe le joueur. Les Mantes (`Techniques.parer`), le cousin qui dicte ses coups
  (`coupsDictes`) et l'allié (`allie`) gardent leur branche : le cerveau ne les prend pas.
- **`Combat.tirer(e, arme, cible)`** — une cible optionnelle ; sans elle, le joueur (l'agent ne change pas).
- **Qui t'attaque ne change pas** : `hostile_si_arme`, `hostile_toujours`, la cour, l'îlot pris — seule la
  façon de se battre change.
- **L'arme d'un membre** se tire **à l'empreinte** à sa naissance (`hash2(e.id, …) % 3`), jamais au dé du
  jeu. Seuls les membres nés de la rue et des rixes la reçoivent : un homme de mission garde l'arme que sa
  mission lui donne (« la première bagarre se gagne aux poings » reste vraie).

### Les vagues

1. **Le cerveau et la tactique au contact.** `rixe.js` et `rixes.py` ; les deux branches y délèguent. Au
   contact : ils se **répartissent autour** de la cible (chacun sa place sur un cercle, par son numéro) au
   lieu de faire la file ; ils **tournent** (un pas de côté), **reculent** après leur coup, **esquivent**
   parfois un coup armé ; chacun frappe **à son rythme** (une cadence de base, décalée à l'empreinte), plus
   jamais au métronome commun.
2. **L'arsenal et la fusillade.** Un membre sur trois porte l'arme de son gang et la sort **dès que le
   combat commence**. Le tireur tient **sa distance** (celle de son arme), cherche un **abri** à portée (un
   char, un mur, du mobilier qui arrête la balle), **sort pour une salve** de deux à quatre coups, **rentre**,
   et **recharge** — un temps mort qu'on voit et qu'on peut punir. Avant sa première balle, il **lève
   l'arme** un instant (le geste qu'on voit venir, comme l'anticipation d'un coup). Il **manque** : sa
   dispersion est plus large que la tienne. Le lanceur de Molotov vise **le groupe**, puis s'éloigne en
   courant.
   - Un coup de feu entre gangs **s'entend** (`Police.entendre`) et fait fuir la rue, mais **ne te colle
     aucune étoile** : c'est un crime d'autrui (`Police.crimeDAutrui`).
   - Une balle perdue qui couche un passant **ne t'est pas comptée** (ni force de gang, ni recherche).
3. **Le moral et les blessés.** Sous un seuil de vie, un blessé **recule** et se bat de loin, ou **fuit en
   boitant** ; quand un camp a perdu la moitié des siens, **les autres se sauvent** (la déroute). Un membre
   couché **lâche son arme** au sol — on la **ramasse** comme les autres.
4. **Les renforts.** Un membre qui perd **crie** ; les siens à portée (dans la bulle, hors de l'écran)
   **accourent**, au plus quelques-uns par rixe ; une fois sur quelques-unes, ils arrivent **en char** et en
   descendent. Une rixe où l'on s'attarde peut donc grossir.

### Ce qui guette

- **Le hasard de la ville** : rien au `B.rng` du monde pour choisir une arme, une place ou un renfort — tout
  à l'empreinte (`hash2`). Un renfort né « au dé » décalerait tous les dés qui suivent (la leçon du char en
  panne), et une entité posée tôt décale les identifiants (e12).
- **Personne n'apparaît à l'écran** : renforts et rixes naissent hors champ (`visibleAEcran`), comme
  aujourd'hui.
- **Les trois réflexes « contre le joueur »** (`alerter`, `blesser`, `majAttaque`) ont chacun leur juge :
  une balle de rixe ne doit pas les réveiller contre toi.
- **L'équilibre** : une mitraillette de Boulonneux, à trois, peut te coucher en deux secondes. Un facteur de
  dégâts des tirs de gang contre le joueur (`degats_contre_joueur`, dans la fiche) se règle au banc, et la
  levée d'arme te laisse le temps de rouler.
- **Les exceptions tenues** : la paix du Boss (pas de rixe), les alliés (ne te touchent jamais, ni une balle),
  un gang libéré ou calmé (M16), les Mantes (sans arme à feu), les missions qui nomment un gang (`groupe`).
- **Le poids du paquet** : la fiche `rixes` s'ajoute au paquet — `test_definitions` dans les juges ciblés.

### Juges (par vague)

1. Deux membres au contact d'une même cible ne sont jamais à la même place (le cercle) ; deux membres ne
   frappent pas à la même image plus d'une fois sur N ; après son coup, il recule ; la rixe finit toujours.
2. Un gang sur trois porte son arme signature, **toujours la même** pour le même membre (l'empreinte) ; les
   Mantes jamais ; le tireur se tient dans sa fourchette de distance ; il va à l'abri quand il y en a un ; il
   recharge après son chargeur ; une rixe armée ne te donne aucune étoile ; un homme de mission garde son
   arme.
3. Un blessé sous le seuil recule ; la moitié du camp couchée, les autres fuient ; l'arme lâchée se
   ramasse.
4. Un cri fait accourir les siens, jamais plus que le plafond, jamais à l'écran ; rien ne tire `B.rng` (la
   ville ne bouge pas : les juges « ce module ne déplace rien »).

Et à chaque vague : une **capture** de la rixe (Chromium), et la jouer au banc.

## Notes
