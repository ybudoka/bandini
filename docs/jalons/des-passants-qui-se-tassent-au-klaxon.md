# Des passants qui se tassent au klaxon

← [le plan](../plan.md)

## Fiche

Demande de Martin (30 sept. 2026) : « réduisons le nombre de morts : si un piéton se fait klaxonner,
il se déplace, laisse le véhicule passer et poursuit sa route. Les véhicules n'écrasent
qu'exceptionnellement les piétons. »

**Ce que la sonde a mesuré** — six graines, 6 000 images chacune, le joueur immobile au départ :
**12 passants morts, tous écrasés par un char de PNJ** (l'autobus d'abord, puis le trafic), aucun
par autre chose. À peu près un mort par minute de jeu, sans rien toucher. Les victimes : des
passants qui fuient, qui flânent au bord de la rue, des gars de gang qui traversent pour sauter sur
le joueur.

**Ce qu'on fait** (tranché par Martin) :

- **Le klaxon fait se tasser.** Chaque coup d'avertisseur — trafic, autobus, police, et le joueur —
  fait faire aux passants à pied qui sont devant le char, dans son couloir, un pas de côté vers le
  bord le plus proche. Ils attendent que le char soit passé (quelques secondes au plus), puis
  reprennent ce qu'ils faisaient : leur état, leur cap, leur direction. Qui se bat, qui tient son
  poste ou qui est assommé ne bouge pas.
- **Le trafic klaxonne tôt.** Un char du trafic ou un autobus qui voit un passant dans son couloir
  klaxonne tout de suite (un coup, puis un répit), au lieu d'attendre 3,3 s de patience avant de
  forcer. Et quand il force, il reste sous la vitesse qui renverse : il bouscule, il ne fauche pas.
- **Écraser devient l'exception.** Un char qui n'est pas conduit par le joueur renverse le passant,
  qui se relève blessé et détale ; il ne le tue qu'**une fois sur dix**, à l'empreinte du char et du
  passant. Le train garde sa règle (il n'arrête pour personne), et le joueur au volant ne change
  pas.
- ⚠️ Rien ne tire un dé : `B.rng` décalerait tout le hasard de la ville.

## Notes

Livré le 30 sept. 2026.

- **Le tassement** vit dans `entites.js` : `Entites.klaxonne(v)` (appelé par `Vehicules.avertir`, donc
  par tout avertisseur — klaxon, sonnette, « Gens du pays ») cherche les passants devant le nez, à
  5 tuiles, dans le couloir du char ; `tasser` garde ce qu'ils faisaient (`avantTasse` : état, cap,
  direction, minuterie, porte) ; `majTasse` fait le pas de côté — vers le trottoir si l'autre côté
  est la chaussée — et `reprendre` rend tout quand l'arrière du char est passé, au bout de 4 s, ou
  après 20 images coincé (un trottoir d'une tuile, un mur).
- **Le trafic klaxonne tôt** (`Vehicules.klaxonnerLePassant`, trafic et autobus) : un coup, puis
  3 s de répit ; jamais au feu rouge, celui qui traverse au blanc est dans son droit.
- **Le forçage** (`Vehicules.vitesseDeForce`) : devant quelqu'un à pied, sous `renverse_vitesse_min`.
  Le coupé sport, le cabriolet et la moto forçaient à 1,2–1,3 px/image — de quoi faucher le passant.
- **La règle du PNJ** (`heurterPietons`, `physique.pnj_tue_une_fois_sur` = 10) : `hash2` du char et
  du passant. L'épargné garde 1 PV, **ne saigne pas** (le saignement mord au bout d'une seconde : il
  mourait quand même), roule sur le côté hors du couloir (`PROJECTION_DE_COTE`), se tasse puis
  détale ; `blesser(…, { sansRiposte })` : ni riposte contre le joueur, ni gang alertée, ni dé.
- ⚠️ Deux pièges trouvés par la sonde, pas par les juges : l'épargné saignait à mort, puis,
  projeté devant le char et fuyant droit devant, il se refaisait frapper (51 coups en 10 minutes).
- `test_velos_js` (le vélo du parc) comptait des **images** de trottoir après l'allée ; le trafic
  plus fluide le faisait attendre 98 images sur UNE tuile au bord de la voie. Il compte maintenant
  les tuiles (≤ 3), et rougit toujours quand on lui fait longer quatre tuiles.
- Rouges déjà sur dev, rejoués sur la base : `test_f05…`, `test_e12…` (`test_dix_missions_js`) et
  `test_la_sirene_lance_la_patrouille…` (`test_patrouille_js`).
