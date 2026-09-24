# Des chars qui montrent leur longueur

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

réponse de Martin (« oui plus long ») : de dos et de face, la berline en volume occupait 21
rangées pour 28 px de long — le sol se voyait du biais de l'ombre (0,5), là où l'ancien toit
tourné en montrait 28. **Livré** : le parc entier se projette à **0,75** (`BIAIS_DU_SOL`,
une seule constante pour toutes les machines) et son ombre suit
(`vehicules.OMBRE.profondeur`). Mesuré après, de dos : berline 28 rangées pour 28 px, sport
26/26, luxe 32/32, vélo 16/16 — les plus hauts en prennent davantage (autobus 55 pour 48,
parce qu'il monte).

- ⚠️ **L'ombre d'un passant n'a pas suivi**, et c'est voulu : elle comparait jusqu'ici son
  12 × 6 au biais du char, faute d'autre référence ; la référence d'un char est maintenant
  son propre dessin, et le juge le dit.
- ⚠️ **Ce que le biais plus long a déplacé**, mesuré juge par juge : les toiles du camion
  (76), de l'autobus (80), de la berline (48), de la luxe, de la sport, de la moto et de la
  remorqueuse rognaient le toit vu de dos ; l'ambulance, déjà au plafond de sa toile, perd
  moins d'un pixel de caisse ; un trait peint sur une surface doit passer devant d'au moins
  le biais — le damier du taxi disparaissait (avance 1) et le pied de la lunette de la
  familiale tombait un rang trop haut ; les phares de la remorqueuse se voyaient à 22 caps
  (26 maintenant) ; le guidon de la moto recule d'un demi-pixel pour rester dans la main du
  motard vu de dos. 1 juge revenu, « de dos un char montre sa longueur », **rouge avant** au
  biais d'avant (« auto vu de dos : 21 rangées pour 28 px de long »), et « le sol se voit du
  même biais sous un char et dans son dessin » remplace la comparaison au passant. 2310
  tests
