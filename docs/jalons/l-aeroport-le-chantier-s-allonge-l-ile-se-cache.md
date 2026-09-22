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
