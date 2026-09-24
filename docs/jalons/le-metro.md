# Le métro

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux aussi un métro », puis, au choix : **souterrain**, comme à
Montréal. ✅ **La ligne jaune**, une **boucle** de six stations : Faubourg, Hôpital, La Shop,
La Pointe, puis **sous la baie** jusqu'aux Quais, Les Érables, et retour. En surface,
seulement les **édicules** — un pavillon vitré, l'escalier qui s'enfonce et le poteau au
« M » jaune. On se tient sur le trottoir devant : **DESCENDRE AU MÉTRO — HÔPITAL — 3 $**. Au
quai, le tunnel et la voie ; la rame **entre, s'arrête, ouvre ses portes et celles du quai,
et repart** à son heure (une toutes les 27 s) ; la ligne du bas dit « STATION HÔPITAL · RAME
DANS 12 S · PROCHAINE : LA SHOP ». **MONTER**, et l'on est dans la voiture : banquettes,
acier, bande jaune, le tunnel qui **défile dans les fenêtres** — ses lampes accélèrent au
départ et ralentissent pour de vrai à l'arrivée —, « PROCHAINE STATION : LA SHOP ». Les
portes restent **fermées dans le tunnel** et s'ouvrent en station : on descend sur **son**
quai, et l'escalier remonte à **son** édicule. La grande carte montre la ligne en pointillé,
sous la ville.

- ⚠️ **Une rame est une heure**, comme un autobus : sa place sur la boucle ne dépend que du
  temps de la partie — rien à simuler, rien à oublier, pas un dé du jeu (rouge-avant
  prouvé).
- ⚠️ **Un édicule n'est pas une porte de bâtiment** : les portes de la ville sont des tuiles
  « D » avec leur vitrine, et quatre juges y tiennent. Les stations ont leur liste à elles
  et réutilisent `Jeu.entrer` avec une porte qui n'est dans aucune façade ; la ville ne perd
  ni un mur ni une tuile.
- ⚠️ **Le quai et la rame sont deux pièces du CATALOGUE**, partagées par les six stations :
  posées, elles se faisaient juger comme des commerces sans commis.
- ⚠️ **On remonte ailleurs qu'on est descendu** : `Jeu.entrer` retient la rue de l'entrée ;
  `B.exterieur` est recalé à chaque image sur l'édicule de la station où l'on est — la
  sauvegarde, la sortie et la mini-carte le lisent tous (juge : descendu à Faubourg, sauvé à
  l'Hôpital). Et le battant de la sortie s'ouvre sur l'édicule, pas sur « la tuile au-dessus
  du pas » : quand le trottoir est au nord, c'est la chaussée.
- ⚠️ **La porte de la rame mène au quai, jamais à la rue** : `Jeu.sortir` passe d'abord par
  `Metro.sortir`.
- ⚠️ **Recherché, on ne passe pas le tourniquet** : une rame où la police ne suit pas, qui
  dépose à l'autre bout de la ville, serait la meilleure cachette du jeu.
- ⚠️ **Pas pendant un fondu** : `Jeu.entrer` est appelé au milieu d'une image, et la fin de
  cette image tournait encore dehors — le billet s'effaçait avant d'arriver au quai.
- ⚠️ Le paquet : 384 octets gzip (74,3 Ko sous 75). 18 juges neufs (`test_metro.py`,
  `test_metro_js.py`) ; rouge-avant prouvé neuf fois — le dernier par l'erreur qui protège
  la pose d'un édicule, pas par son assertion.
- ⚠️ **Et un juge sans rapport, resserré sur sa règle** : « la fille de la Brume tient son
  coin » comparait UN chemin de la fille à UN chemin de passante — sur la base seule,
  décaler trois dés faisait marcher la passante 121 px et la fille 554. Il mesure maintenant
  six essais, une graine chacun : avec son poste, la passante marche au moins 1,5 fois plus
  qu'elle ; sans, 1,0 (rouge-avant prouvé). Reste possible : des voyageurs qui montent et
  descendent, une deuxième ligne.
