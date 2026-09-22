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
