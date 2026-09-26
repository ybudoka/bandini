# La motoneige

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ le véhicule de l'hiver — elle va partout où la neige tombe, les parcs, les bois,
la baie gelée (le pont de glace).

- **La bête** : une fiche de véhicule de plus (`vehicules.CATALOGUE`), rapide dans la neige, lente et
  bruyante sur l'asphalte déblayé (la charrue de M12 note les tuiles déblayées).
- **Où la trouver** : garées devant les chalets et aux Érables, l'hiver seulement.
- **Un défi** : une course dans les bois de La Pointe (les courses aux flèches existent).

⚠️ **Ce qui guette** : un sprite de plus, vu de haut et de profil (les véhicules vus de profil) ; et une
adhérence qui dépend du sol — le trafic ne la conduit pas, seulement le joueur.

**Juges** : elle va plus vite dans la neige que sur l'asphalte ; elle n'apparaît que l'hiver ; elle atteint
sa vitesse (la friction déduite).

## Notes

_Livré le 26 sept. 2026._ ⚠️ **L'hiver du jeu** : la saison du calendrier (`calendrier.py`, décembre à
mars) ET l'option « NEIGE (ESSAI) » — sans neige, pas de motoneige.

- **La bête** (`vehicules.CATALOGUE`, `motoneige`) : classe `moto` (on la voit, on s'y assoit, on en est
  éjecté contre un arbre), 4,6 px/image, `freq` 0 (le trafic ne la conduit pas). Son dessin
  (`MACHINE_MOTONEIGE`) : deux skis et leurs spatules devant, la chenille et ses crampons derrière, un
  capot de couleur, un pare-brise, la selle à la hauteur de celle de la moto.
- **Le sol** (`Vehicules.allureDuSol`, `hors_neige` de la fiche, 1 pour tous les autres) : pleine vitesse
  dans la neige qui tient (pas derrière la charrue), sur la glace de la baie (le pont de glace), et
  l'hiver HORS des rues — parcs, bois, grève : la neige n'y est jamais déblayée (sans cette règle, la
  neige ne tient au sol que les soirs de tempête et le lendemain, et la motoneige se traînait le reste
  de l'hiver). Sur l'asphalte et les trottoirs : 45 % de sa vitesse et de son élan.
- **Où la trouver** (`Missions.majMotoneiges`) : deux motoneiges garées dans la rue la plus proche du
  cœur des Érables (pas celle du camion de crème glacée), nées à l'approche hors champ ; l'hiver fini,
  celles qu'on n'a pas prises repartent, hors champ elles aussi. Les chalets (un bloc de carte d'une
  autre session) n'en ont pas encore.
- **La course des bois de La Pointe** (`missions.DEFIS`, `motoneige` ; `app/motoneige.py` ; l'épreuve
  `balises` de `Conduite`) : un ALLER-RETOUR du phare au bout des sentiers (le plus long d'un seul tenant
  ne fait qu'une soixantaine de tuiles : quatre secondes, pas une course), huit fanions peints à passer
  dans l'ordre, 24 s. La motoneige attend au départ ; l'été, « ÇA SE JOUE L'HIVER, DANS LA NEIGE ». Elle
  s'ouvre après le tour des Érables. Le juge la court en suivant les sentiers et en levant le pied dans les
  virages : 14 s. En ligne droite, on rentre dans un arbre et on vole par-dessus le guidon.
- **Juges** : `test_motoneige.py` (la fiche, la course sur les sentiers, le défi) et `test_motoneige_js.py`
  (elles n'attendent aux Érables que l'hiver avec la neige, jamais au démarrage, et repartent au
  printemps ; la pointe sur l'asphalte est la part `hors_neige`, pleine hors des rues ; la course se
  gagne l'hiver et ne part pas l'été). Chaque juge a été vu rougir sous sa mutation.
- **Pas fait, à dire** : pas de bruit de moteur à elle (celui de la moto) ; pas de motoneiges devant les
  chalets.
