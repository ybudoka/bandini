# Les bulles qui interpellent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« avec une petite bulle de type bande dessiné qui nous interpelle ») : le
jeu avait déjà deux pastilles de 8 px au-dessus des têtes — le « ! » du témoin, le trait de
la peur (`cri`). Elles disent un **état d'esprit** ; elles ne peuvent pas dire un **mot**,
et c'est le mot qui manquait. `Entites.bulle(e, texte, {duree, fond, encre})` pose une boîte
à queue au-dessus de **n'importe quelle entité** (police 3x5, coins coupés, la queue sur la
tête de celui qui parle, une montée de 6 images puis une respiration), `Entites.taire(e)`
l'efface, et elle se dessine dans une **deuxième passe**, après tout le monde : dans une
pièce, un client passe devant le donneur une fois sur deux, et une bulle à moitié cachée par
une nuque ne se lit plus.

- ⚠️ Le texte **ne s'invente pas en JS** : `personnages[].heler` dans `missions.py`, comme
  toutes les répliques du jeu, court par force (`HELER_MAX`) et vérifié par un juge.
- ⚠️ Une bulle qui ne s'éteint jamais ne veut plus rien dire : elle ne s'allume que si **ce
  donneur-là** a une job pour toi (ou t'attend pour la finir), elle se tait pendant sa
  propre mission, et **aucune** bulle ne s'affiche pendant un dialogue — quelqu'un te parle
  déjà, en bas de l'écran. Deux emplois pour l'instant : les **cinq donneurs** et le
  **client du taxi** de M3, qui levait le bras au bord du trottoir sans rien dire. 1 juge
  Python (chaque donneur a son mot, assez court), 1 de banc (elle s'allume sur le bon
  donneur, s'éteint après, et vit d'une image à l'autre), 1 dans le taxi ; vérifié à l'écran
  dans un vrai navigateur (casse-croûte, bar, terminus)
