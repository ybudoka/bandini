# La dépanneuse lève les roues

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « la dépanneuse devrait embarquer les roues avant des véhicules qu'elle
remorque, sauf les motos et vélos qu'elle embarque complètement sur sa plateforme ». C'était
une **corde** : le char roulait à plat au bout d'un élastique, pointé **vers** elle, et le
lien lâchait quand on l'étirait. Maintenant une **fourche** — écart fixe, **dans l'axe**,
avant **levé de deux pixels** (l'ombre restée au sol, sans un seul cap de sprite en plus) —
et un **plateau** pour ce que `vehicules.py` déclare `plateau` (la moto, le vélo) : elles
montent **en entier**, ne heurtent plus rien, et se peignent **après** la remorqueuse.

- ⚠️ La remorqueuse **refuse d'avancer** là où sa charge ne passe pas (sans le garde-fou,
  elle reculait de 22 px dans la façade), et on **ne monte plus** dans un char remorqué. 2
  juges neufs, 2 réécrits
