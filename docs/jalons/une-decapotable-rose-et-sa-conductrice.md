# Une décapotable rose et sa conductrice

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « une voiture type corvette, rose, avec une femme en
robe rose qui la pilote et en descend si volée. Elle va plus vite. » Un char rare de plus au
haut de gamme, et la première auto du parc qui a SA conductrice.

- ⚠️ **Le char** : `cabriolet` (« Cabriolet rose »), une décapotable basse à long capot,
  dessinée en volume comme la sport, et menée à la vue de tous comme la chaloupe
  (`assisDedans`, la selle du côté du conducteur) ; plus rapide que la sport — la moto reste
  devant, un juge le tient — et rare : elle ne naît que dans les districts qui la déclarent.
- ⚠️ **Toujours menée** : c'est la fiche qui dit QUI est au volant (`au_volant`, un
  archétype de `pietons.py`), pas un `slug === 'cabriolet'` caché dans le JS ; le trafic la
  fait naître avec sa conductrice et elle ne se gare jamais.
- ⚠️ **La conductrice** : un archétype à sprite propre — une robe rose, comme la Fille de la
  Brume a le sien —, fréquence 0 (elle ne marche jamais sans sa voiture), et des couleurs
  qui ne sont à personne d'autre.
- ⚠️ **Elle descend si on la vole** : le carjacking existant la fait sortir, témoigner et
  fuir, mais elle, en robe rose, et non un passant tiré au hasard ; sans un dé de plus au
  jeu.
