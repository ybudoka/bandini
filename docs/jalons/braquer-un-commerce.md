# Braquer un commerce

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ un crime de base que le jeu n'a pas encore — sortir une arme au comptoir, et le commis
vide sa caisse.

- **Le geste** : une arme en main devant un comptoir de commerce ; ACTION devient BRAQUER. Le commis lève
  les mains et vide la caisse (un montant par commerce : un dépanneur rapporte moins qu'une bijouterie).
- **Le prix** : l'alarme sonne, la chaleur monte (les étoiles, la police a sa tolérance), un témoin appelle.
- **La mémoire** : un commerce braqué refuse de te servir quelques jours et garde moins d'argent dans sa
  caisse — sinon on braque le même dépanneur en boucle.
- **Les tiens** : on ne braque pas un commerce qu'on possède (les propriétés), ni le kiosque de Mme
  Thibodeau (elle s'en souviendrait).

⚠️ **Ce qui guette** : l'économie — un braquage ne doit pas rapporter plus qu'un boulot à l'heure une fois
la chaleur comptée ; et les commis sont des piétons de pièce : ils ne doivent pas fuir à travers un mur.

**Juges** : braquer rapporte la caisse et fait monter la chaleur ; le même commerce le lendemain ne paie
presque rien ; on ne peut pas braquer sa propre propriété.

## Notes

_Rien de livré._

**Livré le 26 sept. 2026.**

- **Le geste** : une arme en main devant le comptoir d'un commis (`emplettes`, `acheter`, `hotdog`),
  l'invite dit **BRAQUER** ; ACTION — le commis lève les mains (« OK, OK! PRENDS TOUT! ») et vide sa
  caisse, une **alarme** synthétisée sonne, et la police le sait à l'adresse de la porte (`braquage` :
  deux étoiles, bruyant — pas de témoin à convaincre).
- **Les caisses** (`economie.BRAQUAGE`) : 60 $ au terminus, 90 au dépanneur, 240 chez Gus, 120 pour un
  commerce de rue ; la plus grosse reste sous une heure de taxi (jugé).
- **La mémoire** : trois jours, le commerce ne te sert plus (même les mains vides) et sa caisse n'a plus
  que le dixième ; la rancune passée, elle est pleine.
- **Les tiens** : pas un commerce qui est à toi, ni le kiosque de Madame Thibodeau, ni l'hôpital, le
  poste, la planque ou le garage de Rocco.
- **Juges** (`tests/test_braquage_js.py`) : au bouton, la caisse, la chaleur et le crime rapporté ; la
  rancune ; ni à mains nues ni chez soi ; l'économie. Trois mutations les font rougir.

