# Les zones conditionnelles

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les zones conditionnelles : une porte, une condition, un prix (**ajout**, taille 3)_

_Demande de Martin (15 sept. 2026) :_ « certaines zones pourraient être bloquées
conditionnellement à des missions ou prérequis. »

⚠️ **La ville est ouverte en entier depuis M1, et elle le restera** — c'est la promesse de la
vision. Ce qui manque n'est pas une clôture, c'est une **raison** : un endroit qu'on regarde
trois jours avant d'y entrer vaut mieux qu'un endroit qu'on traverse sans le voir. Les jeux
qui ont posé la question avant nous répondent toujours pareil : la barrière doit avoir une
**cause dans la fiction** (un pont qu'on répare, un gang qui tient un coin) et non un mur
invisible, et le joueur doit **voir** ce qui le bloque.

Or le jeu a déjà **trois barrières**, chacune écrite à sa façon, et aucune ne se déclare :
la **guérite de la fourrière** (une grille de 4 tuiles, un comptoir, `etoiles_vol` si on
force), les **zones de gang** (`hostile_toujours`, `hostile_si_arme` : ce n'est pas un mur,
c'est une menace) et les **barrages de police** à 5★. M12 en promet une quatrième famille
(les entraves du jour). Quatre mécanismes pour la même idée, c'est trois de trop.

**La règle : une barrière est une fiche, pas un cas.** `carte.BARRIERES` en Python, lue par
le navigateur comme le reste :

- **où** : un rectangle de tuiles, ou la grille d'un lieu spécial ;
- **quoi** : ce qu'elle arrête — `pieton`, `vehicule`, ou les deux. ⚠️ C'est la clé qui évite
  la moitié des pièges : un pont fermé aux **chars** mais pas aux **jambes** bloque sans
  jamais enfermer ;
- **quand** : la condition — `apres: "<mission>"`, `exige: {...}` (le même objet que M16),
  `heure: "jour"|"nuit"`, ou `jour_tire` (la graine du jour : c'est ainsi que les entraves de
  M12 entrent dans le même mécanisme) ;
- **combien** : `forcer` — ce que ça coûte de passer quand même (`etoiles`, `degats`,
  `payer`), ou `null` pour les deux seules qui ne se forcent pas : le barbelé et l'eau ;
- **quoi dire** : `raison`, une ligne en majuscules — « LES SKATEUX TIENNENT LE PONT ». Elle
  s'affiche quand on s'y bute, et le carnet la liste.

**Les huit barrières de départ** (les trois qui existent y rentrent, cinq sont neuves) :

| Barrière | Où | Arrête | Condition | Forcer |
|---|---|---|---|---|
| Le pont de La Pointe | l'unique pont de la carte (`PONTS`) | **véhicules** | ouvert par p02 | passer à pied, ou pousser les cônes au char (dégâts) |
| La guérite de la fourrière | lot de La Shop (existe) | véhicules | payer au comptoir | 1★ (`etoiles_vol`, déjà écrit) |
| La cour de l'usine Prévost | La Shop | les deux | ouverte le **jour** | 1★ et deux gardiens |
| La cour à ferraille de Ti-Loup | La Shop | les deux | après s02 | 1★ |
| L'allée de la villa du maire | Les Érables | véhicules | après e07 (la clé) | 2★ et deux gardiens |
| Le quai du cargo | Les Quais | les deux | ouvert la **nuit** (déchargement) | 1★ et les matelots |
| Les entraves du jour | n'importe quelle rue | véhicules | `jour_tire` (M12) | dégâts, et un détour existe toujours |
| Le traversier | quai → l'Île | — | un horaire, un billet | aucun : c'est de l'eau (voir la fiche de l'Île) |

**⚠️ Les quatre pièges, et ils sont tous du même genre : enfermer quelqu'un.**

1. ⚠️ **Une barrière fermée ne doit jamais couper un chemin de retour.** Le juge se calcule :
   pour **chaque combinaison** de barrières fermées, la composante marchable qui contient la
   planque doit contenir tous les lieux des missions alors disponibles. `composantes_marchables()`
   existe depuis M1, le juge est une boucle par-dessus.
2. ⚠️ **Le trafic doit la voir**, sinon les chars s'empilent devant une grille qu'ils ne
   connaissent pas. Une barrière écrit dans les **masques de tuiles** (comme les entraves de
   M12), pas seulement dans le dessin — et le chien de garde du trafic (dix secondes sans
   bouger) dira tout de suite si on s'est trompé.
3. ⚠️ **Une zone fermée ne se peuple pas.** Les piétons et les chars naissent dans une bulle
   autour du joueur : une cour fermée qui en fabrique quand même donne des gens enfermés qui
   tournent en rond. Ce que la barrière ferme, elle le vide.
4. ⚠️ **On doit voir pourquoi.** La barrière se dessine (une grille, des cônes, une guérite),
   la mini-carte la marque, et `raison` s'affiche quand on s'y bute. Une porte fermée sans
   raison lisible est un bogue, même quand c'est voulu.

**Juges** : aucune combinaison de barrières n'enferme la planque ni ne rend un lieu de mission
inatteignable ; chaque barrière déclare son `arrete`, sa condition, son `forcer` et sa
`raison` ; aucune ne bloque un **piéton** sans qu'un autre chemin existe (seul le barbelé en a
le droit) ; le trafic ne s'empile pas devant une barrière fermée (le chien de garde ne mord
pas plus qu'avant) ; et une zone fermée ne contient aucun piéton ni char né après sa
fermeture.

