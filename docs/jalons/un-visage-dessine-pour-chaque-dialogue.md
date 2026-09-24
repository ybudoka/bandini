# Un visage dessiné pour chaque dialogue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026) : « je veux des visages dessinés pour chaque dialogue ». Un portrait
en pixels (40×40) à gauche de la boîte de dialogue, pour chaque personnage qui parle (les 23
de `PERSONNAGES`, l'agent de police) : dessiné par du code (`static/js/visages.js`), dans
l'esprit des sprites, avec les couleurs de palette qu'il a déjà dans la rue ; ses traits
(coiffure, moustache, lunettes, casquette, rides…) sont des DONNÉES, dans sa fiche Python
(`visage`). L'expression suit le jeu d'acteur : une `humeur` tirée des balises de `jeu=`
(`[angry]` → fâché, `[warmly]` → content…) voyage vers le navigateur à la place du jeu. La
bouche bouge pendant que la voix parle, les yeux clignent. Juges : chaque personnage a un
visage valide et distinct, chaque balise a son humeur, la boîte le dessine.

## Notes

**Livré le 22 sept. 2026.**

- **Où vivent les traits.** Pas dans `PERSONNAGES` (un fichier que toutes les sessions touchent) :
  dans `app/visages.py`, `VISAGES`, une fiche par slug — tête (`ronde`, `carree`, `longue`, `fine`,
  `large`), coiffure (13), habit (10), pilosité, lunettes, chapeau, et des petits signes (rides,
  cernes, rousseur, cicatrice, mégot, crayon à l'oreille, nœud papillon, stéthoscope…). Toutes des
  listes fermées : un juge refuse un mot que `visages.js` ne dessine nulle part (il a mordu sur
  `sifflet`, qui n'avait pas de dessin). Les couleurs sont celles de la rue (`c`, `h`, `s`), plus
  quelques-unes à lui (`t` le chapeau, `y` l'iris de Sven). `AUTRES` porte l'agent de police, qui
  n'est pas un personnage.
- **Le dessin.** `static/js/visages.js` peint une grille 40×40 en lettres de palette, par couches :
  cheveux de dos, tête et oreilles (ombrée à droite), habit, cheveux de devant (l'ombre de la mèche
  sur le front), signes, barbe, nez, bouche, moustache, yeux et sourcils, lunettes, chapeau — puis
  un **contour** automatique (tout vide qui touche le dessin devient un trait sombre). Aucun
  `Math.random` : le bruit des permanentes et des barbes est tiré à l'empreinte du slug. Cuit une fois
  par (slug, humeur, bouche, clin).
- **L'humeur suit le jeu.** `jeu=` ne va toujours pas au navigateur ; à sa place, `missions.
  pour_le_navigateur` pose `humeur` (absente = `neutre`) tirée de la **première balise qui dit une
  mine** (`visages.humeur`, table `BALISES`). Dix humeurs : neutre, content, rire, fâché, sérieux,
  triste, inquiet, surpris, malin (un sourcil levé, le coin de la bouche), froid (les paupières
  mi-closes). Sur le catalogue : 73 sérieux, 69 contents, 25 malins, 24 tristes… Un juge exige que
  toute balise de `interpretation.BALISES` ait son humeur ; un accent (`[norwegian accent]`) n'en dit
  aucune.
- **La boîte.** `Hud.dialogue(qui, lignes, duree, visage)` : le portrait (cadre 42×42 doré) à
  gauche, la boîte grandit à 50 pixels par le haut (le bas ne bouge pas), le texte se pousse de 48.
  La bouche bouge tant que `Son.Voix.enCours` ; sans voix, deux images par lettre. Les yeux
  clignent sur l'horloge de l'œil (`B.image`), décalés par personnage. Qui a un visage : chaque
  réplique de mission (`Histoire.suivante`), le repos d'un donneur, le Clairon qui lit sa manchette,
  l'agent et le sergent du pot-de-vin. **Pas l'ouverture** (`anonyme`) : une voix sans visage.
- ⚠️ **`lignesDe` recopiait les répliques champ par champ** et laissait tomber `humeur` : le juge
  « la réplique montre le visage de qui parle avec sa mine » l'a vu (Ti-Guy content arrivait neutre).
- ⚠️ **Le paquet de définitions était déjà au-dessus de son plafond** avant ce jalon (≈272 000 octets
  bruts pour 250 000 permis, `test_le_paquet_reste_leger` rouge sur `dev`) ; les visages y ajoutent
  ≈4 700 octets et les humeurs ≈4 600. Les valeurs par défaut ne voyagent pas (`_leger`).
