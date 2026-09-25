# Le vidéopoker du Brouillard

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ une machine qui clignote au fond du bar et du dépanneur, et qui mange ton argent comme
les vraies — un vice de plus pour une ville qui en a.

- **Où** : au Brouillard, au dépanneur de Ti-Paul, à la taverne (des points de pièce `machine`).
- **Le jeu** : un poker à cinq cartes, on garde, on retire, la main paie selon une table affichée. Les
  directions et ACTION suffisent (le même axe unifié que le piratage) — il se joue au doigt, à la manette
  et au clavier.
- **L'honnêteté du jeu** : la machine rend **moins** qu'on y met, en moyenne, et le dit (« RETOUR 92 % » en
  petit). Un jeu d'argent qui paierait plus qu'un boulot à l'heure casserait l'économie : même règle que
  les défis de la foire, qui ne battent jamais un boulot honnête.
- Une mission peut s'y accrocher : Ti-Paul soupçonne sa machine d'être truquée (M16, un `pirater`).

⚠️ **Ce qui guette** : les cartes se tirent au dé — **pas `B.rng()`** (il décalerait tout le hasard du
jeu, règle 8 de `ecrire-drole.md`) : un générateur à part, graine de la partie. Et une limite par jour,
sinon un joueur patient « farme » les gros lots.

**Juges** : sur dix mille mains, le retour moyen reste sous 100 % ; jouer au vidéopoker ne change pas le
prochain `B.rng()` ; la table des gains affichée est celle qui paie.

## Notes

_Rien de livré._
