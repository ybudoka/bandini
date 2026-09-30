# Le marché aux puces du dimanche

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ le dimanche, un stationnement se remplit d'étals, et on y trouve ce qu'aucun
magasin ne vend — les meubles de la planque, les cartes de hockey qui manquent, une arme rouillée.

- **Quand** : un jour sur sept du jeu, de l'aube à midi, dans un stationnement qui existe déjà (pas de pièce
  neuve).
- **Ce qui se vend** : un étal qui change **chaque semaine** — tiré de la semaine du jeu par un hachage,
  pas au dé (la règle des prix de la contrebande, `facteurDuJour`). On y marchande : un prix affiché, un
  bouton pour offrir moins, et le vendeur accepte ou refuse selon son humeur (calculée, elle aussi).
- **Le lien** : c'est là que la ligne des collections trouve ses meubles et ses cartes manquantes ; la
  faire après elle.

⚠️ **Ce qui guette** : des étals et des passants de plus un matin par semaine — le trafic ne doit pas
s'empiler dans le stationnement (le juge du trafic), et rien ne se pose au dé.

**Juges** : le même dimanche, le même étal pour tout le monde ; il change la semaine suivante ; marchander ne
tire aucun `B.rng()` ; un meuble acheté va à la planque.

## Fiche de la deuxième vague

_Tranché par Martin le 30 sept. 2026, après la livraison : trois ajouts._

- **Des voix aux marchands** : Ti-Rhéal et Gisèle parlent à voix haute — une fiche chacun dans
  `docs/personnages/`, une voix ElevenLabs québécoise de la bibliothèque (auditionnée à trois), et leurs répliques :
  l'accueil, le marchandage accepté ou refusé, la vente, rien à vendre cette semaine, au revoir. Chacun se nomme une
  fois. Le jeu d'acteur collé à chaque réplique ; les voix se chargent avec le marché, jamais au démarrage.
- **Une ambiance** : la rumeur d'un marché du dimanche matin (des gens qui jasent, une radio AM au loin, un chien, des
  tables pliantes), dosée à la distance du terrain, le dimanche aux heures d'ouverture seulement — un son de lieu
  (`audio.LIEUX`), chargé en approchant.
- **Y vendre** : revendre à Gisèle un meuble de la planque, à un prix bas (un choix, pas une pompe à argent) ; le
  meuble vendu quitte la planque et la sauvegarde, et peut revenir au catalogue. Le marchandage à l'envers (demander
  plus), avec l'humeur calculée, jamais tirée au dé. Les cartes en double : seulement s'il peut y en avoir.

⚠️ **Rien de neuf dans les définitions ni dans la carte** : voix, textes et sons voyagent sur `/api/collections`.

**Juges** : qui mordent (mutations), au banc par le bouton ACTION ; une capture du menu de vente.

## Notes

### Livré le 30 sept. 2026 (Martin : « le marché aux puces du dimanche », après les collections)

- **Quand** : le dimanche — le jour de partie divisible par sept (le 7, le 14…) —, de 6 h à midi. « La semaine »,
  c'est `(jour - 1) // 7`.
