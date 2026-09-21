# Des sirènes qu'on entend

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Des sirènes qu'on entend (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « je veux des sirènes pour les ambulances et polices. »

⚠️ **Il n'y en avait qu'une, et presque jamais.** `Son.boucle('sirene', true, 0.5)`
s'allumait dans une seule branche : `v.conducteur === 'police'` avec au moins une étoile.
Trois conséquences, et Martin les a toutes entendues d'un coup :

- **L'ambulance n'a jamais fait entendre une sirène.** Sa fiche déclare pourtant
  `sirene: true` depuis M9 — comme `cercles` et `defonce`, c'est une promesse du catalogue
  que le navigateur ne lisait pas.
- **Au volant, aucune des deux.** On volait une auto-patrouille ou une ambulance, et on
  conduisait en silence. C'est la première chose qu'on essaie.
- **Et le volume était fixe** : allumée, elle sonnait pareil à dix pixels et à l'autre bout
  du district. Une sirène qu'on entend toujours ne veut plus rien dire.

Ce qui a été livré :

- **Deux sons, pas un.** `sirene_ambulance` rejoint le catalogue audio (ElevenLabs, 4 s en
  boucle, 16 Ko) : deux notes qui alternent lentement, là où celle de la police monte et
  descend sans s'arrêter. ⚠️ **Les confondre, c'est ne pas savoir qui arrive derrière soi**,
  et c'est toute la différence entre se ranger et se sauver.
- **Un mélangeur**, `majSirenes()` : une boucle par **sorte**, à chaque image, au volume du
  char le plus proche qui la fait hurler — `1 − d / 460 px`, et zéro au-delà. Les deux
  peuvent sonner en même temps ; ni l'une ni l'autre ne dépend d'une branche de l'IA.
- ⚠️ **Le mélangeur retient ce qu'il a demandé**, il ne lit pas l'état de `Son`. Un mp3
  absent — ou un navigateur qui n'a pas encore reçu de geste — laisse `boucleActive` à faux
  **pour toujours** : s'y fier, c'est redemander la même boucle soixante fois par seconde
  sans jamais s'en apercevoir. C'est la leçon du son retenu, appliquée avant de se la reprendre.
- **Une ambulance sur trois qui naît dans le trafic est en course**, sirène allumée : on
  l'entend traverser. Les deux autres rentrent au garage — une ville où **toutes** les
  ambulances hurlent n'est pas une ville, c'est une alarme.
- **Au volant d'un char à sirène, le bouton du klaxon est celui de la sirène**, et
  l'étiquette du bouton tactile passe de KLAXON à SIRÈNE. ⚠️ Le klaxon d'une auto-patrouille
  n'a jamais servi à rien, et le boulot se prendra **au même bouton** : dans une ambulance,
  on répond à l'appel et on part la sirène allumée, d'un seul geste. Dans une auto, le bouton
  reste le klaxon — un juge le vérifie, pour que le métier du bouton ne change pas pour tout
  le monde.
- ⚠️ **Ce qui n'a pas été jugé, et il faut le dire** : _le son lui-même_. Le juge du
  navigateur prouve que `sirene_ambulance-1.mp3` se **décode** ; personne ici n'a d'oreilles.
  Si elle ne sonne pas comme une ambulance, c'est `--refaire sirene_ambulance`.
- **Juge (1 neuf)** : deux boucles distinctes pour une ambulance et une auto-patrouille ; le
  volume tombe à zéro à 520 px et revient en se rapprochant ; éteindre la sirène la fait
  taire ; le bouton l'allume et l'éteint au volant, avec la bonne étiquette ; et dans une
  auto le même bouton klaxonne toujours.

## Notes

demande de Martin (« je veux des sirènes pour les ambulances et polices ») : il n'y en avait
**qu'une**, et presque jamais — `Son.boucle('sirene', …)` ne s'allumait que pour une
auto-patrouille de l'IA en chasse, à volume fixe, sans distance. L'ambulance déclare
pourtant `sirene: true` depuis M9 et n'en a **jamais** fait entendre une seule ; au volant,
aucune des deux. Maintenant : **deux sons** (celle de la police monte et descend, celle de
l'ambulance fait deux notes — les confondre, c'est ne pas savoir qui arrive derrière soi),
un **volume qui suit la distance** (460 px de portée), une **ambulance sur trois** qui naît
en course dans le trafic, et au volant d'un char à sirène le **bouton du klaxon devient
celui de la sirène** — l'étiquette du bouton tactile le dit
