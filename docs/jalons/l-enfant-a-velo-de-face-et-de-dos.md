# L'enfant à vélo, de face et de dos

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22 sept. 2026) : « améliore les images de face et de dos » des enfants à
vélo (`SPRITES.enfant_velo`, livré le 21 sept. avec les vélos). De profil, le vélo se lit ;
de face et de dos, la roue n'est qu'une barre noire sous un enfant en croix, les bras à
l'horizontale, les jambes droites comme debout — on dirait un monocycle. On redessine les
deux vues : le guidon qu'on voit et que les mains tiennent, la fourche et le garde-boue à la
couleur du cadre, le phare devant et le catadioptre derrière, la selle, les genoux pliés qui
pédalent (un en haut, un en bas), les pédales.

- ⚠️ Même grille (16 × 15), mêmes lettres, même ancre : rien d'autre ne bouge, et le casque
  doit rester ce qu'on voit en premier.

## Notes

Livré le 22 sept. 2026. Seules les poses `bas` et `haut` de `SPRITES.enfant_velo` changent (le
profil, la grille 16 × 15, l'ancre et les lettres restent) ; une lettre de plus, `l`, le phare.

Le modèle : **le cycliste du trafic**, peint par le jeu, de face et de dos — le vélo passe devant
lui, la roue fine descend seule jusqu'au sol. Sept jets, regardés dans le vrai jeu (une planche des
poses cuites par l'atlas, à côté du cycliste adulte, puis une rue nord-sud à l'échelle) :

- ⚠️ **Les pieds en l'air.** Ce qui dit « assis sur un vélo » et pas « debout derrière un bâton »,
  c'est que la roue touche le sol et pas lui : chaque chaussure sur sa pédale (grise), l'une plus
  haute que l'autre d'une image à l'autre, et au sol la roue seule.
- ⚠️ **Un jour de pixel entre les jambes et la roue.** Collés, contours compris, ils faisaient un
  seul pilier noir.
- ⚠️ **La couleur du cadre autour de la roue** : c'est elle qui dit « vélo » de loin. Le premier
  redessin l'avait perdue, et l'ancien, avec tous ses défauts, se lisait mieux à l'échelle du jeu.
- ⚠️ **De dos, le catadioptre seul sur le garde-boue**, les haubans une rangée plus bas : collé à
  un cadre rouge (un des six), il disparaissait.
- Jetés en route : les genoux écartés qui pédalent (des jambes de cow-boy) et l'enfant accroupi
  jambes ouvertes du premier jet.

Juge : `test_de_face_et_de_dos_on_voit_le_velo_et_il_est_assis_dessus` (phare de face, catadioptre
non collé au cadre de dos, cadre autour de la roue, chaque chaussure sur sa pédale, au sol la roue
seule) — il rougit sur l'ancien dessin. Les trois rouges croisés en chemin
(`test_amuseurs_js::test_le_public_applaudit_paie_et_se_renouvelle`,
`test_la_nuit_js::test_a_la_fermeture_on_sort_de_l_eau_et_on_rentre_hors_champ`,
`test_la_nuit_js::test_a_l_aube_le_camelot_lance_le_clairon_sur_les_perrons`) tombent aussi sur
`648eff9` sans lui.
