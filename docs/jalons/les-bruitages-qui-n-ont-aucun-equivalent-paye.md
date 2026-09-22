# Générer les bruitages qui n'ont aucun équivalent payé

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

La suite de [« Des bruitages déjà payés »](des-bruitages-deja-payes-la-ou-le-jeu-n-avait-que-des-oscillateurs.md#notes) :
ce qu'aucun des 74 échantillons ne sait dire, à générer quand le quota ElevenLabs revient (17 oct. 2026)
— **à trancher par Martin**, ça coûte des crédits et ça grossit le seau des bruitages.

- **Sons synthétisés sans équivalent** : la cloche du marteau de force (`cloche`), le crépitement
  d'un feu de bâtiment (`rumeur_incendie`) et l'eau sur la braise (`eau`), la borne qui saute et
  son jet (`borne_cassee`, `borne_jet`), le rideau du garage (`rideau_garage`), la distributrice
  (`distributrice`, `machine_brassee`, `monnaie`), le nid-de-poule (`nid_de_poule`), le sifflet
  du petit train (`sifflet_train`), et la benne poussée, le tas de terre, la plaque d'acier
  (`conteneur`, `tas`, `plaque`). Le bip de recul reste synthétisé : le modèle ne fait pas de
  silence entre les bips.
- **Gestes encore muets** : l'impact d'une balle sur un mur, un goéland qui s'envole, la grue
  qui pivote, monter dans un manège et en descendre, le départ et les tours d'une course, un
  char qui prend feu.

Recette : une entrée `_e(...)` dans `app/audio.py`, `--refaire <slug>` ; le SFX de `son.js`
gagne son `joue(slug)` devant son filet. Vérifier le budget de démarrage (`test_audio.py`).
