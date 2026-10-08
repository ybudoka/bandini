# Le volant tactile en joystick

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 8 oct. 2026 : au volant, au doigt, « au lieu des flèches, je veux un joystick sous forme d'un
carré aux côtés arrondis (===) avec le joystick au centre limité au bord. Il doit avoir le même
comportement que les flèches, mais aussi apparaître comme le joystick normal. »

- Les deux boutons ◀ ▶ (`#volant`) deviennent UNE piste horizontale aux bouts arrondis, toujours visible
  au volant, avec le pouce du joystick à pied (`#croix u`) posé au centre.
- Le pouce suit le doigt sur l'horizontale seulement, et s'arrête au bord de la piste.
- Même comportement que les flèches : gauche ou droite, tout ou rien (`vTact`), rien de plus. Lâcher
  ramène le pouce au centre.

## Notes

**Livré le 8 oct. 2026.**

- `#volant` n'a plus de boutons : une piste de 220 × 88 px (`border-radius` à la moitié de la hauteur),
  son pouce (`u`) habillé comme celui du joystick à pied (`#croix u`), toujours visible au volant.
- `Entree` : le pouce suit le doigt sur l'horizontale, borné à la demi-course moins 6 px ; il pose
  `vTact.gauche` / `vTact.droite`, tout ou rien, avec deux crans (entre à 25 % de la course, sort sous
  15 %) — le doigt posé au milieu ne tourne pas. Le doigt capturé tient même sorti de la piste. Quitter
  le volant (`contexte`) lâche le doigt.
- L'écran COMMANDES (`Hud`, `PLAN_TACTILE_VOLANT`) dessine la piste et son pouce, qui va au bord du côté tenu.
- Juge : `test_navigateur.py::test_au_volant_les_commandes_tactiles_deviennent_des_pedales` — le pouce au
  centre, il suit le doigt, reste sur l'horizontale, s'arrête au bord (rougit sans la borne), revient au
  centre au lâcher, et rien au milieu.
