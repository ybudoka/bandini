# Les quatre saisons, réalistes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 27 sept. 2026 : « les 4 saisons réalistes »._

_Ce que ça donne :_ on sait en quelle saison on est **en regardant l'écran**, sans lire le HUD. Janvier
est blanc, gris et glissant ; avril est brun, mouillé et plein de nids-de-poule ; juillet est vert,
tard le soir et plein de monde dehors ; octobre est rouge et orange, et les feuilles volent derrière
les chars. Un Québec vu de haut, qui change quatre fois par année.

**Aujourd'hui** la saison est une **étiquette**, pas un paysage. `app/calendrier.py` (26 sept. 2026)
donne une année de 40 jours, douze mois et quatre saisons (le jour 1 d'une partie est le 1er janvier),
en pure fonction du jour. Huit modules la lisent, chacun pour sa chose : la motoneige et le pont de
glace (l'hiver), la cabane à sucre (le printemps), la Saint-Jean, le déménagement et le ciné-parc
(l'été), le temps des Fêtes. **Le reste de la ville ne bouge pas** : les arbres sont verts en janvier,
et la neige de M12 (`neige.js`, derrière l'option « TEMPÊTES DE NEIGE (ESSAI) ») tombe **tous les
trois jours, toute l'année** — une tempête en juillet est possible. Le verglas a ses jours (9 à 11)
et le brouillard ses matins, sans lien avec la saison.

**Aujourd'hui, au volant** (`vehicules.js`, « Adherence ») : un char ne dérape pas, il **flotte**. Sa
vitesse glisse vers son cap d'une part `adh` par image, et `adh` est un seul nombre : l'adhérence du
char × la neige (0,3 en pleine tempête, 0,75 derrière la charrue) × le verglas (0,4) × la rue mouillée
(l'arroseuse), avec les **pneus d'hiver** du garage de Ti-Guy qui en rendent une part (`Garage.hiver`).
Sur la glace, le char tourne donc comme au sec et dérive un peu plus : pas de sous-virage, pas de
tête-à-queue, pas de contre-braquage, pas de roues bloquées. Le frein à main change `adh`, sans faire
partir l'arrière. Rien ne marque le sol, et rien ne crisse. Seul le **nid-de-poule** fait déjà perdre
le contrôle (`nid_derape_*` : quelques images sans direction et le nez qui part). Le trafic, lui,
roule sur des rails : il lève le pied dans la neige, mais il ne glisse jamais.

**Ce qu'on veut**, en cinq vagues jouables (à trancher par Martin — l'ordre, et ce qui tombe) :

- **Vague 1 — le paysage.** Une **palette par saison** pour ce qui pousse : le gazon, les parcs, les
  arbres de rue, les haies, les sentiers — vert tendre au printemps, vert franc l'été et jauni en
  août, rouge-orange-jaune à l'automne (des érables : c'est le Québec), branches nues l'hiver et
  conifères poudrés. **La neige qui tient l'hiver** : au sol, sur les toits et les chars garés, de
  décembre à mars, pas seulement pendant la tempête ; et **les tempêtes seulement l'hiver** (plus de
  flocons en juillet). **La longueur du jour** : le soleil se couche vers 16 h en décembre, vers 21 h
  en juin — la lumière suit, sans toucher aux heures des commerces ni aux habitudes de la nuit.
- **Vague 2 — la glace et le dérapage.** La **glace de l'hiver**, qui n'attend plus les trois jours du
  verglas : des **plaques de glace noire** qu'on voit à peine (sur les ponts, dans l'ombre des
  bâtiments, aux arrêts où les chars ont poli la neige), tirées à l'empreinte de la tuile ; au
  printemps, **le gel et le dégel** — la fonte le jour, le regel la nuit, la glace le matin ; les
  **patinoires** des parcs, où l'on glisse à pied ; la baie gelée (le pont de glace existe). Et un
  **vrai dérapage** quand ça glisse : l'**avant** qui refuse de tourner (**sous-virage** : tout droit
  dans le banc de neige), l'**arrière** qui part quand on accélère ou qu'on tire le frein à main en
  courbe (**survirage**), le **tête-à-queue** si on laisse faire, le **contre-braquage** qui rattrape,
  les **roues bloquées** qui ne dirigent plus quand on freine trop fort. Le sol le montre : des
  **traces de pneus** noires au sec, des **sillons** dans la neige, qui s'effacent. On l'entend : le
  **crissement** au sec, le silence inquiétant sur la glace, le **banc de neige** qui étouffe et où
  le char s'enlise (les roues patinent, on recule, on repart). À pied aussi : un passant qui court
  sur la glace **glisse et tombe**, et le joueur comme les autres. Le **trafic et la police** ne
  restent pas sur leurs rails partout : sur la glace, un char de la ville peut glisser dans le banc,
  accrocher celui d'en avant, finir dans le fossé.
- **Vague 3 — ce qui tombe, et le sol.** **La pluie** (printemps et automne), **les orages** l'été ;
  **la fonte** en avril : la gadoue brune, les flaques qui éclaboussent les passants, les bancs de
  neige sales qui rapetissent, les **nids-de-poule** ; **les feuilles mortes** au sol en octobre,
  soulevées derrière un char qui passe. L'**adhérence** suit le sol (gadoue, feuilles mouillées,
  pluie) et dérape comme sur la glace de la vague 2 — moins fort.
