# Les juges : moins de doublons, plus de morsure

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demandé par Martin le 27 sept. 2026 (« regarde si tous les tests sont toujours valides et
nécessaires, et si on pourrait en regrouper »). L'audit du 27 sept. (suite complète sur
4f978c23 : 2 669 tests, 8 292 cas, 98 min de CPU, 15 min sur 8 files ; six lecteurs sur les
230 fichiers) : presque tous valides, mais une quinzaine ne mordent pas et une quarantaine
se répètent ; le gros du coût, c'est la ville régénérée sans cache (environ 200 fois) et des
bancs qui refont la même mise en place (environ 150). Vague A — les juges qui ne mordent
pas : test_zz_smoke sans assertion (seul juge des canards), le sentier de parc lu dans le
mauvais repère depuis la bande nord, les assertions tautologiques (or True, or gps,
json.dumps, isascii, le plafond des districts), les règles calculées jamais affirmées (le
feu, la course, la trace, l'empreinte des chars), le PYTHONHASHSEED jugé dans un seul
processus, les répliques hors du paquet que test_accents ne voit plus, la variable morte de
test_version, et le chien de garde du char coincé (rouge). Vague B — une ville partagée
(fixtures de session, cache par graine) et paquet au lieu d'assembler(). Vague C — les
doublons retirés et les bancs fusionnés. Vague D — test_moteur_js découpé par thème, les
petites paires fusionnées, un module commun pour les outils des missions.

- ⚠️ Un juge retiré ou fusionné ne perd aucune règle : chaque retrait nomme le juge qui la
  tient encore.
- ⚠️ Les deux rouges du ciné-parc (test_la_nuit::comptoirs, test_debug_js::portes des blocs)
  restent à la session du cinéma.
