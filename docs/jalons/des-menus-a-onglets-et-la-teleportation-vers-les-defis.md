# Des menus à onglets, et la téléportation vers les défis

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22 sept. 2026) : « ajoute aux triches une téléportation vers les
différents défis, et profites-en pour remanier tous les menus pour que ce soit plus
convivial et plus facile de s'y retrouver — possiblement avec des onglets cliquables ou
déplaçables avec les touches R et L ». (1) La PAUSE devient un classeur à onglets : PAUSE ·
CARNET · BILAN · COMMANDES · OPTIONS · TRICHES (TRICHES seulement après la suite secrète).
On tourne l'onglet aux épaules de la manette (LB/RB, L1/R1, L/R : le 2e bouton d'ARME et de
FRAPPE, celui que le dessin de l'écran MANETTE appelle déjà `epaule_g`/`epaule_d`), à la
croix, aux flèches ← → (les lettres R et L du clavier sont celles de la suite RIGOLO, elles
restent hors de `MAP_TOUCHES`), ou en touchant/cliquant l'onglet. Chaque onglet s'ouvre au
même endroit, dans une boîte de taille fixe ; les sous-pages (journal, répertoire, manette,
sauts) gardent la barre d'onglets et leur titre dessous. Le pied de la boîte montre les
VRAIS boutons de l'appareil qu'on tient. B (ou Échap) recule d'une sous-page, et depuis un
onglet reprend la partie. (2) Les lignes de tous les menus se touchent et se cliquent (le
moteur est commun aux comptoirs). (3) Les TRICHES se rangent en sections (le joueur, aller,
la mission, divers) sans le sous-menu PLUS…, et la suite secrète ouvre le classeur sur
l'onglet TRICHES. (4) SAUT VERS UN DÉFI : la liste de `B.defs.defis` (le catalogue fait la
liste) ; choisir pose le joueur devant le panneau ou le comptoir de foire (hors du char,
hors de la pièce), tourné vers lui, et ouvre la proposition du défi (COMMENCER / PAS
MAINTENANT). Un défi en cours est abandonné sans rien noter. Juges : par le bouton (épaules
de la manette de Martin en Bluetooth, croix sur un axe), chaque défi du catalogue
atteignable par le saut, et des captures du classeur sur les trois appareils.

## Notes

✅ **Livré** (22 sept. 2026).

- **La PAUSE est un classeur** : six onglets (`ONGLETS` dans `hud.js`) — PAUSE (reprendre, carte,
  photo, sauvegarder, quitter), CARNET, BILAN, COMMANDES, OPTIONS, et TRICHES seulement dans une partie
  où la suite secrète a été tapée. La boîte a le **haut fixe** et la rangée d'onglets est centrée sur
  l'**écran** : COMMANDES (476 px) est plus large que les listes (320 px, les pouces du téléphone
  couvrent le reste), rien ne glisse quand on tourne. Une page ouverte depuis un onglet (journal,
  répertoire, fiche, manette, sauts) est une **sous-page** : elle hérite de l'onglet (`ouvrirMenu`), son
  titre s'écrit sous la rangée, B recule. Depuis un onglet, B, FRAPPE, ÉCHAP et START reprennent la
  partie : les lignes RETOUR des pages de tête sont parties.
- **Tourner l'onglet** : les **épaules** (`Entree.neufEpaule` — le NUMÉRO du 2e bouton d'ARME et de
  FRAPPE, la pièce que le dessin de l'écran MANETTE appelle déjà `epaule_g`/`epaule_d` ; LB/RB, L1/R1
  ou L/R selon la famille, dessinés de part et d'autre de la rangée), la croix, les flèches ← → (les
  lettres R et L du clavier sont celles de la suite RIGOLO : hors de `MAP_TOUCHES`), ou le doigt/la
  souris sur l'onglet. ⚠️ RB est aussi FRAPPE, qui ferme un menu : l'onglet se lit AVANT la fermeture,
  et une page qui vient de changer ne se ferme pas dans la même image. Sur l'écran MANETTE et
  RÉAPPRENDRE (`epaulesInertes`), les épaules s'essaient sans tourner ; sur COMMANDES, la croix
  s'allume sans tourner (les épaules tournent), et ses deux pages se tournent en HAUT/BAS.
  ⚠️ Au doigt, seul un geste franchement de côté tourne : une diagonale du pouce monte dans la liste.
