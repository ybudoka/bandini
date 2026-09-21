# Les donneurs ne se cachent plus derrière le décor

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (20 sept. 2026), avec une capture de Ti-Paul devant son dépanneur : « ici Ti-Paul est
caché par l'arrêt, mets un garde pour éviter ça ».

- ⚠️ **Mesuré avant**, au banc : `Histoire.poserDonneur` met le personnage à deux tuiles de sa
  porte sans regarder ce qui se peint devant lui. La ville se peint du nord au sud (`Entites.dessiner`
  trie par `y`) : l'abribus (26 × 28 px) une tuile plus bas passe DEVANT Ti-Paul, à 216, 808, et il ne
  reste que sa tête. Des cinq donneurs du dehors, Ti-Paul est le seul dont le sprite est entièrement
  sous du décor (100 % de son rectangle) ; Ti-Guy en a un tiers sous une roulotte à café. Les quatre
  donneurs du dedans n'ont rien devant eux.
- **Le garde : `placeVisible`.** La première tuile est celle d'avant (deux tuiles de la porte, d'un
  côté puis de l'autre) : un donneur que rien ne cache ne bouge pas d'un pixel. Si du décor peint
  après lui en recouvre la moitié ou plus (`partCachee`, `CACHE_MAX` 0,5), on essaie neuf tuiles de
  trottoir dans un ordre fixe, du plus près au plus loin de la porte (hors du pas de la porte, sans
  décor solide dessus), et l'on prend la première où on le voit — sinon la moins cachée. Ti-Paul
  passe à 136, 808 : trois tuiles à gauche de la porte, entre le poteau de l'arrêt et le guichet.
  Aucun dé (`creerPieton` en tire deux, comme avant, une fois), aucune ville qui change : c'est un
  placement à la partie, pas à la génération.
- **Vu en vrai** : capture Chromium avant (la tête au-dessus de l'abribus, comme sur la capture de
  Martin) et après (Ti-Paul en entier, de face, devant la façade).
- **Deux juges** (`test_donneurs_visibles_js.py`) : aucun des neuf personnages de l'histoire, dedans
  ou dehors, n'est caché à moitié — calcul refait dans le juge avec les vraies dimensions du sprite,
  pour ne pas être d'accord avec la fonction du jeu quand elle se trompe — et un donneur reposé (le
  debug le fait) se tient au même endroit et consomme les deux mêmes dés. ⚠️ Rouge avant :
  « tipaul est caché à 100 % par abribus ».
- ⚠️ **Ce que ça ne couvre pas** : le calcul compte les rectangles des fiches, pixels transparents
  compris (prudent) ; les personnages que les missions posent autrement (le fuyard, la cible, le
  client) ne passent pas par `poserDonneur` ; et la roulotte de Ti-Guy (un tiers) reste sous le seuil.
