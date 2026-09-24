# Les menus au doigt avancent d'une ligne à la fois

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « améliore les contrôles sur mobile, surtout dans les menus. il déplace
souvent de 2 menus à la fois vers le haut et le bas. » Mesuré au banc avant de toucher à
quoi que ce soit : un appui du pouce de **100 ms** descendait de **2 lignes**, un de 330 ms
de **3**, un pouce qui tremble sur la vitre de **6**, et un menu ouvert sous un pouce qui
marchait encore filait de **8 lignes** en une seconde et demie.

- ⚠️ **Deux lecteurs pour un seul pouce.** `Hud.majMenu` bougeait sur le « haut » NEUF du
  pouce (`vTact`, seuil 0.5), puis, l'image suivante, sur l'axe analogique du MÊME pouce
  (`axe.y > 0.6`) — la répétition n'était armée que par l'axe, jamais par l'appui. Le
  clavier et la croix de manette y échappaient (leur axe est `clavier`) ; le stick aussi
  (il ne pose pas de « haut ») : **seul le doigt** avait les deux. Maintenant l'appui neuf
  et le sens tenu arment la même répétition.
- **La répétition** partait après 12 images (200 ms), moins qu'un appui ordinaire du pouce :
  elle part après **27 images (450 ms)**, puis une ligne toutes les **9 (150 ms)**. Tenue,
  elle s'arrête au bout de la liste ; un appui neuf, lui, en fait encore le tour. Les
  flèches du clavier et la croix de la manette répètent aussi, maintenant.
- **Un seuil qui entre à 0.5 et ne sort que sous 0.35** (`entree.js`, `direction`), et pareil
  pour le stick dans un menu (0.6 / 0.35) : autour d'un seuil unique, chaque tremblement
  était un nouvel appui. Effet de bord connu : au volant, le pouce qui relâche garde le gaz
  plein jusqu'à 0.35 au lieu de 0.5 (7 px de course sur la croix).
- **Un menu qui s'ouvre sous un pouce déjà poussé** attend qu'on le lâche (`ouvrirMenu`) : on
  marche vers le comptoir, ACTION, et le curseur ne file plus avant qu'on ait lu la liste.
- **Les boutons HAUT et BAS** : le contexte `menu` renomme ARME et COURS en HAUT et BAS
  depuis M5, mais `majMenu` ne les a jamais lus — deux boutons qui mentaient. Ils marchent,
  **au doigt seulement** (`Entree.basTactile` / `neufTactile`) : à la manette, le bouton de
  droite est aussi RETOUR, et il ne doit pas descendre d'une ligne en fermant.

Juges : `tests/test_menus_au_doigt_js.py` (six), rouges tous les six sur le code d'avant,
avec les chiffres ci-dessus.
