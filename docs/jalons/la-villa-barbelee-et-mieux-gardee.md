# La villa barbelée et mieux gardée

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « la villa devrait avoir des clôtures barbelées et plus de gardes ».
Tranché par Martin : la palissade de bois reste, mais **surmontée de barbelé** — elle ne
s'enjambe plus ; on entre par le trou où manque une planche (au nord) ou par la grille, qui a
son garde. La réplique de Josée ne change pas. Et **cinq gardes de plus** : deux dehors, un au
rez-de-chaussée, un à l'étage, un à la cave — « gardée comme une banque ».

- ⚠️ Un glyphe neuf pour la palissade barbelée : peu courant (les glyphes libres se disputent
  entre sessions), `cloture: barbele` (solidité 5), dessinée en bois avec ses rangs de barbelé.
- ⚠️ Chaque mission de la villa (v01, v02, v03) doit rester faisable au banc, et l'arrivée
  d'un escalier rester un refuge (le juge de la session `garde-escalier-villa`).

En cours de route, Martin (même jour) : « ajoute même deux étages intermédiaires avant la fin » —
tranché : un **2e étage** entre l'étage et le bureau (v02 et e07 montent plus haut), un
**sous-sol** entre la cave et la chambre forte (v03 descend plus bas), deux gardes chacun. Et
« teste-le et vois si des endroits pour se cacher sont requis » : ils l'étaient dehors — tranché,
des **haies de cèdres** ; et la mission durait plus qu'une nuit — tranché, **la nuit tient**
dans la villa.

## Notes

### Livré (30 sept. 2026)

- **La palissade barbelée** (`'` dans `carte.LEGENDE`, solidité 5) : les planches de la palissade,
  plus basses, et deux brins de barbelé par-dessus, leurs épines en petits x (serrées comme
  celles du barbelé, elles faisaient une bande blanche pleine : vu à la capture). Tout le tour
  du terrain, sauf le trou du nord et la grille — un juge le compte.
- **Dix-sept gardes** au lieu de huit (`villa.GARDES`) : un deuxième tour du jardin en sens
  inverse (parti du coin nord-est, il croise l'autre à l'ouest et à l'est, jamais devant le
  trou), la pelouse de l'est, le salon, les chambres de l'étage, le cellier ; au 2e, le
  corridor et la bibliothèque ; au sous-sol, le couloir de la voûte (il tourne à huit tuiles
  du terminal : on pirate dans son dos) et la salle des serveurs.
- **Deux étages de plus** (la carte passe de 70 à 94 rangées, deux cadres de plus) : l'ancien
  bureau de l'étage est une bibliothèque dont l'escalier monte au **2e étage** (les
  appartements du maire, le bureau au fond) ; l'ancienne chambre forte de la cave est une
  antichambre dont l'escalier descend au **sous-sol** (la réserve, la chaufferie, les
  serveurs, le terminal et la chambre forte). Les lieux `villa_bureau`, `villa_terminal`,
  `villa_voute` et la serrure de la voûte ont déménagé ; les juges les lisent dans
  `villa.LIEUX` et `villa.SERRURES` au lieu de coordonnées en dur.
- **Les cachettes** : ce que le banc a montré. Seul un mur coupe la vue d'un garde
  (`Monde.ligneLibre`) — ni un arbre, ni une palissade — et dehors, tout le terrain était vu
  (la carte de surveillance : chaque tuile du jardin à moins de six tuiles d'un point de ronde,
  sans mur). D'où **37 tuiles de haie de cèdres** (`` ` ``, solidité 1) : une poche de chaque
  côté du trou, des barres en travers de la bande ouest, un abri devant la porte de service,
  des îlots au nord, au sud et à l'est. Dedans, les pièces de côté suffisaient.
- **La nuit tient** (`nuit_tient` dans la fiche du bloc, `Monde.majHeure`) : de nuit, l'horloge
  s'arrête tant qu'on est dans la villa ; de jour elle avance, et dehors la nuit repart.

⚠️ **Une ronde ne traverse plus un meuble** (`blocs.erreurs`) : le même jour, dev a fait arrêter un
garde par un meuble, et le garde de l'ancienne chambre forte restait pris sur les deux machines de
(55, 60) que sa ronde traversait depuis le début — v03 rougissait. Sa ronde tourne à la colonne 57 ;
celle des serveurs évite le moniteur.

⚠️ **Le banc a dû apprendre à se cacher** (`cachette`, `surveillee` dans
`tests/test_infiltration_js.py`). Il savait attendre et reculer ; au 2e, le garde du corridor
le parcourt d'un bout à l'autre et le banc restait onze minutes à la porte du bureau. Il se
glisse maintenant dans une pièce qu'**aucune ronde ne voit jamais** et laisse passer. Une
cachette « derrière la haie, là, maintenant » l'a rendu pire (il ne prévoit pas où le garde
tourne) : le banc ne prouve donc pas que les haies aident — ça se juge en jouant.

⚠️ Mesures au banc (joueur prudent, de nuit) : v02 et e07 en ~5 minutes réelles, dont 76 s
d'attente devant le trou et ~2 min 30 pour redescendre du bureau. Sans la nuit qui tient,
l'aube tombait avant la sortie (vers 11 h du matin).
