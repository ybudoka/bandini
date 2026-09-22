# Sven et le piratage : trois missions avec les bateaux

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « ajoute 3 missions avec les bateaux », puis « je veux
de longue mission et aussi de l'infiltration et du hacking ». Trois décisions prises avec
lui (questionnaire) : le piratage se joue comme **une petite séquence à taper** (Simon), les
trois missions forment **un seul fil en trois actes** chez le même donneur, et ce donneur est
**Sven « le Norvégien »** — déjà prévu dans le plan M16 (« le contrebandier qui veut Les
Quais »), jamais encore posé dans le jeu.

**Ce qui manquait au moteur, avant la moindre mission :**

- **Un donneur qui se tient au bord de l'eau, à un endroit stable** : `PERSONNAGES.ou`
  n'avait que `porte:<lieu>` (une porte de bâtiment) et `point:<type>` (dedans). Sven se
  tient sur la jetée, à côté du porte-conteneurs — nouvelle forme `mouillage:<slug>[:n]`,
  résolue vers le **poste à quai** du mouillage (`navires.py` l'exporte maintenant), pas
  vers le centre de la coque, qui est dans l'eau.
- **Poser le véhicule d'un `monter`/`livrer` SUR l'eau** : `Histoire.poserLeChar` faisait
  passer toute position par `tuileDeRue` (la rue la plus proche) — la seule route pour un
  bateau. La même forme `mouillage:` saute cette étape, pose la coque au centre exact du
  mouillage, à son cap, et marque `v.amarrage` pour que le décor (`majMouillages`) ne fasse
  pas naître un second bateau par-dessus.
- **Le piratage** : nouveau type d'objectif `pirater`. On s'approche du point `ou`, on
  presse ACTION ; une séquence de 4 directions s'affiche ; on la reproduit avec le **même
  axe unifié** que la marche (`Entree.axe` — clavier, manette, joystick tactile : rien de
  neuf à apprendre, et ça marche au doigt sans bouton de plus). Une mauvaise direction
  recommence la séquence ; après `essais` ratés, l'alarme sonne (échec `alarme`, nouveau
  dans `ECHECS`).

**Les trois actes, tous donnés par Sven (`prerequis` en chaîne m52 → m53 → m54)** :

1. **m52, la chaloupe** — éclairage : approcher discrètement, de nuit, `sans_etoile`.
   Établit le personnage, n'utilise pas encore le piratage (on apprend un mécanisme à la
   fois).
2. **m53, le chalutier** — sous couverture : approcher un poste sous une fausse
   apparence, PREMIER usage du piratage (désactiver un relais).
3. **m54, le porte-conteneurs** — le gros lot : pirater le registre du quai, prendre la
   coque, la mener sous la police, revenir. Cinq à sept objectifs, comme demandé.

⚠️ **La voix de Sven est un choix provisoire.** Aucune voix « norvégienne » n'existe au
compte ElevenLabs ; `Nicolas Petit` (accent parisien, le seul net-« pas d'ici » du
répertoire) tient la place, mais **cette décision-là revient à Martin, à l'oreille** — c'est
la méthode que le plan M16 écrit lui-même pour ce personnage précis. Les voix ne sont pas
généreées : les textes et leur `jeu=` sont écrits, prêts à l'écoute puis à la génération.

## À voir avant de livrer

Le port au grand complet (capture) ; les trois missions jouées au banc de bout en bout,
piratage compris (correct, une erreur, l'alarme).
