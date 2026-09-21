# Une barre de chargement, et l'icône qui tourne

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026) : « je prendrais bien une barre de chargement au lancement
du jeu. et s'il y a des chargements dans le jeu, un petit icône s'animant dans un coin de
l'écran ». Aujourd'hui le lancement n'a qu'une ligne de texte (`#etat-chargement`) pendant
les deux requêtes (les définitions et la carte, à part depuis « La carte sort du paquet »)
et le préchauffage des mp3 de l'ouverture ; en jeu, l'audio se charge à l'usage (`son.js` :
`fetch` puis `decodeAudioData`) sans que rien ne le dise.

- ⚠️ À mesurer avant de dessiner : ce qui se charge vraiment, et combien de temps, sur le
  téléphone de Martin

**Livrée le 17 sept. 2026.**

- ⚠️ **Mesuré d'abord** (Chromium, Fast 3G, processeur ×4) : l'écran titre arrive à **10,7
  s** — les **20 scripts** jusqu'à 7,2 s, les définitions et la carte jusqu'à 10,3 s, la
  ville qui se bâtit le reste ; puis la musique et les voix de l'ouverture se chargent
  encore **quatre secondes** derrière le titre. **Livré** : la barre du titre
  (`#chargement`, un cadre doré et des briques qui avancent par pas) — `chargement.js`,
  chargé **en premier**, compte les scripts à mesure qu'ils arrivent (60 % de la barre ; un
  fichier et pas un script en ligne, la sécurité du serveur peut refuser ces derniers) ;
  `jeu.js` continue **à l'octet près** sur les deux requêtes, contre la taille décompressée
  que le serveur annonce (`X-Octets` : derrière nginx, la longueur de la réponse est celle
  du gzip) ; la ville bâtie, elle fait son dernier pas et s'efface. Jamais à reculons. **Et
  l'icône** : `Chargements` compte ce qui se télécharge (les six chemins de l'audio passent
  par un seul, `Son.decoder`, et le préchauffage lit le corps) ; le HUD montre huit briques
  qui tournent au **coin bas-gauche** — au bord de la boîte de dialogue sans la toucher,
  contre la mini-carte en tactile (la croix tient le coin) — **après 12 images** de
  chargement (un bruitage en cache ne la fait pas clignoter) et **20 images de plus** après
  le dernier.
- ⚠️ Pas pendant une scène : le HUD s'y tait.
- ⚠️ **Pendant le chargement, l'aide des touches cède sa place à la barre** : le cadre du
  titre était plein à ras bord, et la barre en plus coupait le logo en haut et
  « Chargement… » en bas (vu en Fast 3G) ; elle revient avec l'écran titre, identique à
  avant. Juges : `test_chargement_js` (le compte, le son qui s'y inscrit, l'icône
  brève/longue/qui s'attarde/par-dessus rien), `test_routes` (`X-Octets`, le nombre de
  scripts annoncé), `test_navigateur` (la barre avance pendant les scripts ET pendant les
  octets, finit à 100, s'efface) — chaque règle retirée fait rougir son juge.
