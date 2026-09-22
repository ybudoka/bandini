# Suivre sans se faire voir : le stool attend qu'on soit au volant, roule jusqu'au poste, et le filage tolère un écart

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « mission deuxième service impossible à faire, on se fait voir tout
de suite en sortant de la cantine ». Trois défauts de l'objectif `suivre` (f06, et h02 qui
le copie). (1) Le stool naît sur la tuile de rue la plus proche de la porte du casse-croûte
(`poserLeFuyard`, fait pour m50) : on sort à pied à moins de 3 tuiles de lui, `proche`
échoue à la première image. (2) Il roule en `fuite` + `poursuite` : il brûle les feux et
prend la sortie qui l'éloigne de toi — à pied, le temps de trouver un char, il est à plus de
10 tuiles. (3) `suivre` n'a AUCUNE condition de réussite : rien ne lit de `lieu`, le juge du
banc force l'étape à la main. Le correctif : un stool à part du fuyard — il naît à bonne
distance de la porte, moteur en marche, et attend que tu sois au volant ; il roule comme le
trafic (feux, vitesse de ville) vers le `lieu` de l'objectif (`poste` pour f06, `depanneur`
pour h02), aux croisements par `Monde.cheminRoute` ; l'objectif avance quand il y arrive ;
trop près ou trop loin se tolère un moment (un avertissement au HUD, puis l'échec), comme le
tracé des courses. Juge de banc : sortir du casse-croûte par la porte ne rate plus, et une
filature jouée jusqu'au poste finit la mission.

## Notes

**Livré le 22 sept. 2026.** Reproduit au banc avant de toucher à rien : sorti du casse-croûte
par la porte, le stool était à 44 px (`proche` = 48), et la mission ratait à l'image qui
suivait la réplique de Bouchard — trois graines sur trois.

- **Un stool, pas un fuyard** (`Histoire.poserLeSuivi`). Il naît entre `proche` et `loin` de
  la porte (cinq tuiles au moins), sur une voie **libre devant lui** : sans ça, il naissait
  en amont de notre char garé devant la porte, dans la même voie, et restait coincé derrière
  quinze secondes avant de le pousser. Moteur en marche, il attend qu'on soit au volant
  (`attendLeJoueur`, 45 s au plus), et la ligne d'objectif le dit (« — PRENDS UN CHAR »).
- **Il va quelque part** : `lieu` dans l'objectif (`poste` pour f06, `depanneur` pour h02 —
  deux lieux déjà de mission, la ville ne bouge pas). `v.destination` = la voie la plus
  proche de la porte ; aux croisements, `Vehicules` prend la sortie dont le chemin de
  chaussée (`Monde.cheminRoute`) est le plus court. Il roule comme le trafic : feux, stops,
  vitesse de ville. L'objectif avance quand **il** arrive. Sonde : six traversées de la ville
  (jusqu'à 2 500 px, 75 s), toutes arrivées, aucun déblocage.
- **Une marge, et on la voit** : trop près, la méfiance monte (1,5 s) et redescend quand on
  recule — « — TROP PRÈS ! » ; trop loin, cinq secondes pour le retrouver, comme le tracé des
  courses — « — TU LE PERDS ! N S ». ⚠️ Trop près ne compte que **dans son rétroviseur**
  (derrière lui ou à côté) : en démarrant, il passe à la hauteur de notre char garé.
- À la fin, réussie ou ratée, son char repart dans le trafic au lieu de disparaître sous nos
  yeux. Le percuter jusqu'à l'épave, ou lui voler son char : il nous a vus.
- Juges (`test_dix_missions_js.py`) : f06 jouée comme Martin (garé, dedans, la porte, le char,
  filé jusqu'au poste, payé) ; trop près et trop loin ; h02 jusqu'au dépanneur. L'ancien juge
  forçait l'étape à la main. Mutations : l'ancien `histoire.js`, l'attente retirée et le
  rétroviseur retiré font chacun rougir un juge.
- ⚠️ Du casse-croûte au poste, la filature dure de 15 à 20 s : le poste est à deux coins de
  rue. Si c'est trop court au goût de Martin, c'est le `lieu` ou un détour qui changent, pas
  le moteur.
