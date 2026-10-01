# Des intérieurs fidèles à l'extérieur : la revue complète

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (29 sept. 2026)_, après la deuxième vague du bidonville de la gare (on entre dans les maisons
pauvres, et on y trouve un logement ordinaire) : « je veux des intérieurs toujours représentatifs de l'extérieur.
Ajoute au plan que je veux une revue complète des intérieurs dans ce sens ».

**La règle, pour toute la ville et pour de bon** : ce qu'on voit en poussant une porte doit se lire comme la
suite de ce qu'on a vu dehors. Une maison pauvre a un intérieur pauvre, une maison cossue un intérieur cossu, un
logement du Petit-Canton est au Petit-Canton, un bungalow de banlieue n'est pas un plex du Faubourg.

**Ce qui tient déjà** (livré, à ne pas refaire) :

- **La taille** : la pièce a les mesures de sa part de bâtiment
  ([l'intérieur à la mesure du bâtiment](l-interieur-a-la-mesure-du-batiment.md#fiche)), et un étage a la même
  empreinte que le rez-de-chaussée.
- **Le nom du commerce** suit la taille de son bâtiment
  ([le commerce à la mesure de son bâtiment](le-commerce-a-la-mesure-de-son-batiment.md#fiche)).
- **Un peu du standing, pour les commerces seulement** : `piece_de_commerce(standing=…)` (le comptoir d'un commerce
  pauvre, les plantes d'un commerce cossu —
  [des quartiers qu'on reconnaît](des-quartiers-qu-on-reconnait-riches-pauvres-et-zones.md#fiche)).

**Ce qui manque** (le premier inventaire, à compléter par la revue) :

- **Les logements ne suivent rien** : `piece_de_logement` ne reçoit ni le standing, ni le district, ni le genre
  du bâtiment. Les maisons pauvres de la gare, les maisons cossues des Érables et les logements du Petit-Canton
  ont le même intérieur.
- **Le district** : un intérieur du Petit-Canton, des Quais, de La Shop ne dit rien de son quartier.
- **Le genre du bâtiment** : bungalow, plex à escalier, maison de brique, hangar — dehors on les distingue, dedans
  non.
- **Les matériaux et l'état** : la façade (brique, bois, planches), les fenêtres placardées, le fer rouillé — dedans,
  des murs propres et des meubles neufs partout.
- ⚠️ **Le mur de la porte, vu de dedans, n'est pas un mur de la pièce** — Martin (29 sept. 2026) : « les portes
  et murs des portes intérieur doivent avoir des murs harmonisés ». Dans le logement `nord_logement_1001`
  (capture du 29 sept.), trois murs sont en plâtre gris et le quatrième, celui de la porte, est la **façade
  de brique rouge** et ses fenêtres bleues, peinte comme dehors (le plan de la pièce emploie les tuiles de
  façade `F`, `W`, `D`). Le mur de la porte et la porte elle-même doivent être du même mur que les trois
  autres : même matière, même couleur, fenêtres et porte vues de l'intérieur. À vérifier dans **toutes** les
  pièces (logements, commerces, lieux garantis, blocs), avec un juge qui compare la matière du mur de la porte
  à celle des autres murs.
- **Les pièces faites à la main** (les lieux garantis, les blocs de carte, les pièces des missions) : chacune à
  relire contre son extérieur.

**La revue** : faire l'inventaire de tous les intérieurs (chaque famille de pièce × standing × district × genre
de bâtiment, plus chaque pièce faite à la main), avec une capture dedans et dehors pour chacun ; dresser la liste
des écarts ; puis corriger par vagues, chacune jouable et jugée.

- ⚠️ **Le contenu, pas les mesures** : la taille est tenue par ses juges, on n'y touche pas.
- ⚠️ **Rien au dé** : l'intérieur se décide à ce qu'on lit dehors (standing, district, genre, empreinte), comme
  la pièce de commerce suit déjà le standing du bloc. Un tirage de plus dans le dé
  commun déplacerait toute la ville.
- ⚠️ **Un juge par règle**, qui compare l'intérieur à son extérieur (le standing de la porte, le district, le genre
  du bâtiment) pour TOUTES les portes de la ville, et qu'on fait rougir en retirant la règle.
- ⚠️ **Se regarde** : une capture dedans et dehors par genre avant de livrer, parce qu'aucun juge ne dit qu'un
  intérieur « fait pauvre ».
- ⚠️ **Après les façades**, ou avec elles ([la revue des façades](une-revue-des-facades-des-residences.md#fiche)) :
  l'intérieur suit ce que la façade dit, alors la façade doit d'abord bien le dire.
- La première vague qui s'impose : **le mur de la porte harmonisé** (il se voit dans chaque pièce, et c'est
  une règle de dessin, pas de contenu), puis les logements selon le standing (pauvre, ordinaire, cossu), en commençant par
  les maisons pauvres de la gare.

## Notes

**Vague 1, livrée le 29 sept. 2026 : le mur de la porte, harmonisé.** Deux défauts dans le même mur, vus sur la
capture du logement `nord_logement_1001` : le mur `B` d'une pièce se peignait en **toit de tôle** (le même
glyphe que dehors — et l'hiver venu, les saisons le couvraient de neige, dedans), et le mur de la porte en
**façade de brique** (`W`, `D` peints par `facade()`, comme vus de la rue).

- `Monde.entrer` donne à toute pièce qui n'a pas ses propres matériaux `MATERIAUX_DE_PIECE` = `{B, W, D :
  'piece'}` — le mécanisme des rondins du chalet (`materiaux`), qui garde les siens.
- Trois peintres (`sprites.js`) : `B@piece`, un plâtre et sa plinthe du côté du plancher (`murDePiece`) ;
  `W@piece`, la fenêtre vue de dedans (cadre blanc, rideaux tirés, la tringle) ; `D@piece`, la porte en bois et
  son chambranle — **les deux peints sur le plâtre du mur**. Un rideau de la même couleur à toutes les
  fenêtres d'une pièce (tiré par tuile, c'était bariolé).
- `varianteDeTuile` : un mur de pièce a sa plinthe là où il touche autre chose qu'un mur (`BWD`), pas un bord
  de toit entre le mur et sa fenêtre.
- Plus de neige sur les murs d'une pièce : `B@piece` ne passe pas par `Saisons.enneiger`.
- Regardé : le logement de la gare, le dépanneur, le terminus (fenêtres en haut et en bas).
- Juges (`test_interieurs_js.py`) : `test_tous_les_murs_d_une_piece_sont_du_meme_platre` (chaque pièce de la
  ville, chaque tuile de mur ; rouge sans les matériaux par défaut), `test_la_fenetre_et_la_porte_se_peignent_sur_le_platre_du_mur`
  (un faux contexte : la fenêtre et la porte commencent par le plâtre plein du mur ; rouge si la fenêtre
  repasse sur la brique).
- Pour la vague des logements selon le standing : le plâtre et le rideau sont dans `PLATRE` — un plâtre défraîchi
  chez les pauvres, une autre couleur chez les cossus, par un matériau de plus (`'piece_pauvre'`…).


**L'inventaire, le 30 sept. 2026** (sur la ville de la graine livrée : chaque porte qui s'ouvre, ce qu'on voit
dehors — le district, le standing et le genre de SA résidence ou de SA devanture — contre ce qu'on trouve dedans —
le nom, le plancher, les meubles, les niveaux ; captures dedans et dehors d'un logement par groupe) : **90 portes**,
49 commerces, 32 logements, 9 lieux faits à la main.

| Logement | District | Standing | Portes |
|---|---|---|---|
| maison | Érables | cossu | 4 |
| villa | Érables | cossu | 1 |
| plex | Faubourg | cossu / ordinaire | 1 / 3 |
| plex | Petit-Canton | cossu / ordinaire / pauvre | 2 / 10 / 5 |
| plex | Gare | pauvre | 2 |
| plex | Quais, Pointe | ordinaire | 3, 1 |

- **Les 32 logements avaient le MÊME intérieur** : « Un logement », un plancher de bois verni, un plâtre propre,
  un lit à couverture bleue, la même réserve de meubles — qu'on entre par une façade placardée de la gare, un plex
  du Canton ou la villa des Érables. C'est l'écart qui se voit à chaque porte (la capture de la gare : dehors les
  planches aux fenêtres, le grillage et le fer rouillé ; dedans un logement neuf).
- **Les commerces suivent déjà le standing** (le comptoir, les plantes : la 3e vague des quartiers) ; ils se relisent
  avec le district et le genre dans une vague à eux.
- **La villa** : sa pièce a gardé les mesures du cossu d'avant l'élargissement (6 × 5 pour une façade de 7) et un
  seul niveau pour trois étages dehors — les niveaux sont le jalon « Des étages dedans aussi » (une autre session,
  en cours) ; la villa s'y ajustera quand il sera livré.
- **Les lieux faits à la main** (la planque, la chapelle, le hangar, la fourrière…) : à relire un par un, plus tard.

**Vague 2, livrée le 30 sept. 2026 : l'habit du logement.** Le navigateur le lit DEHORS en poussant la porte
(`Monde.materiauxDuLogement` : le standing final et la villa de la résidence dont c'est la porte — les vitrines
font monter et descendre des standings après la construction, alors la pièce ne le décide pas) ; les mêmes
meubles aux mêmes places, un autre habit (`materiaux` : `B`, `W`, `D`, `t`, `l`), et l'étage du haut le garde
(l'escalier rentre par la même porte). Python ne change pas : rien de la ville ne bouge.

- **Pauvre** : un plâtre jauni, des taches d'humidité, une fissure ; un drap punaisé en guise de rideau, une vitre
  fêlée ; une porte plane éraflée et sa chaîne de sûreté ; des planches grises et usées, un bout qui manque ; le
  matelas à même le plancher sous une couverture de laine grise.
- **Cossu** : un papier peint rayé sous sa cimaise, la plinthe haute ; des tentures bordeaux à embrases d'or ; une
  porte d'acajou et sa poignée de laiton ; un parquet à chevrons ; le lit d'acajou à couverture bordeaux.
- **Villa** : des boiseries blanches à panneaux et leur filet d'or ; des tentures d'or ; la porte double blanche ;
  le marbre en damier, veiné ; le lit d'ivoire à pique d'or.
- L'ordinaire garde le plâtre de toutes les pièces, et les commerces aussi.
- Regardé : la gare (pauvre), un plex cossu du Faubourg, la villa. Une capture a figé la villa au noir — `T`
  manquait à un peintre (une exception dans le dessin fige le jeu) ; corrigée avant de livrer.
- Juges `tests/test_habit_du_logement_js.py` : chaque logement de la ville porte l'habit de sa façade (la table en
  toutes lettres), on entre pour de vrai dans son habit et l'étage du haut le garde, chaque habit a ses peintres et
  ne ressemble pas au plâtre ; cinq mutations, quatre mordent — la cinquième (seule une pièce `maison` s'habille)
  ne peut pas : aucune porte de commerce ne tombe dans la façade d'un logement.
- **Reste** : le district (un logement du Petit-Canton, des Quais, de La Shop) et le genre (le bungalow, le plex, la
  maison de pêcheur) ; la villa à sa taille et à ses niveaux (après « Des étages dedans aussi ») ; les commerces
  relus au district ; les lieux faits à la main.

**Vague 3, livrée le 30 sept. 2026 : le quartier et le genre du logement** (tranché par Martin). Toujours lu dehors
(`Monde.materiauxDuLogement`), toujours sans un dé :

- **Le quartier s'accroche au mur du fond** (une tuile sur trois qui a le plancher au sud, lue à la position) :
  au Petit-Canton la lanterne de papier rouge, le rouleau de calligraphie, le petit autel aux oranges ; aux Quais
  le filet de pêche et son flotteur, le hublot ; au Faubourg le crucifix, le calendrier du dépanneur ; aux Érables
  la photo de famille dans son cadre doré, l'horloge ; à la Gare le calendrier graisseux de la cour à scrap, le
  manteau pendu au clou ; à La Pointe l'affiche de la foire, la planche à roulettes. Chaque habit × chaque quartier
  a son peintre composé (`B@logement_pauvre~gare`…) ; la fenêtre et la porte gardent celui de l'habit — un seul
  mur.
- **Le genre se lit au plancher** : la villa, son marbre ; le bungalow (un seul étage — les maisons des Érables),
  sa moquette beige ; le plex, le plancher de son habit.
- Corrigé en passant (la vague 2 l'avait manqué) : la plinthe du côté du plancher ne venait qu'au plâtre `piece` ;
  tout mur habillé la lit maintenant (`varianteDeTuile`), avec seize bruits de position au lieu de quatre (de quoi
  varier l'objet du quartier, les taches et la fissure).
- Regardé : un plex ordinaire du Petit-Canton (les rouleaux), une maison des Érables (les horloges, la moquette),
  la gare (les manteaux au clou), les Quais.
- Juges `test_habit_du_logement_js.py` : le quartier et le genre de chaque logement de la ville (tables en toutes
  lettres), chaque quartier accroche au moins deux objets, jamais sur un mur de côté ; la variante exacte de chaque
  mur d'une vraie pièce habillée ; cinq mutations, toutes mordent.

**Vague 4, livrée le 30 sept. 2026 : les commerces au quartier.** Un commerce derrière une devanture prend l'habit
du standing de SA devanture (`Monde.materiauxDuCommerce` : le plâtre jauni et fissuré d'une boutique pauvre, le
papier rayé d'une boutique cossue) et, au mur du fond, un objet de COMMERCE de son quartier — jamais ce qu'on
accroche chez soi : au Petit-Canton la lanterne, le chat porte-bonheur à la patte levée, l'autel ; aux Quais la
bouée de sauvetage, le tableau des marées ; au Faubourg le calendrier, le fanion de hockey du quartier ; aux Érables
l'horloge, l'affiche jaune des spéciaux ; à La Shop le panneau de sécurité, l'horloge pointeuse ; à la Gare et aux
Friches le panneau de sécurité, le calendrier graisseux ; à La Pointe l'affiche de la foire, la planche à roulettes.
La fenêtre reste une VITRINE nue et la porte une porte de bois à vitre — pas de drap punaisé ni de chaîne de sûreté
dans une boutique. Un lieu fait à la main (sans devanture) garde son plâtre, et une pièce qui n'est pas un commerce
(le phare derrière sa devanture) n'en prend jamais l'habit.

- Regardé : la pharmacie pauvre des Quais, une boutique du Petit-Canton, le Rialto de La Shop.
- Juges `test_habit_du_logement_js.py` : chaque commerce de la ville porte l'habit de sa devanture et l'objet de son
  quartier (tables en toutes lettres), une boutique n'a ni drap ni chaîne, le crucifix n'y est jamais ; cinq
  mutations, toutes mordent.
- Au passage : la suite complète de la vague 3 avait 24 rouges ; rejoués sur le commit d'avant, les neufs
  (`test_defis_graduels_js`, `test_garages_ou_l_on_entre_js`, `test_mantes_defi_js`, `test_crime_d_autrui`…)
  rougissent pareil sans elle.

**Vague 5, livrée le 30 sept. 2026 : les lieux faits à la main.** Les neuf, dedans et dehors (captures) : quatre
tombaient sur le plâtre et les rideaux rouges d'un salon, qui est l'habit par défaut d'une pièce. Chacun a maintenant
le sien, dans sa pièce (`materiaux`, `carte._piece`) — un seul mur, la plinthe du côté du plancher :

- **La chapelle Sainte-Anne** (l'île) : la chaux, les vitraux en arc et leurs plombs, la porte cloutée, les dalles
  de pierre, les bancs d'église (le dossier et l'assise, d'un banc à l'autre), l'autel nappé, son antependium et
  ses cierges.
- **Le hangar sans nom** (l'île) et **le bureau du ferrailleur** (la gare) : la tôle ondulée et sa rouille qui
  coule, la fenêtre grillagée, la porte de tôle et sa barre ; le béton taché d'huile du hangar.
- **La fourrière municipale** : un bureau de la ville — le vert à deux tons, les stores vénitiens à demi baissés,
  la porte de métal à hublot.
- Les cinq autres se lisent déjà : la planque de Rocco (un logement), le kiosque de Mme Thibodeau, Électronique
  Turcotte, la pharmacie et la criée des Quais (des commerces sans devanture : le plâtre des boutiques).
- Juge `test_les_lieux_faits_a_la_main_portent_leur_habit` (la table en toutes lettres ; on entre dans la chapelle
  et chaque mur lit sa plinthe) ; quatre mutations, toutes mordent.
- **Reste** au jalon : la villa à sa taille et à ses niveaux, après « Des étages dedans aussi ».

**Vague 6, livrée le 1er oct. 2026 : la villa à sa taille et à ses niveaux** (après « Des étages dedans aussi »,
atterri le matin même). La pièce de la villa avait gardé les mesures du cossu d'avant l'élargissement (6 × 5 pour
une façade de 7) et un seul niveau. `villas.poser` la refait maintenant sur la ville finie (`_refaire_la_piece`) :
les mesures du bâtiment ÉLARGI (`carte.mesures_de_la_part` — la façade entière, la profondeur du toit), la même
variante (le numéro de la pièce : rien n'est tiré), la `vitrine` de la porte élargie avec elle (la part de bâtiment
que le juge des mesures relit) ; ses étages d'avant partent, et `etages.monter`, qui passe après, empile ceux que la
façade peint. Mesure : la villa des Érables ouvre sur 9 × 5 (son plancher de 7 × 3) et son étage.

- Juges `test_villas.py` : la villa ouvre sur une pièce à sa taille et chaque niveau a les mesures du rez ; « seule
  l'herbe devient villa » tolère que changent les portes et les pièces des villas, et rien d'autre ;
  `test_carte.test_la_piece_a_les_mesures_de_son_batiment` les tient pour toute la ville. Trois mutations, deux
  mordent — la troisième (retirer les étages d'avant) ne peut pas : aucun cossu devenu villa n'avait d'étage dans
  la ville du témoin.
- Regardé : la villa des Érables, au rez (le marbre, le lit d'ivoire, la cuisine, l'escalier, les horloges).

**Le jalon est livré** : six vagues — le mur de la porte, l'habit du logement, le quartier et le genre, les
commerces, les lieux faits à la main, la villa à sa taille.
