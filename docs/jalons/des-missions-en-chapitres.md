# Des missions en chapitres, de cinq à dix minutes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 30 sept. 2026 : « les missions doivent durer au moins 5 à 10 minutes chacune, trouve une
solution pour agrandir »._

_Ce que ça donne :_ une mission devient un **chapitre** de 5 à 10 minutes, découpé en **actes**. Mourir ou se faire
pogner à l'acte 3 ne renvoie plus au début : après l'hôpital ou le poste, on **reprend l'acte**. Les objectifs
peuvent faire durer le jeu (des renforts, un gang qui te colle au pare-chocs, une étoile) et trois types neufs
prennent du temps par nature. Un chronomètre au carnet dit si on y est.

**Aujourd'hui** (30 sept. 2026) :
- 77 missions. La ville fait ≈ 7 300 × 6 600 px, une berline plafonne à 4 px/image (≈ 240 px/s) : on la traverse
  en 30 s en ligne droite, ≈ 1 min dans le trafic. Estimation, pas une mesure : une mission typique dure 2 à 4 min,
  les plus courtes (p02, p04, p05, p10, e04, s06…) moins de 2. [Des missions plus longues](des-missions-plus-longues.md)
  (22 sept.) a déjà ajouté 2 à 4 étapes à chacune des 37 d'alors.
- **Aucune durée n'est enregistrée** : `missionsFaites[slug]` ne garde que le jour (`histoire.js`, `reussir`).
- **Aucun point de reprise** : `echouer()` (`histoire.js`) nettoie et met `mission = null` ; la mission redevient
  disponible, et on recommence à l'étape 0. Les ennemis déjà couchés restent couchés (`retenirLesTombes`).
- **Une mission ne survit pas au rechargement** : `jeu.js` fait `if (p.mission) p.mission = null`.
- La filature existe (`suivre`), le fuyard aussi (`ramasser` avec `cible: fuyard`) ; aucune option ne fait arriver
  des renforts ni un gang en char pendant un trajet (les renforts existent dans `frenesies.js` et `police.js`).

**Tranché avec Martin (30 sept. 2026)** :
- **Les quatre approches ensemble** : des actes avec des reprises, la fusion des missions courtes en chapitres, des
  objectifs qui durent, et des types d'objectifs longs.
- **On ne compte plus** : l'objectif « cent missions » de M16 tombe ; chaque arc prend le nombre de chapitres que
  son histoire demande.
- **La reprise** : un menu après l'hôpital ou le poste, REPRENDRE L'ACTE N ou PLUS TARD.
- **Ce qui fait durer se déclare dans le fichier de la mission**, objectif par objectif ; rien d'automatique.
- **Le pilote est La Pointe** : p02, p05, p04, p10, p09 et p11 en un chapitre de six actes.

### La forme d'un chapitre

Un chapitre reste **un fichier de mission** (`app/missions/<slug>.py`) : une seule liste d'`objectifs`, coupée par
un marqueur :

```python
{"type": "acte", "titre": "LE DÉFI DE ZED", "donneur": "zed"},
```

- Le marqueur est **instantané**. Il affiche le carton « ACTE 3 — LE DÉFI DE ZED », pose le point de reprise
  et, s'il le déclare, porte ce qui ouvre l'acte : l'appel ou la scène du donneur suivant, et un saut d'horloge
  (`heure: "nuit"`, comme `sur_place`).
- Le premier objectif d'un chapitre est un `acte` ; le validateur (`__init__.py`) le refuse sinon, et refuse un
  `acte` en dernière place.
- `pendant` garde son index d'étape : le marqueur compte comme une étape, et le moteur ne voit presque pas la
  différence. `sur_place` et `frontiere` passent au niveau de l'acte (un acte à la Pointe, un autre au Brouillard).
- `remplace: ["p02", "p05", …]` nomme les missions que le chapitre remplace, dans l'ordre des actes.

**Les parties déjà commencées.** Une mission remplacée faite (`missionsFaites`) compte comme son acte fait. Le
chapitre commence au premier acte pas fait ; tous faits, le chapitre est fait. Les `prerequis` du catalogue qui
visaient une mission remplacée sont réécrits vers le chapitre ; le validateur refuse un slug remplacé ailleurs. Les
mp3 déjà payés gardent leur voix, renommés par (qui, mission, texte) comme au 22 sept.

### La reprise

- **Au marqueur `acte`**, `B.partie.mission.reprise` retient : l'étape, la position (rue ou bloc), le char (modèle,
  couleur), l'arme en main et ses munitions, et l'heure.
- **À l'échec** (`mort`, `arrete`, `vehicule_detruit`, `chrono`…) d'un chapitre, le parcours d'aujourd'hui se fait
  tel quel (hôpital ou poste, frais, armes confisquées en prison), puis un menu : **REPRENDRE L'ACTE N** ou
  **PLUS TARD**.
  - **Reprendre** : fondu au noir, police à zéro, le joueur au point de l'acte avec un char neuf du même modèle et
    l'arme de l'acte **rendue**, même si la prison l'avait prise. Les tombés restent tombés, comme aujourd'hui.
  - **Plus tard** : l'acte atteint reste dans `B.partie.chapitres[slug]` ; le donneur de cet acte rappelle, et le
    chapitre reprend là.
