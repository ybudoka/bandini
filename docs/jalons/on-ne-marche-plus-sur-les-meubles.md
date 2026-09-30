# On ne marche plus sur les meubles

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « on ne doit pas pouvoir marcher sur les meubles ». Jusqu'ici c'était
voulu : un meuble d'intérieur (`c` comptoir, `l` lit, `a` table, `h` chaise…) est `solide 3`,
un obstacle BAS qui arrête un char mais pas un piéton — par peur qu'un meuble coince le joueur
dans une pièce (`carte.py`, « Dedans : les planchers et les meubles »). Le mobilier de rue et les
décors de la planque, eux, sont déjà solides.

Le changement : un bit `MEUBLE` dans les masques du piéton, du joueur (et des agents) et des
chemins à pied ; l'escalier `/` reste marchable (on y marche pour monter). Côté serveur,
`marchable()` ne compte plus un meuble, et le juge des pièces mesure l'atteignable sans passer
dessus : un coin coupé derrière un comptoir est permis (le commis y reste), un point d'action,
un client ou une tuile de sortie coincés ne le sont pas.

- ⚠️ La sonde du 30 sept. : 14 pièces sur 126 se coupent ; à redessiner celles dont un point
  n'est plus atteignable (le hacker de l'électronique, repeindre au garage, le journal du
  kiosque, fouiller dans deux logements). La ville et les blocs ne se coupent nulle part
  (aucun meuble en ville ; la villa garde ses trois morceaux).
- ⚠️ Se lever d'un lit pose déjà les pieds à côté (`seLever`) ; les gens assis ou couchés
  naissent dans leur meuble et n'en sont pas éjectés (collision par bord de tuile).
