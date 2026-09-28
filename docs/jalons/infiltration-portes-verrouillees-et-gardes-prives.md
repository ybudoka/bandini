# Infiltration : portes verrouillées et gardes privés

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin veut des missions d'infiltration dans des bâtiments grands et labyrinthiques : ne pas
être vu, déverrouiller des portes, trouver des clés. Le moteur a déjà presque tout — les
cônes de vision et les paliers d'alerte (`app/recherche.py`, `static/js/police.js`), les
intérieurs à étages (`app/ile.py`, `app/aeroport.py`), les objectifs `sans_etoile` et
`suivre` (`static/js/histoire.js`), et le mini-jeu de piratage (m53). Il manque deux briques
réutilisables, avant d'écrire une vraie mission dessus : ⚠️ une VRAIE serrure —
`carte.BARRIERES` (« une porte, une condition, un prix ») sait déjà fermer un lieu tant
qu'une mission n'est pas faite ou tant qu'on n'a pas payé ; elle apprend une troisième
condition, `objet`, fermée tant que `partie.objets[slug]` n'est pas possédé — la clé qu'on
trouve ou qu'on vole devient une vraie clé.

- ⚠️ Un genre `garde` (vigile privé) — `recherche.VISION` lui donne son propre cône, et
  `police.js` généralise ses deux appels à `voit(..., 'policier', ...)` (dans `gere()` et
  `signalerCrime()`) en `a.genreVision`, avec `'policier'` en défaut, pour que N'IMPORTE
  QUEL genre déclaré compte, pas seulement la police ; un archétype `garde` dans
  `app/pietons.py` (même moule que `policier` : `frequence: 0`, ne naît jamais au hasard) et
  `Police.creerAgent(x, y, etat, genre)` sait désormais fabriquer l'un ou l'autre. Se faire
  voir par un garde compte exactement comme se faire voir par un policier — patrouille,
  poursuite, arrestation : c'est le même moteur, un cône et une palette différents. La
  mission elle-même (le bâtiment, ses pièces, où poser le garde et la clé) reste à écrire
  par-dessus ces deux briques.

## Notes

### Vague 1 — les deux briques (22 sept. 2026)

La serrure `objet` dans `carte.BARRIERES` (`Monde.barriereFermee`), et le genre `garde` (son cône dans
`recherche.VISION`, son archétype dans `pietons.py`, `Police.creerAgent(x, y, etat, 'garde')`).

### Vague 2 — la villa du maire et trois missions (28 sept. 2026)

Martin : « fais des missions d'infiltration ». Trois, jouées de bout en bout au banc, sur un seul
bâtiment grand et labyrinthique : **la villa du maire Tanguay**, que le plan de M16 attendait.

