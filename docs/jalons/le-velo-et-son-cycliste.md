# Le vélo et son cycliste

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui : « il faut améliorer ça ».

- ⚠️ **Mesuré** : la machine qui tournait était le **toit** d'un deux-roues — vu d'en haut,
  un vélo est un bâton avec une barre en travers (vers l'est, un trait de trois pixels et le
  guidon dressé en travers) — et le cycliste posé dessus était un passant **assis**, la pose
  d'un banc : les fesses à la hauteur des moyeux, les mains sur les cuisses, les pieds dans
  le vide. On lisait un passant sur une échasse. **La machine est maintenant décrite en
  volume** (`MACHINE_VELO`, `MACHINE_MOTO` : roues, cadre, guidon, selle, porte-bagages,
  réservoir, moteur, lampes) **et se projette au cap** (`Atlas.projeter`) dans la vue de la
  ville : ce qui est debout monte à l'écran, et le sol se voit du **même biais que l'ombre**
  (0,5 — un juge les tient d'accord). De profil, deux roues rondes ; de dos, un trait, un
  guidon et un feu ; en diagonale, des roues en ellipse.
- ⚠️ **Rien de « le char tourne comme son ombre » n'est perdu** : 32 caps, 32 dessins
  distincts, cuits un par un à la demande (la grille par cap, le canevas par couleur) ; les
  poses `cote`, `haut`, `bas` du vélo et de la moto sont désormais **tirées** de la machine,
  plus dessinées à la main.
- ⚠️ **Une lampe est un bloc, pas un point** : un point se cachait derrière la première roue
  venue — le phare du vélo ne se voyait qu'à 13 caps sur 32, et la moto n'avait aucune lampe
  visible à 6 ; en bloc, phare et feu se voient ensemble à 28 caps sur 32. **Le cycliste
  roule** : trois poses neuves du passant (`roule_cote`, `roule_haut`, `roule_bas`, deux
  images chacune), dessinées là où la projection met la selle, le guidon et les pédales — de
  dos, le guidon est devant lui, donc plus **haut** à l'écran, et ses mains montent aux
  épaules ; de face, plus **bas**, et elles tombent à la ceinture. Il **pédale** avec la
  distance roulée (`v.parcouru` — la distance, pas la vitesse : un vélo poussé contre un mur
  ne pédale pas), un demi-tour tous les `pedale` px de la fiche ; la moto n'en a pas, et son
  pilote garde les pieds aux repose-pieds. La `selle` est **tirée** de l'`assise` de la
  machine : un seul siège, pas deux nombres à tenir d'accord. `assis` reste la pose du banc.
  4 juges neufs, **rouge avant prouvé en retirant chaque règle** (vue d'en haut : « sa
  rangée de sol touche 1 fois — on voit une machine d'en haut » ; cap figé : « aux caps 1 à
  31, ce qui se peint n'est pas sa projection » ; pose assise : « sa main est à 3,0 px de la
  poignée » ; compteur retiré : « le vélo a roulé 40,9 px et n'en compte que 0 ») ; 3 juges
  de toit (phares, bouts de caisse, lampes du moteur) ne regardent plus que les chars, et le
  dessin centré sur son empreinte tient toujours les deux-roues. 2189 tests
