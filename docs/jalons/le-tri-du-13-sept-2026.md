# Le tri du 13 sept. 2026

← [les jalons livrés](README.md) · [le plan](../plan.md)

L'introduction de « La suite » telle qu'elle était le 13 sept. 2026 : la règle de priorité (P1 à P4) et la table de tri d'alors, dont presque toutes les lignes sont livrées depuis. La règle vit toujours dans [le plan](../plan.md), « L'ordre » ; ce qui reste à faire, dans sa table « À faire ». Cette version-ci est une photographie.

Règle inchangée : **chaque vague reste jouable, testée, déployée**.

⚠️ **Le tri est un tri de PRIORITÉ, pas de taille.** Quatre niveaux, et ils répondent à une
seule question : qu'est-ce qui coûte le plus cher à ne pas faire ?

- **P1 — le jeu ment.** Quelque chose est promis et pas tenu : un catalogue qui annonce des
  chars que rien ne dessine, un défi affiché qu'on ne peut pas gagner. C'est ce qui coûte le
  plus cher, parce que ça se paie en confiance et qu'aucun ajout ne la rachète.
- **P2 — ça se sent à chaque partie**, et ça coûte une bouchée. Un défaut qu'on rencontre à
  chaque mort, à chaque parc, à chaque nouvelle partie — et dont le mécanisme existe déjà.
- **P3 — ça porte le reste.** Ce qui redessine la ville ou débloque d'autres fiches. À faire
  avant ce qui s'appuie dessus, sinon on ajuste deux fois.
- **P4 — ça enrichit**, du plus utile au moins.

À l'intérieur d'un niveau : le moins cher d'abord, le correctif avant l'ajout, et les
prérequis toujours devant.

⚠️ **Correctif ou ajout, et ça se voit.** Un **correctif** répare une promesse que le jeu
fait déjà et ne tient pas ; un **ajout** en fait une nouvelle. C'est la même coupure que les
préfixes de commit du dépôt, `fix:` et `feat:` — et c'est voulu : ce qui est écrit ici doit
se retrouver mot pour mot dans l'historique.

⚠️ **Les numéros sont des noms, pas un ordre.** M9 s'appelle M9 parce qu'on l'a nommée là,
et le dépôt entier y renvoie — renuméroter casserait tous les renvois pour rien. L'ordre de
travail, c'est celui du tableau ci-dessous, et les sections qui suivent sont dans cet
ordre-là.

| P | Genre | Ce qu'il y a à faire | Taille | Pourquoi là, et ce qu'il attend |
|---|---|---|---|---|
| **P2** | ajout | Des sortes de gens — le réservoir | 3 | ⚠️ **deux vagues livrées** (les trois de Martin, puis cinq des sept « qui viennent avec »). Reste le réservoir, où l'on pige par vagues — plus la **personne âgée** (attend les feux pour piétons) et le **pickpocket** (M12) |
| **P2** | **correctif** | Les véhicules vus **de profil**, comme les piétons | 5 | ⚠️ **avant tout véhicule de plus** — le tramway et le traversier de M12, le sprite du bateau en dette : chaque char dessiné avant la refonte se dessine deux fois. Ne touche **qu'au dessin** (la physique voit toujours un rectangle vu d'en haut), et jette les quatre toits de M9 |
| **P2** | ajout | La ligne d'histoire : une ouverture et un générique | 3 | ⚠️ **l'ouverture est livrée** (16 sept. 2026) — elle ne dépendait de rien ; le **générique**, lui, attend **M13** : il n'y a pas de fin à filmer avant |
| **P2** | ajout | Les missions mises en scène | 3 | ⚠️ **avant M16** : c'est le vocabulaire de plans que ses cent missions écriront, et chaque mission écrite avant lui s'écrirait deux fois. L'ouverture s'y réécrit en premier (ses 13 juges sont la preuve), puis les cinq missions de la v1 |
| **P3** | **correctif** | Le trottoir **et les traverses** de deux tuiles | 2 | ⚠️ redessine la ville : tout ce qui touche à la géométrie passe après |
| **P3** | ajout | Des quartiers qu'on reconnaît : riches, pauvres, et zonés | 4 | ⚠️ redessine ce qu'il y a sur chaque bloc, et **M16** (des lieux nommés dans chaque quartier), les éboueurs et les crimes d'autrui de **M12**, les lignes d'autobus et les chantiers s'y posent : faits avant, ils s'ajustent deux fois. Attend **les bancs et les arbres de rue** (en cours) — c'est le même semis, on le règle par standing au lieu de le refaire |
| **P4** | ajout | M15 La ville te parle | 4 | le narrateur, le journal et les voix existent ; ⚠️ contient un correctif (les passants se répètent) |
| **P4** | ajout | M10 L'argent sale | 3 | **M9** : les guichets se défoncent au camion |
| **P4** | ajout | Ça travaille : chantiers et démolitions | 3 | ⚠️ **la refonte des véhicules d'abord** (la pelle et la grue sont du décor animé tant qu'elle n'est pas faite) ; partage son mécanisme avec les **entraves de M12**, qui s'y branchent au lieu de vivre à part |
| **P4** | ajout | M12 La ville vit | 4 | tramway, traversier et neige touchent à la physique |
| **P4** | ajout | M14 Meta | 4 | de l'**infrastructure** (serveur, BD, comptes, sessions, NIP) : un autre métier que le reste. ⚠️ Rien n'en dépend, et rien n'en doit dépendre : un compte est un **confort**, le jeu se joue serveur éteint |
| **P4** | ajout | Les zones conditionnelles | 3 | avant l'île et avant les entraves de M12 : c'est le mécanisme qu'elles partagent toutes les deux |
| **P4** | ajout | L'Île-aux-Corneilles | 3 | **les zones conditionnelles** d'abord ; l'eau est livrée, le traversier (M12) viendra après et l'île l'attend sans lui |
| **P4** | ajout | Quatre activités que le jeu n'a pas | 2 | ⚠️ la **refonte des véhicules** d'abord (les deux boulots neufs ne demandent aucun char de plus, mais la liste du quai fait regarder le parc de près) |
| **P4** | ajout | M16 Cent missions | 8 (4 × 2) | le **carnet** d'abord (c'est lui qui rend cent missions lisibles) et **les missions mises en scène** (chaque mission porte ses scènes et ses dialogues) ; ⚠️ les dialogues et les scènes sortent du paquet ; M13 en est la dernière tranche |
| **P4** | ajout | M13 Les deux fins | 4 | **M8** pour les districts, et ça gagne à suivre **M10** : la dette de Rocco est le fil des deux fins. C'est la fin — elle se pose en dernier |

M8 porte tout le reste (les gangs, les fins, le traversier, la fourrière ont besoin de la
ville complète) ; il est livré. Rien n'oblige à suivre la liste à la lettre : à l'intérieur
d'un niveau de priorité, on prend ce dont on a envie. Mais **on ne descend pas d'un niveau
tant qu'il en reste au-dessus** — c'est tout ce que le tri veut dire.

Ce que la suite **ne fait pas**, pour que le plan tienne : pas de multijoueur en ligne, pas
de 3D, pas d'histoire à plus de deux fins, pas de génération de sprites par IA. Le jeu
reste un GTA 1 québécois en pixels, joué au téléphone.

⚠️ **Un compte (M14) n'est pas du multijoueur.** Deux joueurs ne se voient jamais dans la
même ville ; le serveur ne fait que garder une partie et un classement. La ligne ci-dessus
tient : c'est une sauvegarde qui voyage, pas une partie partagée — et le jeu continue de
tourner entièrement dans le navigateur, compte ou pas.
