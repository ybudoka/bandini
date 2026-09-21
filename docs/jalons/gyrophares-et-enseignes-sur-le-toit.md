# Gyrophares et enseignes sur le toit

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « taxi et tous les véhicules qui en ont besoin doivent avoir des
indicateurs ou gyrophare sur leur toit. comme en vrai. »

- ⚠️ **Mesuré** : aucun char n'en avait — la police n'a jamais eu de rampe, et les dessins
  de dos de l'ambulance et de la remorqueuse n'avaient ni gyrophare ni croix (les
  commentaires qui en parlent étaient restés d'un dessin d'avant). **Livré** :
  l'**enseigne** du taxi (`ENSEIGNE_TAXI`, allumée, une ligne sombre en travers pour
  « TAXI ») et la **rampe** de la police (`RAMPE_POLICE`, rouge à gauche, bleue à droite)
  sur la berline en volume, à tous les caps ; une rampe **rouge et blanche** sur le toit de
  cabine de l'ambulance, et une rampe **ambre sur base sombre** pour la remorqueuse (ambre
  sur orange, la première disparaissait).
- ⚠️ **Un gyrophare qui brille tout le temps ne dit plus rien** : les rampes sont
  **éteintes** dans la palette, et la fiche dit QUAND elles tournent (`gyrophares.quand` :
  `sirene` pour la police et l'ambulance, `remorque` pour la remorqueuse) ;
  `Vehicules.swapsDuMoment` les fait battre en alternance aux 7 images — plus vite qu'un feu
  qui clignote, sinon on les lit comme un feu jaune —, avec un objet de couleurs par phase
  gardé sur le char, pas deux neufs par image. 2 juges neufs, **rouge avant prouvé** (rampe
  retirée : « la rampe de la police manque à des caps » ; battement retiré : « ses
  gyrophares ne battent pas ») ; le juge de la livrée admet que le taxi et la police ont
  chacun leur toit. 2192 tests
