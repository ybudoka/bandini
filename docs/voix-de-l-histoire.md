# Bandini — les voix de l'histoire

← [le plan](plan.md), qui ne garde que ce qui reste à faire

## Les voix de l'histoire (décision du 13 sept. 2026)

Le jeu **parle**. Chaque réplique de l'histoire est écrite dans `missions.py` (le texte,
source unique) et **dite** par une voix ElevenLabs générée une fois, comme les répliques
des passants. Ce que ça implique, jalon par jalon :

- **On se présente une fois par mission** (21 sept. 2026, demande de Martin) : la première fois qu'on
  entend quelqu'un dans une mission — l'appel, le plus souvent — il dit son nom, dans **sa** salutation, et
  plus jamais ensuite dans la mission — voir `docs/jeu-d-acteur.md` § 3.11 et les fiches des personnages,
  [docs/personnages/](personnages/README.md).
- **Une voix par personnage**, nommée dans `audio.VOIX_PERSONNAGES`. Martin a ajouté des
  voix québécoises à son compte le 13 sept. ; distribution proposée : Ti-Guy = _Felix
  Tabarnak_ (l'homme de tous les jours), Sgt Bouchard = _Khaivan_ (accent bien dialectal),
  Mme Thibodeau = _Julia_ (courtoise, chaleureuse), Josée « La Chef » = _Jeanne Mance_,
  Dr Lachance = _Patrick_ (clair, ancien journaliste), Marco « Le Cousin » = _Québec
  Tremblay_, le narrateur du Clairon = _annonceur centre d'achat 1_ (vieil homme qui
  soupire), les passants = _Felix_ et _Amélie_ (déjà en place). Une ligne à changer par
  personnage.
- **La réplique est la source** : `missions.py` porte `{"qui": "ti_guy", "texte": "…"}` ;
  le slug du fichier se déduit (`voix-ti_guy-m1-03.mp3`), la recette est donc le texte
  lui-même. `scripts/audio_elevenlabs.py --voix` génère ce qui manque, au caractère (≈ 40
  répliques × 80 caractères : quelques milliers de caractères, rien).
- **Le texte reste affiché** dans la boîte de dialogue (lisibilité, jeu en sourdine,
  tactile) ; la voix **s'ajoute**, elle ne remplace pas. Une réplique dont le fichier
  manque s'affiche sans voix — le filet, comme pour les bruitages.
- **Une seule voix à la fois** : une réplique coupe la précédente ; la radio et l'ambiance
  baissent pendant qu'on parle (_ducking_), puis remontent.
- **Le téléphone** : la voix vient « du combiné » (filtre passe-bande, un peu de grésil) ;
  le journal du matin est lu par le narrateur, en plus de la manchette.
- **Un test navigateur** prouve que chaque voix se décode ; un test Python que chaque
  réplique a un personnage connu et tient en une phrase ou deux.
- **Le repos parle aussi** (20 sept. 2026, demande de Martin : « fais parler les personnages ») :
  quand aucune mission n'attend quelqu'un, chacun des **huit** personnages qu'on peut alors
  aborder dit `REPOS` — « reviens me voir plus tard » avant M5, « le Faubourg est tranquille »
  après — de sa voix et dans son ton : `<qui>-repos-1` et `-2`, chargées d'un coup par
  `Son.Voix.chargerHistoire('repos')`, jeu dans `interpretation.py`. **15 fichiers** (≈ 650
  caractères) : Ti-Guy s'en va après m1 (tant qu'il est là, il a m1 à donner) et Josée ouvre le
  marché noir après M5 au lieu de dire son repos — on ne paie pas ce qui ne s'entend pas. Le
  texte reste dans la boîte (`missions.REPOS`, source unique), et une boîte dont le mp3 manque
  s'affiche sans voix.

## Le dictionnaire (22 sept. 2026)

