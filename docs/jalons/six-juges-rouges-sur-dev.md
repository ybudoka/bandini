# Six juges rouges sur dev

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « les rouges qui restent ». Rouges sur dev (bbca3176), rejoués
seuls : 1) test_quai_se_marche::test_aucun_quai_ni_terrain_vague_ne_se_referme — « 3 tuiles
de friche enfermées par du décor : (375, 16), (381, 24), (381, 25) » ; 2)
test_interieurs::test_les_lieux_des_missions_existent — « m53 : amarrage:hopital
introuvable » ; 3)
test_parole::test_la_rue_se_tait_devant_une_arme_et_crie_apres_un_coup_de_feu — la rumeur ne
suit pas la foule (peur 0,18 pour 1 voulu) ; 4)
test_navigateur::test_la_premiere_mission_se_joue_en_scenes_de_l_intro_a_la_fin — « parler à
Ti-Guy ne joue pas sa scène d'intro » ; 5, 6)
test_navigateur::test_les_echantillons_se_chargent_dans_un_vrai_navigateur et
::test_l_ambiance_et_les_voix_se_decodent — délai de 20 s dépassé, même seuls.

- ⚠️ Pour chacun : le juge a-t-il raison ? On répare le jeu, sauf si le juge mesure mal — et
  alors on le dit.

## Notes

Livré le 29 sept. 2026. Un enquêteur par cause, chacun le commit fautif en main ; le juge ou le jeu ?

- **1) Le quai — le JEU avait tort** (fautif : 36c20bd2, le bidonville). Entre deux cabanes serrées, une ruelle
  d'une tuile ; le bric-à-brac solide, semé après, en bouchait les deux bouts (une palette et une carcasse en
  (375, 16), un caddie en (381, 24-25)). Le terrain vague et le quai appellent `degager_le_decor` après leur
  semis ; le bidonville ne le faisait pas. Remède : dégager en fin de `_bidonville`, sans dé (la lampe part
  avec le baril). Trois décors disparaissent, rien d'autre ne bouge (comparé clé par clé) ; vert sur neuf
  graines de la gare (la 314159 rougissait aussi) ; les 25 juges « ne déplace rien » restent verts.
- **2) m53 — le juge mesurait mal** (fautif : fbd00fce, le premier relais de m53 de l'autre côté de la baie).
  Il a créé la forme de lieu `amarrage:<lieu>` et l'a apprise à `test_missions` et `test_barrieres`, pas à
  `test_interieurs` : il cherchait la chaîne entière parmi les portes. Il exige maintenant ce que le résolveur
  exige (un lieu connu, des amarrages) ; il mord sur un lieu inconnu et sur une ville sans amarrages.
- **3) La rumeur — le juge mesurait mal** (fautif : 36c20bd2, qui a déplacé les passants du départ). Il
  comparait une photo à l'image 300 à la foule du moment, alors que la rumeur remonte doucement par design
  (0,06 par mise à jour) : la foule y a maintenant un creux, la photo tombait en pleine remontée. Il écoute
  chaque `Rumeur.maj` au calme : jamais au-dessus de la foule, remontée au pas de la fiche, et il la rattrape.
  Quatre mutations de `son.js` le font rougir.
- **4-6) Le navigateur — les juges mesuraient mal.** Les échantillons et les voix attendaient ce qui se charge
  EXPRÈS plus tard : les bruits de quartier et de lieux (7d5dae54, 3845083d), les voix de contexte (5c3474a2,
  mp3 de 26cf6f0a) — bloqués à 66 bruitages sur 100 et 42 voix sur 66, sans une erreur. Ils les demandent
  maintenant eux-mêmes, restent le seul endroit qui prouve que TOUS les mp3 se décodent, et nomment ce qui
  manque (`attendre_ou_nommer`) au lieu de « 20 s dépassées ». La scène d'intro de m1 attend
  `/api/mission/m1` (1722dea4, le texte hors du paquet) : le juge l'attend aussi. 40/40, un mp3 illisible
  rougit en se nommant.

