# La ligne d'histoire : une ouverture et un générique

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : La ligne d'histoire : une ouverture et un générique (**ajout**, taille 3)_

_Demande de Martin (16 sept. 2026) :_ « il faut qu'il y ait une ligne d'histoire qui
commence par une introduction audio et visuel au lancement du jeu... aussi une animation
audio visuel à la fin. »

_Ce que ça donne :_ on **sait qui on est** avant de faire un pas, et la partie **se termine**
au lieu de s'arrêter. L'histoire est déjà écrite partout dans le dépôt — l'oncle Rocco mort,
le garage dont on hérite, les 15 000 $ de Sal « Le Barbier » ; ce qui manque, ce sont ses
**deux bouts**, et le même narrateur aux deux.

⚠️ **Mesuré le 16 sept. 2026, et c'est ce qui découpe les deux vagues.**

- **Le lancement ne raconte rien.** Le titre est un voile HTML (`templates/index.html`,
  `voile-titre`) : un `<h1>Bandini</h1>`, la tagline du site, deux boutons et la liste des
  touches. Derrière, le canvas dessine **déjà** la ville figée au terminus — `rendre()`
  tourne dès le chargement, caméra centrée sur l'apparition — mais elle est **vide** : les
  entités ne naissent qu'à `Jeu.commencer()`. Celui-ci pose le bonhomme devant la porte,
  coupe le thème du menu et écrit `BAIE-DES-BRUMES` pendant 150 images. **C'est tout ce que
  le jeu dit de sa prémisse.**
- **La prémisse existe pourtant à trois endroits, et aucun n'est le jeu** : ce plan
  (« Prémisse »), `economie.DETTE` (15 000 $, 2 % par nuit, plafond à une fois et demie) et
  une réplique de Ti-Guy (`missions.py`, m1 : « Heille! Le cousin de Rocco! T'as fait bon
  voyage? ») qu'il faut **aller chercher** à la porte du terminus, et que rien n'oblige à
  entendre. Un joueur qui part à gauche ne saura jamais pourquoi il est là.
- **Le jeu ne finit nulle part.** `B.etat` ne prend que `titre | jeu | pause | carte` :
  l'état `fin` qu'annonce la carte du dépôt (« Côté JS », ligne `jeu.js`) **n'a jamais été
  écrit**, et une partie ne se conclut nulle part : elle se quitte. (Elle s'envoyait au
  tableau des scores depuis le menu PAUSE ; ce tableau est parti le 17 sept. 2026.)
