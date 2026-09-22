# Des squelettes qu'on habille : chapeaux, casquettes, et une garde-robe presque infinie

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026) : « les personnages doivent pouvoir avoir des chapeaux, casquettes et
plus — idéalement des squelettes qu'on habille, ce qui donne une presque infinité
d'habillement » ; « il faut plusieurs types de squelettes pour les types de personnes ».
Vague 1 (le moteur et la rue) : des SQUELETTES (`homme` = le corps actuel et ses 42 poses ;
`femme`, `costaud`, `vieux`, `grand` dérivés par règles ; `enfant`) et des PIÈCES qu'on
enfile (coiffure, chapeau, haut, bas, souliers, accessoires), catalogue dans
`app/garderobe.py`, assemblage dans `static/js/garderobe.js` (grilles composées puis cuites
par `Atlas`, le chapeau posé sur la tête que chaque pose montre). Chaque passant ordinaire
tiré dans la garde-robe de son archétype à l'empreinte de son id (aucun dé : la ville ne
bouge pas) ; les donneurs habillés d'après leur portrait. Vague 2 : le joueur s'habille
(chapeaux au magasin), agents et gangs en pièces.

## Notes

**Vague 1 livrée le 22 sept. 2026 — le moteur et la rue.**

- **Six squelettes** (`garderobe.js`, `squelette`). `homme` est le corps du joueur tel quel, ses
  38 poses dessinées (marche, coups, gestes de scène, assis, à vélo, au volant, couché). Les autres
  en sont DÉRIVÉS par des règles sur les rangées, pose par pose : `costaud` (torse et hanches d'un
  pixel plus larges ; de profil, le ventre seul), `vieux` (une rangée de jambes de moins, la tête
  en avant de profil), `grand` (une rangée de jambes de plus), `femme` (une rangée de moins, les
  hanches plus larges de face). `enfant` est `SPRITES.enfant` (trois vues seulement). Chaque grille
  gagne 3 rangées au-dessus et 2 colonnes de chaque côté : la place d'un chapeau et d'un bord de feutre.
- **Les lettres du squelette sont des RÉGIONS** (`h s o c p b`) : une pièce les recolore
  (t-shirt = l'avant-bras redevient peau, salopette = bavette et bretelles, robe = les jambes
  deviennent le haut…). Le chapeau est un petit dessin par vue, posé sur la tête que la pose MONTRE
  (`tete` : la boîte des pixels `h`/`o` au-dessus du premier `c`) — il suit donc un geste, une
  pose assise ou à vélo sans rien écrire de plus. Couché, il tombe.
- **13 chapeaux** (casquette, à l'envers, tuque à pompon, feutre, casque de chantier, képi,
  canotier, béret, bandana, cowboy, casquette de marin, capuche), **10 coiffures**, **12 hauts**,
  **3 motifs**, short, jupe, bottes, **7 accessoires** (lunettes, verres fumés, barbe, moustache, sac
  à dos, cravate, foulard).
- **La rue.** 21 archétypes au corps commun ont leur garde-robe (`garderobe.GARDE_ROBES`) ; chaque
  passant tire sa tenue à l'EMPREINTE de son id (`hash2(e.id, …)`), jamais `B.rng` — un juge le
  vérifie en comparant le dé suivant avec et sans garde-robe (et il a rougi quand on a fait tirer
  un dé à `tirer`). Un gang garde sa couleur (`haut_fixe`). Sur 40 passants, 35 tenues ou plus
  différentes.
- **Les personnages** portent la tenue de leur portrait (`tenue_du_personnage`) : le képi de
  Bouchard, la tuque du Grand Mo, le canotier du Bonimenteur, la casquette de Fern.
- **La cuisson est paresseuse et bornée** : une tenue ne peint une pose que la première fois
  qu'on la dessine (des getters sur `poses`), et le cache garde les 240 dernières tenues. Chaque
  passant ayant la sienne, un cache à la `Atlas` aurait grossi toute la partie.
- ⚠️ **Celui qu'on jette de son vélo ou de sa moto changeait de tête** (trois juges l'ont vu) : le
  pilote ne voyageait qu'avec ses couleurs (`v.pilote.swaps`), et en redescendant il retirait une
  tenue neuve. La tenue voyage maintenant avec lui (`v.pilote.tenue`), le cycliste du trafic est
  habillé dès sa naissance sur la selle, et des couleurs imposées sans tenue sont reprises par la
  tenue tirée.
- **Ce qui reste (vague 2)** : le cavalier d'un deux-roues se dessine encore avec ses seules
  couleurs (`imageDuCavalier`, sans chapeau) ; le joueur ne s'habille pas encore (le magasin vend
  des couleurs) ; les agents et les gardes gardent leur palette (`police.js`).
- ⚠️ Le paquet de définitions, déjà au-dessus de son plafond avant ce jalon, prend ≈23 Ko de plus
  (les garde-robes répètent leurs listes de peaux et de cheveux ; à factoriser si on sort les
  dialogues du paquet).
