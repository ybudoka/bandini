# M4 Police

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

`police.js` réécrit : agents à pied (archétype `policier`, patrouille par zone, cône vérifié
une image sur trois, poursuite par **A\*** sur les trottoirs, arrestation au contact,
sortent le joueur d'un char arrêté), **rien n'est compté tant qu'un agent ne l'a pas vu** —
un passant qui a vu devient témoin porteur du crime, court le raconter à un agent ou
téléphone (`temoins`), et on peut **acheter son silence** (20 $) ; délits bruyants
(`temoin: false`) comptés tout de suite ; étoiles qui ne tombent qu'hors de vue (dedans
aussi) ; menu d'arrestation **obligatoire** (pot-de-vin selon casier/étoiles, sergent ami
plus tard, refus = délit) ; prison (amende, armes confisquées, casier, 6 h, réveil au poste,
sauvegarde) ; autos de patrouille à 3★ qui **suivent les rails** vers le joueur (feux
brûlés, sortie vers lui) et foncent de près, agents qui descendent ; tirs à 3★ ; −1★ en
changeant de char hors de vue ; affiches « Recherché » sur les façades à 2★ ; blips bleus,
étoiles qui clignotent ; **mode TRACE** (idée de Martin) : le jeu dessine le trajet de
chaque char et se surveille (chien de garde, tour en rond, hors voie)
