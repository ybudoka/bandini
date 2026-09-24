# Le taxi de Marco n'est pas à vendre

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le taxi de Marco n'est pas à vendre (**correctif**, taille 1) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « il ne faut pas pouvoir vendre le taxi de Marco. »

⚠️ **Et ce n'est pas une question d'argent : c'est une histoire qui s'arrête.** M3 pose le
taxi à `porte:garage` — la porte **même** du garage où Ti-Guy rachète n'importe quel char
garé devant (`charDevant()` : le plus proche dans les 90 px, sans une seule question sur à
qui il est). Trois pas, 175 $, et le taxi **sort du monde** : `menuGarage` le retire de
`B.exterieur.entites`. L'objectif « MONTE DANS LE TAXI DE MARCO » attend alors un char qui
n'existe plus — et **la mission ne rate même pas** : `monter` et `livrer` ne font échouer que
sur une **épave**, jamais sur une absence. `p.mission` reste pris, `disponibles()` ne rend
donc plus rien, le téléphone ne sonne plus jamais, et il faut **se faire arrêter**
(`m3.echec` contient `arrete`) pour s'en sortir.

**Le remède dit à qui est le char, et il le dit en Python.** `aToi` existait déjà — un char
**payé** au guichet de la fourrière, sans quoi monter dans le sien était un vol ; il lui
manquait son contraire. `aQui` porte le **slug du personnage** à qui le char appartient, il
vient de la fiche (`prete` sur l'objectif `monter` de `missions.py`), et le navigateur ne
fait que le lire : le menu affiche « IL EST À MARCO » avec le nom de `PERSONNAGES`. Une
ligne grise **qui donne sa raison**, plutôt qu'une vente disparue sans explication.

- ⚠️ **Deux refus, deux raisons, et elles ne se recouvrent pas.** `aQui` dit *à qui il est*
  et ne s'efface **jamais** : le taxi reste à Marco une fois M3 finie, alors que `livrer`
  remet `mission` à `null`. `mission` dit *il sert à quelque chose en ce moment* : ça couvre
  l'**auto-patrouille de M4**, qu'on ne prête pas mais qu'on ne peut pas vendre avant de
  l'avoir larguée — s'arrêter à cinq tuiles du garage, entrer et vendre prenait la mission
  exactement de la même façon.
- **RÉPARER reste ouvert** : Marco veut son taxi **entier**, et le garage est justement là
  pour ça.
- ⚠️ Le refus est **dans `faire`** autant que dans `actif` : un item grisé ne se déclenche
  pas au clavier, mais c'est le **menu** qui le garantit, pas la vente. Appelée en direct,
  elle rend `false` et fait le bruit du refus.
- **Juges** : un Python (un char prêté l'est par un **personnage connu**, sur un objectif
  `monter` ; le taxi de M3 est à son **donneur**) et un de banc en **trois temps** — pendant
  la mission, **après la livraison** (`mission` tombé, `aQui` resté), et une auto de
  n'importe qui garée à la même place, qui elle **se vend toujours** : sinon on aurait
  réparé la fuite en fermant le garage.
- **Resté ouvert, et c'est une question pour Martin** : monter dans le taxi que Marco te
  **prête** compte encore comme un **vol de véhicule** (`Vehicules.monter` : un char
  stationné qui n'est ni volé ni `aToi`), donc un passant peut te dénoncer pour un char
  qu'on t'a confié. `aQui` donne de quoi le corriger en une ligne — mais c'est un choix de
  jeu, pas un bogue à trancher tout seul.

## Notes

demande de Martin : « il ne faut pas pouvoir vendre le taxi de Marco ». Le garage de Ti-Guy
achète **n'importe quel char garé devant sa porte**, et M3 pose le taxi à `porte:garage` —
cette porte-là. Vendu, il sort du monde, et ⚠️ **la mission ne rate même pas** (`monter` et
`livrer` n'échouent que sur une **épave**) : elle reste prise, le téléphone ne sonne plus
jamais. `aQui` — le contraire de `aToi` — dit à qui est le char, vient de la fiche (`prete`
dans `missions.py`) et **ne s'efface jamais** : le taxi est à Marco avant, pendant et après.
Le menu le dit au lieu de le cacher : « IL EST À MARCO ». 2 juges
