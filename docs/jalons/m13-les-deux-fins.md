# M13 Les deux fins

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M13 — Les deux fins (**ajout**, taille 4)_

_Ce que ça donne :_ une histoire qui se termine, de deux façons.

- **Une mission par district** — et bien plus : les arcs de district, les donneurs, les
  voix et les trois missions de fin (m97 _Marco te vend_, m98 _Le Boss_, m99 _Le dernier
  traversier_) sont décrits dans **M16**, dont M13 est la dernière tranche. Ce qui reste
  ici : les génériques, la ville qui change de couleur, la partie qui continue.
- **Marco te vend** : au bout de l'arc, le cousin parle à la police — la mission bascule en
  cours de route.
- **Dr Lachance** devient donneur : l'hôpital a ses secrets (et ses ordonnances).
- **Le Boss** : les 4 propriétés **et** les 4 districts libérés → manchette, générique, la
  ville change de couleur.
- **Sacrer son camp** : 15 000 $ en poche, traversier de nuit, 0★ → l'autre générique.
- **Le générique** — l'animation audio-visuelle de fin, le narrateur du Clairon,
  `generique` — est décrit juste au-dessus, dans « La ligne d'histoire » : M13
  fournit les deux fins, cette section-là fournit ce qu'on en voit et ce qu'on en entend.
- La partie **continue après la fin** : le bilan se montre, le monde reste.
- **Juges** : un test force chacune des deux fins (elles sont atteignables) ; la dette reste
  remboursable jusqu'au bout (aucune fin ne se referme sur un bug) ; chaque réplique
  nouvelle a son personnage et sa voix.

### Ce qu'on trouve en ouvrant le chantier (25 sept. 2026)

⚠️ **Aucune des deux fins n'est atteignable aujourd'hui.** _Le Boss_ (m98) exige 4 districts libérés et 4
propriétés, et m97 en exige 3 ; seul m5 libère un district (le Faubourg), et l'hôtel, quatrième propriété,
n'est en vente nulle part (`phase: 2`, sa mission q07 n'existe pas). Les arcs qui libèrent les autres
districts (q13, e10, s11, p11) sont dans M16, pas encore écrits. _Sacrer son camp_ (m99), elle, ne demande
que m6 et 15 000 $ : on peut la jouer.

D'où deux vagues :

- **Vague 1 — le générique, et la fin qu'on peut jouer.** La machinerie, et m99 au complet.
- **Vague 2 — _Le Boss_.** m98, son générique, la ville qui change de couleur, `p.libere` qui efface les
  zones de gang : quand les arcs de M16 libèrent assez de districts pour qu'on y arrive en jouant.

### Vague 1 : le plan

1. **Le générique est une donnée de la mission.** Une mission de fin porte `scenes["generique"]` et
   `dialogue["generique"]` (le narrateur du Clairon, `jeu=` collé à chaque réplique). `generique` s'ajoute
   **à la fin** de `PARTIES` : aucune voix déjà générée ne change de nom. Pas d'état `B.etat = 'fin'` : le
   générique est une scène, et la ville est figée sous une scène.
2. **`donne.generique: true`** : après la scène de fin, `Histoire` joue celle du générique, puis ouvre le
   BILAN. La partie continue ; `p.fins` retient les fins vues (sauvegarde).
3. **Les chiffres** : le plan `titre` remplit `{fortune}`, `{missions}`, `{proprietes}`, `{jours}`,
   `{dette}` avec la partie (`Scenes.jouer` reçoit `valeurs`) ; `erreurs_de_scene` refuse une clé inconnue.
4. **La musique `generique`** : dans `audio.MUSIQUES` et en notes dans `musique.py` (une variante de
   l'ouverture, plus lente). Le mp3 ElevenLabs viendra après, comme les voix.
5. **Le quai du traversier est un lieu** : `traversier:<escale>` (`lieu()`, `resoudre`), et un donneur
   peut s'y tenir (`ou: "traversier:quais"`).
6. **Un type d'objectif, `embarquer`** : à bord du traversier quand il quitte `escale`. Son juge de banc
   d'abord.
7. **Le capitaine Bérubé** (personnage, fiche `docs/personnages/berube.md`, voix) et **m99 _Le dernier
   traversier_** : m6, 15 000 $ ; de nuit, sans étoile, au quai ; payer le passage ; embarquer ; la fin, puis
   le générique.
8. **Le BILAN** dit aussi les missions faites, la dette, les districts libérés et les fins vues.
9. **Juges** : m99 se joue au banc jusqu'au générique, et on retombe sur une ville jouable (le BILAN
   fermé, les commandes rendues) ; le catalogue atteint m99 en respectant prérequis et `exige` ; chaque
   réplique a son personnage, sa voix et son jeu.

