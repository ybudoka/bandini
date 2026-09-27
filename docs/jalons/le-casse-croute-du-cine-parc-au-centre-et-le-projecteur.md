# Le casse-croûte du ciné-parc au centre, et le projecteur

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (27 sept. 2026) : « pour le ciné-parc, la cabane doit être au centre et vendre
popcorn, chips, liqueur, nachos etc. », « cinéma aussi », « avec un effet projecteur ». La
cabane quitte le coin sud-ouest pour le milieu du terrain, dans l'axe de l'écran, entre la
2e et la 3e rangée : casse-croûte ET cabine de projection. Sa porte s'ouvre sur une pièce,
un comptoir `cineparc` (maïs soufflé, chips, nachos, liqueur, chocolat), l'été seulement. Le
Rialto vend la même chose (chips et nachos de plus). L'effet projecteur : pendant la séance,
un faisceau translucide part de la fenêtre de la cabine et s'élargit jusqu'à l'écran,
poussière qui passe ; au Rialto, le même du mur du fond à la toile, pendant le film.

- ⚠️ Déplacer la cabane change l'ordre des cases : les places des spectateurs bougent (dans
  le bloc seulement, derrière un fondu).

## Notes

_Livré le 27 sept. 2026._

- **La cabane au centre** (`app/blocs/cineparc.py`) : huit tuiles sur trois, colonnes 18 à 25, rangées 12 à 14 —
  au milieu de la 2e rangée de cases, centrée sur l'écran à la tuile près, la porte au sud dans le même axe.
  L'ancien coin sud-ouest redevient de l'asphalte. Ses vitrines (`lampes`) l'ont suivie. La rangée coupée garde
  dix cases de chaque côté, en paires : les poteaux à haut-parleur tombent toujours juste.
- **Elle s'ouvre** : une pièce à sa mesure (`PIECE_CASSE_CROUTE`, huit tuiles de large comme sa façade) — le
  projecteur contre le mur nord, dans l'axe de sa fenêtre, le frigo, l'étagère, le comptoir, la caissière.
  Le comptoir `cineparc` (`magasins.COMPTOIRS`) : l'été seulement (`saison`), de 17 h à 2 h. Hors saison, il le
  dit à sa façon : chaque comptoir de saison porte maintenant son mot (`hors_saison`, lu par
  `Missions.comptoirFerme`) — la cabane à sucre garde « ON OUVRE AU TEMPS DES SUCRES », le ciné-parc dit
  « ON ROUVRE L'ÉTÉ ».
- **Le même grignotage aux deux cinémas** (`magasins._CINEMA`) : maïs soufflé, chips, **nachos** (neufs :
  6 $, +16 PV, +14 souffle — 5 au dollar, sous le hot-dog de `test_reclame`), liqueur, chocolat. Le Rialto
  y gagne les chips et les nachos.
- **Le projecteur** (`Cineparc.faisceau`) : trois cônes l'un dans l'autre, en lumière qui s'additionne
  (`lighter`), qui tremblote comme une lampe à arc, seize grains de poussière qui filent de la lentille à la
  toile — fonction de l'image, ni dé ni état. Au ciné-parc, il part de la fenêtre de la cabine (`bloc.cabine`,
  allumée pendant la séance) jusqu'au bas de l'écran, et se peint **par-dessus la nuit**
  (`Cineparc.dessinerFaisceau`, après `Base.fin`) : sous la nuit, il s'y éteignait. Au Rialto, le même remplace
  l'ancien trait pâle (opacité 0,06, neuf tuiles fixes) : du mur du fond, au-dessus de la porte, jusqu'à la toile,
  en fondu avec les lumières.
- **Juges** (`test_cineparc_js.py`, `test_enseignes_js.py`) : la cabane est le seul bâtiment du stationnement,
  centrée sur l'écran, entre la première et la dernière rangée, sa porte vers son comptoir ; les deux menus ont
  maïs, chips, nachos, liqueur ; le comptoir sert un soir d'été et se dit fermé le matin et l'hiver ; le
  faisceau part de la cabine, couvre toute la toile, le rendu du jeu le peint, et rien le midi ; au Rialto, il part
  du mur du fond. Chaque juge a été vu rougir sous sa mutation (huit mutations). Regardé dans Chromium : la
  nuit, la brunante, le menu, le Rialto pendant le film.
- ⚠️ `test_carte_du_depot` est rouge sur `dev` avant ce jalon (`tests/test_garage.py` absent de la carte) : pas de
  lui.
