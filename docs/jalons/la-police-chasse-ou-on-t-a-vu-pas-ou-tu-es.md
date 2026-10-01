# La police chasse où on t'a vu, pas où tu es

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin en jouant (1er oct. 2026) : « la police doit prendre plus de temps à nous
retrouver. Actuellement avec plusieurs étoiles, on se déplace et elle sait déjà où on est.
C'est impossible de s'échapper. » Quatre omniscences lues dans `police.js` et `vehicules.js`.

- ⚠️ Les autos-patrouilles, sur les rails, choisissaient à chaque croisement la sortie qui les
  rapprochait de ta position RÉELLE.
- ⚠️ Elles naissaient autour de ta position réelle (320 à 520 px), où que tu sois rendu.
- ⚠️ L'hélico tournait au-dessus de ta position réelle, et voyait à 25 tuiles : tant qu'il
  était là, rien ne retombait, où que l'on aille.
- ⚠️ Un barrage se posait devant ton char sans que personne t'ait vu passer.

Le correctif : la police ne sait que ce qu'on lui a dit. Tant qu'un agent, une auto ou l'hélico
t'a vu il y a moins de `piste_fraiche_s`, la radio dit où tu es ; au-delà, tout le monde chasse
`dernierVu` — et, arrivé là sans te voir, ratisse le secteur.

## Notes

**Livré le 1er oct. 2026.** Tout en données dans `app/recherche.py`.

- **La piste** (`POLICE.piste_fraiche_s`, 2 s ; `Police.piste`, `Police.pisteFraiche`). Fraîche,
  c'est toi ; froide, c'est `dernierVu`. Les témoins, les coups de feu et le stool la déplacent
  toujours, comme avant.
- **Les autos vont où on t'a vu** (`vehicules.js`, le choix de sortie en poursuite). Arrivées à
  `ratisse_px` (96 px) de la piste froide sans te voir, elles RATISSENT : leurs sorties se tirent
  comme celles du trafic. ⚠️ Seulement la police : les fuyards et les chars de gang des missions
  gardent leur règle.
- **Elles naissent autour de la piste**, pas de toi (`peuplerAutos`) ; l'hélico aussi
  (`peuplerHelico`).
- **L'hélico ratisse** : piste froide, il tourne au-dessus d'elle en élargissant son cercle
  jusqu'à 220 px. ⚠️ Et il ne voit plus que ce que son projecteur éclaire : 11 tuiles le jour,
  8 la nuit (25 et 20 avant — tout l'écran et plus).
- **Pas de barrage sur une piste froide** (`majBarrages`).

⚠️ Ce qui ne change pas : un agent qui te voit te poursuit dans la seconde, l'auto qui te voit
fonce, et les étoiles ne tombent toujours qu'hors de vue (`decroissance_s`). On s'échappe en
cassant la ligne de vue, puis en ne restant pas là où on t'a vu.

**Le juge** (`tests/test_police_js.py::test_la_police_chasse_ou_on_t_a_vu_pas_ou_tu_es`) : cinq
étoiles, la piste posée à 900 px du joueur et froide ; en 15 s, ni l'hélico ni les autos ne
viennent à lui, et personne ne le revoit. Deux mutations le font rougir : les autos qui visent
de nouveau le joueur, et l'hélico qui le survole de nouveau.
