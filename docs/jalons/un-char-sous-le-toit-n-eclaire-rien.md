# Un char sous le toit d'un garage n'éclaire rien

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (22 sept. 2026), capture à l'appui : un char entré dans une carrosserie, caché sous
le toit — et ses deux phares jaunes et ses deux feux arrière rouges brillent **par-dessus le toit et
l'enseigne**. « Corrige les feux… on devrait rien voir. »

Le toit découpe le DESSIN du char (`Entites.dessiner`, `Monde.rideauPres` : tout ce qui est au-dessus
du bas du rideau, dans le passage). Mais les lampes se composent à la fin de l'image, par-dessus
toute la scène (`Base.fin`) : la découpe ne les atteint pas.

- Ce qui est **sous le toit** ne s'allume pas à l'écran : ni les lueurs des phares et des feux
  arrière, ni le faisceau qui en partirait. Ce qui a passé le linteau (rideau levé, le nez dehors)
  éclaire, lui.
- ⚠️ La même règle que le dessin, lue au même endroit : une lampe cachée est une lampe dont le point
  est dans la zone que le dessin découpe.
