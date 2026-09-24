# Le char tourne comme son ombre

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « le pilotage des véhicules est vraiment impossible maintenant, il faut
que le véhicule tourne vraiment comme l'ombre le fait, sinon impossible de conduire ». Le
char DEBOUT n'avait que **quatre dessins** — profil, dos, face — pour un cap **continu** :
l'ombre pivotait sous lui à chaque image, la caisse attendait 45° et **claquait**, et en
claquant elle **sautait** d'une demi-longueur (la ligne de sol du profil et celle du dos ne
sont pas au même endroit). Au volant, on ne voyait plus où on pointait : on lisait son cap
sur son ombre.

- ⚠️ **Une ÉLÉVATION ne se laisse pas tourner** — un dessin de flanc pivoté de 40°, c'est un
  char qui cabre — mais une **vue d'en haut**, oui : c'est `haut`, le toit, qui roule
  désormais, tourné en **32 caps** comme l'ombre (moins de 6° d'écart avec le vrai cap,
  contre 45 avant), autour du **centre de l'empreinte du catalogue** — donc sur `v.x`,
  `v.y`, là où l'ombre est posée et où les cercles bloquent.
- ⚠️ **Et les caps ne coûtent plus ce qui les avait tués** : les 32 de toute la flotte cuits
  d'avance pesaient 1 024 canevas et 6 Mo ; ils sont maintenant cuits **un par un, à la
  demande** (`Atlas.cuireCap`) — un char à l'arrêt en coûte 3, un tour complet 34, et le
  trafic sur ses rails n'en montre que quatre.
- ⚠️ **Les phares viennent de `bas`** : les deux vues d'en haut sont le même toit lu dans
  l'autre sens (l'une ne montre que les feux arrière, l'autre que les phares), et le dessin
  qui tourne les porte **tous les deux**, sinon un char qui vient vers nous roule tous
  phares éteints — au passage, un vieux bogue de dessin : la moto et le vélo portaient leur
  phare **à la queue** dans leur pose `bas`.
- ⚠️ **La selle est un point de la MACHINE** et elle tourne avec elle (une seule `selle` au
  lieu de trois, une par pose) : sans ça, le cycliste restait assis au nord de son vélo dès
  qu'il roulait vers le sud. `cote` reste dans `sprites.js`, entier et **non dessiné** — une
  belle élévation pour le jour où un char se montre de profil sans rouler ; elle ne coûte
  rien tant que personne ne l'appelle.
- ⚠️ **Reste à faire, mesuré en chemin** : quatre dessins sont plus **courts** que leur
  fiche (l'ambulance et la remorqueuse de 5 px, le camion et l'autobus de 3 — leur grille a
  été taillée à `longueur` au lieu de `longueur + 4`), et le manque se voit au nez. 4 juges
  de banc neufs (le cap dessiné suit l'ombre à un demi-cran près et les 32 servent tous ; le
  dessin est centré sur son empreinte à tous les caps ; le toit qui tourne porte phares ET
  feux, chacun à son bout ; l'atlas ne cuit que les caps montrés), 3 refaits (la ligne de
  sol devenue le milieu, les phares qui pointent où le char va, le cavalier qui reste assis
  quand sa machine tourne)
