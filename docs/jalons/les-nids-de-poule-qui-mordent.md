# Les nids-de-poule qui mordent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ les nids-de-poule dessinés dans les rues (les quartiers qu'on reconnaît les
distribuent déjà) cessent d'être du décor — on les sent.

- **Ce qu'ils font** : rouler dedans secoue le char (la caméra tremble), abîme un peu la carrosserie et, à
  grande vitesse, fait perdre le contrôle une fraction de seconde. Plus nombreux dans les quartiers pauvres,
  et **au printemps** du jeu (après la neige de M12).
- **Le boulot** : la voirie — boucher N nids-de-poule en un chrono, avec le camion d'asphalte (`boulots`).
  Un nid bouché disparaît pour de bon.
- **La blague** : le Clairon publie le décompte des nids-de-poule de la ville chaque lundi.

⚠️ **Ce qui guette** : un effet physique neuf sur tous les chars, trafic et police compris — le trafic ne
doit pas perdre ses virages (le juge des coins en L) ; et le nombre de nids est un budget déjà réparti par
quartier : ne pas en ajouter au dé.

**Juges** : un char qui passe dans un nid prend un choc ; un nid bouché ne revient pas ; le trafic ne sort
pas de sa voie à cause d'eux.

⚠️ **Relevé le 26 sept. 2026, avant de s'y mettre — plus gros que « taille 1 ».** Une bonne part mord
DÉJÀ (« le rythme de la ville ») : `Vehicules.majNidDePoule` secoue la caméra, coûte deux points de
carrosserie, fait vibrer la manette et s'entend, avec un répit par nid. Ce qui reste :
- la **perte de contrôle** une fraction de seconde à grande vitesse (le char du joueur seulement : le trafic
  roule sur des rails) ;
- le **boulot de voirie** — les boulots naissent d'un véhicule (on klaxonne au volant), et le parc n'a pas
  de **camion d'asphalte** : un véhicule neuf (fiche, dessin, bruit), c'est ce qui fait la taille ;
- les nids **bouchés pour de bon** (dans la partie, et `carte.nids` qui les oublie) ;
- le **décompte du Clairon le lundi** (le journal est dit par le narrateur : une phrase générique, le
  nombre en texte) ;
- **plus nombreux au printemps** : le jeu a-t-il un printemps ? (la neige de M12 est une météo, pas une
  saison) — à trancher.

### Le plan (26 sept. 2026)

⚠️ **Vu en ouvrant le chantier : les nids ne se DESSINENT pas.** La carte en pose (`nids_de_poule`, plus
nombreux dans les quartiers pauvres), le char les sent — et la chaussée est lisse à l'écran : on les
subit sans jamais les voir venir. D'abord ça.

1. **Les dessiner** : un trou sombre aux bords cassés sur la tuile, à l'écran (`Monde.dessinerNids`).
2. **La perte de contrôle** : à grande vitesse, le char du joueur ne répond plus une fraction de seconde
   (le trafic roule sur des rails, il n'est pas touché).
3. **Le camion d'asphalte** (`asphalte`, `freq` 0) : garé devant la fourrière municipale, il naît à
   l'approche du joueur, comme le camion de crème glacée.
4. **Le boulot de voirie** : au klaxon, trois nids à boucher, à l'arrêt dessus ; un nid bouché disparaît
   **pour de bon** (`partie.nidsBouches`, rendu au chargement).
5. **Le Clairon du lundi** : le décompte des nids de la ville, sous la manchette (tous les sept jours).
6. **Le printemps** : le jeu n'a pas de saisons — à trancher par Martin, pas dans cette vague.

## Notes

_Rien de livré._