- **Vague 4 — les gens et la rue.** La **garde-robe par saison** (`garderobe.js`) : tuques, foulards
  et manteaux l'hiver, t-shirts et shorts l'été, imperméables sous la pluie ; les **abris Tempo** dans
  les entrées de novembre à avril ; les **bancs de neige** le long des trottoirs que la charrue
  laisse ; la fumée des cheminées l'hiver ; les terrasses, les bornes-fontaines ouvertes et les
  passants plus nombreux dehors l'été ; les citrouilles sur les perrons à l'Halloween (une date de
  plus dans `calendrier.DATES`).
- **Vague 5 — le son.** Une ambiance par saison, par ElevenLabs : le vent et la charrue l'hiver,
  l'eau qui coule à la fonte, les cigales et les tondeuses l'été, les outardes et la pluie à
  l'automne — en fondu enchaîné d'une saison à l'autre.

⚠️ **Ce qui coûte, et ce qui guette :**

- **Une pure fonction du jour et de l'heure**, comme `calendrier.py` : rien à sauvegarder, aucun dé,
  la même saison pour tout le monde. Ce qui se pose dans la ville (abris Tempo, bancs de neige,
  citrouilles, feuilles) se pose **en dernier, sans dé**, tiré à l'empreinte — sinon la ville glisse
  et les juges « ce module ne déplace rien » rougissent.
- **Pas de coupure à minuit** : la palette glisse d'une saison à l'autre sur un jour ou deux (le
  fondu, comme la musique). Une saison ne dure que dix jours du jeu : la transition se voit.
- **Le rythme sur le téléphone** : recolorer la ville ne se fait pas à chaque image — les morceaux
  peints en cache se refont quand la palette change, pas plus. La pluie et les feuilles sont des
  particules comme les flocons : les mesurer à la sonde de performance, et payer enfin la dette
  « le rythme mesuré sur le vrai téléphone de Martin » (son déclencheur disait : la neige).
- **L'option « TEMPÊTES DE NEIGE (ESSAI) »** : à trancher par Martin — la saison la remplace-t-elle
  (l'hiver neige pour tout le monde), ou reste-t-elle l'interrupteur de toute la météo ? La motoneige
  et le pont de glace en dépendent aujourd'hui. Et les juges de la neige posent des jours précis
  (`premier: 2`, `tous_les: 3`) : les faire lire la saison, pas l'inverse.
- **Le dérapage touche TOUTE la conduite** : les courses, les défis chronométrés, les poursuites, les
  records déjà battus. ⚠️ **Au sec, le char se conduit exactement comme aujourd'hui** (le nouveau modèle
  ne s'éveille que sous une adhérence de 1, et les juges de conduite du sec ne bougent pas) ; le
  dérapage ne se tire pas au dé (le côté où part l'arrière vient du volant, de la vitesse et du sol —
  le nid-de-poule, lui, lit l'empreinte de sa tuile).
- **Glisser doit rester jouable** : au téléphone et à la manette de Martin, le contre-braquage doit se
  sentir et rattraper — un char qu'on ne peut plus tenir n'est pas réaliste, il est injouable. Les
  pneus d'hiver (Ti-Guy) doivent enfin valoir leur prix : la différence se sent dès le premier coin.
- **Le trafic sur ses rails** : le laisser glisser, c'est le laisser quitter sa voie — et le trafic
  sait mal revenir sur son chemin (les pilotes qui se perdent, les chars plantés sur la bordure). Une
  glissade de la ville est donc **courte et finit arrêtée** (le banc, le fossé, l'accrochage), puis le
  char repart ou attend la dépanneuse ; jamais en pleine poursuite une police qui se perd.
- **Les traces de pneus** sont une mémoire, comme la neige déblayée : un nombre borné, qui s'efface,
  peintes au sol sous les chars — et jamais sauvegardées.
- **Une partie neuve commence le 1er janvier** : la première impression est une ville blanche et
  glissante. À trancher par Martin : la garder (c'est l'hiver québécois), ou faire commencer
  l'année ailleurs — ce qui déplace toutes les fenêtres de saison (cabane, Saint-Jean, Fêtes).
- **Les missions** ne changent pas avec la saison, sauf celles qui le disent ; une mission ne doit
  jamais devenir impossible en hiver (la motoneige ne remplace pas un char qu'une mission exige).
- **Regarder une couche peinte** avant de livrer : une capture Chromium par saison, les juges verts
  ne voient pas une palette ratée.

**Juges** : la saison se lit du jour, la même pour tout le monde ; pas une tempête hors de l'hiver ;
la palette d'un parc diffère d'une saison à l'autre et glisse d'un jour à l'autre sans saut ; le soleil
se couche plus tôt en décembre qu'en juin, et les commerces ouvrent à la même heure ; rien de ce qui se
pose pour une saison ne déplace la ville ; un passant de janvier porte un manteau. Et au volant : au sec, la conduite ne change pas d'un
pixel ; sur la glace, un char lancé en courbe sous-vire, le frein à main en courbe fait partir l'arrière,
le contre-braquage rattrape et les pneus d'hiver rattrapent mieux ; des roues bloquées ne dirigent pas ;
un passant qui court sur la glace tombe ; un char de la ville qui glisse finit arrêté, jamais perdu.
