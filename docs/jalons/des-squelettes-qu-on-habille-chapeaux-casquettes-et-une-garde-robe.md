# Des squelettes qu'on habille : chapeaux, casquettes, et une garde-robe presque infinie

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026) : « les personnages doivent pouvoir avoir des chapeaux, casquettes et
plus — idéalement des squelettes qu'on habille, ce qui donne une presque infinité
d'habillement » ; « il faut plusieurs types de squelettes pour les types de personnes ».
Vague 1 (le moteur et la rue) : des SQUELETTES (`homme` = le corps actuel et ses 42 poses ;
`femme`, `costaud`, `vieux`, `grand` dérivés par règles ; `enfant`) et des PIÈCES qu'on
enfile (coiffure, chapeau, haut, bas, souliers, accessoires), catalogue dans
`app/garderobe.py`, assemblage dans `static/js/garderobe.js` (grilles composées puis cuites
par `Atlas`, le chapeau posé sur la tête que chaque pose montre). Chaque passant ordinaire
tiré dans la garde-robe de son archétype à l'empreinte de son id (aucun dé : la ville ne
bouge pas) ; les donneurs habillés d'après leur portrait. Vague 2 : le joueur s'habille
(chapeaux au magasin), agents et gangs en pièces.