### Vague 2 : le plan (29 sept. 2026)

_Le Boss_ (m98), la fin qu'on gagne — Josée la donne, comme elle a donné le Faubourg puis la ville.

1. **m98 _Le Boss_** (Josée ; après m97, `exige` 4 districts libérés et 4 propriétés) : sortir devant le
   Brouillard ; les hommes du maire arrivent, **les Morues, les Skateux et les Boulonneux à tes côtés** (une option
   neuve d'objectif, `allies` : ils courent sur les hommes de la mission, jamais sur toi) ; puis la police du maire
   (`survivre` à 5★ — `etoiles` sur `survivre`) ; Bouchard rappelle ses chiens (`treve` : la police rentre) ;
   l'Hôtel Bandini, sa garde devant la porte ; et le maire Réal Tanguay (personnage neuf, dedans, dans la chambre de
   l'hôtel) qui cède — et rend le billet de Rocco, qu'il avait racheté à Sal : **la dette de Rocco finit déchirée**.
2. **Son générique** : l'autre fin, pendant de celui de m99 — ses coupes, ses cartons (les quartiers, la dette
   déchirée), et sa musique à lui.
3. **La ville qui change de couleur** (`donne.boss`, `partie.boss`, gardé par la sauvegarde) : les gangs reviennent
   dans leurs quartiers à tes couleurs et te saluent, les passants aussi ; plus de rixes aux frontières ; le nom
   sous la mini-carte et la grande carte à l'or des Bandini ; la une du Clairon.
4. **Juges** : m98 jouée au bouton, de l'appel au générique puis à la ville d'après ; chaque mécanisme neuf muté.

## Notes

une mission par district, Marco qui te vend, Dr Lachance donneur, _Le Boss_ et _Sacrer son
camp_

**Vague 1 livrée le 25 sept. 2026 — le générique, et _Sacrer son camp_.**

- **m99 _Le dernier traversier_** (`app/missions/m99.py`) : le capitaine Bérubé (personnage neuf, fiche
  `docs/personnages/berube.md`, voix « Paul K — Deep French Narrator ») attend au bout du quai des Quais
  (`traversier:quais`, une forme de lieu neuve). m6 et 15 000 $ (`exige`) ; de nuit, sans une étoile ;
  500 $ de passage ; puis **`embarquer`**, un type d'objectif neuf : à bord quand le traversier QUITTE
  l'escale, à pied ou au volant. La fin se dit sur le pont, devant le capitaine, qui rentre ensuite dans
  sa cabine et quitte la ville (`parti_apres`).
- **Le générique est une donnée de la mission** : `scenes["generique"]` et `dialogue["generique"]`, que
  `donne.generique` fait jouer après la fin (`Histoire.jouerLeGenerique`). Le narrateur du Clairon referme
  l'ouverture : le car de six heures, le billet aller simple, « Bonne chance, le jeune ». Cinq coupes sur
  la ville (terminus, garage, planque, bar, phare), puis les chiffres de la partie dans les cartons
  (`{fortune}`, `{missions}`, `{proprietes}`, `{jours}`, `{dette}` — `VALEURS_DE_TITRE`, jugés) et le
  logo. Ensuite le BILAN, qui dit maintenant les missions, la dette de Rocco, les districts libérés et la
  fin vue (`partie.fins`) ; **la partie continue** — le traversier accoste à La Pointe.
