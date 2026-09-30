# Gisèle Lachapelle

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md) · [le marché aux puces du dimanche](../jalons/le-marche-aux-puces-du-dimanche.md#fiche-de-la-deuxième-vague)

> « Gisèle Lachapelle, brocanteuse. Regarde avec tes yeux, pis touche avec ton argent. »

Née avec le marché aux puces (30 sept. 2026, `app/puces.py`), **voix et nom de famille posés par Claude le
30 sept. 2026** à la deuxième vague (Martin : « des voix aux marchands »). ⚠️ **À valider par Martin** : ce qui suit
est une proposition. (Pas « Pelletier » : Josée et Lulu le portent déjà ; pas « Beaulieu » : la promeneuse d'e03.)

## En bref

| | |
|---|---|
| Slug | `gisele` (ses voix : `gisele-puces-<clé>`) — ⚠️ pas dans `missions.PERSONNAGES` : elle n'a pas de mission, et rien d'elle n'entre dans les définitions |
| Rôle | vend les meubles marqués `ou: puces` à 60 % du catalogue, livrés le lendemain ; **rachète** les meubles de la planque, bas |
| Où | derrière sa table à la nappe brune, à côté de Ti-Rhéal, le dimanche de 6 h à midi |
| Voix | **Kasandra - Natural Quebecer UGC ad** — québécoise de la bibliothèque (vérifiée « quebec »), libre, choisie à l'audition contre Caroline (déjà Mado) et Loulou (française) (`captures/puces-voix/`) : naturelle, spontanée, une vendeuse. ⚠️ Martin ne l'a pas encore écoutée |
| Couleurs | chandail vert, cheveux roux |
| Missions | aucune ; son étal |

## Son histoire

Trente ans de ventes de garage, de successions et de sous-sols vidés. Elle jure que tout a appartenu à un curé,
parce qu'un meuble de curé se vend mieux. Son beau-frère a un pick-up, et c'est tout ce qu'on saura de lui.

## Sa personnalité

- **Ce qu'elle veut** : acheter bas, vendre moins bas, et avoir le dernier mot.
- **Ce qu'elle cache** : qu'elle revend au double ce qu'on lui vend le dimanche.
- **Sa nature** : gouailleuse, rapide, jamais méchante ; elle flatte quand elle cède (« t'as de beaux yeux »), elle
  se moque quand on exagère (« pas la Caisse populaire »).

## Comment elle parle

- Vite, net, en répliques de comptoir ; le joual du marché.
- **Ce qu'elle ne dit jamais** : un prix rond sans le discuter ; le nom du beau-frère.
- **Balises de base** : `[confident]`, `[deadpan]`, `[playfully]`, `[wryly]`, `[firmly]`.

## Comment elle salue et se présente

| Situation | Ce qu'elle dit | Pourquoi |
|---|---|---|
| La première fois qu'on s'arrête à son étal | « Gisèle Lachapelle, brocanteuse. Regarde avec tes yeux, pis touche avec ton argent. » (`salut`) | le nom, le métier et la règle de la maison — une fois pour toutes (`partie.puces.connus`) |
| Ensuite | sa ligne de la semaine (`accueil-1` à `-3`), ou `rien` si toute sa table est déjà chez toi | elle ne se représente pas |
| On lui vend un meuble | « Un meuble à vendre? Je paie comptant, mais je paie pas cher. » (`rachat`) | |
| On s'en va | « Bonne semaine! Pis dis pas au curé où t'as eu ça. » | |

## Ce qu'elle a dit (le canon)

Toutes ses répliques sont dans `app/puces.py` (`REPLIQUES`), avec leur jeu.
