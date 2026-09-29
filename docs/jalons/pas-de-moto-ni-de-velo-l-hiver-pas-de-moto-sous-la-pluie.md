# Pas de moto ni de vélo l'hiver, pas de moto sous la pluie

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 29 sept. 2026 : « pas de moto et velo lhiver », « pas de moto durant
la pluie non plus »._ **La règle dans les données** : la fiche porte `remise`
(`["hiver", "pluie"]` pour la moto, `["hiver"]` pour le vélo) ; `Vehicules.remise(slug)` =
la neige tient (`Saisons.enHiver`) ou il pleut (`Pluie.intensite() > 0`) — pure fonction du
jour et de l'heure, sans dé. **La rue** : `typeDeRue` tire avec LE MÊME DÉ, et un deux-roues
remisé naît berline (rien ne se retire de la liste : la ville ne glisse pas) ; un balayage
aux 60 images, comme les motoneiges, rentre HORS CHAMP les motos et vélos du trafic et garés
l'hiver, les motos qui ROULENT sous la pluie (garées, elles restent) — jamais le char du
joueur ni d'une mission ; les enfants à vélo ne naissent plus l'hiver. **Les missions**
(choix de Martin) : l'hiver le fuyard (m2, f04, f07, p13) file EN MOTONEIGE, sous la pluie
en berline ; q10 : une motoneige attend au pont ; les voix disent « motoneige » l'hiver
(variantes générées). **Le joueur** : la moto du livreur (palier 50) reste remisée l'hiver ;
Le Grand Saut refuse l'hiver (« LA MOTO EST REMISÉE ») ; la pizza se livre en berline
l'hiver ; la moto de la liste de Sven devient une motoneige. **Juges** :
`test_motos_velos_remises_js.py` ; ⚠️ le banc naît en janvier : suite complète.
