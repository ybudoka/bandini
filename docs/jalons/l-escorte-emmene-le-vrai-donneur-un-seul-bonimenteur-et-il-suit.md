# L'escorte emmène le vrai donneur : un seul Bonimenteur, et il suit

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « il y a 2 Marcel Dumouchel et je ne sais pas comment l'escorter »
(p14). L'objectif `proteger` (p14, f09) CRÉE un second personnage à côté du donneur déjà
posé : deux Bonimenteurs, deux Marco. Et le second ne bouge jamais : `creerPersonnage` le
met `fige`, et la branche `fige` de `majPieton` sort AVANT celle de `suit`. Pire,
`Histoire.donneur()` rend le PREMIER — celui resté à l'arche : les Skateux de l'objectif
`tuer` (`ou: "donneur"`) arrivent à la foire, pas au poste, et la fin se dit au téléphone à
deux pas de lui. Les juges téléportaient le protégé au poste : aucun ne l'a vu rester
planté. Correctif : ⚠️ l'escorte prend le donneur qui est LÀ (un clone seulement s'il n'y en
a pas en ville) ; `suit` passe avant `fige` ; à la fin (réussite, échec, abandon), il cesse
de suivre et rentre à son poste dès que lui et son poste sont hors champ, reposé frais (mort
ou assommé compris). Juges : le protégé MARCHE jusqu'au poste derrière le joueur (sans
téléportation), un seul Bonimenteur, les Skateux arrivent près de lui, et il rentre à
l'arche ; mutations.

## Notes

**Livré le 22 sept. 2026.** Au banc d'abord : à l'arche, deux Bonimenteurs, et celui de
l'escorte bougeait de 3 px en une seconde (la poussée de la foule, rien d'autre). Trois
défauts empilés, pas un : le clone (`poser` créait un personnage à côté du donneur), l'état
`fige` qui sortait de `majPieton` avant `suit`, et l'allure 0 de `creerPersonnage` — même
débloqué, il aurait suivi sur place.

- **Le vrai donneur** (`histoire.js`, `poser`) : `donneur(slug)` s'il se tient en ville ;
  un personnage neuf seulement sinon (donneur `point:`). Son poste est retenu (`chezLui`),
  sa `plante` retirée — un fige loin de sa plante est un mur pour la foule (`cede`).
- **Il attend, puis suit** (`majProtege`) : rien tant qu'on n'est pas à 3 tuiles de lui, et
  le GPS mène à LUI ; rejoint, le message « IL TE SUIT — À PIED OU EN CHAR », et le GPS
  passe au lieu. `entites.js` : `suit` passe avant `fige`, et `vitesseSuite` (il court à
  `joueur_sprint`).
- **Sur nos pas** (`suivreLaPiste`) : un pas tous les 12 px, il vise le plus vieux qu'il
  n'a pas atteint, droit sur nous à moins de 3 tuiles. ⚠️ L'arche est à 215 tuiles du
  poste (369 tuiles de chemin) : au banc, en ligne droite et plafonné à `pieton_course`,
  le joueur qui court le laissait à 2 800 px contre une façade.
- **Le char** : arrêté à 40 px de lui (le rayon du client du taxi), il monte — `dansVehicule`
  + `dessine: false`, porté par `majPieton`, intouchable par `blesser`. Il descend quand on
  descend, côté passager, et **au lieu** (sinon la réplique suivante se disait au téléphone).
- **L'arrivée** : `lieu` n'est atteint qu'avec lui, rejoint, à `rayon` + 2 tuiles.
- **La fin** (`lacherLeProtege` dans `nettoyer`) : réussite, échec ou abandon, il lâche le
  joueur ; `majRetours` le ramène à son poste, remis à neuf, dès que ni lui ni son poste
  ne sont à l'écran — couché ou mort compris, un seul personnage, jamais sous nos yeux.
  ⚠️ **Le même, pas un neuf** : la première version le recréait (`creerPersonnage` →
  `creerPieton`, deux dés), et le moment du retour dépend d'où finit la caméra — qu'une
  scène déplace. `test_une_scene_de_mission_ne_tire_aucun_de[f09]` et `[p14]` l'ont vu :
  le prochain dé n'était plus le même avec et sans scène.

Juges (`test_dix_missions_deux_js.py`) : l'escorte à la course de l'arche au poste, sans
téléportation (écart max < 8 tuiles, arrivés ensemble) ; le char (monter, descendre au poste,
Skateux près de lui, fin en personne, retour à l'arche) ; on file 120 tuiles devant en char,
il nous retrouve ; raté, il rentre debout ; seul au poste, rien ne compte. **15 mutations,
13 rouges.** Deux vertes, dites telles quelles : exiger `suit` à l'arrivée double « lui aussi
au poste » dans tous les cas jouables (gardé : un donneur dont le poste touche le lieu
terminerait l'escorte sans être rejoint) ; retirer `plante` ne change rien au banc (la
foule ne s'y frotte pas) — gardé pour la raison de `cede`.

f09 (Marco) passe par le même code : un seul Marco, qui suit depuis le garage.

Rouges d'avant, rejoués sur `dev` nu (`1c8e2e8`) avec les mêmes échecs — pas de ce
correctif : `test_histoire_js` (cravates de M2, repos à voix haute), `test_moteur_js` (la
foule ne se traverse plus, courir ne traverse pas les gens, celui qui tient son poste cède,
la bagarre tient le budget), `test_missions_en_scene_js` (intros seules de f04 et p01, dés
de la scène de h02).
