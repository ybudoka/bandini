# Des garages où l'on entre : semer la police et repeindre

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « il faut des portes de garage qu'on peut vraiment
entrer. pour permettre de semer la police en voiture. », puis « repeindre des voitures ».
Aujourd'hui le rideau du garage Bandini monte tout seul, mais sa tuile reste un MUR : on se
gare devant, on n'entre pas, et rien ne sème la police qu'attendre hors de vue ou changer de
char. Vague 1 — entrer, se cacher, ressortir d'une autre couleur. Le rideau levé laisse
passer le char DU JOUEUR (et lui seul) dans une baie sous le toit : le char disparaît sous
le linteau, le rideau redescend derrière lui. Des carrosseries (« PEINTURE MINUTE ») dans la
ville, posées EN DERNIER sur des bâtiments déjà là, sans dé : la ville ne glisse pas. On y
entre, le rideau tombe, le pistolet siffle, et le char ressort d'une autre couleur — le vol
effacé, les étoiles à zéro, les patrouilles qui cherchaient ce char-là le perdent — pour le
prix de la peinture ; sans l'argent, le rideau ne monte pas. Chez Ti-Guy, entrer ouvre le
menu du garage à l'abri (réparer, repeindre, vendre) au lieu de l'ouvrir devant.

- ⚠️ Seul le char du joueur passe le seuil : l'auto-patrouille qui suit reste dehors, devant
  le rideau qui tombe.
- ⚠️ Ni le char d'une mission en cours, ni pendant une scène : la livraison au garage se
  fait toujours devant le rideau.
- ⚠️ La baie et les carrosseries se posent à la fin de `generer` (voir le lot du poste) : un
  juge compare la ville avec et sans elles.

## Fiche de la deuxième vague

Martin (21 sept. 2026), à la suite de la première : « oui vas-y pour la suite » — les garages des
bungalows, pour se cacher **sans** passer par la peinture.

Aux Érables, quelques bungalows ont un garage qu'on entre au volant, comme la carrosserie : le
rideau monte, le char passe sous le toit, le rideau retombe. Rien ne se repeint et rien ne se paie :
on est **caché**. La police ne voit pas sous un toit, les étoiles tombent comme hors de vue, et on
ressort en reculant quand on veut (« CACHÉ — RECULE POUR SORTIR »). C'est la cachette gratuite et
lente ; la carrosserie reste l'instantanée qui coûte.

- ⚠️ Caché, c'est caché pour TOUT le monde : l'hélico ne voit pas à travers un toit, et une
  auto-patrouille garée devant le rideau ne « sent » plus le joueur à 60 px (`Police.commandes`).
  Sans ça, cinq étoiles ne tomberaient jamais dans un garage.
- ⚠️ Une entrée asphaltée du rideau jusqu'à la rue (le gazon d'un bungalow n'est pas une
  entrée de garage), et rien de fixe dessus.
- ⚠️ Posés EN DERNIER et sans dé, comme les carrosseries : quelques bungalows, écartés les uns
  des autres, choisis par une mesure. Pas sur la carte : une cachette ne s'affiche pas — on la
  voit au rideau et à l'entrée asphaltée.

## Notes

**1re vague, livrée le 21 sept. 2026** — on entre, le rideau tombe, on ressort d'une autre
couleur.

- **Le seuil s'ouvre pour un seul char** (`Monde.seuilOuvert`, lu par
  `Vehicules.tuileInterdite`) : rideau levé, la rangée du rideau et les `baie` rangées de toit
  derrière cessent d'être un mur pour le char ADMIS — celui du joueur — et pour lui seul.
  L'auto-patrouille qui suit bute sur la façade, et la ligne de vue (`ligneLibre`) ne traverse
  pas plus un rideau qu'un mur : sous le toit, personne ne te voit. `baie` (deux rangées, de
  quoi cacher l'autobus et ses 48 px) voyage avec chaque porte ; Python la garantit, le
  navigateur ne la devine pas.
- **L'atelier** (`Missions.majGarage` → `majAtelier`) : tout entier sous le linteau, le volant
  se fige et le rideau retombe derrière le pare-chocs — `baisse` → `peint` (1,5 s, trois passes
  de pistolet synthétisées) ou `menu` (Ti-Guy) → `leve` → `sortie`. On ressort en reculant ;
  le rideau tient tant que le char est dessous ou devant.
- **Les carrosseries** (`carte._Chantier.poser_les_carrosseries`) : une par district, sur un
  commerce sans porte dont l'enseigne change de nom (`devantures.CARROSSERIES` : CARROSSERIE,
  PEINTURE AUTO — La Shop en avait déjà une qui ne menait nulle part, c'est elle qu'on ouvre —,
  PEINTURE MINUTE), et un point des services sur la carte. Sur la ville livrée : le Faubourg,
  La Shop et Les Quais ; La Pointe sur trois graines sur quatre. ⚠️ **Les Érables n'en ont
  pas** : leurs trois commerces se visitent tous, et une enseigne de carrosserie au-dessus d'un
  dépanneur qu'on visite mentirait deux fois (une piste pour la suite : les garages des
  bungalows).
