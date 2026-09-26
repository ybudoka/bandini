# Le dojo du quartier : apprendre les techniques

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026), deuxième des trois jalons des arts martiaux : le répertoire est
[livré](les-techniques-d-arts-martiaux.md#notes), [les Mantes](l-ecole-rivale.md#fiche) viendront après le
[Petit-Canton](le-quartier-chinois.md#fiche). Conçu avec Martin le 26 sept. 2026 (brainstorming : le Faubourg,
Mireille Dion, l'épreuve « au vrai, en rythme », un module à part).

_Ce que ça donne :_ au nord du Faubourg, le **DOJO DION**. Mireille Dion, ancienne danseuse contemporaine venue
à l'aïkido puis au jiu-jitsu, vend ses cours au comptoir ; on les passe sur le tatami, en rythme, contre Kevin,
l'élève partenaire. Réussi, le geste est à nous pour de bon. Au départ, Bandini n'a que les coups de rue.

- ⚠️ **Mesuré avant** : un bâtiment garanti (`SPECIAUX`, une majuscule du plan) déplace la ville ; une devanture
  ordinaire, non (`devantures.py` : elle se peint par-dessus des tuiles qui existent). Il n'existe pas de façon
  générique d'imposer une enseigne et une pièce à un commerce ordinaire ; le précédent est
  `poser_les_carrosseries` (`carte.py`), qui choisit une façade par mesure, sans dé, sur la ville finie. Et le
  cadre des épreuves d'adresse (`B.epreuve`, `adresse.js`) COUPE le combat (`Combat.majGestes`) et fait
  d'ESQUIVE « abandonner » — or la leçon a besoin du combat, et le balayage part d'une roulade (ESQUIVE) :
  la leçon a donc son propre module.

### Le dojo dans la ville

- **Où** : posé après coup, sans un dé, dans la même passe que `poser_les_carrosseries` (fin de `generer`,
  avant `devants.deplacer`) : parmi les façades de commerce du **Faubourg** assez larges pour la pièce, **la
  plus au nord** (du côté du futur Petit-Canton), à égalité la plus proche du milieu du district. On y réécrit
  l'enseigne, la porte (`interieur: "dojo"`) et le point de la carte. La ville d'avant reste identique à la
  tuile près, sauf cette façade.
- **L'enseigne** : `DOJO DION`, famille de devanture `savoir` ; famille de lieu `service` sur la carte (blip et
  légende viennent de là, comme tous les lieux).
- **La pièce** (`_PIECES`, dessinée à la main) : un **tatami** au centre (un sol à lui, `tatami`), le comptoir
  d'accueil (le point de Mireille), un vestiaire, un sac de frappe, un mannequin de bois, des photos de
  spectacles au mur ; la marque de Bandini et celle de Kevin sur le tatami.
- **« SALON MIREILLE »** (`devantures.COMMERCES["faubourg"]`) devient **« SALON LOUISE »** : deux Mireille dans
  le même quartier, on croirait que c'est son dojo.

### Mireille Dion

- **Le personnage** `mireille` (`missions.PERSONNAGES`) : dedans, au point `cours` ; sa fiche
  `docs/personnages/mireille.md` (histoire, personnalité, comment elle parle, comment elle se présente). Calme,
  précise, elle compte les temps et voit tout ce que ton corps fait de travers ; drôle par la situation —
  c'est Bandini qui détonne dans son dojo, pas elle. Elle se nomme **une fois**, dans sa salutation.
- **Sa voix** : une voix ElevenLabs à choisir (voir « Voix multilingues ElevenLabs » : non québécoise permise).
- **ACTION près d'elle** ouvre le menu **LES COURS** (comme Josée ouvre le marché noir, `Histoire.parler`).
- **Horaires** : le dojo ouvre de 8 h à 22 h ; la nuit, la porte est fermée, comme les autres comptoirs à
  heures (`magasins.HEURES_DES_COMPTOIRS`).

### Les cours

- **LES COURS** : les dix techniques non gratuites de `app/techniques.py`, rangées par style (entêtes BOXE,
  KARATÉ, JUDO, JIU-JITSU), au prix du catalogue. À droite de chaque ligne : le prix, **APPRIS**,
  **PAYÉ — À REPRENDRE**, ou **APRÈS L'UPPERCUT** (un maillon de la chaîne attend celui d'avant : le circulaire,
  rang 5, attend l'uppercut, rang 4).
- **Acheter** : `Missions.payer`, le cours noté payé (`B.partie.coursPayes[slug] = true`), et la leçon part
  tout de suite. **Rater** laisse le cours payé : on recommence **sans repayer**. Apprise, la technique s'écrit
  dans `B.partie.techniques` et le cours payé s'efface.

### La leçon sur le tatami : `static/js/dojo.js`

- **La séance** : `B.cours = { slug, temps, fenetre, reussis, rates, kevin }`. Un court fondu, et Bandini est
  sur sa marque, face à **Kevin** (l'élève partenaire, kimono blanc — une tenue de la garde-robe).
- **La mise en place, par technique** (une donnée de `app/techniques.py`, `lecon`) : au contact pour les coups
  et les prises ; Kevin **de dos** pour l'étranglement ; Kevin qui **arme un coup sur le temps** pour la parade ;
  Kevin **plus loin** pour le coup sauté (l'élan) ; Kevin qui **attaque** pour le balayage (on roule, puis on
  balaie).
- **Le rythme** : Mireille compte « un… deux… et… », un temps toutes les **0,75 s** (45 images) ; le « et »
  ouvre une **fenêtre d'environ 0,4 s** (24 images). Une technique tenue se charge sur le « deux » et se
  relâche sur le « et ».
- **La réussite** : `dojo.js` écoute le moteur des techniques (un crochet de `Techniques` : la technique qui
  **porte** — l'arc qui touche, la prise qui projette, l'étranglement qui couche) ; si c'est la technique
  enseignée, **sur Kevin**, dans la fenêtre : « OUI ! ». **Trois réussites** : apprise. **Cinq ratés** :
  « On reprendra » — le cours reste payé. Une technique posée hors de la fenêtre ne compte pas.
- **Pendant la leçon**, la technique enseignée compte comme sue (`Techniques.sait`) ; les autres restent
  utilisables, seule celle-là compte.
- **Kevin** (`partenaire: true`) : on le frappe et on le projette **sans sang, sans crime**, il ne fuit pas ;
  couché, il se relève en une seconde et reprend sa marque. Hors leçon, c'est un élève qui s'entraîne au sac.
- **Sortir par la porte**, ou **ABANDONNER** dans la pause : la leçon est annulée, le cours reste payé.
- **À l'écran** : en haut, « UPPERCUT · 2/3 » et trois points qui s'allument au rythme du compte ; la voix de
  Mireille dit le compte. **Apprise** : « TU SAIS L'UPPERCUT », et un mot de Mireille.

### Les voix

≈ 25 répliques en v3, avec leur `jeu=` (voir « Le jeu d'acteur des missions ») : sa salutation, l'annonce des
cours, « un », « deux », « et », une annonce par technique (dix), trois « oui », trois « raté », la réussite,
l'abandon, le dojo fermé. ≈ 2 000 caractères du forfait ; `elevenlabs_status` avant.

### Les juges

- **Python** : le dojo existe **dans le Faubourg**, une seule fois ; la ville d'avant identique à la tuile près
  sauf sa façade (les deux villes en JSON, clé par clé) ; la pièce donne quelque chose à faire (et ses points
  ne se marchent pas dessus) ; chaque technique non gratuite a sa `lecon` et son annonce ; plus de
  « SALON MIREILLE ».
- **Banc, au bouton** : un cours se paie une fois — raté, il se reprend gratuitement ; trois réussites en
  rythme apprennent la technique ; une technique hors fenêtre ne compte pas ; le circulaire se refuse sans
  l'uppercut ; Kevin se relève et ne fuit pas, et le frapper n'est pas un crime ; sortir annule la leçon ;
  la nuit, la porte est fermée ; aucun `B.rng()` consommé par la leçon.
- **Mutations** sur chaque règle ; **capture** de la pièce, de Mireille au comptoir, et d'une leçon en cours.

## Notes

_Rien de livré._
