# Le ciné-parc

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ l'été, un film sur écran géant à la sortie de la ville ; on y entre en char, pour un
rendez-vous ou une filature à phares éteints.

- **Le lieu** : un grand terrain avec un écran, des rangées de poteaux à haut-parleur, un casse-croûte
  (une pièce de plus, posée sans dé, en bord de ville).
- **Le film** : un écran qui scintille la nuit (un film muet en pixels, une poursuite de chars — un clin
  d'œil au jeu lui-même), l'été seulement.
- **Les missions** (M16) : une filature dans les rangées, phares éteints (`suivre`) ; un rendez-vous de
  Josée dans un char stationné (`parler`).
- **Les phares** comptent pour vrai (ils sont déjà à la mesure de chaque char) : allumer les siens en
  plein film fâche tout le monde.

⚠️ **Ce qui guette** : un grand terrain de plus, en bord de ville — la règle « agrandir la carte sous la
trame » (poser en dernier, sans dé) ; le trafic ne doit pas entrer dans les rangées.

**Juges** : le ciné-parc n'est ouvert que les soirs d'été ; un char s'y gare dans une rangée ; le trafic n'y
entre pas ; la filature se joue au banc.

## Notes

_Livré le 26 sept. 2026._

- **Un bloc de carte, pas un terrain de plus en ville** (`app/blocs/cineparc.py`) : c'est ce que la ligne
  des blocs promettait (« porte… le ciné-parc »). Un grand terrain en bord de ville aurait fait glisser la
  ville ; derrière un fondu au noir, il ne pèse rien sur `/api/carte`. On y entre en poussant contre le
  bord NORD de La Shop (colonnes 350 à 354, le trottoir de ceinture), à pied ou au volant ; on arrive par
  le chemin du sud. Le bloc n'a pas une voie : **le trafic n'y entre pas** (juge).
- **Le terrain** : l'écran au nord (son cadre est une façade du plan), le stationnement d'asphalte clos
  de grillage, quatre rangées de 28 cases nez à l'écran, le casse-croûte au sud-ouest avec ses vitrines
  allumées, deux lampadaires à l'entrée. `carte_du_bloc` lit maintenant les `lampes` d'un bloc (il n'en
  passait aucune).
- **Le film** (`static/js/cineparc.js`) : les soirs d'été seulement (juin à août, crépuscule ou nuit —
  l'année du jeu) ; hors séance, une toile grise. Une poursuite de chars en noir et blanc qui tremble —
  la route qui défile, le fuyard qui zigzague, l'auto-patrouille qui le colle, gyrophare au vent, les
  rayures de la pellicule —, fonction de l'image. L'écran éclaire le stationnement la nuit.
- **Les spectateurs** : pendant la séance, sept chars garés dans les cases (couleurs données, places à
  l'empreinte, jamais deux voisins) ; repartis après. **Les phares** : pendant le film, rouler dans le
  stationnement fait klaxonner les spectateurs (« ÉTEINS TES PHARES! ») ; garé dans une case et arrêté
  une demi-seconde, les phares s'éteignent (`pharesEteints`, lu par `Vehicules.allumerLesPhares`).
- **Juges** : `test_cineparc_js.py` (on y entre par le bord nord de La Shop ; le film et les spectateurs
  les soirs d'été seulement, dans les cases, pas le midi ni l'hiver, pas de trafic, la lueur de l'écran ;
  les phares qui fâchent puis s'éteignent, sans un faisceau) — et `test_blocs.py` juge son plan (le
  retour, l'arrivée, le passage en ville). Chaque juge a été vu rougir sous sa mutation.
- **Pas fait, à dire** : les **missions** (M16 : la filature phares éteints, le rendez-vous de Josée) ;
  le casse-croûte n'a pas d'intérieur (une porte condamnée) ; pas de son du film (une musique à payer).