- ⚠️ **Posées EN DERNIER et sans dé**, comme le rideau de Ti-Guy : la façade la plus proche du
  cœur du district qui offre deux tuiles de vitrine ou de mur (jamais la porte peinte, une
  condamnée ou des planches), deux rangées de toit du même bâtiment derrière, du roulable
  jusqu'à la rue (cinq tuiles au plus, sans meuble fixe), ni chantier, ni façade qui peut
  brûler à deux pas, ni lieu garanti à moins de huit tuiles, ni bloc cossu. Un juge compare la
  ville avec et sans elles : rien ne bouge hors du rideau, de l'abord et du nom sur le bandeau.
- **Le prix** (`economie.CARROSSERIE`) : la peinture de Ti-Guy (100 $) plus 50 $ par étoile —
  cinq étoiles effacées pour cent piastres rendraient la police décorative. Il se fixe à
  l'ENTRÉE (une étoile gagnée en route ne se paie pas) et l'argent se recompte rideau baissé.
  Sans l'argent, le rideau ne monte pas ; une auto-patrouille ne se repeint pas (« ON TOUCHE
  PAS À ÇA ») ; une remorque ne rentre pas. ⚠️ Le char d'une mission PASSE à la carrosserie —
  semer la police en pleine mission, c'est tout l'intérêt — mais pas chez Ti-Guy, où il se
  livre devant le rideau.
- **Chez Ti-Guy, on entre aussi** : rideau baissé, son menu s'ouvre à l'abri (REPARTIR en
  tête). ⚠️ Le menu DEVANT le rideau reste, à l'arrêt dans la baie — on vend sans entrer, et
  ses juges tiennent. Il ne rattrape pas celui qui ressort en reculant : l'atelier garde
  `dedans` jusqu'à ce que le char ait quitté la baie.
- **Repeindre** : une seule main pour le menu de Ti-Guy et la carrosserie (`Missions.repeindre`)
  — une autre couleur de la fiche, le vol effacé, l'alarme coupée, `Police.remiseAZero()`.
  ⚠️ Un char d'une seule couleur (taxi, cabriolet) ressort de la même : sa fiche n'en a pas
  d'autre.
- **Le dessin** : un char près d'un rideau se peint sous un masque `evenodd` qui retire, dans
  les colonnes de la porte, tout ce qui est au-dessus du bas du rideau (`Monde.basDuRideau`,
  le calcul de `dessinerPortesDeGarage`) : le char disparaît sous le linteau, puis derrière
  les lames qui descendent.
- ⚠️ **Le rideau EST la porte** : la porte PEINTE du bandeau (un commerce sans porte en a une,
  peinte) redevient son mur — une peinte ne double jamais une vraie (`test_devantures`). Et un
  point sous un rideau a sa porte au-dessus de lui : le juge des lieux l'admet.
- ⚠️ **Les juges qui comparent la ville avec et sans une étape neutralisent les carrosseries des
  DEUX côtés**, comme `devants.deplacer` : posées sur la ville finie, elles choisissent leur
  façade d'après les noms, les planches et les machines — un local À LOUER ou une machine devant
  la vitrine les fait changer de rue. Deux juges l'ont dit (les commerces qui montent, une
  machine de plus) ; ils le font maintenant.
- ⚠️ **Sous le toit, on ne descend pas** : les portières donnent sur des murs (« RECULE
  D'ABORD »). Forcé — vendu chez Ti-Guy, une épave —, on ressort à pied au milieu de la baie.
  Et ⚠️ **un agent collé au rideau ne sort plus le joueur du char** (`Police.gere` : « un char
  arrêté ne protège de rien ») : sans cette garde, il le tirait à travers les lames.

Juges : 7 de ville sur quatre graines (`test_garages_ou_l_on_entre.py`) et 9 de banc au bouton
(`test_garages_ou_l_on_entre_js.py`, 10 cas). 27 mutations : 25 rougissent ; les deux qui
survivent sont couvertes par une autre règle (vider l'abord : `devants.deplacer` écarte déjà le
mobile ; « sous un toit » : « du même bâtiment » l'implique). Quatre mutations survivaient au
premier passage, et chacune a durci un juge : l'agent posé sur le trajet mourait écrasé, le juge
du dessin relisait `basDuRideau`, la vente « dans le mur » était rattrapée par le garde-fou du
piéton, et rien ne regardait une porte peinte couverte par le rideau. Une autre a montré une
ligne inutile (`servi` à l'entrée), retirée. Regardé dans Chromium : le char rouge s'engouffre,
le rideau tombe, il ressort orange. 3 549 tests ; deux rouges déjà sur la base (la foule, les
Cravates de M2).
