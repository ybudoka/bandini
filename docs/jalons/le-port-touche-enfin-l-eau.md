# Le port touche enfin l'eau

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui : « c'est le quai !! je ne savais même pas que c'était
un quai… **il y a une route entre le quai et l'eau** !! j'aimerais que tu refactore toute
cette région pour que ça soit logique ».

- ⚠️ **Mesuré, et c'est pire que ça — trois défauts empilés.** (1) **Le quai ne touche pas
  l'eau** : 1 818 tuiles de planches, **16 au bord de l'eau — 0,9 %**. Le chiffre était déjà
  écrit dans ce plan (« le glyphe `Q` n'est pas un ponton, c'est le pavage du district des
  Quais ») et personne n'en avait tiré la conséquence : ce n'est pas le semis des poteaux
  d'amarrage qui est faux, c'est la GÉOGRAPHIE. (2) **Ce qu'il y a entre les deux** : la
  coupe du port, du nord au sud, donne `#+.` boulevard, `QQQQQQQQQQ` dix tuiles de quai,
  `.#+.` un **boulevard à quatre voies**, `s` une **plage de sable** (294 tuiles), puis la
  baie. Un débardeur qui décharge un cargo traverse une autoroute et une plage. La cause est
  dans la trame : la rangée de quai et la rangée d'eau sont **deux blocs séparés**, et la
  trame met une rue entre deux blocs. (3) **Le bassin du Faubourg n'est relié à rien** : 250
  tuiles d'eau (120,89 → 146,103) que le boulevard de la rangée 6 coupe de la baie — un
  étang au milieu du port, sur les neuf plans d'eau de la ville.
- ⚠️ Et il vient de devenir dangereux : la 3<sup>e</sup> vague du bord de l'eau y amarre des
  chaloupes, et **une coque qui y naît ne peut pas en sortir**. Ce qui arrive, dans cette
  passe : **Les Quais**, le port que Martin a montré. La rangée d'eau est **avalée** par la
  rangée de quai (`^`, le mécanisme des superblocs — c'est lui qui efface une rue, et il est
  déjà la règle partout ailleurs), un glyphe de plan `j` dit « quai SUR l'eau » (le `q` du
  Faubourg, lui, n'a pas de baie dessous et reste du plancher plein), et `_quai` dessine le
  tablier au nord, la baie au sud, la lèvre entre les deux. Puis un port qui a l'air d'un
  port : des **appontements** qui avancent dans la baie, des **bornes d'amarrage** le long
  de la lèvre, des caisses et des barils en arrière, des pneus en défense au bord.
- ⚠️ **Le bassin du Faubourg n'est PAS dans cette passe** — il demande une darse et un pont
  sur le boulevard, c'est-à-dire un jalon à lui. Il est mesuré et nommé ici pour ne pas être
  reperdu. ✅ **Livré** (16 sept. 2026). **La rangée d'eau est avalée par la rangée de quai**
  (`^`) : la trame n'a plus de raison d'y mettre une rue, c'est le mécanisme des superblocs
  qui fait déjà les gros îlots partout ailleurs. Un glyphe de plan `j` dit « quai SUR
  l'eau » — le `q` du Faubourg n'a pas de baie dessous et reste du plancher plein.
- ⚠️ **`j` entre dans `EAUX`**, et ce n'est pas un abus de langage : les deux tiers de sa
  hauteur sont la baie, et son tablier n'est pas une rue — un quai ne se traverse pas en
  char, on y descend du boulevard de service qui le borde au nord. Conséquence heureuse :
  **les rues verticales qui coupaient le quai deviennent des DARSES**, de l'eau entre deux
  appontements, ce qu'on veut justement y voir. **Après** : `#+.` boulevard de service,
  `QQQQQQQQQQ` le tablier, puis l'eau — **270 tuiles de quai au bord de l'eau (14 %) contre
  16 (0,9 %)**, plus une tuile de sable contre les planches, et **223 objets** sur le port
  (58 bornes d'amarrage, 33 barils, 98 caisses, 16 pneus en défense) contre 120 caisses et
  rien d'autre.
- ⚠️ **La lèvre et l'arrière ne portent pas la même chose** : au bord ce qui sert au bateau,
  en arrière ce qui attend d'être chargé — semé au hasard sur toute la surface, on obtient
  des bornes d'amarrage à six tuiles de l'eau.
- ⚠️ **Un ÉCART, pas « une tuile sur six »** : la lèvre n'est pas une ligne droite (elle
  contourne les appontements), et compter le long d'une liste collait deux bornes dès
  qu'elle tournait le coin.
- ⚠️ **Le quai se meuble AVANT la grève**, et `greve()` ne comptait que ses propres poses :
  deux bornes se sont retrouvées collées sans qu'aucun des deux semis en soit responsable
  (`MEUBLES_DU_BORD` amorce maintenant la règle d'écart).
- ⚠️ **Quatre juges d'à côté sont tombés, et chacun cachait une vraie fragilité** — aucun ne
  parle de port. (1) *La pièce a les mesures de son bâtiment* exigeait la boîte entière,
  alors que `mesures_de_la_part` rogne la profondeur d'un bâtiment en L : le juge était en
  contradiction avec le générateur et ne passait que tant qu'aucune vitrine ne possédait une
  part trouée. (2) *Une case de stationnement se gare* comptait **une chaloupe amarrée**
  comme une auto garée hors case — une coque naît `stationne`, dans la baie, ce qui est sa
  place. (3) *Une balle mord la tôle* n'en tirait **qu'une**, et une arme DISPERSE : le juge
  pariait sur l'état du dé. (4) *Celui qui tient son poste cède* courait 240 images vers
  l'est et **contournait** le donneur au lieu de le pousser — 228 px plus loin, personne de
  bousculé.
- ⚠️ **Et un vrai défaut du générateur** : `fermetures` gardait un tronçon dont la boucle
  avait épuisé `long_max` au lieu d'atteindre le croisement suivant — une rue barrée qui
  finit au milieu de nulle part n'a pas de transversale à son bout, donc **pas de détour à
  montrer**. Son propre commentaire disait déjà la règle. 9 juges neufs (`test_port.py`) ;
  1790 tests.
- ⚠️ **Reste ouvert, mesuré et nommé** : le **bassin du Faubourg**, 342 tuiles d'eau (118,89
  → 147,103) qu'un boulevard coupe de la baie, et le quai du Faubourg qui ne le touche pas
  non plus. Il demande une **darse et un pont** sur le boulevard de la rangée 6 —
  c'est-à-dire un jalon à lui, pas une ligne de celui-ci.
