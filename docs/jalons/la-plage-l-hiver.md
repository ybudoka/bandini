# La plage l'hiver

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026), capture d'une plage un soir de janvier : « la plage devrait aussi être en
hiver, et les exhibitionnistes prennent une pause ». Mesuré : le sable de la grève (`s`) garde sa
couleur d'été toute l'année pendant que le gazon et les trottoirs blanchissent ; les serviettes, les
parasols, les chaises longues, les châteaux et les kayaks restent semés ; les baigneurs n'ont que
leurs heures (`PLAGE.heures`), pas de saison ; et l'homme au manteau ouvre le sien en plein janvier.

Correctif, sans un dé et sans rien déplacer :

- **Le sable sous la neige.** La tuile `s` passe par `Saisons.enneiger`, comme le trottoir : blanche
  tant que la neige tient, avec le sable qui perce ; le dégel la rend.
- **La plage rangée.** Au-dessus d'un seuil de froid (`PLAGE.froid_max`), les meubles mous de la grève
  (parasol, serviette, chaise longue, château de sable, kayak) ne se peignent plus. Aucun n'est solide :
  les ranger ne laisse pas de mur invisible. La chaise du sauveteur et les tables restent.
- **Pas de baignade hors saison.** Le même seuil garde les baigneurs : personne n'y naît, et qui y est
  encore plie bagage hors champ, comme à la fermeture du soir.
- **L'exhibitionniste prend congé.** Une sorte peut porter `froid_max` comme elle porte `heures` :
  au-dessus, elle ne naît pas et rentre hors champ. L'homme au manteau a le sien.

Juges : le sable de janvier est blanchi, celui de juillet ne l'est pas ; en janvier un parasol ne se
peint pas et aucun baigneur ne naît ; l'exhibitionniste ne naît pas en janvier et naît en juillet.
