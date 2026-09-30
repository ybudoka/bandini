# Ti-Rhéal Bergeron

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md) · [le marché aux puces du dimanche](../jalons/le-marche-aux-puces-du-dimanche.md#fiche-de-la-deuxième-vague)

> « Ti-Rhéal Bergeron, trente ans sur la zamboni de l'aréna. Des cartes de hockey, j'en ai vu passer. »

Né avec le marché aux puces (30 sept. 2026, `app/puces.py`), **voix posée par Claude le 30 sept. 2026** à la
deuxième vague (Martin : « des voix aux marchands »). ⚠️ **À valider par Martin** : ce qui suit est une proposition.

## En bref

| | |
|---|---|
| Slug | `ti_rheal` (ses voix : `ti_rheal-puces-<clé>`) — ⚠️ pas dans `missions.PERSONNAGES` : il n'a pas de mission, et rien de lui n'entre dans les définitions |
| Rôle | vend les cartes de hockey de la Ligue au marché aux puces, quatre par semaine, 120 $ la carte |
| Où | derrière sa table à la nappe bleue, sur le terrain vague le plus près de la planque, le dimanche de 6 h à midi |
| Voix | **Christian Page - Narrative and Deep** — québécoise de la bibliothèque (vérifiée « quebec »), choisie à l'audition contre Olivier et Marc André (`captures/puces-voix/`) ; la plus lente et la plus grave des trois : un homme de soixante-dix ans. ⚠️ Martin ne l'a pas encore écoutée |
| Couleurs | chandail rouge des Castors, cheveux blancs |
| Missions | aucune ; son étal |

## Son histoire

Trente ans à conduire la surfaceuse de l'aréna, entre deux périodes, sous l'orgue. Il a vu jouer toute la Ligue
— de dos, surtout, et de loin. À sa retraite, il a descendu de la cave les boîtes de chaussures où il gardait les
cartes que les enfants échappaient dans les estrades, et il les vend le dimanche.

## Sa personnalité

- **Ce qu'il veut** : qu'on l'écoute raconter. La vente vient après.
- **Ce qu'il cache** : que « La Toque », il ne l'a jamais connu (« Il m'a pas connu »).
- **Sa nature** : vantard et attachant — c'est lui qui a tort, jamais le client. Il marchande par principe et cède
  quand on a « une face honnête ».

## Comment il parle

- Lentement, en joual d'aréna, en phrases qui se terminent par une réserve (« Presque. Des fois. »).
- **Ce qu'il ne dit jamais** : un chiffre exact ; du mal d'un joueur.
- **Balises de base** : `[smugly]`, `[knowingly]`, `[warmly]`, `[sarcastic]` quand on offre trop bas.

## Comment il salue et se présente

| Situation | Ce qu'il dit | Pourquoi |
|---|---|---|
| La première fois qu'on s'arrête à son étal | « Ti-Rhéal Bergeron, trente ans sur la zamboni de l'aréna… » (`salut`) | son nom et son titre de gloire, d'une traite — une fois pour toutes (`partie.puces.connus`) |
| Ensuite | sa ligne de la semaine (`accueil-1` à `-3`), ou `rien` si tu as déjà ses quatre cartes | il ne se représente pas |
| On s'en va | « Bon dimanche, là! Garde tes cartes au sec. » | |

## Ce qu'il a dit (le canon)

Toutes ses répliques sont dans `app/puces.py` (`REPLIQUES`), avec leur jeu.
