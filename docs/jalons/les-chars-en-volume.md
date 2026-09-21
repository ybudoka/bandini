# Les chars en volume

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin, après le vélo : « je veux que tu fasses une belle job comme ça avec les
voitures, commence par une et je te donne le go pour la suite ». Le char qui roule est son
**toit** (la pose `haut`, une vue plongeante de dos) tourné en 32 caps : vers l'est, un toit
couché sur le flanc, pas une auto de profil. ✅ **La berline, livrée** : l'auto, le taxi et
la police partagent **une seule carrosserie** (un juge le tient), donc convertir « une
voiture », c'est les convertir tous les trois. Elle est décrite en volume
(`MACHINE_BERLINE`) et projetée au cap comme le vélo, avec deux outils de plus dans
`Atlas.projeter` : la **silhouette de profil extrudée** (`profil` — capot et pare-brise en
pente, quatre passages de roue, ce qu'une boîte ne sait pas faire) et le **contour** `k` de
la silhouette, comme tout ce qui est dessiné à la main (le vélo n'en veut pas : ses tubes
d'un pixel en feraient des barres).

- ⚠️ **La livrée était rouge en dur** : la carrosserie commune peignait bande `y` et damier
  `x`, et l'auto les rendait « invisibles » en les mettant au rouge de sa palette — mais
  seul `c` suit la couleur tirée à la naissance, et une berline bleu marine aurait roulé
  avec une bande et un damier rouges dès que son flanc se dessinait. Le taxi et la police
  **ajoutent** leur livrée (`LIVREE`) ; l'auto n'en porte pas.
- ⚠️ **Des phares posés dans la caisse ne se voient que de face** (4 caps sur 32) : ils
  enveloppent maintenant le coin, et phare et feu se voient ensemble à 25 caps ou plus.
- ⚠️ **À trancher par Martin** (artefact « La berline de Bandini ») : de dos, le sol se voit
  du biais de l'ombre (0,5), et la berline occupe 21 rangées pour 28 px de long, là où le
  toit tourné en occupait 28. 1 juge neuf (la livrée s'ajoute, l'auto n'en porte pas —
  **rouge avant** en remettant la livrée sur l'auto), les juges des machines (roues au sol
  de profil, projection au cap, lampes) étendus à toute fiche en volume, et 9 juges de
  grille repris : l'ancre à la ligne de sol se juge sur la sport, le compte d'atlas admet
  une grille et un canevas par cap, et ceux qui comptaient les chars à toit en attendent
  sept. ✅ **Le cadre des vitres** (retour de Martin : « une légère séparation entre le
  pare-brise et le reste pour mieux démarquer de face et de dos ») : les montants bordaient
  les côtés, mais en haut et en bas la vitre touchait la tôle — bleu pâle contre le blanc de
  la police, on ne voyait plus où finissait le capot. Un trait `D`, l'ombre de la caisse
  comme les montants, ferme le pare-brise et la lunette ; ⚠️ celui du **bas** monte d'un
  demi-pixel sur la vitre et prend une avance de 1, sinon le capot passe devant lui au même
  pixel et il disparaît (vu au premier essai : le juge a rougi, le rendu d'essai l'avait
  posé en fin de liste). 1 juge neuf, **rouge avant** (« auto face : 20 pixels de vitre
  touchent la tôle sans cadre »). ✅ **Le go de Martin pour le reste du parc** (« tu vas
  pouvoir faire pareil pour les autres types de véhicule ») : ✅ **Le parc entier, livré** :
  sport, luxe, ambulance, remorqueuse, camion, autobus et chaloupe sont des machines
  projetées au cap, arrondies et cernées comme la berline, et **plus aucun char ne roule sur
  son toit** (874 lignes de grilles faites main en moins). Chacun garde ce qui le nomme : la
  **sport décapotable** dont on voit les deux sièges, la **luxe** longue et chromée aux
  vitres fumées, l'**ambulance** et sa caisse haute, sa croix sur les flancs et sur le toit,
  une rampe devant et deux feux derrière (sinon, vue de dos, sa caisse cachait la rampe), la
  **remorqueuse** et son plateau, le bras couché et le crochet, le **camion** et sa caisse à
  nervures, l'**autobus** et sa rangée de fenêtres, sa porte, sa girouette, la **chaloupe**
  et sa coque pincée, ses bancs, son hors-bord. La recette d'`habitacle` prend ses hauteurs
  et sa largeur en paramètres (la berline reste identique au pixel), et les aides communes
  (`caisseDeChar`, `passagesDeRoue`, `planPince`, `essieuDeChar`, `lampesDeChar`,
  `parechocsDeChar`) sont **préfixées** : ce fichier vit dans l'espace global.
- ⚠️ **Mesuré en chemin** : les fenêtres de l'autobus faisaient une seule bande de profil
  (la vitre, un pixel plus haut, gagnait sur son cadre au même rang — le cadre passe
  devant) ; les phares, posés dans la caisse, ne se voyaient ensemble qu'à 10 à 22 caps sur
  32 (ils enveloppent le coin : 25 et plus) ; les toiles du camion et de l'ambulance
  rognaient le toit vu de dos (64 et 60). 1 juge neuf, « tout le parc est en volume et sa
  toile ne rogne rien », **rouge avant sur ses deux règles** (une toile de 56 : « le camion
  rogne aux caps 11 à 21 » ; une fiche sans machine : « des véhicules roulent encore sur un
  dessin fait main : ['sport'] »).
- ⚠️ **Trois juges retirés, et pourquoi** : « le toit qui tourne porte les phares ET les
  feux », « les phares pointent où le char va » et « de dos un char montre sa longueur »
  mesuraient un TOIT tourné — il n'y en a plus ; leur règle est tenue cap par cap par « la
  machine se projette au cap et suit son ombre » (phare devant le feu à tous les caps, pour
  tout le parc). Celui de l'ancre à la ligne de sol est devenu le juge de la toile. 2265
  tests. 2189 tests
