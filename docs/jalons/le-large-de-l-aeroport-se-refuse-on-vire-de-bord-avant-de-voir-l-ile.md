# Le large de l'aéroport se refuse : on vire de bord avant de voir l'île

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22 sept. 2026) : « je voudrais que même en bateau on ne puisse pas aller
à l'île de l'aéroport avant que le pont soit réparé, une barrière invisible nous fait
tourner de bord avant qu'on puisse voir l'île ». Aujourd'hui rien n'arrête une chaloupe : le
large est ouvert jusqu'à la plage de l'île, et l'île cachée sur la carte (`masque`) se voit
à l'écran dès qu'on s'en approche. Remède : un large refusé autour de l'île, le rectangle du
masque élargi de ce que la caméra montre au plus loin (la demi-vue, 480 × 270, plus l'avance
de la caméra au volant, plus une tuile) — calculé côté jeu, où vit la caméra, et levé avec
le masque (`a01`). Une coque (ou un char blindé qui roule sur l'eau) qui s'en approche vire
de bord toute seule : le volant lui est pris le temps du demi-tour, le HUD dit pourquoi, et
elle ne franchit jamais la ligne. Un nageur y est repoussé de même : la travée manquante ne
se nage plus jusqu'au bout. Déjà dedans (vieille sauvegarde), on circule. Le mode photo ne
va pas non plus où l'œil ne va pas. Juges au bouton : un bateau lancé vers l'île par le nord
et par l'ouest vire de bord sans que la caméra montre une tuile du masque ; le nageur de la
travée est renvoyé ; TÉMOIN : `a01` faite, on passe.

## Notes

**Livré le 22 sept. 2026** — `static/js/monde.js` (`largeRefuse`, `retenirAuLarge`, `sortieDuLarge`,
`avertirDuLarge`, `vueSurLeMasque`, `AVANCE_CAMERA`), `static/js/vehicules.js` (`virerDeBord`, la ligne
au bout d'`avancer`), `static/js/entites.js` (`auLarge`, le courant), `static/js/jeu.js` (`majPhoto`),
`app/aeroport.py` (`MASQUE["raisons"]`).

- ⚠️ **La ligne** : le rectangle du masque élargi de 304 px à l'ouest (la demi-vue 240, l'avance du
  volant 48, une tuile) et de 199 px au nord (135 + 48 + 16). Elle passe 12 rangées et demie au-dessus
  du bout du pont côté île, et coupe la travée manquante vers sa 20e tuile d'eau sur 32 ; la terre la
  plus proche (le bout du tablier de La Pointe) est à 20 tuiles. Arrêté contre elle, même la caméra qui
  regarde au plus loin devant s'arrête 16 px avant l'île. Elle ne refuse que de la mer (jugé).
- ⚠️ **Sans mémoire du pas d'avant** : ce qui y entre de moins d'une tuile ressort par le bord le plus
  proche, sur un seul axe — un char qui pivote sur son arrière (`pivoterSurLArriere`) ou qu'un autre
  pousse y entre sans passer par `avancer`. Plus loin dedans, c'est une vieille sauvegarde prise sur
  l'île : on circule, comme derrière une barrière.
- ⚠️ **Le virement de bord** : à six tuiles de la ligne, le char du joueur qui y VA (une coque, ou un
  char blindé qui roule sur l'eau) pivote de 0,07 rad par image vers le large permis, moteur à 0,6,
  volant pris ; longer la ligne ou s'en éloigner reste permis. Il pivote autour de son CENTRE : sur sa
  poupe, un porte-conteneurs aurait déplacé son centre de plusieurs tuiles. Au banc : lancée de seize
  tuiles, la coque vire à 36 px de la ligne ; déjà lancée à fond à deux tuiles, c'est la ligne qui la
  retient, sans choc ni dégât. Remontée plus tard, elle ne reprend pas un virage interrompu (`monter`).
- ⚠️ **Le nageur** : arrêté à la ligne, le courant le ramène pendant 45 images, le dos tourné à l'île.
  La travée ne se nage donc plus jusqu'au bout : le souffle (café ET estomac plein) n'est plus la
  dernière porte, il est la deuxième — son juge Python reste, pour le jour où la ligne tombera.
- ⚠️ **Le mode photo** glisse le long du bord de l'île comme contre un mur, un axe à la fois (sauf
  pour qui la voyait déjà).
- ⚠️ **La coop (essai)** : arrivée pendant la livraison (f011716), sa laisse de 130 px remplace le
  zoom arrière. Sa caméra suit le milieu des deux joueurs — à 65 px au plus du premier, sans l'avance
  du volant (48) — et le second ne nage pas : elle reste dans la marge, sans juge dédié. (Avec le
  zoom d'avant, le milieu de deux joueurs éloignés pouvait tomber sur l'île.)
- Juges (`test_aeroport_js.py`) : la coque vire de bord par le nord, par l'ouest et déjà lancée, sans
  qu'une image montre l'île (la vue telle que `Jeu.rendre` la dessine, secousse comprise) ; la
  ligne à une vue de l'île et sur la mer seulement ; le nageur de la travée ramené ; le mode photo
  borné ; TÉMOIN : `a01` faite, la coque passe. `test_aeroport.py` : les deux raisons du HUD. **Six
  mutations, six rouges** : sans virage, sans la ligne du char, sans l'avance de la caméra (c'est le
  juge de la géométrie qui mord : au bouton, le virage détourne le nez avant que la caméra ait pris
  toute son avance), sans le courant, sans la ligne, la photo libre.
- Rouge connu, pas de moi : `test_le_paquet_reste_leger` (271 701 octets pour 250 000), le même sur la
  base (49cdeb0).
