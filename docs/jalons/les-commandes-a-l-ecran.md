# Les commandes à l'écran : l'aide du début, et le vrai bouton sous le pouce

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « au début du jeu, comme les bonnes pratiques, je veux avoir
un affichage d'aides pour que les joueurs puissent savoir comment ça fonctionne. Si une manette
est branchée, il faut indiquer visuellement sur quel bouton peser pour telle ou telle action, et
plus. »

Ce qui existe, et ce qui manque : une ligne d'aide **clavier** sous « Jouer » (cachée au tactile,
muette pour qui tient une manette) ; l'écran MANETTE des options, dont le dessin s'allume bouton
par bouton — une **preuve de disposition**, pas une aide, et on ne le trouve qu'en le cherchant ;
l'invite « ACTION : ENTRER » et le « ACTION > » des dialogues nomment l'action, jamais le bouton.

**Vague 1 — l'écran COMMANDES.** Il s'ouvre à la fin de l'ouverture d'une partie neuve (tout de
suite si l'ouverture ne peut pas jouer), une fois par partie (`commandesVues`), et se rouvre de
PAUSE > COMMANDES. Il parle **l'appareil qu'on tient** — le dernier qui a servi : clavier, manette
ou doigt — et change sous les yeux quand on passe de l'un à l'autre. À la manette : le dessin
agrandi, chaque bouton relié à ce qu'il fait par un trait, avec les lettres de sa famille (Xbox
A B X Y, PlayStation croix rond carré triangle dessinés, Nintendo) ; on appuie, le bouton **et**
son nom s'allument. Deux pages, À PIED et AU VOLANT : les mêmes boutons n'y font pas la même
chose. Au clavier, des touches dessinées ; au doigt, le plan de l'écran tactile. La ligne du
titre suit aussi l'appareil : une manette branchée y lit ses boutons, pas WASD.

**Vague 1 (suite) — le vrai bouton dans les invites.** « ACTION : ENTRER » montre le bouton
dessiné (A, croix, E…) ; au doigt il reste « ACTION », c'est le nom écrit sur le bouton. Même
chose pour le « ACTION > » des dialogues.

- ⚠️ La manette de Martin (8BitDo en Bluetooth, `mapping: ''`) : les lettres suivent la
  **position** du bouton dans la disposition choisie, jamais son numéro — un numéro DirectInput ne
  dit rien de la lettre imprimée dessus.
- ⚠️ Le dessin de l'écran MANETTE place chaque action à une position fixe ; une disposition
  réapprise bouton par bouton garde ce dessin. L'aide fait pareil : un bouton pressé allume la
  pièce de l'action qu'il commande.
- ⚠️ Pendant l'aide la ville est figée (c'est un menu) ; la manette y **allume**, elle ne ferme
  pas — seul ACTION ferme, sinon on la ferme en essayant un bouton.
- ⚠️ Un écran se juge à l'écran : une capture Chromium par appareil avant de livrer.

## Notes

**Livré le 21 sept. 2026 (vague 1 entière).** `manettes.py` porte les tables : la pièce du dessin
de chaque bouton (`pieces`), les lettres de trois familles (`FAMILLES`), la détection
(`DETECTION`) et les deux pages (`PAGES_COMMANDES`). `entree.js` sait quel appareil on tient
(`appareil`) et quelle famille est la manette (`familleManette`) ; `hud.js` dessine l'écran
(`menuCommandes`), le vrai bouton dans l'invite et les répliques (`glypheDAction`), et la ligne
du titre (`majAideDuTitre`). OPTIONS > MANETTE a une ligne LETTRES DES BOUTONS (auto, Xbox,
PlayStation, Nintendo). Juges : `test_commandes_js.py` (9), `test_manettes.py` (+14), et trois
juges du navigateur (le neuf joue tout à la manette, du titre à la ville).

- ⚠️ **Ce que les captures ont trouvé et qu'aucun juge ne voyait** : « Xbox Wireless
  Controller » contient le nom d'une DualShock 4 (une croix bleue sous le A — le motif est
  maintenant ancré, `^wireless controller`) ; les traits s'arrêtaient au bord de la manette
  (ils se tracent par-dessus) ; au téléphone en paysage, le plan tactile centré poussait FRAPPE
  et SPRINT sous les vrais boutons (décalé à gauche, et chaque ligne est une ancre du HUD que
  le juge tactile mesure — la mutation « recentrer » le fait rougir) ; au volant, les trois
  lignes du pouce tombaient dans le cercle du joystick (elles s'empilent vers le haut).
- ⚠️ **La manette ne reprend l'appareil que sur un geste NEUF** (un bouton qui s'enfonce, le
  stick poussé au-delà de 0,5) : une vraie manette branchée au Mac, au repos, gardait
  l'appareil contre le clavier dans Chromium. Un stick qui dérive ou un bouton rendu enfoncé en
  permanence l'auraient repris à chaque image.
- ⚠️ **Le stick ne tourne pas la page** : on le pousse pour voir MARCHER s'allumer, et la page
  tournait sous le pouce (vu au banc). La croix, les flèches et le pouce la tournent.
- ⚠️ **La pause garde sa règle** : RETOUR (Effacer, B) revient à la PAUSE, PAUSE reprend le jeu.
- ⚠️ **VISER sur la 8BitDo en DirectInput** : son bouton 2 n'est nulle part sur la manette ;
  l'aide le dit « BOUTON 2 », sans trait. Une disposition réapprise garde les pièces de la
  disposition par défaut (comme le dessin de l'écran MANETTE), sauf VISER.
- ⚠️ `test_ouverture.py` et `jouer(page)` de `test_navigateur.py` ferment maintenant l'aide avant
  de marcher : c'est la promesse nouvelle, pas un contournement.
- Sept mutations, sept juges rouges : `manetteInerte`, l'ouverture qui ouvre l'aide, l'ancre de
  la détection (banc et Python), l'appareil clavier, le geste neuf, le plan tactile recentré.
