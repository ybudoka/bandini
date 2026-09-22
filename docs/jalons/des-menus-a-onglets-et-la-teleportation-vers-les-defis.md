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
