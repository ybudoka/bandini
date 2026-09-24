# Les portes s'ouvrent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les portes s'ouvrent, et les gens les passent (**ajout**, taille 2) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « les piétons devraient aussi sortir et entrer dans les commerces.
Profites-en pour aussi faire ouvrir concrètement les portes. »

Les deux demandes n'en font qu'une, et le code dit pourquoi.

⚠️ **Un piéton sur trois SORT déjà d'une porte — et on ne le voit jamais.**
`placeDeNaissance()` tire une porte une fois sur trois, puis refuse la place si elle est
**visible à l'écran** (`if (visibleAEcran(x, y, 24)) continue`). Les gens apparaissent donc
sur un pas de porte **là où l'on ne regarde pas**. Ce n'est pas une sortie, c'est une
naissance déguisée en sortie — et elle ne rapporte rien, puisque son seul intérêt serait
d'être vue.

⚠️ **Et personne n'entre nulle part.** Les piétons disparaissent par oubli, quand ils sortent
de la bulle. La ville a des dedans qui n'avalent jamais personne.

⚠️ **Enfin, une porte ne s'ouvre pas.** Les peintres `D` et `d` dessinent un battant fixe, et
il n'existe nulle part d'état d'ouverture.

**Une porte qui s'ouvre est ce qui rend une sortie crédible**, et une sortie visible est ce
qui justifie qu'une porte s'ouvre. D'où une seule fiche.

- ⚠️ **Une porte animée ne peut pas être une tuile.** Le sol est **cuit dans le morceau** de
  256 px : repeindre un morceau à chaque image pour un battant tuerait le cache qui tient le
  rythme sur téléphone. La porte qui s'ouvre est donc un petit dessin posé **par-dessus**,
  dans la passe des entités, et seulement pour les portes à l'écran — il y en a une poignée.
  C'est la même leçon que les feux pour piétons : le poteau est une entité, la traverse est
  une tuile.
- **Sortir, pour de vrai.** Le piéton naît **dans** la porte (invisible), la porte s'ouvre, il
  avance d'une tuile, elle se referme. La règle « hors écran seulement » saute : c'est
  précisément parce qu'on ne le voyait pas que ça ne servait à rien.
- **Entrer.** Un piéton qui flâne se choisit une porte comme but, marche jusqu'à elle, attend
  qu'elle s'ouvre, disparaît dedans. ⚠️ Ça doit **remplacer une part de l'oubli par
  distance** : sinon la ville se vide toujours de la même façon et on a juste ajouté une
  animation.
- ⚠️ **Toutes les portes n'ont pas le même sens.** `portesFermees` mélange les `d` — portes
  condamnées, les logements — et les `D`, les vraies portes qui mènent à un intérieur. Il faut
  trancher : un logement, oui ; un commerce, **aux heures d'ouverture** (`ouvert()` existe
  déjà) ; le poste de police et l'hôpital, seulement pour qui y travaille ; **la planque de
  Rocco, jamais** — c'est chez le joueur.
