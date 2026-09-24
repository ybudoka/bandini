# Un comptoir reste ouvert après un achat

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026) : « lors d'une sélection d'un achat ou autre, je veux rester dans le même
menu, pas quitter, on quitte seulement avec B ou Esc ou un menu retour ou quitter ». Chez Gus, au
casse-croûte, au coffre et au marché noir, le menu restait déjà ouvert (`faire` rend `false`, et
`rafraichirMenu` le refait) ; ailleurs — les soins, Rosa, la garde-robe, le barbier, Ti-Guy, la
fourrière, l'avocat, le comptoir du fond, les hommes de Sal, la caisse, la sauvegarde — un choix
refermait le comptoir. On les range tous du même côté, et un juge presse ACTION sur chaque ligne
de chaque comptoir de la ville pour vérifier que le menu est encore là.

⚠️ Restent fermants, parce que le choix EST un départ : dormir (le fondu de la nuit), lire le
Clairon (la manchette se lit, en voix, hors du menu), REPARTIR au rideau, vendre le char au rideau
(il n'y a plus de char ni de volant), la canette restée prise (il faut brasser la machine),
l'arrestation, et les menus de la pause qui mènent ailleurs (reprendre, carte, photo, titre).

## Notes

Livré le 22 sept. 2026. La règle vit à un seul endroit, `Hud.choisirLigne` : un `faire` qui rend
`false` garde le menu et le refait (`refaire`), le pouce au même rang. Passés du côté « reste
ouvert » : la caisse et l'achat du commerce, la sauvegarde seule, les soins, la friperie, Rosa, la
garde-robe, le barbier, Ti-Guy (réparer, repeindre, assurer, encaisser — et vendre au comptoir), la
fourrière, l'avocat, le comptoir du fond, les hommes de Sal. Le menu du rideau et celui des hommes
de Sal reçoivent un `refaire` : ils n'en avaient pas, et resté ouvert, le prix d'une réparation
déjà payée se serait encore affiché.

⚠️ Le toast (`Hud.message`) se dessinait sous le voile du menu : tant que le comptoir se fermait,
personne ne le voyait. Il se dessine maintenant au-dessus de la boîte (`dessinerMessage`,
`boiteDuMenu`) — « UNE PAGE DE MOINS », « CHAR RACHETÉ » se lisent sans fermer.

Le juge `tests/test_un_comptoir_reste_ouvert_js.py` presse le vrai ACTION sur chaque ligne de chaque
comptoir de la ville ; il rougit si l'on remet un `return true` (vu pour les soins et Rosa) ou si
le toast repasse sous le voile. `test_dette.py` demandait que l'acompte ferme le menu : il demande
maintenant qu'il reste.
