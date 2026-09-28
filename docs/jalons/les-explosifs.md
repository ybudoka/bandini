# Les explosifs

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux des explosifs, C4, grenades, et plus ».

**Tranché avec Martin le même jour** :

- **Les quatre** : la **grenade**, la **dynamite**, le **C4** (et le **char piégé** qu'il permet), le
  **lance-roquettes**.
- **Ce qu'une explosion ouvre** : ce que casse déjà un char qui saute (les gens, les chars, le décor
  destructible) **et certains murs** — « mais juste certains murs ». Les murs **fissurés**, qu'on voit : dedans
  entre deux pièces (la villa du maire, la banque, les planques), dehors sur les murets et les enceintes (les
  entrepôts, la cour de la prison), et là où une mission en veut un. Tout autre mur reste plein.
- **Et le Molotov, en mieux** (ajouté par Martin en cours de séance) — les quatre à la fois : **les gens prennent
  feu**, **le feu se propage**, **il s'allume d'abord**, **plus gros et plus visible** — « je veux voir la
  bouteille voler ». Aujourd'hui (`combat.js`, `allumer`/`majBrasiers`) : une flaque de 20 px qui brûle 5 s et
  mord 12 PV/s à qui reste dedans ; un char dessus finit par brûler.

**Le cœur commun : une seule explosion.** L'explosion du char (`Vehicules.exploser`, `vehicules.js`) sort dans
`Explosions.faire(x, y, puissance, coupable)`, et toutes les bombes passent par elle : elle blesse et renverse les
gens (dégâts qui baissent avec la distance, comme aujourd'hui), abîme les chars (qui sautent à leur tour — la
chaîne), casse le décor (`Entites.decorAutour`), fait céder les murs fissurés du rayon, joue le son, secoue l'écran
et signale le délit `explosion` que la police connaît déjà (`police.js`, `DELITS_ARMES`). Le rayon et les dégâts
de chaque explosif sont dans `app/armes.py`, à côté de la flaque du Molotov (`REGLES`) ; le char garde les siens
(`vehicules.PHYSIQUE` : 60 px, 90 PV).

**Les vagues**, chacune jouable, jugée et livrée seule :

1. **Ce qui se lance** — le cœur commun, puis :
   - **la grenade** (marché noir) : part en cloche comme le Molotov, **rebondit** sur les murs et roule, saute au
     bout de sa mèche (2,5 s) ; tenir le bouton la **cuit** (la mèche brûle dans la main — on la lâche plus près
     de la fin) ;
   - **la dynamite** (ramassée sur les chantiers, et au marché noir, moins chère que la grenade) : mèche de 4 s,
     une étincelle qu'on voit et qu'on entend grésiller, portée courte, rayon plus gros.
2. **Le Molotov, en mieux** :
   - **il s'allume d'abord** : un premier appui allume le chiffon — on le voit flamber dans la main, il éclaire la
     nuit — et le suivant le lance ; ranger l'arme l'éteint ;
   - **on voit la bouteille voler** : son dessin tourne en l'air, son ombre file au sol et rétrécit quand elle
     monte, le chiffon laisse une traînée de flammes et de fumée ;
   - **plus gros, plus visible** : une flaque plus large qui dure plus longtemps, des flammes hautes, de la fumée
     noire, une lueur au sol la nuit ;
   - **les gens prennent feu** : un passant touché s'enflamme, court en hurlant, brûle quelques secondes et peut
     allumer ceux qu'il frôle ; le joueur aussi (se jeter à l'eau l'éteint, l'extincteur aussi) ;
   - **le feu se propage** : la flaque s'étale, et le feu gagne l'herbe sèche, les haies, le décor en bois (bancs,
     palettes, clôtures) et les chars voisins. ⚠️ **Borné** : un nombre de brasiers au plus, et chaque brasier né
     d'un autre vit moins longtemps — un parc ne doit pas brûler jusqu'au matin, ni le téléphone ramer.
