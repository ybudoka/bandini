# La cabane à sucre, pour vrai

← [le plan](../plan.md) · [les jalons livrés](README.md) · [la cabane à sucre](la-cabane-a-sucre.md#notes) · [les blocs de carte](des-blocs-de-carte-en-extensions.md#notes)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « la cabane à sucre a besoin de tout ce qui fait une vraie cabane :
promenade en calèche avec chevaux, seaux et tubulure sur les arbres, banc de neige avec la tire, etc. »

La cabane livrée le 26 sept. ([notes](la-cabane-a-sucre.md#notes)) est une cabane en bois rond au bout du rang,
avec sa salle, son repas des sucres et le défi de la tire — mais dehors, rien ne dit « érablière » : des arbres
comme partout, une façade, et personne.

- **L'érablière** : des érables autour de la cabane, leurs **chaudières** (des seaux de tôle au couvercle
  pointu, accrochés au tronc) près de la cabane, et la **tubulure bleue** d'arbre en arbre plus loin, qui
  descend vers la cabane par un tuyau maître.
- **La cabane crédible** : la **cheminée** de l'évaporateur qui fume, et la **vapeur** blanche qui sort du
  lanterneau du toit quand on fait bouillir ; les **cordes de bois** le long du mur ; la **table de tire**
  dehors — un **banc de neige** dans une auge de bois, où l'on verse le sirop chaud en rubans et où on le
  roule sur un bâton.
- **La calèche** : deux chevaux attelés, un cocher ; elle attend à son arrêt près de la cabane, on monte
  (ACTION), elle fait le tour de l'érablière par son sentier et nous redépose. Les chevaux sont dessinés et
  trottent (les pattes, la tête, la queue).
- **La vie** : des gens à la cabane au temps des sucres (autour de la table de tire, sur la galerie, qui
  flânent), un violoneux si l'audio existe déjà (le reel du musicien de rue) — sans dépense neuve.

⚠️ **Ce qui guette** : le rang est un bloc — changer son plan ne fait pas glisser la ville, mais le chalet,
sa planque et les juges du rang lisent ses coordonnées : on ne touche qu'à l'érablière, loin d'eux. Rien au
dé (tout à l'empreinte ou à `B.t`). Chaque dessin se regarde par capture. La vague « un vrai dehors » des
blocs (trafic, passants, police, nuit d'un bloc) : à trancher selon ce dont la cabane a besoin.

**Juges** : les érables ont leurs chaudières et leur tubulure (le plan et le dessin) ; la vapeur ne sort qu'au
temps des sucres, et sans dé ; la table de tire lance le défi ; on monte dans la calèche, elle fait le tour et
nous redépose où l'on est monté ; les chevaux bougent ; les gens de la cabane naissent au printemps et pas
l'hiver.

## Notes

_Livré le 28 sept. 2026._ Module neuf : `static/js/cabane.js` (`Cabane`) ; au rang, `CABANE` dans
`app/blocs/rang.py`. Captures regardées : la cour, le toit qui fume, l'érablière du nord, la calèche dans ses
quatre sens, la table de tire, l'été et la nuit.

- **L'érablière** : au nord de la cabane, trois rangs d'**érables en tubulure** (`T` → `erable_tube`, leur
  chalumeau bleu) ; la ligne bleue court d'arbre en arbre jusqu'au **tuyau maître** qui descend la colonne 65
  jusqu'au toit (`Cabane.dessinerSol`, calculée une fois par visite, sous les arbres). Au sud, le long du
  sentier de la calèche, une érablière de bois franc aux **chaudières** (`E` → `erable_seau`, le seau de tôle
  au couvercle pointu sous son chalumeau) — posée à l'empreinte de la tuile dans le script qui a composé le
  plan, pas au dé : une forêt, pas un verger. L'érable a son dessin (`peindreErable`) : l'écorce grise, la cime
  ronde, les bourgeons rouges du printemps. Les érables et leurs chaudières sont là toute l'année.
- **La cabane crédible** : la **cheminée de tôle** de l'évaporateur et le **lanterneau** du faîte (des
  persiennes sous un petit toit) — ils fument au temps des sucres, pendant les heures du comptoir (la fumée
  grise de la tôle, la vapeur blanche du lanterneau : `Blocs.fume`, `genre`, `sucres`, `VAPEUR`) ; les
  **cordes de bois** contre les deux flancs (`L` → `corde_bois`, des bouts de bûches ronds en trois rangs) ;
  la **table de tire** dans la cour (`=` → `table_tire`) : l'auge de bois sur ses pattes, pleine de neige
  tassée, où les rubans de sirop s'allongent un à un (le dernier doré, les autres roulés sur leur bâton), puis
  tout est mangé et on recommence ; hors saison, la neige propre (`poseManuelle`). **ACTION devant la table**
  propose le défi de la tire au temps des sucres (s'il est ouvert) ; sinon elle dit pourquoi.
- **La calèche** : deux chevaux (un bai, un alezan) attelés à une caisse rouge au filet doré, trois bancs, un
  cocher. Elle attend 7 s à son arrêt (la pancarte CALÈCHE, face à l'allée de la cabane), fait le tour de
  l'érablière (1 312 px de sentier de gravier, deux tuiles de large, à 0,75 px par image : une trentaine de
  secondes) et revient. **On monte** derrière elle (ACTION, « UN TOUR DE CALÈCHE », gratuit — pas avec des
  étoiles), assis au banc du fond, et on descend à l'arrêt au bout du tour (`j.manege.quoi === 'caleche'`,
  comme le petit train de la foire ; `Foire.majPassager` la laisse à `Cabane`). De profil, les chevaux
  **trottent** par paires diagonales, la tête hoche, la queue balance, les roues tournent ; de dos et de
  face, les pattes se lèvent tour à tour. On ne passe pas au travers (`Cabane.bloquer`). Hors des heures, le
  cocher est couché : elle attend à l'arrêt.
- **Les gens** : au temps des sucres, pendant les heures du comptoir — le tireur derrière la table, trois qui
  roulent leur tire, deux qui jasent près de la cabane, deux qui attendent la calèche, et **le musicien à la
  porte qui joue le reel** (`rue_reel`, la pièce du musicien de rue : un air de danse québécois, déjà payé).
  Ils tiennent leur place (`fige`) et naissent avec un dé **prêté** (`sansDe`, tiré à l'empreinte) : entrer au
  rang ne décale pas le hasard du jeu. À la fermeture, ils rentrent — hors de la vue. L'hiver et l'été,
  personne.
- ⚠️ **La vague « un vrai dehors » des blocs n'a pas servi** : la cabane voulait des gens, pas des passants —
  les siens tiennent leur place et naissent avec leur cabane, comme les spectateurs du ciné-parc. Ni trafic, ni
  police de ronde, ni passants qui flânent (ils tireraient au dé à chaque pas) : la vague attend toujours un
  bloc qui en a besoin (les Galeries le jour, un centre d'achat plein de monde ?).
- **Juges** : `tests/test_cabane_pour_vrai_js.py` (5 : on monte, elle fait le tour par le fond de l'érablière
  et nous redépose à l'arrêt ; les sabots trottent quand elle roule, pas à l'arrêt, et un tour complet plus la
  naissance des gens ne prennent pas un tirage de `B.rng()` ; les gens au printemps, le musicien et son reel,
  personne ne s'évapore sous nos yeux, personne l'hiver ni la nuit, la table propre hors saison ; la vapeur au
  temps des sucres seulement, la tubulure bleue et le maître jusqu'au toit ; la table propose le défi, « FERMÉ »
  l'été) ; `tests/test_rang.py` (3 de plus : les chaudières et la tubulure jusqu'au toit, le sentier libre de
  gravier et d'arbres sous toute la calèche et son arrêt rejoint à pied, les gens là où l'on marche et hors du
  sentier). **Seize mutations, toutes rouges** — dont une qui ne mordait pas au premier essai (le juge du trot
  comparait tout le dessin, et la queue qui balance le rendait vert sans une patte levée : il compare les
  sabots, en coordonnées d'écran).
- **Pas fait, à dire** : le **violon** — le musicien joue le reel du trottoir, à la guitare ; un vrai
  violoneux serait une musique ElevenLabs de plus (une dépense à trancher par Martin). Pas de bruit de sabots
  ni de hennissement (aucun bruitage n'existe). La calèche n'arrête pas les chars (le joueur peut la traverser
  en auto). La saison n'est pas peinte : l'érablière est verte au printemps (le jalon des quatre saisons).
