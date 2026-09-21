# L'aéroport de Baie-des-Brumes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (21 sept. 2026) :_ « aggrandit la carte au sud avec un autre pont sur l'ile de
droite. ajoute un aéroport. ca doit être bloqué par un pont en construction et d'autre stratageme
pour des missions futures. »

« L'île de droite », c'est **La Pointe** (la foire, le phare, un seul pont). La carte grandit donc
**sous La Pointe** : une île neuve, l'aéroport, et un **deuxième pont** qui part de la rue du bord
de l'eau de La Pointe — le prolongement de la rue qui y finit en T (colonne 394).

- ⚠️ **On n'agrandit pas la trame, on ajoute des rangées sous la carte.** Changer une rangée de
  la trame re-tire toute la ville (le chenal du 17 sept. : 26 juges sans rapport tombés). L'île
  de l'aéroport se **dessine** comme l'Île-aux-Corneilles (`app/aeroport.py`, un plan écrit à la
  main, jugé au chargement) et se pose **en tout dernier** dans `generer`, sans un dé : la carte
  s'allonge d'eau vers le sud, et rien de la ville d'aujourd'hui ne bouge.
- ⚠️ **Fermé par étages, pour les missions à venir** — chacun seul suffirait, et chacun est une
  mission à écrire :
  1. **le pont en construction** : une barricade à la tête du pont (barrière `pont_aeroport`,
     « PONT EN CONSTRUCTION ») ; on la défonce en char, mais…
  2. **la travée manquante** : le tablier s'arrête au-dessus de l'eau, des piles sans rien
     dessus, puis le bout du pont côté île. Un char lancé finit dans la baie ; à la nage, ça passe ;
  3. **le barbelé** : l'aéroport est clôturé au complet, et le barbelé ne s'enjambe pas ;
  4. **la guérite** (barrière `aeroport`, « LAISSEZ-PASSER EXIGÉ ») : la seule ouverture de la
     clôture, au pied du pont ; elle ne se force pas ;
  5. **le large** : de la plage de La Pointe à l'île, trop d'eau pour la nager, même avec le café
     et l'estomac plein.
- ⚠️ Les deux barrières attendent des missions qui **n'existent pas encore** (`a01` : le pont se
  finit ; `a02` : le laissez-passer). Elles sont déclarées dans `aeroport.MISSIONS_A_VENIR`, et le
  juge des barrières les accepte de là seulement : une faute de frappe dans un `apres` reste
  rouge.
- ⚠️ **Ce qu'il y a dedans** : une piste est-ouest (marques peintes : seuils, axe, 09 et 27), une
  voie de circulation, l'aire de trafic et ses avions stationnés (peints, pas encore des
  véhicules), l'**aérogare** (un lieu, une pièce dessinée pour les missions : comptoirs,
  carrousel, portique), la tour de contrôle, deux hangars, la guérite et un stationnement. Une
  zone à elle (`aeroport`), avec sa police : ce n'est pas un refuge.
- ⚠️ **Le poids** : la carte voyage à ~48,3 Ko gzip pour un plafond de 50. Des rangées d'eau ne
  coûtent presque rien sur le fil, l'aéroport, lui, coûte ; le plafond du paquet de la carte
  (brut et gzip) montera de ce que la mesure dira — c'est le prix de la demande.
