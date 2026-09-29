# Une amélioration générale des toits

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 25 sept. 2026, en regardant le chalet du rang : « une amélioration générale
des toits »._

_Ce que ça donne :_ la moitié de ce qu'on voit à l'écran, c'est des toits — vue de dessus, une ville
est d'abord ses toits. Qu'ils racontent le bâtiment dessous : son âge, son quartier, son métier.

**Aujourd'hui** (`static/js/sprites.js`, « Les toits ») : **quatre matières** — tôle, ardoise, gravier
(`toitPlat`) et bardeau (`toitEnPente`, deux versants et une ligne de faîte) — peintes tuile par
tuile, **une couleur par matière pour toute la ville**. Par-dessus, 242 objets de toit (`carte.toits`) :
122 ventilations, 33 cheminées, 30 antennes, 21 réservoirs, 19 climatiseurs, 15 cages d'escalier, un
clocher, une tour de contrôle. Sur les captures du chalet, le grand toit de bardeau est un rectangle
brun uniforme qui écrase la façade.

**Ce qu'on veut** (à trancher par Martin — la liste, et par où commencer) :

- **Une teinte par bâtiment**, pas par matière : tirée à l'empreinte du bâtiment, dans une palette par
  matière et par standing du quartier (les quartiers riches, pauvres et zonés existent) — un bardeau
  neuf vert forêt aux Érables, un bardeau délavé au Faubourg.
- **Les bords** : la rive et la gouttière d'un toit en pente, le parapet d'un toit plat, et l'ombre
  que le toit jette au sol du côté opposé au soleil — ce qui donne du RELIEF à une ville vue de haut.
- **Les versants et les pignons** : des toits à quatre versants, en L, à pignon sur rue, au lieu du
  seul toit à deux versants en long.
- **L'usure** : des bardeaux manquants, des taches de rouille sur la tôle, de la mousse sur l'ardoise
  au nord, des flaques sur le gravier après la pluie.
- **Plus d'objets, mieux posés** : des puits de lumière, des panneaux solaires, des cordes à linge sur
  les toits plats des Quais, des nids de goélands, des lucarnes sur les toits en pente.
- **Les saisons et la nuit** : la neige qui reste sur les toits (M12, `neige.js`), les fenêtres de
  lucarne qui s'allument la nuit.
- **Le chalet du rang** d'abord, comme banc d'essai : un toit de **bardeaux de cèdre** qui va avec son
  bois rond (`app/blocs/chalet.py`, les `materiaux` d'une carte de bloc peignent déjà autrement les
  glyphes d'un bloc).

⚠️ **Ce qui coûte, et ce qui guette :**

- **Le cache des morceaux** : les toits se peignent dans les morceaux de 256 px (`peindreMorceau`), une
  fois. Une teinte par bâtiment multiplie les tuiles cuites (`Atlas.cuireTuile` met en cache par glyphe
  et variante) — mesurer la mémoire et le temps de cuisson sur le téléphone de Martin (la dette du rythme).
- **Rien au dé** : une teinte, une usure, un objet se tirent à l'EMPREINTE du bâtiment (`hash2`),
  jamais `B.rng()` — sinon tout le hasard du jeu glisse, et une ville qui change de couleur à chaque
  partie n'a pas de quartiers.
- **Les juges visuels ne voient rien** : une capture avant et après chaque vague (« regarder une couche
  peinte »), et les écrans de Martin.
- **Les toits sont solides** : aucun changement de glyphe (la trame et la carte ne bougent pas) ; tout se
  joue dans le peintre et dans `carte.toits`.

**Juges** : la teinte d'un toit est la même d'une partie à l'autre et diffère entre deux bâtiments
voisins de même matière ; aucun `B.rng()` n'est tiré par le dessin ; la carte (`/api/carte`) ne change
que par ses objets de toit ; le temps de cuisson d'un morceau reste sous son budget.

## Notes

_Tranché par Martin le 29 sept. 2026 : les quatre — une teinte par bâtiment ; les bords, les gouttières et
l'ombre ; des formes de toit ; l'usure et des objets neufs — sur toute la ville, vague par vague (pas le chalet
d'abord)._

### Vague 1 — une teinte par bâtiment — **livrée le 29 sept. 2026**

- **Six teintes par matière** (`sprites.js`, `TOITS_TOLE`, `TOITS_ARDOISE`, `TOITS_GRAVIER`, `TOITS_BARDEAU`), de
  la plus neuve à la plus délavée : la tôle peinte verte, bleue, rouge de grange, la sienne, galvanisée, rouillée ;
  l'ardoise bleu nuit, violacée, verte, grise ; le gravier en membrane blanche refaite ou en goudron noirci ; le
  bardeau vert forêt, bourgogne, cèdre, asphalte gris, délavé. La teinte d'avant de chaque matière est la
  troisième : l'ordinaire ne change pas d'air.
- **Le quartier choisit dans lesquelles** (`Monde`, `TEINTES_DE_STANDING`) : le cossu dans les quatre plus
  neuves, le pauvre dans les quatre plus délavées, l'ordinaire au milieu.
- ⚠️ **Le bâtiment se retrouve sans une donnée de plus.** Le générateur ne couvre jamais deux bâtiments collés de
  la même matière (`Chantier.batiment_forme`) : un toit, c'est un morceau d'un seul tenant d'un même glyphe. Le
  navigateur les compte une fois par carte (`Monde.teintesDesToits`, un remplissage), au premier morceau peint —
  la carte, à son plafond gzip, ne grossit pas d'un octet.
- **Rien au dé** : la teinte se tire à l'empreinte du bâtiment (`hash2` de sa première tuile dans l'ordre de
  lecture) ; et deux toits de même matière à trois tuiles ou moins l'un de l'autre n'ont pas la même, tant que
  le quartier en a une autre à offrir.
- **Dans la variante de la tuile** : au-dessus du bord et du grain (bit 7 pour un toit plat, bit 6 pour une pente)
  — la cuisson reste une image par variante, et la neige des saisons (`Saisons.enneiger`) blanchit chaque teinte.
  Les toits peints par une matière de bloc (le chalet, les pièces) et la tôle des cabanes (`{`) gardent leur
  peintre.
- **Juges** : `test_toits_js.py` (les mêmes teintes d'un compte à l'autre, portées par la variante, quatre au
  moins par matière ; deux voisins de même matière jamais pareils, chaque toit dans les teintes de son quartier ;
  aucun `B.rng()`, et le compte sous 400 ms). Cinq mutations rouges. Capture avant/après aux Quais, au Faubourg,
  à La Shop.
- **Reste** : vague 2, les bords, les gouttières et l'ombre ; vague 3, des formes de toit ; vague 4, l'usure et
  des objets neufs.
