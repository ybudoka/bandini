# Le dictionnaire de prononciation en phonèmes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026, après avoir écouté un essai (« Deux piastres. » en eleven_v3, un
dictionnaire jetable d'une seule règle `piastres → pjɑs`) : « ça marche bien, je préfère que tu
y ailles avec ça pour le dictionnaire ». Les 107 règles d'`app/prononciation.pls` passent de
l'**alias** (un mot réécrit comme on l'entend, « piasses ») au **phonème IPA** (`pjɑs`) : on dit
exactement le son, l'affrication de « p'tit » (`ptsɪ`), le « gang » d'ici (`ɡɛŋ`), sans passer par
une orthographe que le modèle relit à sa façon.

Ce que ça coûte : rien à générer (le téléversement est gratuit), mais le fichier ne se relit plus
sans l'IPA — chaque règle garde donc sa lecture en clair (`dit : piasses`), et un juge l'exige.
Toutes les voix qui prennent le dictionnaire sont en eleven_v3 : le phonème que multilingual_v2
ignorerait ne perd rien ici. Les 46 voix à refaire ([la ligne voisine](refaire-les-voix-que-le-dictionnaire-de-prononciation-change.md))
le seront avec les phonèmes.

## Notes

Livré le 22 sept. 2026.

- **L'essai qui a décidé** : « Deux piastres. » dit par Bouchard (eleven_v3), un dictionnaire
  jetable d'une règle `<phoneme>pjɑs</phoneme>` (`jTrjaEwqRbzNGjKunvjU`, « essai phoneme piasses
  (a jeter) », resté sur le compte : l'API ne sait pas l'archiver). 14 caractères — le quota du
  mois était à 17. Martin a écouté : « ça marche bien ».
- **Les 107 règles** d'`app/prononciation.pls` sont des `<phoneme>` en IPA du français d'ici :
  `ʁ` (jamais `r`), `ɡ` (U+0261), voyelles relâchées en syllabe fermée (`fʊl`, `ʃɪft`, `ptsɪt`),
  affrication devant `i` (`ptsɪ`, `tsiɡi`), l'anglais comme on le dit ici (`tʁɔk`, `ɡɛŋ`,
  `dʒɔb`, `ʁɔn`). Aucune marque de longueur ni d'accent : l'essai n'en avait pas.
- **La lecture en clair** reste, en commentaire juste après chaque règle
  (`<!-- dit : piasses -->`) — c'est l'ancien alias. `prononciation.lectures()` la lit,
  `entendu()` rend le texte avec elle, `--dictionnaire` affiche les deux.
- **Juges neufs** (`tests/test_prononciation.py`) : un lexème = grapheme + phonème ; chaque
  phonème n'emploie que l'IPA d'ici (mutation `ɡɛŋ` → `gɛŋ` : rouge) ; chaque règle a sa
  lecture (mutation « dit : piasses » retiré : rouge) ; `interpretation.MODELE` reste
  eleven_v3, le seul qui lise un phonème.
- **Téléversé** : `3sL7rOxQyYL7UGIiT0jz`, 107 règles lues (`app/prononciation.json`).
- ⚠️ **Aucune règle réelle n'a encore été écoutée** en phonème, sauf `piastres` : les 46 voix de
  [la ligne voisine](refaire-les-voix-que-le-dictionnaire-de-prononciation-change.md) (17 oct.)
  seront la première écoute. Une règle qui sonne mal se corrige dans son IPA, ou se retire.
