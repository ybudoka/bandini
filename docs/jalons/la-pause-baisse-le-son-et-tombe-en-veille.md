# La pause baisse le son et tombe en veille

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (3 oct. 2026)_ : « affaiblis le son sur pause, et je voudrais un style de screen saver ».

**Le son.** En pause, rien ne baissait : la musique, la radio, le moteur jouaient plein volume par-dessus le menu.
Le gain MAÎTRE glisse vers environ 30 % (`pause` dans les réglages de la musique, à côté de `ducking`) avec le même
`glisser` que le ducking — jamais d'un coup — et remonte à la reprise. Le muet reste franc : c'est une coupure.

**La veille.** Après 20 s en pause sans toucher à rien, le menu et le voile s'effacent en fondu, la caméra flâne
lentement autour du joueur (bornée comme celle de la photo, ville figée) et le logo BANDINI se pose dans un coin.
N'importe quel bouton RÉVEILLE seulement — le menu revient, la caméra rentre — sans reprendre la partie.
Choisi par Martin : la caméra qui flâne, à 20 s.

**Juges** : le maître descend en douceur en pause et remonte à la reprise ; 1 200 images sans touche démarrent la
veille et la caméra bouge ; une touche réveille, toujours en pause ; une capture pour regarder.

## Notes

_Livré le 3 oct. 2026._

- **Le son** : `Son.Pause` glisse le gain maître vers `pause` (0,3, dans `app/musique.py`) avec `glisser`, comme le
  ducking ; `Mus.tick` le fait avancer à chaque image, pause comprise. `majVolume` passe par `volumeMaitre()` :
  le muet reste une coupure franche.
- **La veille** : `Jeu.majVeille`, en tête de la branche pause de `maj`. `B.veille` naît à `pause()` et meurt à
  `reprendre()`. `Entree.activite()` dit si quelqu'un touche à quelque chose cette image (appui neuf, stick, pouce,
  souris qui bouge, molette). ⚠️ L'appui qui réveille est avalé, et tant que son geste TIENT (`relache`), la pause
  attend qu'il lâche : sans ça, le stick du réveil descendait le menu l'image d'après.
- **Le dessin** : `Hud.dessiner` efface le HUD et le menu par `globalAlpha` (seules la roue et la grande carte le
  remettent à 1, et ni l'une ni l'autre ne vit en pause), éclaircit le voile de 0,6 à 0,2, et `dessinerVeille` pose
  une bande sombre en bas et le logo de l'accueil, qui respire. La caméra : `vue` + `B.veille.dx/dy`, bornée par
  `Monde.limitesCamera` et `vueSurLeMasque` comme la photo.
- **Juges** : `tests/test_pause_veille_js.py` (10), chacun vu rouge par mutation (le glissement du maître, l'appui
  avalé, la garde `relache`, le compte remis à zéro, la souris, la vue décalée). Capture Chromium : sans la bande,
  le logo se perdait sur la façade de Chez Gus.