- **Tous les menus** (le moteur est commun aux comptoirs) : chaque ligne qu'on peut choisir se touche et
  se clique (`toucherMenu`, lu dans la boucle à l'image suivante — la toile est étirée en CSS, on ramène
  le point aux 480 × 270 pixels) ; les titres de section (`entete`) que le curseur saute. Le pied du
  classeur dessine les **vrais boutons** de l'appareil qu'on tient (A/B, E/ÉCHAP, ou « TOUCHE UN ONGLET »),
  sans promettre CHOISIR sur une page qui ne se lit que (le BILAN n'a plus de curseur).
- **Les TRICHES en sections** (le joueur, aller, la mission, divers), sans PLUS… ; la suite secrète
  ouvre la pause sur leur onglet — et tapée DANS la pause, elle y tourne.
- **SAUT VERS UN DÉFI** (`menuSautDefis`) : le catalogue rangé au volant / les tours / la foire ; on sort
  du char et de la pièce sans fondu, on se pose sur la tuile à pied la plus proche d'où ACTION lit le
  panneau (ou le comptoir de la baraque : hors décor solide, à portée), tourné vers lui, la pause se
  referme et la proposition s'ouvre (COMMENCER / PAS MAINTENANT). Un défi en cours est abandonné sans
  rien noter (`Histoire.abandonnerDefi`, et le forain reprend sa carabine).
- **Juges** : `test_classeur_js.py` (sur la manette de Martin en Bluetooth, `bt_dinput`, croix sur
  l'axe 9 : épaules, croix, FRAPPE ; clavier ; sous-page ; écran MANETTE ; sections ; toucher ; rangée
  immobile et lignes entre les pouces ; diagonale du pouce) et six juges du saut dans `test_debug_js.py`
  (chaque défi du catalogue atteint, ACTION relit le panneau et COMMENCER lance, char et pièce,
  abandon, scène). Les juges de la pause, des triches, de COMMANDES et de MANETTE suivent le classeur.
  **Quinze mutations, toutes rouges** — et des captures Chromium du classeur au clavier, à la manette et au téléphone
  (844 × 390) : elles ont fait ranger les deux pages de COMMANDES à gauche (« AU VOLANT » tombait sous
  le bouton PAUSE du téléphone) et retirer les vieilles aides texte du journal.
- ⚠️ **En coop locale**, l'épaule ne tourne l'onglet que si c'est le joueur 1 qui tient la manette
  (`Entree.joueur1PrendLaManette`, arrivé sur `dev` pendant ce jalon) : sinon le deuxième joueur
  feuillette le classeur de l'autre en jouant.
- ⚠️ **Quinze juges sont rouges sur `dev`** à ce jour, tous confirmés à l'identique sur `dev` nu par
  la session du large de l'aéroport (`f011716`) et rejoués ici sur `f5dbc7a` : `test_moteur_js` × 4
  (la foule, courir dans la foule, le poste tenu, le budget de la bagarre), `test_ondes` (la voix de
  la police), `test_histoire_js` × 2 (les cravates de M2, les repos à voix haute), `test_abri_js`
  (la balle dans la tôle), `test_definitions` (le paquet), `test_interieurs_js` (un comptoir dessiné
  non servi), `test_missions_en_scene_js` × 3 (f04, p01, h02), `test_interieurs` (l'hôpital) et
  `test_navigateur` (les échantillons). Aucun de ce jalon.
