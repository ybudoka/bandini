# Le temps des Fêtes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ en décembre du jeu, la ville s'allume — des lumières sur les maisons, un Père Noël au
centre d'achat, des dindes à livrer, et le party de bureau de la Prévost qui dégénère.

- **Quand** : une fenêtre de jours calculée (comme la neige de M12, avec elle).
- **La ville** : des guirlandes sur les façades des quartiers (les lampes existent, leur couleur change),
  un sapin sur le Carré, la radio qui passe des chansons de Noël (les stations existent).
- **Les boulots** : livrer des dindes (`boulots`), et le Père Noël au centre d'achat (un boulot drôle : des
  enfants sur les genoux, un chrono).
- **Une mission** (M16) : le party de bureau de la Prévost — Raymonde et Prévost au même party, ça finit
  mal ; ramener un cadre soûl chez lui sans qu'il vomisse dans le char (`sans_degats`).

⚠️ **Ce qui guette** : les décorations se posent sans dé et s'en vont après ; la musique de Noël est une
dépense ElevenLabs (à trancher par Martin).

**Juges** : les décorations apparaissent et disparaissent aux bons jours ; aucune ne bloque une porte (la
règle « rien devant une porte ») ; la mission se joue au banc.

## Notes

_Livré le 26 sept. 2026._ Pas d'option : décembre, c'est l'année du jeu (`calendrier.py`, les jours 37 à 40
de chaque année de quarante jours) — une pure fonction du jour, rien à défaire en janvier.

- **Les guirlandes** (`static/js/fetes.js`) : pas une lampe de plus — la COULEUR de celles qui existent.
  La nuit, les fenêtres et les vitrines prennent le rouge, le vert, l'or ou le bleu (à l'empreinte de la
  tuile de la lampe), et une ampoule sur quatre change à son tour ; les lampadaires de rue restent
  blancs (`Monde.lampesVisibles` demande la couleur à `Fetes.couleur`). Rien ne bouche une porte.
- **Le sapin** (`app/fetes.py`) : la fiche le voulait « sur le Carré » — la ville n'a pas de Carré ; il est
  sur la place du Faubourg, la scène la mieux cotée du district, lue sur la ville finie. PEINT : ses
  étages, ses boules qui clignotent, l'étoile au bout, et sa lueur la nuit.
- **Les dindes** (`BOULOTS.dindes`) : dans un camion, en décembre, trois livraisons. ⚠️ Le camion a DEUX
  boulots de saison — les génératrices pendant le verglas, les dindes en décembre, rien le reste de l'année
  (`Missions.boulotDuChar`) ; la fiche des dindes dit qu'elle `partage` son camion, et le juge « un boulot
  par char » le sait. Le boulot en cours se juge sur le char de SA fiche (`economie.BOULOTS[slug].vehicule`),
  plus sur le `boulot` du char : sans ça, les dindes se perdaient à l'image suivante. Paliers : +30 % de
  prime, -20 % aux kiosques, +10 % de vie.
- **Le Clairon**, le premier matin de décembre.
- **Juges** : `test_fetes.py` (décembre, le sapin sur une scène du Faubourg, l'économie) et
  `test_fetes_js.py` (les guirlandes en décembre seulement, pas sur les lampadaires ; le sapin et sa lueur,
  partis en janvier ; le camion : dindes en décembre, génératrices au verglas, rien en juillet ; le
  Clairon). Chaque juge a été vu rougir sous sa mutation.
- **Pas fait, à dire** : **la radio de Noël** (une musique à payer, à trancher par Martin) ; **le Père Noël
  des Galeries** (un boulot drôle, les enfants sur les genoux — les Galeries existent maintenant, il
  s'y posera) ; **le party de bureau de la Prévost** (une mission M16) ; la neige de décembre n'est pas
  forcée (elle reste une option).
