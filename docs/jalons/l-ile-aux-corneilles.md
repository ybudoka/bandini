# L'Île-aux-Corneilles

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : L'Île-aux-Corneilles : la ville a une île et ne le sait pas (**ajout**, taille 3)_

_Demande de Martin (15 sept. 2026) :_ « tu peux extensionner la carte au besoin. »

⚠️ **Mesuré d'abord : le besoin est plus petit qu'il en a l'air.** La carte fait 421 × 213
tuiles, et **21 % en sont déjà de l'eau** — 18 675 tuiles. Au milieu de la baie il y a un
rectangle de **40 × 24 tuiles d'eau pleine** (à partir de 158, 116) qui ne touche aucune
rive. On n'agrandit donc **rien** : on pose une île dans ce qui existe, et la carte garde sa
taille, son paquet et tous ses juges de géométrie.

**Pourquoi une île, et pas un quartier de plus.** Depuis que l'eau n'est plus un mur (livré le
14 sept.), la baie est **traversable** — à la nage, en chaloupe, et un char y coule. La ville
a donc un cinquième de sa surface qui ne sert qu'à se noyer. Et deux choses du plan pointent
déjà vers un ailleurs sans l'avoir : le **traversier** de M12, qui ne va nulle part, et
_Le dernier traversier_ (m99), la fin où l'on sacre son camp — aujourd'hui un fondu au noir
sur un quai. L'île leur donne une destination.

**Ce qu'elle est.** Un quai de bois, une **chapelle** et son couvent à moitié vide, une
**usine à poisson** fermée depuis quinze ans, six maisons, un hangar sans nom au bout du
chemin. Trente habitants l'hiver. Pas de gang. Et surtout :

- ⚠️ **Pas de police.** C'est la seule idée mécanique de la fiche, et elle vaut toutes les
  autres : on peut y **laisser refroidir** un char et un casier. Les étoiles tombent à quai
  et ne remontent pas — mais l'île n'a qu'un chemin de retour, et Roy finit par le savoir
  (M11). Un endroit sûr qui n'a qu'une porte n'est pas un endroit sûr, c'est un piège qu'on
  choisit.
- **On y va comme on veut** : à la nage (long, et on arrive les mains vides), en chaloupe
  (celle du capitaine, gagnée en q08), en bateau volé, ou par le **traversier** quand M12 le
  fera rouler. C'est la barrière la plus honnête du jeu : elle n'est pas fermée, elle est
  **loin**.
- **Un char sur l'île y reste** : rien n'y roule qui n'ait été débarqué. Le premier char que
  tu y emmènes par le traversier est un événement.

**⚠️ Ce que coûte un septième district**, et il faut le dire avant de dessiner :

- **une ambiance de plus** (la musique par district est livrée) — ou elle emprunte celle de La
  Pointe, et ça s'entend ;
- **un rythme de population** (`DISTRICTS`), une couleur de légende, une ligne de mini-carte ;
- ⚠️ **les juges de géométrie ne parlent pas de l'eau** : « un seul îlot marchable » deviendrait
  faux le jour où l'île existe. Il devient « **un îlot par terre ferme**, et chacun atteignable
  par l'eau » — c'est une ligne de juge, mais il faut la changer **exprès**, pas la découvrir ;
- ⚠️ **le paquet** : 40 × 24 tuiles de plus, plus une chapelle et un hangar en intérieurs. On
  mesure avant (370 Ko bruts sur 600).

**L'arc de l'île est dans M16** (arc I, huit missions), et _Le dernier traversier_ y gagne sa
dernière image : le traversier passe devant l'île, et la ville rapetisse derrière.

**Juges** : l'île ne touche aucune rive (une ceinture d'eau d'au moins quatre tuiles tout
autour) ; on ne peut y arriver qu'à la nage, par un bateau ou par le traversier — aucun pont,
aucune tuile de route ne la relie ; la police n'y patrouille pas et les étoiles y descendent ;
chaque terre ferme reste un seul îlot marchable ; et le paquet reste sous son plafond.

### 1re vague — l'île existe, et la police n'y va pas — **livrée le 17 sept. 2026**

⚠️ **Remesuré avant de dessiner, et le chiffre de la fiche avait vieilli** : la carte fait
419 × 211, 23 % d'eau, et depuis que les plages et le port ont été redessinés la baie est un
rectangle d'eau pleine de **117 × 93** qui touche le bas de la carte. La place de l'île s'est
CHERCHÉE, pas choisie : parmi 5 125 ancres possibles, (203, 139) met la terre de l'île à
**trente tuiles d'eau** de la rive la plus proche et laisse le large à **64** tuiles de toute
terre — le juge « on ne va même pas au milieu de la baie » tient sans retouche.

