# Les feux s'allument pour vrai

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les feux s'allument pour vrai (**correctif**, taille 1) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « je veux que les feux de circulation et de piéton allument pour vrai. »

Ils sont **peints**, pas allumés — et la nuit, ça se retourne contre eux. `Base.fin` compose la
nuit en **multipliant** toute l'image par la teinte de l'heure, puis rajoute les lampes en
`lighter` par-dessus. Un feu n'a aucune lampe : il ne reçoit donc que la multiplication, comme
une brique. À minuit (teinte 26, 32, 80 à 0,72) :

| ce qu'on peint | de jour | à minuit |
|---|---|---|
| le vert des chars | 46, 204, 113 | **16, 76, 57** |
| le rouge des chars | 231, 76, 60 | **82, 28, 30** |
| le blanc qui dit MARCHE | 242, 242, 242 | **86, 90, 122** |
| le trottoir sous le poteau | 154, 150, 137 | 54, 56, 69 |

⚠️ **Le blanc du feu piéton à minuit est plus sombre qu'un trottoir de midi** (luminance 92
contre 150). Le seul objet de la ville qui éclaire pour vrai, c'est le **lampadaire** — et la
seule raison, c'est qu'il a une entrée dans `carte.lampes`. Les feux n'en ont pas.

- **Une ampoule allumée pose une lampe, de la couleur de sa phase.** Rouge, vert, orange, le
  blanc du piéton : ce n'est pas un halo jaune de plus, c'est **la couleur de l'information**
  qui se répand sur l'asphalte. C'est aussi ce qui fait qu'on lit un feu **de loin**, la nuit,
  avant même de distinguer le poteau.
- ⚠️ **Elles se ramassent EN DESSINANT, jamais en parcourant la ville.** `carte.lampes` est une
  liste fixe qu'on peut balayer ; les feux sont **482 poteaux** (124 pour les chars, 358 pour
  les piétons) dont la couleur change à chaque phase. Les parcourir par image pour trouver ceux
  de l'écran serait payer la ville entière pour en éclairer trente. `dessinerFeu` est déjà
  appelé **une fois par feu visible** — c'est là, et nulle part ailleurs, que la lampe se pose.
- ⚠️ **Et elles se vident toutes seules.** Une liste qu'un dessin remplit et qu'un autre module
  doit penser à vider finit par fuir le jour où quelqu'un dessine sans composer. Elle porte donc
  son numéro d'image (`B.image`, l'horloge de l'œil) : à l'image suivante, elle est vide sans
  que personne l'ait vidée.
- **Le plafond de `Base.fin` doit monter.** Il est à 25 lampes, taillé pour les lampadaires
  seuls. Un croisement, c'est 2 poteaux de chars (2 ampoules chacun) et jusqu'à 4 poteaux de
  piétons : **8 lampes** — et il en tient plusieurs à l'écran. Sans un plafond plus haut, les
  feux **éteindraient les lampadaires** au lieu de s'ajouter à eux.
- **De jour, une ampoule doit aussi se lire comme allumée**, et ça ne se joue pas sur la
  couleur : un carré vert plat est un carré vert. Ce qui dit « allumé », c'est un **cœur** plus
  pâle que le pourtour — la convention du pixel art pour une source de lumière, et la seule qui
  tienne dans trois pixels sur trois.
- ⚠️ **Deux ampoules à cinq pixels l'une de l'autre mélangent leurs halos.** Le feu des chars
  porte le nord-sud et l'est-ouest côte à côte : quand l'un est rouge et l'autre vert, la flaque
  au sol tire vers le jaune. C'est ce que fait un vrai croisement vu de haut ; ce qui doit rester
  **net**, c'est le cœur de chaque ampoule, donc les halos restent **petits**.
- ⚠️ **Le seuil de la brune est celui de tout le monde** : sous `ambiance().alpha` 0,2, les
  lampadaires ne s'allument pas et les feux non plus. Deux seuils voudraient dire deux règles
  pour « il fait noir », et la deuxième serait fausse un jour.
