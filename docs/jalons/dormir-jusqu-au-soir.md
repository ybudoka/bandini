# Dormir jusqu'au soir

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « ajoute un mécanisme pour passer de jour à nuit ».

- ⚠️ **Mesuré avant** : le lit ne mène qu'au MATIN (7 h 12), et `estNuit()` ne s'allume qu'à
  **19 h 52** — une mission `nuit` prise au réveil faisait donc **attendre 4 min 15
  réelles** sous « ATTENDS LA NUIT », sans rien à faire. Le lit (la planque, la chambre de
  l'Hôtel Bandini) propose **DORMIR JUSQU'AU SOIR** tant qu'il fait jour dehors : fondu au
  noir, réveil à **20 h 45** (lampadaires allumés, feux déjà au clignotant), endurance
  pleine, **25 % de la vie** (choix de Martin : une sieste n'est pas une nuit), étoiles
  effacées et partie sauvée comme au sommeil.
- ⚠️ Offerte seulement le jour, elle ne passe **jamais minuit** : aucun `nouveauJour()`,
  donc ni dette, ni revenus, ni skimmers de plus. Les réglages sont `economie.SIESTE`
  (`reveil` 0,865, `soin` 0,25) ; la nuit et la sieste partagent `seReveiller`, et
  `Monde.estNuit(heure)` répond pour DEHORS même depuis une pièce (sans argument, un
  intérieur n'est jamais de nuit — le lit posait la mauvaise question).
- ⚠️ Un juge mesure la nuit **minute par minute sur la table des teintes** : le réveil doit
  tomber après le clignotant et laisser au moins 85 % de la nuit. 4 juges de banc
  (`test_sieste_js.py`).