- ⚠️ **Un BLOC, pas un lieu de la ville ni une pièce** (`app/blocs/villa.py`). Une pièce de cette taille en
  ville fait glisser la ville, et une PIÈCE arrête tout : `Histoire.majObjectif` et `Police.maj` ne
  tournent pas dedans (l'objectif avance à la sortie, la police « ne patrouille pas les salons »). Dans un
  bloc, `B.interieur` reste nul : objectifs, gardes, étoiles, tout tourne. Le passage : au bout de la rue
  est-ouest du bord ouest des Érables (rangées 36 à 39 de la ville d'avant) ; on arrive sur le chemin,
  devant la grille.
- **Trois étages dans une carte, et des cadres de caméra.** Le terrain et le rez-de-chaussée en haut ;
  l'étage et la cave dessous, côte à côte. Chaque étage est un CADRE (`cadres`) : `Monde.cibleCamera` et
  `limitesCamera` ne sortent pas de celui du joueur, et chacun est plus grand que l'écran (jugé par
  `blocs.erreurs`) — on ne voit jamais l'étage d'à côté. Les `escaliers` (deux bouts : leurs marches et leur
  arrivée) passent de l'un à l'autre au noir (`Infiltration.majEscaliers`).
- **Les lieux de bloc.** Un bloc déclare ses `lieux` ; `carte_du_bloc` en fait ses `points_interet`, et
  `Histoire.lieu` les trouve dans le bloc. En ville, la flèche vise le passage (`passageDuBloc`) ; dans le
  bloc, le lieu, le terminal ou l'objet (`cibleDansLeBloc`), et la sortie pour tout le reste. Une scène les
  montre par `bloc:<slug>`. ⚠️ `blocs.LIEUX_PAR_BLOC` recopie leurs noms AVANT tout import :
  `missions` bâtit ses scènes par défaut en se chargeant, pendant que `blocs` attend `carte`, qui attend
  `missions` (la boucle a planté au premier essai) ; `erreurs` juge que les deux listes sont les mêmes.
- **Les gardes sont au bloc, pas aux missions** (`GARDES` : huit rondes — la grille, le jardin, le hall, le
  corridor, deux à l'étage, deux à la cave). `Infiltration.releve` les pose en entrant (hors de la suite des
  numéros), les mêmes à chaque visite ; `Police.garder` les mène : la ronde au pas (`pas` 0,45), une pause à
  chaque point, tournés vers son cap, à balayer du regard (`balaye_deg` 35). Sur le terrain `prive`, te voir
  dans son cône le temps de te reconnaître (`reperage_s` 0,9 au bout du cône, trois fois plus vite tout
  près) donne l'alerte : une étoile, lui et ceux de son étage à tes trousses. Avant l'alerte, le « ? » : il
  s'arrête et regarde par là. La nuit, sa lampe de poche se voit (le cône, par-dessus le noir). Ni la
  foule (`peupler`) ni rien d'autre ne les oublie quand on s'éloigne.
- **Les serrures** : des barrières du bloc (`serrures`, exportées par `blocs.serrure` au format de
  `carte.BARRIERES`, condition `objet`), peintes en porte cadenassée (`decor: serrure`). La porte de service
  (`cle_villa`) et la chambre forte (`code_voute`).
- **L'objectif `obtenir`** : un objet dans le sac, posé à son lieu (ramassé en marchant dessus — il ne
  s'oublie pas, `objetDeMission`) ou dans la poche d'un garde (`garde`) : ACTION dans son dos le prend sans
  qu'il sente rien (`Combat.pickpocket` → `Infiltration.voler`), assommé il le lâche. Et **`objet` sur
  n'importe quel objectif** : ce que l'objectif fini met dans le sac (le code du terminal piraté). Une
  mission ratée fait retomber ce que ses objectifs avaient mis dans le sac (`Infiltration.rendre`).
- **Les missions** (`app/missions/v01.py` à `v03.py`, 29 voix générées) :
  - **v01 — La clé du maire** (Josée, après q04) : de nuit, par le trou de la palissade (une planche manque
    au nord ; la grille a son garde), la clé dans la poche du garde du jardin, ressortir. 500 $ ; la clé
    reste dans le sac.
  - **v02 — Le dossier du sergent** (Bouchard, après v01) : la porte de service, la cuisine, le corridor, le
    hall, le grand escalier ; à l'étage, le bureau du maire et le dossier qu'il garde sur Bouchard. 700 $ et
    deux pages de moins au casier.
  - **v03 — La chambre forte** (Sven, après v02) : l'escalier de la cave, le dédale, le terminal piraté (le
    labyrinthe électrifié, `longueur` 5) — le code ouvre la chambre forte —, le grand livre du maire,
    ressortir, le rapporter à Sven. 1 200 $.
- **Les juges** : `tests/test_infiltration_js.py` — la relève et la ronde, le « ? » puis l'alerte (et rien
  dans le dos), la serrure au clavier, l'escalier et la caméra qui reste dans son cadre, le GPS, la mission
  ratée qui fait retomber le dossier, et **les trois missions JOUÉES** : un marcheur au pas du joueur qui
  attend, recule ou se cache quand un garde le verrait, le vol au bouton, le piratage au clavier. Les
  mutations (retirer l'alerte, la relève, le cadre, l'`objet` du piratage, le vol, `rendre`) les font
  rougir. `blocs.erreurs` juge les lieux, les escaliers, les rondes et les cadres ; `test_missions` juge
  `obtenir`.
- ⚠️ **Ce que le banc a montré** : un garde qui s'arrête à un coin se TOURNE (son cap de pause) — le suivre
  de près dans une ligne droite, c'est se faire voir au coin ; le bon moment pour le vol est une longue
  ligne droite, et on attend caché, derrière la palissade (le chemin n'est pas privé). Et un marcheur qui
  recule vers le centre d'une tuile bordée d'un arbre ne l'atteint jamais (le décor le repousse d'un pixel).
- **À voir par Martin** : la difficulté (le repérage, le pas des gardes, les rondes), l'éclairage de la
  villa la nuit (quelques lampes, le reste noir), et les voix (générées, pas écoutées).
