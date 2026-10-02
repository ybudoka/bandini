# La façade du garage Bandini

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (2 oct. 2026)_, sur une capture du garage la nuit, char rangé dans la baie : « il faudrait ajuster
ça », puis « mets aussi la façade pleine largeur si possible ».

Deux défauts sur la même capture :

- **La façade s'arrête au milieu du rideau.** Le mur à étages d'un commerce s'étend jusqu'au bout de son bâtiment
  sur le mur nu (`F`, `W` : `Monde.murDuBatiment`, `etages._mur`). Le rideau du garage (`G`, deux tuiles) l'arrête,
  et la devanture de GARAGE BANDINI commence sur sa deuxième tuile (`GWDW`) : la façade (le bardeau, les fenêtres
  d'étage) ne couvre ni la première tuile du rideau ni la brique d'à côté. Ce qu'on veut : le mur va d'un bout à
  l'autre du bâtiment, le rideau percé dedans.
- **Le nez du char sort du toit.** Un char rangé au fond de la baie y a son centre, et son avant dépasse
  au-dessus. Le dessin ne le cache que sur la baie (`Monde.sousLeToit`) : le capot se peint par-dessus la façade, en
  tache brune.

**Juges** : le mur du garage couvre tout son bâtiment, rideau compris, et c'est la seule devanture qui bouge ; un
char au fond de la baie n'a plus un pixel au-dessus du toit.

## Notes

Livré le 2 oct. 2026.

- **La façade pleine largeur.** Le mur d'un commerce passe aussi sur un rideau de garage (`G`) : `rideaux` dans
  `etages._mur` et `Monde.murDuBatiment`, pour les devantures seulement (un logement garde sa règle). Le mur de
  GARAGE BANDINI va de x 155 à 162 au lieu de 157 à 162 : le bardeau et ses deux étages couvrent le rideau et le
  coin de brique. Mesuré sur la ville : c'est la seule des 135 devantures qui bouge, et ses étages ne changent
  pas (deux). Le rideau se peint par-dessus le mur (`dessinerPortesDeGarage`), un pixel de cadre autour.
- **Le nez sous le toit.** Le masque d'un char près d'un rideau (`Monde.sousLeToit`) monte deux tuiles plus
  haut que le fond de la baie (`NEZ_SOUS_LE_TOIT`, une demi-longueur d'autobus). La tache de la capture était
  l'arrière d'un char rangé phares au seuil : l'autobus orange de Martin (48 px), reproduit au banc avant le
  correctif. Les lampes lisent la même zone.
- **Juges** : `test_la_facade_du_garage_couvre_son_rideau_et_tout_son_batiment` (trois graines),
  `test_le_navigateur_peint_le_mur_que_python_a_mesure` (les deux règles mesurent pareil, chaque devanture),
  `test_un_autobus_phares_au_seuil_a_tout_son_arriere_sous_le_toit` ; le masque attendu de
  `test_sous_le_linteau_le_char_se_peint_coupe_au_bas_du_rideau` suit. Chacun rougit quand on retire sa règle.
