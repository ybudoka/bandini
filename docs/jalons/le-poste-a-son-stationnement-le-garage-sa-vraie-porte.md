# Le poste a son stationnement, le garage sa vraie porte

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026) : « ajoute toujours un stationnement au poste de police avec
une ou des véhicules de police stationnés et aussi pour le garage, il faut une vraie porte de
garage où on stationne pour vendre ou faire des missions. la porte ouvre seule dès qu'on est
devant en voiture. »

- **Le lot du poste** (`carte._stationnement_de_service`) : le bout de bande que le poste
  laisse à côté de son bâtiment (trois tuiles sur la ville livrée), de la ruelle au devant —
  une rangée de cases nez au nord contre la ruelle, et l'allée qui descend jusqu'au boulevard.
  `SPECIAUX["P"]["stationnement"] = "police"` dit quel char s'y gare, `garees` combien (une
  place reste libre dès trois : on s'y gare pour entrer au poste). ⚠️ Pas `_stationnement` :
  un lot générique en veut quatre de large et rendait trois tuiles d'asphalte nu.
- ⚠️ **Le lot et la porte se posent EN DERNIER** (`poser_les_lots_et_les_rideaux`, au bout
  de `generer`). Posé pendant la construction, le lot faisait passer vingt-sept tuiles de la
  dalle à l'asphalte : les nids-de-poule, les arbres de rue, les paquets, le métro tirent leur
  place dans des listes de tuiles, et **toute la ville a glissé** — 166 décors, les vingt
  paquets, la cale du cargo hors de sa barrière ; trois juges sans rapport sont tombés
  (barrières, autobus, défi). La baie du garage déplaçait neuf kiosques de la même façon. Vu
  par le diff des deux villes clé par clé ; un juge compare maintenant la ville avec et sans
  eux, **poseurs neutralisés** (neutraliser l'étape de la fin ne voyait pas un lot posé trop
  tôt) : rien ne bouge hors du lot et de la baie, et ce qui s'y serait posé s'en va.
- ⚠️ **La BORDURE du lot se vide aussi** : un meuble au bout d'une sortie de char ferme la
  sortie (`mobilier.SORTIES_DE_CHAR`), et le semis ne l'aurait pas posé là si le lot avait
  existé — un arbre, un parcomètre et un lampadaire bordaient l'allée, et
  `test_mobilier` l'a dit.
- **Les autos-patrouilles garées** (`Vehicules.majGaresDeService`) : nées hors champ, dans la
  bulle et en deçà de l'oubli (sinon elles clignotent), dans leurs lignes, sans conducteur, la
  couleur **donnée** (`creer` en tirait une au dé). Elles ne comptent pas dans le parc de la
  rue. On en vole une : l'alarme, à vingt pas du poste ; sa place reste vide tant que le char
  existe.
- **La porte de garage** (`carte.poser_porte_de_garage`) : deux tuiles `G` sur la façade, une
  tuile de mur entre elle et la porte des piétons, sa baie dégagée et pavée jusqu'au trottoir
  (la tuile unique d'avant était un dessin, deux cases à gauche de la porte) ; la pancarte de
  l'enseigne, qui pendait devant, passe à l'autre bout du bandeau. La tuile reste un
  **mur** : le char se gare devant, il n'entre pas sous le toit. Le rideau est peint par-dessus
  le sol comme un battant (`Monde.dessinerPortesDeGarage`), monte seul dès qu'un char conduit
  par le joueur est devant (quatre tuiles, une de marge), redescend 45 images après son départ,
  et roule en montant (`Son.SFX.rideau_garage`, synthétisé).
- **On se gare devant** (`Missions.majGarage`) : arrêté dans la baie, rideau levé, le menu du
  garage s'ouvre avec CE char — vendre (on descend d'abord), réparer, repeindre, assurer.
  ⚠️ **REPARTIR en tête, sous le curseur** : le menu s'ouvre au moment où l'on freine, donc où
  la main appuie sur ACTION pour descendre — deux pressions auraient vendu le char. ⚠️ Une fois
  par arrivée **du char**, pas du conducteur : on descend entrer à pied, on remonte, et le menu
  ne rattrape pas à la portière. Jamais pour le char d'une mission ni pendant une scène.
- **Les missions livrent devant le rideau** (`Histoire.lieuDeLivraison`) : « RAMÈNE-LE AU
  GARAGE » vise la baie et la flèche y mène ; le rayon ne change pas (la baie est à trois tuiles
  de la porte de Ti-Guy). ⚠️ Le panneau du défi « Livraison sans bosse » se plantait trois tuiles
  à l'ouest de la porte — pile dans la baie. Poussé à l'est, il tombait sous le nez de Marco et
  ACTION lui parlait au lieu de lire le panneau (`interagir` sert les personnages d'abord) : il
  s'éloigne par pas, hors de la baie et à trois tuiles de tout donneur ; ailleurs, rien ne change.
- ⚠️ **Avec M4** (« l'auto-patrouille attend au poste », livré le même jour) : celle de la
  mission naît sur une tuile de RUE devant la porte, jamais dans le lot (il n'a pas de flèche de
  voie). Le poste montre donc deux autos-patrouilles garées qui ne sont pas la sienne — la flèche
  mène à la bonne, et une place du lot reste libre (`stationnement_du_poste.places[garees]`) si
  l'on veut un jour l'y faire attendre.

Juges : 6 de ville sur trois graines (`test_poste_et_garage.py`) et 7 de banc
(`test_poste_et_garage_js.py`), l'arrivée au garage et le panneau **au bouton** (gaz, frein,
ACTION, BAS). 26 mutations, toutes vues rougir — dont « posé pendant la construction », qui ne
mordait pas tant que la ville témoin subissait la même mutation. Regardé dans Chromium : deux
autos-patrouilles dans leurs lignes et une place libre ; le rideau fermé, à mi-course, levé —
c'est la capture qui a montré la pancarte plantée devant la porte. 2887 tests.
