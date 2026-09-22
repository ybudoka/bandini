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
