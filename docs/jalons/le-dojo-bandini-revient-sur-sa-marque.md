# Le dojo : Bandini revient sur sa marque

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « coup de pied sauté est trop difficile ». Mesuré au banc : depuis sa marque, le coup
réussit dans une large plage (partir pendant le « deux » ou sur le « et », frapper de 12 à plus de 30 images
après). Mais après un essai, seul Kevin revient sur sa marque : Bandini reste où sa course l'a mené, 32 px
DERRIÈRE Kevin, dos à lui, sans élan — tous les essais suivants ratent, jusqu'au cinquième.

- **Au début de chaque « un »**, Bandini revient sur sa marque, face à Kevin — sauf en plein geste (un coup,
  une prise, une roulade). Pour toutes les leçons ; le coup de pied sauté est celui qui traverse le tatami.
- Ni la distance, ni la portée, ni la fenêtre ne changent.
- **Juge au banc** : trois essais de suite joués comme un joueur (courir sur le « et », frapper) apprennent
  le coup ; il rougit avant. Mutation, et une capture.

## Notes

**Livré le 29 sept. 2026.**

- **La marque de Bandini** (`B.cours.marque`, posée dans `Dojo.commencer`) : au début de chaque « un »,
  `Dojo.maj` l'y ramène, face à Kevin — sauf en plein geste (`occupe`) ou quand un geste attend son verdict
  (`c.attend`).
- **Ce qui le faisait dépasser Kevin** : parti dès le « deux », Bandini arrive sur Kevin avant le « et » ;
  Kevin reprend sa marque LÀ où Bandini se tient, et `Entites.demeler` les sépare de travers — Bandini
  derrière, dos à lui.
- **Juges** : `test_le_coup_de_pied_saute_s_apprend_essai_apres_essai` (un premier essai parti trop tôt, puis
  trois essais de joueur), `test_bandini_revient_sur_sa_marque_face_a_kevin` ; la mutation fait rougir les
  deux. ⚠️ Le juge au bouton du coup de pied sauté (`GESTES`) courait 9 images, 23 px sur 70 : il frappait
  de trop loin et n'était vert que PAR le défaut (Bandini restait collé à Kevin après le premier essai). Il
  court maintenant 16 images, jusqu'à Kevin.
