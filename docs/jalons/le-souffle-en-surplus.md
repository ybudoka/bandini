# Le souffle en surplus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le souffle en surplus (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « les choses qui donnent du souffle devraient donner un **bonus** de
souffle, parce que le souffle monte seul actuellement. Ce serait une petite ligne de couleur
différente qui se superposerait sur la ligne jaune du souffle. »

⚠️ **Et c'était mesurable.** Le sprint coûte 0,4 par image ; dès qu'on arrête de courir, le
souffle remonte de 0,4 × 0,6 = **0,24 par image** — une barre vide se remplit toute seule en
**sept secondes**. Or `nourrir()` faisait `min(100, endurance + souffle)`. Une poutine à 18 $
rendait donc 70 points… qu'on aurait eus gratuitement en s'arrêtant quatre secondes.

⚠️ Pire : le dépôt s'était déjà donné cette raison-là, et elle n'avait jamais tenu. Le commit
`1a03d16` dit « manger reprend le souffle », et `economie.py` expliquait : « sans ça, le seul
moyen de reprendre son souffle était d'arrêter de courir ». L'intention était juste ; la
régénération automatique la vidait de son sens le jour même.

**Le surplus est ce que la régénération ne peut pas donner.** Manger ne remplit plus la barre :
il ajoute par-dessus, au-delà des 100 (plafond **60**). Et cette part-là :

- **se dépense en premier** quand on sprinte — c'est la seule qui vaille ce qu'on l'a payée ;
- **ne revient jamais toute seule**, et c'est exactement ce qui redonne un sens au kiosque ;
- **se perd** en dormant, à l'hôpital et en prison, comme le reste de ce qui est passager.

**À l'écran** : une ligne cyan d'un pixel, **posée sur** la barre jaune plutôt qu'à côté — on
lit d'un coup d'œil « j'ai du souffle, et j'ai de l'avance en plus ».

- ⚠️ **Cette barre porte déjà deux autres messages**, et c'était le vrai risque. Sous café elle
  passe au **vert** et clignote la dernière seconde ; **au volant**, ce n'est plus le souffle
  du tout mais la carrosserie du char. Le surplus se pose donc **sur** la barre sans la
  remplacer, garde sa couleur que la base soit jaune ou verte, et **disparaît au volant** —
  sinon il se superposerait aux points de vie d'une auto, ce qui ne veut rien dire.
- ⚠️ **Le plafond est un réglage de poursuite, pas de confort.** Le joueur sprinte à 2,1, le
  policier court à 1,9 : chaque point de surplus est de l'avance qu'on ne peut pas lui
  reprendre. À 0,4 par image, 60 points valent **2,5 secondes** de sprint de plus — et **5**
  sous café, puisque le café divise la dépense par deux. Le budget (`surplus_secondes_max`)
  est déclaré à côté, et un juge refait le calcul dès qu'un des trois nombres bouge.
- **Juges (2 neufs)** : côté Python, le plein de surplus reste sous le budget de secondes,
  café compris, et une poutine en donne un vrai morceau ; côté banc, les quatre promesses d'un
  coup — manger à barre pleine monte le surplus et pas la base, jamais au-delà du plafond ; à
  l'arrêt il ne remonte pas d'un point quand la base, elle, remonte ; au sprint c'est lui qui
  part en premier (la base reste pleine) ; et une nuit l'efface.

## Notes

demande de Martin (« les choses qui donnent du souffle devraient donner un **bonus**, parce
que le souffle monte seul ») : il remontait de 0,24 par image — une barre vide pleine en **7
s** — et `nourrir` plafonnait à 100, donc une poutine à 18 $ rendait 70 points qu'on avait
gratuitement en s'arrêtant quatre secondes. Manger ajoute maintenant **par-dessus** les 100
(plafond 60) : le surplus **part en premier** au sprint, ne remonte **jamais** tout seul, et
se perd en dormant, à l'hôpital et en prison. À l'écran, une ligne cyan d'un pixel **posée
sur** la barre — elle garde sa couleur sous café (barre verte) et **disparaît au volant**,
où la barre montre la carrosserie. Son plafond est un réglage de **poursuite** : 60 points =
2,5 s de sprint de plus, 5 s sous café, et un juge refait le calcul. 2 juges neufs