- ⚠️ **Et le joueur ne doit pas pouvoir suivre dans le vide.** Une porte condamnée est solide :
  elle ne mène nulle part. Si quelqu'un y entre sous les yeux du joueur, il essaiera d'entrer
  et trouvera un mur — une promesse qu'on ne tient pas. Soit le piéton n'entre que par des
  portes que le joueur peut franchir, soit la porte condamnée **dit** qu'elle ne s'ouvre que
  pour ceux qui habitent là (une poignée, pas d'enseigne, aucune lumière).
- **Le rythme s'en sert.** La nuit vide maintenant la ville pour de vrai ; les portes doivent
  battre au **matin** (on sort) et au **soir** (on rentre), et presque plus la nuit. C'est
  `Monde.rythme(zone)`, qui donne déjà les trois.
- **Juges** : une porte ne s'ouvre jamais sur rien — un piéton qui entre disparaît **après**
  l'ouverture, jamais avant ; la planque du joueur n'avale personne ; un commerce fermé ne
  laisse entrer personne ; le cache de morceaux **ne bouge pas** quand une porte s'ouvre
  (`stats.morceaux` le mesure) ; et le va-et-vient ne fait pas déborder le plafond de piétons.

**Livré le 13 sept. 2026 :**

- **Le battant est une entité de dessin, pas une tuile** : `carte.battants`, une poignée
  d'états, dessinés **par-dessus** le sol dans `Jeu.rendre()`. ⚠️ Le juge mesure
  `stats.morceaux` avant et après une ouverture : le cache ne bouge pas d'un morceau.
- ⚠️ **Redemander une porte déjà en train de s'ouvrir ne la remet pas à zéro.** Un piéton qui
  attend devant appelle `ouvrirPorte` à **chaque image** : le battant restait figé au premier
  pixel et ne s'ouvrait jamais — donc personne n'entrait. Une porte qui se referme, elle, se
  retient ouverte. C'est le genre de bogue qu'on ne voit qu'en regardant la courbe.
- **Sortir** : on naît **dans** la porte, invisible tant qu'elle s'ouvre, puis on avance d'une
  tuile et elle se referme. La règle « hors écran seulement » saute — c'était précisément
  parce qu'on ne le voyait pas que ça ne servait à rien.
- **Entrer** : un flâneur se choisit la porte utile la plus proche, y marche, **attend qu'elle
  soit grande ouverte**, et disparaît — jamais devant un battant fermé. S'il est bloqué par la
  foule une seconde, il renonce plutôt que de piétiner.
- **Quelles portes** : un `d` est un **logement** (toujours) ; un `D` mène à un intérieur — ⚠️
  jamais la **planque** (c'est chez le joueur), ni le **poste**, ni l'**hôpital**.
- ⚠️ **Et le joueur n'est pas trompé.** La fiche laissait le choix ; c'est le **dessin** qui
  tranche, et il était déjà bon : un `D` a une poignée de laiton, un `d` est un battant sombre
  sans poignée, sans enseigne et sans lumière. On apprend à ne pas pousser celle-là.
- ⚠️ **Les intérieurs n'ont PAS d'heures déclarées** — seuls les kiosques de rue
  (`ambulants`) en ont. La **nuit** tient donc lieu de fermeture, avec la seule exception qui
  compte : le **bar**, qui vit justement la nuit. Le jour où `carte.INTERIEURS` portera des
  heures, ces deux lignes deviennent `Missions.ouvert(...)`.
- **Juge (1 neuf)** : le battant monte, tient et redescend tout seul ; le cache de morceaux ne
  bouge pas ; la planque, le poste et l'hôpital n'avalent personne, un logement oui, un
  commerce le jour mais pas la nuit, le bar la nuit ; on naît caché et on sort **visible, en
  plein écran** ; et celui qui entre disparaît avec la porte **à plus de 90 % ouverte**.

**Corrigé le 14 sept. 2026** (retour de Martin : « les portes doivent ouvrir quand j'entre
aussi »). Elles s'ouvraient pour les piétons et **pas pour le joueur** — il traversait un
battant fermé, et c'était d'autant plus voyant que les passants, eux, attendaient poliment.

- ⚠️ **Le piège était dans l'ordre.** Le jeu est **figé** pendant un fondu de porte (`maj()`
  ne fait avancer que la transition) : un battant ouvert juste avant y resterait au premier
  pixel, et la porte serait fermée à l'écran pendant tout le fondu. `Monde.majBattants()`
  tourne donc **aussi** dans la branche de transition — c'est la seule chose qui bouge quand
  tout le reste est arrêté, et elle ne touche qu'à son propre compteur.
- **La porte s'ouvre AVANT de noircir**, pas au noir : la première moitié du fondu se joue
  sur la rue, et c'est là — et seulement là — qu'on peut voir le battant bouger.
- **Au retour, c'est celle de la RUE qui s'ouvre**, et seulement une fois `Monde.restaurer()`
  fait : avant, `Monde.carte` est encore la pièce, et ses battants ne sont pas ceux de la
  ville.
- **Juge (1 neuf)** : il mesure l'ouverture **image par image pendant le fondu**, et n'accepte
  que ce qui se passe tant que la rue est encore visible ; puis la porte de la rue au retour,
  et le fait qu'elle se referme derrière.

## Notes

demande de Martin (« les piétons devraient aussi sortir et entrer dans les commerces ;
profites-en pour faire ouvrir concrètement les portes ») : ⚠️ un piéton sur trois sortait
**déjà** d'une porte — mais `placeDeNaissance()` refusait la place si elle était **visible à
l'écran**. Ce n'était pas une sortie, c'était une naissance déguisée en sortie, dont le seul
intérêt aurait été d'être vue. Maintenant : un **battant** qui s'ouvre, tient et se referme
— posé **par-dessus** le sol, jamais dans le morceau cuit —, on naît **dans** la porte et on
en sort à l'écran, et un flâneur se choisit une porte et **rentre**, ce qui remplace une
part de l'oubli par distance.

- ⚠️ Jamais la planque, ni le poste, ni l'hôpital ; un commerce pas la nuit — sauf le bar
