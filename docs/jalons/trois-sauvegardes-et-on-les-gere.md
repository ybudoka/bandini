# Trois sauvegardes, et on les gère

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « on devrait pouvoir avoir 3 sauvegardes et les gérer ». Une seule
partie vivait dans le `localStorage` et le titre n'avait qu'un bouton JOUER : recommencer,
c'était perdre sa partie. **Livré** : JOUER ouvre **LE CHOIX DES PARTIES**, un menu canvas
comme la pause (manette, clavier, croix tactile) — trois emplacements (« 1  JOUR 12 ·
4300 $ », le temps de jeu à droite, et en bas « SAUVÉE HIER À 23 H 01 · 5 MISSIONS » pour la
ligne sous le curseur), **COPIER UNE PARTIE** et **EFFACER UNE PARTIE**. Continuer, c'est
deux ACTION : le curseur attend sur la dernière partie jouée (`bandini-emplacement-v1`).

- ⚠️ **La partie d'avant ne bouge pas** : l'emplacement 1 garde la clé `bandini-partie-v1`,
  les deux autres sont `-2` et `-3` — aucune migration, donc rien qui puisse s'arrêter au
  milieu, et une version d'avant retrouve sa partie.
- ⚠️ **Sans aucune partie, JOUER joue** (dans la 1) : trois fois « NOUVELLE PARTIE » devant
  quelqu'un qui ouvre le jeu, c'est un menu qui ne choisit rien.
- ⚠️ **Une ville posée pour une partie ne sert pas à une autre** : `commencer()` sait
  reposer la MÊME partie après un retour au titre, pas oublier tout ce qu'une autre a laissé
  (sang, lampadaires cassés, phase des chantiers, compteurs accrochés à `B`). Changer de
  partie après avoir joué **recharge la page**, et le choix se rouvre tout seul sur la case
  prise (drapeau dans `sessionStorage`, qui porte le NUMÉRO : Chromium a attrapé qu'une case
  vide rouvrait sinon sur la première partie existante) — il reste un ACTION à faire, et
  c'est ce geste-là qui rend le son. Même règle pour la même case effacée ou écrasée depuis.
- ⚠️ **Une partie effacée ne revient pas** : effacer ou écraser la partie chargée la
  remplace aussi en mémoire (sinon la sauvegarde automatique la réécrit dix secondes plus
  tard), et les deux confirmations s'ouvrent sur **NON**. Copier recopie **à l'octet** (pas
  de passage par `completer()`). La date part avec la copie écrite (`sauveeLe`), jamais dans
  `B.partie`.
- ⚠️ Entrée sur le bouton JOUER qui a le focus faisait un clic ET un ACTION : le clic
  ouvrait le choix et l'appui y choisissait aussitôt — le clic vide les touches. Le banc
  sait maintenant démarrer sur un stockage déjà rempli
  (`banc(corps, stockage=…, session=…)`) et compte les rechargements (`o.rechargements()`).
  **13 juges de banc** (`test_parties_js.py`, tous au bouton) **+ 1 Chromium** (le vrai
  rechargement), **24 mutations, toutes rouges**.
- ⚠️ Pour M14 : les trois emplacements par compte existent déjà côté navigateur, le serveur
  n'aura qu'à les refléter.
