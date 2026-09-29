# Le tunnel, sa falaise et le passage à niveau en 2.5D

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (29 sept. 2026), sur une capture du passage à niveau devant le tunnel : « améliore
ça, il faut que ce soit 2.5D ». Tout ce qui touche au train y était peint à plat au milieu
de bicoques et de chars en volume : un rectangle gris pour le portail, des lignes pour la
voie, deux pixels pour les feux, un trait qui glisse au sol pour la barrière — et une
falaise striée à l'horizontale comme une façade, dans une bande qui court du nord au sud. Ce
qu'on fait (design approuvé par Martin, falaise comprise) : le portail devient un ouvrage de
béton encastré (chaperon, face, arc qui s'enfonce dans le noir, murs en aile, ombre au
sol) ; la voie a son talus de ballast, ses traverses en relief et l'ombre de ses rails ; les
signaux sont des poteaux debout (mât, ombre, croix de Saint-André, deux feux) ; la barrière
pivote en volume — dressée levée, en arc à la descente, à hauteur de capot baissée avec son
ombre sur l'asphalte, un moignon cassée ; la falaise `C` lit ses voisines (le côté ville, le
côté montagne) et se peint en paroi : la crête éclairée du nord-ouest, des arêtes qui
descendent, les éboulis au pied.

- ⚠️ Rien de la ville ne bouge : du dessin seulement — pas une tuile, pas un dé, ni
  collision ni horaire.

## Notes

**Livré le 29 sept. 2026.** Du dessin seulement : ni tuile, ni dé, ni collision, ni horaire.

- **La voie** (`Train.dessinerVoie`) : un talus de ballast (l'arête nord au soleil, le flanc sud sombre, son
  ombre au pied), des traverses dont on voit le chant, des rails debout (le champignon, l'âme, l'ombre au sud).
  Au passage, le tablier de caoutchouc reste au ras de la rue, les rails noyés, leur ornière sombre.
- **Les barrières** (`Train.barrieres`, `peindreBarriere`) : un mât debout (24 px), la croix de Saint-André,
  deux feux sur leur traverse, chacun sa visière et son halo quand il est allumé ; à côté, le boîtier du bras
  et son contrepoids. Le bras **pivote** : dressé ouvert, en arc à la descente, couché à 7 px (hauteur de
  capot) une fois baissé, penché sous le niveau quand on l'a défoncé. Les ombres (mât, bras) tombent au
  sud-est, au sol, sous les gens. Les poteaux entrent dans le **tri des visibles** par leur pied
  (`ajouterVisibles`), même quand le train est loin : on passe derrière celui du nord, devant celui du sud.
- **Le portail** (`dessinerBouche` au sol, `dessinerPortail` en haut) : une ouverture en pierre tombale, du
  bord sud du ballast jusqu'à la voûte arrondie au nord. ⚠️ **La hauteur se peint au nord** (`y - z`) : une
  bouche centrée sur les rails laissait le toit de la locomotive dépasser sur la roche. Autour : les piédroits
  et la voûte (intrados sombre, arête claire), la clé, le chaperon du mur de tête posé sur la pente, deux murs
  en aile pleins, l'ombre au sud-est.
- **La falaise** (`varianteDeFalaise` dans `monde.js`, `falaise` dans `sprites.js`) : la tuile `C` lit ses
  voisines — où est le bas (ni `C` ni `M`), où est le haut (`M`). Dans la chaîne de l'est, la roche
  s'éclaircit du pied à la crête en tons tramés, des corniches descendent la pente (le rebord au soleil,
  l'ombre dessous), la crête est une lèvre claire soulignée d'un surplomb noir, et le pied porte ses éboulis.
  ⚠️ **Une paroi tournée vers le nord ne se voit pas** (on regarde du sud, d'en haut) : les falaises du large,
  l'eau au nord, ne montrent que le rebord du plateau et sa lèvre au bord de l'eau.
- Juges : `test_la_barriere_pivote_en_volume`, `test_les_poteaux_du_passage_se_trient_avec_les_gens`,
  `test_la_falaise_sait_ou_est_sa_crete` (`test_train_js.py`), chacun vu rouge sous sa mutation.
