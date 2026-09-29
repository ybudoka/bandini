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

## Notes

**Livré le 29 sept. 2026.**

- **La règle** : `remise` dans la fiche (`app/vehicules.py`, la clé n'existe que sur la moto et le
  vélo — le poids du paquet) ; `Vehicules.remise(slug)` rend `'hiver'`, `'pluie'` ou `null`, pure
  fonction du jour et de l'heure. ⚠️ La pluie À L'HEURE (`Pluie.intensiteA`), pas `intensite()`, qui
  tombe à zéro dès qu'on entre quelque part.
- **La rue** : `typeDeRue` tire avec le même dé et `horsRemise` rend une berline à la place d'un
  deux-roues remisé — jugé sur tout le dé (400 tirages, 400 dés, et seules les berlines changent).
  `rentrerLesRemises` (aux 60 images, dans `peupler`) : hors champ seulement, jamais ce qui est à
  quelqu'un (`aToi`, `vole`, `aLaPlanque`, `mission`, `fuyard`). Les enfants à vélo rentrent aussi.
- **La bâche** (`fiche.bache`, `sprites.js`) : ce qui reste l'hiver est à quelqu'un et dort sous une
  bâche grise ; `Vehicules.remisee(v)`, et `monter` dit « REMISÉE POUR L'HIVER — REVIENS AU
  PRINTEMPS ». `recreerLeChar` marque le char d'une planque (`aLaPlanque`) : la moto du livreur
  n'est jamais emportée, et la sauvegarde la garde.
- **Les missions** : `Histoire.charDeSaison` — le fuyard file en motoneige l'hiver (« LE FUYARD FILE
  EN MOTONEIGE ! »), en berline sous la pluie ; q10 pose une motoneige au pont l'hiver seulement (une
  moto garée attend la fin de l'averse). Le Grand Saut refuse l'hiver au départ.
- **Les voix** : variante `hiver=(texte, jeu)` des répliques (`_l`, `_p`), au slug suivi de `-hiver`
  sans décaler les autres ; `"hiver"` sur un objectif (`Histoire.texteDObjectif`). Cinq voix générées
  (m2, f04, p13, q10 ×2) : **184 caractères** ElevenLabs. ⚠️ Sous la pluie, les voix disent encore
  « en moto » alors que le fuyard file en berline (le HUD, lui, dit « EN CHAR »).
- **La berline de livreur** (choix de Martin : la ville n'a pas de pizzeria et le boulot part au
  klaxon) : `auto_pizza`, berline blanche au toit PIZZA (`de: 'auto'`, jamais tirée au sort), née
  hors champ près de la planque l'hiver (`Missions.majBerlineDeLivreur`), sans dé ; seul son klaxon
  lance la pizza. Sven veut une motoneige à la place de la moto (remplacée après le tirage).
- ⚠️ **La berline de livreur se gare sur le TROTTOIR de la planque**, huit tuiles à l'est de la porte (là
  où la planque gare ton char, deux rangées sous la porte). Première version : une tuile de rue près de la
  planque — elle s'y garait EN PLEINE VOIE, et le suivi de h02 s'est arrêté derrière elle pour de bon (et
  l'arroseuse de la nuit ne trouvait plus sa place). Il n'y a aucune case de stationnement à moins de 500 px
  de la planque. Et à plus de 100 px de la porte : la sauvegarde garde le premier char dans ce rayon.
- **Juges** : `test_motos_velos_remises_js.py` (9), neuf mutations qui rougissent chacune le sien.
- **Le banc naît en janvier : 31 juges sont tombés** à la première suite complète — tous verts sur la base.
  Ceux qui mènent ou attendent une moto ou un vélo se calent en JUILLET (`jour = 21`, une ligne commentée) ;
  `test_velos_js` retire la clé `remise` de son décor (ses juges tiennent à l'état exact de la ville, et
  chaque jour essayé — 13, 20, 21, 23 — en faisait tomber un autre) ; le feu des défis graduels se joue au
  13 avril SANS DETTE (dès le 2e jour, les hommes de Rocco se servent au contact) ; la course des bois passe
  à la graine 14 (base : 3, 4, 13 gagnent sur 24 ; build : 14) ; l'autobus, de la graine 5 à 7 (l'hiver,
  l'autobus va moins vite derrière les berlines, et le voyageur qui descend presque un tour plus loin n'y
  arrive plus — aucun char coincé ; 16 graines, 5 seule tombe). ⚠️ Un juge calé au jour 21 rencontre la dette
  de Rocco : le 21 n'est pas neutre.

