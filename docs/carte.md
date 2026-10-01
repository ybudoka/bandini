# La carte de Baie-des-Brumes — inventaire

> Source de vérité : `app/carte.py` (`DISTRICTS`, `SPECIAUX`, `INTERIEURS`,
> `BARRIERES`), `app/pietons.py` (`CATALOGUE`, `GANGS`), `app/missions/__init__.py`
> (`PERSONNAGES`), `app/vehicules.py` (`CATALOGUE`).
>
> ⚠️ **Ce document est un instantané.** La carte est générée depuis le code —
> c'est `app/carte.py` qui fait foi. **Toute modification de la carte, des
> districts, des bâtiments, des personnages, des véhicules ou des gangs DOIT
> être répercutée ici.** Voir la consigne correspondante dans `docs/reprendre-le-travail.md`.

La ville tient sur **une seule grille de blocs** (20 colonnes × 12 rangées),
rebâtie à l'ouverture par `generer(plan, graine)`. Rien n'est régulier : chaque
colonne a sa largeur, chaque rangée sa hauteur, et les superblocs (`<` `^`)
fusionnent des îlots en effaçant la rue qui les séparait.

**Sous la grille, depuis le 21 sept. 2026 : l'aéroport** (`app/aeroport.py`). La
carte fait 419 × 304 tuiles au lieu de 419 × 224 : quatre-vingts rangées d'eau (le
large) et une île **dessinée** sous La Pointe, posée en dernier et sans un dé — la
ville d'au-dessus n'a pas bougé d'une tuile.

**Autour de la grille, depuis le 21 sept. 2026 : le relief**
(`app/relief.py`). La carte fait 459 × 304 tuiles au lieu de 419 × 304 : quarante
colonnes de montagnes à l'est (posées après la dernière rue, sans toucher la
trame — le même principe que l'aéroport au sud), et une ligne de falaises qui
referme le large au sud de l'aéroport. Infranchissable partout (`solide 1`) :
ni à pied, ni en char, ni à la nage.

**Au-dessus de la grille, depuis le 27 sept. 2026 : la bande nord** (`app/nord.py`). La
carte fait 459 × 414 tuiles au lieu de 459 × 304 : **toute la ville descend de 110
rangées** (`nord.DECALAGE_NORD`), en tout dernier dans `generer` et sans un dé, et une
deuxième ville, bâtie par le même chantier sur sa trame (`TRAME_NORD` : les mêmes colonnes,
ses rangées) et sa graine (`GRAINE_NORD`), se colle au-dessus : les Friches, la place du
Petit-Canton, la Gare de triage. Elle se coud au boulevard qui bordait la ville au nord : ses
rues nord-sud y débouchent, et les croisements gagnent leur bras nord.
⚠️ **Une clé neuve dans la carte = une ligne dans `nord.DECALAGES`** : la translation connaît
chaque clé de `generer` et dit comment elle descend (un objet `{x, y}`, une paire `[x, y]`, des
pixels) ; une clé qu'elle ne connaît pas fait échouer la génération en la nommant.
⚠️ Le navigateur lit DEUX trames (`grille`, qui commence à `y0 = 110`, et `grille_nord`) ;
les blocs de carte écrivent leur passage en coordonnées de la ville d'avant, et
`blocs.passage_en_ville` les fait descendre. Une partie écrite avant descend avec la ville
(`Sauvegarde.completer`, `decalage_nord`).

---

## 1. Les districts

Cinq quartiers habités, plus la baie. Chaque district porte un **gang**, un
rythme de vie (matin/soir/nuit) et ses propres bâtiments garantis.

