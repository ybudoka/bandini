# Le vélo s'enfourche et sonne

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« je veux aussi un nouveau son pour ramasser et monter sur un vélo. je
veux la sonnette comme klaxon de vélo ») : monter sur un vélo — ou une moto — jouait
`ramasse`, le cliquetis d'un objet qu'on ramasse, et Martin l'a entendu pour ce que c'était.
Nouvel échantillon `enfourcher` (la béquille qui claque, le cadre et la chaîne qui tintent
sous le poids), pour tout char **sans portières** — la moto aussi, donc. Et **la sonnette
est l'avertisseur du vélo** : la fiche nomme l'avertisseur (`vehicules.klaxon`, « sonnette »
pour le vélo, « klaxon » pour tous les autres, juge sur `AVERTISSEURS`), `avertir(v)` joue
celui de la fiche au même bouton — le trafic impatient passe par là aussi — et l'étiquette
du bouton tactile dit **SONNETTE** (contexte `vehicule_sonnette`, sur le modèle de
`vehicule_sirene`). Les vélos du trafic sonnaient déjà en passant (`jouerA('sonnette')`) :
même son, désormais aussi sous le pouce, avec un repli synthétisé. Juges : la fiche du vélo
dit « sonnette » et les autres « klaxon » ; au banc, au guidon d'un vélo le bouton dit
SONNETTE et fait sonner la sonnette, au volant d'une auto KLAXON et le klaxon ; monter et
descendre d'une moto et d'un vélo joue `enfourcher` deux fois et aucune portière. Poids :
578 → **586 Ko**, il reste **14 Ko** sous le plafond de 600 — la prochaine variante ne
rentre pas sans baisser un débit ou relever le plafond.

- ⚠️ Pas écouté : `enfourcher` est sorti à 0,62 s avec +11 dB de gain (plancher propre, 43
  dB) — `--refaire enfourcher` si ce n'est pas ça
