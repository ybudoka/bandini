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