## Notes

demande de Martin : « certaines zones pourraient être bloquées conditionnellement à des
missions ou prérequis ». Le jeu a déjà **trois** barrières écrites chacune à sa façon (la
guérite de la fourrière, les zones de gang, les barrages à 5★) et M12 en promet une
quatrième : une seule fiche `carte.BARRIERES` — où, ce qu'elle arrête (piéton / véhicule /
les deux), à quelle condition, ce que coûte de forcer, et la **raison** qui s'affiche.

- ⚠️ Le juge qui compte : aucune combinaison de barrières fermées n'enferme la planque ni ne
  rend un lieu de mission inatteignable ✅ **Livré** (15 sept. 2026) : `carte.BARRIERES`, une
  fiche par barrière — `ou` (résolu par le chantier en rectangle de tuiles : le tablier d'un
  pont, la grille d'un lot, le bâtiment d'un lieu garanti plus `marge` tuiles de cour, le
  quai qui porte un ambulant), `arrete` (piéton, véhicule, les deux), `condition` (`apres`
  une mission, `heure` jour/nuit, `jour_tire` pour les entraves de M12, `payer` pour la
  guérite), `forcer` (étoiles, dégâts, ou rien), `raison`.
- ⚠️ **Seule la couronne du rectangle arrête, et seulement quand on vient de l'extérieur** :
  qui est dedans quand elle se ferme en sort librement — c'est ce qui fait qu'une barrière
  bloque sans jamais enfermer, et c'est écrit une fois (`Monde.barriereBloque`), lu par le
  mouvement des piétons, des chars et du trafic. Un char lancé pousse les cônes (dégâts de
  la fiche, une seule fois par traversée) ; à pied, on pousse une seconde — le temps de lire
  la raison —, l'enjambée part, et l'étoile tombe à la retombée. **Le trafic fait
  demi-tour** devant une barrière fermée (la voie d'en face la plus proche) au lieu de
  s'empiler — un juge le tient. Ce qui ferme **se voit** : des cônes sur la couronne d'un
  pont, une chaîne sur des poteaux autour d'une cour ; et le carnet liste ce qui est fermé,
  avec sa raison. **Quatre barrières** : le pont de La Pointe (chars, fermé tant que m2
  n'est pas faite — ⚠️ p02 n'existe pas encore, M16 le remplacera), la guérite de la
  fourrière (déclarée `existant` : `majFourriere` la joue déjà, un juge tient son étoile
  d'accord avec `economie.FOURRIERE`), la cour de l'usine Prévost (les deux, ouverte le
  jour, 1★), le quai du cargo (les deux, ouvert la nuit, 1★ — la run de Sven est une affaire
  de nuit). Les zones de gang et les barrages ne sont pas des barrières : une menace et un
  char en travers ne sont pas des murs à condition. Le juge qui compte tient : toutes
  fermées en même temps, la planque n'est dans aucune et chaque lieu de mission reste à
  portée de jambes ; ce qui ne rouvre jamais tout seul (`apres`) n'enferme aucun lieu ; une
  barrière d'heure ne couvre jamais un lieu de mission. 4 juges Python + 3 de banc ; 1574
  tests. Restent, avec M16 : la cour à ferraille de Ti-Loup (s02), l'allée de la villa du
  maire (e07), et les gardiens
