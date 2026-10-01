# Mme Thérèse Beaulieu

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md)

> « Allô? C'est Thérèse Beaulieu, des Érables. Mon Biscuit s'est sauvé, pis j'ai pus les jambes pour courir après. » — e03

## En bref

| | |
|---|---|
| Slug | `beaulieu` |
| Rôle | la promeneuse des Érables : veuve, soixante-dix ans, trois promenades par jour avec Biscuit, son vieux chien couleur biscuit |
| Où | devant le dépanneur de Ti-Paul (`porte:depanneur`), après m6 (`arrive_apres`) ; Biscuit à ses pieds une fois e03 faite (`chien: e03`) |
| Voix | **Caroline — Soft Quebec accent** (bibliothèque, accent québécois, partagée avec Mado, qu'elle ne croise dans aucune mission) ; choisie à l'audition contre Julia et Grandma Clo (1er oct. 2026) — **à valider par Martin** : `captures/audition-beaulieu-*.mp3` |
| Bulle | « Ouhou! Vous! » |
| Couleurs | gilet mauve tricoté, permanente blanche, pantalon gris |
| Visage | tête ronde, permanente, gilet, lunettes rondes, rides, joues roses, boucles d'oreilles (`visages.py`) |
| Missions | **e03** _Biscuit s'est sauvé_ |

## Son histoire

Thérèse Beaulieu a enterré son Gérard il y a six ans et gardé son chien. Biscuit a treize ans, il dort sur le divan
de Gérard, et il se pense encore un chiot dès qu'il voit un écureuil. Elle fait le tour des Érables trois fois par jour
avec lui, connaît tout le monde par le nom de leur chien, et achète ses biscuits chez Ti-Paul — d'où le nom.

## Sa personnalité

Douce, polie, inquiète pour rien et rassurée pour moins encore. Elle vouvoie tout le monde sauf son chien, qu'elle
appelle « mon bébé » et « mon beau grand fou ». Elle n'a peur de rien sauf de perdre Biscuit.

## Comment elle parle

Elle vouvoie, elle dit « mon bébé », « le vlimeux ». Balises : `[worried]`, `[nervously]` quand Biscuit est loin,
`[relieved]`, `[warmly]`, `[happy]` quand il revient, `[amused]` quand elle parle de lui comme d'un enfant.

## Comment elle salue et se présente

Au téléphone : « C'est Thérèse Beaulieu, des Érables. » — le nom et la rue, comme à la pharmacie.

## Biscuit

Le premier chien du jeu (`sprites.js` : `chien` assis, `chien_bouge` au trot et au galop ; un piéton peint en bête,
`Entites.poseDePietonBete`). Dans e03, il se sauve trois fois avant de se coucher, la langue sortie. Après, il est
assis à ses pieds devant le dépanneur, et à pied, il te suit dans les Érables (`static/js/biscuit.js`).

## À trancher

- La fiche des cent missions la dit « perd son chien, **puis déménage** » : aucune mission ne la fait déménager.
