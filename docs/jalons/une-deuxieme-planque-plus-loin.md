# Une deuxième planque, plus loin

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 25 sept. 2026 : « une 2e planque plus loin »._

_Ce que ça donne :_ un endroit où dormir, sauvegarder et garer un char à l'autre bout de la ville — on ne
traverse plus toute la carte pour sauvegarder après une mission à La Pointe ou aux Érables.

**Aujourd'hui**, la planque de Rocco est la seule : un lit (DORMIR, la sauvegarde), un coffre, une
garde-robe, et **une seule place** de garage (`partie.planque.vehicule`, `estDeLaPlanque` : un char garé
là ne part jamais à la fourrière). L'hôtel prête un lit, mais rien d'autre.

**La deuxième** : loin de la première, dans un district que les missions longues font traverser — à
trancher par Martin :

- **un chalet dans les bois de La Pointe** (au bout du pont, près du phare et de la foire) ;
- **un bungalow des Érables** (les garages où l'on entre y sont déjà) ;
- ⚠️ **pas sur l'Île-aux-Corneilles** : elle ne se rejoint pas à pied, et une planque doit l'être.

⚠️ **Et depuis le 25 sept. 2026, une quatrième possibilité** : un chalet **dans un bloc de carte**, au bout
d'un chemin, derrière un fondu au noir ([des blocs de carte en extensions](des-blocs-de-carte-en-extensions.md#fiche),
tranché par Martin). « Plus loin » pour vrai, et la ville n'en bouge pas d'une tuile — mais il faut les
blocs d'abord.

**Comment on l'a** — à trancher aussi : l'**acheter** (comme un commerce, `economie.PROPRIETES`), ou la
**gagner** en mission (un personnage te la laisse, le fil de M16 s'y prête).

⚠️ **Ce qui coûte, et ce qui guette :**

- **« La planque » est écrite au singulier partout** : `partie.planque`, `estDeLaPlanque`, le spawn de
  début de partie, les véhicules `donne` « garé à la planque » (le taxi, l'autobus, la remorqueuse, la
  berline de Rocco…). Il faut décider pour chacun : la planque **la plus proche**, ou toujours la
  première ? La règle simple : on se réveille et on retrouve ses chars **à la planque où l'on a dormi**.
- **Le coffre** : un par planque, ou partagé (le même contenu aux deux endroits) ? Partagé est plus
  simple à jouer, séparé est plus « vrai ».
- **Une pièce de plus, garantie, dans la ville** : la poser **en dernier, sans dé** (même règle que les
  collections et l'aéroport), sinon toute la ville glisse.
- **Le décor conditionnel** de la ligne des collections (des objets qui apparaissent selon la partie)
  servira aux deux planques : faire cette ligne-là d'abord, ou les deux ensemble.

**Juges** : la deuxième planque est à pied de la première et à plus de N tuiles d'elle ; y dormir
sauvegarde et fait se réveiller là ; un char garé devant n'est jamais saisi ; une vieille sauvegarde (une
seule planque) se charge sans rien perdre.

## Notes

_Livré le 25 sept. 2026 : **le chalet du rang**, dans un bloc de carte (le choix de Martin)._

- **Où** : on pousse contre le bord OUEST des Quais, à côté de l'Hôtel Bandini (une plaque « CHALET ← ») —
  à l'autre bout de la ville par rapport à la planque de Rocco (au Faubourg). Noir, et on est sur le rang
  qui mène au chalet, au bord d'un étang (`app/blocs/chalet.py`, 44 × 30).
- **Le chalet** : en **bois rond** (Martin : « une vraie texture de bois rond ») — des rondins couchés, le
  calfeutrage clair entre eux, des nœuds, et **les bouts des rondins qui dépassent aux coins** en
  alternance (le glyphe `H`) ; fenêtres à croisillons, porte en planches. Captures : `captures/chalet/`.
- **Il s'achète** (2 500 $, le prix du bar — la fiche laissait le choix ; acheter se joue sans mission) :
  avant, son lit, son coffre et sa garde-robe ne proposent que « ACHETER LE CHALET DU RANG ».
- **On y dort, on s'y sauvegarde, et une partie rouverte s'y réveille** (`partie.bloc`) ; `p.x`/`p.y`
  restent le passage en ville — le repli si la carte du bloc ne vient pas.
- **Son char** : celui qu'on gare sur sa place revient avec la partie (`partie.charsDesPlanques`), comme
  devant la planque de Rocco ; et le bloc s'en souvient le temps de la partie.
- **Le coffre est partagé** avec celui de la planque de Rocco (la fiche laissait le choix ; le même magot
  rangé à deux endroits se joue mieux).
- **Les chars donnés en mission** (le taxi de m97…) restent garés devant la planque de Rocco : « la
  planque » au singulier du code, c'est elle.
- ⚠️ **Un défaut trouvé en chemin, et réparé** : sauvegarder depuis un bloc cherchait la porte de la
  planque de Rocco dans la carte COURANTE — le char qui l'attendait était oublié. (Et un comportement
  d'avant, laissé tel quel : la ville oublie un char garé loin du joueur, planque ou pas.)
- **Juges** : `tests/test_chalet_js.py` (7 : il s'achète avant de servir, on y dort et la partie s'y
  réveille avec son char, hors ligne on retombe en ville sans rester au noir, le noir attend la carte au
  réveil, le bloc se souvient du char, la sauvegarde n'oublie plus le char de Rocco, tombé au chalet on va
  à l'hôpital et le chalet garde le char) — **six mutations, toutes rouges**.
