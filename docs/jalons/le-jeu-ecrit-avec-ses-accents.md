# Le jeu écrit avec ses accents

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

Demande de Martin (17 sept. 2026) : « le jeu doit supporter les accents ». Mesuré avant : la
police pixel 3×5 (`POLICE_PIXEL`) n'a que des majuscules nues, et `Atlas.normaliser` **retire**
chaque accent avant de dessiner (« HÔPITAL » s'écrit HOPITAL) — un choix du jalon « Gestes et
lisibilité », quand un glyphe absent tombait sur « ? ». Deux conséquences : un texte accentué
à la source perd ses accents à l'écran, et des centaines de textes du jeu ont été écrits sans
accents dès le départ (« PARTIE SAUVEGARDEE », « HOPITAL A MOITIE PRIX », « LA POLICE A
LACHE »), côté JS comme côté Python.

- **1re vague — la police** : les accents se dessinent **au-dessus** de la capitale, dans
  l'interligne (aigu, grave, circonflexe, tréma ; la cédille dessous), sans changer la largeur
  d'une lettre ni la hauteur d'une ligne ; les lieux où le texte colle au bord du dessus
  (panneau de chantier, bulle) se vérifient sur capture.
- **2e vague — les textes** : remettre les accents dans tout ce qui s'affiche, fichier par
  fichier, et un juge qui refuse un mot connu sans son accent.

**1re vague livrée le 17 sept. 2026 — la police dessine les accents.**

- `Atlas.normaliser` garde les lettres accentuées (NFC, un caractère chacune) ; `lettre`
  décompose chaque caractère une fois (NFD) en glyphe de base + marques de `MARQUES_PIXEL`
  (aigu, grave, circonflexe, tréma au-dessus, cédille dessous). Les quatre faux « É È À Ç »
  de `POLICE_PIXEL`, copies de la lettre nue, sont partis. Une lettre dont la marque n'est
  pas dessinée (« Ñ ») garde sa base au lieu d'un « ? ».
- ⚠️ **La forme a été choisie sur capture, entre trois** : un accent d'un seul pixel ne se
  lisait pas ; collé à la lettre, « Ê » se lisait comme un E plus grand et « Î » comme un I
  plus haut. Retenu : **deux rangs, et un rang vide avant la lettre** (rangs −3 et −2). Ni la
  largeur d'une lettre ni la hauteur d'une ligne ne changent : l'accent prend l'interligne.
- ⚠️ **Trois endroits collaient le texte au bord du haut**, et l'accent tombait dans le cadre :
  la bulle (11 → 12 de haut, texte à 4 du haut — l'accent touchait le trait, de la même
  encre), le panneau de chantier (9 → 12, grandi vers le haut : son bas reste où il pendait)
  et la plaque de la station de métro (11 → 13). Menus (14 px par ligne), boîte de dialogue
  (9) et enseignes (texte à 4 du haut) avaient déjà la place.
- Tout ce qui était déjà accentué à la source s'affiche maintenant avec ses accents : les
  noms de quartier (« LES ÉRABLES »), les répliques des passants (« HÉ! LE COUSIN! »), les
  messages récents (« CHAR ASSURÉ »).
- **Juges** : `test_la_police_dessine_l_accent_au_dessus_de_la_lettre` compte les pixels
  peints (l'aigu à sa place exacte, à l'échelle 1 et 2 ; quatre accents, quatre dessins ; la
  cédille dessous ; « E » + U+0301 = « É » ; « é » = « É » ; la largeur ne bouge pas) — rouge
  quand on retire la boucle des marques ; le juge « la police sait écrire tout ce que le jeu
  affiche » passe par `Atlas.connait` et attend « HÔPITAL ».

**2e vague livrée le 17 sept. 2026 — les textes retrouvent leurs accents.**

- **184 chaînes corrigées** dans 13 fichiers : les menus et messages du moteur (`hud.js`,
  `missions.js`, `vehicules.js`, `police.js`, `jeu.js`, `combat.js`, `entree.js`), les
  enseignes et les tags (`devantures.py`, 50 textes), le journal du matin, les paliers de boulot
  (`economie.py`), les panneaux de chantier, les profils de manette. On n'a **ajouté que
  des accents** : un script refusait toute correction qui changeait autre chose, posait mot à
  mot DANS le littéral (« IL A FINI — RESTE À SAVOIR CE QU'IL A FAIT » : un « A » sur trois)
  et relisait le fichier posé.
- ⚠️ **Comment on les a trouvées** : le correcteur français de macOS (`NSSpellChecker`, par
  un script Swift) sur chaque mot des chaînes affichables — un mot refusé dont une
  suggestion a les mêmes lettres est une faute sûre (« hopital » → « hôpital ») ; un mot
  juste qui a une variante accentuée juste aussi (« A » / « À », « PASSE » / « PASSÉ ») est
  AMBIGU et s'est relu dans sa phrase, 704 chaînes en cinq lots. ⚠️ Le correcteur admet
  les rectifications de 1990 (« aout », « croute ») : le dépôt garde l'orthographe
  traditionnelle, partout.
- ⚠️ **Laissés sans accent, exprès** : les noms de voix ElevenLabs (« Khaivan - Quebec
  accent » — c'est leur nom sur le compte), le SQL de M14, `fr-CA`, les étiquettes du mode
  TRACE (« BOITE », « DEPORT » : un outil de diagnostic que des juges comparent), « Me
  Desjardins » (Maître), « COUTURE CHEZ EVA » (on n'invente pas un prénom), « PIZZERIA ».
- ⚠️ **Les enseignes des quartiers pauvres et cossus** (3e vague, arrivée PENDANT cette livraison)
  étaient neuves et sans accents : le juge les a vues au remontage. « À LOUER » y est aussi une
  CONSTANTE comparée (`devantures.A_LOUER`, relue par `vitrines.py` et `test_quartiers`) : la
  constante et ses juges ont changé ensemble. La ville générée a été comparée avant/après, clé par
  clé, accents retirés : identique.
- **23 comparaisons, dans 8 fichiers de juges, suivaient une chaîne mot pour mot** et la
  suivent maintenant accentuée.
  ⚠️ `test_son_js` vérifiait que « TOUCHE L'ECRAN » était **absent** : un `not in` sur
  l'ancienne forme serait resté vert pour toujours.
- **Juge** : `tests/test_accents.py` refuse 96 mots qui n'existent pas sans leur accent
  (« HOPITAL », « DEJA », « FOURRIERE », « AOUT »…) dans les chaînes de `static/js`
  (commentaires exclus : ils sont écrits sans accents, et c'est du code) et dans TOUT le
  paquet servi au navigateur, carte comprise. Rouge sur « PARTIE SAUVEGARDEE » remis dans
  `hud.js`, rouge sur l'enseigne « HOPITAL » remise dans `devantures.py` — et il a trouvé, à
  sa première exécution, trois textes de `manettes.py` que l'inventaire avait écartés.
  ⚠️ Il ne tranche pas « A » / « À » : ça se relit.
