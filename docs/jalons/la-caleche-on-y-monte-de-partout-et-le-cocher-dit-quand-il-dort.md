# La calèche : on y monte de partout, et le cocher dit quand il dort

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 28 sept. 2026 : « je ne peux plus embarquer ». Sa partie : au rang à 2 h 54, debout
près des chevaux. La nuit (22 h à 7 h), la calèche refusait sans un mot ; le jour, seulement
à 30 px de l'arrière ou du milieu. On monte à côté de la caisse, de n'importe quel côté ;
hors des heures, l'invite dit que le cocher dort et quand revenir.

Puis, en cours de route (Martin, 28 sept. 2026) : « la calèche devrait être absente si fermée ».

## Notes

**Livré le 28 sept. 2026.** Ce n'était pas une régression des virages (`la-caleche-sa-pancarte-dans-l-axe…`) :
la règle était déjà là, mais elle refusait sans un mot. La partie de Martin (`donnees/bandini.sqlite3`) : au rang
à 2 h 54, debout au-dessus des chevaux, à 43 px du milieu de la caisse et 62 de son arrière.

- **La cabane fermée, pas de calèche** : hors des heures du comptoir `sucre` (7 h à 22 h) ET hors du temps des
  sucres, comme les gens de la cabane (`onFaitBouillir`). `etat.absente` ; `Cabane.caleche()` rend `null`. Elle
  s'en va et revient à son arrêt **hors de la vue** (`enVue`, la caisse et les chevaux à 48 px près de l'écran),
  jamais sous nos yeux, et un tour commencé se finit — un passager le finit aussi. Arriver au rang la nuit : elle
  n'est déjà pas là.
- **Le cocher dit quand il attelle** (`calecheFermee`) : à 44 px de l'arrêt ou de la pancarte, la cabane fermée,
  l'invite dit « PAS DE CALÈCHE — LE COCHER ATTELLE À 7 H » (l'heure lue au comptoir), ou « … — ON ATTELLE AU
  TEMPS DES SUCRES » hors saison, et ACTION le redit.
- **On monte de partout** : à 16 px du bord de la caisse OU des chevaux, de n'importe quel côté (`horsDe`, la
  boîte orientée qui bloque), au lieu de 30 px de l'arrière ou du milieu seulement.
- **Juges** (`tests/test_cabane_pour_vrai_js.py`) : `test_on_monte_de_n_importe_quel_cote_meme_pres_des_chevaux`
  (rougit à portée nulle) et `test_la_cabane_fermee_pas_de_caleche_et_le_cocher_dit_quand_il_attelle` (la nuit,
  l'hiver, et « pas sous nos yeux » — rougit sans la garde de la vue).
