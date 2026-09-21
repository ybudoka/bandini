# Cinq missions de plus, dans la lignée de m50

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

demande de Martin (21 sept. 2026) : « crée-moi 5 nouvelles missions dans la lignée ».

_Ce que ça donne :_ cinq missions écrites à la main, chacune avec ses objectifs, ses répliques à
chaque temps, ses scènes et le jeu de chaque voix — le catalogue passe de huit à treize. Elles
suivent **m50** (_Le Cargo de Minuit_) : une faveur du Faubourg, un donneur qui parle québécois, un
lieu qu'on connaît, et rien qui demande un moteur neuf.

⚠️ **Deux règles ont décidé du choix** :

- **Que des donneurs qui existent** (Marco, Ti-Paul, Lulu, Raymonde, Bouchard) : aucune voix à
  auditionner, aucun personnage à poser (`docs/carte.md` ne bouge pas), et deux personnages de
  même voix ne se croisent pas (Marco et Ti-Paul partagent « Québec Tremblay » : jamais dans le
  même dialogue).
- **Que des types d'objectifs éprouvés** : `aller`, `monter`, `livrer`, `tuer`, `semer`, `parler`,
  `retourner`. Les neuf types de M16 (`suivre`, `proteger`, `pickpocket`…) attendent encore leur
  juge de banc, et `course` n'est pas joué en mission : une mission qui s'en sert avant n'est pas
  finie. C'est pourquoi la moitié de l'arc F du plan (`f06`, `f07`, `f09`) n'est pas dans ce lot.

| Slug | Titre | Donneur | Après | Ce qu'on fait |
|---|---|---|---|---|
| `f01` | Les Cravates reviennent | Marco | m50 | de nuit au garage : repousser trois Cravates qui arrivent de loin, coucher leur chef, revenir |
| `e01` | Les drifts de Ti-Paul | Ti-Paul | m6 | de nuit au dépanneur : trois Chevreuils, les poings nus, qui viennent se servir en bière |
| `q02` | Le poisson du vendredi | Lulu | e01 | le camion de poisson dort dans une ruelle des Quais : le livrer au casse-croûte, sans bosse |
| `s03` | La paie de la Prévost | Raymonde | q02 | voler le camion de paie derrière l'hôtel, semer 2★, le livrer au syndicat |
| `m51` | La tournée du sergent | Bouchard | e01, q02 | serrer la main de trois commerçants (Thibodeau, Lulu, Ti-Paul) pour « la cotisation », rapporter les enveloppes |

⚠️ **Les prérequis font une chaîne exprès.** Le téléphone sonne pour la première mission
disponible dont l'appel n'a pas été dit, toutes les dix secondes (`DELAI_APPEL`) : cinq missions
ouvertes d'un coup à la fin de m6, c'est cinq appels de suite. Elles s'ouvrent donc dans l'ordre où
m6 présente les gens (Ti-Paul, Lulu, Raymonde), et Marco a sa suite de m50. Le « un appel par
demi-journée » de M16 les trierait mieux ; il n'est pas livré.

⚠️ **Les slugs suivent le plan de M16** quand la mission y est (`e01`, `q02`, `s03`, `f01`), avec
ce qui change : `f01` est donnée par Marco au garage (Ti-Guy n'a plus de place après m1) et n'a pas
d'extincteur (`eteindre` attend son juge) ; `q02` livre un camion, pas trois ; `s03` n'a pas de
gardiens. `m51` n'est pas au plan : c'est un nom hors catalogue, comme m50.

⚠️ **Les voix ne sont pas générées** : ElevenLabs se paie au caractère, et Martin n'a pas encore
écouté un ton neuf. Chaque réplique a son jeu dans `app/interpretation.py` (un juge l'exige) ; une
réplique dont le fichier manque s'affiche sans voix. La commande est dans les Notes.

## Notes
