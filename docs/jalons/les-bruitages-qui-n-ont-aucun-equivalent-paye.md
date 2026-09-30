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

## Notes

_Martin, 30 sept. 2026 : on les génère. Deux vagues : les quatorze sons synthétisés d'abord, les gestes muets
ensuite._

### Vague 1 — les quatorze sons synthétisés — **livrée le 30 sept. 2026**

- **Quatorze échantillons ElevenLabs** (`app/audio.py`, après la borne de la canicule) : la cloche du marteau de
  force, le sifflet du petit train, le feu d'un bâtiment (une BOUCLE) et l'eau sur la braise, la borne qui saute et
  son jet (une BOUCLE — pas celle de la canicule : deux gestes qui tiendraient la même boucle à deux volumes se la
  voleraient), le rideau du garage, la distributrice, la machine secouée et la monnaie, le nid-de-poule, la benne
  poussée, le tas de terre et la plaque d'acier. **424 crédits** (67 794 restants au 30 sept.) ; 284 Ko.
- ⚠️ **Le premier écran est plein** : chacun vit dans un LIEU (`audio.LIEUX` : `foire`, `incendie`, `borne`,
  `garage`, `distributrice`, `chaussee`). Ces sons n'ont pas d'endroit dont on approche : le PREMIER geste demande
  son lieu et joue sa synthèse (`Son.jouerDuLieu`, `tenirDuLieu` pour les deux boucles, et `SFX.chantier` pour
  les trois sons de chaussée — il demande son lieu avant même que l'audio soit prêt) ; les suivants ont le fichier.
  La synthèse reste le filet.
- **Le plafond des lieux** (`test_audio.py`) passe de 1,35 à **1,8 Mo, sur décision de Martin** : il ne borne que
  le dépôt (ces sons ne se chargent jamais au premier écran), et la marge sert aussi aux chocs et aux pas.
- **Regardés sans être écoutés** (je ne peux pas écouter) : la finition du script (gain, rapport signal/bruit de
  39 à 66 dB) et l'enveloppe — la plaque claque deux fois à 0,2 s d'écart (les roues avant, puis arrière), la
  cloche frappe une fois et s'éteint, le nid-de-poule est un coup sec. Le sifflet du petit train est UN long coup,
  pas deux courts. **À écouter par Martin** ; `--refaire <slug>` pour en reprendre un.
- **Juges** : `test_bruitages_js.py` (chacun a son fichier et UN lieu, les deux boucles sont des boucles ; le
  premier geste de chacun demande son lieu — témoins : un son tenu à force nulle ne demande rien, un son du
  premier écran non plus). Quatre mutations rouges.
- **Reste, vague 2** : les gestes encore muets — l'impact d'une balle sur un mur, un goéland qui s'envole, la grue
  qui pivote, monter dans un manège et en descendre, le départ et les tours d'une course, un char qui prend feu.
