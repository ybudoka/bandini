# Le quai se marche, et la ville est moins sale

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « il y a **trop de saleté partout** et **impossible d'aller sur une
partie du quai, il est clôturé, sans chemin à pied** ».

- ⚠️ **Mesuré, et les deux sont vrais — le second est P1 : une partie de la ville ne se
  visite pas.** **191 tuiles de quai sont inatteignables à pied**, en une quarantaine de
  poches. Et ce n'est PAS une clôture : c'est du décor solide. (1) **Deux semis posent des
  bornes d'amarrage sur la même lèvre** — `_meubler_le_quai` (écart 6) et `greve()`
  (`quai_poteau`, écart 3) — et la rangée du bord donne `QpQQAQQAQQQpQQQQQAQQpQQpQQAQQA` :
  une borne ou un pneu **tous les 3 pas sur soixante tuiles**. Vu d'en haut, c'est une
  palissade, et Martin l'a nommée comme telle. (2) **La cargaison couvre tout le tablier** :
  `PART_CARGAISON` sème une caisse par dix tuiles d'arrière, soit ~60 caisses SOLIDES sur
  dix rangées de profondeur — un plancher d'entrepôt, pas un quai. (3) **Les terrains vagues
  sont trop chargés** : un déchet par six tuiles, plus une mauvaise herbe par quatorze — 303
  objets de saleté dans la ville (126 caisses, 65 sacs, 44 barils, 34 pneus, 34 gravats). Ce
  qui arrive : **un quai a un APRON** — la bande du bord reste dégagée (des bornes espacées,
  rien d'autre), la cargaison s'empile **au fond**, contre la rue par où les camions
  arrivent, et le milieu se marche ; la grève **cesse d'amarrer sur les planches** (le quai
  le fait chez lui) ; les densités baissent. Et une garantie plutôt qu'un réglage :
  **`carte.DECOR_SOLIDE`** dit en Python ce qui arrête un piéton, un juge de banc vérifie
  qu'elle dit la même chose que les fiches de dessin, et un juge tient qu'**aucun lot ni
  aucun quai ne se referme sur lui-même**. ✅ **Livré** (16 sept. 2026).
- ⚠️ **La « clôture » n'était pas un décor semé : c'était une BARRIÈRE.** « Le quai du
  cargo » est une zone conditionnelle (fermée le jour, décor `chaine`) qui prenait la
  **région** de quai du contrebandier — et depuis que le port a avalé la baie, cette région
  faisait **61 × 26 tuiles, eau comprise**. C'est la chaîne de la capture : le long du
  trottoir et en travers de tout le quai ouest. Elle ferme maintenant le **mouillage** (15 ×
  6, `MOUILLAGE`), sur le tablier seulement, et jamais l'apron — on longe le quai par le
  bord de l'eau, cargo ou pas.
- ⚠️ **Et on a failli ne pas la trouver** : « aucune clôture ne touche le quai » était vrai
  (la barrière n'est pas un glyphe), « aucun décor régulier sur la rangée nord » aussi ; il
  a fallu REGARDER la capture — des poteaux gris à chaque tuile, reliés par une lisse — et
  chercher ce qui se dessine au pourtour d'une région plutôt que dans une tuile. **Le
  générateur sait maintenant ce qui arrête un piéton** : `DECOR_SOLIDE`, déclaré en Python,
  porté par le paquet, et un juge de banc vérifie qu'il dit exactement ce que disent les
  fiches de dessin (la parade de `FLOTTANTS`). **`degager_le_decor`** est le pendant de
  `boucher_les_poches` pour le mobilier : après chaque quai et chaque terrain vague, il
  enlève ce qui enferme une tuile — on ENLÈVE, on ne déplace pas, sinon le décor déplacé
  ferme autre chose. Mesuré : **191 tuiles de quai enfermées → 0**, et zéro sur les friches
  et les trottoirs. **Un seul semis amarre le quai** : la grève tire encore son dé (pour ne
  pas décaler le sien) mais ne pose plus sur les planches ; les bornes passent d'un écart de
  6 à **11** — la rangée du bord donnait une borne ou un pneu tous les trois pas. **Un quai
  a un APRON** (deux tuiles depuis la lèvre, où rien ne s'empile) et un **FOND** (trois
  rangées côté rue, où la cargaison attend le camion) ; le milieu se marche. **Moins de
  saleté** : un déchet par dix tuiles de friche au lieu de six, une mauvaise herbe par
  dix-huit — **303 objets de saleté → 166**.
- ⚠️ **Mes propres juges de la veille ont dû changer de sens**, et c'est la vraie leçon :
  ils disaient « au moins un objet par douze tuiles de quai », « une tuile de friche sur
  huit au plus », « vingt bornes » — c'est-à-dire qu'ils garantissaient exactement ce que
  Martin a renvoyé. Ce sont maintenant des **fourchettes**.
- ⚠️ **Et un juge voisin ne tenait que par un singe coincé** : « la bagarre tient le
  budget » faisait marcher 2 500 images au hasard ; à HEAD le singe finissait dans un coin
  vide (10, 1) avec un seul piéton à métier, après le changement il arrivait au centre-ville
  (146, 6) — et son plafond **recopiait** le nombre de vendeurs fixes (douze, ils sont
  treize), ce que sa propre note interdit. Il les lit maintenant dans la carte. 7 juges
  neufs (`test_quai_se_marche.py`) ; 1804 tests.
