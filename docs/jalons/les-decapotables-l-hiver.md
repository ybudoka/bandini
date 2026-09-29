# Les décapotables l'hiver

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 29 sept. 2026 : « penses au décapotable l'hiver »._ Aujourd'hui la
sport et le cabriolet rose roulent l'habitacle grand ouvert en pleine tempête de janvier.
**Quand la neige tient** (`Saisons.palette().neige > 0`, décembre à mars), les deux roulent
et se garent **capote relevée** : une toile noire mate du pare-brise jusque derrière les
sièges, une petite lunette arrière ; au dégel, ils se rouvrent. Pure fonction du jour, sans
dé : la ville ne bouge pas. **Comment** : deux machines de plus dans `sprites.js` (la même
carrosserie + la toile), rangées DANS la fiche (`SPRITES.sport.capote`), pas comme clé neuve
de `SPRITES` (concessionnaires, variantes et sauvegardes ne la voient pas) ; `vehicules.js`
choisit le dessin du moment pour `dessinerUn`, sous un nom de cache à part. **Sous la capote
on ne voit plus qui conduit** (comme dans une berline : `cavalierDe` rend `null`), la
conductrice comprise. **La tuque** (choix de Martin) : l'hiver, la conductrice sort du
cabriolet volé en **manteau et tuque roses** — sa tenue d'hiver, tirée comme l'autre, sans
dé de plus. **Juges** : `test_decapotable_l_hiver_js.py` (janvier contre juillet : le dessin
cuit diffère, pas de cavalier sous la capote, la tuque l'hiver ; retirer la règle doit
rougir) ; `test_cabriolet_js` calé en été (le banc naît en janvier) ; capture Chromium des
deux capotes.
