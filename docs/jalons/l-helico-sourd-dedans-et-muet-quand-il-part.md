# L'hélico : sourd dedans, et muet quand il est parti

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (21 sept. 2026) : « je suis resté avec un son d'hélicoptère de police, il faudrait
qu'on l'entende très sourd quand on est dans un bâtiment et être certain qu'il arrête quand
l'hélicoptère s'en va ». Ce que le code montre : la boucle `helico` ne se règle et ne
s'éteint que dans `Police.majHelico`, qui ne tourne que dehors, sur un hélico trouvé dans
`B.entites`. Trois chemins la laissent tourner **pour toujours**, au dernier volume :
entrer dans une pièce (`Police.maj` sort tôt, et l'hélico est resté dans les entités du
dehors), se réveiller à l'hôpital après une mort à cinq étoiles (même chose), et recommencer
ou recharger une partie (`commencer()` vide les entités, l'hélico disparaît sans éteindre
son bruit). Le plan : un **mélangeur** comme celui des sirènes (`majSirenes`), appelé à
chaque image, qui retient ce qu'il a demandé et règle la boucle d'après l'hélico qui existe
vraiment (dehors, ou dans `B.exterieur.entites` quand on est dedans) — pas d'hélico, pas de
bruit ; dedans, un volume bas **et** un passe-bas (le rotor à travers les murs) ; et
l'hélico continue de vivre pendant qu'on est dedans, pour qu'il puisse repartir quand les
étoiles tombent, et que le bruit s'éteigne en fondu à son départ.

## Notes

_Livré le 21 sept. 2026._

- ⚠️ **Reproduit d'abord, au banc, son branché et fichiers chargés** : sous l'hélico, on
  recommence la partie — `Son.boucleActive('helico')` reste vrai, pour un hélico qui n'existe
  plus. Même chose en entrant dans une pièce : la boucle y gardait son volume de plein air.
- **Un mélangeur**, `Police.majBruitHelico()`, à chaque image de `Police.maj`, **dans ses
  trois chemins** (la rue, la pièce, l'île) : il cherche l'hélico là où il vole vraiment
  (`helicoDuCiel` — dans `B.exterieur.entites` quand on est dedans) et règle la boucle
  d'après lui. Pas d'hélico, pas de bruit, quelle que soit la façon dont il a disparu.
  ⚠️ Contrairement aux sirènes, il **lit** `Son.boucleActive` : c'est ce qui rend l'arrêt
  certain, et une boucle qui ne peut pas jouer se redemande pour presque rien.
- **Dedans, l'hélico vit encore** : il tourne au-dessus de la porte par où l'on est entré
  (`ceQuIlSurvole`), sans rien voir à travers le toit ; les étoiles tombées, il repart, et
  on l'entend s'éloigner à travers le toit, puis plus rien — sans avoir à ressortir. Reparti,
  il se retire de la ville mise de côté (`oublierHelico` : `Entites.retirer` ne regarde que
  la pièce).
- **Sourd** : `Son.etouffer(slug, part)` glisse un passe-bas entre la source et le gain à
  la première demande (0 = 20 kHz, 1 = 250 Hz, en octaves), et le volume est multiplié par
  0,45. Mesuré au banc devant la même porte : 0,63 dehors, 0,28 dedans ; coupure 20 000 Hz
  dehors, 250 Hz dedans. `Son.coupureBoucle` est son pendant en lecture, comme `volumeBoucle`.
- ⚠️ **Au noir, pas après le fondu** : le monde est figé pendant un fondu de porte, alors
  `chargerPiece` et `sortir` appellent le mélangeur eux-mêmes — l'hélico devient sourd avec
  la porte qui se ferme, pas un tiers de seconde plus tard dans une pièce déjà éclairée.
- **Il s'éteint en s'éloignant** : reparti, son volume suit `1 − d / 700` jusqu'à zéro, là
  où il disparaît (avant : un plancher à 0,05 puis une coupure nette). Il entre et sort de
  l'oreille en fondu (0,6 s).
- **L'écran titre le fait taire** (`Police.taireHelico`) : la ville reste figée derrière le
  titre, et plus rien n'y réglait son bruit.
- **Juges (2 neufs)**, `tests/test_police_js.py` : dans une pièce, l'hélico s'entend plus bas
  et sourd, dès le noir, sans débrancher la boucle de la sortie, et se tait quand il repart ;
  une partie reprise et l'écran titre l'éteignent. **Huit mutations**, chacune fait rougir
  un juge ; verts sous douze graines.
- ⚠️ **Pas corrigé, vu en passant** : la **sirène** et le **moteur** continuent eux aussi
  sur l'écran titre (sondé au banc). Même bogue, autre module (`Vehicules`) — et la sirène
  retient ce qu'elle a demandé, donc la couper de l'extérieur la rendrait muette pour de bon :
  il faut une porte de sortie dans `Vehicules`.
- ⚠️ **Ce qui n'a pas été jugé** : l'oreille. 250 Hz est un choix, pas une mesure ; si le
  rotor sonne trop étouffé ou pas assez, c'est `COUPURE_SOURDE` dans `son.js`.
