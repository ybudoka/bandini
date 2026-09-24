# Quelqu'un dans la chaloupe

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « on devrait pouvoir voir le personnage ou un voleur assis dans la
chaloupe ».

- ⚠️ **Mesuré** : on y montait et elle partait **vide**, aux 32 caps et pour les deux
  silhouettes. Le joueur n'est plus dessiné une fois à bord, et `Vehicules.cavalierDe` ne
  peint que ce qui déclare une `selle` — seuls le vélo et la moto en avaient une.

✅ **Livré** (17 sept. 2026). **La coque déclare où le corps se tient**, comme le vélo : ses
fesses sur le banc de poupe (`assise`), sa main au bout de la **barre franche** (`barre`,
une pièce de plus, du haut du moteur vers le banc). Le bateau à console a les siens : assis
sur son siège, les mains au **volant** (une pièce de plus sur la console). `assisDedans` en
tire la `selle` par la même formule qu'un deux-roues.

- ⚠️ **Une posture, pas la pose de la moto** (`posture` de la fiche) : six poses neuves du
  passant, `barre_*` et `volant_*`. On ne voit de lui que ce qui dépasse du plat-bord — la
  tête, les épaules, les bras, les genoux — et les rangées du bas sont **vides** à dessein,
  comme celles du malade alité : c'est la coque qu'on doit y voir, pas des souliers.
- ⚠️ **Le banc est écrasé comme la coque** (`profondeur`) dans `imageDuCavalier`. La selle
  d'un vélo est à deux pixels du milieu et le biais du sol n'y changeait rien ; le banc de
  poupe est à huit : posé sans lui, le barreur vu de dos s'asseyait **2,0 px** derrière son
  banc (mesuré par le juge, rouge sans la correction).
- ⚠️ **Le voleur** : aucun ne monte dans une coque aujourd'hui, et c'est voulu — c'est le
  correctif « Une chaloupe sur la route » (le trafic roule sur des rails et emmenait la
  coque dans la rue). Le dessin, lui, ne choisit pas : `cavalierDe` peint celui qui la mène,
  joueur ou pilote. Le jour où une coque a un autre barreur, c'est son chemin sur l'eau
  qu'il faudra écrire, pas son dessin.

2 juges neufs (`test_poses_vehicules.py`), **rouges avant** : personne à bord à 32 caps sur
32 ; et l'ancre du barreur à 2,0 px de son banc sans le biais du sol. Vu en jeu
(Playwright), aux quatre caps et en diagonale, pour les deux silhouettes.
