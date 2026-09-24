# De vraies plages, pas des bouts de sable

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « moins de plage autour, et des accessoires de plage et des gens s'il y a
beaucoup de place, pas juste des petits morceaux de plage ».

- ⚠️ **Mesuré** (graine livrée) : **1 754 tuiles de sable en 65 morceaux**, dont **41 de
  moins de dix tuiles** — `_eau()` bordait CHAQUE côté de chaque bassin d'une bande de 0 à 4
  tuiles qui avançait et reculait, jusque dans le chenal de La Pointe, des deux rives ; et
  les **104 meubles de plage** tombaient tous sur ces bandes étroites. ✅ **Livré** (16 sept.
  2026). **`PLAGES` : peu, mais larges.** Au plus une plage par côté de bassin, sur le plus
  long bout de rivage d'un seul tenant : **26 à 44 tuiles de long, 5 à 8 de profondeur**,
  les deux bouts qui s'amincissent. **Jamais dans un chenal** : un bassin donne un tiers de
  sa largeur s'il y a une rive en face, la moitié sinon, et sous cinq tuiles ce côté n'a pas
  de plage ; sous **120 tuiles**, pas de plage du tout. Le reste de la côte touche l'eau
  sans sable. Sur la graine livrée : **cinq plages** de 164 à 224 tuiles — le nord de la
  baie, sa rive ouest, la rive ouest de La Pointe et deux au sud de La Pointe. Elles
  **déclarent leur rectangle** (`plages`, dans le paquet).
- ⚠️ **Leur dé à elles** (`des_plage`), et `_eau` **brûle** ce que l'ancienne rive tirait
  dans le dé commun (un coup par colonne et par rangée du bassin) : aucun îlot posé après la
  baie ne change de gabarit. **Les accessoires** : seulement sur une plage déclarée, mais
  **sur toute sa profondeur** (`GREVE["bord"]` passe de 3 à 8 : à trois, le fond d'une plage
  large restait nu), une vingtaine par plage ; trois fiches neuves — la **chaise longue**,
  le **kayak** et la **chaise du sauveteur** (une par plage, au milieu, posée avant le
  semis ; solide, elle cède sous un char comme un banc). Le château passe **en tête** du
  tirage : tiré en dernier, il n'en restait que deux pour cinq plages.
- ⚠️ **Effet de bord, trouvé en mesurant** : sans sable, le trottoir du chenal de La Pointe
  touchait l'eau et prenait un **poteau d'amarrage tous les trois pas** — la palissade que
  le quai avait déjà appris à ne pas planter ; poteaux espacés de 11 tuiles, bouées de 6.
  **Les gens** : `baigneur` et `baigneuse` (le corps commun, et la palette qui les met en
  maillot), **deux plafonds** — cinq enfants, sept grands — pour que les premiers nés ne
  prennent pas toutes les places. Ils ne naissent **que sur une plage déclarée** (la
  première règle, « du sable avec l'eau à trois tuiles », en faisait naître au bord des
  étangs de parc). Les grands se font **bronzer** sur une serviette ou une chaise longue
  **libre**, tout le monde se **promène** sur le sable sans traverser d'anse, et l'on trouve
  l'eau depuis le fond d'une plage (`bordDeLEau` cherche à neuf tuiles au lieu de quatre).
- ⚠️ **Un juge rendu déterministe** : « un enfant ne dépasse jamais la première tuile
  d'eau » attendait qu'un baigneur TIRE la baignade — or le jeu se tire à l'empreinte et
  dure une à trois minutes, donc un tirage en trente secondes ; sur la ville d'après la
  foire, personne ne l'a tirée et le juge est tombé sur « il ne mesure rien ». Il envoie
  désormais chacun à l'eau par `bordDeLEau` (le geste, pas la chance) ; vérifié en retirant
  l'arrêt au premier pied mouillé : **962 images au large**. **Juges** (`test_greve`,
  `test_plage_js`) : chaque plage a la place, **tout sable qui touche le large est une plage
  déclarée**, les accessoires de plage n'existent que dedans, un sauveteur par plage, pas de
  plage dans un chenal, le dé de la ville intact ; les baigneurs ne naissent que sur une
  plage (vérifié en retirant la règle : **12 baigneurs au bord d'un étang**), des grands
  aussi, et un grand bronze sur une serviette que personne d'autre ne prend.
