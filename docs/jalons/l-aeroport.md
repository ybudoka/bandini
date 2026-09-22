# L'aéroport de Baie-des-Brumes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (21 sept. 2026) :_ « aggrandit la carte au sud avec un autre pont sur l'ile de
droite. ajoute un aéroport. ca doit être bloqué par un pont en construction et d'autre stratageme
pour des missions futures. »

« L'île de droite », c'est **La Pointe** (la foire, le phare, un seul pont). La carte grandit donc
**sous La Pointe** : une île neuve, l'aéroport, et un **deuxième pont** qui part de la rue du bord
de l'eau de La Pointe — le prolongement de la rue qui y finit en T (colonne 394).

- ⚠️ **On n'agrandit pas la trame, on ajoute des rangées sous la carte.** Changer une rangée de
  la trame re-tire toute la ville (le chenal du 17 sept. : 26 juges sans rapport tombés). L'île
  de l'aéroport se **dessine** comme l'Île-aux-Corneilles (`app/aeroport.py`, un plan écrit à la
  main, jugé au chargement) et se pose **en tout dernier** dans `generer`, sans un dé : la carte
  s'allonge d'eau vers le sud, et rien de la ville d'aujourd'hui ne bouge.
- ⚠️ **Fermé par étages, pour les missions à venir** — chacun seul suffirait, et chacun est une
  mission à écrire :
  1. **le pont en construction** : une barricade à la tête du pont (barrière `pont_aeroport`,
     « PONT EN CONSTRUCTION ») ; on la défonce en char, mais…
  2. **la travée manquante** : le tablier s'arrête au-dessus de l'eau, des piles sans rien
     dessus, puis le bout du pont côté île. Un char lancé finit dans la baie ; à la nage, ça passe ;
  3. **le barbelé** : l'aéroport est clôturé au complet, et le barbelé ne s'enjambe pas ;
  4. **la guérite** (barrière `aeroport`, « LAISSEZ-PASSER EXIGÉ ») : la seule ouverture de la
     clôture, au pied du pont ; elle ne se force pas ;
  5. **le large** : de la plage de La Pointe à l'île, trop d'eau pour la nager, même avec le café
     et l'estomac plein.
- ⚠️ Les deux barrières attendent des missions qui **n'existent pas encore** (`a01` : le pont se
  finit ; `a02` : le laissez-passer). Elles sont déclarées dans `aeroport.MISSIONS_A_VENIR`, et le
  juge des barrières les accepte de là seulement : une faute de frappe dans un `apres` reste
  rouge.
- ⚠️ **Ce qu'il y a dedans** : une piste est-ouest (marques peintes : seuils, axe, 09 et 27), une
  voie de circulation, l'aire de trafic et ses avions stationnés (peints, pas encore des
  véhicules), l'**aérogare** (un lieu, une pièce dessinée pour les missions : comptoirs,
  carrousel, portique), la tour de contrôle, deux hangars, la guérite et un stationnement. Une
  zone à elle (`aeroport`), avec sa police : ce n'est pas un refuge.
- ⚠️ **Le poids** : la carte voyage à ~48,3 Ko gzip pour un plafond de 50. Des rangées d'eau ne
  coûtent presque rien sur le fil, l'aéroport, lui, coûte ; le plafond du paquet de la carte
  (brut et gzip) montera de ce que la mesure dira — c'est le prix de la demande.

## Notes

**Livré le 21 sept. 2026** — `app/aeroport.py`, `static/js/aeroport.js`, `tests/test_aeroport.py`,
`tests/test_aeroport_js.py`.

