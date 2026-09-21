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