3. **Les murs, et le C4** :
   - **le mur fissuré** : une tuile neuve, pleine, dessinée fissurée, qui ne cède qu'à une explosion et devient
     des gravats où l'on passe. Posé **en dernier et sans dé** (voir ⚠️) : dedans, dehors, et pour les missions ;
   - **le C4** (marché noir) : un appui le **pose** — au sol, sur un mur, **sur un char** (il le suit s'il
     roule) ; **tenir** le bouton fait tout sauter, trois charges au plus d'un coup.
4. **Les gros jouets** :
   - **le char piégé** : du C4 posé sur un char vide ; il saute quand quelqu'un le **démarre** — un passant, un
     gangster, un policier — ou à la télécommande. Pas de garage à bombes ;
   - **le lance-roquettes** (marché noir, l'arme la plus chère) : tire droit, la roquette saute à l'impact ; une
     roquette par chargeur, les munitions chères, la portée plafonnée à l'écran comme la carabine.

**Les sons** : des bruitages ElevenLabs neufs — la mèche qui grésille, la grenade qui rebondit, le bip du C4, la
roquette qui siffle, le chiffon qu'on allume, le passant qui brûle. L'explosion existe déjà (`Son.SFX.explosion`). La synthèse reste le filet.

**Les juges** : au catalogue (Python) — les prix qui montent, aucune portée au-delà de l'écran (`test_armes`), chaque
son au catalogue audio ; au banc (JS, joués) — la grenade saute au bout de sa mèche et pas avant, la cuire la fait
sauter plus tôt, le mur fissuré cède et **son voisin plein non**, le C4 suit le char qui roule, le char piégé saute
au démarrage et le coupable est le poseur, la roquette saute à l'impact ; le Molotov qu'on lance sans l'allumer
n'existe pas (le premier appui allume), le passant touché brûle et allume son voisin, le feu gagne la haie et **s'arrête**
(le nombre de brasiers plafonne), l'eau éteint le joueur. Et des captures — le mur fissuré entier puis en gravats, la
bouteille en l'air avec son ombre — avant de livrer (mémoire « Regarder une couche peinte »).

⚠️ **Ce que ça touche** (à relire avant de coder) :
- **Changer une tuile en cours de partie existe déjà** : `Monde.defoncer` (`monde.js`, le char lourd qui casse une
  clôture) et `Chantiers.appliquer` (`chantiers.js`) — mettre à jour `sol`, `solide`, `route`, `passage`,
  invalider les morceaux cuits **avec marge** (la façade lit ses voisines, l'ombre tombe au sud) et la mini-carte.
  ⚠️ `defoncer` refuse exprès les façades (« un trou dans un mur ouvrirait sur un toit ») : c'est pourquoi seul un
  mur fissuré cède — posé **là où il y a du sol des deux côtés**, et un juge le vérifie pour chacun.
- **Les index cuits au chargement** (`devantures`, `residences`, `toits`, les lampes de fenêtre, `portesParTuile`) :
  rien ne doit être posé sur un mur fissuré, sinon une enseigne flotte sur des gravats.
- **Un mur fissuré posé dans la ville la fait glisser** s'il consomme un dé ou grossit un lieu (mémoire « Grossir un
  lieu garanti déplace la ville ») : en dernier, sans dé, et les juges « ce module ne déplace rien » à relire. Dans
  la bande nord : ses dés à elle. Dans un bloc (la villa) : `Monde.carte` est le bloc.
- **Un trou ne se sauvegarde pas** (comme une clôture défoncée) : il se referme au rechargement — c'est voulu,
  ça rend le mur à la mission suivante.
- **Les objets posés au démarrage consomment des identifiants** (mémoire « Décor eager décale les identifiants ») :
  une charge de C4 ou une grenade naît en partie, jamais au chargement.
- **Le feu de bâtiment existe à part** (`incendies.js`, tiré à l'empreinte de l'heure, éteint à l'extincteur) : le feu
  du Molotov reste un feu de **brasiers** (des entités), il ne rallume pas les façades — sinon la ville cesse d'être
  la même pour deux joueurs à la même heure.
- **Le poids du paquet** : des armes et des sons de plus → `test_definitions` dans les juges ciblés.
- **L'enfer de la chaîne** : dix chars garés côte à côte qui sautent l'un l'autre dans la même image — l'explosion
  d'un char se fait à l'image suivante, pas dans la boucle de l'autre.

## Notes

_Rien de livré._
