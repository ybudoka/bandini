# Les bateaux ne sont pas des chars

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 30 sept. 2026 : « révise les bateaux car ils sont trop comme des véhicules et ce n'est pas toujours
cohérent ». Tout ce qu'il a vu : la conduite, la police et la descente, les règles de char, l'habillage. Tranché
par Martin : tout corriger, en vagues ; erre et gouvernail ; une vedette de police ; descendre au large = plonger ;
les chaloupes remisées l'hiver.

Un bateau est un `vehicule` ordinaire marqué `eau: true` (`app/vehicules.py`, la chaloupe, le chalutier, le
porte-conteneurs). Six endroits seulement le traitent à part (`tuileInterdite`, `majNoyade`, `majConducteur`,
`majVolDeChar`, `Derapage.exempt`, le moteur et les phares) ; tout le reste — police, fourrière, météo, sons,
statistiques — le prend pour une auto.

**Vague 1 — la conduite : erre et gouvernail.** Une branche `eau` dans `majPhysique` : la coque pivote au tiers
avant (la poupe chasse, le nez ne balaie plus comme un train arrière) ; pas de frein sec — l'arrière met la
machine en arrière, qui ralentit doucement puis recule lentement ; lâcher le gaz laisse filer sur l'erre. La
neige, le verglas, la pluie et les pneus d'hiver (`Neige`, `Verglas`, `Pluie`, `Garage.hiver`) ne jouent plus sur
l'eau, et les feuilles d'octobre ne se lèvent plus d'une coque.

**Vague 2 — ce qui n'est pas une règle de bateau.** Ni « mal garé » ni fourrière pour une coque
(`malGare`, `charSaisissable` — le porte-conteneurs saisi renaissait sur la terre ferme du lot) ; la remorqueuse
ne l'accroche pas (`aCrocher`) ; le garage de Ti-Guy la refuse (`Garage.accepte`, `charDevant`) ; une coque
amarrée ne compte plus comme une auto garée (`compteCommeGare`) ; le carnet a sa ligne **BATEAUX VOLÉS** ; la
frénésie « chars » ne compte plus les bateaux ; le traversier n'accoste pas sur une coque (`traversier.js`
`poser`, comme `Pont.poser`).

**Vague 3 — le plongeon, et la police de terre.** Descendre au large = plonger : une éclaboussure, on nage ; la
coque file sur son erre et s'arrête, elle n'est pas « laissée » (la fourrière l'ignore). Les agents à la nage ne
sortent plus personne d'une coque (« SORS DU CHAR ! » en pleine eau) — ils attrapent encore un joueur qui nage.
Les autos-patrouilles ne foncent plus en ligne droite dans la baie (`police.js` `commandes`, la ligne de vue
traverse l'eau) : elles s'arrêtent au bord. Pas de barrage routier tant que le joueur est sur l'eau.

**Vague 4 — la vedette de police.** Une fiche `vedette` (police, sirène, eau) et son sprite. Le premier pilote
sur l'eau (aucun n'existe : `docs/exploitation.md` en annonce un qui n'est pas là) : un chemin sur les tuiles
d'eau, au grain grossier, recalculé chaque seconde. Elle naît hors champ, dans la même étendue d'eau que le
joueur — une dès une étoile, deux dès trois. Elle aborde bord à bord ; coque du joueur presque arrêtée à côté
d'elle : **« ARRAISONNÉ ! »**, qui vaut l'arrestation.

**Vague 5 — l'habillage et l'hiver.** Le compteur en **NŒUDS** ; le bouton **CORNE** quand la fiche a la
corne ; monter à bord fait des pas sur un pont (pas la béquille du vélo) ; le chalutier et le cargo ont un diesel
grave (ElevenLabs), la chaloupe garde son hors-bord ; les feux de navigation — rouge et vert aux flancs, blanc à
la poupe ; l'épave **coule** en quelques secondes, avec ses bulles, puis s'efface. De décembre à mars, les
chaloupes de plaisance sont sur des bers à quai ; la chaloupe de Sven (m52), le chalutier et le cargo restent à
l'eau.

- ⚠️ **L'ordre compte** : la vague 3 retire l'arrestation par les nageurs, la vague 4 la remplace — entre les deux,
  sur l'eau, la police ne peut que suivre jusqu'au quai.
- ⚠️ **Les amarrages sont un tirage** (`carte.amarrages`, `majAmarrages`) : la remise d'hiver MARQUE l'amarrage et
  peint le ber sans entité, elle n'en retire aucun — sinon les identifiants et le hasard de la ville glissent.
- ⚠️ **L'épave qui coule** : une cible de mission détruite reste comptée détruite (m52 à m54) — s'effacer ne doit
  pas la faire revenir « debout ».
- ⚠️ Chaque règle neuve a son juge, et chaque juge est vu rougir, règle retirée.
