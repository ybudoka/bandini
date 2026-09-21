# Les gens se présentent — une fois par mission, et l'oncle Rocco

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Deux corrections de Martin sur « Les gens se présentent » (livré le même jour). 1)
« finalement les personnes doivent se présenter seulement une fois par mission » : la
première livraison les nommait une fois par CONVERSATION — Josée disait son nom à l'appel,
au pendant, à la fin et à l'échec de m5. On garde la présentation la première fois qu'on
entend quelqu'un dans la mission (l'appel, ou l'intro quand il n'y a pas d'appel, ou la
poignée de main), et on rend aux autres répliques leur texte d'avant — 25 répliques, dont
les mp3 d'avant sont dans git : aucune voix à repayer. Le juge passe de « l'appel, l'échec
et la fin au combiné se nomment » à « on se nomme une fois par mission, pas deux ». 2)
« l'oncle Rocco » (réponse à la question laissée dans `docs/personnages/rocco.md`) :
l'ouverture a raison, le joueur est son NEVEU ; Ti-Guy dit « le cousin de Rocco » deux fois
à m1 et sa bulle dit « Hé! Le cousin! » — trois textes à corriger, deux voix à regénérer.

- ⚠️ Et un piège trouvé en chemin : `audio_elevenlabs.py --refaire … --masters` écrit la
  nouvelle voix en `<slug>-2.mp3` (le serveur n'écrase jamais) alors que `--refinir` relit
  `<slug>.mp3` — l'ANCIENNE phrase ; le master payé doit prendre le nom qu'on relit.

## Notes

⚠️ **Livré le 21 sept. 2026, le soir même de « Les gens se présentent »** (voir
[son fichier](les-gens-se-presentent-salutations-et-fiches-des-personnages.md#notes)).

**Une fois par mission**

- **25 répliques reprennent leur texte d'avant** — celles qui redisaient le nom de quelqu'un déjà entendu
  dans la mission : les **treize échecs**, les **sept fins au combiné** (m4, m5, m6, q02, s03, m51, m97), les `pendant` de Ti-Guy (m1), Josée (m5), Lulu (q02), Raymonde (s03) et Bouchard (m51). Leurs
  **mp3 d'avant** reviennent tels quels (`git show fbf75d2:static/audio/…`) : texte et jeu identiques, rien à
  repayer. Les **13 présentations** restent : l'appel de m3, m4, m5, m50, q02, s03, m51, Ti-Guy au terminus,
  les quatre poignées de main de m6 et celle de Lulu à m50. Chaque personnage se nomme maintenant
  **exactement une fois** dans chaque mission où il parle au téléphone ou pour la première fois (compté par le
  juge sur les treize missions).
- **Le juge** : `erreurs_de_mise_en_scene` ne demande plus que l'échec et la fin au combiné se nomment ; il
  demande que **l'appel** se nomme et que **personne ne se nomme deux fois** dans une mission
  (`dans_l_ordre_ou_on_les_entend` + `se_nomme`). `test_on_se_presente_une_fois_par_mission` remplace
  `test_qui_parle_au_combine_se_nomme` ; il rougit quand on neutralise la règle (mutation faite, puis
  défaite). Le squelette de `verifier_missions.py` ne nomme plus à l'échec ; `_fiche` non plus.
- **La doc** : `jeu-d-acteur.md` § 3.11 (la règle en quatre temps réécrite, deux formes retirées — « C'est
  encore X! » et « C'est pas X qui t'appelle, OK? » supposaient un deuxième nom), § 3.7 et la liste de
  contrôle ; `comment-monter-les-missions.md`, `missions-en-scene.md`, `ecrire-drole.md` (règle 7),
  `voix-de-l-histoire.md` ; l'index des personnages et les tables de salutation de sept fiches (la ligne
  « plus tard dans la mission » : sans nom).

**L'oncle Rocco**

- Martin a tranché la question laissée dans `docs/personnages/rocco.md` : **l'oncle**. Ti-Guy dit maintenant
  « Heille, le **neveu** de Rocco! » et « T'es ben le **neveu** de Rocco. » (m1, deux voix régénérées,
  ≈ 170 caractères), et sa bulle « Hé! Le neveu! ». « Rocco est parti se faire oublier » reste : c'est sa
  façon de ne pas dire « mort ». Les fiches de Rocco, Ti-Guy et Marco, et l'index, le disent.

**Les masters (le piège trouvé en chemin)**

- ⚠️ `scripts/audio_elevenlabs.py --refaire … --masters DOSSIER` : le serveur n'écrase jamais, il écrivait la
  nouvelle voix en `<slug>-2.mp3` (et `-2-sec.wav`) — et `--refinir` relisait `<slug>.mp3`, **l'ancienne
  phrase**, qu'il aurait finie comme si c'était la nouvelle, sans rien dire. Corrigé : `ranger_master` donne
  au master payé le nom que `--refinir` relit, et garde l'ancien à côté (`<slug>-avant-<date>.mp3`). Essayé
  sur les deux voix du neveu : `histoire-ti_guy-m1-1.mp3` est la neuve, `…-avant-2026-09-21-185749.mp3`
  l'ancienne.
- Le dossier `~/elevenlabs-audio/bandini-voix-v3-masters-2026-09-16` remis d'aplomb à la main, **par
  renommage seulement** (39) : les six appels gardés reprennent le nom de base (l'ancien en `-avant-…`) ; les
  répliques rendues dont le master du jour avait pris le nom de base le cèdent (`-nomme-2026-09-21`), pour
  que `--refinir` dise « pas de master » plutôt que de finir la mauvaise phrase ; les `-2` orphelins portent
  le même suffixe.

**La suite complète** (7 groupes en parallèle, puis `test_navigateur.py` seul, `BANDINI_TESTS_OBLIGATOIRES=1`) :
3 858 verts, 4 `xfail`, 14 sautés ; 4 rouges — les deux **d'avant** (`test_la_foule_ne_se_traverse_plus`,
`test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`, rouges aussi sur `fbf75d2`) et
deux du navigateur sous charge (`test_une_carte_d_une_autre_construction_est_refusee`,
`test_jouer_puis_marcher_au_clavier` : un délai de 15 s, un pas trop court), **verts rejoués seuls**.
`test_le_paquet_reste_leger` reste rouge d'avant (plafond de 44 000 octets gzip, à Martin).