- **La musique `generique`** : « Le dernier traversier », la même tonalité que l'ouverture, plus lente, qui
  monte au lieu de descendre et se résout en la majeur (en notes dans `musique.py`, et 45 s d'ElevenLabs).
- **Les voix** : les 13 répliques de m99 et les deux repos de Bérubé, générées (≈ 1 230 caractères, plus
  1 350 crédits pour la musique). ⚠️ **Personne ne les a encore écoutées** : la voix de Bérubé est neuve.
- **Juges** : `tests/test_les_deux_fins_js.py` joue m99 au banc, de la poignée de main au générique et au
  BILAN, puis fait accoster le traversier et marcher le joueur ; trois mutations le font rougir (générique
  jamais lancé, `embarquer` qui n'avance pas, chiffres non remplis). `erreurs_de_mise_en_scene` exige un
  générique ENTIER (scène, répliques, `donne.generique`) et dit par le narrateur seul.
- **Vu en le jouant** : la ligne « TRAVERSIER POUR LA POINTE · DÉPART… » s'écrivait sous les cartons —
  elle se tait sous une scène.

**La suite complète, après l'atterrissage** : trois rouges, tous de la vague.
- `test_interactions` comparait le butin d'un bac à « la plus petite prime », qui vaut 0 $ depuis m99 : la
  plus petite prime est celle d'une mission qui en paie une.
- `test_passage_pietons` et `test_velos_js` : Bérubé, en naissant, décale les identifiants d'un cran (même
  retiré aussitôt, ils rougissaient). L'autobus du juge tournait à droite au vert au lieu de filer tout
  droit, et le juge mesurait sa progression sur l'axe : il mesure maintenant qu'il franchit la ligne et
  qu'il ROULE. Le vélo, lui, montre un vrai défaut, ancien (la base le fait à la graine 24) : sa ligne est au
  plan, « Un vélo qui redescend du trottoir reste planté », et la graine 5 est un `xfail` strict.

**Ce qui reste (vague 2)** : _Le Boss_ (m98), son générique et la ville qui change de couleur,
`p.libere` qui efface les zones de gang, Marco qui disparaît après m97 — dès que les arcs de M16
libèrent assez de districts pour qu'on y arrive en jouant (et que l'hôtel se vende).

**29 sept. 2026 — les districts de _Le Boss_ sont débloqués (M16).** Les quatre missions qui libèrent un district
sont livrées : `q13` (les Quais), `e10` (les Érables), `p11` (La Pointe), `s11` (La Shop) — avec le Faubourg de m5,
cinq districts peuvent être libérés en jouant. Chacune écrit `libere` et la rue le montre (le gang ne sort plus, ne
saute plus, sort du jeu des territoires, rend ses coins ; sous la mini-carte, sa cour redevient le quartier) ;
`exigeTenu({liberes: n})` est jugé au banc à chaque cran, et _Marco te vend_ (m97, trois districts) s'ouvre.
⚠️ **Ce qui manque encore à _Le Boss_** : la **quatrième propriété**. L'hôtel est `phase: 2` et rien ne le met en
vente : `q07` (_La chambre 12_, Norbert) et `donne.a_vendre` sont en brouillon sous `refs/wip/m16-q07`. Puis m98,
son générique et la ville qui change de couleur.

**29 sept. 2026, le soir — et la quatrième propriété.** `q07` (Norbert, _La chambre 12_) met l'Hôtel Bandini en vente
(`donne.a_vendre`, `partie.enVente`) : il s'achète au comptoir du hall, et le juge de banc fait les quatre propriétés.
**_Le Boss_ est débloqué** : ses deux conditions (4 districts, 4 propriétés) se gagnent en jouant. Reste à l'écrire —
m98, son générique, la ville qui change de couleur.

**29 sept. 2026 — vague 2 livrée : _Le Boss_. Les deux fins se jouent ; M13 est livré.**