| District | Slug | Gang | Brume | Notes |
|---|---|---|---|---|
| **Les Friches** | `friches` | Les Chevreuils | ➖ | La bande nord, au-dessus des Érables (`nord.py`) : herbes hautes, sentiers de terre battue, terrains vagues clôturés, carcasses d'autos. Aucune porte. |
| **Le Petit-Canton** | `canton` | Les Mantes | ➖ | La bande nord, au-dessus du Faubourg : une **rue principale** commerçante nord-sud jusqu'à la couture, des logements tout autour, la **place du marché** au cœur (étape 2, vague A). Ses enseignes sont à lui (`devantures.COMMERCES["canton"]` : JARDIN DE JADE, HERBORISTE CHAN, NOTAIRE LEUNG…), et chaque commerce porte une **plaque verticale** rouge et or à deux idéogrammes (`devantures.IDEOGRAMMES`). Au nord de la place, le **casino du Dragon d'or** (`nord_casino`, `casino.py`) : une façade de trente-deux tuiles, sa marquise de néon, son portier ; dedans, dix-huit machines à sous et quatre vidéopokers, cinq tables, Irène Lam au bout du bar (le donneur du quartier) — et, derrière une porte gardée qu'ouvre c01, l'escalier du **tripot du Pouce** (`nord_tripot`, `tripot.py`) : la barbotte aux dés pipés, sous la grande salle. Après c04, le tripot a **changé de mains** (`tripot.REPRISE`) : le Pouce et ses gros bras sont partis, le vieux Chan tient la barbotte pour Irène, les dés sont blancs. Au nord-ouest, à l'écart de la rue principale, l'**ÉCOLE LA MANTE** (`ecole_mante`, `mantes.py`) : le territoire des Mantes est le coin de leur école — on y passe à mains nues, et un Mante vient quand même te défier. Après c04, le vieux maître Victor Tam, revenu de Floride, se tient dans sa salle ; après c08, l'école **rouvre ses cours** (`mantes.REPRISE`) : ses élèves font face au maître, beaucoup moins de Mantes traînent dehors, et le gang, calmé, ne défie plus personne. Sa musique, à pied : `amb_canton`, « Lanternes du Petit-Canton » (guzheng, erhu et dizi sur une nappe douce). |
| **La Gare de triage** | `gare` | Les Boulonneux | ➖ | La bande nord, au-dessus de La Shop : à l'ouest, la **cour à scrap** des Boulonneux (une seule voie au nord — celle du **train**, qui y a sa gare centrale, au rang 6 : il vient des Friches au sol, passe le Petit-Canton **sur son viaduc**, et entre dans le portail de son tunnel, dans la falaise de l'est, `app/train.py` — puis une cour de barbelé : rangées de piles de carcasses, de cubes de ferraille et de pneus entre des allées, la grue à aimant) et le **bureau du ferrailleur** (`nord_ferrailleur`, une pièce) ; au sud, des hangars. À l'est, le **bidonville** (`t` : cabanes de tôle `{` et de planches `}`, barils en feu, linge, pneus sur la tôle) et, dessous, des **maisons pauvres** (standing `-`), dont quelques logements se visitent (`nord_logement_1001`…, comptés à part) ; on n'entre dans aucune cabane. |
| **Le Faubourg** | `faubourg` | Les Cravates | ✅ | Centre-ville, le plus peuplé (34 piétons). On y débarque de l'autobus. La cour des Cravates au centre. |
| **Les Érables** | `erables` | Les Chevreuils | ➖ | La banlieue cossue : maisons détachées, deux parcs, un dépanneur. |
| **La Shop** | `shop` | Les Boulonneux | ➖ | L'industriel : entrepôts 2×2, presque pas de rues, désert la nuit. |
| **Les Quais** | `quais` | Les Morues | ✅ | Le port : hangars longs, une rangée de quais, l'eau au sud. |
| **La baie** | `baie` | — | ➖ | Pas un quartier : l'eau (un bloc fusionné de 7×6). |
| **La Pointe** | `pointe` | Les Skateux | ➖ | Le parc au bout de la ville, coupé par un chenal de 24 tuiles — un pont, la foire, et au sud le pont inachevé de l'aéroport. |
| **Le large** | `large` (zone) | — | ➖ | Pas un district : l'eau que la carte a gagnée au sud (district `baie`), personne n'y naît. |
| **L'aéroport** | `aeroport` (zone) | — | ➖ | Pas un district de la trame : une île dessinée (`aeroport.py`), clôturée de barbelé, **fermée** pour les missions à venir. Deux agents : ce n'est pas un refuge. |

---

## 2. Les bâtiments garantis (`SPECIAUX`)

Un bâtiment par majuscule du plan de district. Chacun a un **intérieur**
dessiné à la main (sauf exceptions), et appartient à une **famille de lieu**
(qui donne sa couleur sur la carte).

| Glyphe | Bâtiment | Slug | Intérieur | Famille |
|---|---|---|---|---|
| `T` | Terminus Baie-des-Brumes | `terminus` | ✅ | transport |
| `M` | Chez Gus (armurerie) | `armurerie` | ✅ | magasin |
| `A` | Boutique Rosa (vêtements) | `vetements` | ✅ | magasin |
| `G` | Garage Rocco Bandini | `garage` | ✅ | tes_places |
| `K` | La planque de Rocco | `planque` | ✅ | tes_places |
| `P` | Poste de police | `poste` | ✅ | service |
| `H` | Hôpital de Baie-des-Brumes | `hopital` | ✅ (+ étage `hopital_soins`) | soins |
| `B` | Bar Le Brouillard | `bar` | ✅ | tes_places |
| `C` | Casse-croûte du Faubourg | `casse_croute` | ✅ | manger |
| `D` | Dépanneur Chez Ti-Paul | `depanneur` | ✅ | magasin |
| `L` | Hôtel Bandini | `hotel` | ✅ (+ `hotel_chambre`) | tes_places |
| `N` | Cantine des Quais | `cantine` | ✅ | manger |
| `U` | Usine Prévost | `usine` | ✅ | travail |
| `V` | Le phare de La Pointe | `phare` | ✅ | repere |
| `Y` | Fourrière municipale | `fourriere` | ✅ | service |
| `E` | Électronique Turcotte | `electronique` | ✅ | service |

