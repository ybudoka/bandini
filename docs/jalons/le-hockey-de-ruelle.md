# Le hockey de ruelle

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ le soir, dans une ruelle des Érables, des jeunes jouent au hockey bottine avec deux
filets de fortune — on peut se joindre à eux, trois contre trois.

- **Le jeu** : une balle orange, deux filets, trois minutes ; on court avec les commandes du jeu, ATTAQUE
  lance, ESQUIVE passe. Les jeunes jouent contre toi, les enfants à vélo s'arrêtent pour regarder.
- **Un défi** (le rail des défis existe) : gagner par trois buts ; une prime modeste — jamais plus qu'un
  boulot à l'heure — et le respect des Chevreuils (ils sont du même quartier).
- **L'hiver** : quand la neige de M12 tombe, la ruelle devient une patinoire et la balle glisse.

⚠️ **Ce qui guette** : c'est de la physique neuve (une balle qui rebondit, des adversaires qui la
poursuivent) — la plus chère des idées de ce lot. Les jeunes tirent leurs décisions sans `B.rng()`, sur
leur propre graine, sinon tout le hasard du jeu se décale.

**Juges** : une partie se termine toujours (chrono) ; un tir droit au filet vide marque ; les jeunes ne
sortent pas de la ruelle ; aucun `B.rng()` consommé.

## Notes

_Livré le 26 sept. 2026._

- **Le défi** (`missions.DEFIS`, `hockey` ; l'épreuve `hockey` de `Rue`) : le soir seulement, au panneau
  devant le dépanneur des Érables ; il s'ouvre après quatre défis. La patinoire est la ruelle la plus
  proche (deux rangées de `x` sur 22 tuiles — la ruelle fait 32 px de large : c'est serré, c'est une
  ruelle) ; la partie commence quand on y entre. Trois minutes et demie au chrono du défi, le seul à
  l'écran (l'épreuve n'a pas d'horloge à elle : deux chronos ne disaient pas la même chose). On gagne en
  menant par trois buts ; prime 80 $.
- **Le jeu** : toi et deux jeunes du quartier (chandails bleus) contre trois Chevreuils (verts). Les
  jeunes sont PEINTS — ni entités ni `B.rng()` : ils décident sur leur générateur (`mulberry`, semé par
  le jour et la partie), et la patinoire les retient. Le plus proche de la balle y court, le gardien
  (rang 0) tient son filet à la hauteur de la balle et arrête souvent ce qui le frôle, les autres se
  placent ; celui qui a la balle file vers le filet d'en face et tire de près (ou quand on le colle), un
  gardien qui la prend la passe. On ramasse la balle en passant dessus ; ATTAQUE lance dans son cap,
  ESQUIVE passe au plus proche des siens ; un adversaire collé vole parfois. L'hiver (la saison et la
  neige), la ruelle est une patinoire : la balle glisse bien plus loin.
- **Réglé au banc**, avec un pilote qui court à la balle et tire dans le coin que le gardien ne couvre
  pas : sans gardien, 27 buts en trois minutes ; le repit du joueur posé sur son entité n'était jamais
  décompté (il ne touchait plus la balle après son premier tir — il vit dans l'épreuve) ; le test « dans
  la patinoire » la rétrécissait au lieu de tolérer un débord ; les filets ramenés à 16 px. Ce pilote gagne
  en 13 à 37 s ; un humain au clavier dans une ruelle de deux tuiles mettra plus.
- **Juges** : `test_hockey_js.py` (le soir, dans une ruelle des Érables, cinq jeunes ; une partie finit
  toujours au chrono et aucun jeune ne sort — même poussé dehors, il est ramené ; un tir droit au filet
  vide marque ; aucun dé du jeu ; on gagne par trois buts ; l'hiver la balle glisse). Chaque juge a été vu
  rougir sous sa mutation.
- **Pas fait, à dire** : le **respect des Chevreuils** (la réputation d'un gang est à trancher avec « La
  réputation et la lecture des passants ») ; les enfants à vélo qui s'arrêtent pour regarder ; pas de
  son de rondelle à lui (le cône).
