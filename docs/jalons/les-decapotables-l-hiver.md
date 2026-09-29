# Les décapotables l'hiver

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 29 sept. 2026 : « penses au décapotable l'hiver »._ Aujourd'hui la
sport et le cabriolet rose roulent l'habitacle grand ouvert en pleine tempête de janvier.
**Quand la neige tient** (`Saisons.palette().neige > 0`, décembre à mars), les deux roulent
et se garent **capote relevée** : une toile noire mate du pare-brise jusque derrière les
sièges, une petite lunette arrière ; au dégel, ils se rouvrent. Pure fonction du jour, sans
dé : la ville ne bouge pas. **Comment** : deux machines de plus dans `sprites.js` (la même
carrosserie + la toile), rangées DANS la fiche (`SPRITES.sport.hiver`), pas comme clé neuve
de `SPRITES` (concessionnaires, variantes et sauvegardes ne la voient pas) ; `vehicules.js`
choisit le dessin du moment pour `dessinerUn`, sous un nom de cache à part. **Sous la capote
on ne voit plus qui conduit** (comme dans une berline : `cavalierDe` rend `null`), la
conductrice comprise. **La tuque** (choix de Martin) : l'hiver, la conductrice sort du
cabriolet volé en **manteau et tuque roses** — sa tenue d'hiver, tirée comme l'autre, sans
dé de plus. **Juges** : `test_decapotable_l_hiver_js.py` (janvier contre juillet : le dessin
cuit diffère, pas de cavalier sous la capote, la tuque l'hiver ; retirer la règle doit
rougir) ; `test_cabriolet_js` calé en été (le banc naît en janvier) ; capture Chromium des
deux capotes.

## Notes

**Livré le 29 sept. 2026.**

- **La règle** (`saisons.js`) : `Saisons.enHiver()` = la neige tient (`palette().neige > 0`) —
  du jour 1 au dégel du 11-12, puis du 37-38 au 41, la même bascule que le sol. Pas le mois du
  calendrier : une capote relevée sur une rue sans neige ne se comprendrait pas.
  `Saisons.ficheDuMoment(nom, fiche)` rend `[nom + '~hiver', fiche.hiver]` quand une fiche porte
  sa version d'hiver, sinon `[nom, fiche]` — le NOM change avec elle, sinon le cache de l'atlas
  rendrait l'image d'été.
- **La capote** (`sprites.js`, `capote(avant, arriere, demi)`) : la même machine plus la toile —
  un profil noir mat (`q`) du haut du pare-brise jusque derrière les dossiers, deux arceaux (`Q`),
  une lunette dans la pente arrière et une glace de chaque flanc. `SPRITES.sport.hiver` et
  `SPRITES.cabriolet.hiver`, rangées DANS la fiche, sans selle. ⚠️ Deux retouches faites à la
  capture : la pente passait sous le haut des dossiers (7 de haut) et les laissait percer la
  toile, et l'arrière se pinçait plus étroit que les sièges (5,1 contre 5,2).
- **Le dessin** (`vehicules.js`) : `Vehicules.ficheDuMoment(v)` choisit ce que `dessinerUn` cuit ;
  `cavalierDe` lit la même fiche, donc sous la capote on ne voit plus personne, ni la conductrice
  ni le joueur. Les lampes, l'ombre et les collisions restent celles de `v.sprite`.
- **La tuque** (`sprites.js`, `SPRITES.conductrice.hiver`) : tirée de la robe rangée par rangée —
  la tuque rose à pompon blanc et son revers sur les trois rangées du crâne, un col de fourrure,
  des manches, des bottes blanches. `couche` reste la robe (la tuque tombe). `Entites.imageDe`
  passe par `Saisons.ficheDuMoment`, comme le char.
- **Juges** : `test_decapotable_l_hiver_js.py` (4) — le dessin cuit l'hiver, au printemps, en
  décembre et pour la berline ; aucun pixel de siège sous la toile aux 32 caps ; plus de
  cavalier sous la capote ; la tuque par `Jeu.rendre()` après un vol. Trois mutations (l'hiver
  jamais vrai, `cavalierDe` sur la fiche d'été, le passant sans la saison) rougissent chacune son
  juge. `test_cabriolet_js` se cale en juillet (`jour = 21`).
- **Pas fait** : la neige sur la capote d'un char garé (la neige sur les chars garés reste au lot 1
  des saisons), et la garde-robe d'hiver des autres passants (lot 4).
