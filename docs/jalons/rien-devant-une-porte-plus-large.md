# Rien devant une porte, plus large

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (20 sept. 2026) : « déplace les obstacles pour éviter que ça soit devant les
portes des commerces et dans les missions ».

- ⚠️ **Mesuré avant** (quatre graines) : le pas de porte (deux tuiles) était propre sur toutes les
  couches — mais un obstacle se lit « devant » dès qu'il est dans l'axe à trois tuiles, ou collé de
  côté. **16 à 40 objets par ville** : six à douze scènes d'amuseurs (leur foule tombe sur le
  seuil), deux à quatre kiosques (une roulotte à café contre la porte du terminus, où M1 commence),
  des réclames, jusqu'à huit BBQ, des caisses, des arbres — et, en jeu, la voie fermée du jour et le
  bris d'aqueduc à trois tuiles de la porte du bar. Martin a dit oui aux trois : le décor de la
  rue, plus large ; ce qui apparaît en jeu ; ce que les missions posent.
- ⚠️ **Livré : `app/devants.py`, à la toute fin de `generer`, sans un dé.** Réserver plus large
  pendant la construction re-tire la ville (deux tuiles ont fait tomber trois juges sans
  rapport, une rangée de la trame vingt-six) : on **déplace** donc après coup, sur la ville
  finie. Le devant d'une porte, c'est trois tuiles dans l'axe et une de chaque côté
  (`DEVANT`) ; devant un **lieu de mission** — les onze que lisent les objectifs, les scènes
  et les personnages de `missions`, jamais une liste écrite ici —, deux tuiles de plus de chaque
  côté et une de plus devant (`DEVANT_DE_MISSION`) : c'est là que le donneur attend et que le char
  se livre. Ce qui bouche part sur la tuile voisine la plus proche, dans l'ordre de lecture :
  les **scènes** (dans leur îlot ; leur foule ne tombe plus sur un seuil), les **kiosques** (même
  sorte de sol, même quartier, leur réclame suit et se déplace si elle n'est plus à portée de
  marche) et le **décor** mobile (`DECOR_MOBILE` : BBQ, caisses, arbres, poubelles…, sur le même
  sol, sans couper de passage), en évitant tout ce qui a déjà choisi sa place (quais d'autobus,
  stations, bacs des éboueurs, pistes de rampe). Rien ne s'y perd — ni kiosque, ni décor — sauf,
  au pire, deux scènes sur une cinquantaine, faute de place dans leur îlot.
- ⚠️ **Ce qui apparaît en jeu est MARQUÉ, pas retiré** : la voie fermée du jour, la rue barrée et
  le bris d'aqueduc se tirent dans leur liste par `hash % longueur`, et une entrée de moins
  rebat tous les jours — un juge de trafic qui prend « le premier chantier » en a trouvé un autre,
  planté avant un croisement, et a rougi. Python pose `ecartee: 1` sur ceux qui tombent devant une
  porte ; `Monde.entraveDuJour` et `Monde.brisDAqueduc` passent à la suivante. Les nids-de-poule,
  tous actifs à la fois, sortent de leur liste.
- ⚠️ **Côté jeu** : `ville["devant"]` porte la fenêtre (`cote`, `profondeur`), `Monde.devantDUnePorte`
  la lit (portes du sol et portes peintes), et `Histoire.tuileLibre` — où les missions posent leur
  monde : le donneur, les hommes de main, le fuyard, l'escorte — prend la première tuile qui n'est
  pas devant une porte (à défaut, la première venue : mieux vaut un donneur devant une porte que
  pas de donneur). Les panneaux de défi aussi.
- ⚠️ **Trois juges ne tenaient qu'à la place exacte de la roulotte du terminus**, et le déplacer les
  a dits : `test_ils_partagent_un_plafond…` (un amuseur naît dans la bulle, hors champ — le juge
  partait du terminus, où toutes les scènes sont à l'écran : **une graine de jeu sur vingt** le
  voyait naître, avant comme après ; il part maintenant du centre du Faubourg, comme son voisin),
  `test_plusieurs_dialogues…` (la roulotte et son vendeur poussaient la fille de la Brume à 50 px,
  hors de portée d'accoster) et `test_celui_qui_tient_son_poste_…` (à l'ouest de Ti-Guy, la roulotte
  arrêtait le coureur : il mesurait 1 px, la roulotte, pas la laisse). Les trois se jugent
  maintenant sans elle, sur leur règle ; celui du poste déplace Ti-Guy de huit pixels avant de le
  lâcher, et rougit si la laisse cesse de le ramener (mutation vue). Trois autres juges qui
  comparent la ville avec et sans une étape (`test_autobus`, `test_metro`,
  `test_poste_et_garage`) neutralisent celle-ci des deux côtés, comme la saleté.
- ⚠️ **Pas touché** : les guichets et les machines encastrées sous une vitrine (elles ne bouchent
  rien), les lampadaires, les bancs et les abribus (une lampe, un sens, un tracé les suivent), les
  meubles **dans** les pièces (la porte de sortie de 51 pièces sur 67 a un meuble à trois tuiles :
  des comptoirs, tous atteignables — non demandé), l'équipe des chantiers (un ouvrier posté à trois
  tuiles d'une porte sur une graine de six ; le juge veut son compte exact par phase) et la
  tranchée (aucune devant une porte sur six graines).
- 31 juges neufs (`test_devants.py`, `test_devants_js.py`), **rouge avant** : sans le
  déplacement (13 des 23 juges Python), avec l'ancienne `tuileLibre` (le juge des tuiles libres), sans le saut
  de la voie et du bris écartés (un juge chacun).
- ⚠️ **Rouge sur `dev` avant moi, pas de moi** : `test_les_voix_de_l_histoire_sont_declarees_par_mission`
  (m50 pas déclarée), `test_la_carte_du_depot_est_a_jour` (incendies, `test_debug_js`),
  `test_la_foule_ne_se_traverse_plus` (deux façons de tomber) et l'intro de m97
  (`test_chaque_intro_se_joue_seule…`, m50 se pose avant). Et `ruff` y trouve six erreurs dans
  `app/missions/` et `test_argent_sale_js.py`.
