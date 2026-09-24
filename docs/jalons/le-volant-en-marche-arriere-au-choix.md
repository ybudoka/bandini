# Le volant en marche arrière, au choix

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (17 sept. 2026) : « je pense que ce serait logique d'inverser les contrôles de
virage gauche et droite quand on recule avec un véhicule », puis « mets-le dans une option de
jeu ». Mesuré avant : depuis M3, `majPhysique` inverse **déjà** le volant en marche arrière,
comme une vraie auto (droite : l'arrière part à droite du conducteur, le char tourne dans le
sens inverse des aiguilles d'une montre). Vue de dessus, ça ne colle à l'écran que nez en
haut. L'option garde le même sens de rotation qu'en marche avant (droite = horaire, toujours).

- Une bascule dans OPTIONS, sauvegardée avec les autres ; par défaut, rien ne change.
- Pour le joueur seulement : la police et le trafic gardent la physique d'auto.
- ⚠️ Le signe de la **rotation**, pas la consigne du stick : le volant est lissé
  (`volant_prise`), inverser la consigne le ferait traverser de butée à butée au passage à
  vitesse nulle, et le char tournerait du mauvais côté au début de chaque recul.

**Livré le 17 sept. 2026.**

- `B.options.reculCommeEnAvant` (NON par défaut), sauvegardée avec les autres options ; la
  ligne « VOLANT EN MARCHE ARRIÈRE » des OPTIONS dit `COMME UNE AUTO` ou `COMME EN AVANT`.
- `commandesJoueur` passe l'option à `majPhysique`, qui ne retourne plus le signe de la
  rotation quand elle est là. La police et le trafic appellent `majPhysique` sans elle.
- **Juges** : `test_le_volant_en_marche_arriere_se_choisit_dans_les_options` conduit **au
  clavier** dans la boucle (D tenu, W puis S) et mesure la rotation image par image dans les
  deux réglages, plus un char qui n'est pas au joueur ;
  `test_l_option_du_volant_en_marche_arriere_se_bascule_et_se_garde` passe par le menu. Rouges
  sur trois mutations : l'option ignorée, la consigne retournée au lieu du signe (une image à
  rebours au passage à zéro, −0,002 rad), l'option lue pour tous les chars.
