# Le voleur de moto est dessus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « un voleur qui vole une moto n'apparait pas dessus ».

- ⚠️ **Mesuré** : la moto volée partait **vide** — `cavalierDe` nul, peinte en une seule
  image, et si le joueur la reprenait, c'est un inconnu qui en descendait. Le passant qui
  vole un char garé (`Entites.majVolDeChar`) **disparaît** dedans et le confie au trafic :
  voulu pour une auto, où l'on ne voit pas le volant. Mais un deux-roues du trafic
  **montre** son pilote (`v.pilote`), et `emporterLeChar` n'en posait pas. Le voleur monte
  maintenant en selle **avec ses couleurs** — tout sprite qui déclare une `selle`, donc la
  moto et le vélo —, et c'est **lui** qui descend quand le joueur la lui reprend (le
  carjacking lisait déjà `v.pilote`). Aucun dé de plus. 1 juge neuf (`test_ville_vit.py`),
  **rouge avant** sur la selle vide. 2500 tests jugés dans un worktree isolé, et les
  fichiers touchés rejugés sur le HEAD des quartiers.
