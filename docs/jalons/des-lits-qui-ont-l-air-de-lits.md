# Des lits qui ont l'air de lits

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« les lits existants doivent vraiment avoir l'air de lits, juste un set
d'oreillers et des couvertes ; actuellement c'est 2 ou 4 cases avec chacune leur
oreiller »).

- ⚠️ Le peintre du lit ne savait pas qu'il avait des voisines : chaque tuile `l` dessinait
  son oreiller, sa couverture et son ombre, donc un lit de 2 × 2 (tous les lits du jeu :
  planque, hôpital, hôtel, phare, logements) était **quatre lits d'une place collés**. Le
  remède était déjà écrit trois fois dans `monde.js` : le lit **lit ses voisines** comme la
  clôture et le toit (`varianteDeLit`, le masque des côtés où le lit continue — 1 nord, 2
  est, 4 sud, 8 ouest). Le peintre n'a plus qu'une règle : la **tête de lit et l'oreiller**
  ne vont qu'aux tuiles sans lit au nord, l'oreiller et la couverte **courent d'une tuile à
  l'autre** sans couture (le piqué de la couverte tombe sur la même grille de 4 px des deux
  côtés de la couture), et le **cadre de bois ne se ferme que là où le lit s'arrête** — avec
  un pixel de plancher devant, comme tous les meubles, et l'ombre au pied seulement.
- ⚠️ Le corollaire, gardé par un juge des plans : **deux lits ne se touchent jamais**
  (collés, ils seraient peints comme un seul lit de quatre de large) et un lit est un
  rectangle plein d'au plus deux tuiles de côté — pas de lit en L sans tête. Un lit d'une
  seule tuile, d'une tuile sur deux ou de deux sur une se dessine aussi, la même règle
  suffit. Juges : 29 en Python (`test_interieurs.py`, un par pièce) + 1 de banc
  (`test_interieurs_js.py` : les quatre variantes lues dans la planque, puis les traces des
  quatre tuiles — un oreiller par tuile de tête et aucun au pied, à cheval sur la couture,
  la couverte continue, le cadre qui laisse son pixel de plancher au nord-ouest et pas à la
  couture). Vu à l'œil dans un rendu des traces (2 × 2, 1 × 2, 2 × 1, 1 × 1)