Demande de Martin : « crée moi un dictionnaire pour mon jeu » — les
[pronunciation dictionaries](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices#pronunciation-dictionaries)
d'ElevenLabs. Un mot que la voix dit mal se corrige **sans toucher au texte** : la boîte
affiche « Prenez donc la rue », la voix dit « Prenez don la rue ».

- **Les règles** vivent dans [`app/prononciation.pls`](../app/prononciation.pls) (format W3C
  PLS, celui qu'ElevenLabs lit) : un `<grapheme>` (le mot tel qu'on l'écrit), un `<phoneme>`
  (le son qu'on veut entendre, en IPA : `pjɑs`) et, juste après, sa **lecture en clair**
  (`<!-- dit : piasses -->`). Un commentaire au-dessus de chaque règle dit pourquoi elle est là.
- **Ajouter une règle** : un `<lexeme>` de plus dans le `.pls`. ⚠️ Sensible à la **casse**
  (« Astheure » en tête de phrase est une deuxième règle), un mot **entier** seulement, et
  seule la **première** règle qui colle s'applique. Pas de `--` dans un commentaire XML (le
  format l'interdit). `tests/test_prononciation.py` refuse un lexique illisible, une règle en
  double, une règle morte (son mot n'est plus dans aucune réplique) et une règle qui mordrait
  dans une balise de jeu.
- **Deux parties** : au-dessus du commentaire `EN RÉSERVE`, chaque règle touche une réplique qu'on
  entend déjà (le juge l'exige : une faute de frappe dans le mot ne corrigerait rien, en silence) ;
  en dessous, **la réserve** — les mots que les prochaines missions diront sans doute (l'anglais du
  garage et de la rue, les contractions, les noms pas encore dits, `OK`, `Mme`, `10-4`). Une
  réplique neuve qui dit « brakes » est donc déjà prononcée « brèques » (`bʁek`). Un mot neuf qui sonne mal :
  sa règle va dans la réserve, ou au-dessus si une réplique le dit déjà.
- **L'ordre compte** : une règle longue passe avant la courte qu'elle contient (« Ti-Guy » avant
  « Guy »), le juge y veille.
- **Des phonèmes, plus des alias** (Martin, 22 sept. 2026, après un essai « Deux piastres. » →
  `pjɑs` en v3 : « ça marche bien, je préfère que tu y ailles avec ça ») : le phonème dit le son
  exact — l'affrication de « p'tit » (`ptsɪ`), le « gang » d'ici (`ɡɛŋ`) — là où l'alias passait
  par une orthographe que le modèle relisait à sa façon. ⚠️ Il **dépend du modèle** : eleven_v3 le
  lit, multilingual_v2 l'ignore en silence (un juge tient `interpretation.MODELE` à v3). Écrire
  l'IPA d'ici : `ʁ` (jamais `r`), `ɡ` (U+0261, jamais le `g` du clavier), les voyelles relâchées
  des syllabes fermées (`fʊl`, `ʃɪft`), `ts`/`dz` devant `i` et `y` ; le juge refuse un caractère
  hors de l'IPA qu'on emploie, et une règle sans sa lecture « dit : ».
- **Le téléversement** est automatique et gratuit : `scripts/audio_elevenlabs.py` compare
  l'empreinte du `.pls` à `app/prononciation.json` et en téléverse un neuf s'il a changé
  (chaque téléversement crée un nouveau dictionnaire chez ElevenLabs — committer le `.json`
  pour que les autres sessions réutilisent le même). Puis il le joint à **chaque** voix
  générée (`pronunciation_dictionary_locators`).
- **Rien ne se régénère tout seul** : une règle vaut pour la prochaine voix générée.

```bash
uv run python scripts/audio_elevenlabs.py --dictionnaire   # téléverser s'il a changé, et les voix déjà faites qu'il changerait (gratuit)
```

La commande finit par le `--refaire` qui referait ces voix-là (**payant**, au caractère).

⚠️ **La clé ElevenLabs doit avoir la permission `pronunciation_dictionaries_write`** (et
`_read`) — Martin l'a ajoutée le 22 sept. 2026. Sans elle, le script génère encore les voix
qu'aucune règle ne touche, et refuse les autres plutôt que de les faire payer deux fois.

⚠️ **v3 applique bien le dictionnaire** (vérifié le 22 sept. 2026 : une règle jetable `truck` →
« banane », et la reconnaissance vocale a entendu « le banane »). Mais la reconnaissance vocale
ne sait pas juger une règle réaliste : elle ramène « piasses » à « piastres ». **Seule l'oreille
juge.**

