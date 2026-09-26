# La cabane à sucre : un événement de printemps

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ une fois par partie, au printemps du jeu, la ville sent le sirop — une cabane s'ouvre
dans les bois de La Pointe, avec ses missions, son défi et son menu.

**Aujourd'hui** le jeu n'a pas de saisons : il a des jours, des heures, et la neige de M12 (`neige.js`), une
intensité **tirée du jour et de l'heure** — rien à simuler, deux joueurs voient la même tempête. La cabane
prend le même chemin : ouverte certains jours, calculée, jamais tirée au dé.

- **La cabane** : une pièce neuve dans les bois (`tuileDeBois` existe), un comptoir (oreilles de crisse,
  fèves au lard, tire sur la neige — qui remplit le souffle comme un café), un violoneux.
- **Une mission** : le camion de sirop du cousin de Lulu, à livrer sans bosse (la prime `sans_degats`
  existe) — le sirop, ça se renverse.
- **Un défi** : la tire sur la neige, un jeu d'adresse de foire (le rail des défis de la foire existe).
- **La saison** : « le printemps » = une fenêtre de jours (par exemple les jours 20 à 26 d'une partie), pas
  une date réelle — le jeu se joue en tout temps.

⚠️ **Ce qui guette** : une pièce de plus dans la ville se pose **en dernier, sans dé** (sinon la ville
glisse) ; une cabane fermée hors saison ne doit pas enfermer un lieu de mission (le juge des barrières) ;
la musique de violon est une dépense ElevenLabs (à trancher par Martin).

**Juges** : la cabane n'ouvre que dans sa fenêtre, et le même jour pour tout le monde ; hors saison elle
se dit fermée (pas un menu vide) ; la mission se joue au banc de l'appel à la prime.

## Notes

_Livré le 26 sept. 2026._

- **La saison** : le printemps de l'année du jeu (`calendrier.py` : avril et mai, les jours 11 à 16 de
  chaque année de quarante jours) — pas une fenêtre « des jours 20 à 26 d'une partie » : l'année existe
  depuis le pont de glace, et une cabane qui ne revient jamais ne se revisite pas.
- **Un bloc de carte** (`app/blocs/cabane.py`) : la ligne des blocs la portait, et une pièce de plus EN
  VILLE aurait fait glisser la ville. ⚠️ La fiche la voulait dans les bois de La Pointe — on n'y pousse
  contre aucun bord (seuls le nord et l'ouest de la carte se marchent) : elle est au bout d'un rang, par le
  bord NORD du Faubourg (colonnes 200 à 204). L'érablière, la cabane en bois rond au toit à deux
  versants, l'allée de pierre ; dedans, la salle des sucres — le poêle, la corde de bois, le comptoir, les
  grandes tables de pin et leurs bancs.
- **Le comptoir** (`magasins.COMPTOIRS["sucre"]`) : oreilles de crisse, fèves au lard, tire sur la neige
  (qui remplit le souffle comme un café) ; ouvert de 7 h à 22 h (tout comptoir ouvre avant que le jeu commence, `test_la_nuit`). ⚠️ **De saison** (`saison`) : hors du
  printemps, il se dit « FERMÉ — ON OUVRE AU TEMPS DES SUCRES » — pas un menu vide
  (`Missions.comptoirFerme`, qui vaudra pour tout comptoir de saison).
- **Le défi : la tire sur la neige** (`missions.DEFIS`, `tire` ; l'épreuve `tire` d'`Adresse`) : le comptoir
  le propose lui-même (`COMPTOIRS["sucre"]["defi"]`), comme un kiosque de foire, une fois ouvert (après trois
  défis : une partie neuve n'a que les dix de la v1). La triche SAUT VERS UN DÉFI la propose sur place (elle
  n'a pas de point en ville). Le sirop refroidit sur la
  neige ; ACTION quand il est à point, dans le vert : trop tôt il coule, trop tard il casse. Quatre
  palettes, deux ratées permises, et chaque palette refroidit plus vite. Le point change à l'empreinte du
  compte, jamais au dé. Prime 50 $.
- **Juges** : `test_cabane_js.py` (on entre dans le bloc et dans la cabane ; le repas des sucres et le
  défi au printemps, « FERMÉ… » l'hiver et l'été ; la tire se gagne à point, se rate les mains dans les
  poches ou trop tôt, sans un dé même en réussissant) ; `test_blocs.py` juge son plan. Chaque juge a été
  vu rougir sous sa mutation.
- **Pas fait, à dire** : la **mission du camion de sirop** du cousin de Lulu (M16) ; le **violoneux**
  (un personnage de plus, et sa musique est une dépense à trancher) ; « la ville sent le sirop » (une
  ligne du Clairon au printemps viendrait facilement).
