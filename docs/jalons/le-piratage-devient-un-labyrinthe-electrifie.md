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

## Notes
