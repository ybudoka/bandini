# Le derby de démolition à la foire

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ une arène de terre battue à la foire, cinq bazous, et le dernier qui roule gagne.

- **L'arène** : un enclos dans la foire (le lieu existe, le Bonimenteur y tient déjà ses défis), fermé par
  des pneus — on y entre en char.
- **Le jeu** : cinq chars pilotés par le jeu qui foncent sur les autres ; les chars ont déjà leurs points de
  vie et leurs épaves. Le dernier qui roule gagne la prime et le respect du Bonimenteur.
- **Un défi** du rail de la foire (une prime modeste, jamais plus qu'un boulot à l'heure), et le soir
  seulement.

⚠️ **Ce qui guette** : des chars pilotés qui visent d'autres chars, c'est une conduite neuve (le trafic
suit des voies, la police vise le joueur) ; l'arène ne doit pas déborder sur la foire à pied.

**Juges** : un derby se termine toujours (chrono ou dernier debout) ; les chars restent dans l'arène ; la
prime ne bat pas le taxi à l'heure.

## Notes

_Livré le 26 sept. 2026._

- **L'arène** (`app/derby.py`) : pas DANS la foire — l'enceinte est pleine (kiosques, manèges, le petit
  train), sa palissade arrête les chars, et l'arche ne laisse passer que les piétons qui paient. Elle est
  sur le gazon libre juste à l'est de la palissade, là où la foire ne s'étend pas pour laisser l'élan du
  pont : le premier rectangle de 16 × 11 tuiles de gazon sans décor ni pont (marge comprise), LU sur la
  ville finie. Rien n'est posé dans la ville : aucune tuile, aucun décor, aucun dé — les pneus sont
  PEINTS au sol, et l'arène ne retient que les bazous (`retenir`) : un passant ou une auto-patrouille y
  entre et en sort.
- **Le défi** (`missions.DEFIS`, `derby`, `ou: "derby"`) : un panneau au bord sud de l'arène, planté
  quand le défi s'ouvre — après **la galerie de tir** (le rail de la foire), jamais au démarrage. Il ne
  se joue que **le soir** (`soir` : crépuscule ou nuit ; sinon « ÇA SE JOUE LE SOIR — REVIENS À LA
  BRUNANTE »). ⚠️ Un comptoir de la foire ne sert qu'un défi (`defiDuComptoir` prend le premier
  ouvert) et un kiosque à manger perdrait son menu : d'où la forme `derby`, à côté de `porte:` et de
  `rampe` dans `Histoire.poserPanneau`.
- **Le jeu** (`Conduite.EPREUVES.derby`) : le Bonimenteur prête un bazou (`aToi` : y monter n'est pas
  un vol) et on y est assis tout de suite ; quatre autres (`conducteur: 'derby'`, `commandesDerby`)
  foncent sur le plus proche qui roule — le joueur compte plus près qu'il n'est (`vise_joueur`), une
  cible se garde quatre secondes, on recule quand on colle et après avoir cogné, et on ne revise pas
  tout de suite celui qu'on vient d'avoir. Aucun dé. Les bazous ont 60 % de la carrosserie d'une auto.
- **Les chocs** : jusqu'ici, deux chars du jeu ne s'abîmaient jamais (seuls les chocs du joueur
  comptaient). Deux bazous se cognent pour vrai — avec un **répit** d'une demi-seconde par bazou
  (`Conduite.choc`) : sans lui, deux bazous qui poussent l'un contre l'autre se cognaient à chaque image
  et s'achevaient en une demi-seconde (le premier essai : le joueur gagnait sans bouger). Un bazou mort
  se **plie** (épave fumante), il n'explose pas : la déflagration tuait le joueur dans le sien, et on
  se réveillait à l'hôpital pour un jeu de foire. Foncer sur un bazou n'est pas de la conduite
  dangereuse, et rien de tout ça n'est un crime.
- **La fin** : le dernier qui roule gagne ; ton bazou mort (ou laissé), c'est raté ; au bout du temps
  (2 min après le décompte), c'est **aux points** — la carrosserie qui reste, en part de la sienne. Le
  chrono du défi est le seul à l'écran (`chrono_s` = attente + temps), le verdict tombe avec lui. À la
  fin, l'arène se vide ; on garde son bazou s'il roule. Prime : 120 $ (la première fois, et le défi du
  jour), bien sous un taxi à l'heure.
- **Juges** : `test_derby.py` (l'arène : du gazon libre, hors de la foire et de tout, lue sans rien
  déplacer ; le défi : le soir, après la galerie, deux chronos qui disent la même chose, une prime
  modeste) et `test_derby_js.py` (le soir seulement, le bazou prêté sans crime ; trois derbies qui
  finissent — bazou mort, dernier debout, aux points — sans qu'un bazou sorte de l'arène, sans hôpital
  ni étoile, et l'arène vidée ; deux bazous qui se cognent pour vrai mais pas pendant le répit, le
  trafic non, et le joueur qui fonce sans délit ; le panneau au bord de l'arène seulement une fois
  ouvert ; la carrosserie qui décide aux points). Chaque juge a été vu rougir sous sa mutation, et le
  juge des trois derbies tient sur quatre graines.
- **Pas fait, à dire** : pas de foule autour de l'arène ni de voix du Bonimenteur pour l'annoncer (du
  texte et le klaxon du départ) ; le bazou est une auto de la fiche, repeinte — pas un sprite cabossé à
  lui.
