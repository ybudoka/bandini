# Le carnet revient sur la même ligne en sortant d'une fiche

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « quand on entre dans une fiche personnage et qu'on en sort, je veux
que ça revienne sur la même sélection ». RETOUR (ou B) depuis une fiche rouvrait le
RÉPERTOIRE sur sa première ligne : avec dix personnes connues, on reperdait sa place à
chaque fiche. Le répertoire s'ouvre maintenant sur la personne dont on sort ; et, pour la
même raison, le CARNET s'ouvre sur la ligne de la page dont on revient (EN COURS, JOURNAL,
RÉPERTOIRE…). Juge : ouvrir la fiche de la 2e personne, en sortir par RETOUR et par B, le
curseur est sur elle.

## Notes

- `surLaLigne(cle, menu)` (`hud.js`) pose le curseur sur la ligne dont l'`item.cle` vaut
  `cle` ; une clé introuvable laisse `ouvrirMenu` choisir comme avant. Les lignes du
  répertoire portent le slug du personnage, celles du carnet `en_cours`, `journal`,
  `repertoire`. La fiche rouvre `menuCarnetRepertoire(slug)`, chaque page du carnet rouvre
  `menuCarnet('<sa clé>')` — par RETOUR comme par B.
- Juge : `test_sortir_d_une_fiche_rend_le_curseur_a_la_meme_personne`, au clavier (B = `KeyB` ;
  Échap, lui, reprend la partie). Deux mutations (fiche sans slug, répertoire sans clé)
  le font rougir.