- **Dessinée, pas générée** (`app/ile.py`) : un plan de 48 × 30, une rangée de texte par
  rangée de tuiles, jugé au chargement comme une pièce. Au nord-ouest le quai et sa jetée (39
  planches — sous les 50 du juge des quais de ville, qui veut de l'eau au sud de chaque
  planche), au milieu la **chapelle Sainte-Anne** et le couvent, six maisons le long du grand
  chemin, l'usine à poisson **condamnée** et sa vieille jetée au sud-ouest, le **hangar sans
  nom** au bout du chemin. La chapelle est un repère (`famille: repere`) avec un **clocher**
  peint sur son ardoise (`toits`, `TOITURES.clocher`) ; le hangar s'ouvre sans repère, son nom
  sur la porte. Les deux pièces sont à la mesure de leur bâtiment (9 × 8 et 8 × 6).
- ⚠️ **Sans sable** : Martin a renvoyé « moins de plage autour », et le juge de la grève veut
  que tout sable du large soit une plage déclarée — donc meublée, avec son sauveteur. L'île
  touche l'eau par l'herbe, comme la ville. ⚠️ **Et sans palissade** : le bois est une image de
  banlieue (`test_carte`) ; le jardin des sœurs est une haie de buissons.
- ⚠️ **Posée après le filet, et c'est ce qui la laisse exister** : `boucher_les_poches` bouche
  toute terre qu'on ne rejoint pas à pied depuis le terminus. Posée AVANT, l'île entière
  redevenait de l'eau sans un mot.
- ⚠️ **Posée après le dictionnaire de la ville, sans un dé, et AVANT les chantiers, l'autobus et
  le mobilier** : leurs juges comparent la ville avec et sans eux par le DÉBUT de la liste de
  décor, et un décor d'île ajouté après le leur les décalait. `test_ile` bâtit la ville avec et
  sans l'île : hors de son rectangle, rien ne bouge — ni une tuile, ni un abribus.
- ⚠️ **Le piège payé : `degager_le_devant` RÉASSIGNE `chantier.decor`** au lieu de l'allonger.
  Appelé après la construction du dictionnaire, il détachait la liste de la ville : le décor
  de l'île, les **337 abribus, bancs et arbres de rue** posés ensuite partaient dans une liste
  que plus personne ne lisait. L'île réserve donc le devant de ses portes sans y toucher
  (`_reserver_le_devant`), et `poser` lève si la liste a été détachée.
- **Deux chaloupes à quai, hors du plafond de la ville** : ses dix-huit places étaient toutes
  prises, et une île sans bateau est une île d'où l'on revient à la nage. Deux, et à 27 pas
  l'une de l'autre : l'écart des amarrages vaut aussi entre elles.
- **La nage est un pari, jugé** : 28 tuiles à payer (la première et la dernière sont de l'eau
  basse), 224 points de souffle, 112 avec un café. Ni le souffle seul, ni le café seul (100),
  ni l'estomac plein seul (160) — les deux ensemble, oui. Mutation : l'île à (203, 130), vingt-deux
  tuiles d'eau, et le juge rougit (« on y va l'estomac plein, sans café »).
- **Pas de police** : la zone `ile` passe en DERNIER (`Monde.zoneA` garde la dernière) et porte
  `refuge`. `Police.auRefuge` lit la zone — ou, dedans, la rue laissée derrière la porte : aucun
  agent n'y naît, l'hélico repart, ce qui patrouillait hors de l'écran s'en va, l'agent qui t'a
  suivi à la nage redevient un passant (il remettait `vu` à zéro à chaque regard), et
  `ajouterChaleur` comme `etoilesAuMoins` ne font rien. Les étoiles descendent au rythme d'une
  pièce. Chaque juge JS porte son témoin en ville ; les trois gardes retirées tour à tour font
  rougir chacune son juge, et lui seul.
- ⚠️ **« Un seul îlot marchable » est devenu « un îlot par terre ferme »**
  (`carte.composantes_par_terre`), changé EXPRÈS dans `test_carte`, `test_districts`,
  `test_eau` et `test_chantiers` ; `test_barrieres` saute les lieux de l'île (on n'y va pas à
  pied, et aucune barrière ne la touche), `test_quai_se_marche` part aussi de ses chaloupes, et
  `test_bateau` compte le plafond des amarrages sans elles.
