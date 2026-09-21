# Une seule musique pour toute la ville

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : La musique dit où tu es et ce qui t'arrive (**ajout**, taille 3) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « je veux des musiques différentes par district, et une musique générée
par IA pour l'écran titre. Je veux aussi des musiques pour quand on se bat avec des gangs, et
quand on a plusieurs étoiles. »

Aujourd'hui il y a **une** musique de fond — `ville`, 60 secondes, la même de La Pointe aux
Quais — et le thème du menu, écrit en notes. Rien ne change quand on traverse un pont, rien ne
change quand trois Cravates te tombent dessus, rien ne change à quatre étoiles.

**Le thème du titre : le plan l'avait déjà prévu, mot pour mot.** `musique.py` s'explique
là-dessus depuis le premier jour : « le jour où Martin veut une vraie pièce jouée par de vrais
instruments, elle se posera **par-dessus** comme les radios — c'est la même règle que partout
dans `audio.py` : l'échantillon quand il existe, la synthèse sinon ». Ce n'est donc pas un
revirement : le thème écrit en notes devient le **filet**, et un enregistrement se pose
dessus. Le jour où le fichier manque — réseau coupé, génération ratée — le menu a encore sa
musique.

**Cinq districts, cinq ambiances**, chacune avec ce qui fait son quartier : la brume et le
piano du Faubourg, le calme plat des Érables, le fer et le vide de La Shop, la corne et les
mouettes des Quais, le vent et les arbres de La Pointe.

⚠️ **Trois choses à régler, et ce sont elles le vrai travail** — pas les pistes :

- **Le poids.** Une piste de 60 s à 64 kbit/s pèse 480 Ko. Cinq districts, un titre, une
  poursuite et une bagarre font **huit** pistes, presque 4 Mo — le dossier audio en pèse déjà 4. Elles ne peuvent donc **pas** se charger au démarrage. La règle des radios s'applique
  telle quelle : on charge **au moment d'en avoir besoin**, une à la fois, et la piste d'un
  district s'annonce quand on approche de sa frontière, pas quand on y entre.
- **La couture.** Les districts se touchent — c'est tout le propos de M8, la ville est d'un
  seul tenant et rien ne se charge en roulant. Une musique ne peut donc pas **couper** à la
  frontière : elle se fond sur quelques secondes. ⚠️ Et il faut de l'**hystérésis** : on
  traverse une frontière en zigzag sur un boulevard, et une musique qui bascule à chaque pas
  de côté est pire que pas de musique du tout.
- ⚠️ **Qui gagne.** C'est la question qu'aucune des quatre demandes ne pose et dont tout
  dépend. Il y a déjà de la radio dans un char, l'ambiance à pied, la rumeur de la foule, les
  sirènes et les voix. Il faut **une échelle, écrite une fois** :

  |     |                                                             |
  | --- | ----------------------------------------------------------- |
  | 1   | une réplique de l'histoire — elle baisse déjà tout le reste |
  | 2   | **la poursuite**, à partir de N étoiles                     |
  | 3   | **la bagarre de gang**                                      |
  | 4   | la radio du char, ou l'ambiance du district                 |

  Et la rumeur de la foule passe dessous, toujours.

- ⚠️ **Une musique d'état a besoin d'une queue.** Les étoiles montent et descendent, une
  bagarre s'arrête et reprend. Sans durée minimale ni fondu de sortie, la poursuite
  démarrerait et s'arrêterait trois fois en dix secondes. La musique de poursuite continue
  quelques secondes après la dernière étoile perdue — c'est ce qui fait qu'on **souffle**.
- **À partir de combien d'étoiles ?** Une étoile, c'est un témoin qui a appelé ; ça n'est pas
  une poursuite. La musique arrive à **deux**, et peut monter d'un cran à quatre, quand
  l'hélico entre. Un seul réglage en Python, comme tout le reste.
- **Juges** : chaque district a une ambiance déclarée, et aucune ne se charge avant qu'on en
  approche ; une seule piste de musique joue à la fois (l'échelle est respectée, un test la
  rejoue) ; traverser une frontière en zigzag ne change pas de piste plus d'une fois ; le
  thème du menu joue **même sans aucun fichier** ; et le poids total reste sous son plafond,
  mesuré comme celui des radios.

**Livré le 14 sept. 2026 :**

- ⚠️ **Écrites en notes, et le poids disparaît avec la question.** Huit pistes de 60 s à
  64 kbit/s pèsent 4 Mo — autant que tout le dossier audio — et coûtent des crédits
  ElevenLabs. En notes, elles pèsent quelques kilo-octets, se chargent avec le paquet, et il
  n'y a **rien à charger à l'approche d'une frontière**. Ce n'est pas un raccourci :
  `musique.py` l'écrit depuis le premier jour — « le jour où Martin veut une vraie pièce
  jouée par de vrais instruments, elle se posera **par-dessus** comme les radios ». Le jour où
  un mp3 arrive, il se pose et celles-ci redeviennent le filet.
- **L'échelle est en Python** (`musique.ECHELLE`) et le navigateur la **lit** : histoire 1,
  poursuite 2, bagarre 3, ambiance 4. Sans ça, chaque endroit du JS aurait la sienne et deux
  musiques joueraient ensemble un jour sur trois.
- ⚠️ **La radio d'un char et l'ambiance occupent la MÊME case.** Et c'est `demandee` qu'on
  regarde, pas `courante` : une station se demande tout de suite et n'arrive qu'une seconde
  plus tard — attendre son arrivée laisserait le district jouer par-dessus pendant tout le
  téléchargement.
- ⚠️ **L'hystérésis ne s'applique pas au PREMIER district.** Elle sert à ne pas basculer trop
  vite ; au démarrage il n'y a rien à quitter — et sans ce cas, la musique attendait qu'on
  marche six tuiles avant de commencer, c'est-à-dire qu'elle ne commençait **jamais** si on
  restait sur place.
- **La queue** : la poursuite continue sept secondes après la dernière étoile perdue. Sans
  elle, elle démarrerait et s'arrêterait trois fois en dix secondes — et c'est cette queue
  qui fait qu'on **souffle**.
- ⚠️ **La musique unique de la ville ne démarre plus**, c'est tout le propos. Le fichier
  `ville.mp3` reste sur le disque et garde son juge de navigateur — celui qui prouve qu'il se
  **décode** — mais on le demande maintenant explicitement au lieu de l'attendre.
- **Juges (1 neuf, 4 rejoués)** : l'échelle est ordonnée et la poursuite couvre l'ambiance à
  deux étoiles ; la queue tient ses sept secondes puis rend la main au district ; un **zigzag
  de quarante images sur une frontière ne change de piste qu'une fois**, et s'enfoncer pour de
  bon la change ; à pied c'est l'ambiance du district, au volant la radio, et jamais les deux.

## Notes

demande de Martin (« des musiques différentes par district, et des musiques pour quand on se
bat avec des gangs, et quand on a plusieurs étoiles ») : il y en avait **une**, la même de
La Pointe aux Quais.

- ⚠️ Le vrai travail n'était pas les pistes, c'était **qui gagne** — l'échelle est
  maintenant **écrite une fois en Python** et le navigateur la lit. Cinq ambiances de
  district + poursuite + bagarre, **écrites en notes** (aucun mp3, aucun crédit :
  `musique.py` promettait cette porte depuis le premier jour), avec **hystérésis** aux
  frontières et **queue** sur les musiques d'état — c'est elle qui fait qu'on souffle