- **Au rechargement**, la mission en cours est encore vidée (`jeu.js` ne change pas), mais `chapitres[slug]` est
  sauvegardé : fermer le jeu à la 8ᵉ minute ne perd que l'acte en cours.

### Le chronomètre

Le temps d'une mission se compte dans `Jeu.maj` (ni rAF ni `B.t`), sans la pause ni les menus. Il s'écrit dans
`B.partie.durees[slug]` : le dernier temps et le meilleur, pour le chapitre et pour chaque acte. Le carnet l'affiche
sur la fiche du donneur, à côté de « FAITE ». C'est lui qui dit si on tient 5 à 10 minutes dans les vraies parties
de Martin (`donnees/bandini.sqlite3`, table `parties`).

### Ce qui fait durer

Des **options**, déclarées dans le fichier, là où l'histoire les justifie :

- `renforts: {"vagues": 2, "n": 3}` sur `tuer`, `proteger`, `tenir` : quand le groupe tombe à un seul debout, la
  vague suivante arrive `loin`, hors champ (`poserLesCravates`, `faireArriver`). Une réplique `pendant` peut
  l'annoncer.
- `poursuite: {"groupe": "skateux", "chars": 1}` sur `aller`, `livrer`, `retourner` : un char du gang naît hors
  champ et te colle jusqu'à la fin de l'objectif ; crevé ou semé, il lâche. L'IA se branche sur celle des renforts
  de frénésie et de la poursuite de police, pour un gang.
- `etoiles: N` sur n'importe quel objectif : ce que `semer` et `survivre` font déjà, généralisé.

Trois **types neufs** (la filature existe déjà : `suivre`) :

- `tournee` : N arrêts dans l'ordre (collecter, livrer, poser des affiches), `chrono_s` au choix ; une flèche et une
  réplique par arrêt.
- `tenir` : rester dans un rayon pendant X secondes pendant que les vagues arrivent ; en sortir remet le compte à
  zéro, ou fait échouer (`strict`). C'est « défendre le phare ».
- `relais` sur le fuyard (`ramasser` avec `cible: fuyard`) : il change de char ou de district une ou deux fois
  avant qu'on le coince.

Chaque option et chaque type s'ajoute à `OPTIONS_OBJECTIFS` ou aux types de `__init__.py`, et se lit dans
`poser()`/`majObjectif()` de `histoire.js`.

### Le pilote : La Pointe

| Acte | D'où | Donneur | Ce qu'on fait |
|---|---|---|---|
| 1 | p02 | M. Bilodeau | les Skateux bloquent le pont, leur grand au cône |
| 2 | p05 | le Trappeur | de nuit, les collets près du phare |
| 3 | p04 | Zed | la course à pied contre son temps |
| 4 | p10 | Zed | le saut de la rampe, sur sa machine |
| 5 | p09 | Ovila | le phare éteint : le tenir, puis rallumer la lampe |
| 6 | p11 | Josée | Zed au Brouillard sain et sauf, et la paix (`libere: pointe`) |

Aujourd'hui ≈ 15 étapes. Le chapitre ajoute des répliques de pont entre les actes (le donneur suivant appelle, ou
attend sur place), des `renforts` au pont et au phare, une `poursuite` de Skateux vers le Brouillard, un `tenir` au
phare et une `tournee` au besoin. Visée : 8 à 10 min au chronomètre. Les voix neuves se génèrent dans le même passage
(ElevenLabs v3 : Martin a donné carte blanche le 28 sept.), et la dépense se dit.

### Les juges

- `tests/test_arc_p_js.py` réécrit : le chapitre de la Pointe joué de bout en bout, au bouton, sous Node.
- La reprise : mort à l'acte 3, REPRENDRE, et l'étape, la position, le char et l'arme sont ceux de l'acte ; arrêté à
  l'acte 5, l'arme confisquée revient ; PLUS TARD, puis le chapitre repart à l'acte atteint, rechargement compris.
- La migration : une partie qui a fait p02 et p05 commence le chapitre à l'acte 3 ; toutes faites, le chapitre est
  fait ; un prérequis vers p11 est réécrit.
- Chaque option et chaque type neuf a son juge de banc, qui rougit sans sa règle.
- Le chronomètre ne compte ni la pause ni les menus.
- `test_missions_en_scene_js` et `test_definitions` avant d'atterrir (le poids du paquet).

### Ensuite

Après le pilote joué par Martin, les autres arcs passent en chapitres par vagues, un arc à la fois. Les arcs qui
restent à écrire (Q, E, S, P, H, D, C, R, T, I, X de M16) s'écrivent directement en chapitres.

⚠️ **Ce qui guette** :
- Une mission remplacée a pu être une clé de `donne` ou de `ferme` (le téléphone, la rue libérée) : `libere`,
  `calme`, `manchette` et `a_vendre` passent à la fin de l'acte qui les donnait, pas à la fin du chapitre.
- Les juges « ce module ne déplace rien » et la ville : un chapitre ne pose aucun lieu neuf.
- [Qui parle se nomme](../personnages/README.md) : une fois par mission, donc une fois par **donneur** dans un
  chapitre.
- Six donneurs pour un chapitre : deux voix partagées ne se croisent jamais dans un même dialogue.
