# Une chaloupe sur la route

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui : « un bateau sur la route ?? » — une chaloupe arrêtée
dans sa voie au passage piéton, cap à l'est.

- ⚠️ **Ce n'était pas l'amarrage** : les dix-huit places sont bien sur l'eau. **C'était un
  VOL.** Le voleur de char (`Entites.majVolDeChar`) prend le premier véhicule garé à
  l'écran, et une coque amarrée est `stationne` comme une auto : pour un passant du quai,
  c'était elle. Volée, elle passait au trafic (`conducteur: 'trafic'`), et **le trafic roule
  sur des rails sans lire une seule tuile** (`v.x += v.vx`) — `tuileInterdite`, la seule
  règle qui tient une coque sur l'eau, n'y est jamais consultée. La voie la plus proche
  (`voieLaPlusProche`, trois tuiles) l'attendait sur la rive : elle y montait et faisait sa
  tournée. **Mesuré au banc avant** : visée, emportée, puis **911 images sur 1 500 au sec**,
  cap à l'est sur une chaussée. ✅ **Livré** (16 sept. 2026) : **on vole un char, pas un
  bateau** — le voleur ignore une coque (`def.eau`) ; et **le trafic ne navigue pas** — une
  coque qu'on lui confierait est lâchée sur place, sans conducteur (`majConducteur`), pour
  le prochain chemin qui le ferait.
- ⚠️ Au banc, **le témoin compte autant que la règle** : une auto garée au même endroit se
  fait toujours voler — sans lui, un voleur qui ne vole plus rien passerait le juge.
- ⚠️ Et le juge cherche son eau **dans la carte, pas dans `amarrages`** : une autre session
  déplace les chaloupes vers la baie le même jour. 2 juges neufs dans `test_ville_vit.py`
  (429 images au sec pour une coque confiée au trafic, avant), 1836 tests.