- **Où, sans un dé** (`app/puces.py`, appelé en tout dernier par `collectionner.poser`) : ⚠️ **pas un stationnement**
  comme la fiche le proposait — ses allées sont celles des chars, et des étals peints y auraient été traversés par le
  trafic (le « trafic qui s'empile » de la fiche). Martin avait dit « dans un lieu à choisir » : c'est **le terrain
  vague le plus près de la planque, à pied** — huit tuiles sur quatre d'herbe ou de friche, rien de posé dessus ni
  autour, hors des cours de gangs et des chantiers, loin des trouvailles et des pistes des sauts. Sur la graine
  livrée : l'herbe au bord du trottoir, au coin des Friches et du Petit-Canton (104, 106).
- **Deux étals, deux marchands, peints** (`static/js/puces.js`, aucune entité : rien ne naît, rien ne s'empile) :
  **Ti-Rhéal** et ses cartes de hockey — quatre numéros par semaine, tirés de la SEMAINE par un hachage (le même
  dimanche, le même étal pour tout le monde), **120 $** la carte (une carte trouvée par terre en rapporte 25 : on paie
  pour ne pas chercher) ; elle entre dans l'album par `Collections.donner(numero, 'puces')`, **sans** la prime de la
  rue (les paliers, eux, suivent). **Gisèle** et ses meubles : les quatre qui portent `ou: puces` (le juke-box, le
  sofa, le téléviseur, le tapis tressé) à **60 %** du catalogue Beausoleil, livrés le lendemain à la planque de Rocco.
- **Marchander** : chaque article a « ACHETER » et « OFFRIR » (70 % du prix). Le marchand accepte si son **humeur**
  pour cet article cette semaine (un hachage, jamais `B.rng()`) est sous 45 sur 100 ; sinon « 84 $ ? T'ES DRÔLE,
  TOI. » et l'article garde son prix jusqu'au dimanche suivant (`partie.puces = { semaine, refus }`).
- **ACTION** devant une table (dans `Missions.interagir`, après la cabane à sucre) ouvre l'étal ; le marchand y dit
  une de ses trois lignes (une par semaine). **Triche** : TRICHES > ALLER > COLLECTIONS > AU MARCHÉ, DIMANCHE 8 H
  (le jour avance jusqu'au prochain dimanche).
- ⚠️ **Pas de voix, pas de son neuf** : les marchands parlent par écrit. Des voix ElevenLabs demanderaient deux
  personnages de plus au catalogue des voix (et leur place au paquet) ; et on n'y **vend** rien (« peut-être » dans la
  demande) — à trancher par Martin, comme une ambiance de marché (le plafond des sons de lieu a 23 Ko de marge).
- **Le poids** : sur `/api/collections` (17 872 bruts / 6 348 gzip, plafond relevé à 22 000 / 8 000) ; rien dans les
  définitions ni la carte.
- **Captures** (`captures/collections/`) : `puces-terrain.png` (les deux étals un dimanche de janvier),
  `puces-menu.png`, `puces-article.png`.
- **Juges** : `tests/test_puces.py` (cinq) et `tests/test_puces_js.py` (huit : ouvert le dimanche matin seulement,
  le même étal la même semaine et un autre la suivante, marchander sans un dé et le refus qui tient la semaine, la
  carte sans la prime, le meuble le lendemain, ACTION **par le bouton**, le dessin, la triche) ; neuf mutations vues
  rouges — l'écart aux trouvailles ne mordait pas sur la graine livrée (le terrain choisi est déjà loin de tout) :
  un pré synthétique le sépare.

### Deuxième vague — des voix, la rumeur, et on y vend (✅ livrée le 30 sept. 2026)

- **Les voix** (Martin : « des voix aux marchands ») : deux voix québécoises de la bibliothèque ElevenLabs, ajoutées au
  compte et à personne d'autre (jugé) — **Ti-Rhéal = Christian Page** (grave et lent : un homme de soixante-dix ans),
  choisi contre Olivier et Marc André ; **Gisèle = Kasandra** (naturelle, spontanée : une vendeuse), choisie contre
  Caroline (déjà Mado) et Loulou (française). Les auditions sont dans `captures/puces-voix/` (la même première réplique
  par les trois) : ⚠️ **Martin ne les a pas écoutées** — changer de voix = `puces.VOIX` + `--refaire` des 9 ou 13 slugs.
  Le nom des deux voix a été remis au compte (`/v1/voices/<id>/edit`) : la bibliothèque les ajoutait sous un nom
  traduit (« Kasandra – Québécoise naturelle UGC pub ») que le script ne trouvait pas.
- **Les fiches** : [Ti-Rhéal Bergeron](../personnages/ti-rheal.md), trente ans sur la surfaceuse de l'aréna ;
  [Gisèle Lachapelle](../personnages/gisele.md), brocanteuse (ni Pelletier — Josée et Lulu —, ni Beaulieu — e03). Hors de
  `missions.PERSONNAGES` : ni l'un ni l'autre n'a de mission, et rien d'eux n'entre dans les définitions.
- **Les répliques** (`puces.REPLIQUES`, le jeu collé à chacune, 22 voix) : `salut` (le nom — **une fois pour toutes**,
  la première fois qu'on s'arrête à l'étal : `partie.puces.connus`), `accueil-1` à `-3` (les trois anciennes lignes
  écrites, dites maintenant — une par semaine), `vente`, `accepte`, `refuse`, `rien` (tout l'étal est déjà à toi),
  `aurevoir` (Échap ou B au menu de l'étal) ; chez Gisèle, `rachat`, `rachat-conclu`, `plus-accepte`, `plus-refuse`. Ce
  qu'il vient de dire s'écrit au pied du menu (élargi à la réplique) ; le bandeau du HUD ne tient qu'une quarantaine
  de lettres et ne montre que la première phrase (« TI-RHÉAL : « 84 $ ? T'ES DRÔLE, TOI. » »). Le refus de Gisèle a été
  réécrit pour ça (« Voyons donc! À ce prix-là… ») et refait une fois.
- **Leur route** : les textes, les séries de voix (`audio.serie_de_voix`) et la rumeur voyagent sur `/api/collections`
  (`puces.exporter`) ; `Son.Voix.declarer` (neuf) les remet à la liste de l'histoire, `Son.Lieu.declarer` le son. Tout se
  charge la première fois que la rumeur se fait entendre (`Puces.majSon`), jamais au démarrage (jugé).
- **La rumeur** (`rumeur_puces`, ElevenLabs, six secondes en boucle : des gens qui jasent et marchandent, une radio AM
  au loin, une table pliante, des boîtes de carton) : pleine sur le terrain, nulle à 320 px de son bord, le dimanche de
  6 h à midi seulement, jamais dans une pièce ni un bloc ; elle **glisse** vers ce volume en 2,5 s (on arrive, midi
  sonne). Un son du lieu `puces` (`audio.LIEUX`, `LIEUX_A_PART`) ; le filet, un murmure synthétisé. ⚠️ **Le plafond des
  sons de lieu (1,95 Mo) est plein** : une première boucle de dix secondes y tenait (32 kbit/s, le plancher du mp3 en
  44,1 kHz), puis les bêtes écrasées sont arrivées le même jour (+17 Ko) — refaite à six secondes, **sans le chien**
  demandé (un aboiement toutes les six secondes se remarque) : 24 364 octets, les lieux à 1 948 987, **1 Ko de marge**.
  Le chien, une boucle plus longue ou le prochain son de lieu demandent à Martin de relever le plafond.
  - **30 sept. 2026, le chien revient** (Martin relève le plafond des lieux à **3 Mo** : « ils ne se téléchargent qu'à
    la demande, jamais au démarrage »). La rumeur refaite en **douze secondes à 64 kbit/s** (le débit des boucles) :
    96 592 octets — toujours **sans chien dans la boucle** (Scribe n'y entend que « [background noise] »). Le chien est
    un son **à part** (`chien_puces`, 0,58 s, un seul aboiement au loin, 7 881 octets, même lieu `puces`) : un
    aboiement dans une boucle de douze secondes reviendrait encore à chaque tour, alors que posé à part il vient de
    loin en loin et d'un côté différent chaque fois. `Puces.majChien` : tant qu'on entend le marché (volume ≥ 0,25),
    le premier 35 s après qu'on l'entend, puis tous les 35 à 70 s (`RUMEUR["chien_s"]`, un écart qui change par
    `n × 17`, comme les bruits de quartier) — **à l'horloge, jamais au dé** ; posé à 224 px du milieu du terrain dans
    une direction qui tourne (`Son.jouerA`, portée 420 px : il s'entend au loin). Pas de filet synthétisé. Le plafond
    par fichier des lieux passe de 80 à 100 Ko pour la boucle. Les lieux : **2 029 096** octets sur 3 Mo. Juge :
    `test_le_chien_aboie_au_loin_a_l_horloge_et_pas_au_de`. ElevenLabs : 153 crédits au compteur (60 174 → 60 327 : la boucle, l’aboiement, deux relectures Scribe ; compteur partagé).
- **Vendre à Gisèle** (VENDRE UN MEUBLE, dans son menu) : chaque meuble **livré** d'une planque (celle de Rocco, le
  chalet) — pas un trophée, pas un meuble d'hier pas encore arrivé. Elle paie **le quart du catalogue** (`rachat` : le
  juke-box 375 $, l'aquarium 150 $, le sofa 100 $, le téléviseur 88 $, la lampe 38 $, le tapis 23 $), et on peut lui
  **demander 30 % de plus** : son humeur (`humeur(semaine, 'meubles', 'rachat:<meuble>')`, sous 40) décide, un refus tient
  jusqu'au dimanche suivant. ⚠️ **Un choix, pas une pompe** : le plus qu'on en tire (32,5 %) reste sous le moins qu'un
  meuble coûte (42 % : chez Gisèle, à l'offre acceptée) — jugé en Python et au banc. Le meuble vendu quitte
  `partie.meubles`, donc la planque et la sauvegarde ; il revient au catalogue Beausoleil et à l'étal de Gisèle. Une
  ligne au carnet (« VENDU AUX PUCES : … »).
- **Les cartes en double** : il ne peut pas y en avoir — l'album prend chaque numéro une fois, une carte achetée n'est
  plus par terre, et Ti-Rhéal ne vend pas celles de l'album. Rien à revendre, donc rien de fait.
- **Captures** (`captures/collections/`) : `puces-gisele-accueil.png`, `puces-vendre.png`, `puces-vendre-sofa.png`,
  `puces-apres-demande.png` — c'est la capture qui a montré le bandeau coupé et la réplique qui débordait du menu.
- **Juges** : `tests/test_puces.py` (cinq de plus : toutes les répliques, qui se nomme une fois, une voix chacun, rien
  dans les définitions, revendre ne paie jamais plus qu'acheter) et `tests/test_puces_js.py` (huit de plus, au bouton
  ACTION : le nom la première fois puis la ligne de la semaine et l'au revoir, rien à vendre, la vente et le marchandage
  qui se disent, vendre un meuble retire de la planque et de la sauvegarde, pas avant livraison, demander plus sans un dé
  et le refus qui tient, acheter pour revendre perd, la rumeur à la distance, aux heures, qui glisse et ne charge rien au
  démarrage). Quinze mutations vues rouges — dont une qui ne mordait pas au premier passage (les voix
  chargées dès la première image : le juge regardait avant que la partie tourne ; il fait maintenant tourner la
  partie loin du marché d'abord).
- **ElevenLabs** : 4 145 crédits au compteur pendant la vague (64 997 → 60 852 ; le compteur est partagé avec
  les autres sessions du jour) — auditions (6 × ≈ 100), 23 voix (≈ 1 500), deux rumeurs, et Scribe pour
  relire chaque voix (les mots y sont tous).