- **Juges** : à minuit, un feu au vert pose une lampe verte et un feu au rouge une lampe rouge —
  la couleur **suit la phase** ; en plein jour, aucune lampe ; l'orange **clignotant** du piéton
  n'éclaire pas pendant qu'il est éteint (sinon il clignote à l'œil et brille en continu au sol) ;
  et le compte des lampes d'une image tient sous le plafond de `Base.fin`.

**Livré le 14 sept. 2026.** ⚠️ **L'analyse ci-dessus était trop généreuse, et la mesure l'a
dit tout de suite** : les feux n'étaient pas *peints puis éteints par la nuit*, ils n'étaient **pas
peints du tout**. Le premier juge écrit — « un feu au vert pose une lampe verte » — est revenu
avec **zéro lampe**, à midi comme à minuit. En remontant : `dessinerFeu` et `dessinerFeuPieton`
n'avaient **jamais été appelés une seule fois** depuis qu'on a posé les feux.

- ⚠️ **Un champ de trop suffisait.** `creerSignalisation` créait l'entité avec `decor: 'feu'`, et
  `Entites.dessiner` teste `if (e.decor)` **avant** `if (e.type === 'feu')` : la branche générique
  peignait le boîtier cuit — le poteau noir, sans lanternes — et faisait `continue`. Le peintre
  nommé était derrière, inatteignable. **482 poteaux** noirs (124 pour les chars, 358 pour les
  piétons), à tous les croisements de la ville, depuis le premier jour.
- ⚠️ **Et le champ ne servait à rien.** Un feu n'est pas solide, il n'entre donc jamais dans
  `grilleFixe` — les deux seuls autres lecteurs de `e.decor` (`bloquerParDecor`, `heurterDecor`)
  passent par là. Il ne faisait que **masquer le peintre**. Il est parti, **et** l'ordre du
  dispatch est corrigé : les peintres nommés d'abord, la branche générique ensuite. Dans l'autre
  sens, le prochain `decor` posé sur une entité qui a déjà son peintre l'effacerait pareil.
- ⚠️ **Pourquoi aucun juge ne l'a vu, et c'est la vraie leçon.** Les feux avaient déjà quatre
  juges — l'alternance, les T sans feu, le dégagement de 180 images, les poteaux posés sur le
  trottoir et pas sur la route. **Tous parlent de l'horloge ou de la carte, aucun du dessin.** Un
  système peut être juste de bout en bout et ne rien montrer ; il manquait la question bête :
  *est-ce qu'on voit quelque chose ?* Le banc sait y répondre — `ctx.traces` garde chaque
  `fillRect` — et c'est ce que fait le juge neuf `test_un_feu_peint_ses_lanternes...`, **en plein
  jour**, là où aucune lampe ne vient aider.
- **La lampe, ensuite**, comme prévu : une par ampoule allumée, de la couleur de sa phase,
  ramassée **en dessinant** (`Vehicules.lampesDesFeux()`), remise à `Base.fin` par `jeu.js`. La
  liste porte son numéro d'image et se vide toute seule.
- ⚠️ **Le rayon s'est décidé à l'écran, pas sur le papier.** À **10 px**, les deux ampoules du feu
  des chars — cinq pixels d'écart — additionnaient assez de rouge et de vert pour rendre du
  **blanc** : on voyait bien qu'un feu brillait, on ne lisait plus **lequel des deux sens** était
  vert. À **7 px** et une lumière moins forte, les deux cœurs restent nets et la flaque tire vers
  le jaune, ce qui est ce que fait un vrai croisement vu d'en haut. Le lampadaire garde ses 44 px :
  lui éclaire une rue, un feu ne s'éclaire que lui-même — et la hiérarchie se voit.
- **Le plafond de `Base.fin` passe de 25 à 50** : 25 lampadaires (`lampesVisibles`), 24 feux et le
  projecteur de l'hélico. Deux juges le tiennent, et ils **lisent les trois nombres dans le JS**
  plutôt que de les recopier — avec le seuil de la brune, qui doit rester **le même** que celui des
  lampadaires.
- **Juges (5 neufs)** : un feu **peint** ses deux lanternes (vert pour le sens qui roule, rouge pour
  l'autre) et son cœur, en plein midi, mesuré sur les rectangles ; à minuit une ampoule pose une
  lampe et **la couleur suit la phase** (les deux sens échangent au demi-cycle, l'orange n'est ni
  l'un ni l'autre) ; **rien n'éclaire à midi** ; l'orange qui clignote **n'éclaire pas** pendant
  qu'il est éteint ; le plafond de lampes et le seuil de la brune tiennent. Les trois juges de banc
  sont **rouges sur le code d'avant** — vérifié en remettant le bogue.
- **Ce qui reste ouvert, inchangé** : la traverse elle-même ne s'éclaire toujours pas (tuiles
  cuites dans le morceau de 256 px), et les feux ne passent pas au **clignotant la nuit** — c'est
  M12, « la ville vit ».

## Notes

demande de Martin : « je veux que les feux de circulation et de piéton allument pour vrai ».

- ⚠️ **Ils n'ont jamais été allumés du tout, et personne ne l'a vu.** L'entité portait
  `decor: 'feu'`, et `Entites.dessiner` teste `if (e.decor)` **avant**
  `if (e.type === 'feu')` : la branche générique peignait le boîtier cuit et s'en allait.
  `dessinerFeu` n'a **jamais** été appelé — ni rouge, ni vert, ni blanc, un poteau noir à
  chacun des **482** coins de la ville. Aucun juge ne le voyait : ils parlent tous de
  l'**horloge** (`feuVert`, `feuPieton`, l'alternance, le dégagement), aucun du **dessin**.
  Et la nuit s'ajoutait à ça : sans lampe à elle, une ampoule ne reçoit que la
  **multiplication** du voile — le vert (46, 204, 113) tombe à (16, 76, 57), le blanc qui
  dit MARCHE (242, 242, 242) à (86, 90, 122), **plus sombre qu'un trottoir de midi**.
  Maintenant : les peintres nommés passent **avant** la branche générique, chaque ampoule a
  un **cœur** plus pâle qui la dit allumée, et elle **pose sa lampe** à la brune, de la
  couleur de sa phase, ramassée **en dessinant**. 5 juges neufs
