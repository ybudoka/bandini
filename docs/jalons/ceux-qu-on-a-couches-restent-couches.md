# Ceux qu'on a couchés restent couchés

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « quand on meurt ou est arrêté lors d'une mission, ceux qu'on a tués sont
resettés ».

- ⚠️ **Mesuré** : m5, quatre Cravates sur six abattus (« 4/6 »), l'hôpital fait rater la
  mission, et la reprise repose les **six** (« 0/6 ») — `poserLesCravates` repartait de la
  fiche à chaque essai. **Et un second défaut par la même porte** : les six du premier
  objectif restent au sol quand le chef sort, et le compte de `tuer` prenait **toutes** les
  cibles de la mission — six corps contre un chef debout, « COUCHE LE CHEF » se validait à
  l'image suivante, **le chef vivant**. **Livré** : l'échec compte ceux qui sont tombés
  **par objectif et par coin** (`B.partie.tombes`, sauvegardé ; K.-O. compte comme mort,
  comme au compteur de l'objectif) ; la reprise ne repose que ce qui manque à chaque coin —
  un coin vidé reste vide —, le compteur repart du « 4/6 » lu, un objectif déjà vidé est
  sauté, et la réussite oublie les essais. Le compte de `tuer` ne prend plus que les cibles
  de **son** objectif (`e.etape`). Juge :
  `test_ceux_qu_on_a_couches_restent_couches_quand_la_mission_rate` (hôpital puis prison
  dans la même partie), rouge sur l'ancien `histoire.js` ; six mutations sur sept le font
  tomber — la septième (couper la pose à `o.n` au lieu du reste) ne change rien tant que les
  Cravates se partagent juste entre les coins (6 en 3), c'est une garde pour un partage
  inégal qu'aucune mission n'a encore.
