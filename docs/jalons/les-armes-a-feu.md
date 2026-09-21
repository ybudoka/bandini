# Les armes à feu

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les armes à feu (**ajout**, taille 2) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « je veux des armes à feu. »

Il y en a **deux** aujourd'hui, et c'est ça le problème : le **pistolet** (250 $, chargeur
de 12, 30 points) et le **fusil à pompe** (600 $, 8 cartouches, 6 plombs). Sur dix armes au
catalogue, huit sont de la mêlée, du ramassé par terre ou une fronde. Il ne manque pas _une_
arme à feu — il manque une **raison de choisir** entre elles. Trois de plus, et chacune
répond à une question que les deux autres ne savent pas régler :

- **La mitraillette** — _« ils sont trois. »_ Automatique : on tient le bouton, la cadence
  est haute, les dégâts par balle bas, et la dispersion **monte tant qu'on tient**. On arrose
  ou on tire par rafales courtes ; c'est le choix qui fait l'arme. ⚠️ Le moteur ne sait pas
  tirer en automatique : une arme tire un coup par pression, `cadence` images plus tard. Le
  champ `auto` est du travail neuf, et il touche au tactile — au téléphone, « tenir » est un
  geste, pas un clic.
- **La carabine** — _« il est loin. »_ Longue portée, lente, précise, un passant d'une balle.
  ⚠️ **Plafonnée à la largeur de l'écran** : la vue fait 480 px de large, soit 30 tuiles.
  Une portée qui dépasse ça, c'est tirer sur ce qu'on ne voit pas — et le pistolet est déjà
  à 180 px, onze tuiles. La carabine s'arrête à ce que l'écran montre, et c'est une borne,
  pas un réglage.
- **Le cocktail Molotov** — _« ils sont groupés, et je veux que ça dure. »_ Il se lance **en
  cloche**, comme la fronde (le seul projectile qui a déjà un `z` et une gravité), et il
  laisse une **flaque de feu** qui brûle quelques secondes — le feu existe déjà, c'est celui
  des chars sous 20 % de PV, avec ses dégâts par seconde. Deux mécaniques déjà écrites, une
  arme neuve.

Ce qu'il faut décider en même temps, sinon l'ajout se retourne contre le jeu :

- ⚠️ **Une arme à feu change le jeu de police, pas seulement le combat.** La taxonomie est
  déjà là : sortir une arme près d'un policier +1★, tirer sur un policier +2★, le tuer +3★.
  Chaque nouvelle arme déclare donc son `etoiles_usage` — et **une arme bruyante réveille le
  quartier** : une rafale s'entend comme une explosion s'entend (l'alarme de rayon existe
  déjà), même quand personne ne t'a vu.
- ⚠️ **La même parade que pour le char rapide.** Une carabine qui descend les policiers hors
  de leur cône rendrait le 5★ gratuit. La parade est celle qu'on a déjà écrite pour la
  vitesse : le cône n'est pas le seul sens. **Un coup de feu s'entend** — tirer de loin
  t'évite d'être _vu_, jamais d'être _cherché_. La distance achète du temps, pas
  l'impunité.
- ⚠️ **Les munitions font l'équilibre, pas les dégâts.** Une mitraillette qui vide trente
  balles en deux secondes est inutile ou infinie selon le prix du chargeur, et rien entre les
  deux. `prix_munitions` porte tout le poids.
- **Où on les achète** : pas chez Gus. Le **marché noir** existe depuis M7, en arrière du
  bar — c'est là que se vend ce qui fait du bruit, et ça donne enfin à ce comptoir autre
  chose à offrir qu'à M10.
- **Juges** : les prix montent toujours dans l'ordre du catalogue (le test existe) ; aucune
  portée ne dépasse la largeur de la vue ; une arme automatique consomme bien une balle par
  coup et s'arrête chargeur vide ; le feu d'un Molotov s'éteint, ne se propage pas à
  l'infini, et compte comme une mort **causée par le joueur** (sinon on tue sans étoiles) ;
  et un policier abattu laisse tomber son arme — ça marche déjà, ça doit continuer.

**Livré le 14 sept. 2026.** Les trois armes, le comptoir, l'ouïe — et cinq choses apprises
en chemin.

