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
