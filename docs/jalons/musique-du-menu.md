# Musique du menu

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« s'il n'y en a pas je veux aussi une musique au menu d'accueil ») : il
n'y en avait pas — `Mus` était resté l'ébauche de M7 (trois lignes).

- ⚠️ Le thème est **écrit en notes**, pas enregistré (`app/musique.py`) : un mp3 de menu
  pèserait plus que tout le paquet réuni, coûterait des crédits à générer et ne se
  **testerait** pas, alors que 2 Ko de notes se relisent, se corrigent à la note près et se
  jugent. _Baie-des-Brumes_ : 92 bpm, la mineur, une grille de huit mesures qui tourne (Am7
  Dm7 G7 Cmaj7 Fmaj7 Bm7b5 E7 Am7 — le tour de chant le plus banal du jazz, **et c'est
  voulu** : il doit tourner sous un menu sans jamais accrocher l'oreille), quatre voix
  (basse marchante, nappe, chant sur seize mesures qui ne se répètent pas, balai sur le
  contretemps), boucle de 42 s. `Mus` est maintenant un vrai séquenceur : il pose les notes
  sur **l'horloge audio** avec un quart de seconde d'avance, jamais sur les images — sinon
  un à-coup d'affichage troue la mesure.
- ⚠️ Il ne programme **rien** tant que le son n'est pas accordé (voir « Le son retenu ») :
  dans un contexte suspendu l'horloge est figée, et toute la boucle sortirait d'un bloc à la
  seconde où le joueur touche l'écran. 13 juges Python (aucune note hors du clavier, aucune
  qui déborde de son motif — elle ne jouerait **jamais**, aucun chevauchement dans une voix,
  volumes cumulés sous l'écrêtage, la boucle finit sur un la) + 7 de banc (le rythme tombe
  sur un multiple exact du pas, la boucle reboucle sur la même note, le menu se tait quand
  la partie commence). `scripts/musique_apercu.py` rend un morceau en WAV sans lancer le
  jeu : une note fausse s'entend là plutôt qu'en ligne. Paquet **322 Ko bruts / 32,5 Ko
  gzip** (+2 Ko)
