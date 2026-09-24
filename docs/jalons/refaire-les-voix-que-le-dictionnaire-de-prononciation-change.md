# Refaire les voix que le dictionnaire de prononciation change

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Le dictionnaire (app/prononciation.pls) ne vaut que pour les voix générées APRÈS lui. Depuis
l'écoute du 24 sept. 2026, il n'a plus que 6 règles (piastres, astheure, Envoye et leurs formes) :
**12 voix** déjà faites les disent encore sans lui (1 071 caractères — les piastres du narrateur
et de Bouchard, les astheure, l'« Envoye » de Xavier), et non plus 46.
`uv run python scripts/audio_elevenlabs.py --dictionnaire` en donne la liste à jour et la
commande --refaire (payante, avec --masters pour garder les masters). Quota : palier Creator
depuis le 23 sept. 2026, 121 007 crédits par mois, remise le 23. Après la génération : écouter,
et lancer test_aucune_voix_de_scene_n_est_coupee_par_la_suivante (une voix plus longue peut se
faire couper par sa scène).

## Notes

Livré le 24 sept. 2026, sur le oui de Martin.

- **12 voix refaites** avec le dictionnaire de 6 règles (`jwZzc3f7cYRTspC4ZnfB`) : ti_guy-m1-2,
  josee-m6-5, bouchard-f06-3, -4, -7, xavier-e12-8, marco-f08-5, bouchard-r01-7,
  bonimenteur-p14-5, -8, narrateur-ouverture-3, -4 (le narrateur repassé par l'isolateur,
  `comment=voix isolee`). Masters rangés dans `~/elevenlabs-audio/bandini-voix-v3-masters-2026-09-16/`.
- Deux voix s'allongent (ti_guy-m1-2 : 5,3 → 6,4 s ; bouchard-f06-7 : 4,5 → 5,8 s) : aucune scène
  ne les coupe (`test_aucune_voix_de_scene_n_est_coupee_par_la_suivante`), l'ouverture et le
  niveau des voix restent verts.
- `--dictionnaire` les listait encore (il ne savait pas avec quel dictionnaire une voix avait été
  faite) : réglé le jour même, [une voix sait avec quel dictionnaire elle a été faite](une-voix-sait-avec-quel-dictionnaire-elle-a-ete-faite.md).
  L'avant/après des douze :
  `captures/essai-dico/00-douze-voix-avant-apres.mp3` (hors dépôt) — Martin écoute.
