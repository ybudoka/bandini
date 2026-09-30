# Une file pour entrer à la foire

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « je veux une file de personnes qui attendent pour entrer à la foire quand
c'est ouvert », puis « je veux que la clôture soit infranchissable » et « mets aussi des câbles de
gestion de file ».

Mesuré : la foire est ouverte jour et nuit (seul l'hiver la fermera, [la foire fermée
l'hiver](la-foire-fermee-l-hiver.md), `Foire.fermee`). L'arche (`carte.BARRIERES`, slug `foire`) est une
ouverture de trois tuiles dans le grillage (`foire_entree`) ; au sud, une rangée d'abord, le trottoir, puis
la rue. Le joueur paie 15 $ en se butant à l'arche ; le grillage s'enjambe comme toutes les clôtures, et
retomber dedans sans billet coûte une étoile (`Monde.resquille`).

Tranché par Martin :

- **Quand** : tant que la foire est ouverte (pas l'hiver), avec une longueur qui suit l'heure : deux ou trois
  personnes le matin, une douzaine en fin d'après-midi et en soirée, presque personne la nuit.
- **Elle avance** : toutes les quelques secondes, le premier passe l'arche (son billet payé) et va se perdre
  dans la foule de la foire ; les autres font un pas, et un nouveau arrive au bout. Rien au dé : à l'empreinte.
- **Des câbles à sangle, en zigzag sur le trottoir** : le vrai serpentin d'attente, devant l'arche. Il prend
  le trottoir : les passants le contournent par le bord de la rue.
- **Le joueur coupe s'il veut** : l'arche ne l'oblige pas à faire la file, mais ceux qui y sont le lui disent
  à voix haute (« Heille ! Y'a une file, là ! »), sans étoile ni bagarre.
- **Le grillage de la foire ne s'enjambe plus.** L'arche, elle, se force encore (on pousse, une étoile).

## Notes

Livré le 30 sept. 2026.

- **Le serpentin** : Python pose un rectangle de cinq couloirs sur deux rangées (l'herbe et le trottoir), sous la
  colonne EST de l'arche (`carte.FOIRE["file"]`, `_Chantier.file_de_foire`, clé de carte `file_de_foire`, lue sur la
  ville finie : rien de posé, rien de tiré). Le navigateur (`static/js/file_de_foire.js`) en tire UN chemin, du
  trottoir de l'est jusqu'à dedans : l'entrée au bas du dernier couloir, le zigzag, la bouche de l'arche. Ses tuiles
  sont solides pour tous les autres (`Monde.charger` : solidité 5, mais pas une clôture à peindre, `estCloture`) —
  les passants contournent par la rue, comme Martin l'a choisi. Les câbles : des poteaux chromés et une sangle
  rouge, ouverts là où l'on tourne, triés au dessin avec les gens (`ajouterVisibles`).
- **Ceux qui attendent** glissent le long du chemin (`fileS`) : c'est la file qui les pose, `majPieton` les laisse
  (`enFile`), `demeler` ne les pousse pas (`cede`) — c'est l'autre qui se tasse. Écart de 15 px : à 12, deux
  voisins de part et d'autre d'un coin passaient à 8,5 px, sous les 10 de `demeler` (le juge l'a vu).
- **La longueur suit l'heure** (`par_heure`) : 2 à 9 h, 5 à midi, 12 de 17 h à 19 h, 0 de 1 h à 6 h ; le
  serpentin en tient douze. Hors de l'écran, la file se remplit d'un coup (on la trouve pleine en arrivant) ; sous
  nos yeux, on arrive à pied par le trottoir de l'est, d'aussi loin qu'on ne se voit pas. La tête paie et entre
  toutes les 2,5 à 4,5 s (à l'empreinte), et devient un forain (`majForain`). Loin de la foire, la file se vide.
  L'hiver (`Foire.fermee`, s'il existe : [la foire fermée l'hiver](la-foire-fermee-l-hiver.md)), personne.
- **Couper la file** : le joueur qui passe l'arche vers dedans alors qu'on attend se fait chialer par le plus
  proche — une bulle et sa voix (Felix ou Amélie, selon qui parle), six répliques qui tournent (un compteur, pas
  un dé), pas plus d'une fois en dix secondes, aucune étoile. Les six voix (`audio.VOIX_DE_LA_FILE`) voyagent
  dans la SUITE du paquet (`repliques_de_la_file`) : le paquet des définitions était à son plafond, elles le
  faisaient déborder de 640 octets. Elles se chargent à l'approche (`Son.Voix.chargerLieu`).
- **Le grillage ne s'enjambe plus** : `GRILLAGE_DE_FOIRE` (`¦`, un poteau — le `?` est parti à la piscine de la villa le même jour, et un chiffre se range devant les autres clés dans un objet JavaScript : `test_pliage` l'a vu), le même grillage à voir, la solidité du barbelé.
  `Monde.resquille` (l'étoile à la retombée) n'avait plus de clôture à juger : retiré. L'arche se force encore
  (pousser une seconde, une étoile).
- **Le juge de p14** traçait le plus court chemin de l'arche au poste : le serpentin prenant le trottoir, le
  chemin descendait sur la rue et n'en remontait plus, et le Bonimenteur y prenait peur du premier char. La
  chaussée y coûte maintenant trois pas : on remonte sur le trottoir, comme un joueur.
- Juges : `tests/test_file_de_foire.py`, `tests/test_file_de_foire_js.py`,
  `test_foire.py::test_le_grillage_ne_s_enjambe_plus_mais_l_arche_se_force`.
