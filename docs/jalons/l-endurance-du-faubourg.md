# L'endurance du Faubourg

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : L'endurance est restée celle du Faubourg (**correctif**, taille 2) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « je veux que la course ne consomme plus d'énergie, mais que ce soit le
sprint qui en consomme — étant donné qu'on court quand même tout le temps, avec la grandeur
de la carte. »

⚠️ **Mesuré, et c'est pire que « on court tout le temps ».** Le modèle d'endurance a été réglé
pour le Faubourg de 157 tuiles ; M8 a quintuplé la ville et personne n'y est revenu :

|  |  |
|---|---|
| Un souffle complet de course | **4,2 secondes**, soit 525 px — **33 tuiles** |
| La ville | **421 tuiles** de large |
| Refaire le plein, en marchant | **6,9 secondes** |
| Vitesse **soutenable** (courir, puis marcher pour souffler) | **1,54 px/image** |
| Vitesse du policier à pied | **1,9** |
| Traverser la ville à ce rythme | **73 secondes** |

⚠️ **Le policier court donc plus vite que la vitesse que le joueur peut tenir.** Fuir à pied
ne marche déjà pas — et pendant ce temps, traverser la ville demande de gérer une barre
pendant une minute et quart. La barre ne récompense rien : elle taxe le déplacement.

**Trois vitesses au lieu de deux**, et c'est exactement ce qui est demandé :

|  | Vitesse | Coût |
|---|---|---|
| **Marche** | 1,2 | rien |
| **Course** | ~2,0 | **rien** — la vitesse de voyage, celle qu'on tient de La Pointe aux Quais |
| **Sprint** | ~2,6 | l'endurance, par bouffées |

⚠️ **Mais rendre la course gratuite casse toutes les poursuites à pied si on s'arrête là.** Le
dépôt a déjà écrit pourquoi, dans `economie.py`, à propos du café : « la vitesse, c'est ce qui
sépare le joueur (2,1) du policier (1,9) ; y toucher casserait toutes les poursuites du jeu ».
Une course gratuite à 2,0 contre un policier à 1,9, c'est **s'échapper à pied, toujours, sans
rien dépenser**. La parade est celle déjà écrite deux fois ailleurs — le char rapide, les
armes à feu : **la vitesse achète de la distance, jamais l'impunité**.

- **Le policier court à la vitesse de ta course.** À pied, on ne gagne plus de terrain en
  courant : on en gagne par **bouffées de sprint**, et ça coûte. On sème la police en cassant
  la ligne de vue, en montant dans un char, ou en payant du souffle. C'est mieux que ce qu'on
  a — aujourd'hui la poursuite à pied se perd toujours, et lentement.
- ⚠️ **M5 en dépend** : « semer la police et rentrer » est une mission au tableau. Elle se
  rejoue après le changement, elle ne se suppose pas.
- **Le café et le surplus y gagnent.** Le café divise la dépense du sprint ; le surplus, qui
  vient d'arriver, est ce que le repos ne donne pas. Les deux servaient à courir un peu plus
  longtemps ; ils serviront à **s'échapper** — une bien meilleure raison de s'arrêter au
  kiosque.
- ⚠️ **La barre sera presque toujours pleine**, puisque seul le sprint la vide. Une barre qui
  ne bouge jamais ne dit rien : elle doit se montrer quand elle compte et s'effacer sinon.
- ⚠️ **Le vocabulaire ment déjà.** `VITESSES["joueur_sprint"]` désigne ce qui deviendra la
  **course**, et le commentaire du café raisonne sur « 2,1 contre 1,9 ». Renommer fait partie
  du correctif — `joueur_course` et `joueur_sprint` — sinon la prochaine personne lira le
  contraire de ce que le code fait.
- **Juges** : traverser la ville d'un bout à l'autre ne consomme **rien** ; un policier lancé
  derrière un joueur qui court ne perd pas de terrain ; un sprint plein, café compris, ouvre
  un écart **borné** (le même calcul que pour le char rapide) ; et la durée d'un souffle se
  compare à la **taille de la ville**, pas à un nombre choisi une fois pour toutes.

**Livré le 13 sept. 2026 :**

- **Trois vitesses, un seul bouton** — et la **course est la vitesse par défaut**. Pousser le
  pouce à fond, ou n'importe quelle touche de direction, c'est courir ; l'effleurer, c'est
  marcher ; le bouton, c'est sprinter. ⚠️ **Au clavier, on ne marche donc plus**, et c'est
  voulu : il n'y a pas d'analogique sur un clavier, et inventer une touche « marcher »
  ajouterait une commande pour un usage que personne n'a réclamé. La marche reste là où elle
  se dose — au pouce.
- **Le bouton s'appelle SPRINT**, plus « COURS » : l'étiquette disait le contraire de ce que
  le bouton fait maintenant.
- ⚠️ **La barre de souffle s'efface quand elle n'a rien à dire.** Seul le sprint la vide :
  elle est pleine presque tout le temps, et une barre qui ne bouge jamais ne se lit plus — on
  cesse de la regarder le jour où elle compte. Elle revient dès qu'on entame le souffle, qu'on
  a du surplus ou qu'on est sous café, et s'attarde une seconde pour ne pas clignoter.
- **Le vocabulaire a été corrigé** : `joueur_course` (gratuite) et `joueur_sprint` (payante).
  L'ancien `joueur_sprint` désignait ce qui devient la course, et le commentaire du café
  raisonnait sur « 2,1 contre 1,9 » — la prochaine personne aurait lu le contraire de ce que
  le code fait.
- **Juges (3 neufs, 1 réécrit)** : traverser la ville d'un bout à l'autre — 421 tuiles, 56 s
  de touche tenue — ne coûte **rien** ; un agent lancé derrière un joueur qui court ne perd
  **pas un pixel**, et le même agent, même décor, perd **plus de trois tuiles** quand le
  joueur sprinte (et le souffle baisse) ; l'écart d'un sprint plein, café compris, reste
  **borné** sous quatre fois la portée de vision d'un agent ; et le juge du mouvement mesure
  maintenant les **trois** vitesses au lieu de deux. ⚠️ Le juge de la fuite est une vraie
  poursuite simulée, pas un calcul : c'est la seule façon de voir que le A\* de l'agent, ses
  virages et ses sous-pas ne lui rendent pas le terrain que la vitesse lui refuse.

## Notes

demande de Martin (« que la course ne consomme plus d'énergie, mais que ce soit le
sprint ») : le modèle avait été réglé pour le Faubourg de 157 tuiles et M8 a **quintuplé la
ville**. Un souffle valait **33 tuiles sur 421**, et la vitesse qu'on pouvait tenir tombait
**sous celle du policier** — la barre ne récompensait rien, elle taxait le déplacement.
**Trois vitesses** : marche 1,2 · **course 2,0, gratuite** · sprint 2,6, qui coûte.

- ⚠️ Et le policier court **exactement** à la vitesse de la course, sinon une course
  gratuite serait l'impunité : on gagne du terrain par **bouffées de sprint**, ou en cassant
  la ligne de vue. La barre s'**efface** quand elle n'a rien à dire, et le bouton s'appelle
  **SPRINT**
