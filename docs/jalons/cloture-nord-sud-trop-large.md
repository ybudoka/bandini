# Clôture nord-sud trop large

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les clôtures nord-sud doivent être MINCES, vues par la tranche (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « les clôtures nord-sud doivent être plus vues de haut, donc mince. »

Les clôtures lisent maintenant leurs voisines et ne sont plus couchées — mais elles ont été
corrigées **par une rotation** : le nord-sud est l'est-ouest tourné de 90°, les deux axes
échangés. D'où un panneau vertical large de sept pixels, avec sa maille et ses lisses, qui a
l'air d'être **posé à plat** plutôt que debout.

⚠️ **La bonne règle est déjà écrite deux fois dans le dépôt, et les clôtures ne l'appliquent
pas.** Les bâtiments : « toute tuile dont la voisine du sud n'appartient pas au bâtiment est
une façade — on voit toujours le mur avant, jamais le dos d'un toit ». Les meubles : « un
meuble se dessine **vu d'en haut, avec juste assez de face au sud** pour qu'on lise son
volume — c'est la même règle que les façades de la ville ».

La caméra regarde donc d'en haut, avec un peu de face au sud. Il en découle, sans rien
inventer :

- **Est-ouest** : on la voit **de face**. Sa hauteur est visible — lisses, maille, poteaux. Le
  panneau actuel est juste, il ne change pas.
- **Nord-sud** : on la voit **par la tranche**. Il ne reste que son **épaisseur** : un trait
  fin, les chapeaux de poteaux, et un liseré d'ombre d'un côté. Deux ou trois pixels de large,
  pas sept. Une clôture n'a pas d'épaisseur, c'est tout son propos.
- **Au coin**, les deux se rencontrent : le bras est-ouest garde sa face, le bras nord-sud est
  mince, et le poteau du centre fait la jointure — c'est lui qui empêche que la différence de
  largeur ait l'air d'une cassure.

⚠️ **Et un juge verrouille aujourd'hui exactement le défaut.**
`test_une_cloture_nord_sud_ne_se_peint_pas_comme_une_est_ouest` compare les deux cuissons
trait par trait et exige que « le nord-sud soit l'est-ouest **tourné**, les deux axes
échangés ». Il a rendu service — il a sorti les clôtures de leur premier bug — mais il
**interdit maintenant la correction**. Il doit être remplacé par son contraire : le nord-sud
n'est **pas** la rotation de l'est-ouest, il est **plus mince** que lui, et le juge mesure
cette largeur.

- **Juges** : la largeur peinte d'un brin nord-sud est au plus la **moitié** de la hauteur
  peinte d'un brin est-ouest, pour les **trois** clôtures ; un bout nord-sud se ferme par un
  **chapeau** et jamais par un piquet debout ; un coin garde son poteau ; et le nord-sud n'est
  plus la rotation de l'est-ouest — l'ancien juge, retourné.

**Livré.** Mesuré après coup : grillage 12 px de haut en est-ouest contre **4 px de large** en
nord-sud, bois 12 contre **5**, barbelé 14 contre **4**. Le poteau se montre debout quand un
bras est-ouest donne sa face, et en **chapeau** quand la tuile est toute en nord-sud.

## Notes

demande de Martin : elles ont été redressées **par une rotation**, donc le nord-sud est un
panneau de 7 px vu à plat. Vue d'en haut, une clôture nord-sud se voit **par la tranche** —
la règle est déjà écrite pour les façades et les meubles.

- ⚠️ Le juge actuel exige la rotation : il verrouille le défaut
