# Des photos pour le Clairon

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« ajoute tout au plan »)._

_Ce que ça donne :_ le mode photo devient un boulot — Louise, au Clairon, paie pour une photo d'une
poursuite, d'un char en feu ou d'un saut, et la une du lendemain l'affiche.

**Aujourd'hui** le mode photo existe (M14, 6e vague : le jeu se fige, la caméra se détache, des filtres),
mais une photo ne sert à rien dans la partie. Louise Tremblay-Dion est prévue (M16, arc C, « Le Clairon »)
sans être encore un personnage.

- **Ce que le jeu reconnaît** dans le cadre, au moment du déclic : un char en feu, une poursuite (des
  étoiles et un char de police à l'écran), un char en l'air, un personnage de mission. Chaque sujet a son
  prix ; une photo floue ou vide ne vaut rien.
- **La une** : le Clairon du lendemain titre sur la meilleure photo vendue (le journal du matin existe, avec
  ses manchettes lues par le narrateur).
- **Un piège drôle** : une photo de TOI en pleine poursuite se vend très cher… et fait monter ta chaleur
  le lendemain.

⚠️ **Ce qui guette** : le jeu ne « voit » pas l'image — il juge **ce qui est dans le cadre** (les entités
visibles au moment du déclic), jamais les pixels. À faire après le personnage de Louise (arc C de M16).

**Juges** : une photo d'un char en feu cadré se vend ; la même photo sans le char ne vaut rien ; la une du
lendemain nomme le sujet de la meilleure photo.

## Notes

**Livré le 29 sept. 2026** (Martin : « Louise d'abord »). `app/photos.py`, `static/js/photos.js`, Louise dans
`missions.PERSONNAGES` (son visage, sa tenue, sa fiche `docs/personnages/louise.md`, sept voix `louise-clairon-*`) ;
juges `tests/test_photos.py` et `tests/test_photos_js.py` (huit mutations, toutes mordent).

- **Louise Tremblay-Dion** se tient devant le kiosque de Mme Thibodeau, où le Clairon se vend (`porte:kiosque`, un
  lieu garanti), à partir de m2. ⚠️ **Sa fiche est une proposition** (à valider) ; sa voix, Ana Rita (libre,
  vérifiée « quebec » en multilingue v2), est générée, **pas écoutée**. On lui parle : la première fois elle se
  présente, ensuite elle regarde ta photo (son menu, comme Mireille au dojo — pas de repos).
- **Au déclic**, le jeu juge ce qui est dans le cadre de la vue détachée — les entités à l'écran, jamais les pixels :
  un char en feu (ou le bâtiment qui brûle), 150 $ ; un char qui vole, 120 $ ; une poursuite (la police à l'écran,
  des étoiles), 90 $ plus 20 par étoile ; une figure du quartier, 40 $ ; **toi en pleine poursuite, 300 $**. Le
  bandeau du mode photo dit ce que Louise en donnerait. La meilleure photo du jour attend dans la partie.
- **Une par jour** : Louise en achète une ; le lendemain, « j'ai ma une ». Une photo d'avant-hier ne se vend plus.
- **La une du lendemain** ouvre le Clairon (une ligne sous la manchette, en tête) et nomme le sujet — texte seul,
  sans voix du narrateur. **Ta face en une** : ce matin-là, une étoile.
- ⚠️ **Pas fait** : l'arc C de M16 (les six missions de Louise — leurs slugs c01 à c06 sont pris par le
  Petit-Canton) ; le bureau du Clairon comme lieu (Louise est au kiosque) ; une vraie manchette lue par le narrateur
  pour la une (il faudrait une voix par sujet).
- Capture regardée : Louise devant le kiosque, à côté de Mme Thibodeau ; le bandeau après le déclic sur un char en
  feu. ⚠️ En Chromium sans tête, le téléchargement du PNG fait perdre le focus et referme le mode photo — le
  bandeau ne se voit qu'avec le téléchargement coupé ; à vérifier en jouant.