**Intérieurs secondaires** (hors `SPECIAUX`, entrés par une porte dédiée) :
`kiosque` (Mme Thibodeau), `hopital_soins`, `hotel_chambre`, `metro_quai`,
`metro_rame`.

**Les carrosseries** (des garages où l'on entre, 21 sept. 2026) : une par district, posées
sur la ville finie par `_Chantier.poser_les_carrosseries` — un commerce sans porte dont
l'enseigne devient CARROSSERIE, PEINTURE AUTO ou PEINTURE MINUTE (`devantures.CARROSSERIES`),
un rideau de deux tuiles et une baie de deux rangées sous le toit. Point `carrosserie_<district>`,
famille `service`, sans intérieur : on y entre en char, on en ressort repeint et la police à
zéro (100 $ + 50 $ par étoile, `economie.CARROSSERIE`). Ville livrée : Faubourg, La Shop, Les
Quais — pas Les Érables (leurs commerces se visitent tous). Le rideau de Ti-Guy s'entre aussi :
son menu s'ouvre à l'abri.

**Le DOJO DION** (le dojo du quartier, 26 sept. 2026) : la pièce d'un commerce visitable du
Faubourg, reprise sur la ville finie par `_Chantier.poser_le_dojo` — la plus au nord du district,
sans un dé, aux mêmes mesures (au moins 9 × 5). Son intérieur (`piece_de_dojo`) : les casiers du
vestiaire, le sac de frappe (`@`) et le mannequin de bois (`%`) au fond, le TATAMI (`A`) au milieu,
le comptoir de Mireille Dion (point `cours`) et Kevin, l'élève partenaire (`eleve`). Point `dojo`,
famille `service`. L'ancien SALON MIREILLE du Faubourg s'appelle SALON LOUISE.

**L'ÉCOLE LA MANTE** (l'école rivale, 29 sept. 2026, `app/mantes.py`) : la pièce d'un commerce du
Petit-Canton (c'était la CAISSE POP), reprise par `nord.poser` sur la carte finie et sans un dé — la plus
au nord des portes de commerce à l'ouest de la rue principale, au moins 8 × 5. Dedans (`piece_d_ecole`) :
un plancher de bois nu, deux mannequins de bois (`%`), le sac (`@`), les casiers des élèves (`k`, le point
`fouiller`, **gardé** : les Mantes présents te tombent dessus), un banc de chaises, et trois élèves
(`mante`). Point `ecole_mante`, famille `service`. Autour, le territoire des Mantes (zone `mantes`).

**LA CAISSE POPULAIRE** (le casse de l'arc X, 1er oct. 2026, `app/caisse.py`) : la caisse des ouvriers de **La
Shop**, où le fourgon dépose la paie de l'usine Prévost — la pièce d'un commerce ordinaire (LIQUIDATION, à la vraie
graine), reprise **en dernier** sur la ville finie, sans un dé : la plus grande pièce d'une famille qui garde une
autre porte, dont l'enseigne tient « CAISSE POP » et qu'aucune mission ne lit par son nom. La ville d'avant est la
même, clé par clé (`test_caisse.py`). Dedans (`piece_de_caisse`, son habit `caisse` : la boiserie brune, le plâtre
crème, le prélart beige) : le **comptoir des guichets** d'un mur à l'autre et sa porte battante, la **voûte** d'acier
au fond (un bloc de deux sur deux, point `voute`), le **bureau du gérant** derrière une cloison (monsieur Lemire,
`gerant`), la salle d'attente ; deux caissières, Fernand le vigile (`vigile`), des clients. Point `caisse_pop`,
famille `service`. Pas d'étages : une pièce faite main n'en monte pas.

**Les concessionnaires** (28 sept. 2026, `app/concessionnaires.py`) : **Prestige Automobiles**, bâti sur
la moitié sud du plus grand stationnement cossu des Érables (un salon de toit d'ardoise, façade vitrée) ;
la moitié nord, ses cases `^` telles quelles, est le lot — huit chars neufs (sport, luxe, VUS de luxe,
berline, familiale), au prix du catalogue, l'alarme sur tous. **Chez Ti-Pout — Autos usagées**, dans les
Friches : une cour de poussière de pierre grillagée contre le boulevard, une trouée de cinq tuiles au sud,
une roulotte-bureau (une fenêtre placardée) et sept minounes délavées à 60 % de vie, à 40 % du prix.
Tous deux sur la ville finie, sans un dé ; point `concession` au comptoir (`lot` : le slug), famille
`magasin`. Les chars naissent hors champ (`Vehicules.majLotsDeConcession`) ; payés, ils sont à toi
(`aToi`) ; vendue, la place se regarnit le lendemain (`partie.concession`).

**Les bungalows avec garage** (2e vague, 21 sept. 2026) : cinq logements de banlieue
(`bungalow_1`…), posés sur la ville finie par `_Chantier.poser_les_garages_de_bungalows` — un
rideau, une baie sous le toit, une entrée asphaltée jusqu'au trottoir. Pas sur la carte. On y
entre en char et on s'y cache : rien ne se paie ni ne se repeint, la police ne voit pas sous le
toit, les étoiles tombent comme hors de vue. Ville livrée : les cinq aux Érables.

**Lieux sans intérieur propre** (points de commerce générés sur les parcelles) :
`logement` (logements procéduraux, un par habitation), et les devantures de
quartier (commerces tirés par famille).

### Familles de lieu (couleurs sur la carte / blips)

| Famille | Couleur | Libellé |
|---|---|---|
| `tes_places` | `#e8b33c` | TES PLACES |
| `magasin` | `#8ad26a` | MAGASINS |
| `manger` | `#e8925a` | MANGER |
| `service` | `#6f9fd8` | SERVICES |
| `soins` | `#d86f7f` | SOINS |
| `transport` | `#cdc6e6` | TRANSPORT |
| `travail` | `#9a8fb0` | TRAVAIL |
| `repere` | `#7fd4d0` | REPÈRES |

---

## 3. Les barrières (`BARRIERES`)

Des obstacles à condition : un mur qui s'ouvre selon l'avancement, l'heure ou
un paiement.

| Barrière | Slug | Bloque | Condition |
|---|---|---|---|
| Le pont de La Pointe | `pont` | véhicule | après **m2** |
| La guérite de la fourrière | `fourriere` | véhicule | payer (`fourriere`) |
| La cour de l'usine Prévost | `usine` | piéton + véhicule | **de jour** |
| L'arche de la foire | `foire` | piéton + véhicule | payer le billet (à la journée) — ou la forcer, une étoile. Le grillage autour ne s'enjambe pas (`¦`, 30 sept. 2026) ; devant, sur le trottoir, la file attend dans son serpentin de câbles (`file_de_foire`) |
| Le pont de l'aéroport | `pont_aeroport` | piéton + véhicule | après **a01** (pas encore écrite) — la barricade se défonce et s'enjambe, sans étoile, mais le tablier s'arrête au-dessus de l'eau : trente-deux tuiles de chantier et six piles |
| La guérite de l'aéroport | `aeroport` | piéton + véhicule | après **a02** (pas encore écrite) — ne se force pas |

**Les serrures des blocs** (l'infiltration, 28 sept. 2026) : un bloc de carte peut avoir ses propres
barrières (`serrures` dans sa fiche, `app/blocs/villa.py`), exportées au même format et lues par le même
`Monde.barriereFermee` — condition `objet`, pleines, elles ne se forcent pas. La villa du maire en a deux :
la **porte de service** (`cle_villa`, la clé volée au garde du jardin, v01) et la **chambre forte** du
sous-sol (`code_voute`, le code du terminal piraté, v03).

---

## 4. Les véhicules (`app/vehicules.py`)

| Slug | Véhicule | Classe | Places | Notes |
|---|---|---|---|---|
| `auto` | Berline | auto | 4 | La référence (vitesse 100 %). |
| `taxi` | Taxi | auto | 4 | Boulot taxi, radio. |
| `moto` | Moto | moto | 2 | Éjecte, boulot pizza. |
| `velo` | Vélo | velo | 1 | Roule à la bordure (tassé vers le trottoir) et se range à gauche pour tourner à gauche ; de temps en temps un bout de trottoir, ou la traversée d'un parc par ses allées, au pas et en sonnant (`TRAFIC["velo"]`). |
| `police` | Auto-patrouille | auto | 4 | Sirène, alarme, radio 10-4. |
| `camion` | Camion | camion | 2 | |
| `autobus` | Autobus | camion | 12 | |
| `ambulance` | Ambulance | auto | 3 | Sirène, soigne, boulot ambulance. |
| `creme_glacee` | Camion de crème glacée | auto | 2 | Ne roule pas dans le trafic : garé devant le dépanneur des Érables ; boulot tournée, ritournelle, discret (la chaleur monte moitié moins). |
| `asphalte` | Camion d'asphalte | camion | 2 | Ne roule pas dans le trafic : garé devant la fourrière municipale ; boulot voirie (boucher les nids-de-poule, pour de bon). |
| `motoneige` | Motoneige | moto | 2 | Ne roule pas dans le trafic : l'hiver seulement (la saison du calendrier), deux garées dans une rue des Érables ; pleine vitesse dans la neige, sur la glace et hors des rues, 45 % sur l'asphalte ; la course des bois de La Pointe. |
| `quatre_roues` | 4 roues | moto | 2 | Ne roule pas dans le trafic : trois garés à côté des cabanons des Friches, le tien au chalet du rang, nés à l'approche ; plein régime sur la terre (herbe, friche, sable), là où une auto garde deux tiers de son allure ; stable — on n'en tombe qu'à 4,2 px par image, au lieu de 2,6 pour une moto ; la course des Friches (huit fanions, 60 s). |
| `remorqueuse` | Remorqueuse | camion | 2 | |
| `pelleteuse` | Pelleteuse | camion | 1 | « Ça travaille » : ne naît jamais dans la rue (`frequence` 0), sort du décor du chantier quand on monte dedans. Le char le plus lent du catalogue (12 km/h, y compris les bateaux) et le plus lourd de la rue ; défonce au pas (le seuil se règle sur sa vitesse) ; un agent à pied la rattrape, et c'est voulu. |
| `sport` | Coupé sport | auto | 2 | Rare. |
| `luxe` | Berline de luxe | auto | 4 | Rare. |
| `cabriolet` | Cabriolet rose | auto | 2 | Rare (Faubourg, La Pointe). Le plus rapide des chars à quatre roues, sous la moto ; menée à la vue de tous par la conductrice (`au_volant`), qui descend si on la vole. Ne se gare jamais. |
| `bateau` | Chaloupe | bateau | 4 | Hors trafic : amarrée contre une rive bâtie (`carte.amarrages`). Deux silhouettes, la barre et la console. |
| `chalutier` | Chalutier | bateau | 3 | Hors trafic : deux à quai autour du cargo (`navires.py`). Plus lent et plus lourd que la chaloupe ; la corne. |
| `porte_conteneurs` | Porte-conteneurs | bateau | 2 | Hors trafic : un seul, au quai du cargo (`navires.py`). Dix tuiles, le plus lourd du parc (la pelleteuse du chantier, hors trafic elle aussi, la bat en lenteur) ; la corne. |
| `vedette` | Vedette de police | bateau | 2 | Hors trafic : la poursuite la fait naître, hors champ sur l'eau, quand on est recherché dans une coque (`vedette.js`). La coque de la chaloupe, plus vive qu'elle, bleu nuit, la rampe rouge et bleue sur son arceau ; elle arraisonne bord à bord. |

---

## 5. Les personnages de l'histoire (`missions.PERSONNAGES`)

Ceux qui donnent les missions et font vivre le fil, avec leur position et leur
voix. Leur histoire, leur personnalité et leur façon de parler et de se présenter : une fiche
chacun dans [docs/personnages/](personnages/README.md).

| Slug | Nom | Voix | Où | S'en va |
|---|---|---|---|---|
| `ti_guy` | Ti-Guy | Felix Tabarnak | porte:terminus | après m1 |
| `thibodeau` | Madame Thibodeau | Julia | porte:kiosque | — |
| `marco` | Marco | Québec Tremblay | porte:garage | — |
| `bouchard` | Sergent Bouchard | Khaivan | point:sergent | — |
| `josee` | Josée | Jeanne Mance | point:contact | — |
| `civil` | Le client | Alexandre | — (dans le taxi) | — |
| `passant` | Un passant (une petite job) | Felix (la voix des passants) | — (dans la rue : `jobs.js` le fait naître) | — |
| `passante` | Une passante (une petite job) | Amélie (la voix des passantes) | — (dans la rue : `jobs.js` la fait naître) | — |
| `narrateur` | Le Clairon de la Baie | annonceur centre d'achat 1 | — | — |
| `tipaul` | Ti-Paul Gagnon | Québec Tremblay | porte:depanneur | — |
| `lulu` | Lucienne « Lulu » Pelletier | Claudia | point:lulu | — |
| `raymonde` | Raymonde Fortin | Nadine | porte:usine | — |
| `ovila` | Ovila Saint-Onge | annonceur centre d'achat 1 | point:ovila | — |
| `mo` | Le Grand Mo | Alexandre Boutin | porte:terminus | — |
| `fern` | Fern Côté | Premium Male teacher (Adam) | porte:terminus | — |
| `mado` | Mado | Caroline | porte:casse_croute | — |
| `gege` | Gérard « Gégé » Morin | Alexandre Boutin | porte:cantine | — |
| `xavier` | Xavier | Premium Male teacher (Adam) | porte:depanneur | — |
| `lachance` | Dr Lachance | Patrick | point:lachance | — |
| `gus` | Gus Lévesque | Khaivan | porte:armurerie | — |
| `rosa` | Rosa Di Meo | Amélie | porte:vetements | — |
| `ginette` | Ginette | Jeanne Mance | porte:hopital | — |
| `gilles` | Gilles Thériault | Patrick | porte:fourriere | — |
| `bonimenteur` | Le Bonimenteur | Léo | foire (l'arche) | — |
| `mireille` | Mireille Dion | Marie Line | point:cours (le DOJO DION) | — |
| `jeanne` | Sœur Jeanne | Julia | porte:chapelle (l'Île-aux-Corneilles) | — |
| `leo` | Léo Cyr | Alexandre | porte:hangar_ile (l'Île-aux-Corneilles) | — |
| `norbert` | Norbert | Martin Dupont Intime | point:norbert (le hall de l'Hôtel Bandini) | — |
| `irene` | Irène Lam | Meera | point:irene (le bout du bar du Dragon d'or, au Petit-Canton) | — |
| `pouce` | Réal « le Pouce » Vachon | Callum - Husky Trickster | — (on ne l'entend qu'en se sauvant, c04) | — |
| `cindy` | Cindy Boivin | Ruby Roo | porte:cantine (la Brume des Quais — partie après q05, `parti_apres`) | — |
| `diane` | Diane Larivière | Riya Rao | porte:depanneur (après e01, `arrive_apres`) | — |
| `beaulieu` | Mme Thérèse Beaulieu | Caroline | porte:depanneur (après m6, `arrive_apres` ; Biscuit, son chien, à ses pieds après e03) | — |
| `jo` | Jo Bellemare | Omar J | porte:depanneur (entre e01 et e04) | — |
| `bilodeau` | Roméo Bilodeau | Santa | porte:phare (après p01) | — |
| `zed` | Zacharie « Zed » Lemieux | Lutz | porte:phare (après p02) | — |
| `trappeur` | Armand, le Trappeur | George | porte:phare (après p01) | — |
| `tiloup` | Ti-Loup Ferraille | Chris | porte:fourriere (après s01) | — |
| `boulon` | Marcel « Gros-Boulon » Boulanger | Roger | porte:fourriere (après s02) | — |
| `prevost` | Réjean Prévost | Roland Lescalde | point:prevost (son bureau, dans l'usine — après s10) | — |
| `maire` | Le maire Réal Tanguay | Eric - Smooth, Trustworthy | point:maire (la chambre de l'Hôtel Bandini, à l'étage — entre m97 et m98) | — |
| `maitre` | Victor Tam | Luca - Storyteller | point:maitre (sa salle de l'ÉCOLE LA MANTE, au Petit-Canton — une fois revenu de Floride, `arrive_apres: c04`) | — |
| `sal` | Salvatore « Sal » Ferraro | Pascal — Voix québécoise chaleureuse | point:sal (sa chaise de barbier, au milieu du terminus — après m6) | — |
| `roy` | Inspectrice Claudine Roy | Kasandra - Natural Quebecer UGC ad | point:roy (son bureau, au milieu du poste — après r01) | — |

⚠️ **`ou: "foire"` est un lieu neuf** (22 sept. 2026) : le seul personnage posé DANS l'enceinte de la
foire, vivant à l'arche — `histoire.js::lieuFoire`/`poserDonneurFoire` trouvent sa position dans la
barrière `"foire"` déjà exportée (même patron que `lieuPont` pour le pont de La Pointe), sans toucher
`app/carte.py`. Contrairement à un donneur `point:`, il hèle et se retrouve par `retourner`.

---

## 6. Les gangs (`app/pietons.py`, `GANGS`)

Un par district habité. Ils ne naissent que sur leur territoire (fréquence 0
hors de leur zone).

| Gang | Slug | Piéton | District | Membres | Hostile |
|---|---|---|---|---|---|
| Les Cravates | `cravates` | `cravate` | faubourg | 8 | si arme sortie |
| Les Morues | `morues` | `morue` | quais | 8 | si arme sortie |
| Les Chevreuils | `chevreuils` | `chevreuil` | erables | 6 | si arme sortie |
| Les Boulonneux | `boulonneux` | `boulonneux` | shop | 9 | **toujours** |
| Les Skateux | `skateux` | `skateux` | pointe | 6 | si arme sortie |
| Les Mantes | `mantes` | `mante` | canton (leur zone : le coin de l'ÉCOLE LA MANTE) | 7 | si arme sortie — et **chez eux, même à mains nues** : un Mante qui te voit de près vient te défier, une réplique en bulle (`mantes.PROVOCATION`) ; ils se battent avec les pieds, les projections, la parade (`mantes.COMBAT`) |

---

## 7. Les piétons (`app/pietons.py`, `CATALOGUE`)

La foule anonyme, les sortes posées, et les gens d'intérieur. `frequence`
= poids de naissance aléatoire ; `0` = jamais au hasard (posé par un système).

### La foule (naissent partout, sauf `districts` restreint)

| Slug | Nom | Districts |
|---|---|---|
| `passant` / `passante` | Passant·e | — |
| `ouvrier` | Ouvrier | — |
| `ado` | Ado en planche | — |
| `dame` | Dame du Faubourg | faubourg |
| `docker` | Débardeur | quais |
| `banlieusard` | Banlieusard | erables |
| `machiniste` | Machiniste | shop |
| `promeneur` | Promeneur de chien | pointe |
| `itinerant` | Itinérant | — |
| `livreur` | Livreur | — |
| `enfant` | Enfant (intouchable) | — |
| `mere` | Mère avec son petit | — |

### Les sortes posées (fréquence 0 — posées par un système)

| Slug | Nom | Où |
|---|---|---|
| `baigneur` / `baigneuse` | Baigneur·se | plages |
| `racoleuse` | Fille de la Brume | bar/port, la nuit |
| `conductrice` | Dame au cabriolet | au volant du cabriolet rose — jamais à pied avant qu'on la vole |
| `vendeur` | Marchand ambulant | comptoirs |
| `mascotte` | Mascotte (ours) | foire (La Pointe) |
| `mascotte_bleue` | Mascotte (bleue) | foire (La Pointe) |
| `mascotte_rose` | Mascotte (rose) | foire (La Pointe) |
| `homme_sandwich` | Homme-sandwich | postes de réclame, le jour |
| `musicien` / `amuseur` / `jongleur` / `echassier` | Amuseurs | faubourg |
| `exhibitionniste` | L'homme au manteau | — (la police l'arrête) |
| `contractuelle` | Contractuelle | faubourg, shop |
| `touriste` | Touriste | quais, pointe |
| `ivrogne` | Ivrogne | quais, faubourg — et à 3 h, en grappe devant chaque bar (le last call) |
| `jogger` | Joggeuse | erables, pointe |
| `facteur` | Facteur | erables, faubourg |
| `crieur` | Crieur de journaux | faubourg, shop (le jour) |
| `camelot` | Camelot du _Clairon_ (lance le journal sur les perrons) | erables, faubourg (à l'aube) |
| `laveur` | Laveur de vitres | shop, faubourg |
| `pickpocket` | Pickpocket | faubourg, quais |
| `enfant_velo` | Enfant à vélo (casqué, intouchable) | erables, pointe, faubourg — le jour, sur le trottoir et dans les parcs seulement (`ENFANTS_A_VELO`) |

### Les gens d'intérieur (fréquence 0 — posés derrière une porte)

| Slug | Nom | Où |
|---|---|---|
| `commis` | Commis | derrière chaque caisse |
| `soignante` | Infirmière | hôpital |
| `malade` | Malade | lits de l'hôpital |
| `avocat` | Me Desjardins | table du fond, Le Brouillard |
| `mante` | Une Mante | l'ÉCOLE LA MANTE : trois élèves qui s'entraînent (l'archétype du gang, `pietons.py`) |
| `gerant` | M. Lemire | le gérant de la CAISSE POPULAIRE, à son bureau de chêne (le corps du commis, veston brun, cravate et lunettes, `entites.archetypeDedans`) |
| `vigile` | Fernand | le vigile de la CAISSE POPULAIRE, près de la porte (le corps du garde, sa matraque) — il salue un livreur, il reconnaît les autres le jour du coup |
| `eleve` | Kevin | le DOJO DION : au sac, et sur le tatami pendant une leçon (le corps du commis en kimono blanc, `entites.archetypeDedans` — pas un archétype de `pietons.py`) |
| `policier` | Agent | patrouille (posé par `police.js`) |
| `garde` | Garde de sécurité | vigile privé de l'infiltration, posé à la main par une mission (`Police.creerAgent(x, y, etat, 'garde')`) |
| `gardien` | Gardien du lot | grille de la fourrière |
| `matelot` | Matelot | les gars de Sven : ne naît jamais dans la foule (fréquence 0), seulement quand une mission l'envoie (`tuer` avec `pieton: "matelot"`, q13) |

---

## 8. Les points d'intérêt et zones

- **Zones nommées** : rectangles de districts, territoires de gang (`cravates`,
  `morues`, `chevreuils`, `boulonneux`, `skateux`, `mantes`), port, etc.
- **Rampe / Grand Saut** : le tremplin du défi « Le Grand Saut » (`ELAN_RAMPE`).
- **Foire** : les trois jeux d'adresse (`galerie_tir`, `marteau_force`,
  `peche_canards`) — un par kiosque, joués à pied.
- **Plages** : où naissent les baigneurs.
- **Frénésies** (`frenesies.py`) : huit crânes cachés, un par district de terre — dans une ruelle (la friche aux Friches, l'herbe à la Gare de triage, qui n'ont pas de ruelle), près de la cour de la gang visée. Les Cravates au pistolet (Faubourg), les Mantes à la carabine (Petit-Canton, « Kung-fu contre carabine »), les Chevreuils à la batte (Érables) et à la mitraillette (Friches), les Morues au fusil (Quais), les Skateux au couteau (La Pointe), les Boulonneux au Molotov (la Gare de triage), et des chars au Molotov à la Shop.
- **Cartes de hockey** (`collectionner.py`) : quarante cartes de la Ligue de Baie-des-Brumes (1974-75), cinq par district de terre — les Castors du Faubourg, les Seigneurs des Érables, les Boulons de la Shop, les Goélands des Quais, les Phoques de La Pointe, les Chardons des Friches, les Dragons du Canton, les Aiguilleurs de la Gare —, chacune dans un recoin (le fond d'une ruelle, un coin entre deux murs, le bout d'un quai, une friche entre deux cabanes) ; elles voyagent sur `/api/collections`, pas dans la carte.
- **Bebelles** (`collectionner.py`, vague 3) : douze curiosités québécoises dans les endroits durs — la bouteille à la mer au bout de l'Île-aux-Corneilles, le cendrier de l'Expo 67 au fond de l'aéroport (on y saute le trou du pont), la raquette en babiche au fond du rang, les lunettes 3D derrière l'écran du ciné-parc, et au bout de chaque district : le Bonhomme en plastique (les Friches), le calendrier du garage (la Shop), la lanterne du serre-frein (la Gare), le chat qui salue (le Petit-Canton), la boîte de biscuits danois (le Faubourg), le flamant rose (les Érables), la tuque des Marsouins (les Quais), le chien du tableau de bord (La Pointe). Trouvées, elles vont sur l'étagère de la planque ; elles voyagent sur `/api/collections`.
- **Les sauts de Rocco** (`collectionner.py`, vague 4) : vingt sauts — les huit rampes de la ville et douze tremplins en contreplaqué aux chevrons rouges, que la carte ne connaît pas (ils voyagent sur `/api/collections` et se peignent par-dessus le sol) : un sur l'abord du Faubourg, trois aux Érables, un aux Quais, deux sur le pont de La Pointe, deux dans l'herbe des Friches (en 4 roues), un au Petit-Canton, deux à la Gare.
- **Le marché aux puces du dimanche** (`puces.py`) : le dimanche, de l'aube à midi, deux étals sur le terrain vague le plus près de la planque — les cartes de hockey de Ti-Rhéal, les meubles de Gisèle ; les marchands parlent, la rumeur d'un dimanche matin s'entend en approchant, et Gisèle rachète les meubles de la planque.
- **Métro** : quai (`metro_quai`) et rame (`metro_rame`).
- **Statues** (`statues.py`) : au coeur de la place des trois parcs de ville, un grand homme de
  bronze sur son socle — Samuel-Ovide Brumaire, le fondateur, aux Érables ; le général
  Trudel-Laflamme et sa jument Princesse au Faubourg ; Gilles « La Toque » Bouchard, 1971, à la
  Shop. Au bord du sentier des grands parcs de quartier des Érables, cinq bustes (la mairesse
  Rose-Aimée Paradis, l'abbé Côté, l'inventeur Omer Gauthier). On lit leur plaque à ACTION, une
  ligne par pression.
- **Aéroport** (`aeroport.py`) : l'aérogare (lieu `aeroport`, famille transport,
  pièce `aerogare` — comptoirs, sièges, carrousel, portiques), la tour de contrôle,
  deux hangars et la guérite (portes condamnées), la piste 09-27, la voie de
  circulation, trois avions peints (un bimoteur _Air Brumes_, un de Gaspésie, le
  monomoteur de l'aéroclub), un stationnement, une manche à air. Fermé par
  étages : la barricade du pont, le chantier (six piles sur 32 tuiles d'eau :
  aucun saut, et la nage demande le café et l'estomac plein), le barbelé, la
  guérite, le large (trop d'eau pour la nager depuis la plage de La Pointe) — et
  le **large refusé** : une ligne invisible, à une vue de l'île, où une coque vire
  de bord toute seule et où le courant ramène le nageur (la travée comprise).
  **Caché sur la carte** (mini-carte et grande carte) jusqu'au pont fini : de
  l'eau à la place de l'île, pas de repère. Les missions qui l'ouvriront :
  `aeroport.MISSIONS_A_VENIR` (`a01`, `a02`).

---

## 9. Les points d'apparition

- **Apparition du joueur** : au Terminus (débarqué de l'autobus, 50 $ en poche).
- **Zone du joueur** : la ruelle où dort le char de m1 (`RUELLE_DU_CHAR_DE_M1`).
- **Stationnements de service** : le poste de police a son lot avec une
  auto-patrouille garée.

> Rappel : les missions (`m1`…`m97`) et les défis sont documentés dans
> `app/missions/` (une mission par fichier) — voir `docs/comment-monter-les-missions.md`.