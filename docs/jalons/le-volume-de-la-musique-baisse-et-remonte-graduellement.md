# Le volume de la musique baisse et remonte graduellement

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (20 sept. 2026), dans le prolongement du fondu enchaîné : « il faut aussi baisser
les volumes et les monter graduellement ».

- ⚠️ **Mesuré avant** : le ducking (`Voix.baisserLeReste`) met la musique au quart **d'un coup** à
  la première syllabe d'une réplique ou d'un appel, et la **remet d'un coup** à la dernière ;
  deux répliques qui s'enchaînent font donc sauter la musique deux fois. Même saut pour le musicien de
  rue (`rue_sous_etat`, ×0,25 quand la poursuite ou la bagarre démarre, ×1 quand elle s'arrête).
  Le quart (0,25) est écrit en dur dans le JS, à deux endroits.
- ⚠️ **Livré** (`son.js`, section « Le ducking »). `baisserLeReste` ne baisse plus rien : il donne une
  **cible** à `Duck`, dont le niveau glisse vers elle à chaque `Mus.tick()` — donc à chaque pas de
  `maj()`, 60 par seconde à pas fixe : `baisse_s` et `remonte_s` sont de vraies secondes, quel que
  soit l'écran, et le banc voit la même courbe. Le niveau est appliqué aux trois familles : les boucles
  (`musique-`, `radio-`, `ambiance-`), les notes du séquenceur (`Mus.attenuation`) et le musicien de rue
  (`Rue.attenuation`). Le retrait du musicien sous la poursuite (`Rue.sousEtat`) glisse de la même
  façon, **même sans musicien en vue** : un gars qui apparaît en pleine poursuite entre déjà tassé.
- ⚠️ **Elle remonte plus lentement qu'elle ne baisse** (0,3 s contre 1,2 s), et c'est le point qui
  compte : une conversation, ce sont des répliques à une seconde l'une de l'autre, et la musique
  n'a plus le temps de revenir entre deux. Les trois chiffres — le quart, `baisse_s`, `remonte_s` —
  sont écrits **une fois**, dans `musique.MUSIQUE`, et le JS les lit.
- ⚠️ **Corrigé au passage** : une piste lancée PENDANT une réplique (on entre dans un commerce en
  plein appel) entrait au plein volume et couvrait la voix ; elle prend maintenant le ducking en
  cours. Les notes du séquenceur, elles, lisent le niveau à la pose : jusqu'à `HORIZON_S` (0,25 s) de
  retard, ce qui est déjà programmé garde son volume — le filet, pas le chemin courant.
- ⚠️ **Pas touché, exprès** : la rumeur de la foule **tombe d'un coup** quand on sort une arme, c'est
  l'effet (« ils t'ont vu »), et elle remonte déjà doucement ; le bouton SON coupé reste immédiat,
  c'est un geste du joueur.
- **Juges** : `test_la_musique_baisse_puis_remonte_graduellement_et_remonte_plus_lentement` (lit le
  volume à chaque pas : monotone, aucun pas ne saute de plus du quart du chemin, arrivée exacte, et les
  durées suivent les chiffres du juge — doublés — pas ceux de Python),
  `test_deux_repliques_qui_s_enchainent_ne_font_pas_sauter_la_musique`,
  `test_une_musique_qui_demarre_pendant_une_replique_baisse_elle_aussi`,
  `test_le_musicien_de_rue_glisse_sous_la_musique_d_etat_et_sous_une_voix` (quatre trajets), et les deux
  juges du ducking d'avant, qui avancent maintenant dans le temps ; en Python, les chiffres exportés.
  Vus **rouges** : dix mutations (le saut, la remontée aussi rapide, les durées et le quart en dur, les
  boucles qui ne retrouvent pas leur volume, le séquenceur ou le musicien non baissés, la boucle neuve
  non baissée…). Une onzième restait verte — `Duck.sale`, un drapeau **redondant** : supprimé.
