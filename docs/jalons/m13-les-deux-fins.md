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
