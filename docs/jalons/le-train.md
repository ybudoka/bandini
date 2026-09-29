# Le train

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux un vrai train aérien, terrestre et tunnel. »

Ce qui roule déjà n'en est pas un : le [métro](le-metro.md) ne se voit qu'au quai et dans la voiture, le
tramway est un autobus sur rails dans la rue, et la Gare de triage a perdu ses voies (elles sont devenues la
cour à scrap des Boulonneux) — elle n'a plus de train.

**Tranché avec Martin le même jour** (quatre questions, quatre « oui ») :

- **Ce qu'il apporte : tout.** On le **voit** passer (viaduc, passages à niveau, portail du tunnel), on y
  **monte** à une gare, et il **écrase** ce qui traîne sur la voie.
- **Une ligne de passage**, pas une boucle : un vrai train interurbain qui entre à l'ouest hors carte et
  sort à l'est, **dans les deux sens**.
- **À bord, les deux** : s'asseoir dans le wagon (une pièce), ou rester sur la plateforme avec la caméra
  qui suit le train dehors.
- **Le viaduc est une couche du haut** (voir plus bas), pas des tuiles pleines : les rues passent dessous.

### Le tracé

D'ouest en est, la bande nord ([`app/nord.py`](../../app/nord.py)) va Friches (`bx 0`) → Petit-Canton
(`bx 5`) → Gare de triage (`bx 13`) → montagnes (`app/relief.py`) : exactement sol, aérien, gare, tunnel.

| Tronçon | Niveau | Ce qu'on y voit |
|---|---|---|
| Ouest, hors carte → les Friches | **au sol** | des passages à niveau : feux qui clignotent, cloche, barrières ; les chars attendent |
| Le Petit-Canton | **aérien** | le viaduc monte avant le quartier, enjambe la rue principale et redescend ; chars et gens passent **dessous**, entre les piliers |
| La Gare de triage | **au sol** | la **gare centrale** : un quai, un bâtiment de voyageurs |
| Est : les montagnes | **tunnel** | un portail de béton ; le train y entre et sort de la carte |

**Trois arrêts** : le quai des Friches, la station du viaduc (un escalier monte au quai), la gare centrale.

### Deux règles de fond

- ⚠️ **Le train est une heure**, comme la rame du métro et l'autobus : sa place sur la ligne ne dépend que
  du temps de la partie — rien à simuler, pas un dé (`B.rng` intact), la même place au rechargement. Un train
  vers l'est, puis un vers l'ouest, chacun à son heure.
- ⚠️ **La voie se pose en tout dernier dans `generer`, sans dé** (grossir un lieu garanti déplace la
  ville) : la ville avec et sans la voie est la même, clé par clé. Une clé neuve
  de la carte = une ligne dans `nord.DECALAGES`.

### Le viaduc : une couche du haut

Au niveau de la rue, le viaduc n'est que ses **piliers** (solides) ; la ville dessous garde toutes ses
tuiles, ses rues restent ouvertes. Le **tablier** et le train se dessinent **par-dessus** les chars et les
gens (après `Entites.dessiner`), avec leur ombre au sol. Écartés : le viaduc en tuiles pleines (un mur à
travers le Petit-Canton) et le viaduc seulement au-dessus du vide (on ne passe jamais dessous — c'est pourtant
ce qui fait vrai).

### Subir le train

- **Les passages à niveau.** Quelques secondes avant le train : feux, cloche, barrières qui descendent. Le
  trafic s'y arrête comme à un feu rouge (un « bloqué » que les chars lisent) ; les barrières remontent
  derrière le dernier wagon. Un char peut les **défoncer**, comme les barrières coulissantes.
- **Sur la voie** : un **char** est poussé de côté et cabossé — à grande vitesse, il prend feu ; un
  **piéton**, toi compris, meurt. **Le train ne freine jamais** : il klaxonne quand quelque chose est devant,
  et il passe. Rien ne l'arrête ni ne le dévie — pas même un autobus.
