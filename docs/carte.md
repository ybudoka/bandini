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

---

## 1. Les districts

Cinq quartiers habités, plus la baie. Chaque district porte un **gang**, un
rythme de vie (matin/soir/nuit) et ses propres bâtiments garantis.

| District | Slug | Gang | Brume | Notes |
|---|---|---|---|---|
| **Le Faubourg** | `faubourg` | Les Cravates | ✅ | Centre-ville, le plus peuplé (34 piétons). On y débarque de l'autobus. La cour des Cravates au centre. |
| **Les Érables** | `erables` | Les Chevreuils | ➖ | La banlieue cossue : maisons détachées, deux parcs, un dépanneur. |
| **La Shop** | `shop` | Les Boulonneux | ➖ | L'industriel : entrepôts 2×2, presque pas de rues, désert la nuit. |
| **Les Quais** | `quais` | Les Morues | ✅ | Le port : hangars longs, une rangée de quais, l'eau au sud. |
| **La baie** | `baie` | — | ➖ | Pas un quartier : l'eau (un bloc fusionné de 7×6). |
| **La Pointe** | `pointe` | Les Skateux | ➖ | Le parc au bout de la ville, coupé par un chenal de 24 tuiles — un seul pont et la foire. |

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
| Le quai du cargo | `cargo` | piéton + véhicule | **de nuit** |
| L'arche de la foire | `foire` | piéton + véhicule | payer le billet (à la journée) |

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
| `remorqueuse` | Remorqueuse | camion | 2 | |
| `sport` | Coupé sport | auto | 2 | Rare. |
| `luxe` | Berline de luxe | auto | 4 | Rare. |
| `cabriolet` | Cabriolet rose | auto | 2 | Rare (Faubourg, La Pointe). Le plus rapide des chars à quatre roues, sous la moto ; menée à la vue de tous par la conductrice (`au_volant`), qui descend si on la vole. Ne se gare jamais. |
| `bateau` | Chaloupe | bateau | 4 | Hors trafic : amarrée contre une rive bâtie (`carte.amarrages`). Deux silhouettes, la barre et la console. |
| `chalutier` | Chalutier | bateau | 3 | Hors trafic : deux à quai autour du cargo (`navires.py`). Plus lent et plus lourd que la chaloupe ; la corne. |
| `porte_conteneurs` | Porte-conteneurs | bateau | 2 | Hors trafic : un seul, au quai du cargo (`navires.py`). Dix tuiles, le plus lent et le plus lourd du parc ; la corne. |

---

## 5. Les personnages de l'histoire (`missions.PERSONNAGES`)

Ceux qui donnent les missions et font vivre le fil, avec leur position et leur
voix.

| Slug | Nom | Voix | Où | S'en va |
|---|---|---|---|---|
| `ti_guy` | Ti-Guy | Felix Tabarnak | porte:terminus | après m1 |
| `thibodeau` | Madame Thibodeau | Julia | porte:kiosque | — |
| `marco` | Marco | Québec Tremblay | porte:garage | — |
| `bouchard` | Sergent Bouchard | Khaivan | point:sergent | — |
| `josee` | Josée | Jeanne Mance | point:contact | — |
| `civil` | Le client | Alexandre | — (dans le taxi) | — |
| `narrateur` | Le Clairon de la Baie | annonceur centre d'achat 1 | — | — |
| `tipaul` | Ti-Paul Gagnon | Québec Tremblay | porte:depanneur | — |
| `lulu` | Lucienne « Lulu » Pelletier | Claudia | point:lulu | — |
| `raymonde` | Raymonde Fortin | Nadine | porte:usine | — |
| `ovila` | Ovila Saint-Onge | annonceur centre d'achat 1 | point:ovila | — |

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
| `policier` | Agent | patrouille (posé par `police.js`) |
| `gardien` | Gardien du lot | grille de la fourrière |

---

## 8. Les points d'intérêt et zones

- **Zones nommées** : rectangles de districts, territoires de gang (`cravates`,
  `morues`, `chevreuils`, `boulonneux`, `skateux`), port, etc.
- **Rampe / Grand Saut** : le tremplin du défi « Le Grand Saut » (`ELAN_RAMPE`).
- **Foire** : les trois jeux d'adresse (`galerie_tir`, `marteau_force`,
  `peche_canards`) — un par kiosque, joués à pied.
- **Plages** : où naissent les baigneurs.
- **Métro** : quai (`metro_quai`) et rame (`metro_rame`).

---

## 9. Les points d'apparition

- **Apparition du joueur** : au Terminus (débarqué de l'autobus, 50 $ en poche).
- **Zone du joueur** : la ruelle où dort le char de m1 (`RUELLE_DU_CHAR_DE_M1`).
- **Stationnements de service** : le poste de police a son lot avec une
  auto-patrouille garée.

> Rappel : les missions (`m1`…`m97`) et les défis sont documentés dans
> `app/missions/` (une mission par fichier) — voir `docs/comment-monter-les-missions.md`.