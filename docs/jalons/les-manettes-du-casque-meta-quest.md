# Les manettes du casque Meta Quest

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « ajoute le support des manettes sur casque vr meta quest ».

- ⚠️ **Vérifié dans la doc Meta d'abord** (`webxr-pro-controller`) : les manettes Touch ne
  se lisent que par le **gamepad d'une session WebXR** (`XRInputSource.gamepad`, disposition
  `xr-standard`) — une page 2D ne les voit pas dans `navigator.getGamepads()`, elles n'y
  font que pointer. Et une session immersive n'affiche rien de la page. **Livré**
  (`casque.js`) : un bouton **JOUER DANS LE CASQUE** au titre, montré seulement si
  `isSessionSupported('immersive-vr')` (la gâchette qui le clique est un vrai geste : la
  session **et le son** partent du même clic), qui fait ce que fait JOUER — le **choix des
  parties**, un menu de la toile qui se voit et se choisit dans le casque ; le jeu sur un
  **écran virtuel** fixe dans la pièce (2,4 m à 2 m, la toile copiée en texture chaque image
  à l'échelle 3, fond noir du jeu) ; c'est **la session qui cadence** (la boucle de la
  fenêtre se tait, sinon le monde avancerait deux fois). Les deux Touch sont rendues à
  `Entree` comme **une manette Xbox**, dans un quatrième sac lu toujours avec la disposition
  par défaut : A action, B courir/retour, X frapper, Y arme, poignées = épaules (arme,
  frapper), gâchettes = frein et gaz, **clic du stick gauche = PAUSE** (xr-standard ne
  promet pas le bouton ☰ ; le jeu le dit en entrant), clic du stick droit = CARTE, stick
  gauche = marcher, stick droit = la croix des menus ; les vibrations passent par les mains.
  Le menu du Quest par-dessus la partie la met en pause ; toute **voile DOM** (le titre —
  la seule qui reste depuis le retrait du tableau des scores) **fait sortir du casque**, et sortir du casque ramène au titre,
  partie sauvegardée — hors du casque, un joueur de Quest n'a plus aucune manette (même
  règle quand on en sort pendant le choix des parties, et quand un changement de partie
  recharge la page : sur un navigateur qui ouvre un casque, le titre revient au lieu du
  choix rouvert). **Juges** : `test_casque_js.py` (14, tous par le bouton et par la
  session : la gâchette sur le bouton lance la partie, la fenêtre ne fait plus un pas,
  chaque Touch tombe sur son bouton Xbox, Bandini marche au stick, le char roule à la
  gâchette, PAUSE → QUITTER sort du casque, le menu du système pause, B annule un
  apprentissage, une main nue ne touche à rien, le choix des parties se joue à la Touch et
  rend le titre en sortant) et, dans `test_navigateur.py`, **un vrai WebGL** derrière un
  faux casque : quatre quarts de couleur peints sur la toile doivent sortir chacun à sa
  place (une texture absente, un écran derrière la tête ou une image à l'envers rougissent —
  vérifié en retirant chaque règle).
- ⚠️ **Pas encore essayé dans un vrai casque** (aucun Quest branché) : c'est à Martin de le
  dire.
- ⚠️ **WebXR exige une origine sûre** : `https://bandini.gestiondojo.ca`, ou
  `http://localhost:5400` par `adb reverse tcp:5400 tcp:5400` — l'adresse
  `http://192.168.x.x:5400` du réseau local **n'aura pas le bouton**
