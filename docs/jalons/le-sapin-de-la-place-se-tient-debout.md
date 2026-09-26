# Le sapin de la place se tient debout

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (26 sept. 2026, capture) : « corrige ça » — le sapin des Fêtes planté par-dessus un banc et la
fontaine de la place du Faubourg, et le joueur qui marche au milieu de ses branches.

- **Sa place** était la scène d'amuseur la mieux cotée du Faubourg, telle quelle : (201, 45), entre le
  banc (200, 44) et la fontaine (200, 46). Personne ne regardait ce qui l'entourait.
- **Il était peint au sol**, sous les gens : tout passait par-dessus, rien ne s'y cognait.

## Notes

**Livré le 26 sept. 2026.**

- **Sa place se cherche** (`fetes.sapin`) : autour de la scène la mieux cotée du Faubourg (`PORTEE`), la
  tuile la plus proche où tout le `GABARIT` (trois de large, deux rangées de branches, une d'ombre) est
  du sol de la place, plus une tuile d'`AIR` autour — sans décor, ambulant, réclame, paquet ni scène, sans
  devant de porte, sans rue — et à `LOIN_D_UNE_SCENE` des scènes : l'amuseur garde la sienne. Sur la ville
  d'aujourd'hui : (204, 46), côté est de la place, entre les deux arbres du coin, à quatre tuiles de la
  fontaine. Toujours sans dé.
- **Il se trie avec les gens** (`Fetes.ajouterVisibles`, comme la coque du traversier) par le pied de son
  tronc : derrière, ses branches cachent le joueur ; devant, le joueur passe par-dessus.
- **Son tronc est une tuile pleine en décembre** (`Fetes.maj`, posée et rendue comme le pont du
  traversier) — jamais dans une pièce ni dans un bloc de carte, où `Monde.carte` n'est pas la ville.
- ⚠️ L'ancien juge exigeait que le sapin soit SUR une scène : c'était le bogue. Il est remplacé par
  `test_le_sapin_a_une_place_libre_sur_la_place`, qui rougit quand on remet l'ancienne place (un banc
  sous ses branches).
- Au passage, l'insertion du sapin dans `jeu.js` avait arraché le commentaire de la ligne des épreuves au
  volant (« la case, les lignes, les cônes ») : remis à sa place.
