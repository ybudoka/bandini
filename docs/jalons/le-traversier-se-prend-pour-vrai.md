# Le traversier se prend pour vrai

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (26 sept. 2026) : « le traversier a des problèmes, valide-le et teste-le à fond ». Les quinze
juges du traversier étaient verts : ils posent le char pile sur le bout de quai, déjà dans l'axe, et
ne font jamais le chemin d'un joueur. Joué pour de vrai, au banc et dans Chromium :

- **La cabine est en face de la voie de droite.** Aux deux escales, la rue arrive sur deux rangées
  (135 et 136) et le pont en occupe deux autres (134 et 135) : la recherche prenait la place la plus
  au nord à égalité. Qui roule à droite vers l'est fonce dans la cabine (−29 PV) et reste à quai ;
  la voie nord débarque sur le trottoir à La Pointe.
- **Du décor sur le débarcadère.** Un poteau d'amarrage planté sur le bout de quai des Quais, une
  borne-fontaine contre la rampe (−6 PV en montant), une bouée qui flotte là où le pont accoste à La
  Pointe : la grève et le mobilier se posent avant le traversier, sans savoir qu'un quai viendra là.
- **Sauvegarder en pleine traversée, c'est se réveiller à la nage.** La sauvegarde auto (dix
  secondes) tombe pendant la traversée (treize) : la partie rouverte remet le joueur à sa place, au
  milieu de la baie, sans le remettre à bord.
- **Un bloc de carte laisse un pont fantôme.** Aller au chalet pendant que le traversier est à quai,
  revenir après son départ : ses 8 × 3 tuiles restent posées sur l'eau, roulables, cabine comprise.
- **À deux, le deuxième joueur reste à quai** — ou plutôt, il se fait traîner à la nage derrière.

## Notes

**Livré le 26 sept. 2026.** Les cinq, chacun avec son juge — et chaque juge a rougi quand on lui
remettait son bogue.

- **Le pont prolonge la rue** (`traversier.dans_l_axe`) : en remontant chaque rangée depuis le bout
  du quai, tant qu'on est sur la chaussée, on doit croiser une voie est-ouest (`<` ou `>` dans
  `ville["voie"]`) sur les deux rangées du pont, et aucune sur celle de la cabine. C'est la première
  clé du tri des paires, devant la longueur de la traversée. Les deux escales descendent d'une rangée
  (134 → 135) ; le tramway, les grands bateaux et le capitaine Bérubé suivent tout seuls.
- ⚠️ **La rue du quai finit sur un croisement** : quatre tuiles `+` sans sens entre le bout du quai
  et la première flèche, et le croisement couvre aussi la rangée de trop. Tester « la tuile derrière
  le bout de quai est de la chaussée » disait oui aux deux places ; il faut remonter jusqu'à une
  flèche (`AXE_PORTEE`).
- **Le débarcadère est dégagé** (`traversier.degager`, juste après `devants` dans `carte.generer`) :
  la coque à quai, deux tuiles de rive devant le pont, une rangée de plus de chaque côté. Le décor de
  rive (`poteau_amarrage`, `bouee`, `pneu`) s'en va ; le décor mobile glisse à côté par
  `devants._deplacer_le_decor`. Le juge « la ville est la même avec ou sans traversier » compare
  maintenant le décor hors du débarcadère, et exige que ce qui a bougé soit du décor mobile.
- **Une partie rouverte en pleine baie remonte à bord** (`adopter`, à la première image après
  `oublier`) : la place et l'heure se sauvent ensemble, donc un joueur sur le pont de la coque à
  cette heure-là y était. Son char ne se sauve pas : il se réveille à pied, à sa place.
- **Rien dans un bloc de carte** (`B.bloc`, comme `pont.js`) : la carte courante est le bloc, et la
  branche « la ville a été rechargée » oubliait le pont posé sur la vraie ville.
- **À deux** : `Entites.estJoueur` partout où il y avait `B.joueur` (embarquer, suivre, débarquer).
- ⚠️ **Le juge en char lit les voies de LA RUE**, pas celles du pont : écrit dans l'axe du traversier,
  il est resté vert quand on a remis la cabine en face de la voie de droite — l'angle mort même des
  quinze juges d'avant.
