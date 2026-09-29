# Les passants restent au trottoir quand on les démêle

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « garder les passants au trottoir ». Vu en réglant le juge du
signaleur ([notes](trois-juges-rouges-neufs-sur-dev.md#notes)) : une passante qui flâne
contre un corps figé (le signaleur d'un chantier) est poussée par `demeler` au bord de la
chaussée et y reste ≈ 8 s ; le trafic s'arrête pour elle jusqu'à ce qu'un char force.
`demeler` protège déjà l'enfant à vélo de ce cas, pas les autres passants. Étendre la
garde : démêler ne pousse jamais un passant sur la chaussée (il glisse le long du trottoir,
ou c'est l'autre qui cède, ou il reste collé).

- ⚠️ La foule de toute la ville en dépend : les juges « ne déplace rien », de la foule
  (`test_pietons_js`), du trafic et des passages piétons doivent rester verts sur plusieurs
  graines ; deux corps jamais sous 10 px (la mémoire « Deux corps jamais sous 10 px »).

## Notes

Livré le 29 sept. 2026.

- **La cause.** Une passante qui marche sur un corps figé en longeant la bordure (un pixel côté
  rue suffit) reçoit de `demeler` une poussée le long de la ligne des centres : chaque image, un
  peu vers la rue. Le figé ne cède pas, son pas la ramène contre lui, et l'écart latéral se creuse
  jusqu'à la voie (reproduit au signaleur sans la foule : centre à 2 592, la bordure même, 106
  images le centre sur la chaussée). Le char la voit à moins de `largeur/2 + 0,8 r` de son axe :
  il s'arrête, puis force.
- **Le remède** (`entites.js`, `demeler`). Un passant qui ne traverse pas (`resteAuTrottoir` :
  un piéton, pas un agent, pas pressé — fuit, témoin, attaque le joueur, bagarre, vole un char —,
  et pas déjà sur la rue, passage compris) n'est jamais posé plus avant sur la chaussée
  (`enfoncement` : ce que son corps en mord). À la paire, celui que sa part y mettrait s'écarte
  LE LONG du trottoir (`glissade`, un axe seul, d'autant qu'il faut pour 10 px) et l'autre prend
  tout le chemin s'il cède ; à l'application, un pas qui mordrait plus se rabat sur un axe, ou
  ne se fait pas. La garde de l'enfant à vélo reste, plus stricte (toute la rue).
- **Deux corps jamais sous 10 px.** Première version (la poussée rabattue sur l'axe) : la
  passante passait au travers du signaleur à 3,6 px — d'où la glissade calculée. Puis trois corps
  à la bordure, l'un calé contre un banc : 4 px quand l'autre restait seul à s'écarter — d'où la
  moitié gardée en glissade. Après : 10,0 px au signaleur.
- **Mesures** (3 graines × 3 000 images, joueur qui marche, heure fixée). À midi : 59 centres
  posés sur la chaussée par `demeler`, 1 067 corps enfoncés plus avant → 0 et 0. À 0,35 : 30 et
  719 → 0 et 0. Chevauchements de plus d'un pixel entre passants : 0 / 348 / 13 avant, 0 / 11 / 22
  après (pire 1,79 px) — le reste est la foule ordinaire (une mère et son petit nés l'un sur
  l'autre, un passant contre une façade), sans chaussée autour.
- **Preuve.** `test_pietons_js::test_demeler_ne_pousse_pas_un_passant_sur_la_chaussee` : un
  homme figé au bord du trottoir, une passante qui marche sur lui un pixel côté rue, puis un char
  du trafic sur la voie du bord. Vert : elle ne mord pas la chaussée, 10 px entre eux, le char
  passe sans s'arrêter pour elle ni forcer. Garde retirée : rouge (5,27 px dans la voie, le char
  arrêté 278 images pour elle, 43 à forcer).
- Le juge du signaleur (`test_chantiers_js`) écarte toujours la foule : il juge la palette, pas
  la passante ; on peut le laisser ainsi.
- **Un juge vert par chance de graine** : `test_velos_js::test_la_ville_roule_avec_ses_velos_sans_une_anomalie[1]`
  est tombé (2 vélos, aucun parti). Graines 1 à 30, base contre build : aucun départ sur 2 graines
  avant (3, 6), sur 3 après (1, 6, 28), 119 départs contre 120 ; la 1 a changé de côté. Elle est
  remplacée par la 2 (partie des deux côtés), mesure en commentaire. Au passage : la base relevait
  une anomalie de trace sur 3 graines (3, 12, 21), le build sur aucune.
