# Les machines distributrices

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « ajoute aussi un concept de machine distributrice partout dans la
ville ».

- ⚠️ **Mesuré avant : zéro.** **Livré** : **trois sortes** (`magasins.DISTRIBUTRICES`) — la
  machine à **liqueur** (liqueur, jus), à **grignotines** (chips, chocolat), à **café**
  (café, soupe en gobelet) —, chacune avec sa couleur qu'on reconnaît de l'autre bord de la
  rue. **Dans la rue**, 32 à 35 machines selon la graine (`carte.distributrices`) : adossées
  à une devanture, jamais sous une porte, une rangée libre devant, la sorte tirée dans la
  famille du commerce (du café devant la soudure, de la liqueur devant la taverne), et
  **neuf au plus par district** — sans ce plafond, La Shop et les Quais en prenaient 35 sur
  48 et les Érables une seule.
- ⚠️ **Mesuré** : sous les 313 façades de commerce, 265 donnent sur un parvis de dalle et 35
  sur l'abord ; la règle du guichet (l'abord seulement) ne laissait que **cinq** machines
  dans toute la ville.
- ⚠️ Elles tirent dans **leur propre dé, après les paquets** : un juge génère la ville avec
  et sans, et tout le reste est identique. **Dans les salles d'attente** : le terminus (la
  première pièce du jeu), le poste de police (sa machine à café) et l'urgence, en meuble `b`
  portant un point `distributrice`.
- ⚠️ **Jamais collée à une porte** : à moins de 22 px de la tuile où l'on pousse une porte,
  une machine lui volait ACTION — l'invite disait MACHINE À CAFÉ devant l'entrée d'un
  commerce (un juge des intérieurs l'a vu le jour même). La ville ne les colle plus, et
  `distributriceSousLaMain` cède la main à la porte. **Au prix du comptoir** (les articles
  pointent dans `TARIFS`, `itemBouchee` sert les deux), et la **spirale** garde l'achat une
  fois sur sept : on a payé, rien ne tombe, l'invite devient BRASSER LA MACHINE, et une
  secousse sur deux le fait tomber ; la nuit vide ce qui est resté pris. **Défoncée** — une
  berline suffit, trois balles aussi — elle crache sa monnaie en trois tas et deux canettes
  qui se boivent en passant : une étoile, et seulement si un témoin va le raconter ; au
  matin elle est debout.
- ⚠️ Un juge tient qu'une nuit à défoncer **toutes** les machines (40 × 22 $) rapporte moins
  qu'une journée honnête (1 230 $). Trois bruitages synthétisés (la canette qui tombe, la
  machine brassée, la monnaie) : le seau des échantillons est plein
