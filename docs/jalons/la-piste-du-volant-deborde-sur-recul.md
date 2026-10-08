# La piste du volant déborde sur RECUL

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (8 oct. 2026, sur son iPhone) : « le joystick déborde sur le bouton ». La piste du
volant fait 220 px depuis le bord gauche ; sur un téléphone de 393 px en portrait, son bout
droit passe 19 px sous RECUL, et la NITRO (sur un char qui en a une) tombe en plein dessus.
Le juge navigateur du volant mesurait les chevauchements sur un écran plus large. À faire :
la piste se rétrécit à la place qui reste à gauche des pédales, la NITRO monte au-dessus
d'elle, et le juge mesure à la largeur d'un iPhone.

## Notes

✅ **Livré** (8 oct. 2026), avec deux autres retours de Martin le même jour, sur son iPhone : le bouton plein écran qui
ne faisait rien, et les commandes tactiles qui se montraient sur l'écran titre.

- **La piste** prend la place qui reste à gauche des pédales, 10 px d'air compris :
  `min(220px, 100vw − marges − 178px)` — 191 px sur un iPhone de 393 px en portrait, 220 px en paysage comme avant.
  Mesuré par le juge navigateur, avant la correction : RECUL à x = 215, la piste jusqu'à 234.
- **La NITRO** monte au-dessus du bout de la piste, à gauche de FREIN : au ras du bas, à gauche de RECUL, elle tombait
  en plein sur la piste d'un téléphone en portrait.
- **Le plein écran** : Safari sur iPhone n'a ni `requestFullscreen` ni `webkitRequestFullscreen` pour la page
  (seulement pour une vidéo). `Entree.initTactile` pose alors `body.sans-plein-ecran` : le bouton ⛶ part, PAUSE prend
  le coin. L'iPad et Android gardent le bouton.
- ⚠️ Les juges navigateur du volant mesuraient en paysage (844 × 390) seulement. Deux juges neufs à la taille d'un
  iPhone en portrait (393 × 852) : la piste avec et sans NITRO (rouge sur l'ancienne feuille), et le plein écran
  absent quand le navigateur ne sait pas le faire (le juge retire `requestFullscreen` avant le chargement ; rouge
  sans le code).
- **L'écran titre** (« sur l'écran principal, les boutons tactiles et joystick ne devraient pas apparaître ») :
  `#tactile` se cache tant que `#bandini` est au titre ou au chargement (`data-etat`). On y touche JOUER et les lignes
  du menu, sur la toile ; les commandes viennent avec la partie. Juge navigateur neuf, rouge sur l'ancienne feuille.
