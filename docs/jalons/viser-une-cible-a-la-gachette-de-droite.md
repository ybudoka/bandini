# Viser une cible à la gâchette de droite

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin : « le bouton RT doit servir pour viser une cible au lieu du bouton 2 ».
Sur sa 8BitDo en Bluetooth (`bt_dinput`), VISER UNE CIBLE était le bouton 2, un numéro que
DirectInput saute : l'aide disait « BOUTON 2 » et aucun bouton ne visait. À pied, VISER suit
désormais la gâchette de droite — la pédale de gaz du profil, bouton ou axe, disposition
sauvée comprise ; au volant elle reste le gaz. Plus de bouton VISER à part (ni le 2, ni le
clic du stick) ; l'aide COMMANDES montre RT ; juges par le bouton.

## Notes

Livré le 22 sept. 2026.

- **VISER n'a plus de bouton** : c'est la gâchette de droite, la pédale de GAZ du profil
  (`entree.js`, `gachetteVise`). Elle suit donc le gaz tel qu'il est connu — un bouton (7 sur
  une manette reconnue, 9 sur la 8BitDo en DirectInput) ou un axe réappris — et les manettes
  Touch du casque aussi. Tape = verrouille / cible suivante, tenue = déverrouille, comme avant.
- ⚠️ **Au volant, la gâchette reste le gaz** : `Combat` ne lit le verrou qu'à pied, et remet
  son compteur à zéro dans un char — descendre gâchette enfoncée ne verrouille rien.
- ⚠️ **La disposition sauvée de Martin** (`options.manette`, `verrouiller: [2]`) n'a pas besoin
  d'être refaite : `reglerManette` ne recopie que les actions qui ont un bouton, et VISER n'en a
  plus. Le 2 ne fait plus rien.
- Retirés : le `verrouiller` des dispositions (`manettes.py`, le 2 de `bt_dinput` et le clic du
  stick des autres), sa ligne dans RÉAPPRENDRE (« TOUT RÉAPPRENDRE » passe à onze gestes) et sa
  pièce `centre` du dessin de l'écran MANETTE. L'aide COMMANDES dit **RT** (R2, ZR selon la
  famille), la même pièce que GAZ au volant.
- Clavier inchangé : H.
- Juges par le bouton : `test_viser_a_la_gachette_js.py` (RT vise, le 2 ne vise plus, tenue
  déverrouille ; gâchette sur un axe ; au volant RT accélère sans verrouiller ; l'aide dit RT).
  Mutation : sans l'appel à `gachetteVise` dans `lireManette`, deux rouges.
