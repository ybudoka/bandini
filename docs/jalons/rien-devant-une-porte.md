# Rien devant une porte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui (une machine distributrice plantée devant la porte de la
PIZZERIA NAPOLI) : « jamais rien devant la porte d'une maison, d'un commerce ou autre ».

- ⚠️ **Mesuré** sur sept graines : les vraies portes (`D`, `d`, `G`) avaient toujours leurs
  deux tuiles de devant libres ; **tout** ce qui bouchait était devant une porte **peinte**
  (`P`, celle qu'une devanture ou un logement se dessine quand son bâtiment n'en a pas tiré)
  — 3 à 7 objets par ville : des distributrices surtout (`distributrices()` prenait le `P`
  pour une vitrine), un BBQ, un arbre, un paquet. **Livré** : la porte peinte est une porte
  — `degager_le_devant` (sorti de `poser_porte`) réserve et vide ses deux tuiles comme pour
  une vraie, `est_une_porte` la reconnaît, et la machine ne se pose plus ni sous elle ni à
  côté. Remesuré : **zéro** objet devant une porte sur les sept graines, et autant de
  machines qu'avant (30 à 32). Juge `test_rien_ne_se_tient_devant_une_porte_meme_peinte`
  (quatre graines, décor, kiosques, réclames, scènes et paquets) — vu **rouge** sans le
  dégagement (BBQ, arbre, paquet sur trois graines).
- ⚠️ **La piste d'une rampe passe quand même** devant une porte peinte (`devants_peints`,
  `_roulable(piste=True)`) : elle se garde vide, et sans ça la rampe du stationnement voisin
  de la NAPOLI tombait — cinq rampes, `test_il_y_a_des_rampes` rouge, le panneau du Grand
  Saut déplacé et un baigneur sans serviette : les kiosques, les réclames et la barrière du
  cargo suivaient la rampe. Le pied et la lèvre, eux, jamais (le juge les compte). Ce qui
  bouge dans la ville du jeu : le décor dégagé et **les 20 paquets** (leur liste de places a
  perdu des tuiles).
- ⚠️ Pas touché : **à côté** d'une vraie porte, neuf guichets restent encastrés sous la
  vitrine voisine — ils ne bouchent rien, mais c'est à Martin de dire si « devant » veut
  aussi dire « collé ».
