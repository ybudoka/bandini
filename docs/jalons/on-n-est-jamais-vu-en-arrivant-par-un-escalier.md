# On n'est jamais vu en arrivant par un escalier

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 30 sept. 2026, une capture de l'étage de la villa à l'appui : « il y avait un garde qui regardait
l'escalier dans la mission, impossible de réussir » — v02, _Le dossier du sergent_, ratée deux fois (jours 480
et 552 de sa partie).

On monte à l'aveugle : chaque étage de la villa est un cadre de caméra, et celui d'en haut ne se voit pas
d'en bas. Le garde de l'étage (`etage_nord_sud`) descendait le couloir au tapis jusqu'à la rangée 64, deux
tuiles devant l'arrivée du grand escalier (18, 66), en regardant vers elle : pendant un quart de sa ronde, on
débouchait dans sa lampe, et l'alerte partait 25 images (0,4 s) après le fondu.

- L'arrivée d'un escalier est un **refuge** : planté là, aucun garde ne te soupçonne, jamais — on y regarde
  où ils sont avant de bouger.
- Un juge plante le joueur à chaque arrivée, deux rondes complètes de chaque garde.

## Notes

- **Livré le 30 sept. 2026.** Au banc, le garde de l'étage sondé à chaque phase de sa ronde : l'arrivée était vue
  quand il descendait entre les rangées 55 et 63, alerte de 25 à 227 images après le fondu. Le juge a trouvé
  **trois arrivées vues sur quatre**, pas une :
  - l'étage (18, 66) : le garde du tapis descendait à 64. Il tourne maintenant à **60** — six tuiles, sa lampe
    en porte cinq la nuit. Une première idée (tourner au croisement de la coursive, 56) mettait sa pause pile
    au croisement : le marcheur de v02 s'y faisait prendre en sandwich avec le garde de la coursive ;
  - la cuisine (16, 29) : le garde du corridor la voyait par la porte (18, 26). L'arrivée recule en (14, 30) ;
  - la cave (40, 67) : juste sous l'ouverture du couloir de la cave (40-41, 66). L'arrivée passe en (40, 68).
- **Le juge** : `tests/test_infiltration_js.py::test_on_n_est_jamais_vu_en_arrivant_par_un_escalier` — le
  joueur planté à chaque arrivée, 12 000 images depuis la relève ; le moindre soupçon rougit. Avant la
  correction, il nommait les trois gardes. v01, v02 et v03 rejouées de bout en bout.
