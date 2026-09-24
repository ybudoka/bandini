# L'aéroport — le chantier du pont s'allonge, et l'île se cache sur la carte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandes de Martin (21 sept. 2026), après [l'aéroport](l-aeroport.md) :_ « ajoute 4 sections de plus de
pont en construction », puis « la carte de l'aéroport peut elle etre masqué jusqu'à… » — précisé par ses
réponses : le **chantier plus long**, et **l'île entière cachée** sur la carte **jusqu'au pont fini** (`a01`).

- ⚠️ **Six piles au lieu de deux**, toujours une toutes les cinq tuiles : la travée manquante passe de
  12 à 32 tuiles d'eau, le tablier fini de La Pointe de 24 à 12, le bout côté île de 16 à 8 (le détroit
  ne bouge pas : 52 tuiles). Conséquences voulues : le trou ne se nage plus qu'avec le café ET l'estomac
  plein, et aucune moto ne le saute plus (32 tuiles, contre 13 de réception lancée).
- ⚠️ **L'île cachée sur la carte** — mini-carte et grande carte (touche N) : de l'eau à la place de l'île
  et du bout du pont côté île, pas de repère de l'aérogare, tant que `a01` n'est pas faite. Python dit
  quoi cacher et jusqu'à quand (le rectangle et la mission, dans la fiche de l'aéroport) ; le navigateur
  refait la mini-carte le jour où le pont se finit.
- ⚠️ Rien de neuf ne naît au chargement (ni décor, ni porte) : la leçon de [l'aéroport](l-aeroport.md#notes).

## Notes

**Livré le 21 sept. 2026** — `app/aeroport.py` (`PONT`, `MASQUE`), `static/js/monde.js` (`masquee`,
`couleurMiniA`, `hauteurConnue`), `static/js/hud.js` (`lieuxSurLaCarte`).

- ⚠️ **Le chantier** : 12 rangées de tablier fini depuis La Pointe, **32 d'eau** avec six piles aux
  rangées 3, 8, 13, 18, 23 et 28 du trou, 8 rangées côté île jusqu'à la guérite. Rien d'autre ne bouge
  dans la ville (le tablier est plus court : quatre colonnes redeviennent de l'eau). Le juge du trou a
  changé de promesse avec lui : il ne se nage plus qu'au café ET à l'estomac plein (120 points pour
  160), et aucune moto ne le saute (32 tuiles contre 13 de réception) — la « porte laissée au saut »
  de la première livraison est fermée, c'est le prix du chantier plus long.
- ⚠️ **L'île cachée sur la carte** jusqu'à `a01`, la mission qui finit le pont (la même que la
  barricade) : sur la mini-carte et la grande carte, le rectangle de la terre de l'aéroport (bout du pont
  compris) se peint en eau, et l'aérogare n'a ni repère ni place dans la légende. Le tablier côté La
  Pointe, lui, se voit : il est de ce côté-ci. La mini-carte garde la clé du masque avec lequel elle a été
  cuite, et se recuit le jour où il tombe.
- ⚠️ **La grande carte retrouve l'échelle d'avant** tant que l'île est cachée : elle s'arrête à la
  carte connue (`masque.carte_h`, 224 rangées) — sous elle, hors de l'île, il n'y a que de l'eau
  (`test_la_carte_cache_l_ile_jusqu_au_pont_fini`). Sauf si le joueur est lui-même plus bas : on ne le
  perd pas de la carte. Le pont fini, elle reprend la carte entière.
- ⚠️ Ce qui ne se cache pas : le carnet liste toujours « FERMÉ — LA GUÉRITE DE L'AÉROPORT » (le pont
  porte le nom de l'aéroport de toute façon), et le nom de la zone s'affiche si l'on se tient sur l'île.
