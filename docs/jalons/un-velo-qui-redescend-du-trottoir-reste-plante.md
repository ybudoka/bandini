# Un vélo qui redescend du trottoir reste planté

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Vu le 25 sept. 2026, en livrant M13 : le capitaine Bérubé, un personnage de plus en ville, décale les
identifiants d'un cran, et `test_velos_js::test_la_ville_roule_avec_ses_velos_sans_une_anomalie` (graine
5) a rougi. Le défaut n'est pas neuf : la base le fait aussi, à la graine 24._

**Ce qu'on voit.** Un vélo du trafic part au trottoir de son plein gré (`horsRue`), arrive au bout de son
chemin (130, 40) et attend un trou dans la voie (`attente_images`, 240 images). La voie ne se libère pas :
il rend `horsRue` et vise la chaussée — mais il reste planté sur la bordure encore une seconde et plus,
avec une `patience` qui monte, puis repart à 0,5 px par image. La trace le relève HORS VOIE (90 images
hors de la chaussée sans `horsRue`), et plus tard le chien de garde le déplace (« ROULE 8S »).

**Mesuré** (le juge de la ville, 3 000 images, graines 1 à 40) : 1 graine sur 40 sur la base (24), 3 sur 40
avec Bérubé (5, 23, 30).

**Ce qu'on a essayé.** Faire redescendre le vélo EN FORÇANT (`v.force = 90`) quand son attente au bout du
trottoir est épuisée — ce que dit déjà le commentaire de `cibleHorsRue` (« au pire il se frôle ») : la
graine 30 guérit, pas la 5 ni la 23. Ce qui le retient n'est donc pas (seulement) l'évitement : à tracer
image par image (`Vehicules.majConducteur`, ce qui met la vitesse voulue à zéro pendant ces images-là).

**Les juges.** Le juge de la ville tourne aux graines 1 et 5 ; la 5 est marquée `xfail(strict=True)` : le
défaut réparé, elle rougit, et la marque s'en va.

## Notes

**Livré le 26 sept. 2026.** Deux défauts, pas un — tracés image par image, graine par graine.

- **Graine 5 : la file arrêtée au feu.** Ce qui bouchait la voie de retour était une remorqueuse du trafic
  arrêtée au rouge, pile sur la tuile où le vélo redescend. Il attendait ses quatre secondes, rendait son
  tour de trottoir, et l'évitement le retenait encore trois secondes et demie sur la bordure. Il attend
  maintenant **avec la file** (`attendVoie`, sans compte à rebours) dès qu'un char de la voie attend
  légitimement, et le chien de garde le voit comme une attente légitime (`attenteLegitime`). Devant un
  autre bouchon (un passant, un char en panne), les quatre secondes tiennent, et il redescend **en
  forçant**, comme le disait déjà le commentaire de `cibleHorsRue` (« au pire il se frôle »).
- **Graine 23 : le char qui arrive pendant qu'il descend.** La voie était libre au bout du trottoir ; le
  vélo rendait `horsRue` au moment de DÉCIDER, puis cédait en bordure à un char qui arrivait — la trace le
  croyait perdu. Il `redescend`, maintenant, jusqu'à toucher la voie (`cibleDeLaVoie`).
- **Mesuré** : le juge de la ville, 40 graines sur 40 propres (39 sur la base, 37 avec Bérubé). Le juge
  tourne aux graines 1, 5 et 23 ; sans `attendVoie`, la 5 rougit, sans `redescend`, la 23. L'`xfail` est
  parti.
