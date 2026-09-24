# Un kiosque fermé n'a personne derrière

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

Retour de Martin (17 sept. 2026), capture à l'appui — la cabane à fruits de mer, un marchand
derrière le comptoir : « cantine, restaurant ou commerce fermé, il ne faut pas qu'il y ait
quelqu'un ». Mesuré avant : `Entites.creerAmbulants` pose un vendeur `fige` derrière chaque
comptoir au chargement, et il ne s'en va jamais. Trois kiosques ont des heures
(`magasins.AMBULANTS` : journaux 6 h–18 h, café 4 h 48–14 h 24, fruits de mer 7 h 12–20 h 24) ;
hors de ces heures ACTION répond « FERME », mais l'invite annonce encore le prix et le
marchand attend au comptoir. Les intérieurs, eux, n'ont pas d'heures : leur commis est là
parce qu'ils sont ouverts.

**Livré** : `Entites.majKiosques`, une ronde toutes les trente images dans `peupler`. À la
fermeture, le marchand plie bagage : hors champ il s'efface, sous nos yeux il quitte le
comptoir à pied vers une porte (`envoyerAUnePorte`) et la foule l'oublie comme un passant. À
l'ouverture il revient, **hors champ seulement**. Une partie chargée la nuit pose les kiosques
fermés vides. L'invite dit « CABANE À FRUITS DE MER — FERMÉ » au lieu d'un prix, et ACTION
« FERMÉ ». Trois juges de banc (`test_kiosque_ferme_js.py`), chacun vu rougir sans sa règle
(six mutations). Capture Chromium : la cabane à midi, son marchand ; à 21 h 39, vide.

- ⚠️ **Le lien passe par le kiosque** (`etal.vendeur`), pas par le slug : trois kiosques à
  hot-dogs portent le même.
- ⚠️ **Le marchand a une allure de 0** (`pietons.py`, `vendeur`) : sans `allure = 1` au départ,
  il « flâne » sur place derrière son comptoir fermé.
- ⚠️ Un marchand assommé ou tué se détache aussi à la fermeture : avant, un kiosque dont on
  avait couché le vendeur restait vide pour toute la partie ; il est maintenant regarni à
  l'ouverture suivante.
