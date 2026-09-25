# Un char qui coule est détruit

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026) : « pour la mission de détruire le camion devant l'usine, si on le fout dans l'eau ça devrait le détruire. (même hors mission) »

- ⚠️ **Mesuré avant** : `Vehicules.majNoyade` retire de la ville le char qui touche le fond, mais son `etat` reste `stationne` ou `roule`. Or tout ce qui guette un char détruit lit `etat === 'epave'` : `detruire` (q03) ne l'a jamais vu mourir, et le chrono faisait échouer la mission avec le camion au fond de la baie. Même chose pour le char d'une mission qui coule : aucun `vehicule_detruit`, la mission restait prise.
- **La règle, partout** : un char qui coule est une épave, comme un char qui explose — l'état, la vie à zéro, le câble de la remorque qui lâche.
