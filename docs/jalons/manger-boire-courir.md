# Manger, boire, courir

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« il faut que la bouffe redonne de l'énergie et le café permet de courir
plus longtemps ») : un kiosque ne rendait que des **PV**, et le souffle (`endurance`, 100
points, 0,4 par image au sprint) ne se refaisait **qu'en arrêtant de courir** — autrement
dit, les quatre commerces de trottoir ne servaient à rien à la seule minute où l'on en a
besoin, celle où la police est derrière. Manger rend maintenant les deux (`*_souffle` dans
`economie.TARIFS` : hot-dog +40, poutine +70, café +30), et ce qui coûte plus cher nourrit
plus, en vie **comme en jambes**.

- ⚠️ **Le café n'achète que de la DURÉE.** Pendant 90 s (`economie.CAFE`) le sprint ne coûte
  que la **moitié** : 4,2 s de course d'une traite deviennent 8,4 s. Sa vitesse, elle, ne
  bouge pas d'un pixel — les 2,1 du sprint contre 1,9 au policier et 1,35 au fuyard sont ce
  qui rend une poursuite **gagnable des deux côtés** ; y toucher pour 4 $ aurait cassé
  toutes les poursuites du jeu d'un coup, alors un juge mesure la distance par image sous
  café et la refuse si elle change.
- ⚠️ C'est une **minuterie, pas une dépense** : elle s'écoule dans `Missions.maj` (donc
  aussi au volant et dans une pièce, là où `majJoueur` ne passe pas), elle ne s'**empile**
  pas (un deuxième café repart le compte — sinon on s'achète l'endurance infinie à 4 $) et
  elle ne survit ni à la nuit ni à l'hôpital.
- ⚠️ Et elle **se voit** : la barre d'endurance passe au vert et clignote la dernière
  seconde, parce qu'un souffle long qui s'arrête au milieu d'une fuite sans rien annoncer se
  lit comme une panne. Le **casse-croûte sert le café** lui aussi : la roulotte du trottoir
  ferme de 14 h 24 à 4 h 48 et elle était le seul endroit du jeu où courir plus longtemps
  s'achetait. 4 juges Python (la bouffe rend du souffle sans faire déborder la barre, la
  poutine vaut son prix, le café n'achète que de la durée et dure plus qu'un plein de
  souffle, seul le café réveille) + 2 de banc (manger remonte le souffle et ne déborde pas,
  un hot-dog ne réveille pas ; sous café on tient **deux fois plus d'images à la même
  vitesse**)
