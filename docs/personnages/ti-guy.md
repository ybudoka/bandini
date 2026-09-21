# Ti-Guy Lelièvre

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md)

> « Heille, le neveu de Rocco! C'est moi, Ti-Guy, tu me replaces pas? T'as fait bon voyage? » — m1

## En bref

| | |
|---|---|
| Slug | `ti_guy` |
| Rôle | le receleur du garage (la vision), le chum de Rocco ; le premier visage de la ville |
| Où | devant le terminus d'autobus (`porte:terminus`) ; après m1, il entre au garage et n'en ressort plus (`parti_apres: "m1"`) |
| Voix | **Felix Tabarnak — Confident and Witty**, québécoise d'origine |
| Bulle | « Hé! Le neveu! » |
| Couleurs | chandail vert forêt, cheveux bruns foncés, pantalon ardoise |
| Missions | donne **m1** ; parle au combiné dans **m4** (il te suit en char pour faire diversion) |

## Son histoire

Ti-Guy a grandi dans le Faubourg, trois portes plus loin que Rocco, et il l'a suivi partout depuis la petite
école — un pas derrière, en riant plus fort que lui. Quand Rocco a ouvert le garage, Ti-Guy s'est installé
dans le bureau du fond : c'est lui qui rachète les chars qu'on gare devant la porte, sans demander d'où ils
viennent. Il ne s'est jamais pris pour un bandit ; il se voit en commerçant qui rend service.

C'est lui qui attend le car au terminus le jour où tu arrives (m1), parce que Rocco le lui a demandé. Il te
dit que « Rocco est parti se faire oublier » et que « le garage, c'est toi qui le tiens, astheure » (m1). Il
te met à l'épreuve avec un char qui traîne dans une ruelle, puis te donne la clé de la planque (m1). Ensuite,
il retourne dans son bureau du garage : il a trouvé qui le remplace dehors. On l'entend encore — il te suit
en char pour faire diversion quand tu voles l'auto-patrouille de Bouchard (m4) — mais on ne le voit plus
dans la rue.

## Sa personnalité

- **Ce qu'il veut** : que le garage continue, et qu'on dise de lui qu'il a bien accueilli le petit de Rocco.
- **Ce qu'il cache** : il a peur. Rocco parti, Ti-Guy n'a plus personne derrière qui marcher, et il te
  pousse devant lui avec un grand sourire. Sa bonne humeur est un bruit qu'il fait pour ne pas y penser.
- **Ce qui le fait craquer** : qu'on ne le reconnaisse pas. Il croit que toute la ville le connaît — et il a
  à moitié raison.
- **Son défaut** : il parle trop vite, promet trop tôt (« Personne va s'en ennuyer », m1).

## Comment il parle

- **Familier, fort, content.** Il tutoie tout le monde, le sergent compris. « Heille! », « astheure »,
  « j'm'occupe des bœufs » (m4) — la police, dans sa bouche, c'est « les bœufs ».
- **Il rit de ses propres phrases.** Le `[laughs]` lui va, et lui seul le porte sans que ça sonne faux.
- **Il se trompe de ton quand ça va mal** : il essaie encore d'être drôle (« On va dire que c'était un
  essai », m1).
- **Balises de base** : `[excited]`, `[warmly]`, `[mischievously]`, `[amused]` ; `[laughs]` pour le corps. Pour
  l'échec, `[disappointed]` + `[sighs]` : sa gaieté qui retombe.
- **Ce qu'il ne dit jamais** : « bonjour », « monsieur », une phrase sans point d'exclamation quand il est
  content.

## Comment il salue et se présente

| Situation | Ce qu'il dit | Pourquoi |
|---|---|---|
| À la première rencontre | « C'est moi, Ti-Guy, tu me replaces pas? » (m1) | il **croit qu'on le connaît** : c'est drôle, et c'est tout lui |
| Au téléphone, sa première réplique de la mission | « C'est Ti-Guy, j'suis juste derrière toi. » (m4) | fier d'appeler, comme s'il faisait une surprise |
| Plus tard dans la mission (au combiné, à l'échec) | « Beau char! » (m1), « Ouain… On va dire que c'était un essai. » (m1) | ⚠️ pas de nom : il s'est présenté au terminus (une fois par mission) — sa gaieté, ou sa gaieté qui retombe, suffit |
| Déjà connu, en personne | « Heille, le neveu! » (sa bulle : « Hé! Le neveu! ») | il ne se nomme plus : pour lui, on est de la famille |

## Son corps

`montrer` (il désigne le garage, m1), `donner` (la clé de la planque, m1). À la fin de m1, il **sort** du
garage et **marche** jusqu'à toi avant de parler — l'effort de venir, c'est sa façon de dire merci
(`docs/jeu-d-acteur.md` § 4.4). Jamais les bras croisés : il n'attend rien de personne.

## Ses liens

- **Rocco** — son chum d'enfance, son patron, son grand frère d'adoption. Il en parle au présent.
- **Le joueur** — « le neveu de Rocco » : il le couve, et il compte sur lui.
- **Bouchard** — il le connaît assez pour le suivre dans un coup (m4), pas assez pour lui faire confiance.
- **Marco** — deux hommes de Rocco qui se disputent en silence qui était le plus proche de lui.

## Ce qu'il a dit (le canon)

- m1 : le joueur est « le neveu de Rocco » ; « Rocco est parti se faire oublier » ; le garage est à toi ;
  un char dort dans une ruelle ; la clé de la planque.
- m4 : « C'est Ti-Guy, j'suis juste derrière toi. Roule, j'm'occupe des bœufs. »

## Ce qui l'attend (M16)

`f08` — la berline de luxe de Rocco est au lot ; `d06` — les hommes de Sal s'en prennent au garage ; `i08` —
les papiers du coffre parlent d'une île. Trois missions qui le ramènent au garage, là où il se tient
maintenant : il faudra lui donner un `ou` au garage et lever son `parti_apres`, ou le faire parler au combiné.

## Tranché

- ✅ **« Le neveu de Rocco »** (Martin, 21 sept. 2026 : « l'oncle Rocco ») : Ti-Guy disait « le cousin »,
  l'ouverture « ton oncle » — c'est l'ouverture qui a raison. Deux répliques de m1 et sa bulle corrigées.
  « Rocco est parti se faire oublier » reste : c'est sa façon de ne pas dire « mort » (voir
  [rocco.md](rocco.md)).