- **Sous le viaduc**, rien : seuls les piliers sont solides.
- **Le tunnel ne se visite qu'à bord** : son portail est clôturé.
- **Marcher sur la voie** est permis au sol (Friches, gare) — c'est là tout le danger ; sur le viaduc et dans
  le tunnel, on ne met les pieds qu'à bord.
- **La police** : **pas de billet quand on est recherché**, comme au métro (sinon, la meilleure cachette du
  jeu). Mais **sauter sur la plateforme d'un train arrêté en gare** reste possible en fuite, et l'hélico
  suit : une évasion, pas une téléportation.
- **Le son** : la cloche des passages, le klaxon grave, le roulement — fort de près, étouffé sur le viaduc
  au-dessus de soi. Bruitages ElevenLabs, la synthèse en filet ([audio](../../app/audio.py)).

### Monter à bord

- **En gare**, on se tient sur le quai : « TRAIN VERS L'EST — GARE CENTRALE — 5 $ · DANS 14 S ». Le train
  entre, ralentit pour de vrai, s'arrête une dizaine de secondes portes ouvertes, et repart à son heure —
  avec ou sans toi.
- **S'ASSEOIR** : le wagon, une pièce du CATALOGUE partagée comme la rame du métro (banquettes,
  porte-bagages) ; aux fenêtres, le paysage **du tronçon** — les Friches, les toits du Petit-Canton vus d'en
  haut, le noir du tunnel et ses lampes. « PROCHAINE GARE : GARE CENTRALE ».
- **RESTER SUR LA PLATEFORME** : le bonhomme à l'arrière du dernier wagon, la caméra suit le train dehors ;
  dans le tunnel, l'écran passe au noir et les lampes filent.
- **On change d'idée en route**, d'une pression : du wagon à la plateforme, et l'inverse.
- **Descendre** : en gare, sur **son** quai (à la station du viaduc, l'escalier ramène à la rue). **En
  marche, depuis la plateforme**, on peut **sauter** — au sol seulement : on roule par terre et l'on perd de
  la vie selon la vitesse ; sur le viaduc et dans le tunnel, refusé.
- **Les bouts de la ligne** : rester à bord jusqu'au tunnel ramène à la gare centrale ; le train sort de la
  carte, le joueur jamais.
- **Sauvegarde** : sauver à bord, c'est sauver à la gare d'où l'on est parti (comme le métro recale
  `B.exterieur` sur son édicule). **La grande carte** trace la ligne : pleine au sol, doublée sur le viaduc,
  en pointillé dans le tunnel.

### Les vagues

1. **Le train passe.** La voie posée en dernier sans dé : au sol, le viaduc (piliers, tablier dans la couche
   du haut, ombre), le portail du tunnel ; le train à son heure dans les deux sens ; les passages à niveau et
   le trafic qui s'arrête ; les collisions ; les sons ; la ligne sur la grande carte. _À la fin, on le voit
   passer et il peut t'écraser._
2. **On monte.** Les trois quais, le billet et son refus quand on est recherché, la plateforme et la caméra
   qui suit, sauter en marche, descendre à son quai, la sauvegarde recalée.
3. **On s'assoit.** Le wagon ; le paysage aux fenêtres selon le tronçon ; passer du wagon à la plateforme et
   revenir.

### Les juges (chacun rouge avant sa règle)

- **La ville ne bouge pas** : la même ville avec et sans la voie, clé par clé.
- **Les rues restent ouvertes** : chaque rue du Petit-Canton reste traversable sous le viaduc ; seuls les
  piliers sont solides.
- **Le train est une heure** : même heure, même place ; `B.rng` intact.
- **Un char attend au passage à niveau** ; un autre, laissé sur la voie, est poussé.
- **Au banc sous Node** : prendre le billet et descendre à la gare centrale — **au bouton**, pas en appelant
  la fonction.
- **Le poids du paquet** (`test_definitions`), et une **capture Chromium** de chaque niveau (sol, viaduc,
  portail) avant de livrer : un juge vert ne voit pas un dessin raté.
