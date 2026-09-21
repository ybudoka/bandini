# Le carnet

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le carnet : la mission, le journal, le répertoire (**ajout**, taille 2) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « je veux pouvoir avoir un rappel de la mission en cours dans le menu.
Un journal et un "bestiaire" avec les personnages connus. »

Une seule entrée au menu Pause — **LE CARNET** — et trois pages. ⚠️ Il n'invente **aucune
donnée** : tout est déjà là, et n'est montré nulle part.

- **EN COURS.** `Histoire.ligneObjectif()` écrit déjà une ligne en haut de l'écran, et
  `Histoire.cible()` pose déjà le point du GPS — mais une ligne de trente caractères ne dit
  ni qui t'a donné ça, ni ce que tu as déjà fait, ni ce que ça paie. La page donne le titre,
  le donneur, **les objectifs faits barrés et celui qui reste**, la récompense promise et où
  c'est. ⚠️ Elle rappelle **ce qu'il faut faire**, elle ne raconte pas l'histoire : quelqu'un
  qui rouvre le jeu après trois jours doit savoir où aller en deux secondes.
- **JOURNAL.** Ce qui s'est passé, en ordre, daté au jour de jeu : missions finies, défis,
  manchettes du matin, arrestations, propriétés achetées, premières fois (le premier char
  volé, le premier boulot). ⚠️ **Il s'écrit tout seul** à partir de ce que le jeu émet déjà
  (`Histoire.evenement(...)`, `p.stats`) — le jour où c'est une deuxième comptabilité à tenir
  à la main, elle dérive de la première et plus personne ne sait laquelle a raison.
- **RÉPERTOIRE** (le « bestiaire »). Les gens qu'on a rencontrés : leur visage — on a déjà
  leurs couleurs de palette dans `missions.PERSONNAGES` et le sprite 12×16 pour le dessiner —,
  leur nom, ce qu'on sait d'eux, et la dernière chose qu'ils ont dite. Les gangs y ont leur
  fiche aussi : `pietons.py` les décrit déjà, avec leur territoire.

⚠️ **Rien ne dit aujourd'hui qu'on a rencontré quelqu'un.** `p.appels` et `p.missionsFaites`
le disent à moitié. Il faut un `p.connus` — un ensemble, écrit la première fois qu'on parle à
quelqu'un. Sans lui, le répertoire affiche des gens qu'on n'a jamais vus, et il **divulgâche
l'histoire** : Josée, le Dr Lachance de M13, Marco qui te vend. Un répertoire qui montre la
fin est pire que pas de répertoire.

⚠️ **Le mot « journal » est déjà pris deux fois dans ce dépôt**, et c'est le genre de
collision qu'on paie six mois plus tard : `journal.py` est **Le Clairon**, la manchette du
matin lue par le narrateur ; M11 prévoit le **carnet du poste**, le dossier de la police sur
toi. La page du joueur s'appelle **JOURNAL**, elle vit dans **LE CARNET**, et les deux autres
gardent leur nom. Trois choses, trois noms — écrit ici pour qu'on arrête de les confondre.

- **La sauvegarde grossit.** `Sauvegarde.completer()` a déjà le repli champ par champ, donc
  une vieille partie sans carnet repart avec un carnet vide plutôt que de planter. Mais une
  partie de dix jours accumule des dizaines d'entrées : le journal est **plafonné** (les
  dernières, plus les jalons qu'on ne jette jamais). Ça compte double en M14, où la partie
  voyage par le réseau.
- **Le vrai travail est à l'écran.** Les menus canvas savent afficher une liste de boutons
  avec un curseur ; une **page de texte qui défile** sur 480 × 270 en police 5×7, c'est autre
  chose. C'est là que va le temps de cette entrée, pas dans les données.
