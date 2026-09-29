# Douze juges rouges sur dev, avant la prod

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

La suite complète sur `407de5d2` (le SHA qu'on voulait mettre en prod) a douze rouges, qui
tombent aussi seuls, sans la charge. Huit dans `test_devants`
(`test_aucun_abribus_ne_colle_la_porte_d_un_lieu_de_mission`,
`test_le_temoin_a_bien_des_abribus_colles` : `KeyError: 4`), venus des commits d'après
`442e6ffb` ; `test_donneurs_visibles_js` (Cindy « pas là ») rouge déjà sur `0bdabaa1` ; et
trois des deux-roues remisés (`442e6ffb`) mêlés au train et au dojo : le clignotant rouge la
nuit et le public des amuseurs (des juges qui tiennent à l'état de la rue de janvier) et
deux autobus dans la même boîte (`test_trafic_js[23]`, seule graine sur trente, seulement
sur le build — à tracer). Chaque rouge : sa cause, puis sa correction ou son juge recalé,
puis la suite complète sur le SHA exact, puis la prod.

## Notes

**Livré le 29 sept. 2026.** Douze rouges, deux vrais défauts du jeu, et chacun sa cause :

- **Deux autobus dans la même boîte** (`test_trafic_js[23]`) — **un vrai défaut** : un autobus que
  l'horaire faisait naître entre la tuile d'avant la ligne d'arrêt et la boîte ne demandait jamais le
  feu, le stop ni la réservation (`peutEntrer` ne se pose qu'en arrivant sur la tuile d'avant la ligne),
  et il traversait. `Autobus.faireNaitre` le fait naître au regard suivant, sans dé. Sur 40 graines ×
  2 000 images : 1 entrée sans réservation sur la base (la 23), 0 après. La circulation d'hiver des
  deux-roues remisés (442e6ffb) n'a fait que l'amener là.
- **Les personnages qui arrivent après une mission** (`arrive_apres` : Cindy après q04, Diane et Jo
  après e01, Zed, le Trappeur, Ti-Loup, Boulon, Prévost…) — **un vrai défaut** : ceux du dehors ne se
  posaient qu'au CHARGEMENT d'une partie ; le joueur qui finissait q04 ne trouvait Cindy qu'après avoir
  rechargé. La fin de la mission les pose (`Histoire.poserDehors`, dans la ville même si la fin se joue
  dedans), comme elle retire déjà ceux qui partent. Juge : `test_personnages_tardifs_js.py` (rouge sans).
- **Huit abribus** (`test_devants`, `KeyError: 4`) : depuis b729a387, quatre donneurs attendent devant
  le dépanneur, et la table `AIR` écrite à la main du juge s'arrêtait à trois. Le jeu le faisait déjà
  (2×n+1) ; le juge prend `4: 9` et dit en toutes lettres un lieu qu'il ne connaît pas.
- **Les donneurs visibles** (Cindy « pas là ») : depuis 9ee0ae6f (`arrive_apres`), un personnage peut
  n'être pas encore arrivé ; le juge exigeait tout le monde à la naissance. Il regarde maintenant les
  arrivés à la naissance, puis les tardifs une fois leur mission faite.
- **Le clignotant la nuit et le public des amuseurs** : des juges qui tenaient à la rue de janvier
  d'avant les deux-roues remisés ; ils retirent la clé `remise` (la recette de `test_velos_js`).

