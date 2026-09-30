# La radio dit le temps qu'il fait

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « les commentaires radio doivent être conformes à la météo (ou neutres) ».
Mesuré : `Son.Ondes.maj` pioche à tour de rôle dans les répliques de l'animateur sans rien savoir du
ciel. Taxi-Radio lance « pis y fait beau à Baie-des-Brumes! » en pleine tempête de neige, et La Brume
dit « La pluie rentre par la baie » un soir de janvier où il n'a pas plu de la journée.

Correctif : une réplique qui parle du temps porte sa `meteo` (`beau`, `pluie`, `neige`, `brouillard`,
`verglas`). Les ondes ne la disent que si le ciel du moment lui donne raison, et une réplique sans
`meteo` est neutre et passe toujours. Le ciel se lit par les fonctions pures du jour et de l'heure
(`Pluie`, `Neige`, `Brouillard`, `Verglas`), sans dé. Le brouillard et le verglas ne comptent que si
leur option est allumée.

Pour que la radio *réagisse* au temps au lieu de seulement se taire, chaque station reçoit quelques
répliques neuves pour la pluie, la neige, le brouillard et le verglas (voix v3, ElevenLabs).

Un juge refuse une réplique de radio qui parle du temps (pluie, neige, beau, verglas…) sans porter sa
`meteo`. Un juge au banc fait tourner les deux stations un jour de pluie, un soir de tempête et un jour
clair, et compte ce qui passe.

## Notes

Livré le 30 sept. 2026. Chaque réplique d'animateur qui nomme le temps porte sa `meteo`
(`audio.METEOS` : `beau`, `pluie`, `neige`, `brouillard`, `verglas`). `Son.Ondes.ciel` lit le temps
dans les fonctions pures du jour et de l'heure (`Pluie`, `Neige`, `Brouillard` et `Verglas` par
`intensiteA`, le brouillard et le verglas seulement si leur option est allumée) ; `Ondes.convient`
écarte du tour de rôle ce que le ciel contredit. « Y fait beau » ne passe plus que par temps clair,
« la pluie rentre par la baie » seulement quand il pleut. Les autres répliques sont neutres.

Sept répliques neuves (v3, `app/interpretation.py`) : La Brume a la neige, le brouillard (« La Brume
porte bien son nom ») et le verglas ; Taxi-Radio a la pluie (« y mouille à siaux »), la neige (la
charrue, « elle, a' travaille »), le brouillard et le verglas (« freinez d'avance, pis priez un
peu »). 376 caractères ElevenLabs.

⚠️ **Elles ne partent pas au démarrage.** Le premier écran n'avait que 6 Ko de marge et elles en
pesaient 229 : `voix_a_la_volee` les met à part, comme les répliques de contexte. `Voix.charger` les
saute, et `Voix.chargerMeteo` les demande dix secondes avant que l'animateur reprenne le micro, un
ciel à la fois, une fois par partie.

Juges (`tests/test_ondes.py`) :

- `test_une_replique_qui_parle_du_temps_porte_sa_meteo` : une réplique d'animateur qui dit pluie,
  neige, beau, verglas… sans `meteo` est refusée (rouge si l'on retire celle de `taxi_bonjour_r`).
- `test_par_tous_les_temps_l_animateur_a_de_quoi_dire` : au moins deux répliques sous chaque ciel.
- `test_une_replique_d_un_ciel_ne_part_pas_au_demarrage`.
- `test_la_radio_dit_le_temps_qu_il_fait` : les deux stations, vingt minutes sous chacun des cinq
  ciels. Rien ne contredit le ciel, la réplique du ciel passe, aucun dé n'est tiré, et le ciel est
  demandé au moins 5 s avant la première voix. Rouge sans le filtre, et rouge sans la fenêtre de
  dix secondes.

`test_l_ambiance_et_les_voix_se_decodent` (navigateur) demande aussi les ciels.
