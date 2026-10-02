# Reprendre un acte sans redire la fin d'avant

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (3 oct. 2026)_ : « il y a plusieurs problèmes avec quel dialogue qui se lit et par qui et pour
quelle mission » — au téléphone et en parlant à quelqu'un, un peu partout. Sa capture : devant Chez Gus, à l'acte 2
du _Garage de Rocco_, il appuie sur E pour parler à Gus, et c'est **Josée, au téléphone**, qui répond — « Pis il a
déchiré deux pages de ton casier en passant », la fin de l'acte 1, déjà dite au Brouillard.

**La cause.** Le marqueur d'un acte (`acte`) dit, à son ouverture, ses répliques `pendant` : d'abord la FIN de l'acte
d'avant (la fin de la mission que cet acte remplaçait, dite par son donneur), puis l'appel et l'intro du donneur du
nouvel acte. Enchaîné, c'est juste : on vient de finir l'acte 1 devant Josée. Mais un chapitre REPRIS à un acte —
REPRENDRE L'ACTE après l'hôpital ou le poste, ou PLUS TARD puis le donneur de l'acte au téléphone ou à sa porte —
rejoue le marqueur en entier : le donneur d'avant redit sa fin, au combiné puisqu'il n'est pas là, et paie une
deuxième fois en paroles ce qui a été payé. Une centaine de ces lignes dans les chapitres (Sal redit « Tiens, pour
le taxi », Louise « pour l'essence »…).

**Ce qui a été vérifié avant** (pour qu'on ne le recherche pas) : les 1 632 voix ont une durée qui suit leur texte ;
les 756 mp3 renommés par les chapitres portent la réplique qu'ils disaient avant (deux écarts voulus : un nom coupé,
et la voix de Bilodeau dit encore « cinquante piastres » quand la boîte dit « deux ») ; chaque réplique d'acte
tombe à l'étape où elle se disait dans sa mission d'origine.

**Le correctif.** Les répliques qui ferment l'acte d'avant portent `cloture=True` (`_p(…, cloture=True)` ; aucun slug
de voix ne bouge). `Chapitres.ouvrirActe` retient si l'acte s'ENCHAÎNE (l'acte d'avant s'est joué ici) ou s'il est
REPRIS ; repris, le marqueur ne dit pas ses répliques `cloture`.

**Juges** : une reprise à l'acte 2 ne dit que ce que dit le donneur de l'acte 2 ; enchaîné, la fin de l'acte 1 se dit
toujours ; et chaque fin d'une mission remplacée, quand elle est dite au marqueur de l'acte suivant, porte `cloture`.

## Notes

Livré le 3 oct. 2026.

- **Les données.** `_p(…, cloture=True)` sur les 110 répliques qui ferment un acte, dans 30 chapitres — retrouvées en
  comparant chaque réplique de marqueur à la `fin` de la mission que l'acte d'avant remplaçait (les instantanés
  d'avant chaque commit de chapitre). Aucune voix ne change de nom : le slug ne compte que la place de la réplique.
- **Le moteur.** `Chapitres.ouvrirActe` pose `mission.enchaine` (l'acte d'avant s'est ouvert ici :
  `acteOuvert === k - 1`) ; `Histoire.maj` ne dit une `cloture` qu'enchaînée. Une reprise — REPRENDRE L'ACTE, ou
  PLUS TARD puis le donneur de l'acte — repart d'une mission neuve, sans `acteOuvert` : elle se tait.
- **Les juges.** Au banc (`test_chapitres_js.py`) : enchaîné, la fin de l'acte 1 se dit ; repris plus tard, ou après
  l'hôpital, seul le donneur de l'acte 2 parle — les deux rougissaient avant le correctif, avec la réplique de
  M. Bilodeau. En Python (`erreurs_de_chapitre`) : au marqueur d'un acte, une réplique du donneur d'avant (quand ce
  n'est pas aussi celui de cet acte) porte `cloture`, une `cloture` ne se dit qu'au marqueur d'un acte suivant, et
  en premier ; retirer celle de Josée fait rougir le catalogue.
- **Reste, hors de ce jalon** : la voix de M. Bilodeau dit « cinquante piastres » quand sa boîte dit « deux »
  (`bilodeau-la_pointe-3`, le péage changé après la prise).
