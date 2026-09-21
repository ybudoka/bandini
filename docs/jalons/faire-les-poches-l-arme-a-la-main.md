# Faire les poches, l'arme à la main

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « je n'arrive plus à voler les gens ». Reproduit par le vrai bouton : aux
poings, une tape d'ACTION dans le dos d'un passant rapporte ses 40 $ ; **un pistolet ou une
batte en main, la même tape ne rapporte rien** et le HUD dit « BOUCLIER HUMAIN — TENIR ». Le
bouclier est le dernier maillon de `Missions.interagir` : depuis qu'il se tient, la pression
arme la prise, rend `true`, et n'atteint jamais `Combat.pickpocket` — la portée du bouclier
(26 px) couvre celle des poches (20 px), donc toute victime est aussi un otage. Le juge des
poches appelait `Combat.pickpocket` directement et ne passait jamais par le bouton. **Taper
fait les poches, tenir prend l'otage** : `Combat.majSaisie` tranche au relâcher — relâchée
avant d'avoir mûri, la pression était une tape et vide les poches (jamais depuis un char ni
à travers le mur d'une pièce) ; tenue, elle prend l'otage sans rien voler en chemin.
L'invite « BOUCLIER HUMAIN — TENIR » reste vraie. Le juge « une pression ne prend personne »
tapait dans le dos de son passant : il le fait maintenant regarder le joueur, comme
quelqu'un qu'on met en joue. 1 juge neuf, passé par le bouton, vu rouge sans la règle (0 $ à
la tape) et avec les poches vidées dès la pression (plus d'otage)
