# Le piratage devient un labyrinthe électrifié

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 27 sept. 2026, après la relecture de m53 (« Sous pavillon ») : « pour le défi, je veux un jeu de
labyrinthe électrifié ». Tranché avec lui le même jour : il **remplace** la séquence de directions de
chaque objectif `pirater` (m53, m54 — cinq terminaux en tout), et l'étincelle **glisse librement** au
stick, comme le fil électrique des foires. La séquence de 4 directions disparaît.

**Le jeu.** Une boîte d'environ 200 × 120 px au centre de l'écran (480 de large) : un circuit en
couloirs de 14 px entre des fils électrifiés qui grésillent. On part de la **prise** (à gauche), on
arrive au **port** du terminal (à droite). L'étincelle est un point de 2 px de rayon avec une courte
traînée. Sa vitesse suit l'inclinaison de `Entree.axe` (plein régime ≈ 1,1 px par image, zone morte
0,22) : clavier en 8 directions à pleine vitesse, manette, stick tactile — le même axe que la marche,
rien de neuf à apprendre au pouce.

**Le zap.** Le cercle de l'étincelle touche un fil : éclair, `Son.SFX.erreur`, petite secousse, et
retour au dernier **relais** franchi (la prise, ou le relais posé à mi-chemin sur la solution, une fois
passé), avec une vingtaine d'images d'immunité. Au-delà de `essais` zaps : l'échec `alarme`, inchangé.
FRAPPE abandonne toujours (on revient au terminal par ACTION) — ⚠️ **les zaps restent comptés pour
l'objectif** : sans ça, abandonner remettrait le compteur à zéro gratuitement (ce que faisait la
séquence).

