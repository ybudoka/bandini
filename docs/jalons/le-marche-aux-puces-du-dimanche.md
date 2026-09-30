# Le marché aux puces du dimanche

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ le dimanche, un stationnement se remplit d'étals, et on y trouve ce qu'aucun
magasin ne vend — les meubles de la planque, les cartes de hockey qui manquent, une arme rouillée.

- **Quand** : un jour sur sept du jeu, de l'aube à midi, dans un stationnement qui existe déjà (pas de pièce
  neuve).
- **Ce qui se vend** : un étal qui change **chaque semaine** — tiré de la semaine du jeu par un hachage,
  pas au dé (la règle des prix de la contrebande, `facteurDuJour`). On y marchande : un prix affiché, un
  bouton pour offrir moins, et le vendeur accepte ou refuse selon son humeur (calculée, elle aussi).
- **Le lien** : c'est là que la ligne des collections trouve ses meubles et ses cartes manquantes ; la
  faire après elle.

⚠️ **Ce qui guette** : des étals et des passants de plus un matin par semaine — le trafic ne doit pas
s'empiler dans le stationnement (le juge du trafic), et rien ne se pose au dé.

**Juges** : le même dimanche, le même étal pour tout le monde ; il change la semaine suivante ; marchander ne
tire aucun `B.rng()` ; un meuble acheté va à la planque.

## Notes

### Livré le 30 sept. 2026 (Martin : « le marché aux puces du dimanche », après les collections)

- **Quand** : le dimanche — le jour de partie divisible par sept (le 7, le 14…) —, de 6 h à midi. « La semaine »,
  c'est `(jour - 1) // 7`.
- **Où, sans un dé** (`app/puces.py`, appelé en tout dernier par `collectionner.poser`) : ⚠️ **pas un stationnement**
  comme la fiche le proposait — ses allées sont celles des chars, et des étals peints y auraient été traversés par le
  trafic (le « trafic qui s'empile » de la fiche). Martin avait dit « dans un lieu à choisir » : c'est **le terrain
  vague le plus près de la planque, à pied** — huit tuiles sur quatre d'herbe ou de friche, rien de posé dessus ni
  autour, hors des cours de gangs et des chantiers, loin des trouvailles et des pistes des sauts. Sur la graine
  livrée : l'herbe au bord du trottoir, au coin des Friches et du Petit-Canton (104, 106).
- **Deux étals, deux marchands, peints** (`static/js/puces.js`, aucune entité : rien ne naît, rien ne s'empile) :
  **Ti-Rhéal** et ses cartes de hockey — quatre numéros par semaine, tirés de la SEMAINE par un hachage (le même
  dimanche, le même étal pour tout le monde), **120 $** la carte (une carte trouvée par terre en rapporte 25 : on paie
  pour ne pas chercher) ; elle entre dans l'album par `Collections.donner(numero, 'puces')`, **sans** la prime de la
  rue (les paliers, eux, suivent). **Gisèle** et ses meubles : les quatre qui portent `ou: puces` (le juke-box, le
  sofa, le téléviseur, le tapis tressé) à **60 %** du catalogue Beausoleil, livrés le lendemain à la planque de Rocco.
- **Marchander** : chaque article a « ACHETER » et « OFFRIR » (70 % du prix). Le marchand accepte si son **humeur**
  pour cet article cette semaine (un hachage, jamais `B.rng()`) est sous 45 sur 100 ; sinon « 84 $ ? T'ES DRÔLE,
  TOI. » et l'article garde son prix jusqu'au dimanche suivant (`partie.puces = { semaine, refus }`).
- **ACTION** devant une table (dans `Missions.interagir`, après la cabane à sucre) ouvre l'étal ; le marchand y dit
  une de ses trois lignes (une par semaine). **Triche** : TRICHES > ALLER > COLLECTIONS > AU MARCHÉ, DIMANCHE 8 H
  (le jour avance jusqu'au prochain dimanche).
- ⚠️ **Pas de voix, pas de son neuf** : les marchands parlent par écrit. Des voix ElevenLabs demanderaient deux
  personnages de plus au catalogue des voix (et leur place au paquet) ; et on n'y **vend** rien (« peut-être » dans la
  demande) — à trancher par Martin, comme une ambiance de marché (le plafond des sons de lieu a 23 Ko de marge).
- **Le poids** : sur `/api/collections` (17 872 bruts / 6 348 gzip, plafond relevé à 22 000 / 8 000) ; rien dans les
  définitions ni la carte.
- **Captures** (`captures/collections/`) : `puces-terrain.png` (les deux étals un dimanche de janvier),
  `puces-menu.png`, `puces-article.png`.
- **Juges** : `tests/test_puces.py` (cinq) et `tests/test_puces_js.py` (huit : ouvert le dimanche matin seulement,
  le même étal la même semaine et un autre la suivante, marchander sans un dé et le refus qui tient la semaine, la
  carte sans la prime, le meuble le lendemain, ACTION **par le bouton**, le dessin, la triche) ; neuf mutations vues
  rouges — l'écart aux trouvailles ne mordait pas sur la graine livrée (le terrain choisi est déjà loin de tout) :
  un pré synthétique le sépare.
