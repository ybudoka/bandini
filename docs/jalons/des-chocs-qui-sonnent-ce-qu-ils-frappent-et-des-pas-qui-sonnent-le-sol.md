# Des chocs qui sonnent ce qu'ils frappent, et des pas qui sonnent le sol

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

tranché par Martin le 30 sept. 2026 (« Go + pas des passants ») : huit chocs de véhicule
selon ce qu'on frappe — accrochage, mur, bois, barrière, piéton renversé (muet jusqu'ici),
orignal, atterrissage, crochet de remorque — et le pas selon la tuile sous le pied — herbe,
gravier, sable, bois, carrelage, tapis, neige, le béton restant le `pas` d'aujourd'hui —
pour le joueur ET les passants proches ; tout en `audio.LIEUX` (le premier écran est plein),
la synthèse et les sons d'aujourd'hui restent le filet

## Notes

**Livré le 30 sept. 2026.** 44 bruitages ElevenLabs neufs, finis à 96 kbit/s comme tous les bruitages brefs.

**Les pas selon le sol.** `audio.SOLS_DES_PAS` donne le pas de CHAQUE glyphe où l'on marche. Un juge
exige qu'un glyphe neuf y soit rangé. On y trouve l'herbe (`,`), le gravier (friche `;`, allée `g`,
ballast `T`), le sable (`s`), le bois (quai `Q`, plancher `t`, escalier `/`), le carrelage (`u`) et le
tapis (`y`, peau d'ours `U`, tatami `A`). Le béton, l'asphalte et la ruelle restent le `pas` d'avant.
La neige n'est pas une tuile : `Son.solDuPas` la lit dehors, sur la tempête (`Neige.couverture`),
sauf là où la charrue vient de passer. Tout l'hiver (`Saisons.enHiver`), la terre reste sous la
neige, même quand la rue est nette. Le joueur (`majJoueur`) et les passants (`Son.pasDePassant`)
passent par le même chemin. Pour les passants, trois bornes : seulement à 150 px et à l'écran, un
seul pas par image, et au plus 60 % du volume (`audio.PAS_DES_PASSANTS`). Leur filet synthétisé
suit leur volume, pour qu'un pas d'à côté ne sorte jamais au plein volume.

**Les chocs selon ce qu'on frappe** (`Son.SFX.choc(genre)`) :

- sous `choc_leger_vitesse` (2,5 px/image, `vehicules.PHYSIQUE`), un accrochage entre chars ;
- au-dessus, la tôle froissée d'avant ;
- un mur (`heurterMur`) ;
- le décor selon sa matière (`Son.chocDuDecor` : le bois des arbres et des bancs, le métal mince
  du lampadaire et de la borne, la tôle d'une carcasse) ;
- la clôture défoncée (bois), la barrière forcée ;
- le passant renversé, muet jusqu'ici ;
- l'orignal, une seule fois et plus deux ;
- le char qui retombe d'une rampe (`atterrissage_vz_min`) ;
- la remorque accrochée (`crochet`).

Seule l'épave garde `Son.SFX.choc()` sans genre, et un juge compte ces appels.

**Le poids.** Tout est en `audio.LIEUX` :

- `pas` se charge au premier pas hors béton ;
- `chocs` se charge à la première conduite, avec le crissement.

D'ici là, le `pas` et le `choc` d'avant jouent. Le plafond des lieux passe de 1,35 à **1,65 Mo**
(choix de Martin). La marge n'était plus que de 9 Ko, et même à 48 kbit/s il aurait fallu relever
à 1,49 Mo. Le même jour, les bruitages sans équivalent payé ont pris leurs 284 Ko dans les lieux
(plafond à 1,8 Mo) : ensemble, 1,91 Mo. Martin a relevé le plafond à **1,95 Mo**, tout à 96 kbit/s.

**À écouter** (personne d'autre ne peut juger un son). Refaire une prise par `--refaire <slug>-N`.
Les prises que le finissage a le plus remontées sont propres (RSB ≥ 39 dB), mais ce sont elles à
écouter d'abord : `pas_tapis-2/3/4`, `pas_carrelage-1`, `pas_herbe-2/3` et `choc_leger-2`, entre
+27 et +40 dB de gain.