- **Juges** : le rappel de mission dit toujours la même chose que la ligne du HUD et que le
  GPS (trois endroits, une seule vérité) ; le journal ne contient que des événements réellement
  émis, jamais recalculés ; le répertoire ne montre **que** `p.connus`, et un test rejoue une
  partie neuve pour vérifier qu'aucun personnage non rencontré n'y apparaît ; le carnet reste
  sous son plafond après cent jours de jeu simulés.

**Livré le 13 sept. 2026 :**

- **Le défilement manquait à TOUS les menus**, et c'est ce qui bloquait la page de texte
  annoncée plus haut. `dessinerMenu` dessinait ses items du premier au dernier : au-delà de
  quatorze lignes, ils sortaient de la boîte. Une **fenêtre** suit maintenant le curseur, avec
  deux petites flèches. ⚠️ Elles sont **dessinées**, pas écrites : la police pixel n'a que des
  lettres, des chiffres et un peu de ponctuation — un « ▲ » y tomberait sur un « ? », comme
  les accents avant qu'on les normalise. ⚠️ Et un menu qui tient au complet ne change pas
  d'allure : le calcul rend exactement son nombre d'items tant que la hauteur ne bute pas sur
  l'écran.
- **`m.retour`** : sortir d'une page recule d'un cran au lieu de rendre la main au jeu. Sans
  ça, quitter le JOURNAL relançait la partie et il fallait remettre PAUSE pour lire la page
  d'à côté.
- **EN COURS** donne le donneur, la récompense, **tous** les objectifs — celui du moment
  marqué d'un chevron, les faits d'un point — et **où**. ⚠️ « Barré » n'existe pas en 5×7 :
  on marque et on éteint, et `actif: false` grise le reste.
- **JOURNAL** : le plus récent en haut, daté au jour de jeu. ⚠️ Il s'écrit depuis ce que le
  jeu **émet déjà** — `Histoire.evenement('mort')` et `('arrete')` sont les mêmes émissions
  qui font échouer une mission ; il n'y a pas deux endroits qui décident qu'on est allé à
  l'hôpital.
- **RÉPERTOIRE** : `p.connus`, écrit à la **première parole** (`Histoire.parler`), et sa fiche
  cuit le visage avec **ses** couleurs de palette — les mêmes que celles de son sosie dans la
  rue, rien de neuf à dessiner.
- **Le plafond** jette le quotidien **avant** les jalons, et quand il n'y a plus que des
  jalons, ils cèdent aussi : rien ne grossit sans fin, ce qui comptera double en M14.
- ⚠️ **Ce qui manque encore au journal** : les manchettes du matin et les propriétés
  achetées. Elles s'émettent dans `missions.js`, qu'une autre session réécrivait au même
  moment — c'est **une ligne chacune** le jour où ce fichier est libre (`Histoire.noter(...)`
  est exporté pour ça).
- **Juges (3 neufs)** : la page EN COURS dit la même mission que `ligneObjectif()` **et** que
  `cible()` (trois endroits, une seule vérité) et barre exactement les objectifs faits ; le
  journal retient une mission réussie, une arrestation et un séjour à l'hôpital **sans qu'une
  ligne du carnet ne les déclenche**, reste sous son plafond après 300 entrées et n'y perd
  aucun jalon ; le répertoire est **vide** dans une partie neuve, ne prend Ti-Guy qu'après lui
  avoir parlé, ne le prend **qu'une fois**, et sa fiche dessine bien un visage.

## Notes

demande de Martin (« un rappel de la mission en cours dans le menu, un journal et un
bestiaire avec les personnages connus ») : **LE CARNET** au menu Pause, trois pages — **EN
COURS** (donneur, récompense, objectifs faits marqués, celui du moment, et où), **JOURNAL**
(écrit tout seul depuis ce que le jeu émet déjà, daté au jour, plafonné — le quotidien cède
avant les jalons), **RÉPERTOIRE** (⚠️ `p.connus` seulement : un répertoire qui montre la fin
est pire que pas de répertoire). Les menus savent maintenant **défiler**, et une page recule
d'un cran au lieu de rendre la main au jeu
