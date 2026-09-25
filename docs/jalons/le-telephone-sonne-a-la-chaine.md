# Le téléphone sonne à la chaîne : un appel à la fois

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026) : « j'ai trop de missions au téléphone une après l'autre, je voudrais que ce soit moins fréquent ».

- ⚠️ **Mesuré avant** : `Histoire.majTelephone` sonne dès qu'une mission disponible n'a pas encore été annoncée, `DELAI_APPEL` (600 images, **10 s**) après le dernier appel ou la dernière mission. Il ne regarde pas si l'appel d'avant a été suivi : avec une dizaine de donneurs, quatre ou cinq missions s'ouvrent ensemble et le combiné sonne toutes les dix secondes.
- **Choix de Martin : un appel à la fois.** Pas de nouvel appel tant qu'une mission annoncée au téléphone attend d'être prise. Filet : si on l'ignore, le téléphone relance (la suivante) après ~3 min de jeu. Et après une mission réussie, ~45 s au lieu de 10 avant la sonnerie.

## Notes

Livré le 25 sept. 2026, dans `Histoire.majTelephone` (`static/js/histoire.js`).

- **Un appel à la fois** : si une mission annoncée au téléphone est encore disponible (ni prise ni faite), la sonnerie suivante attend `DELAI_RELANCE` (10 800 images, **3 min**). Sinon, `DELAI_APPEL` passe de 10 s à **45 s** (2 700 images). Rien de neuf dans la sauvegarde : « annoncée et en attente » se lit déjà dans `p.appels` et `disponibles()`.
- ⚠️ **L'échéance repart de zéro pendant une mission** (`p.appelT = null`) : sans ça, une mission ratée laissait une sonnerie déjà due, qui tombait à la seconde de l'échec.
- ⚠️ **`appelT` est sauvegardé, `B.t` repart de zéro au chargement** : une échéance plus loin que `DELAI_RELANCE` vient d'une autre session et se recalcule.
- Juge `test_un_appel_a_la_fois` (`tests/test_histoire_js.py`) : il cherche le premier moment où deux missions s'annoncent, décroche le premier appel sans bouger et mesure l'écart avec le deuxième (entre 3 min et 3 min 3 s). **Il mord** : avec l'ancien délai partout, il rougit à 2 722 images. Les deux juges du premier appel après M1 attendent maintenant 45 s.
