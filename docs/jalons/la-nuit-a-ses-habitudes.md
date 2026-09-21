# La nuit a ses habitudes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « la nuit, personne ne se baigne, plus de véhicules
stationnés, et donne-moi d'autres idées pour la nuit » — puis, devant la liste : « je veux
toutes les idées ». « Plus de véhicules stationnés » veut dire **davantage, et ailleurs**
(tranché avec Martin) : c'est la dette que [la nuit ne se vide pas](la-nuit-ne-se-vide-pas.md)
avait écrite d'avance (« plus dans les entrées des Érables la nuit, moins sur les rues
commerçantes »).

Ce que la nuit fait déjà, et qu'on ne refait pas : les feux qui clignotent (`TRAFIC.clignotant_*`),
les kiosques fermés, la Brume, les cônes de vision raccourcis, l'équipe du chantier qui rentre,
les autobus plus rares, le quai du cargo ouvert, le rythme des districts.

**Vague 1 — les deux demandes.** Les baigneurs ne naissent que le jour, et ceux qui restent à la
brunante rentrent **hors de l'écran**. Les chars garés suivent l'heure : plus nombreux la nuit, et
d'abord dans les entrées de cour et les rues à logements ; le jour, d'abord devant les commerces.

- ⚠️ L'heure de la plage vit dans `pietons.PLAGE`, **pas** sur l'archétype `enfant` : toute la
  ville s'en sert, et les enfants disparaîtraient de partout la nuit.
- ⚠️ `stationnes_max` reste un entier de 0 à 20 (un juge le tient) : la nuit a sa propre clé.
- ⚠️ Chaque naissance évitée décale tous les dés qui suivent (`Vehicules.peupler`) : choisir la
  place ne tire **aucun dé de plus**.

**Vague 2 — ce qu'on voit.** Les **phares** éclairent devant les chars qui roulent (deux faisceaux
dans le tampon de lumière, des feux arrière rouges). Les **fenêtres** des immeubles à logements
s'allument à la brunante et s'éteignent une à une vers 2 h. En quartier pauvre, **un lampadaire
sur quelques-uns est mort** ou grésille : des poches d'ombre.

- ⚠️ Le budget : 25 lampes par image. Les phares se comptent avec les lampadaires.
- ⚠️ Quelle fenêtre, quel lampadaire : une empreinte de sa position, **jamais un dé**, et rien ne
  bouge dans la ville (`carte.generer` identique).

**Vague 3 — qui est dehors.** Le **last call** : à la fermeture des bars, une grappe de fêtards
titubants sort des devantures de nuit, chante et cherche la chicane. Le **camelot du _Clairon_**
passe à l'aube et lance le journal sur les perrons. La nuit, une poubelle fouillée sort un **raton
laveur** au lieu du rat, et les goélands dorment.

**Vague 4 — ce que ça change au jeu.** Les **comptoirs ferment la nuit**, sauf le dépanneur et le
bar (seuls les kiosques ont des heures aujourd'hui : `Missions.ouvert`). L'**arroseuse de nuit** : un
camion de la ville sur une boucle tracée comme celle des éboueurs, et l'asphalte mouillé derrière
elle qui glisse un moment.

- ⚠️ Chaque vague est jouable, testée, et ses juges **rougissent sans leur règle** (mutations).
