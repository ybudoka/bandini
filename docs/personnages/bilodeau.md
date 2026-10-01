# Roméo Bilodeau

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md)

> « Roméo Bilodeau, du bout de La Pointe. Les jeunes ont fermé le pont, monsieur. Avec des cônes! » — La Pointe, acte 1 (p02)

## En bref

| | |
|---|---|
| Slug | `bilodeau` |
| Rôle | retraité du bout de La Pointe ; ne passe plus le pont qu'avec sa femme, le jeudi, pour le docteur |
| Où | devant le phare (`porte:phare`), après p01 (`arrive_apres`) |
| Voix | **Santa — Gentle and Heartwarming** (bibliothèque, « old », accent québécois) ; choisie à l'audition contre Pascal et Mathieu (Martin, 30 sept. 2026) — Bill, l'américain d'avant, sonnait faux |
| Bulle | « Monsieur! » |
| Couleurs | gilet brun, cheveux blancs, pantalon marine |
| Missions | donne **La Pointe** (le chapitre, 30 sept. 2026 ; son acte 1, le pont, était p02 ; et, plus tard, **p07** : _Le souper dansant_ — l'autobus du club de l'âge d'or jusqu'à l'Hôtel Bandini) |

## Son histoire

Quarante hivers au bout de La Pointe, dans une maison qu'il a bâtie lui-même en face du phare. Il a travaillé au port, il a élevé quatre enfants partis en ville, et il connaît Ovila depuis l'école. Il ne sort plus de La Pointe que le jeudi, pour le docteur de sa femme — par le seul pont.

## Sa personnalité

Poli, un peu vieux jeu, il vouvoie tout le monde et s'emporte contre « la jeunesse » — puis a honte de s'être emporté. Il paie en biscuits.

## Comment il parle

Il vouvoie, il dit « monsieur », il parle de sa femme. Balises : `[gruffly]`, `[annoyed]` quand il s'emporte, `[warmly]` quand il se reprend.

## Comment il salue et se présente

Au téléphone : « Roméo Bilodeau, du bout de La Pointe. » — le nom et l'adresse, comme au bureau de poste.

## À trancher

- Rien pour l'instant.

## Notes

- **30 sept. 2026 — Santa introuvable au compte, puis retrouvée.** `--libres` disait « le jeu nomme des voix que le
  compte n'a pas : Santa - Gentle and Heartwarming ». La voix n'était ni retirée ni absente : ajoutée depuis la
  bibliothèque (`s6w9aeDifUqNIV5QeIBE`), elle était arrivée au compte sous le nom **d'origine** de son autrice,
  « Santa Claus – Gentle & Heartwarming Christmas (Multilingual) » — la bibliothèque, elle, l'affiche « Santa - Gentle
  and Heartwarming » (le nom que l'audition a lu), et `POST /v1/voices/add` ignore `new_name`. Renommée au compte
  (`POST /v1/voices/<id>/edit`, `name=Santa - Gentle and Heartwarming`) : `--libres` et la recherche par nom d'une
  régénération la retrouvent. Rien de refait : les 11 mp3 restent ceux du 30 sept.
