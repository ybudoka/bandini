# Le bouclier se tient

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « pour le bouclier humain, il faudrait tenir le bouton plus longtemps
pour éviter de le faire par accident ».

- ⚠️ **Le bouclier est LE DERNIER de la chaîne d'ACTION** — ce que le bouton fait quand il
  n'a rien trouvé d'autre à faire —, donc exactement ce qu'on déclenche sans le vouloir : on
  visait une porte d'un pas trop loin, une arme par terre, un char, et on repartait avec un
  bonhomme dans les bras et **deux étoiles** qu'on n'avait pas demandées. La pression
  **arme** la prise, le maintien la prend (`saisie_s` = 0,5 s, `Combat.majSaisie`).
- ⚠️ La demi-seconde se juge **des deux côtés** : plus longue qu'une pression (le coup fort,
  l'autre bouton qu'on tient, en demande un tiers) et plus courte que la **cadence de tir**
  de la police (1,2 s) — une sortie de secours doit s'ouvrir avant la deuxième balle.
- ⚠️ **Et l'invite le dit, puis se remplit** : « ACTION : BOUCLIER HUMAIN — TENIR », et le
  bandeau se remplit pendant qu'on insiste ; un bouton qui demande qu'on insiste sans le
  montrer ne se lit pas comme un bouton qui résiste, il se lit comme un bouton brisé.
- ⚠️ La prise rejuge `otageSousLaMain` **à chaque image** plutôt que de garder la personne
  visée : le passant qui s'éloigne, la porte ou le char qui entre à portée la font tomber —
  le bouton ne fait jamais autre chose que ce que l'écran promet.
- ⚠️ **Un défaut de décor trouvé au passage** : les juges du bouclier **dégelaient** leur
  victime (`etat = 'flane'`) au milieu de la chaussée, et un piéton sur la chaussée court
  vers le trottoir le plus proche à `pieton_course` — instantanée, la prise ne s'en
  apercevait pas ; tenue une demi-seconde, elle tombait à la vingt-cinquième image. Les
  passants du jeu sont sur le trottoir : la victime reste **figée**, comme `o.poser` la
  rend. Et le juge du recul prend l'otage **avant** de lancer l'agent, puis le lâche et
  remesure — vingt balles cherchaient le joueur, et celui qu'on voulait prendre se tenait
  dans la trajectoire. 2 juges neufs (1 Python, 1 de banc), rouge-avant prouvé : sans le
  maintien, une pression pose 48 points de chaleur
