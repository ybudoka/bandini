# Le téléphone sonne à la chaîne : un appel à la fois

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026) : « j'ai trop de missions au téléphone une après l'autre, je voudrais que ce soit moins fréquent ».

- ⚠️ **Mesuré avant** : `Histoire.majTelephone` sonne dès qu'une mission disponible n'a pas encore été annoncée, `DELAI_APPEL` (600 images, **10 s**) après le dernier appel ou la dernière mission. Il ne regarde pas si l'appel d'avant a été suivi : avec une dizaine de donneurs, quatre ou cinq missions s'ouvrent ensemble et le combiné sonne toutes les dix secondes.
- **Choix de Martin : un appel à la fois.** Pas de nouvel appel tant qu'une mission annoncée au téléphone attend d'être prise. Filet : si on l'ignore, le téléphone relance (la suivante) après ~3 min de jeu. Et après une mission réussie, ~45 s au lieu de 10 avant la sonnerie.
