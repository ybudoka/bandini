# Le dialogue attend la fin de la sonnerie

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026) : « quand on reçoit des appels, le dialogue commence après
la fin de la sonnerie ». La première réplique partait sur le même coup d'horloge que
`Son.SFX.telephone()` : le combine sonnait deux secondes PAR-DESSUS la voix du donneur, et on
décrochait avant que ça ait fini de sonner.

**1re vague livrée** (17 sept. 2026) : l'appel d'une mission. `Son.SFX.telephone()` rend ce
qu'elle dure (le `duree_s` du catalogue quand le mp3 joue, 0,37 s pour les trois bips de la
synthèse) et `B.sonnerie` tient qui appelle et à quelle image on décroche. `p.appels` ne se
marque plus qu'au **décrochage** : fermer l'onglet pendant que ça sonne refait sonner l'appel
plus tard au lieu de le perdre. Juge : `test_le_dialogue_de_l_appel_attend_la_fin_de_la_sonnerie`
(deux mutations le font rougir).

**2e vague livrée** (17 sept. 2026) — retour de Martin, sur le narrateur : « il y a une
sonnerie trop forte avant qu'il parle ». Deux choses, mesurées à l'`ebur128` (le fichier, fois
le volume du catalogue — le `volume` seul ne dit rien : la sonnerie est à 0,28 et la voix à
0,85, et c'est pourtant la sonnerie qui sortait plus fort, son fichier étant 9 dB plus haut) :

- **Elle sortait au niveau d'un klaxon.** Téléphone −14,3 LUFS, klaxon −13,1, **la voix
  −20,8** : 6,5 dB AU-DESSUS de celui qui parle ensuite, et c'est un aigu électronique, ce qui
  perce encore plus. À **0,28** elle tombe à −21,2 — juste sous la voix, bien au-dessus d'une
  porte de commerce (−22,9). Juge :
  `test_la_sonnerie_du_telephone_ne_couvre_pas_la_voix_qui_la_suit`.
- **Le Clairon partait dans la même image que la sonnerie de Sal.** Au lever du jour,
  `nuitDeLaDette()` fait sonner le rappel du shylock et `nouveauJour()` enchaînait aussitôt sur
  la manchette : le combiné sonnait par-dessus ses premiers mots. `nuitDeLaDette` rend
  maintenant les images de sa sonnerie, et la manchette attend dans `B.manchette` que le
  combiné se taise (`Missions.maj`). Juge :
  `test_le_narrateur_du_matin_attend_la_fin_de_la_sonnerie`.
**3e vague livrée** (17 sept. 2026) — Martin, en réponse à la 2e : « enlève complètement la
sonnerie quand le narrateur parle ». Attendre ne suffisait pas : le rappel de Sal tombe au
**lever du jour**, dans la même image que la manchette. `nuitDeLaDette` ne fait plus sonner le
téléphone du tout — le message « SAL : TU ME DOIS X $ » reste, c'est lui qui porte la pression
du shylock, et le matin appartient à celui qui lit le journal. `B.manchette` et son attente
s'en vont avec.

- ⚠️ **L'appel d'une mission GARDE sa sonnerie** (1re vague) : elle annonce quelqu'un au bout
  du fil, et le donneur attend qu'elle se taise. Elle descend à **0,26** (−21,8 LUFS) : la
  voix la plus basse des 58 générées (`civil-m3-4`) sort à −21,3, et 0,28 la dépassait de deux
  dixièmes de dB. Le juge compare donc à TOUTES les voix — donneurs, manchette, ouverture — et
  c'est la plus basse qui décide.
- Juge : `test_le_rappel_de_sal_ne_sonne_pas_quand_le_narrateur_parle`. Il **espionne**
  `Son.SFX.telephone` : au banc il n'y a pas d'`AudioContext`, donc compter les sources jouées
  ne dirait rien — ce qu'on veut savoir, c'est si le jeu a DEMANDÉ la sonnerie. Remettre le
  `Son.SFX.telephone()` de Sal le fait rougir.

- ⚠️ **Ce qui n'est PAS corrigé, et qui se mesure aussi** : l'encadré du Clairon tient 420
  images (7 s) alors que 7 des 15 manchettes lues durent plus longtemps — jusqu'à 9,7 s pour
  la leçon du klaxon. Le narrateur finit donc sa phrase sans texte à l'écran. À reprendre le
  jour où la boîte de dialogue saura attendre la voix, comme une réplique de mission le fait
  déjà (`Histoire.majCinema`).
