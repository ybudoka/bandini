# Douze juges rouges sur dev, avant la prod

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

La suite complète sur `407de5d2` (le SHA qu'on voulait mettre en prod) a douze rouges, qui
tombent aussi seuls, sans la charge. Huit dans `test_devants`
(`test_aucun_abribus_ne_colle_la_porte_d_un_lieu_de_mission`,
`test_le_temoin_a_bien_des_abribus_colles` : `KeyError: 4`), venus des commits d'après
`442e6ffb` ; `test_donneurs_visibles_js` (Cindy « pas là ») rouge déjà sur `0bdabaa1` ; et
trois des deux-roues remisés (`442e6ffb`) mêlés au train et au dojo : le clignotant rouge la
nuit et le public des amuseurs (des juges qui tiennent à l'état de la rue de janvier) et
deux autobus dans la même boîte (`test_trafic_js[23]`, seule graine sur trente, seulement
sur le build — à tracer). Chaque rouge : sa cause, puis sa correction ou son juge recalé,
puis la suite complète sur le SHA exact, puis la prod.
