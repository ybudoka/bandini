# Le son de l'eau

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le son de l'eau (**correctif**, taille 1) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « améliore le son de quand on va dans l'eau. »

Il n'y a **rien à améliorer** : il n'y a pas de son d'eau dans le jeu. Ce qu'on entend en
entrant dans la baie, c'est `SFX.choc` — « Tôle froissée », le son d'un **accident de
char** (`app/audio.py` : deux variantes de carrosserie qui se plie). C'est la seule ligne de
son que « L'eau n'est plus un mur » a posée, et elle l'a été faute de mieux.

Le reste est du silence, et c'est pire que le mauvais son :

- **On nage sans rien entendre.** `majJoueur` coupe les pas dans l'eau (« On ne fait pas de
  pas dans l'eau ») et ne met rien à la place : onze tuiles de chenal, 88 points de souffle,
  et pas un bruit.
- **On sort de l'eau sans un bruit** non plus : le drapeau `j.nage` retombe, les remous
  s'arrêtent, rien ne se fait entendre.
- **On coule en silence.** `noyade()` fait seize remous et appelle l'hôpital — le moment le
  plus grave que l'eau peut produire ne s'entend pas.
- **Un char qui coule est muet de bout en bout.** `majNoyade` écrit « IL COULE — SORS » au
  HUD, fait bouillir l'eau autour pendant trois secondes, et on n'entend **rien** : ni la
  plongée, ni les bulles, ni le dernier glouglou. Le HUD dit ce que l'oreille aurait dû dire
  la première.

**Ce qu'on fait.** Trois bruitages ElevenLabs de plus, et le câblage qui manque :

- `plongeon` (2 variantes) — un corps qui entre dans l'eau. Il remplace la tôle froissée à
  l'entrée, **et** sert à la sortie de l'eau, à l'entrée des piétons et des agents
  (`Son.jouerA`, donc plus faible de loin) et au char qui plonge.
- `nage` (3 variantes) — la brassée. Elle se joue **à la distance parcourue**, exactement
  comme `pas` : c'est le même geste et le même besoin. Une boucle tenue sous un nageur
  immobile sonnerait comme une fontaine. ⚠️ Trois variantes et pas une : une brassée revient
  une fois et demie par seconde, c'est là que l'oreille s'agace le plus vite.
- `couler` (1) — la tête qui passe sous l'eau : le glouglou et les bulles. Il joue à la
  noyade du joueur **et** quand le char touche le fond.

⚠️ **Le char n'a pas son propre fichier, et c'est voulu** : c'est la même eau, avec plus de
masse. Il joue `plongeon` **plus un coup de grave synthétisé** — le poids, c'est ce qui
manque à un corps de 80 kg, pas la matière. Un quatrième fichier aurait coûté 20 Ko pour
dire la même chose.

⚠️ **Le budget des bruitages doit monter** (900 → 950 Ko) : c'est un son qu'on n'avait pas,
pas un son qu'on a laissé grossir. On reste sous le mégaoctet, et la finition ne change pas.

- **Juges** : entrer dans l'eau joue le plongeon et **plus jamais la tôle** ; nager fait des
  brassées et **aucun pas** ; à bout de souffle, on entend `couler` ; un char qui entre dans
  l'eau plonge, puis fait du bruit en coulant ; et le filet synthétisé des trois **atteint la
  sortie**, comme pour tous les autres effets.

**Livré le 14 sept. 2026.** Six fichiers (83 Ko), six moments qui ne s'entendaient pas, et un
cul-de-sac trouvé en chemin.

- **Les trois sons sont générés et mesurés.** `plongeon` et `nage` **brillent** (‑10 dB au-dessus
  de 8 kHz : ce qui fait entendre l'eau, ce sont les gouttes — le plongeon entre donc dans le
  juge de l'aigu), et `couler` est **sourd** (‑47 dB), ce qui est le signe que le son est le
  bon : une tête qui passe sous l'eau n'a plus d'aigu. ⚠️ **Martin ne les a pas encore
  écoutés** — c'est la seule chose qu'aucun juge ne remplace ; `--refaire plongeon` est là pour
  ça.
- **Six moments câblés**, et chacun existait déjà sans bruit : on entre (plongeon), on avance
  (brassée à la distance, comme un pas), on sort (une dernière brassée), on coule (`couler`),
  un autre corps entre (`jouerA`, donc plus faible de loin), un char plonge et s'enfonce.
- ⚠️ **Une seule porte pour entrer dans l'eau** (`Entites.mouiller`). `police.js` posait lui
  aussi `a.nage` avant de déplacer son agent : deux endroits qui lisent la même transition, et
  le premier la mange. Tant que la transition se lisait à deux endroits, le son de l'agent
  dépendait de **l'ordre d'appel** — le genre de dépendance qu'on ne voit pas et qui se casse
  au prochain remaniement.
- ⚠️ **LE défaut trouvé en chemin, et il vaut plus que le son** : `v.conducteur === 'joueur'`
  — la chaîne — n'était **jamais vrai**. Partout ailleurs le conducteur est l'**entité**
  (`v.conducteur = j` dans `monter`) ; seul le trafic porte une chaîne. Trois lignes en
  dépendaient, et le silence était la moins grave : « IL COULE — SORS » **ne s'affichait
  jamais**, et surtout le joueur restait `dansVehicule` un char **retiré des entités** —
  mesure du banc : `nage` faux, et **0 px en 60 images de touche**. Couler dans son char était
  un **cul-de-sac**, et personne ne l'avait vu parce que le juge de « L'eau n'est plus un mur »
  poussait un char **vide** à l'eau.
- ⚠️ **Le juge de l'agent se trompait d'une image**, et c'est instructif : la police pose
  `a.nage` **avant** de déplacer son agent, donc l'image où `dansLEau` devient vrai est celle
  où il entre — le plongeon part à la suivante. Un juge qui s'arrête pile à la première mesure
  un silence qui n'existe pas.
- **Ce qui reste ouvert** : le **sable** (`s`) borde l'eau mais ne sonne pas encore comme une
  rive (l'eau basse où l'on entre debout, cf. « L'eau n'est plus un mur ») ; et rien ne dit
  encore, à l'oreille, qu'on **manque de souffle** dans l'eau — c'est le souffle du joueur de
  M15, qui attend ses clips.

## Notes

demande de Martin : « améliore le son de quand on va dans l'eau ». Il n'y avait **rien à
améliorer** : on y entrait sur de la **tôle froissée** (`SFX.choc`, un accident de char), on
nageait dans le **silence complet** — pas même un pas — et un char qui coule était muet de
bout en bout. Trois bruitages neufs (`plongeon` ×2, `nage` ×3, `couler`) et le câblage des
six moments que l'eau produit.

- ⚠️ **Et un cul-de-sac trouvé en chemin** : `v.conducteur === 'joueur'` — la chaîne —
  n'était **jamais vrai**, donc « IL COULE — SORS » ne s'affichait jamais et le joueur
  restait dans un char **retiré des entités**, immobile pour toujours au fond de la baie. 6
  juges neufs
