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
