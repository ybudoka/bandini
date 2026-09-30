# Des missions sur place — deuxième vague

← [le plan](../plan.md) · [les jalons livrés](README.md) · la première vague :
[des missions sur place, avec une frontière](des-missions-sur-place-avec-une-frontiere.md)

## Notes

✅ **Livré** (30 sept. 2026).

- **v02, v03, p05** branchées ; **e07** non (son vol de clé se joue en ville). La frontière **tombe au
  premier `retourner`** (`SurPlace.tient`) : v03 est gardée dans la villa jusqu'au retour chez Sven, et ni
  compte ni gris ne survivent à cette étape. Le chemin de sortie de la villa passe au rayon 6 dans v02 et
  v03 (le juge de la bande est les joue toutes les trois).
- ⚠️ **Le paquet a débordé** : les six clés de la première vague et de celle-ci l'ont passé de 18 octets gzip
  (59 018 pour un plafond de 59 000). `sur_place` et `frontiere` rejoignent `HORS_DU_PAQUET` : elles arrivent
  avec le texte de la mission (`/api/mission/<slug>`, `pour_jouer`), posées par `Histoire.charger` — et par
  le banc, qui précharge comme lui (`tests/banc.js`).
- ⚠️ **Un juge générique** : `test_chaque_mission_sur_place_se_joue_sur_place` joue chaque mission du
  catalogue qui a `sur_place`, par le vrai chemin de l'intro ET le vrai téléchargement de son texte
  (`poser_les_missions=False`) — la prochaine mission branchée est jugée d'office. Retirer la ligne de
  `charger` le fait rougir.

## Fiche

Demande de Martin (30 sept. 2026) : brancher d'autres missions sur `sur_place` et `frontiere`.

- **v02** « Le dossier du sergent » : de nuit au chemin de la villa, gardée dans la villa (`bloc:villa`).
- **p05** « Les collets du Trappeur » : de nuit au phare, gardée à la Pointe (le phare, les Skateux et le
  Trappeur y sont tous).
- **v03** « La chambre forte » : de nuit au chemin de la villa, gardée dans la villa **jusqu'au retour** —
  tranché par Martin : **la frontière tombe au premier objectif `retourner`** (rapporter le butin au
  donneur se fait forcément ailleurs). Règle générale, sans clé de plus.
- **e07** reste comme avant : son vol de clé (le chauffeur, à 6 h) se joue en ville, avant la villa.
- ⚠️ Le chemin de sortie de la villa (« RESSORS PAR LE CHEMIN ») passe au **rayon 6** dans v02 et v03,
  comme v01 : sinon la bande d'herbe à l'est mène dehors sans le valider, et la frontière fait rater.
- ⚠️ Juges : un juge **générique** — chaque mission du catalogue qui a `sur_place` se joue sur place
  (l'heure, le lieu, dedans sa frontière) — pour que la prochaine mission branchée soit jugée d'office ;
  le chemin de sortie par la bande est pour v01, v02 et v03 ; la frontière levée au `retourner` ; le juge
  « lieu dans la frontière » ne juge que les objectifs d'avant le premier `retourner`.
