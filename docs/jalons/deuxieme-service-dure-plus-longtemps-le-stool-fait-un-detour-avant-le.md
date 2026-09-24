# Deuxième service dure plus longtemps : le stool fait un détour avant le poste

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026, après la réparation de f06 : « je veux que ce soit plus long ». Du
casse-croûte au poste, la filature durait 15 à 20 s (le poste est à deux coins de rue). Le
stool fait maintenant un détour nerveux avant d'y aller : une clé `par` sur l'objectif
`suivre`, des lieux qu'il traverse dans l'ordre (`v.destination` passe au suivant quand il
arrive au précédent), puis le `lieu`. Visée : autour d'une minute et quart de filature,
mesurée au banc sur plusieurs graines. Juge : le juge de f06 file jusqu'au poste en passant
par chaque lieu du détour.

## Notes

**Livré le 22 sept. 2026.** L'objectif `suivre` prend une clé `par` : les lieux du détour,
traversés dans l'ordre avant le `lieu` (`B.mission.etapesDuSuivi` ; `destination` passe à
la suivante quand il arrive à moins de 4 tuiles de la précédente). f06 : `par: ["garage",
"terminus"]`, puis le poste — environ 190 tuiles de chaussée au lieu de 34.

- Mesuré au banc (le parcours du juge : garé, dedans, sortie, filé à six tuiles) sur six
  graines : 57 à 74 s de filature, contre 15 à 20 s. Il passe à 48 px du garage et à 32 px
  du terminus.
- Le garage et le terminus sont déjà des lieux de mission, et `devants.lieux_de_mission` ne
  lit pas `par` : la ville ne bouge pas. `test_missions` refuse un lieu de détour inconnu.
- Le juge de f06 exige chaque étape du détour et plus de 40 s de filature ; sans `par`, il
  rougit (le stool passe à 350 px du garage).
- Les répliques ne changent pas : « jusqu'au poste » reste vrai, il y va — par le chemin
  d'un stool nerveux.
