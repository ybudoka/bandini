# Rocco Bandini

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md)

> « Ton oncle Rocco est mort le mois passé. Il te laisse son garage, sa planque, pis son nom. » — l'ouverture

## En bref

| | |
|---|---|
| Slug | aucun : **il n'est pas dans `PERSONNAGES`**, et il ne doit pas y entrer tant qu'il est absent |
| Rôle | celui qu'on remplace ; le « Bandini » de ton surnom |
| Où | nulle part — son garage (`garage`, « Garage Rocco Bandini »), sa planque (`planque`), l'Hôtel Bandini |
| Ce qu'il laisse | un garage, une planque, un nom, et **15 000 piastres de dette à Sal le Barbier** (l'ouverture) |

## Son histoire

Rocco Bandini était un petit bandit du Faubourg — pas un parrain : un homme qui connaissait tout le monde et
devait à chacun. Il a ouvert le garage où l'on repeint les chars qu'il ne faut pas reconnaître (le journal :
« Le garage de Rocco »), s'est fait des amis dans la police (Bouchard, « un ami de la famille », m3) et des
ennemis chez les Cravates, qui disent qu'il leur devait de l'argent (f01). Il a emprunté à Sal le Barbier
plus qu'il ne pouvait rendre (l'ouverture).

Puis il a disparu, et c'est toi qu'on a fait venir, en autobus, avec cinquante piastres (l'ouverture). Tout
le monde dans la ville a une version de Rocco : Ti-Guy parle de lui au présent, Marco en parle le moins
possible, Sal compte les jours.

## Ce que chacun dit de lui

| Qui | Ce qu'il dit | Où |
|---|---|---|
| le narrateur | « Ton oncle Rocco est mort le mois passé. » | l'ouverture |
| Ti-Guy | « Le cousin de Rocco! » ; « Rocco est parti se faire oublier. » | m1 |
| Ti-Guy | « T'es ben le cousin de Rocco. » | m1 |
| Marco | « Ils disent que Rocco leur devait de l'argent. » | f01 |
| le journal | « Le garage de Rocco. On y répare, on y repeint… » | `journal.py` |

## Comment on parle de lui

Personne ne dit « feu Rocco » : on dit **Rocco**, tout court, comme s'il allait entrer. C'est la marque
d'un absent qui prend encore de la place. Une mission qui le nomme choisit **qui** en parle, et donc **quelle**
version : celle de Ti-Guy (l'ami, au présent), celle de Marco (le cousin, avec rancune), celle de Sal (le
débiteur, en chiffres).

## Ce qui l'attend (M16)

Il reste le fil : `f08` « Le char de Rocco » (sa berline de luxe au lot), `d01` « Le barbier » (« Rocco me
devait 15 000 »), `d05` (ses papiers dans le coffre de la planque), `d08` (sa bague), `i08` « La cache de
Rocco » (une île), `f04` (ses paquets cachés, selon le Grand Mo). Et **Rosa Di Meo**, la couturière, son
ancienne blonde (M16).

## À trancher

⚠️ **Le jeu se contredit sur Rocco, et c'est la première chose qu'on entend.**

- **Mort ou en fuite ?** L'ouverture : « ton oncle Rocco est **mort** le mois passé ». Ti-Guy, trois minutes
  plus tard (m1) : « Rocco est **parti se faire oublier** ».
- **Oncle ou cousin ?** L'ouverture : « ton **oncle** ». Ti-Guy : « le **cousin** de Rocco », deux fois (m1).

Deux lectures tiennent, et il faut en garder une :

1. **Rocco est mort, tu es son neveu** (l'ouverture a raison). Alors Ti-Guy **ment** ou **n'y arrive pas** :
   « parti se faire oublier » est sa façon de ne pas dire « mort », et « le cousin » est un mot de la famille,
   pas un lien. C'est jouable — à condition de le jouer : un `[quietly]` sur « parti se faire oublier »
   (c'est déjà le cas) et, plus tard, une mission où quelqu'un le lui fait remarquer.
2. **Rocco est en fuite** (Ti-Guy a raison). Alors l'ouverture ment, ou croit ce que la ville croit — et
   les deux fins (M13) gagnent un retour possible de Rocco.

La première ne demande de changer aucun mot ; la seconde, l'ouverture (deux voix du narrateur à régénérer).
C'est à Martin de choisir : c'est son histoire.
