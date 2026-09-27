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

**Ce qu'on veut**, en quatre vagues jouables (à trancher par Martin — l'ordre, et ce qui tombe) :

- **Vague 1 — le paysage.** Une **palette par saison** pour ce qui pousse : le gazon, les parcs, les
  arbres de rue, les haies, les sentiers — vert tendre au printemps, vert franc l'été et jauni en
  août, rouge-orange-jaune à l'automne (des érables : c'est le Québec), branches nues l'hiver et
  conifères poudrés. **La neige qui tient l'hiver** : au sol, sur les toits et les chars garés, de
  décembre à mars, pas seulement pendant la tempête ; et **les tempêtes seulement l'hiver** (plus de
  flocons en juillet). **La longueur du jour** : le soleil se couche vers 16 h en décembre, vers 21 h
  en juin — la lumière suit, sans toucher aux heures des commerces ni aux habitudes de la nuit.
- **Vague 2 — ce qui tombe, et le sol.** **La pluie** (printemps et automne), **les orages** l'été ;
  **la fonte** en avril : la gadoue brune, les flaques qui éclaboussent les passants, les bancs de
  neige sales qui rapetissent, les **nids-de-poule** ; **les feuilles mortes** au sol en octobre,
  soulevées derrière un char qui passe. L'**adhérence** suit le sol (gadoue, feuilles mouillées,
  pluie), comme la neige le fait déjà.
- **Vague 3 — les gens et la rue.** La **garde-robe par saison** (`garderobe.js`) : tuques, foulards
  et manteaux l'hiver, t-shirts et shorts l'été, imperméables sous la pluie ; les **abris Tempo** dans
  les entrées de novembre à avril ; les **bancs de neige** le long des trottoirs que la charrue
  laisse ; la fumée des cheminées l'hiver ; les terrasses, les bornes-fontaines ouvertes et les
  passants plus nombreux dehors l'été ; les citrouilles sur les perrons à l'Halloween (une date de
  plus dans `calendrier.DATES`).
- **Vague 4 — le son.** Une ambiance par saison, par ElevenLabs : le vent et la charrue l'hiver,
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
pose pour une saison ne déplace la ville ; un passant de janvier porte un manteau.
