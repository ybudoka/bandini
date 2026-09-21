# Le décor, les bêtes et les gens répondent

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

demande de Martin (21 sept. 2026) : « ajoute plusieurs interactions avec le décor,
l'environnement, les autres gens, et plus ».

_Ce que ça donne :_ ACTION cesse de ne servir que les portes, les chars et les comptoirs.
Un banc, une poubelle, un buisson, une fontaine, un chat de ruelle et un musicien de rue
**répondent** — six gestes qui prennent la même route que tout le reste (« on agit sur ce qu'on
regarde », `faceA`), sans un menu de plus et sans un seul son neuf.

- **S'asseoir** (bancs, dans les quatre orientations) — on prend place sur le banc, le souffle
  remonte plus vite que debout, et la première poussée du stick nous relève. Comme le lit de
  l'hôpital : une pose (`assis_bas` / `assis_haut` / `assis_gauche` / `assis_droite`, déjà dessinées
  pour le patient de la salle d'attente), aucune arme sortie, et un coup reçu nous lève aussi.
- **Fouiller** (poubelles, ordures, bacs, bennes) — quelques sous, des canettes consignées, un
  reste de poutine, ou un rat qui mord ; **une fois par jour et par bac** (le bac dit « DÉJÀ
  FOUILLÉ »). Le standing du quartier compte : la poubelle d'un quartier cossu est presque vide,
  celle d'un quartier pauvre déborde (`poubelle_pleine`).
- **Se cacher** (buissons) — on s'y tapit ; la police ne nous voit plus que de très près, et les
  étoiles tombent comme hors de vue. Bouger, frapper ou être touché nous sort de là.
- **Boire** (la fontaine de la place) — le souffle remonte, et rien d'autre.
- **Caresser** (le chat des ruelles) — il ne file plus, il ronronne (une bulle), et on reprend
  quelques PV. Les gens le voient.
- **Un pourboire** (musicien, mime, jongleur, échassier) — un dollar dans le chapeau : l'artiste
  remercie d'un mot, et la ville ne reste pas indifférente.

⚠️ **Le catalogue est en Python, le moteur en JS** (le principe de la maison) : `app/interactions.py`
dit quel décor donne quel geste et ce que chaque geste rend ; `static/js/interactions.js` les joue.
Un juge en Python garde les bornes (un geste ne rend jamais plus qu'une mission, un décor nommé
existe, chaque geste a son invite), un juge sous Node garde le geste **par le bouton** (ACTION
face à la chose, l'invite qui ne promet que ce qui va se passer, et le dos tourné qui ne fait rien).

⚠️ **Ce que ça ne touche pas** : ACTION garde son ordre de priorité (un personnage, un comptoir, un
char, une porte passent avant le décor) et les poches restent le geste de qui n'a rien d'autre à
faire ; un pourboire ne remplace pas le pickpocket d'un musicien qu'on n'a pas les moyens de payer.