**Le tracé.** Un labyrinthe parfait (un seul chemin entre deux cases) tiré à l'**empreinte**
`slug + étape`, par un petit générateur à graine — ⚠️ **jamais `B.rng`** : le même labyrinthe à
chaque essai (on l'apprend), et aucun dé consommé dans la ville. `longueur` en donne la taille :
`longueur + 3` colonnes sur 4 rangées (m53, `longueur: 4` : 7 × 4 ; m54, `longueur: 5` : 8 × 4).
Aucune clé neuve dans les missions.

**Le code.** Un module neuf, `static/js/circuit.js` (`Circuit`), en fonctions pures qu'on juge
seules : `generer(empreinte, cols, rangs)`, `maj(etat, axe)` (rend `'zap'`, `'fini'` ou rien),
`dessiner(ctx, etat, x, y)`. `histoire.js` garde ce qu'il fait déjà — ouvrir (`commencerPiratage`),
refermer, avancer, échouer (`majPiratage`) — et `hud.js` (`dessinerPiratage`) délègue le dessin. Le
script se charge avant `histoire.js` ; il se nomme dans `docs/architecture.md`.

**Autour.**

- m53 : « PIRATE LE RELAIS — SUIS LA SÉQUENCE » devient « PIRATE LE RELAIS — SANS TOUCHER LES FILS » ;
  la réplique de Sven « Le boîtier est sur le quai. Reproduis ce qu'il montre, rien de plus. » devient
  « Le boîtier est sur le quai. Suis le courant jusqu'au bout. Ne touche pas les fils. » — une voix à
  refaire (`sven-m53-10`, ≈ 110 crédits).
- Les commentaires qui décrivent la séquence (`missions/__init__.py`, `m53.py`, `histoire.js`,
  `adresse.js`, `entree.js`) et les docs (`comment-monter-les-missions.md`, `architecture.md`,
  la fiche du jalon de Sven).

**Les juges.** `tests/test_piratage_js.py` est réécrit :

- un pilote au banc suit la solution (chemin calculé sur le labyrinthe) de la prise au port → l'objectif
  avance ;
- pousser contre un fil → un zap, retour au relais ; `essais` + 1 zaps → échec `alarme` ;
- deux ouvertures du même terminal → le même labyrinthe, et `B.rng` n'a pas bougé ;
- chaque labyrinthe de m53 et m54 : un chemin de la prise au port, des couloirs plus larges que
  l'étincelle ;
- FRAPPE abandonne, et les zaps restent comptés à la réouverture.

Les parcours de bout en bout de m53 et m54 (`test_sven_missions_js.py`) restent verts, et une capture
Chromium du labyrinthe peint est regardée avant de livrer : les juges verts ne voient pas un dessin raté.

**Ce qui guette.** Au doigt, un couloir de 14 px à 1,1 px par image doit rester jouable : le régler à
la capture, pas au juge. La boîte ne doit pas cacher le terminal ni l'étincelle derrière le HUD d'une
mission (le bandeau d'objectif en haut).

### Plan d'exécution

> Exécuté dans la session (Martin, 27 sept. 2026 : « oui code »), tâche par tâche, dans un worktree.

**But.** Remplacer la séquence de `pirater` par un labyrinthe à parcourir au stick. **Architecture** :
un module pur `Circuit` (tracé, pas, dessin) ; `Histoire` l'ouvre, le fait avancer et tranche
(avancer, `alarme`) ; `Hud` le peint. **Contraintes** : aucun `B.rng` ; aucune clé neuve dans les
missions ; `B.piratage` reste la porte que lisent `combat.js`, `entites.js`, `interactions.js`.

**À surveiller (aucun juge ne l'attrape de lui-même).** Une diagonale au clavier qui frotte un
coin (les poteaux aux croisements comptent comme des fils) ; l'étincelle qui sort de la boîte par la
prise ; un zap qui recompte à chaque image tant qu'on reste collé (l'immunité) ; ouvrir, abandonner et
rouvrir pour remettre les zaps à zéro ; la mission qui finit ailleurs pendant que la boîte est ouverte.

**Tâche 1 — le module `static/js/circuit.js`.** `Circuit.generer(empreinte: string, cols, rangs)` →
`{ cols, rangs, est: bool[], sud: bool[], entree: rang, sortie: rang, solution: [{c, r}], relais: {c, r} }`
(labyrinthe parfait, retour arrière sur pile, graine FNV-1a de l'empreinte, générateur mulberry32) ;
`Circuit.ouvrir(plan, zaps)` → l'état `{ plan, x, y, relais, zaps, immunite, eclair, trace }` ;
`Circuit.maj(etat, axe)` → `'zap'`, `'fini'` ou `null` ; `Circuit.touche(plan, x, y)` ;
`Circuit.dessiner(ctx, etat, x0, y0)` et `Circuit.taille(plan)`. Chargé dans `templates/index.html`
avant `histoire.js`. Juges (`tests/test_circuit_js.py`) : même empreinte → même tracé, deux empreintes →
deux tracés ; toute case atteinte depuis la prise, la solution va de la prise au port par des
passages ouverts ; `B.rng` intact ; au centre d'un couloir rien ne touche, contre un fil ou un poteau
ça touche ; `maj` pousse l'étincelle, le zap la ramène au relais et ne recompte pas pendant
l'immunité ; passer le relais le retient ; atteindre le port rend `'fini'`.

**Tâche 2 — le brancher.** `commencerPiratage` : `Circuit.generer(slug + ':' + étape, longueur + 3, 4)`,
zaps repris de `B.mission.zaps[étape]` ; `majPiratage` : FRAPPE abandonne, `'zap'` → son d'erreur,
secousse, zaps notés, au-delà de `essais` → `alarme` ; `'fini'` → `avancer()`. `DIRS_PIRATAGE` et les
seuils partent. `Hud.dessinerPiratage` peint la boîte (le circuit, les zaps restants, la consigne) et
pose l'ancre `piratage`. Juges : `tests/test_piratage_js.py` réécrit (ouvrir au bouton, le pilote au
clavier qui suit la solution fait avancer l'objectif, un fil → zap et relais, `essais` + 1 → alarme,
FRAPPE abandonne et les zaps restent, l'étiquette du bouton, le HUD dessine) ; le pilote `pirater` de
`tests/test_sven_missions_js.py` suit la solution au lieu de la séquence.

**Tâche 3 — les mots.** m53 (texte de l'étape 2, réplique `sven-m53-10` et sa voix), les commentaires
qui décrivent la séquence, `comment-monter-les-missions.md`, `architecture.md` (le module),
la fiche du jalon de Sven.

**Tâche 4 — le regarder.** Capture Chromium du labyrinthe ouvert (m53 puis m54) dans `captures/`,
réglage de la taille et des couleurs à l'œil, puis les juges ciblés, `ruff`, atterrir.

## Notes

**Livré le 27 sept. 2026.** Les cinq terminaux de m53 et m54 sont des labyrinthes : `circuit.js`
(le tracé, l'étincelle, le dessin), `Histoire.commencerPiratage` / `majPiratage` (les zaps notés dans
`B.mission.zaps` par étape, la secousse, l'alarme), `Hud.dessinerPiratage` (la boîte, un point par
essai, rouge une fois brûlé). m53 dit « SANS TOUCHER LES FILS », et Sven « Suis le courant jusqu'au
bout, sans toucher les fils » (voix `sven-m53-10` refaite).

- ⚠️ **Réglé à la capture, pas au juge** : à 14 px la case, la boîte de m53 faisait 100 × 60 px sur
  480 — illisible au téléphone. Elle a maintenant 18 px la case, une étincelle de 3 px de rayon
  (10 px de jeu dans un couloir) et 1,3 px par image à fond : m53 fait 146 × 99 px, m54 164 × 99. La
  boîte descend à y = 84 : le titre de la mission (« SOUS PAVILLON ») la chevauchait à 70.
- ⚠️ **Tous les poteaux touchent**, même entre deux côtés ouverts — dans un labyrinthe parfait,
  aucun croisement n'est libre de ses quatre fils ; c'est là qu'une diagonale au clavier frotte.
- ⚠️ **Le pilote du banc** (`test_piratage_js.py`, `test_sven_missions_js.py`) tient une touche à la
  fois vers le centre de la case suivante de la solution, avec une tolérance d'une demi-`VITESSE` :
  plus serrée, il oscille autour du centre sans jamais s'arrêter.
- Juges : `test_circuit_js.py` (6, le module seul — trois mutations mordent : sans poteaux, sans
  immunité, sans relais) et `test_piratage_js.py` réécrit (7).
