# La roue d'armes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux un meilleur sélecteur d'arme ».

- ⚠️ **Mesuré** : le catalogue compte **13 armes** et `cycler` n'avançait que d'**un cran,
  dans un seul sens** — revenir de la carabine aux poings coûtait **12 pressions**, en
  pleine fusillade, et le HUD ne montrant que l'arme en main, on cyclait **à l'aveugle**.
  Deux gestes sur le même bouton : une **tape** bascule entre les **deux dernières** armes
  (les poings pour les poches, la carabine pour le toit — le geste qu'on fait le plus
  souvent, et il ne coûte rien) ; **tenir** ouvre la **roue**, les armes possédées en
  cercle, on choisit à la direction (stick, flèches, pouce), on relâche pour dégainer. Rien
  de neuf n'a été dessiné : les icônes sont les `OBJETS` 16×10 des armes lâchées par terre,
  avec les munitions sous chacune et **grisée + rouge à sec** — c'est tout ce que le vieux
  cycle ne disait pas (on dégainait un pistolet à zéro et on perdait le tour).
- ⚠️ **La roue RALENTIT le monde, elle ne le FIGE pas** : une image sur quatre. Les menus du
  jeu figent (« le temps ne passe pas au comptoir ») et c'est juste pour un comptoir ; une
  roue qui fige est une **pause gratuite** au milieu d'une fusillade. Le prix, c'est le
  quart de vitesse **et** un joueur cloué sur place — une seule direction, un seul rôle,
  sinon choisir son arme au stick ferait marcher le personnage vers son choix.
- ⚠️ **Et on ne se bat pas dedans** : ni frappe, ni ACTION, ni prise d'otage qui mûrit. Sans
  ces portes, tenir ARME donne un **ralenti à la demande** — viser tranquillement, puis
  tirer ; la prise d'otage lisait ACTION **avant** la porte de la frappe, et elle a été
  fermée avec les autres.
- ⚠️ **Deux défauts trouvés en chemin, et le premier n'a rien à voir avec les armes.**
  `Jeu.boucle` avance par **accumulateur** — zéro à quatre `maj` par image dessinée — donc
  une **tape d'une image tombe parfois ENTIÈREMENT entre deux `maj`**, et le niveau du
  bouton (`bas`) ne la voit jamais : mesuré, elle se perdait une fois sur deux et le bouton
  avait l'air brisé. Elle se latche sur `neuf`, qui survit jusqu'au `videPresse` fermant le
  tour : le seul signal qu'un pas variable ne peut pas manger. Le second est le `cycler` à
  sens inverse, écrit puis **supprimé** — la roue rend le cycle à rebours inutile, et le
  dépôt ne garde pas une branche que rien n'atteint.
- ⚠️ **Le juge qui compte le plus refait le chemin complet** : du créneau au pixel
  (`Hud.posteDeLaRoue`), du pixel à la direction, de la direction au créneau
  (`Combat.creneauVise`). Une roue dessinée dans un sens et lue dans l'autre se joue à
  l'envers — le pouce pointe la carabine, le jeu dégaine la pelle — **sans qu'aucun test de
  logique ne rougisse**. 11 juges neufs (`test_roue_js.py`), **rouge-avant prouvé sept
  fois** ; 1715 tests.
- ⚠️ Jugé dans un **worktree isolé**, et la première tentative était **fausse** : y copier
  mes fichiers entiers a emporté le chantier d'une autre session — 168 juges rouges qui
  n'étaient pas à moi, mon `jeu.js` appelant un `Histoire` qui n'existe que chez elle. Les
  hunks se posent maintenant par **texte exact**, et le juge tourne sur `HEAD` + la seule
  roue.