- **m98 _Le Boss_** (`app/missions/m98.py`, Josée ; après m97, `exige` quatre districts libérés et quatre
  propriétés). Le téléphone sonne : « Josée. Quatre quartiers, quatre propriétés. » Six étapes :
  0. **sortir devant le Brouillard** (l'intro se joue dedans : Josée croise les bras, la caméra va voir la porte du
     bar puis l'Hôtel Bandini, elle montre la sortie) ;
  1. **les Cravates du maire** (six, qui arrivent de la grande rue) — **les Morues, les Skateux et les Boulonneux à
     tes côtés** : deux de chaque gang arrivent en courant de l'autre bout de la rue et cognent les hommes du maire
     (Zed appelle : « On arrive! ») ;
  2. **la police du maire, à cinq étoiles** : tenir 90 secondes (Gros-Boulon a barré le boulevard de l'usine) ;
  3. **Bouchard rappelle ses chiens** (`treve` : zéro étoile) ; les alliés rentrent chez eux ; direction l'hôtel,
     « le maire dort chez toi » ;
  4. **la garde du maire** (quatre gardes de sécurité) devant ta porte — Norbert appelle de la réception ;
  5. **la chambre douze** : par l'escalier du hall, le maire Réal Tanguay (personnage neuf, dedans, en robe de
     chambre) se présente à la poignée de main — « Pour encore cinq minutes, j'imagine. »
  La **fin** se joue devant lui : il hausse les épaules (« Trois mandats pour avoir cette ville-là. Toi, t'as pris un
  mois. »), tend **le billet de Rocco — il l'avait racheté à Sal, « pour te tenir en laisse »** —, un silence ; la
  caméra va chez Josée, et quand elle revient, il est parti (« Bienvenue chez toi… Boss. », le seul `[warmly]` de
  Josée). **La dette de Rocco est déchirée** (`donne.dette`, le billet entier, plafond compris) : c'est le
  dénouement du fil des deux fins.
- **Son générique** — le pendant de celui de m99 : le narrateur (cinq phrases, « Mais c'est toi qu'elle salue, le
  Boss. »), une coupe sur chacun des quatre quartiers libérés (la cantine, le dépanneur, la fourrière, le phare), puis
  l'Hôtel Bandini où la caméra reste pendant que les chiffres montent : fortune, **QUARTIERS À TOI** (`{liberes}`),
  propriétés, missions, jours, **LA DETTE DE ROCCO — DÉCHIRÉE**, et le logo sur « LE BOSS ». Sa musique à lui,
  **`generique_boss`** « Le Boss » : ré mineur qui se résout en ré majeur, la trompette seule sur le quai qui finit
  avec toute la section (notes dans `musique.py`, et 45 s d'ElevenLabs). Puis le BILAN, et la partie continue.
- **La ville qui change de couleur** (`donne.boss`, `partie.boss`, gardé par la sauvegarde ; `pietons.BOSS`) : les
  gangs des districts libérés (Morues, Chevreuils, Boulonneux, Skateux — pas les Cravates, au maire jusqu'au bout,
  ni les Mantes) **reviennent dans leur cour, à tes couleurs** (le haut de leur tenue à l'or des Bandini) ; **on te
  salue** — un passant sur deux qui passe à deux pas (« SALUT, BOSS! », « M'SIEUR BANDINI! »), un membre de gang
  (« TOUT EST CALME. »), tiré à l'empreinte, jamais au dé ; **plus de rixe aux frontières** ; le nom du quartier
  sous la mini-carte et les cinq districts de la grande carte **à l'or des Bandini**, le titre « LA VILLE DU BOSS » ;
  la **une du Clairon** : « LE MAIRE TANGUAY DÉMISSIONNE » ; et le maire a quitté l'hôtel pour de bon.
- **Le moteur apprend** (chaque clé jugée et mutée) : deux options d'objectif, **`allies`** (l'état `allie`
  d'`Entites` : il vise la `cible` debout la plus proche du joueur, ne frappe ni le joueur ni un autre allié, et ni
  `alerter` ni `blesser` ne le retournent contre toi) et **`treve`** ; `etoiles` sur `survivre` ; `parti_apres`
  vaut aussi pour un personnage de pièce ; la flèche trouve un personnage d'**étage** (la chambre n'a pas de porte en
  ville : celle de la pièce dont l'escalier y monte) ; `maire` est un titre (`TITRES`).
- **Les voix** : 21 répliques de m98, le repos du maire et la une du Clairon — 23 voix, ≈ 2 400 caractères, le
  narrateur passé à l'isolateur ; la musique, 619 crédits ; ≈ 2 160 crédits en tout. Le maire a la voix **Eric —
  Smooth, Trustworthy** (multilingue, un français « standard » vérifié en v2 ; Scribe relit ses trois répliques mot
  pour mot). ⚠️ **Personne ne les a encore écoutées.**
- **Juges** (`tests/test_le_boss_js.py`, neuf, sur une partie JOUÉE au bouton : l'appel qui sonne tout seul, ACTION
  devant Josée, les combats, la chambre, ACTION devant le maire, la fin, le générique, le BILAN, puis la ville
  d'après, la sauvegarde et un joueur qui marche) ; **treize mutations, toutes rouges** (les alliés jamais posés,
  `alerter`, `blesser`, le coup allié sur le joueur, `etoiles` sur `survivre`, `treve`, `boss`, les gangs qui
  reviennent, les saluts, la paix aux frontières, le maire qui reste dans sa chambre, la flèche de l'étage, la
  sauvegarde). `test_missions_en_scene_js.py` apprend qu'une poignée de main finit **devant sa cible** quand la
  scène de fin la fait jouer (on va la voir, par l'escalier s'il le faut) : le maire y parle en personne, Josée au
  combiné.
- **Vu à la capture** : la teinte seule de la grande carte se confondait avec la brique — un liseré d'or l'entoure.
- ⚠️ **Ce qui reste hors de M13** : Marco ne disparaît toujours pas après m97 (il a encore des missions à donner
  dans certains chemins) ; se cacher dedans pendant les 90 secondes de la police fait tomber les étoiles comme
  partout — le chrono, lui, court.
