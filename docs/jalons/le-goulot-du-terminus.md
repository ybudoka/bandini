# Le goulot du terminus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Trouvé le 30 sept. 2026 en livrant [la foire fermée l'hiver](la-foire-fermee-l-hiver.md) ; Martin : « le corriger
maintenant ». `test_la_foule_ne_se_traverse_plus` tombe pour 3 graines sur 10 sur dev, et sur sa graine par
défaut depuis que le jongleur revient en janvier : au terminus, sur le trottoir d'une tuile entre la façade et
l'abribus (autour de la tuile 128, 125), deux passants qui se croisent s'enfoncent l'un dans l'autre et y
restent (« creuse » : le chevauchement grandit deux images de suite). Aucun n'est figé ; ce sont deux
flâneurs face à face dans un passage où `demeler` n'a nulle part où les écarter.

Correctif, sans un dé et sans rien déplacer. Juge : le geste rejoué à la main, et
`test_la_foule_ne_se_traverse_plus` sur onze graines.

## Notes

- **Ce n'était pas un goulot** : le trottoir fait quatre tuiles à cet endroit. La sonde a montré le joueur à
  8-9 px de chaque paire qui creusait — c'est LUI qui, au départ de la partie, marchait dans la foule du terminus
  et écrasait un passant contre un autre corps (un passant, Momo planté à son poste). Le juge écarte les paires
  qui touchent le joueur, pas un troisième corps pris entre les deux.
- **Le mécanisme** : coincé, le passant recevait deux poussées opposées de `demeler` qui s'annulaient, et le
  joueur, qui avançait encore, l'enfonçait dans l'autre. **Le correctif** : un passant qui touche déjà quelqu'un
  d'autre — chevauchement ou contact à un pixel près (`coinceParAutre`) — ne recule plus devant le joueur ; la part
  que le joueur lui donnait, le joueur la reprend, et il se bute comme contre un mur.
- **Mesuré** : `test_la_foule_ne_se_traverse_plus` passe sur 11 graines sur 11 (7 sur 11 sur dev, dont sa graine
  par défaut : 15 gros chevauchements, 6 creusements) ; le geste seul (`tests/test_goulot_du_terminus_js.py`)
  s'enfonçait de 2,35 px sur dev, de 1,11 avec le seul chevauchement, de moins d'un pixel avec le contact.
