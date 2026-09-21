# Les policiers descendent d'une auto arrêtée

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

Retour de Martin (21 sept. 2026) : « quand on est à plusieurs étoiles, la police arrive en voiture
rapidement, les policiers en sortent trop vite et se font écraser par leur propre voiture. Idéalement,
quand les policiers en sortent, le véhicule ne devrait plus rouler, à moins qu'un seul policier en sorte. »

- ⚠️ **Deux défauts, pas un.** (1) À 60 px du joueur à pied, l'auto « freinait » et faisait naître ses deux
  agents *à la même image*, à ±14 px de son centre **dans l'axe du monde** (pas dans celui de la
  carrosserie), pendant qu'elle roulait encore à 2,5–3,7 px/image : `heurterPietons` les renversait en une
  image, et chaque corps lui retirait 15 % de vitesse (le cadavre faisait office de frein). (2) `frein` à
  l'arrêt, dans `majPhysique`, c'est la **marche arrière** : l'auto s'arrêtait, puis reculait à 1,45 px/image
  — le seuil qui renverse est à 1,2 — et repartait. Mesuré au banc avant de coder.
- **La règle de Martin, telle qu'elle est écrite.** `Police.stationner` : le **passager** saute seul quand
  l'auto est descendue au pas (`auto_passager_saute_sous`, 0,8 px/image, sous le seuil qui renverse) — le
  conducteur reste au volant et continue de freiner —, le **conducteur** descend auto **arrêtée**
  (`auto_arret_sous`, 0,15). Jamais deux dehors tant que ça roule. Équipage dehors, l'auto est **garée** :
  vitesse tenue à zéro, aucune marche arrière.
- ⚠️ **Deux agents par auto, un seul conduit** (2e consigne de Martin : « si deux policiers sortent, le
  véhicule reste immobile à moins qu'un policier reprenne le volant — deux policiers par véhicule, un prend
  le volant, un seul peut en ressortir »). `v.equipage` = combien en restent en vie (`auto_equipage`, deux),
  `v.equipe` = ceux qui sont **dehors** ; le reste est à bord (`Police.equipageDe(v)` → `{ dehors, abord }`,
  toujours `dehors + abord = équipage`). **L'auto ne roule que si `abord ≥ 1`.** Avant, elle « repartait
  pleine » dès que le joueur était à 150 px — sans conducteur, ses deux agents à pied — et la fois d'après
  en fabriquait deux de plus.
  - Les deux dehors et le joueur n'est plus sur eux (plus de 150 px, ou il roule) : l'auto reste **garée**,
    et les agents **regagnent l'auto à pied** (`rappeler` → l'état `regagne` → `regagner`). Le premier
    arrivé **monte** — l'entité quitte la ville, l'auto le compte à bord — et **reprend le volant** : elle
    repart. L'auto **attend** l'équipier qui arrive en courant (`auto_attend_px`, 40 px) ; l'autre, s'il est
    resté loin, reprend la chasse à pied : « un seul dehors ».
  - Le joueur revient sur eux : ceux qui rentraient reprennent la chasse. Personne n'est fabriqué à
    la descente suivante : un agent qui a monté redescend, il n'en naît pas un troisième.
  - **Un agent mort ne remonte pas** : l'équipage perd un homme (un seul reste : il conduit, et descend seul
    auto arrêtée). L'équipage entier mort, l'auto reste garée mais **ne compte plus** dans `autos` du palier
    (`abandonnee`) — sinon la police n'enverrait plus jamais de renfort. Un agent à plus de `auto_rappel_px`
    (480), ou qui n'a pas regagné l'auto en `auto_regagne_s` (15 s), n'est plus de son équipage.
  - Sans conducteur, l'auto ne « voit » plus (elle ne remet plus `vu` à zéro) : ses agents, dehors, voient
    pour eux.
- **Par les portières.** Chacun descend de son côté (passager à droite, conducteur à gauche), à
  `largeur/2 + 8` px de l'axe — la règle de `Vehicules.descendre` du joueur —, jamais dans l'axe où l'auto
  roule ; côté bouché, l'autre côté, puis derrière. Un claquement de portière (`Son.depuis`, muet hors champ).
- **Un vrai coup de frein** (`auto_frein`, ×2). Au frein normal l'auto mettait 47 px à s'arrêter depuis les
  60 px du déclenchement : elle finissait contre le joueur, et ne se sauvait de ses agents que grâce à leurs
  corps. Elle s'arrête maintenant à ~30 px.
- **Freiner sans reculer** (`freiner`) : le frein ne s'applique que tant que l'auto avance. Vaut aussi
  quand la recherche tombe à zéro (elle reculait sans fin devant les yeux du joueur).
- **Le filet** (`heurterPietons`) : une auto à conducteur `police` **pousse** ses agents hors de sa carrosserie
  au lieu de les renverser (elle repart avec l'équipage au flanc, une autre patrouille le frôle). La règle
  est au-dessus ; ceci n'est que le dessous.
- Sept juges de banc dans `test_police_js.py` (l'équipage : jamais deux dehors tant que ça roule,
  portières et non axe, auto garée sans bouger ni reculer, personne d'écrasé ; le filet ; la chasse finie
  sans marche arrière ; **deux dehors = immobile image par image jusqu'à ce qu'un agent reprenne le volant,
  dehors + à bord = deux à chaque image, jamais plus de deux agents par auto** ; un seul dehors = elle
  roule, deux = jamais ; l'équipage mort ne retient pas les renforts), deux de fiche dans
  `test_recherche.py`. **Chacun a été vu rouge** en retirant sa règle (neuf mutations) : le filet, le frein
  qui recule, « tous d'un coup », le passager qui saute à toute vitesse, le conducteur qui descend d'une auto
  qui roule, l'auto qui roule sans conducteur, personne qui reprend le volant, l'auto abandonnée qui retient
  un renfort.
- ⚠️ **Un rouge d'avant, pas de moi** : `test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`
  (`test_histoire_js.py`, « ils arrivent de hors de l'écran ») échoue aussi sur `2b2a001`, sans ce changement.
