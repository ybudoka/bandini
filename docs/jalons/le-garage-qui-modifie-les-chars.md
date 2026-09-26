# Le garage qui modifie les chars

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ un char qu'on **garde** et qu'on améliore, au lieu de le voler et de l'oublier —
chez Ti-Guy, au Garage Rocco Bandini.

**Aujourd'hui** le garage répare, repeint et achète les chars volés (les garages où l'on entre, M9) ; la
planque garde **un** char (`partie.planque.vehicule`). Rien ne s'améliore.

- **Ce qui s'installe** (à trancher par Martin, la liste comme les prix) : le moteur (vitesse maximale), le
  blindage (points de vie, les balles mordent la tôle), les pneus d'hiver (l'adhérence dans la neige de
  M12), la nitro (une poussée par ACTION, qui se recharge), et **le klaxon qui joue « Gens du pays »**.
- **Où ça vit** : sur le char garé à la planque, sauvegardé avec lui — un char modifié qui part à la
  fourrière revient modifié, et se rachète plus cher.
- Ti-Guy le commente : une réplique par pièce posée, sa voix existe déjà.

⚠️ **Ce qui guette** : la vitesse maximale touche à la friction (`vehicules.friction_pour`, le camion de
paie de s03 bridé) — un moteur neuf doit **atteindre** sa vitesse, le juger au banc au bouton. Et un char
trop fort casse les poursuites : la police doit rester une menace à 5★.

**Juges** : chaque pièce change ce qu'elle promet (mesuré au banc) ; elle survit à une sauvegarde et à la
fourrière ; le klaxon joue le bon air.

## Notes

**Livré le 26 sept. 2026.** `app/garage.py` (le catalogue), `static/js/garage.js`, cinq lignes de plus au
menu de Ti-Guy (`Missions.menuGarage`), cinq voix de Ti-Guy (une série, `ti_guy-garage-*`) ; juges
`tests/test_garage_js.py` (dix mutations, toutes mordent).

- **Les pièces et leurs prix** (la liste de la fiche, les prix choisis à défaut d'un mot de Martin) :
  le moteur gonflé 600 $ (pointe et accélération × 1,2), le blindage 800 $ (vie × 1,6), les pneus
  d'hiver 250 $ (ils rendent 60 % de ce que la neige et le verglas prennent à l'adhérence et au frein),
  la nitro 900 $ (× 1,35 pendant 1,5 s, 10 s de recharge), le klaxon 150 $. Une fois chacune ; pas sur
  un vélo.
- **Un char modifié a SA fiche** (`v.def`, une copie du catalogue) : ⚠️ le moteur gonfle la pointe ET
  l'accélération du même facteur — la pointe est un équilibre entre l'accélération et la friction ; mesuré
  au bouton sur un boulevard, 3,995 → 4,793. La nitro fait pareil le temps de sa bonbonne.
- **La nitro prend le bouton libre du volant** (SAISIR : `U` au clavier, l'épaule droite à la manette) ;
  l'étiquette tactile dit NITRO sur un char qui en a une.
- **Elles voyagent avec le char** (`v.mods`) : devant la planque et dans les planques des blocs (la
  sauvegarde), à la fourrière (un char modifié revient modifié) — et il se rachète plus cher (la moitié du
  prix de ses pièces en plus).
- **Ti-Guy commente** chaque pièce posée (sa voix, et la ligne à l'écran). ⚠️ Les cinq voix sont
  générées, **pas écoutées**.
- ⚠️ **Le klaxon ne joue PAS encore « Gens du pays »** : la mélodie n'a pas été transcrite note pour note,
  et une fausse aurait été pire qu'une fanfare. `garage.KLAXON_AIR` joue une fanfare de klaxon qui monte ;
  c'est une donnée (Hz, secondes) — la vraie phrase la remplace sans une ligne de code.
- ⚠️ **La police** : une auto au moteur gonflé (4,8) file aussi vite qu'une sport du catalogue, plus vite
  qu'une auto-patrouille (4,4). Rien n'a été retouché de ce côté : à 5★, les barrages et l'hélico restent
  la menace. À surveiller en jouant.
