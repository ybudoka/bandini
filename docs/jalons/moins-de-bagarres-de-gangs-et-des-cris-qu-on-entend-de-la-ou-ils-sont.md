# Moins de bagarres de gangs, et des cris qu'on entend de là où ils sont

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « je veux moins de bagarre de gang, et les cris doivent être moins fort
si on est loin et devenir plus fort quand on s'approche », puis « même que je veux pas
entendre quand on les voit pas ».

- ⚠️ **Mesuré : « par minute de jeu » trompait.** Une minute de jeu dure un tiers de seconde
  et `majBagarre` tire deux fois par seconde : à 0,12, **quatre secondes** en vue d'une
  frontière suffisaient pour qu'une rixe parte. `chance_par_minute` passe à **0,01**
  (attente moyenne **50 s**), tenue par `test_une_rixe_se_fait_attendre`, qui lit la cadence
  dans `entites.js`.
- ⚠️ **Et le coup (`SFX.arme`) et le grognement (`touche`) d'un autre partaient au plein
  volume, où que ce soit** — la rixe naît exprès hors champ, donc on l'entendait sans la
  voir. **Livré** : `Son.depuis(qui, effet)` — muet hors de l'écran, volume en ligne droite
  avec la distance au joueur (`audio.COUPS_DES_AUTRES`, portée 300 px : un cinquième au bord
  de l'écran), panoramique ; le joueur reste plein volume, et le filet de synthèse suit la
  même règle. Deux juges : la règle seule (filet et échantillon ; 200 px au-dessus est muet,
  200 px à droite s'entend) et une vraie rixe, hors champ puis vue de près. Les coups de feu
  des autres ne changent pas.
