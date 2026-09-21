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
