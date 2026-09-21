# Les chars lourds atteignent leur vitesse — la paie de la Prévost se sème

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (21 sept. 2026) : « la mission de la paie de la Prévost est presque impossible, le
camion va trop lentement pour les policiers ». Mesuré au banc : à fond, le camion plafonne à
1,97 px/image au lieu des 2,8 de sa fiche — moins qu'un agent à pied (2,0), qui le suit à 40
px pendant dix secondes : `vu` ne dépasse jamais cinq images, les deux étoiles ne tombent
jamais. La cause est dans la physique, pas dans la mission :
`vitesse = (vitesse + acceleration) × friction` plafonne à
`acceleration × friction / (1 − friction)`, et avec la friction de la rue (0,985) un moteur
faible n'atteint jamais sa `vitesse_max` — le camion (70 %), l'autobus (71 %), la berline de
luxe (77 %), la remorqueuse, l'ambulance, le chalutier et le porte-conteneurs (52 %) ;
l'auto est à 98 %. Le plan : la friction de ces chars se DÉDUIT de leur fiche (juste assez
faible pour que la pointe soit la `vitesse_max`), l'accélération ne bouge pas (le camion
démarre en camion) et le trafic, qui roule sur ses rails sans friction, ne voit rien. Deux
juges : aucune fiche ne promet une pointe que la physique refuse, et au banc le camion de
paie à fond distance un agent à pied jusqu'à ce que les étoiles tombent.

## Notes

**Livré le 21 sept. 2026.** La friction se déduit : `vehicules.friction_pour(vitesse_max,
acceleration, base)` rend celle de la rue (0,985) ou de l'eau (0,995), sauf si elle vole au
char la `vitesse_max` de sa fiche — elle est alors juste assez faible pour que la pointe soit la
fiche (arrondie vers le haut : au plus près, elle retombait d'un cheveu dessous). Les pointes,
avant → après, en px/image : camion 1,97 → 2,8 ; autobus 1,84 → 2,6 ; berline de luxe 2,76 →
3,6 ; remorqueuse 2,63 → 3,0 ; ambulance 3,28 → 3,6 ; chalutier 2,39 → 2,6 ; porte-conteneurs
0,99 → 1,9 ; auto 3,94 → 4,0. Le taxi, la moto, le vélo, la police, le sport, le cabriolet et
la chaloupe gardent leur friction. L'accélération ne bouge pas (le camion démarre toujours en
camion), et le trafic, qui roule sur ses rails sans friction, ne voit rien.

- Au banc, le camion de paie gaz tenu sur la plus longue ligne droite de la ville (416 tuiles),
  un agent en chasse à 40 px : avant, l'agent était encore à 41 px au bout de 45 s et les deux
  étoiles n'avaient pas bougé ; après, il décroche à 6,6 s (189 px) et la première étoile tombe
  à 30,6 s. La même mesure sur huit graines.
- ⚠️ Le juge de s03 d'origine SAUTE l'étape « sème la police » (`etoiles = 0`) : c'est pour ça
  que personne ne l'avait vue. `test_s03_le_camion_de_paie_a_fond_seme_l_agent_a_pied…` la joue
  au bouton, et mord sous l'ancienne friction.
- ⚠️ À 3★, l'auto-patrouille en chasse roule à 3,74 (0,85 × 4,4) : un camion ne la distance pas,
  et c'est voulu. Prendre le camion de paie est un `vol_vehicule` si quelqu'un le voit (35 de
  chaleur) ; deux délits de plus et c'est 3★. Avec un camion enfin plus rapide qu'un agent à
  pied, on n'a plus à les bousculer pour passer.
- ⚠️ **Un poids lourd lancé tourne large** : à fond, le cercle du camion fait 5 tuiles, celui de
  l'autobus 6,1 (une intersection en fait 4). `test_le_cercle_d_un_char_ne_grandit_pas…` était
  vert À VIDE pour l'autobus — il le mesurait « à fond » à 1,84 — et il rougissait avec lui : la
  borne des chars de classe `camion` passe à 6,5 tuiles (4,5 pour les autres), et le camion y est
  mesuré aussi. Rien n'a reculé : la courbe lit `vitesse / vitesse_max`, qui n'a pas bougé, donc à
  chaque vitesse que ces chars atteignaient avant, ils tournent comme avant. Le camion prend une
  intersection jusqu'à ≈ 2,5 px/image, plus vite qu'un agent qui court.
- Le paquet des définitions prend 30 octets (les frictions à cinq décimales) : 44 422 octets
  gzip. `test_le_paquet_reste_leger` était déjà rouge sur la base (44 392, plafond 44 000).
