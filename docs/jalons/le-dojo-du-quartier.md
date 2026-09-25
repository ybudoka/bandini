# Le dojo du quartier : apprendre les techniques

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026), deuxième des trois jalons des arts martiaux — le répertoire est dans
[les techniques d'arts martiaux](les-techniques-d-arts-martiaux.md#fiche), qui doit être livré avant.

_Ce que ça donne :_ un dojo dans la ville, un sensei derrière le comptoir. On paie un cours, on le réussit
sur le tatami, et la technique est à nous pour de bon. Au départ, Bandini n'a que les poings de rue.

- **Le lieu** : une pièce (tatami, sac de frappe, mannequin de bois, vestiaire), une porte sur rue. ⚠️ Une
  pièce de plus est un lieu **ajouté** : il se pose en dernier, sans dé, sinon la ville glisse (voir
  « Grossir un lieu garanti déplace la ville »).
- **Le sensei** : un personnage de `missions.PERSONNAGES`, sa fiche dans `docs/personnages/`, sa voix ; il se
  nomme une fois, dans sa salutation.
- **Les cours** : dix, au comptoir, un par technique (les prix sont dans `app/techniques.py`) ; un cours
  n'ouvre que si le précédent de sa chaîne est su (le 5e maillon attend le 4e).
- **L'épreuve du tatami** : une sorte neuve dans `adresse.js`, dans l'esprit de `danse` — le sensei annonce
  le geste, on le fait aux vrais boutons (tapes, tenue, prise + direction) contre un partenaire. Réussie :
  `B.partie.techniques[slug] = true`. Ratée : on recommence **sans repayer**.
- ⚠️ **Ce qui guette** : l'épreuve lit les boutons du jeu — `B.epreuve` coupe déjà les gestes de
  `Combat.majGestes` ; la prise doit s'y couper aussi.

**Juges** : un cours acheté puis raté ne se repaie pas ; une épreuve réussie apprend la bonne technique ;
un cours dont le maillon d'avant manque ne s'achète pas ; la pièce ne déplace rien dans la ville.

## Notes

_Rien de livré._
