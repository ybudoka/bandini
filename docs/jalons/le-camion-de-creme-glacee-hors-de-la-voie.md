# Le camion de crème glacée hors de la voie

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « le camion de crème glacée devant Ti-Paul devrait être sur le terrain ou le
trottoir pour ne pas bloquer la voie ». Il naissait sur `Histoire.tuileDeRue` près du dépanneur des
Érables — une tuile de CHAUSSÉE : garé en pleine voie vers l'ouest, il arrêtait le trafic derrière lui.

Le changement : sa place se cherche HORS de la chaussée, près de la porte du dépanneur — d'abord une
allée (la poussière de pierre du terrain voisin), sinon l'herbe, sinon le trottoir ; son emprise entière
hors de la rue, loin des portes, sans toucher un décor, et le nez vers une rue qu'il rejoint tout droit.

- ⚠️ Le trottoir devant Ti-Paul est déjà plein (guichet, édicule, abribus, banc, et les donneurs juste
  au-dessus) : c'est le terrain voisin qui le prend.
- ⚠️ Sans dé et sans rien poser à la carte : la ville ne bouge pas, seul le point de naissance change.

## Notes

**Livré le 30 sept. 2026.**

- **Sa place** (`Missions.placeDuCamion`) : cherchée autour de la porte du dépanneur (12 tuiles), une emprise de
  trois tuiles dans l'axe — une allée d'abord, puis l'herbe, puis le trottoir ou l'abord (`solDuCamion`) ; jamais
  la chaussée, un mur, une porte ou l'eau ; à trois tuiles au moins de toute porte ; sans toucher le décor ni le
  mobilier de la rue ; le nez tourné vers une rue qu'il rejoint tout droit en six tuiles. Aujourd'hui : l'allée du
  terrain voisin, tuile (20, 156), à 150 px de la porte de Ti-Paul, le nez vers la rue nord-sud à l'est.
- Les motoneiges, qui se tiennent à trois tuiles du camion (`placeDesMotoneiges`), lisent la même place.
- **Juges** (`tests/test_creme_glacee_js.py`) : aucun coin de son emprise sur la chaussée, aucun décor sous lui,
  et à côté du dépanneur ; à l'accélérateur (la touche, pas `vitesse`), il atteint la rue sans rien cogner.
  Deux mutations les font rougir (l'ancienne place dans la voie ; le garde du décor retiré). Le juge des enfants
  à vélo remet le camion DANS la rue, dans le sens de sa voie : c'est la tournée qu'il juge, et, poussé tout droit
  depuis l'allée, le camion traversait les terrains et l'enfant le perdait.
