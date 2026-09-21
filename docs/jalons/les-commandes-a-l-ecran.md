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
