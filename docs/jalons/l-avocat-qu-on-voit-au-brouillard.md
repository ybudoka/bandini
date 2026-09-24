# L'avocat qu'on voit au Brouillard

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je ne vois pas d'image de l'avocat dans le bar, il faut en faire
une ». Le jeu promettait un avocat (« PARLER A L'AVOCAT », le menu **ME DESJARDINS**) et la
table du fond était **vide** : le point `avocat` n'était qu'un comptoir invisible, le défaut
déjà réparé pour Bouchard et Josée. **1.** **Un corps à lui**, `SPRITES.avocat` : veston
anthracite, le **V de la chemise blanche coupé par une cravate rouge**, cheveux gris et
moustache.

- ⚠️ Pas le corps commun repeint : un complet foncé sur le corps commun, c'est une
  **Cravate** — la gang du Faubourg assise à la table où l'on vient nettoyer son dossier.
  Personne d'autre en ville ne porte le rouge `t`. **2.** **Assis sur la chaise de sa
  table** (`carte.ASSIS_OU_COUCHE`, comme le patient de l'hôpital), archétype `avocat` dans
  `pietons.py` (fréquence 0, `QUI_DEDANS`) ; frappé, il se lève, se sauve — et témoigne à
  0,9. **3.** ⚠️ **Son point est passé de la table à SA chaise** (2,5 → 3,5). Une fois qu'on
  le voit, c'est lui qu'on vise : planté à sa droite, on était à **deux tuiles** du point,
  hors de `RAYON_POINT` (1,6), et ACTION ne faisait rien. **Juges** (`test_effacer.py`) :
  dans le plan, il est sur une chaise, à côté d'une table, sur son point, dans son corps ;
  au banc, on pousse la porte, il est assis dans SON sprite et n'a pas bougé après 300
  images, et chaque pas libre autour **de lui** affiche « PARLER A L'AVOCAT » et ouvre ME
  DESJARDINS. **Rouges avant** : sur la base (« 0 avocat au Brouillard »), et le point remis
  sur la table (« à 4,5, le HUD promet None »).
