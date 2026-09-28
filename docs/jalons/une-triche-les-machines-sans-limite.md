# Une triche : les machines sans limite

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (28 sept.) : « ajoute une triche pour enlever les limites des machines ». Une bascule
MACHINES SANS LIMITE dans la section TOUJOURS de l'onglet TRICHES, sauvée avec la partie
(`B.partie.triches.machines`) comme les autres. Allumée, le vidéopoker et la machine à sous
ne disent plus « la machine a assez mangé pour aujourd'hui » : le plafond du jour
(`mains_par_jour`, `tours_par_jour`) ne compte plus, et l'aide du menu dit SANS LIMITE. Le
compteur continue de compter (le hasard reste numéroté de la même main) ; éteinte, la limite
revient avec les mains déjà jouées ce jour-là.

- ⚠️ Les tables du casino (vague 2, en cours ailleurs) liront la même bascule si elles ont
  un plafond.

## Notes

✅ Livré le 28 sept. 2026.

- `B.partie.triches.machines` (`base.js`, éteinte dans une partie neuve et complétée à
  « éteinte » dans une vieille sauvegarde), basculée par **MACHINES SANS LIMITE**, la dernière
  ligne de TOUJOURS (`hud.js`).
- Trois plafonds la lisent, chacun à deux endroits — le geste qui refuse et la ligne du menu
  qui s'éteint : `mains_par_jour` du vidéopoker (`missions.js`), `tours_par_jour` de la
  machine à sous (`casino.js`), et les quarante coups par table (`tables.js`, livrées le même
  soir : Martin les appelait « des machines »). L'aide du menu dit **SANS LIMITE** à la place
  du compte.
- Le compteur compte toujours : le hasard reste numéroté par la même main, et la triche
  éteinte, la limite revient avec les coups déjà joués ce jour-là.
- Juges : un par sorte (`test_casino_js`, `test_videopoker_js`, `test_tables_js`), rouges
  avant le code ; la bascule ajoutée aux juges des triches sauvées (`test_debug_js`) ; et les
  deux juges d'ordre de l'onglet (cinq bascules, le saut depuis la dernière) suivent la
  sixième.

