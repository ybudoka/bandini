# Bandini — les voix de l'histoire

← [le plan](plan.md), qui ne garde que ce qui reste à faire

## Les voix de l'histoire (décision du 13 sept. 2026)

Le jeu **parle**. Chaque réplique de l'histoire est écrite dans `missions.py` (le texte,
source unique) et **dite** par une voix ElevenLabs générée une fois, comme les répliques
des passants. Ce que ça implique, jalon par jalon :

- **Qui parle se nomme** (21 sept. 2026, demande de Martin) : au téléphone et à la première rencontre,
  la première réplique dit le nom de celui qui parle, dans **sa** salutation — voir `docs/jeu-d-acteur.md`
  § 3.11 et les fiches des personnages, [docs/personnages/](personnages/README.md).
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
