# Des meubles d'un seul tenant : table, tapis, machine

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

suite des lits, demande de Martin (« regarde si d'autres composantes mériteraient un
traitement similaire », puis « oui vas-y »). J'ai compté les blocs dans les 29 plans et
rendu chaque forme telle qu'elle se peignait : même défaut pour trois glyphes. Le
**billard** du bar et de la taverne (table 4 × 2), l'établi du garage (3 × 2) et treize
tables sur deux rangées étaient autant de petites tables avec chacune ses bords rentrés, son
vernis, son chant et son ombre ; le **tapis** mettait son galon en haut et en bas de chaque
tuile, donc un 3 × 3 était trois chemins de couloir sans bord à gauche ni à droite ; une
**presse** de l'usine (4 × 2) était huit petites machines avec leurs boulons.

- ⚠️ **C'est la fiche qui le dit** : `bloc` dans `carte.LEGENDE` (lit, table, tapis,
  machine), et `varianteDeLit` devient `varianteDeBloc(g)` — le masque des côtés où le même
  glyphe continue, plus un **grain** dans les bits 4 et 5 (sans lui, deux tuiles au même
  masque avaient le même grain de tapis, et une machine seule ne pouvait plus tirer le sens
  de sa courroie au sort). Chaque peintre n'a qu'une règle de plus : ce qui marque un bout
  (chant, vernis, galon, boulon, face, ombre) ne va qu'aux tuiles où le bloc s'arrête, le
  reste court d'une tuile à l'autre ; la courroie d'une machine suit le sens du bloc. Une
  table, un tapis, une machine d'une seule tuile n'ont pas changé d'un pixel (un juge le
  vérifie).
- ⚠️ **Le juge des plans a rougi une fois** : dans la taverne, la table de gauche touchait
  le billard, et les deux auraient été peints comme un meuble en L de 4 × 4 — le billard
  passe contre le mur de l'est. Restent tels quels, à dessein : le comptoir (déjà d'une
  seule planche), l'étagère (cadre continu), les classeurs et les frigos (des unités côte à
  côte), l'escalier (ses marches s'enchaînent), les chaises (des rangées de sièges, jamais
  une banquette). Juges : la liste des `bloc` est exactement ces quatre-là ; un bloc est un
  rectangle plein dans les 29 pièces (et un lit fait au plus 2 × 2) ; trois juges de banc
  cuisent un 4 × 2 de tables, un 3 × 3 de tapis et un 4 × 2 de machines et lisent les traces
  (vernis au nord seulement, chant au sud, deux galons aux coins et aucun au centre, un
  boulon par coin, courroie couchée qui court jusqu'au bord). Vu à l'œil dans un rendu
  avant/après des onze formes de blocs du jeu
