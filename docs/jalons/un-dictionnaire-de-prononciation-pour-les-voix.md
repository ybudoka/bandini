# Un dictionnaire de prononciation pour les voix

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « crée moi un dictionnaire pour mon jeu » (lien vers les
pronunciation dictionaries d'ElevenLabs). C'est la troisième voie que
docs/ecrire-un-accent.md § 5 laissait fermée : la voix prononce autrement un mot SANS que le
texte affiché ni le jeu= changent — la règle s'applique côté ElevenLabs, le juge mot à mot
ne voit rien. Un lexique PLS dans le dépôt (règles alias : l'orthographe qu'on veut
entendre, comme « tâsse-toi don » que Martin a dicté le 13 sept.) ; le serveur MCP
elevenlabs apprend à téléverser un lexique et à passer pronunciation_dictionary_locators ;
scripts/audio_elevenlabs.py le téléverse quand il a changé (empreinte) et le joint à chaque
voix ; un juge valide le lexique (XML, pas de doublon, chaque mot existe dans une réplique).
Rien n'est régénéré sans l'accord de Martin : le dictionnaire vaut pour la prochaine
génération ou un --refaire.

## Notes

**22 sept. 2026 — le dictionnaire, le branchement, le juge.** La recette est dans
[voix-de-l-histoire.md](../voix-de-l-histoire.md#le-dictionnaire-22-sept-2026).

- `app/prononciation.pls` : **15 règles** (des alias), trouvées en passant les 375 répliques
  dites (31 618 caractères) au correcteur français de macOS, puis en lisant chaque anglicisme,
  québécisme et nom propre dans sa phrase. Le parler d'ici (`donc` → `don` : la dictée de
  Martin du 13 sept. ; `piastres` → `piasses`, `astheure`, `Envoye`, `su'l`, `Skateux`), les
  mots anglais comme on les dit ici (`run`, `full`, `stool`, `smoked meat`), trois noms
  (`Roy` → `Roi`, `Prévost` → `Prévo`, `Ti-Guy` → `Ti-Gui`) et un sigle involontaire (`ET`,
  la majuscule d'insistance de Gus, s'épellerait « E.T. »). ⚠️ **Aucune n'a été écoutée** :
  ce sont les lectures françaises qui diffèrent de celles du Québec, pas des fautes entendues.
  Martin juge à l'oreille ; une règle qui sonne mal se retire.
- Laissés dehors exprès : `job`, `cash`, `boss`, `parking`, `stock` (la lecture française
  est déjà celle d'ici), `gang` (le « gagne » québécois ne s'écrit pas sans ambiguïté),
  `Heille` et `Tâsse-toi` (déjà écrits comme Martin les dit), les autres noms.
- Le serveur MCP `elevenlabs` (hors dépôt, `~/.mcp-servers/elevenlabs/`) a un **8e outil**,
  `elevenlabs_pronunciation_dictionary` (téléverse un `.pls`, rend id et version), et
  `elevenlabs_text_to_speech` prend `pronunciation_dictionaries` (3 au plus). `test_serveur.py`
  vert ; l'ancienne version est à côté, `*.avant-dictionnaire-2026-09-22`.
- `scripts/audio_elevenlabs.py` : `lexique()` téléverse si l'empreinte du `.pls` a changé
  (`app/prononciation.json`), puis le joint à **chaque** voix ; `--dictionnaire` le téléverse et
  liste les voix déjà faites qu'il changerait, avec la commande `--refaire` (payante).
- ⚠️ **Premier téléversement refusé** : 401, la clé n'a pas `pronunciation_dictionaries_write`.
  Le script ne bloque alors que les voix qu'une règle touche (elles seraient à repayer) et
  génère les autres sans dictionnaire. Donc : **ElevenLabs n'a pas encore lu ce `.pls`**.
  C'est le seul point non vérifié.
- Le juge `tests/test_prononciation.py` a mordu tout de suite : un `--` dans un commentaire
  XML (interdit par le format, ElevenLabs l'aurait refusé aussi). Mutations : règle morte,
  doublon, règle qui mord dans `[sighs]` → rouge chaque fois.
- **13 voix déjà générées** disent encore les mots à l'ancienne (1 257 caractères) :
  `taxi_trafic_r`, `pub_gus_r`, `ti_guy-m1-1`, `ti_guy-m1-2`, `bouchard-m4-3`, `ti_guy-m4-8`,
  `josee-m6-5`, `raymonde-s03-1/-2/-5/-6`, `narrateur-ouverture-3/-4`. On attend l'accord de
  Martin pour les refaire.
