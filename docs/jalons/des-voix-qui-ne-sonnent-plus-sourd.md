# Des voix qui ne sonnent plus sourd

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

suite du retour « caverneuses ou étouffées » ; Martin a dit oui à la correction mesurée.

- ⚠️ **Mesuré d'abord** (chaque réplique v3 contre la MÊME en v2, par tiers d'octave) : la
  finition ne touchait pas au timbre (master et fichier fini à 0,3 dB près) — c'est v3 qui
  avait déplacé les voix : Julia +3 à +7 dB entre 100 et 250 Hz et sourde en haut, Amélie +6
  à +18 dB dans les graves, Jeanne Mance +6 à +11, Léo −5 à −9 dB entre 3 et 6 kHz. **Une
  égalisation par voix** dans `interpretation.EGALISATION`, des coupes **de la taille de
  l'écart** et un passe-haut pour tous (85 Hz hommes, 120 Hz femmes), posée **avant** de
  mesurer le niveau. Résultat, fichiers finis contre v2 : Julia centroïde 307 → **524 Hz**
  (523 en v2), graves +6,6 → +1,3 dB ; Amélie +6,0 → +0,5 ; Josée +6,2 → +2,6 ; Léo aigus
  −6,6 → −2,6 ; Felix, narrateur, Khaivan, Tremblay intacts.
- ⚠️ Amélie ressortait alors à +7,7 dB en haut (v3 l'avait déjà rendue brillante) : coupe de
  4 dB à 5 kHz, +4,5. **Les passants, radios et pubs en 44 kHz / 48 kbit/s** : le 22 kHz /
  32 coupait tout au-dessus de 8 kHz (budget de démarrage 1,21 → **1,41 Mo** sur 1,5 — 94 Ko
  de marge). Deux pannes trouvées en chemin : le pic du mp3 **ne suit pas le gain** (sur
  `bouchard-m4-2`, −1 dB sort à −4,5 dBFS et −2 dB à −3,1) — la boucle de correction descend
  maintenant par quarts de dB — et une réplique dite bas avec une consonne qui claque
  restait **4 dB sous les autres** (−23,2 LUFS) : **limiteur** doux à −3 dBFS, 6 dB de
  travail au plus. `--refinir` ne s'arrête plus à la première réplique en échec. **Aucun
  crédit** : tout depuis les masters. Juges : chaque égalisation corrige une voix du jeu,
  les trois chemins qui fabriquent une voix égalisent, chaque voix de la rue est en 44 kHz
  (29 fichiers, rouges avant).
- ⚠️ **À écouter** : A/B avant/après préparés pour Martin.