La carte passe de 419 × 224 à **419 × 304** tuiles : quatre-vingts rangées d'eau (la zone `large`)
et une île dessinée de 194 × 50 sous La Pointe. Le **pont de l'aéroport** prolonge la rue 19 de La
Pointe (celle qui finit en T sur la rue du bord de l'eau) : 24 rangées de tablier, **12 de vide**
avec deux piles qui attendent leur tablier, puis 16 rangées côté île jusqu'à la guérite. Dedans :
la piste 09-27 (175 tuiles), la voie de circulation, l'aire et trois avions peints, l'aérogare et
son enseigne (le seul bâtiment qui s'ouvre — pièce `aerogare`), la tour de contrôle, deux hangars,
la guérite, un stationnement, une manche à air, des balises qui s'allument la nuit. La ceinture de l'île
est d'herbe, pas de sable : « moins de plage autour » (`test_greve`).

- ⚠️ **La ville d'avant n'a pas bougé d'une tuile** : `poser` passe après les grands bateaux, sans
  un dé ; seules les quatre colonnes du tablier changent dans la carte d'hier, et toutes les listes
  (décor, portes, lampes, toits, zones, barrières, devantures) ne font que s'allonger
  (`test_la_ville_d_avant_ne_bouge_pas`).
- ⚠️ **Le pont part parfois du sable** : sur d'autres graines (3, 7, 777), la plage de La Pointe
  descend sous le tablier. Ce qui traînait dessous ou à son flanc (serviette, parasol, bouée)
  déménage sur la tuile libre la plus proche de même nature — déplacé, pas retiré.
- ⚠️ **Les étages, chacun jugé avec son témoin** : la barricade (`pont_aeroport`, après `a01`) arrête
  puis s'enjambe sans étoile ; la travée se nage (10 tuiles à payer, 80 points sur 100) mais aucune
  rampe n'y mène — 12 tuiles, c'est une de moins que ce que dégage une moto lancée, une porte laissée
  à une mission ; le barbelé ferme tout sauf la guérite (`aeroport`, après `a02`, ne se force pas) ;
  la plage de La Pointe est à **45 tuiles d'eau** de l'île, 172 points de souffle avec le café pour
  160 au mieux. Le carnet annonce les deux barrières (« FERMÉ — … »).
- ⚠️ **Les missions qui l'ouvriront n'existent pas** : `aeroport.MISSIONS_A_VENIR` les déclare (`a01`
  le pont se finit, `a02` le laissez-passer), et le juge des barrières n'accepte un `apres` que du
  catalogue ou de là. Idées pour l'arc A, à trancher par Martin : sauter la travée en moto (une rampe
  au bout du tablier), un colis au hangar sans nom de Sven qui arrive par avion, voler le monomoteur
  de l'aéroclub (il entrerait au catalogue des véhicules comme le chalutier), la tour qui voit toute
  la baie.
- ⚠️ **Le poids** : la carte passe de 48 282 à 50 331 octets gzip (409 780 → 483 244 bruts) ; ses deux
  plafonds montent à 53 000 et 520 000 (`test_definitions`). Le rouge des **définitions** (44 488
  pour 44 000) n'est pas de l'aéroport : 44 487 sur `dev` avant lui.
- ⚠️ **Le décor et les portes fermées de l'aéroport sont PEINTS** (`aeroport.PEINTS`,
  `portes_peintes`) : le jeu crée tout le décor au chargement (chaque entité prend un numéro) et
  tire au hasard dans toutes les portes `d` ; quinze entités et quatre portes de plus décalaient le
  hasard de la ville entière — cinq juges sans rapport sont tombés (les vélos, le petit train, le
  clignotant, la plage qui ferme, l'arroseuse), chacun selon le compte exact, et la bissection
  changeait la liste à chaque essai. Seule l'aérogare a une vraie porte. La mission qui ouvrira
  l'aéroport en fera du vrai décor — et devra compter avec ces juges-là.
- ⚠️ **Le juge de l'arroseuse tenait par chance** (`test_la_nuit_js`) : le joueur, planté sur la
  chaussée la nuit, se faisait faucher et se réveillait à l'hôpital, et le juge lisait la carte de la
  PIÈCE — tout ce qui était mouillé y devenait « hors route ». Il tombait aussi sur la base avec
  quinze caisses et cinq portes de plus au coin de la carte. Durci : le joueur est invincible pendant
  la mesure, et le juge dit s'il est entré quelque part ; vert sur la base perturbée, rouge sous
  mutation (l'arroseuse qui mouille le trottoir).
- ⚠️ **Hors de la trame, pas de quartier** : `Monde.standingA`/`usageA` rendaient la dernière rangée de
  blocs à tout ce qui est plus bas (la mer au sud des Quais était « pauvre ») ; bornés à la trame,
  comme `standing_en`/`usage_en`.
- ⚠️ **La grande carte** (touche N) se met à l'échelle de la hauteur : la ville d'avant y est dessinée
  un quart plus petite, l'aéroport en bas. C'est le prix d'une carte plus haute.
