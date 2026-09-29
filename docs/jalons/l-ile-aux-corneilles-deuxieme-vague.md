# L'Île-aux-Corneilles — deuxième vague

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

ce que la 1re vague a laissé exprès : **les habitants** (Sœur Jeanne sur le parvis, Léo Cyr
devant le hangar — les deux figurants de l'arc I), **sa musique et ses sons à elle** (elle
emprunte le vent de La Pointe, et ça s'entend ; des corneilles, la cloche, le ressac), des
**façades qui ne sont pas toutes la même brique** (le peintre des logements ne lit pas `mur`
comme il le devrait, mesuré sur l'île), et **le traversier de M12** qui y accoste.

- ⚠️ La chapelle qui sauve la partie est une **récompense de mission** (i02, M16), pas un
  meuble de cette vague

### 2e vague — ses habitants, ses sons, ses façades — **livrée le 27 sept. 2026**

- **Des façades en bois à clin.** Le peintre des logements (`FACADES.residence`) ne peignait que les
  fenêtres et la porte : la brique venait toujours de la tuile de façade, et le `mur` ne changeait que la
  couleur des cadres. Mesuré sur une capture : les six maisons étaient la même maison rouge. Chaque maison
  de pêcheur porte maintenant un **bois à clin nommé au plan** (`ile.BATIMENTS[…]["declin"]`,
  `devantures.DECLINS` : rouge grange, jaune beurre, bleu large, vert sapin, blanc chaux), peint d'un coin à
  l'autre de la façade — sur quatre tuiles, la cinquième restait de brique. ⚠️ **Hors de `MURS`** : la
  ville tire son mur par `entier(0, len(MURS) - 1)`, une entrée de plus aurait changé les fenêtres de toute
  la ville. ⚠️ Et **plus d'escalier de fer** sur l'île, ni aux maisons ni au couvent (`escalier: None`, que
  le peintre et `carte.py` lisent comme « aucun ») : c'est une image de ruelle.
- **Deux habitants** : **Sœur Jeanne** sur le parvis de la chapelle (`porte:chapelle`, voix Julia) et
  **Léo Cyr** devant le hangar sans nom (`porte:hangar_ile`, voix Alexandre), les deux figurants de l'arc I.
  Pas encore de mission à donner : on leur parle et ils disent **leur repos à eux** (`repos` du personnage,
  lu par `missions.repliques_de_repos` et `Histoire.parler`) — « le Faubourg est tranquille », dit sur
  l'île, mentait. Fiches : [jeanne](../personnages/jeanne.md), [leo](../personnages/leo.md). Quatre voix
  (`histoire-jeanne-repos-*`, `histoire-leo-repos-*`, 327 crédits).
- **Sa musique à elle** : `amb_ile`, « L'île sans cloche » — une contrebasse à l'archet et un violon seul,
  la plus lente des ambiances (45 s, ~1 350 crédits). Elle empruntait le vent de La Pointe.
- **Ses bruits à elle** (`audio.QUARTIERS["sons"]["ile"]`) : les **corneilles** et le **volet qui claque**
  de l'usine (neufs), la cloche de bouée et le quai qui grince. ⚠️ **Pas de cloche d'église** : celle de la
  chapelle est chez Ti-Loup (i02), et Sœur Jeanne le dit à qui passe. Le juge des quartiers connaît
  maintenant l'île comme un district qui doit s'entendre.
- **Juges** : `test_ile.py` (six maisons en bois, cinq couleurs, deux voisines jamais pareilles, bois sur
  toute la façade, aucun escalier) ; `test_ile_js.py` (le peintre pose les planches et aucune marche — témoin :
  un logement de ville a les siennes ; Sœur Jeanne et Léo devant leur porte, qui disent leur repos — témoin :
  Ti-Paul dit le commun ; l'île joue `amb_ile` et ses bruits, jamais la cloche — témoin : la ville). Trois
  mutations rouges (l'escalier, les planches, le repos propre) et une quatrième sur la musique.
- ⚠️ **Reste pour une vague suivante** : **le traversier qui accoste** (`traversier.ESCALES` n'a que les
  Quais et La Pointe ; une escale de plus déplace sa route, donc à mesurer contre `test_l_ile_ne_deplace_
  rien_de_la_ville`).

### 3e vague — le traversier y accoste : la navette de l'île — **livrée le 29 sept. 2026**

- ⚠️ **Un deuxième bateau, pas une troisième escale.** Le traversier des Quais à La Pointe porte la fin m99 (le
  capitaine Bérubé, son quai, son horaire) et une dizaine de juges : lui ajouter l'île changeait sa route et son
  heure. La **navette** (`app/navette.py`) est la même coque et le même code — `static/js/traversier.js` est
  devenu une FABRIQUE (`fabriqueDeTraversier`) : `Traversier` et `Navette` lisent chacun leur clé de carte,
  disent leur nom (« NAVETTE POUR L'ÎLE-AUX-CORNEILLES ») et se trient à leur rang. Son horaire est celui du
  traversier DÉCALÉ d'une heure (`decalage_h`) : elle quitte les Quais aux heures impaires, quand il en arrive.
- **Sa route, lue sur la carte finie sans un dé** : aux Quais, une place du traversier (`traversier._quais`) ; à
  l'île, qui n'a pas une rue, un accostage le long de ses PLANCHES (`Q`) — on débarque sur une jetée, jamais sur
  l'herbe. La traversée la plus courte l'emporte : la vieille jetée de l'usine à poisson, au sud-ouest (celle du
  nord-ouest a sa chaloupe amarrée). ⚠️ Rien ne se pose ni ne se déplace : on ne retient qu'un débarcadère déjà
  libre de décor, et un couloir qui ne croise ni le traversier ni son débarcadère.
- **On y va en char** : la fiche le disait (« le premier char que tu y emmènes par le traversier est un
  événement ») — un char garé sur le pont aux Quais arrive au quai de l'île (jugé au banc).
- **Juges** : `test_navette.py`, `test_navette_js.py` ; trois juges d'avant apprennent qu'il y a deux bateaux (la
  ville avec ou sans traversier, avec ou sans l'île, et la carte rendue intacte : on lève les deux coques). Une
  mutation rouge (l'horaire qui ignorerait le décalage).
- **Reste** (pas au plan) : la dernière image de m99 — le traversier qui passe devant l'île, Sœur Jeanne qui
  sonne sa cloche — reste à M16 (arc I).
