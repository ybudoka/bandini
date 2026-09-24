# Le dictionnaire ne garde que ce qui a été écouté

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin a écouté, les 23 et 24 sept. 2026, onze phrases dites sans puis avec le dictionnaire en
phonèmes (`captures/essai-dico/`). Verdict : **sans** vaut mieux pour p'tit, t'sais, j'suis, truck,
brakes, muffler, Coudonc, chum, cheap, Ti-Guy, Roy, Prévost, OK, 10-4, lunch, su'l, full, fun,
party, donc, p't-être, v'là, docker, Skateux, run, smoked meat, stool ; **pareil** pour gang, job,
y'a, ET, Y a ; **avec** pour astheure et piastres. Et « Envoye » doit sonner « envoueille » : de
quatre variantes, c'est l'alias « Anvoueille » qu'il a retenu.

Les voix québécoises d'eleven_v3 disent déjà bien le parler d'ici : une règle qui n'aide pas
nuit. Le lexique ne garde que astheure, piastres (IPA) et Envoye (alias), avec leurs autres formes ;
la réserve des mots jamais dits s'en va. Une règle n'entre plus qu'après une écoute sans/avec.

## Notes

Livré le 24 sept. 2026.

- **Les deux écoutes** (`captures/essai-dico/`, hors dépôt) : le 23, huit phrases sans/avec les
  107 règles en phonèmes (742 caractères) ; le 24, cinq « Envoye, fonce! » (sans, alias
  « Envoueille », alias « Anvoueille », IPA `ɑ̃vwɛːj`, IPA `ɑ̃ˈvwɛj`) et trois phrases de plus
  sans/avec (≈ 380 caractères). Les dictionnaires jetables de ces essais restent sur le compte
  ElevenLabs : l'API ne sait pas les archiver.
- **Le lexique** : 6 règles — `piastres`, `astheure`, `Astheure` en IPA (`pjɑs`, `astœʁ`),
  `Envoye` en alias (« Anvoueille ») ; en réserve, `piastre` et `envoye`. Les 101 autres sont
  parties (git les garde, 499168f et a012d5e). Téléversé : `jwZzc3f7cYRTspC4ZnfB`.
- **Phonème OU alias** : `prononciation.py` lit l'un ou l'autre (`GENRES`, `phonemes()`) ;
  `--dictionnaire` affiche `/pjɑs/` pour un phonème, `alias « … »` pour un alias.
- **Juges** : un lexème porte un grapheme puis UN son (mutation « alias + phonème » : rouge) ;
  l'IPA d'ici pour les phonèmes seulement ; hors réserve, le commentaire d'une règle dit
  « Écouté le … » (mutation : rouge).
- **Les voix à refaire** passent de 46 à **12** (1 071 caractères) :
  [la ligne voisine](refaire-les-voix-que-le-dictionnaire-de-prononciation-change.md).
