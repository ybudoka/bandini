# La carte sort du paquet

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

décision de Martin (16 sept. 2026), devant l'Île-aux-Corneilles qui faisait passer le paquet
à 75,3 Ko gzip sur 75 : **la carte sort du paquet** plutôt que de relever le plafond une
fois de plus — ce que `test_definitions` écrivait d'avance (« c'est à ce plafond-ci qu'on le
prendra »). **Livré** : `/api/carte` avec son propre ETag (la même revalidation, ETag faible
de nginx compris), deux requêtes **parallèles** au démarrage, et le navigateur remet la
carte dans `defs.carte` — aucun lecteur de la carte n'a changé.

- ⚠️ **Les définitions portent l'empreinte de leur carte** (`carte_empreinte`) : la
  sauvegarde oublie une position quand la VILLE change même si aucun catalogue ne bouge, et
  le navigateur **refuse une carte d'une autre construction** (un déploiement tombé entre
  les deux requêtes) — la page reste au chargement et dit de recharger. Mesuré au
  découpage : définitions **32 975** octets gzip (140 Ko bruts), carte **41 269** (374 Ko
  bruts) ; chacune a son plafond (40 et 48 Ko gzip).
- ⚠️ **Ce que ça n'achète pas** : au premier chargement, le téléphone reçoit à peu près
  autant d'octets qu'avant. Ce que ça achète : un déploiement de catalogues revalide la
  ville par un 304 (et l'inverse), deux `JSON.parse` plus petits, un budget par sujet. Les
  districts chargés autour du joueur restent une dette (« Dettes »). Juges :
  `test_definitions`, `test_routes`, `test_moteur_js` (deux requêtes plus l'ouverture, pas
  une de plus), `test_navigateur` (la carte d'une autre construction).