- **Trois champs de fiche, pas trois cas dans le JS** : `auto`, `bruit` (tuiles) et `feu_s`
  (secondes), plus `dispersion_max`. Le pistolet et le fusil ont reçu leur `bruit` du même
  coup (14 et 18 tuiles) : ils détonaient déjà, personne ne les entendait. Ce qui n'est pas
  propre à une arme (`rafale_images`, le rayon et la morsure de l'incendie) voyage dans
  `armes_regles`.
- **L'automatique ne demande rien de neuf à l'entrée.** `frapper` refuse déjà tant que la
  cadence court : tenir le bouton et rappeler `frapper` à chaque image suffit, **c'est la
  cadence qui rythme la rafale** — et le tactile suit sans un geste de plus, puisque le bouton
  FRAPPE tenu se lit déjà comme « bas ». ⚠️ **À vide, la gâchette tenue ne clique qu'à la
  pression** : sans ce garde, un chargeur vide cliquait soixante fois par seconde.
- **L'ouïe, c'est `alerterAgent` sans le cône.** `Police.entendre(x, y, rayon)` envoie en
  enquête chaque agent dans le rayon, **sans étoile** — il n'a rien vu — et, si tu es déjà
  recherché, déplace `dernierVu` sur le coup. Mesuré au banc : un agent qui te tourne le dos à
  douze tuiles vient voir la carabine, celui à trente reste, et la fronde ne s'entend pas.
- ⚠️ **Le type `feu` était pris — c'est le feu de circulation.** La flaque s'appelle donc
  `brasier` : une entité `dessine: false` qui n'existe que par ses particules (des flammes à
  chaque deuxième image, de la fumée) et mord toutes les vingt images un tiers des dégâts de la
  seconde — passants, joueur, chars (`Vehicules.endommager`, le lanceur pour agresseur : un
  char qui en explose, c'est **son** explosion). Sur l'eau, un remous et rien d'autre.
- ⚠️ **`Entites.blesser` pousse la victime loin de la SOURCE**, par défaut : dans le feu, la
  source est le lanceur, et le passant aurait été poussé loin du joueur — donc parfois plus
  au fond du feu. Le brasier passe son propre angle : il pousse **dehors**.
- **La bouteille s'entend quand elle casse**, pas quand elle part : `tirer` se tait pour une
  arme à `feu_s`, et `allumer` joue le son. Le juge compte zéro au lancer, un à l'arrivée.
- ⚠️ **Le script de génération audio tombait sur `duree_s: 0.4`** sans rien expliquer : le
  serveur MCP a un plancher de 0,5 s et répond alors par une erreur qui n'est pas du JSON. Le
  catalogue dit 0,5 maintenant, et la note est dans `audio.py`. Quatre fichiers (45 Ko) ont
  fait déborder le budget des bruitages de 700 octets : relevé à 900 Ko, encore un son qu'on
  n'avait pas.
- **Ce qui n'a pas bougé, et c'est voulu** : les agents gardent leur pistolet à tous les
  paliers (donner la mitraillette au 4★ est une décision de M11, pas de cette fiche) ; et le
  sprite en main est celui de l'objet par terre, comme pour les autres — le chargeur qui
  pend, la crosse de bois, le chiffon allumé, c'est ce qui les nomme à seize pixels.
- **Juges (7 neufs)** : côté Python, trois questions distinctes (une seule `auto`, la plus
  longue portée sans dispersion, le seul `feu_s` en cloche), aucune portée au-delà de la
  demi-vue **lue dans `base.js`**, tout ce qui détone déclare un `bruit` et se vend chez Josée
  sans vitrine chez Gus, et les règles voyagent ; au banc, la mitraillette tenue 90 images
  tire exactement ses huit balles, s'ouvre à `dispersion_max` et se referme quand on lâche ;
  la carabine s'entend à douze tuiles dans le dos d'un agent, sans étoile ; le Molotov
  n'allume qu'un brasier, tue celui qui y reste avant qu'il s'éteigne, le signale comme une
  mort du joueur, et s'éteint.

## Notes

demande de Martin : il n'y en avait que **deux** (pistolet, fusil à pompe) sur dix armes.
Trois de plus, chacune pour une question : la **mitraillette** (automatique — on tient, la
cadence rythme la rafale, la dispersion s'ouvre en 45 images et se referme quand on lâche),
la **carabine** (230 px, un passant d'une balle, bornée par un juge à la demi-vue lue dans
`base.js`) et le **cocktail Molotov** (en cloche, et un **brasier** de 5 s là où il casse —
une entité invisible qui crache des particules, jamais une tuile repeinte). **Un coup de feu
s'entend** : `Police.entendre`, rayon `bruit` de la fiche, l'agent hors du cône vient voir
sans étoile. Vendues au marché noir seulement, munitions comprises. 4 juges Python + 3 au
banc
