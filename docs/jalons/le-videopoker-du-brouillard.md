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

**Livré le 26 sept. 2026.** Une borne noire au voyant qui clignote (le meuble `S`), au fond du Brouillard
et chez Ti-Paul ; ACTION dessus ouvre la machine.

- **Un menu, pas un écran à part** : DONNER (5 $), puis les cinq cartes en lignes — GARDÉE / JETER — et
  TIRER. Le clavier, la manette et le doigt savent déjà s'en servir ; les cartes, elles, se dessinent à
  côté (rang, couleur en pixels), avec la table des gains en dollars dessous, et la main qui vient de payer
  s'allume. Le menu reste ouvert d'une main à l'autre ; on part par B ou Échap.
- **La table** : valets ou mieux, 6/5 à une pièce (`app/videopoker.py`). **« RETOUR 93 % »**, mesuré :
  deux cent mille mains jouées par un habitué en Python, dix mille dans la vraie machine au banc — elle
  rend moins qu'on y met, et même jouée à la perfection, cette table reste sous 96 %.
- **Son hasard est à elle** : le paquet de la main n° _n_ se bat avec `mulberry(graine de la partie ×
  n)`, jamais `B.rng()` — cent mains jouées ne changent pas le tirage suivant du jeu (jugé).
- **Quarante mains par jour**, toutes machines comprises ; le lendemain, elle remange.
- **Juges** : `test_videopoker.py` (l'évaluation, la table, le retour mesuré) et `test_videopoker_js.py`
  (au bouton dans les deux pièces, garder et tirer, l'évaluation du navigateur = celle de Python sur deux
  mille mains, le hasard intact, dix mille mains sous 100 %, la limite du jour) ; trois mutations le font
  rougir (les cartes à `B.rng()`, pas de limite, des gains doublés).
- **Pas encore** : la taverne (un intérieur généré, pas un plan écrit — sa machine viendra avec les
  enseignes qui ouvrent pour vrai) et la mission de Ti-Paul qui soupçonne sa machine (M16).
