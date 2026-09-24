# Plus de temps pour les courses aux flèches

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « je veux ajouter du temps pour les courses avec flèche bleue, je
n'ai pas assez de temps ». Les cinq chronos exigent 69 % de la vitesse max de l'auto en
moyenne (165 px/s sur 240), sur trois tours de 10 à 14 virages, sans compter le trafic ni
les freinages. Plan : faire rouler un pilote au banc sur chaque circuit pour MESURER un tour
propre, puis donner un chrono qui laisse une vraie marge ; le juge « même vitesse que le
Tour du Faubourg » garde l'égalité entre quartiers, et son plafond descend pour qu'un chrono
serré ne revienne pas.

## Notes

**Livré le 22 sept. 2026.** Un pilote au banc (une sonde, pas un juge) a roulé chaque circuit
avec la vraie physique : il vise un point de la piste 5 ou 8 points devant lui, tient le gaz,
freine quand l'angle dépasse 0,5 rad, et son char est increvable. Temps pour les trois tours,
contre le chrono d'avant :

| Course | Chrono d'avant | Pilote (2 essais) | Chrono neuf |
|---|---|---|---|
| Faubourg | 2:00 | 96 s, 98 s | **3:00** |
| Érables | 1:30 | 63 s, 84 s | **2:15** |
| Shop | 1:55 | 87 s, 90 s | **2:50** |
| Quais | 1:55 | 101 s, 102 s | **2:55** |
| Pointe | 1:50 | 89 s, 108 s | **2:45** |

L'étalon passe de 69 % à 46 % de la vitesse max d'une berline (≈ 110 px/s au lieu de 165) ; les
quatre autres exigent toujours la même vitesse, arrondie en faveur du joueur (la Pointe à 2:45
plutôt qu'à 2:40 : à 2:40 elle tenait à 0,1 % de l'étalon, un point de circuit de plus la faisait
rougir). Le juge `test_les_chronos_exigent_la_meme_vitesse_que_le_tour_du_faubourg` refuse
maintenant plus de 50 % de la vitesse max (il acceptait 75 %) — mutation : les chronos d'avant
sous le juge neuf, rouge (« 164.8 <= 120 »).

- ⚠️ **Le char du pilote éclatait en UN choc** à 190 px/s (« SANS CHAR, PAS DE COURSE » sur
  les Quais et la Shop, même avec `vie` remise à 50 à chaque image) : à la vitesse qu'exigeait
  l'ancien chrono, un joueur qui accroche un char du trafic perd la course d'un coup. Il a fallu
  `vie = 1e6` pour mesurer.
- ⚠️ **Le trafic fait l'écart**, pas le circuit : 63 s puis 84 s sur les Érables, le même pilote,
  selon qui traversait. Un chrono se mesure sur le pire essai, pas sur le meilleur.
- `test_histoire_js.py` lisait « TOUR DU FAUBOURG 2:00 » à l'écran : il lit 3:00.

