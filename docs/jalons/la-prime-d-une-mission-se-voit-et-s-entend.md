# La prime d'une mission se voit et s'entend

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22 sept. 2026) : « quand je reçois une prime pour une mission, je veux le
voir clairement et avec un son qui correspond à la prime. » Aujourd'hui la prime d'une
mission réussie n'est qu'un « +350 $ TITRE » dans la bande de messages, le même ding que
ramasser une liasse, puis le jingle de mission par-dessus, et la scène de fin arrive
aussitôt. À faire : un bandeau de prime au centre de l'écran (MISSION RÉUSSIE, le montant
qui défile jusqu'à sa valeur, le bonus sans bosse à part), et quatre sons selon la taille de
la prime (petite < 250 $, moyenne < 450 $, grosse < 800 $, gros lot au-delà), du tintement
de caisse à la pluie de pièces. Les sons sont synthétisés (quota ElevenLabs à sec jusqu'au
17 oct.) ; la recette ElevenLabs est posée au catalogue pour plus tard. Le défi réussi passe
par le même bandeau.

## Notes

**Livré le 22 sept. 2026.**

- **Pourquoi on ne la voyait pas** : le HUD se tait pendant une scène (`!B.scene` dans
  `Hud.dessiner`), et `reussir()` lance la scène de fin dans la foulée. Le « +150 $ » de la bande
  des messages était donc, la plupart du temps, écrit sous une scène et jamais affiché.
- **Le bandeau** (`Hud.prime`, appelé par `Missions.annoncerPrime`) : MISSION RÉUSSIE (ou DÉFI
  RÉUSSI, DÉFI DU JOUR), le montant en gros qui monte jusqu'à sa valeur, le titre, et la part « sans
  une bosse » sur sa ligne. Dessiné **après** le fondu (`dessinerTransition`), donc par-dessus la
  scène de fin ; posé sous la bande des messages (le `message` d'une fin, « LA CLÉ DE LA PLANQUE »,
  s'y écrit en même temps). Le gros lot clignote et saute d'un cran quand le compte arrive ; les
  grosses primes font tomber des pièces à l'écran.
- ⚠️ **Il compte en pas de simulation, pas en images peintes ni en `B.t`** (`Hud.majPrime`, appelé
  en tête de `Jeu.maj`). Les images peintes suivent l'écran (un 120 Hz le ferait durer moitié
  moins ; le Chromium headless peignait à ~127 images/s), et `B.t` se fige sous un dialogue — la
  scène de fin, justement : le bandeau restait collé toute la conversation. Un menu le suspend.
- **Quatre paliers** (`economie.PRIME_PALIERS`, servis dans `economie.prime_paliers`) : petite
  (< 250 $), moyenne (< 450 $), grosse (< 800 $), gros lot. Sur les 36 missions de l'histoire :
  12, 17, 5, 2 — un juge exige que chaque palier se gagne et que le gros lot reste rare.
- **Le son** (`Son.SFX.prime(palier)`) remplace le jingle de mission ET le ding de la liasse (trois
  sons l'un sur l'autre ne disaient plus la taille) : la caisse, puis des pièces de plus en plus
  nombreuses, puis la fanfare (do-mi-sol-do, deux fois pour le gros lot, et l'accord tenu). La
  pluie de pièces dure ce que dure le compteur du bandeau.
- ⚠️ **Synthétisé pour l'instant** : le quota ElevenLabs était à 17 crédits (remise le 17 oct.).
  Les quatre recettes attendent dans `audio.EN_ATTENTE`, **hors du catalogue** : le catalogue ne
  déclare jamais un son sans son fichier (`test_le_son_survit_a_l_absence_d_audio` l'a rappelé à la
  première suite). À la remise : les déplacer dans `CATALOGUE`, lancer `scripts/audio_elevenlabs.py`
  (`--essai` les liste), puis remettre `if (!joue('prime_…'))` devant chaque synthèse de
  `SFX.prime_*` — la synthèse redevient le filet. Martin écoute et dit lesquels refaire.
- `Missions.encaisser(montant, raison, enSilence)` : l'argent s'encaisse toujours là (les juges y
  guettent les paiements), sans ding ni message quand la prime s'annonce à part.
- Juges : `tests/test_prime_js.py` (mordent : sans `Hud.majPrime` dans `Jeu.maj`, ou avec le
  jingle remis, ils rougissent). Deux juges lisaient le vieux « +X $ » dans `B.msg`
  (`test_defi_js`, `test_histoire_js` — la livraison) : ils lisent le bandeau.
