# Refaire les voix que le dictionnaire de prononciation change

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Le dictionnaire (app/prononciation.pls) est téléversé et v3 l'applique (vérifié le 22 sept.
2026), mais il ne vaut que pour les voix générées APRÈS. 46 voix déjà faites disent encore
les mots à l'ancienne (4 230 caractères au 22 sept. : les piastres du narrateur, Ti-Guy,
Prévost, Roy, les astheure…). `uv run python scripts/audio_elevenlabs.py --dictionnaire` en
donne la liste à jour et la commande --refaire (payante, avec --masters pour garder les
masters). Le quota ElevenLabs (50 216 crédits) était à 111 crédits du plafond le 22 sept.,
remise le 17 oct. 2026. Après la génération : écouter, retirer du .pls une règle qui sonne
mal, et lancer test_aucune_voix_de_scene_n_est_coupee_par_la_suivante (une voix plus longue
peut se faire couper par sa scène).
