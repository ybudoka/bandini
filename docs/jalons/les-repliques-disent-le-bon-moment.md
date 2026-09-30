# Les répliques disent le bon moment

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Suite de [la radio dit le temps qu'il fait](la-radio-dit-le-temps-qu-il-fait.md) (Martin, 30 sept. 2026 : « les
deux »). Trois répliques mentent encore, cette fois sur l'heure et sur le froid : La Brume annonce « Il est minuit
passé sur le port » en plein midi, et le passant (`frette_h`) comme la fille de la Brume (`frette_b`) lancent
« Fait frette, hein? » en pleine canicule.

Correctif : une réplique peut porter `froid` (elle ne se dit que quand les passants ont au moins une veste,
`Saisons.palette().froid` ≥ `habits.frais`) ou `heures` (elle ne se dit qu'entre ces heures-là). Un seul garde,
`Son.Voix.deSaison`, sert aux trois endroits où l'on choisit une réplique : le tirage des passants, le choix de la
fille de la Brume et le tour de rôle des ondes. Aucun dé de plus. La Brume reçoit une réplique neutre neuve pour ne
pas tourner sur une seule en plein jour.

## Notes

Livré le 30 sept. 2026. `Son.Voix.deSaison` est un filtre, pas un dé : qui tire tire une fois,
quelle que soit la liste. `froid` (`frette_h`, `frette_b`) ne passe que quand `Saisons.palette().froid`
atteint `habits.frais`, le seuil de la veste. `heures` [de, a) : `brume_nuit_r` entre 0 h et 5 h. Le
garde sert à `Voix.dire` (le tirage des passants, quand aucune réplique n'est imposée), à
`Voix.choisir` (la fille de la Brume) et à `Ondes.convient` (le tour de rôle des stations).

Réplique neutre neuve : `brume_port_r`, « La Brume, cent trois virgule sept. De la musique douce, pis
personne qui crie dans le micro. » Sans elle, La Brume n'aurait eu qu'une réplique un midi de beau
temps.

⚠️ **Les voix des stations arrivent avec la radio.** `brume_port_r`, neutre, serait partie au premier
écran, qui n'avait plus que 6 Ko de marge. Les animateurs et les pubs ne servent qu'une station
allumée : `voix_a_la_volee` les met à part. `Voix.charger` les saute, et `Voix.chargerOndes` les
demande quand la première station qui parle s'allume, vingt secondes avant la première voix. Environ
515 Ko de moins au démarrage. La police reste au démarrage : elle parle sans prévenir.

Juges (`tests/test_repliques_du_moment.py`) :

- une réplique qui dit « fait frette » porte `froid`, une qui dit minuit ou midi porte `heures` ;
- à chaque heure et sous chaque ciel, chaque animateur garde deux répliques ;
- au banc avec les mp3, l'été, aucun « frette » ne sort de `Voix.dire` ni de `Voix.choisir`, et au
  grand froid, les deux sortent ;
- La Brume ne dit « minuit passé » qu'à deux heures du matin, et elle le dit.

Le garde a été retiré tour à tour de chacun de ses trois branchements : chaque fois, un juge rougit.

Dans `tests/test_ondes.py`, `test_les_voix_des_stations_arrivent_avec_la_radio` compte les vraies
requêtes : aucune voix de station au démarrage, toutes les neutres à l'allumage, aucune d'un ciel, et
rien de plus au changement de station. Il rougit dans les deux sens (voix remises au démarrage, radio
qui ne les demande plus).
