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
