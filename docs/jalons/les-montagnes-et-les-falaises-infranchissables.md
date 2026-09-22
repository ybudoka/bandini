# Les montagnes et les falaises infranchissables

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (21 sept. 2026) :_ « ajoute des falaises et montagnes infranchissable pour
délimiter les endroits strategique ».

Deux questions tranchées avec Martin avant de coder (l'endroit, puis le besoin) : le relief
délimite des **zones précises de la carte** (pas tout le pourtour au hasard), et sert à la fois de
**bordure de carte** et de **renfort autour de l'aéroport**.

- ⚠️ **La trame ne bouge pas.** Le chenal du 17 sept. l'a montré : changer une rangée ou une
  colonne de `COLONNES`/`RANGEES`/`RUES_V`/`RUES_H` re-tire toute la ville (26 juges sans rapport
  tombés d'un coup). Le relief se pose comme l'aéroport et l'Île-aux-Corneilles : en **ajoutant**
  au bord de la carte finie, jamais en la redessinant.
- ⚠️ **Est et sud seulement, pour l'instant.** Ajouter des colonnes après la dernière rue (à
  l'est) ne décale aucune coordonnée déjà posée — exactement comme l'aéroport a ajouté des
  rangées après la dernière rue (au sud). Ajouter au **nord** ou à l'**ouest** décalerait TOUT ce
  qui a un `x, y` dans la ville entière (portes, décor, personnages, missions, chantiers, zones…) :
  un chantier à part, bien plus gros que celui-ci, pas dans cette vague. Le nord et l'ouest
  gardent leur mur invisible déjà en place (`solidite` hors carte = 1, déjà infranchissable) —
  seulement, on ne le VOIT pas encore.
- ⚠️ **Ce qui se pose**, en tout dernier dans `generer`, sans un dé (comme `aeroport.poser`) :
  1. une chaîne de **montagnes à l'est** de la ville — des colonnes ajoutées après la dernière rue,
     une paroi de **falaise** en bordure (le mur qu'on voit depuis la ville) puis du rocher plein
     derrière, jusqu'au bord de la carte ;
  2. des **falaises au sud du large**, au-delà de l'aéroport — le « large » (`baie`) est de l'eau à
     perte de vue depuis le 21 sept. ; une ligne de falaises au bord lui donne une limite, et une
     raison de ne pas naviguer plus loin.
- ⚠️ Le relief est **infranchissable** comme une façade (`solide 1`) : ni à pied, ni en char, ni en
  bateau, ni à la nage — ce n'est pas une clôture qu'on enjambe ou qu'on défonce, ni de l'eau qu'on
  traverse à bout de souffle.
- ⚠️ Posé **après l'aéroport** (le dernier morceau de ville aujourd'hui) : rien de la ville
  d'aujourd'hui, aéroport compris, ne bouge d'une tuile.

## Notes

**Livré le 21 sept. 2026** — `app/relief.py`, deux glyphes dans `carte.LEGENDE` (`M` montagne, `C`
falaise, `solide 1`), leur rendu dans `sprites.js`, `tests/test_relief.py`.

La carte passe de 419 × 304 à **459 × 304** tuiles : quarante colonnes ajoutées après la dernière
rue de la trame, à l'est — deux de falaise (la paroi qu'on voit depuis la ville), trente-huit de
montagne. Posé en tout dernier dans `generer`, après l'aéroport : `_agrandir_a_l_est` ajoute les
colonnes (sol, voie, bouchon) sur toute la hauteur de la carte et rend sa fiche
(`ville["relief"]["montagnes"]`, `{x, y, l, h}`), lue par les juges de trame à la place d'un
419 codé en dur. `_falaises_du_large` referme ensuite le « large » au sud de l'aéroport, colonne
par colonne, en s'arrêtant net à la première tuile qui n'est pas de l'eau (jamais la clôture, la
grève ou un bâtiment) — et seulement si l'aéroport existe (`ville["aeroport"]["masque"]["carte_h"]`
donne la borne nord ; sans lui, pas de « large » à border).

- ⚠️ **Le rendu évite le papier peint.** `varianteDePassage` (le repli générique de `monde.js` pour
  un glyphe sans propriété particulière) ne rend que quatre valeurs — assez pour un rocher qui se
  répète en grille à l'échelle d'une chaîne de montagnes, la même leçon que le trottoir et l'herbe.
  Le bruit vient donc de la POSITION (`points`, qui boucle sur seize points par tuile), jamais d'une
  forme géométrique fixe.
- ⚠️ **`_empreinte` ne voit jamais le relief** (`test_carte.py`, « une pièce plus grande que sa
  maison ») : la rue qui longe le bord est de la trame n'a aucune tuile `solide == 1`, donc rien ne
  fusionne le relief à un mur de bâtiment par erreur — vérifié colonne par colonne
  (`test_la_chaine_ne_touche_aucun_batiment`). Falaises du sud et montagnes de l'est, eux, se
  touchent bien au coin sud-est : c'est voulu.
- ⚠️ **Deux juges existants tenaient une largeur codée en dur** (`test_carte.py`,
  `test_trottoir.py`) et deux autres une somme district + large = largeur totale
  (`test_districts.py`, l'aire de la ville) ou une hypothèse « rien que de l'eau hors du plan de
  l'aéroport » (`test_aeroport.py`) : ajustés pour lire `ville["relief"]`, comme la hauteur l'a été
  pour l'aéroport le 21 sept. « La Pointe, une fois le pont défait, ne voit aucune rive » (`test_eau.py`)
  tombait aussi : son BFS de « terre » ne distinguait pas une façade d'un pan de montagne — les
  deux sont juste « pas de l'eau » — et le relief, en touchant le vieux bord est de la trame, fusionnait
  silencieusement La Pointe au reste de la ville par la roche. Corrigé en traitant `M`/`C` comme un
  obstacle des deux côtés du calcul, pas une terre qu'on rejoint.
- ⚠️ **Le poids** : la carte gagne 24 346 octets bruts (quarante colonnes de plus, sur 304 rangées,
  deux calques : sol et voie) pour 178 de plus sur le fil (le rocher, très répétitif, se compresse
  presque aussi bien que l'eau) — 507 263 / 520 000 bruts, 50 586 / 53 000 gzip
  (`test_definitions.py`), sans qu'il ait fallu monter les plafonds.
- ⚠️ **Nord et ouest restent le mur invisible d'aujourd'hui**, sans changement : les agrandir
  décalerait toutes les coordonnées de la ville (portes, décor, missions, chantiers, zones…), un
  chantier à part, tranché avec Martin comme hors de cette vague.
