# La barbotte du Pouce à l'essai

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (29 sept. 2026) : « valide la barbotte du Pouce et assure-toi que ça fonctionne », puis « regarde les
règles sur le net ». Les règles de l'époque (gambling-history.com, dice-play.com, le Dictionnaire historique du
français québécois) : les huit coups du jeu sont les bons — 3-3, 5-5, 6-6, 5-6 gagnent, 1-1, 2-2, 4-4, 1-2
perdent, le reste ne compte pas —, les deux côtés ont la même chance, et la maison prend de 3 à 5 %. La vraie fait
lancer le LANCEUR et le FADER chacun son tour ; Martin garde POUR et CONTRE (mêmes chances, plus lisible, et les
pipés n'ont de sens que si les côtés sont fixes). Joué dans Chromium, tout marche, sans une erreur. Trois choses
à corriger, choisies par Martin :

- **DESCENDRE** : l'invite de TOUS les escaliers dit « MONTER », même celui qui descend au tripot, et ceux qui
  redescendent d'un étage (hôpital, hôtel, plex).
- **Une cave, pas un bureau** : le tripot se meuble de classeurs gris, de bibliothèques colorées et de plantes
  vertes — il lui faut des caisses de bière, des tonneaux, des bouteilles.
- **Peu de dés jaunes pour la mission** (c02) : sous 500 $ le Pouce ne pipe jamais et le menu part à 100 $ ; à
  500 $ et plus, trois fois sur cinq ; et une dénonciation le rend honnête jusqu'au lendemain — le réflexe devant
  des dés jaunes bloque la mission pour la journée.

- ⚠️ Rien de la ville ne bouge : les mesures du tripot restent (24 × 9), aucun dé du jeu n'est tiré.

## Notes

**Livré le 29 sept. 2026.** Rien de la ville ne bouge : pas une tuile, pas un dé du jeu.

- **La validation** : les 23 juges du tripot et de la chute du Pouce verts ; puis joué dans un vrai Chromium, au
  clavier — la porte fermée avant c01 (« LE SOUS-SOL, C'EST SUR INVITATION »), ouverte après, l'escalier, la table,
  un coup honnête à 100 $, les pipés jaunes à 1 000 $ retournés contre lui (+950 $, méfiance 25 puis 40), dénoncés
  (mise rendue), une fausse accusation (les gros bras te sortent, pas une étoile) — sans une erreur JS. Le voile de
  fumée est bien peint (le plancher passe de 176 à 72 au pixel).
- **Les règles** (gambling-history.com, dice-play.com, dhfq.org) : les huit coups et la cote égale sont les bons ;
  la maison de l'époque prenait de 3 à 5 %, la piastre du Pouce (5 %) est dans l'intervalle. On garde POUR et
  CONTRE plutôt que le lanceur et le fader en alternance (Martin).
- **DESCENDRE** : un escalier qui descend porte `descend` (`carte._pt`) — celui du Dragon d'or vers le tripot, le
  retour des soins de l'hôpital, celui de la chambre d'hôtel, et l'étage du haut de chaque plex
  (`piece_de_logement(haut=True)`) ; `Missions.majInvite` le dit DESCENDRE. Juges : de deux escaliers qui se
  répondent, un seul descend (`test_interieurs.py`) ; le plex au bouton lit DESCENDRE en haut
  (`test_interieurs_js.py`) ; l'escalier du tripot (`test_tripot_js.py`). La mutation qui retire la ligne du JS
  rougit les deux juges du navigateur.
- **La cave** (`tripot.CAVE`, les `materiaux` de la pièce, comme le chalet) : le mur de fondation en pierre des
  champs et sa porte d'en arrière barrée de fer (`B@cave`, `D@cave`), le béton (`t@cave`, un grain fin : ni tache ni fissure, quatre variantes les alignaient en grille), les caisses de 24
  (`k@cave`), les étagères de bouteilles (`e@cave`), les tonneaux (`n@cave`), le feutre vert des petites tables de
  cartes (`a@cave`). ⚠️ Des matériaux remplacent `MATERIAUX_DE_PIECE` : le mur et la porte ont donc les leurs.
- **Les dés jaunes de c02** (`Tripot.miser`, `Tripot.menu`) : envoyé par Irène, tant que la preuve manque, le
  Pouce pipe CHAQUE mise de 500 $ et plus, même après une dénonciation, et la table s'ouvre à 500 $. Juge :
  `test_c02_envoye_par_irene_le_pouce_pipe_chaque_grosse_mise` (hors mission, le hasard et la paix ; en mission,
  12 sur 12, 0 sous 500 $, 6 sur 6 après une dénonciation) ; deux mutations rouges (la règle de mission retirée :
  8 sur 12 ; la mise d'ouverture retirée : 100 au lieu de 500).
