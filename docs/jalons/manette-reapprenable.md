# Manette réapprenable

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (« les boutons de la manette bluetooth ne sont pas bien mappé ») : les
numéros de boutons d'une manette que le navigateur ne reconnaît pas (`mapping: ""`) ne
veulent rien dire — la même manette n'a pas les mêmes numéros sur le téléphone et sur le
Mac, **ça ne se devine pas**. OPTIONS > **MANETTE** : des **dispositions à choisir**
(`app/manettes.py` : Xbox/PlayStation, **8BitDo en Bluetooth**, Bluetooth croix-sur-un-axe)
et un **dessin de manette en pixels** qui sert de **preuve** — on appuie, la pièce
s'allume ; au bon endroit, c'est la bonne disposition. Le dessin s'allume par **numéro de
bouton**, pas par action : l'épaule droite et le bouton de gauche font la même chose et
doivent pourtant se distinguer.

- ⚠️ Sur cet écran la manette ne **ferme** plus le menu (`manetteInerte`) — on y appuie sur
  ses boutons pour les voir, pas pour commander — mais elle peut encore bouger le curseur et
  choisir, sinon un joueur qui n'a qu'une manette resterait enfermé. Deuxième écran,
  RÉAPPRENDRE : ce que la manette dit d'elle-même (nom, RECONNUE / NON RECONNUE, boutons
  enfoncés et axes qui bougent en direct), une ligne par action qu'on réapprend en
  l'appuyant, la croix en quatre gestes, gaz et frein en **bouton ou en axe** (repos
  mesuré : une gâchette-axe repose à −1 sur une manette et à 0 sur la suivante), TOUT
  RÉAPPRENDRE qui enchaîne, PAR DÉFAUT ; gardé dans les options. **Croix-chapeau** : sur une
  8BitDo en Bluetooth la croix n'est pas quatre boutons mais UN axe — on appuie et aucun
  numéro ne s'allume, elle a l'air morte ; on apprend HAUT et DROITE et le tour des huit
  positions se déduit, diagonales comprises (sinon repli sur les quatre côtés). L'écran
  liste les **axes qui bougent**, nomme un bouton **que la disposition ne connaît pas**
  (sinon il n'allume rien et on croirait la manette morte), et souffle le mode Xbox aux
  8BitDo (le dongle 2,4 GHz ou le câble : c'est là que le navigateur les reconnaît).
- ⚠️ **Mesure de Martin** : ses gâchettes ouvraient la carte et la pause — or carte et pause
  sont 8 et 9 sur une manette reconnue, donc ses gâchettes _sont_ 8 et 9, et toute la
  numérotation DirectInput suit (boutons de droite 0/1/3/4, épaules 6-7, SELECT/START
  10-11). Un juge garde ce fait : le « corriger » effacerait le retour.
- ⚠️ Un apprentissage **attend qu'on relâche** : sur un axe, lâcher le haut bouge autant
  qu'appuyer sur le bas, et la direction suivante s'apprenait sur la valeur du repos — la
  croix tenait alors les quatre directions en permanence. Corrigé au passage : `annuler`
  n'avait **aucun** bouton (le bouton de droite fait RETOUR), et « Jouer » n'était qu'un
  bouton de la page — on commence maintenant la partie à la manette ou au clavier
