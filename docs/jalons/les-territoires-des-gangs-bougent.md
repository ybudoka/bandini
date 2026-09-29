# Les territoires des gangs bougent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ la carte des gangs vit — quand tu affaiblis un gang, son voisin grignote son
territoire, et une mission peut le renverser.

**Aujourd'hui** chaque gang a sa zone fixe (`pietons.GANGS`, `carte.zones`), et M16 prévoit `libere` (un
district libéré : le gang devient des passants) et `calme` (l'hostilité tombe). Rien ne bouge entre les
deux.

- **La force d'un gang** : un nombre par gang, dans la partie. Coucher ses membres la fait baisser, le temps
  la fait remonter lentement.
- **La frontière** : chaque nuit, un gang plus fort que son voisin lui prend un coin de rue (un bloc de la
  zone) ; les couleurs de la carte et les graffitis suivent (les devantures et graffitis existent).
- **Les missions** : « reprendre le coin » (un `tuer` sur le bloc disputé) rend le coin à qui tu veux.
- **Le lien avec `libere`** : un district libéré sort du jeu ; ses voisins ne peuvent plus le grignoter.

⚠️ **Ce qui guette** : les zones servent partout (piétons, hostilité, missions `zone:`) — une zone qui
bouge doit rester un **calcul** (la force + le jour), jamais une simulation qui dérive ; et la ligne « La
réputation et la lecture des passants » touche au même sujet : à trancher ensemble.

**Tranché avec Martin (29 sept. 2026)** :
- **Un coin par nuit** : chaque nuit, un gang plus fort que son voisin lui prend UN îlot à la frontière.
- **Coucher ses membres** l'affaiblit (assommé ou tué) ; sa force remonte doucement avec le temps. (Ni les
  missions ni les commerces volés, pour cette vague.)
- **Il garde son cœur** : son îlot d'origine (sa cour, son QG) ne se prend jamais par la frontière — pour lui
  prendre son district, il faut une mission (`libere`, M16).

**Juges** : un gang qu'on affaiblit perd un coin la nuit suivante ; le coin repris change de couleur et de
piétons ; une zone `libere` ne bouge plus ; tout survit à une sauvegarde.

## Notes

### Vague 1 — la force, la frontière qui bouge la nuit, l'îlot pris qui se vit — **livrée le 29 sept. 2026**

- ⚠️ **Mesuré avant de coder : le territoire d'un gang, c'était sa COUR.** Les zones de district n'ont pas de gang ;
  seule la cour en a un, et c'est là seulement que ses membres naissent et défendent. Les cours de deux gangs
  voisins sont loin l'une de l'autre : la frontière se joue donc à l'échelle des DISTRICTS, îlot par îlot.
- **La carte des îlots** (`app/territoires.py`, dans le paquet des définitions : `pietons.territoires`) : les
  îlots de chaque district de la ville d'avant, le gang du départ, et le **cœur** de chaque gang — les îlots de
  sa cour (le glyphe `g` du plan et ce qu'il a avalé). La bande nord n'en est pas : son gang du Canton sera les
  Mantes.
- **La partie** garde le reste : `forcesDesGangs` (absente = pleine, 100) et `territoires` (« bx,by » → le gang
  qui a PRIS l'îlot). Une nouvelle partie n'a rien de pris : rien ne change au départ.
- **Coucher un membre** (assommé ou tué, par un joueur) coûte 4 à son gang — une fois par membre (`compteGang` :
  un deuxième coup sur un assommé ne compte pas). Il reprend 8 par jour.
- **La nuit** (`Territoires.nuit`, dans `Missions.nouveauJour`) : pour chaque paire de gangs, le plus fort de 15
  au moins prend UN îlot au plus faible — un îlot à lui, voisin d'un îlot du fort, jamais son cœur ; choisi à
  l'empreinte du jour, sans dé. Un district libéré (`libere`) sort du jeu. Le Clairon le dit (« LES CHEVREUILS
  ONT PRIS UN COIN AUX CRAVATES »).
- **L'îlot pris se vit** : `Territoires.gangA` remplace « le gang de la zone » là où il se lisait — la naissance
  des membres (`Entites.peupler`) et l'hostilité à l'arme au poing. Chez lui = sa cour, ou un îlot que son gang a
  pris. Les îlots d'origine restent ce qu'ils étaient (pas de gang dans la rue hors de la cour).
- **La grande carte** (touche N) peint les îlots pris aux couleurs de qui les tient (la couleur du haut de ses
  membres).
- **Juges** : `test_territoires.py`, `test_territoires_js.py` (rien de pris au départ ; un membre couché compte
  une fois ; la nuit prend un coin par voisin plus fort, jamais le cœur en soixante nuits — témoin : à forces
  égales, rien ; un district libéré sort du jeu ; l'îlot pris se peuple de son nouveau gang ; tout survit à la
  sauvegarde). Deux mutations rouges.
- **Reste, vague 2** : reprendre un coin (une mission ou une activité qui rend l'îlot), les graffitis qui suivent
  la frontière, une légende des territoires sur la carte, et le Petit-Canton quand les Mantes y seront.

### Vague 2 — reprendre un coin, le nom sous la mini-carte, la légende — **livrée le 29 sept. 2026**

- **Reprendre un coin** (`Territoires.couche` → `reprendre`) : dans un îlot qu'un gang a PRIS, coucher quatre de
  SES membres le même jour (`regles.reprise`) le rend au gang de son district. Le jeu compte à voix haute
  (« COIN DISPUTÉ · 3 / 4 », puis « LE COIN EST REPRIS · LES CRAVATES SONT CHEZ EUX »). Le compte est par îlot et
  par jour (`partie.reprises`) : trois un jour et un le lendemain ne suffisent pas ; un membre couché hors de
  l'îlot, ou d'un autre gang que l'occupant, ne compte pas. Sans script, sans voix : une activité, pas une
  mission.
- **Le nom sous la mini-carte** (`Hud.nomIci`) : dans un îlot pris, le nom du gang qui le tient, en rose — comme
  dans une cour.
- **La légende de la grande carte** (`Territoires.dessinerLaLegende`) : « COINS PRIS », une puce de la couleur de
  chaque gang qui en tient, dans la marge de gauche ; rien tant que rien n'est pris.
- **Juges** : deux de plus dans `test_territoires_js.py` (la reprise et ses trois témoins ; le nom et la légende).
  Une mutation rouge (la reprise qui compterait n'importe quel gang) — après avoir ajouté le témoin qui manquait.
- **Reste** : les graffitis qui suivent la frontière (ils sont cuits dans les morceaux de carte : les recuire), et
  les Mantes du Petit-Canton dans le jeu des territoires (la bande nord a sa propre trame).