- ⚠️ **Le paquet, et c'est elle qui a sorti la carte.** Avec l'île, il passait à **75 307 octets
  gzip sur un plafond de 75 000** (la ville seule 74 472 — elle avait pris deux Ko dans la
  journée —, l'île 835). Martin a tranché : la carte sort du paquet d'abord (« La carte sort du
  paquet », livrée juste avant), et l'île est partie après. La carte fait maintenant
  42 722 octets gzip sur son plafond de 48 000 (l'île y pèse 774).
- ⚠️ **Deux juges sans rapport sont tombés, et ils tenaient par chance.** Chaque décor devient
  une entité numérotée au chargement : les quarante décors de l'île décalent le numéro de chaque
  passant et de chaque char créés ensuite, donc leurs cadences. Mesuré sur 40 graines, **à la base
  et avec l'île** : le juge des virages à gauche tombait sur 1 graine (2 avec l'île) — le joueur,
  posé à une tuile du croisement, se faisait renverser, se réveillait à l'hôpital, et `estRoute`
  répondait non sur de l'asphalte parce que la carte active était la PIÈCE ; le juge des amuseurs
  tombait sur 4 (3 avec l'île) — il jugeait les secondes où un numéro né juste hors champ
  rassemble encore son public, que sa propre docstring exclut. Resserrés tous les deux sur leur
  règle (le joueur invincible ; on juge un numéro une fois son cercle formé) : 40/40 pour les
  virages des deux côtés, et le juge des amuseurs rougit encore sans la retenue des partants.
  ⚠️ **Reste une fragilité mesurée et pas réglée** : sur 3 graines sur 40 (2 avec l'île), le juge
  des amuseurs voit trop peu de numéros à l'écran (`vues`) — pas sur sa graine, et l'île n'y
  change rien.
- **Elle emprunte le vent de La Pointe** (`musique.AMBIANCES_DE_DISTRICT["ile"]`) : une
  musique à elle est pour la deuxième vague.

**Juges** : `tests/test_ile.py` (dans la baie, la ceinture, ni route ni pont ni barrière, un
îlot par terre ferme, le décor qui ne ferme aucun passage, le pari de la nage, les chaloupes,
la zone refuge en dernier, la chapelle et le hangar, six maisons et l'usine, la ville qui ne
bouge pas, la même île sur une autre graine) et `tests/test_ile_js.py` (la police ne vient pas
et les étoiles tombent, rien ne les fait monter — dehors comme dans la chapelle —, l'agent qui
t'a suivi rentre).

## Notes

demande de Martin : « tu peux extensionner la carte au besoin » — ⚠️ **remesuré le 16 sept.
2026, le besoin reste nul** : 23 % de la carte est de l'eau, et la baie est un rectangle
d'eau pleine de **117 × 93** (le « 40 × 24 » de la fiche datait d'avant les plages).
**Livré** : une île **dessinée** (`app/ile.py`, un plan de 48 × 30 comme une pièce, jugé au
chargement) posée à (203, 139) — le quai et sa jetée, la **chapelle Sainte-Anne** (on y
entre, un repère sur la carte, un **clocher** sur son ardoise), le couvent, six maisons et
leurs cordes à linge, l'usine à poisson condamnée, le **hangar sans nom** (on y entre) et
deux chaloupes à quai, **hors du plafond** des dix-huit de la ville.

- ⚠️ **Posée après le filet** (`boucher_les_poches` la noyait : on ne la rejoint pas à
  pied), **sans un dé** et avant les chantiers, l'autobus et le mobilier — un juge bâtit la
  ville avec et sans elle et compare.
- ⚠️ **Trente tuiles d'eau** jusqu'à la rive : ni le souffle, ni le café seul, ni l'estomac
  plein n'y suffisent, les deux ensemble oui.
- ⚠️ **Pas de police** : la zone `ile` (la dernière) est un `refuge` — aucun agent n'y naît,
  l'hélico repart, l'agent qui t'a suivi redevient un passant, et rien n'y fait monter les
  étoiles (`Police.auRefuge`).
- ⚠️ « Un seul îlot marchable » devient **« un îlot par terre ferme »**
  (`carte.composantes_par_terre`), changé exprès dans neuf juges. Détail dans
  « L'Île-aux-Corneilles » plus bas.
