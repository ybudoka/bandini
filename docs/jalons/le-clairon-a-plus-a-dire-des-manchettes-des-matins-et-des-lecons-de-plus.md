# Le Clairon a plus à dire : des manchettes, des matins et des leçons de plus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « ajoute des voix du narrateur » — toutes ses répliques ont déjà
leur voix (95 sur 95) ; il a choisi « plus de manchettes » pour que le Clairon se répète
moins. Trois manchettes neuves sur des statistiques déjà comptées et jamais lues (un
dépanneur braqué, une arrestation, un bateau volé), glissées à leur rang de gravité et
gardées dans l'instantané de la veille (`p.journal`) — sinon elles passeraient tous les
matins ; une dizaine de matins calmes de plus, sans saison (la partie commence en janvier) ;
six leçons de plus sur ce que le jeu fait déjà et n'explique pas, chacune vérifiée dans le
code avant d'être écrite. Chaque texte a son `lu`, son jeu v3 dans `interpretation.JEU` et
sa voix ElevenLabs (le narrateur, passé à l'isolateur).

- ⚠️ `REGLES[0]` et `REGLES[1]` restent `nuit_rouge` et `un_mort` (`test_ondes`), et le
  poids de la suite du paquet se juge avant d'atterrir.

## Notes

**Livré le 30 sept. 2026** — dix-neuf textes de plus pour le narrateur, chacun avec sa voix (19 mp3,
2 375 caractères ElevenLabs, séchés à l'isolateur par `--voix` lui-même).

- **Trois manchettes** (`journal.REGLES`), à leur rang de gravité : `un_braquage` (après `un_mort`),
  `une_arrestation` (après `un_blesse`), `un_bateau_vole` (entre `vague_de_vols` et `un_char_vole`). Elles
  lisent `braquages`, `arrestations` et `bateauxVoles`, que le jeu comptait sans que personne les lise.
- **L'instantané de la veille les garde** (`p.journal`, `Missions.manchetteDuJour`) : sans lui, un seul
  braquage ferait la une tous les matins suivants. ⚠️ Et une clé que l'instantané ne connaît pas compte
  **zéro** ce matin-là : une partie commencée avant n'imprime pas d'un coup ses sept braquages. Le premier
  matin d'une partie neuve (`p.journal` absent) compte tout, ses statistiques partent de zéro.
- **Dix matins calmes** (`journal.MATINS`, 7 → 17), sans saison : le traversier à l'heure, le bingo, le chat
  du dépanneur, l'horloge de l'hôtel de ville, l'autre rive, le casse-croûte, les cloches, les mots croisés,
  le facteur, la même toune à la radio.
- **Six leçons** (`journal.LECONS`, 6 → 12), vérifiées dans le code : dormir à la planque (sauvegarde, toute la
  vie), la coupe de couleur chez le barbier (12 $, la recherche à zéro), le 6/49 (2 $ chez Ti-Paul, tirage la
  nuit), le camion d'asphalte devant la fourrière, Me Desjardins au Brouillard (une page par jour), et les
  photos de Louise, en dernier — elle n'arrive qu'avec l'histoire.
- La radio en profite : le bulletin lit les mêmes voix (`ONDES`), il a treize unes de plus à dire.
- ⚠️ **Le paquet débordait** : `dev` était déjà à 240 119 octets bruts pour un plafond de 240 000, et dix-neuf
  noms de plus le portaient à 240 169. Plutôt que relever le plafond (choix de Martin), **les voix du Clairon et
  des Galeries suivent leurs textes dans la suite du paquet** : les séries du journal, du 6/49, de Louise et des
  Galeries voyagent sous `voix_de_la_suite` (`audio.series_de_la_suite`, `definitions.DANS_LA_SUITE`), et
  `Son.Voix.histoire()` les déplie à leur arrivée. Définitions 240 119 → 238 387 bruts (54 290 → 53 744 gzip) ;
  la suite 10 562 → 17 635 (4 884 → 7 455 gzip), son plafond relevé à 19 500 / 8 500 avec la raison écrite.
  ⚠️ Le piège : `chargerHistoire('journal')` appelé avant la suite marquait la banque chargée, vide, pour
  toujours — une banque vide ne se marque plus (`test_les_voix_du_clairon_arrivent_avec_la_suite`, vu rouge
  sans la garde).
- Juge : `test_un_braquage_une_arrestation_un_bateau_font_la_une_sans_ressortir_le_passe` — vu rouge sans la
  garde (la vieille partie fait la une de son passé) et sans l'instantané (la manchette ne passe jamais).
