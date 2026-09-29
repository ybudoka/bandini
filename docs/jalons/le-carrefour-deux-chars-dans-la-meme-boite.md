# Le carrefour : deux chars dans la même boîte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « l'enquêter et la resserrer ». La soupape du trafic laisse un char
entrer dans une boîte déjà occupée quand son attente déborde ; c'est la vraie racine de
l'autobus poussé sur le trottoir (graine 23, [quatre juges
rouges](quatre-juges-rouges-sur-dev.md#notes)). Enquêter : quand et pourquoi l'attente
déborde (mesurer dans les boîtes, heure fixée, partir des entrées), combien de fois par
partie ; puis resserrer sans figer le trafic ailleurs.

- ⚠️ Un trafic qui se fige est pire qu'un char qui en frôle un autre : les juges de trafic
  (velos, trace, trafic, autobus, police) doivent rester verts sur plusieurs graines.

## Notes

Livré le 29 sept. 2026. **La soupape n'était pas la racine : c'était l'autobus de ligne.**

Mesuré d'abord (sonde jetée ensuite) : chaque image, les chars du trafic et des lignes dont le centre
est dans la même boîte, qui les y a mis, et avec quelle réservation (`enBoite`). Quatre graines × trois
heures fixées (8 h 25, midi, 18 h 40) × 10 000 images, plus six graines × 3 000 images comme la ville
des vélos.

- **La soupape** (`patience x 2` d'attente, puis on entre quand même) : ouverte sur une boîte réservée
  **2 fois en 120 000 images**, et les deux fois l'occupant ROULAIT (une moto entrée cinq images plus
  tôt — le camion avait vu passer toute la file avant son tour ; une auto au pas derrière un flâneur).
- **L'autobus de ligne** : 12 doublons sur 13 à 18 h 40, 1 à 2 par partie de 3 000 images sur quatre
  graines sur six — dont les 625 images à deux de la graine 23. Deux trous : `peutEntrer` prenait la
  boîte, et la même image la rendait (« la suivante n'est pas un `+` » : c'était la ligne d'arrêt `S`) —
  aucun autobus ne la tenait jamais ; et l'horaire le faisait **naître en pleine boîte** (le terminus,
  graines 5 et 23), sans réservation. `croisementLibre` ne regarde pas un autobus de ligne posé dans la
  boîte : une auto s'engageait sous lui. L'autobus de la graine 23 attendait la mère et l'enfant, et
  l'auto qui a forcé dans son flanc était entrée **sans soupape**.

Remèdes :
1. `autobus.js` : la boîte se rend sur la voie de sortie (tuile ni `+` ni `S`), comme le trafic, et
   avant l'abribus ; un autobus né dans une boîte la tient, ou ne naît pas si elle est prise.
2. `vehicules.js` : `soupapeOuverte` — elle ne s'ouvre plus contre un occupant qui avance ; seulement
   s'il n'a pas bougé d'une demi-tuile en dix secondes (sa patience, son `force`, le chien de garde ont
   échoué). En attendant, le compte reste sous `patience x 2` : l'attente est légitime, le chien ne mord
   pas. Contre un char stationné ou le joueur : la soupape d'avant. L'autobus passe par la même porte.

Après : **0 doublon** sur les 36 parties (216 000 images) ; morsures du chien de garde 0 → 0 ;
chars immobiles plus de 10 s : 43 → 42 (tous à une ligne d'arrêt, feu ou boîte — aucun dans une boîte).

Preuve (`test_trafic_js.py`) : `test_deux_chars_du_trafic_ne_sont_jamais_dans_la_meme_boite` (graines
5 et 23, 2 000 images, plafond zéro — la base en fait 2 et 2) ; `test_on_n_entre_pas_dans_une_boite_dont_l_occupant_avance`
et `test_contre_un_occupant_coince_la_soupape_s_ouvre_encore` (une boîte tenue à la main, graines 3 et 17).
Mutations : la réservation rendue trop tôt, l'autobus né sans la tenir → rouge (le premier) ; la soupape
d'avant → rouge (les deux synthétiques : entré à l'image 429 sous l'occupant) ; la soupape jamais
ouverte → rouge (le carrefour se fige) ; l'attente non retenue → rouge (le chien mord). ⚠️ Honnête : le
juge des graines ne voit pas la soupape d'avant (2 cas en 120 000 images, trop rare pour 2 000), et
« ne pas naître dans une boîte prise » ne rougit rien — la réservation à la naissance la couvre sur ces
graines. Juges du trafic, des autobus, du tramway, des éboueurs, de la neige, de la police et des
piétons : verts.