- **Le mécanisme, lui, est entièrement là** — c'est pour ça que l'ouverture est une vague de
  taille 2 et pas un jalon : `B.cinema` fige la ville et enchaîne des répliques **dites à
  voix haute** (`Histoire.dire` : ACTION passe, la voix finie passe toute seule, la radio et
  l'ambiance baissent), `Jeu.transiter()` fait un fondu dans le bon ordre, `Son.Mus` tient un
  thème avec sa queue, le **narrateur du Clairon** a déjà sa voix (`annonceur centre d'achat
  1`) et lit des textes qui ne sont pas des répliques de mission (`audio.voix_journal`, slug
  `narrateur-journal-…`), et l'**autobus** est un véhicule du catalogue avec son sprite,
  devant un **terminus** qui est le point d'apparition du joueur. Aucun sprite neuf, aucun
  moteur neuf.

### 1re vague — l'ouverture — **livrée le 16 sept. 2026**

⚠️ **Ce qui a bougé en la faisant, et qui ne se devine pas** : `Jeu.commencer()` s'est coupé en
**deux**. Il POSE une partie — c'est ce qu'appellent cent tests du banc, qui veulent une ville et pas
une introduction — et le nouveau `Jeu.jouer()` est le **geste** : il pose la partie, puis lance
l'ouverture si elle est neuve. Les deux chemins de JOUER (le bouton de la page et la manette) passent
par `jouer()`. Sans cette coupure, chacun des cent tests aurait joué la scène avant de mesurer quoi
que ce soit. Et le morceau s'appelle **`ouverture`**, pas `mus_ouverture` : `mus_*` est le préfixe des
deux musiques d'ÉTAT (poursuite, bagarre), et l'ouverture est une pièce nommée comme `titre`.

- ⚠️ **Elle part sur JOUER, jamais au chargement de la page.** Le navigateur retient
  l'`AudioContext` tant que personne n'a touché (`Son.reveiller`, `Son.enAttente`) : une
  ouverture lancée par `Jeu.demarrer()` serait **muette une fois sur deux**, et une
  introduction audio muette n'est pas une introduction. Le bandeau du titre reste donc ce
  qu'il est — c'est lui qui réclame le geste — et l'ouverture commence juste après, dans
  `commencer()`. ⚠️ **Après**, et pas avant : c'est `commencer()` qui peuple la ville, et un
  autobus filmé sur une carte vide n'existe pas.
- **Ce qu'on voit** (rien de neuf à dessiner) : l'autobus entre par le bord de l'écran,
  s'arrête devant le terminus, la caméra le suit ; la portière s'ouvre, le bonhomme descend
  — il n'y a pas de valise dessinée, et on n'en promet pas ; le car repart, la caméra monte sur la ville et le titre s'inscrit.
  ⚠️ **Son propre noir, pas celui de `Jeu.transiter()`** : un fondu de porte FIGE la boucle
  (`B.transition` coupe `maj()`), or c'est justement pendant le noir que le car doit
  arriver. Deux compteurs qui ne veulent pas dire la même chose ne partagent pas une
  variable — le voile de l'ouverture vit dans `B.ouverture.noir`, dessiné par le HUD.
- **Ce qu'on entend** : le narrateur dit la prémisse en trois ou quatre phrases (l'oncle, le
  garage, la dette, les 50 $) sur `ouverture` — un morceau de plus dans `audio.MUSIQUES`
  (19 aujourd'hui, 851 s en tout) **et** écrit en notes dans `musique.py`, parce que les
  notes restent le filet. Le moteur au ralenti, la portière et la rumeur de la rue existent
  déjà au catalogue ; il n'y a que le soupir des portes d'air à ajouter, s'il en faut un.
- **Le texte reste la source** : les répliques de l'ouverture vivent dans `missions.py` comme
  toutes les autres, **jamais dans `histoire.js`**, et `audio.voix_ouverture()` les génère
  sur le modèle exact de `voix_journal()` (`mission: 'ouverture'`, slugs
  `narrateur-ouverture-1…n`). Une réplique dont le mp3 manque **s'affiche sans voix** : c'est
  la règle du fichier, et c'est elle qui permet d'écrire le texte avant de dépenser un
  crédit.
- ⚠️ **On la passe, et on la revoit.** ACTION saute une réplique (le cinéma sait déjà le
  faire), PAUSE saute l'ouverture entière — à la manette et au doigt comme au clavier. Une
  ouverture qu'on ne peut pas passer devient une punition à la deuxième partie.
- ⚠️ **Une partie en cours ne la rejoue pas.** `commencer()` reprend une sauvegarde (jour,
  position, char devant la planque) : l'ouverture ne joue qu'à la **première** partie d'une
  sauvegarde (drapeau `ouvertureVue`, versionné comme le reste de la sauvegarde et couvert
  par le repli sur `etatInitial()`), et se revoit à la demande depuis le carnet.
- ⚠️ **Le poids se surveille** : `static/audio/` pèse **12 Mo en 166 fichiers**, chargés à la
  demande (`fetch` puis `decodeAudioData`). L'ouverture est le seul son qu'il faut avoir
  **avant** de le jouer : elle se précharge pendant que le joueur lit l'écran titre, et si le
  fichier n'est pas là, le texte défile quand même.

### 2e vague — le générique (taille 1, ⚠️ **attend M13**)

- ⚠️ **Il n'y a pas de fin à filmer avant M13.** Les deux fins (_Le Boss_, _Sacrer son camp_)
  sont la dernière tranche de **M16** ; cette vague est ce qui se **branche dessus**, pas ce
  qui les écrit. Ce qu'elle apporte au moteur : l'état `fin` qui manque à `B.etat`, et un
  enchaînement qui ne soit pas un item de menu.
- ⚠️ **Il s'écrit dans le vocabulaire de plans** (« Les missions mises en scène »), pas en
  dur comme l'ouverture l'a d'abord été : `camera` sur le district libéré, `conduire` pour le
  traversier, `titre` pour les chiffres. Les deux génériques sont des données dans
  `missions.py`, comme les scènes de mission.
- **Ce qu'on voit** : la ville en plan large, la caméra qui traverse le district libéré — ou
  le traversier qui s'éloigne du quai, selon la fin — puis les chiffres de la partie qui
  montent un à un (fortune, missions, propriétés, jours, la dette de Rocco réglée ou non),
  et la manchette du Clairon du lendemain.
- **Ce qu'on entend** : `generique`, dans `audio.MUSIQUES` et en notes comme les autres —
  une variante de l'ouverture, même tonalité, plus lente, pas un morceau étranger. Et la
  manchette **lue par le narrateur qui a ouvert le jeu** : c'est le même homme aux deux
  bouts, et c'est ça qui fait une ligne plutôt que deux animations.
- **Elle mène au BILAN** (`Hud.menuBilan`) : jours joués, fortune, propriétés, paquets,
  crimes. ⚠️ Elle menait au tableau des scores jusqu'au 17 sept. 2026 ; il a été retiré du
  jeu, et le bilan est ce qui reste à montrer quand le générique se termine.
- ⚠️ **La partie continue après le générique** (règle de M13, inchangée) : le monde reste,
  la sauvegarde ne se referme pas. Un générique qui verrouille la ville transforme une fin
  en écran de défaite.

**Ce que ça coûte en crédits** : deux morceaux de 45 s à **30 crédits la seconde = 2 700**
sur les 90 000 du mois, plus quelques centaines de caractères de narration (les voix se
paient au caractère). Même échelle que les dix-neuf morceaux déjà générés.

**Juges** — la règle habituelle : on juge le **câblage**, pas la fiche.

- _Python_ : chaque réplique de l'ouverture a un personnage connu et un slug de voix unique ;
  `ouverture` et `generique` existent des **deux** côtés (un mp3 déclaré par
  `exporter()` **ou** des notes dans `musique.py`) — une musique qui n'a ni fichier ni notes
  est un silence qui se déploie.
- _Banc_ : l'ouverture se **termine toujours** (elle ne peut pas laisser `B.cinema` ouvert),
  PAUSE la saute à n'importe quelle réplique, et l'état de la partie après l'ouverture est
  exactement celui qu'on aurait sans elle — joueur vivant, à sa tuile, sans étoile, sans
  mission en cours.
- _Banc_ : une sauvegarde qui porte `ouvertureVue` ne rejoue pas l'ouverture ; une sauvegarde
  d'avant le drapeau ne plante pas.
- _Navigateur_ : JOUER au clavier **et** à la manette lance l'ouverture, aucune erreur
  console, et le son n'est jamais demandé avant le geste.
- _Générique_ : le test qui force chacune des deux fins (déjà prévu par M13) vérifie qu'on
  retombe sur une ville jouable, bilan fermé ou non.

⚠️ **Ce que les juges de la 1re vague ont réellement attrapé** (13 dans `test_ouverture.py`, plus un
dans `test_navigateur.py`) : deux pièges de mesure dans les juges eux-mêmes — le banc **écrit dans le
tableau de traces qu'on tient** (sans `.slice()`, les images suivantes remplissent la mesure qu'on
vient de prendre), et compter les `fillRect` pour prouver que le HUD se tait **accuse l'ouverture** :
le titre « BANDINI » en corps 4 s'écrit pixel par pixel et en dessine plus qu'un HUD complet. On juge
donc un rectangle NOMMÉ (la barre de vie, `6, 6, 60, 5`), pas un nombre. Et le juge « l'ouverture ne
change rien » a tenu du premier coup — parce que la règle « aucun dé tiré » était écrite avant le
code, pas après.

