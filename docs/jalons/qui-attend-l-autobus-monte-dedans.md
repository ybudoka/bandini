# Qui attend l'autobus monte dedans

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

vu le 17 sept. 2026 en livrant la 3e vague des quartiers : le juge
`test_l_autobus_s_arrete_pour_eux_ils_montent_et_descendent_plus_loin` (on attend l'autobus)
**ne tient que par sa graine**. Rejoué sur la base avec `L.graine(1…12)` : **11 graines sur 12
tombent** — « l'autobus est reparti et il reste du monde sur le trottoir », « 2 attendaient,
4 sont montés » (des passants qui n'attendaient pas montent aussi), « l'autobus n'a pas marqué
l'abribus servi », un descendu à 564 px de son arrêt. La 3e vague des quartiers l'a fait tomber
sur sa propre graine en ajoutant vingt-neuf lampadaires (des entités de plus, donc d'autres
dés) ; elle a renoncé aux poteaux, mais la règle reste fausse la plupart du temps.

- ⚠️ À faire : lire chaque défaut sur une graine où il se produit (le chien de garde et le vélo
  qui poussait l'autobus ont été trouvés comme ça), corriger la règle, puis tenir le juge sur
  **plusieurs** graines.

✅ **Livré** (17 sept. 2026). Rejoué graine par graine, **un seul vrai défaut dans le jeu** :
un voyageur bousculé ou effrayé quittait son poste (`fige`) sans perdre sa marque d'attente —
il ne montait plus, l'autobus repartait sans lui, il errait avec, et l'abribus ne faisait naître
personne à sa place (graines 1 et 5). `Autobus.renoncerALAttente` : qui n'est plus à son poste
redevient un passant, et `quiAttend` ne compte que ceux qui y sont.

- ⚠️ **Le reste était le juge.** Il comptait ceux qui attendaient à l'image 40 (d'autres arrivent
  pendant les deux minutes où l'autobus se fait attendre : « 2 attendaient, 4 sont montés ») ;
  il gardait une copie de surface des passagers (un passager dévié à l'arrêt suivant modifiait
  l'objet copié : « (44, 5) ») ; il comptait un mort ; il prenait pour siens les descendus d'un
  autre arrêt (« 564 px ») ; et il comparait « servi » au quart d'heure d'après. Il compte
  maintenant ceux qui attendent **quand l'autobus s'arrête**, les suit par leur identifiant (`qui`,
  sur chaque passager), et tourne sur **six graines**. Sans la règle, il rougit sur les graines 1
  et 5.
