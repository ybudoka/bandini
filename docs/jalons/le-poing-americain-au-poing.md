# Le poing américain au poing

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « l'arme poing américain devrait être seulement un tip gris au bout des
poings, mais quelque chose de plus gros à ramasser ».

- ⚠️ **Vu avant, en capture** : un seul dessin (`OBJETS.poing_americain`, 12 × 6 px) servait
  à la main, à la roue et au sol — tenu, il dépassait du poing comme une planche aussi large
  que le torse ; par terre, gris sans contour sur le gris du trottoir, on ne le voyait pas
  tomber. **Deux dessins maintenant.** Dans la main, `EN_MAIN.poing_americain`
  (`sprites.js`) : un bout d'acier de **2 × 3 px** posé sur la prise (le pixel 2, 5), et
  `dessinerArme` le tient **au quart de tour le plus proche** — tourné de biais (0,9 rad au
  repos), trois pixels n'étaient plus qu'une tache. Par terre et dans la roue,
  `OBJETS.poing_americain` passe à **15 × 8 px** : quatre anneaux aux trous sombres sur la
  barre de paume, **cerné de noir** pour se lire sur le trottoir, l'asphalte et l'herbe. Les
  autres armes se tiennent comme elles se ramassent (une arme absente de `EN_MAIN` ne change
  pas). Juge : `test_le_poing_americain_se_tient_en_bout_de_poing_et_se_ramasse_en_arme`
  (`test_moteur_js.py`) — il lit ce que le VRAI `Entites.dessiner` cuit pour l'arme, au
  coup, au repos et par terre ; il rougit si la main reprend le dessin du sol, et si le sol
  redevient la dalle pâle sans contour.
