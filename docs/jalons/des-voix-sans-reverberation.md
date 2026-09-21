# Des voix sans réverbération

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin après écoute : « caverneuses ou étouffées », puis « regénère Mme Thibodeau
et les prostituées et toutes les voix avec réverbération, je les veux sans réverbération ».

- ⚠️ **Mesuré d'abord, et étalonné** : la vitesse de chute du son en fin de syllabe (95e
  centile, dB/s) — une pièce la borne ; une voix sèche à 534 tombe à 315 quand on lui ajoute
  soi-même une réverbération de 0,4 s.
- ⚠️ **Régénérer ne sèche rien** : même phrase de Mme Thibodeau, v3 en stabilité 0 / 0,5 / 1
  et en similarité basse, entre 294 et 350 ; v2 et turbo montent à 423-443 mais perdent
  l'émotion. Ce qui sèche, c'est l'**isolateur d'ElevenLabs** — ajouté au serveur MCP maison
  (`elevenlabs_voice_isolation`, hors dépôt ; refuse sous 4,6 s : on allonge de silence et
  on recoupe) : sur la voix réverbérée à 0,4 s, **315 → 532**. Passé sur les masters déjà
  payés, **sans régénérer une réplique** (`--secher --masters`).
- ⚠️ **Il ne sèche que ce qui est mouillé** : Julia (Thibodeau, la Brume, La Brume radio)
  347 → 373 et le narrateur 428 → 471, timbre intact (Julia gagne même 6 dB d'air) ; Amélie,
  Felix et Léo **rien à retirer** (432, 436, 443 avant comme après — leur écart avec v2
  était le débit de v3) et Felix et Léo y perdaient 1,5 à 4,6 dB d'aigus : **pas séchés**,
  sinon plus étouffés. `interpretation.VOIX_A_SECHER` = Julia + narrateur ; la génération
  sèche avant de finir, `--refinir` repart du master séché, et chaque fichier séché porte
  `comment=voix isolee` — un juge le lit sur les **35 fichiers** (rouge avant).
- ⚠️ Ce qui reste à Julia (373, une voix sèche est à 510+) **n'est pas la pièce, c'est sa
  voix** : rauque, fins de mots soufflées — même v2 isolée plafonne à 441 ; plus sec
  voudrait dire **une autre voix** pour Thibodeau et la Brume. 7 378 crédits (essais
  compris).
- ⚠️ **À écouter** : c'est l'oreille de Martin qui dit si la pièce est partie.