## Notes

demande de Martin : « il faut qu'il y ait une ligne d'histoire qui commence par une
introduction audio et visuel au lancement du jeu... aussi une animation audio visuel à la
fin ».

⚠️ **1re vague livrée le 16 sept. 2026 — l'ouverture.** Le car de six heures entre au
terminus, s'arrête, le bonhomme descend, le car repart et le titre s'inscrit ; le
**narrateur du Clairon** dit la prémisse en quatre phrases (`missions.OUVERTURE`, voix
ElevenLabs, `musique-ouverture.mp3` **et** trente secondes écrites en notes dans
`musique.py`). Elle part sur **JOUER** (`Jeu.jouer()`, distinct de `commencer()`), se passe
d'un bouton, ne se rejoue pas, et se revoit du carnet. **13 juges** (`test_ouverture.py`) +
un juge navigateur qui prouve que la voix se décode.

- ⚠️ Le morceau s'appelle `ouverture`, pas `ouverture` : `mus_*` est réservé aux deux
  musiques d'ÉTAT. Reste le **générique**.
- ⚠️ **Mesuré le 16 sept. 2026 : le jeu ne dit JAMAIS sa prémisse, et il ne finit nulle
  part.** Le titre est un voile HTML (`voile-titre`) posé sur la ville figée au terminus —
  et **vide**, les entités ne naissant qu'à `Jeu.commencer()`, qui pose le bonhomme devant
  la porte et écrit `BAIE-DES-BRUMES` pendant 150 images. C'est tout. L'oncle Rocco, le
  garage, les 15 000 $ de Sal : c'est écrit **dans ce plan**, dans `economie.DETTE` et dans
  une réplique de Ti-Guy qu'il faut aller chercher à la porte du terminus. À l'autre bout,
  `B.etat` ne prend que `titre`, `jeu`, `pause` et `carte` : l'état `fin` qu'annonce la
  carte du dépôt (« Côté JS », `jeu.js`) **n'a jamais été écrit** : rien ne conclut une
  partie.
- ⚠️ **Deux vagues, deux échéances** : l'**ouverture** se livre tout de suite (rien de neuf
  à dessiner — l'autobus, le terminus, la caméra, le fondu `Jeu.transiter()` et le cinéma
  `B.cinema`, qui fige la ville et dit une réplique à voix haute, existent tous), le
  **générique** attend une fin à laquelle arriver (**M13**, dernière tranche de M16).
- ⚠️ **Le son n'a pas le droit de jouer avant un geste** : le navigateur retient
  l'`AudioContext` tant que personne n'a touché — une ouverture partie au chargement serait
  muette une fois sur deux. Elle part donc sur JOUER, pas sur `demarrer()`.
- ⚠️ **Et on la passe** : ACTION saute une réplique, PAUSE saute l'ouverture entière, une
  partie en cours ne la rejoue pas, et elle se revoit depuis le carnet. Le **même
  narrateur** aux deux bouts (celui du Clairon) : c'est lui qui en fait une ligne et non
  deux animations
