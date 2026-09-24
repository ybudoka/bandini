# Le poste clôturé : du barbelé et une barrière coulissante

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (23 sept. 2026) : « le poste de police doit etre completement cloturé
barbelé pour ne pas qu'on vole les auto. crée une nouvelle cloture coulissante avec comme
morte une cloture barbelé. » (lu : « comme modèle »). Aujourd'hui le lot des autos-patrouilles (3 × 9 tuiles, collé
au mur est du poste) est ouvert sur la ruelle, le côté et la rue : on y entre à pied et on
repart avec une auto-patrouille. Le lot se ferme de barbelé (`X`) sur ses trois côtés
libres, et sa sortie sur la rue devient une BARRIÈRE COULISSANTE — un glyphe neuf (`Z`),
barbelée comme le reste (solidité 5, ni à pied ni en char, un lourd ne la défonce pas).

- ⚠️ Elle s'ouvre pour une auto-patrouille CONDUITE (par la police ou par le joueur qui en a
  volé une ailleurs), jamais pour un piéton ni un char civil : le panneau glisse le long de
  son rail, la tuile devient libre une fois ouverte, et se referme quand plus rien n'est
  dessous.
- ⚠️ La connexité : une barrière est une OUVERTURE qui a une clé — `franchissable` la
  compte, sinon le lot serait une poche fermée de barbelé.
- ⚠️ Posée dans `_stationnement_de_service`, donc EN DERNIER : rien d'autre ne bouge dans la
  ville (le juge « le lot ne déplace rien »). Juges : le lot est clos (on n'en sort que par
  la barrière), la barrière est large comme l'allée et donne sur la rue ; au banc, à pied et
  en char civil elle reste fermée et bloque, une auto-patrouille conduite l'ouvre, passe, et
  elle se referme. Capture avant de livrer.

## Notes

**Livré le 23 sept. 2026.** Le lot des autos-patrouilles (3 × 9 tuiles, collé au mur est du
poste) est clos : du barbelé (`X`) sur la rangée du haut et sur ses deux côtés — sauf là où le
mur du poste ferme déjà —, les cases descendues d'une tuile sous la clôture, et la rangée du bas,
sur la rue, est la **barrière coulissante** (`Z`, glyphe neuf). Tout se pose dans
`_stationnement_de_service`, donc en dernier : le juge « le lot ne déplace rien d'autre dans la
ville » est resté vert sans y toucher.

- **La barrière** : du barbelé (solidité 5 — ni à pied, ni en char, et un lourd ne la défonce pas)
  tant qu'elle n'est pas GRANDE ouverte. Elle s'ouvre pour une auto-patrouille **conduite** (la
  police, ou le joueur qui en a volé une ailleurs) qui a le nez entre deux tuiles dans l'allée et
  deux dehors — pas la chaussée : une patrouille qui passe dans la rue n'ouvre pas le lot. Le panneau
  glisse vers l'est en 50 images et rentre derrière son poteau ; il reste ouvert 60 images après le
  départ de la clé, et **jamais ne se referme sur quelqu'un** (char, passant ou joueur dans sa
  rangée). Un grincement synthétisé quand il part, s'il est à l'écran.
- **Le dessin** : la tuile cuite n'est que le sol (l'asphalte et le rail) ; le panneau — la maille,
  les trois fils et leurs épines du barbelé, dans un cadre à roulettes — se peint par-dessus à chaque
  image (`Monde.dessinerBarrieresCoulissantes`), comme le rideau d'un garage.
- ⚠️ **La faille qu'une clôture seule ne fermait pas** : la portière s'ouvre à 30 px, deux tuiles —
  depuis la ruelle ou le bout de dalle à l'ouest, la main passait par-dessus le barbelé, et
  l'auto-patrouille volée ouvrait ensuite sa propre barrière. `vehiculeSousLaMain` refuse
  maintenant un char dont le trait main → char traverse une tuile de solidité 5 (le barbelé, la
  barrière) — seulement 5 : on monte dans une chaloupe par-dessus l'eau du quai.
- ⚠️ **La connexité** : `franchissable` compte la barrière (c'est une ouverture qui a une clé) —
  sinon le lot serait une poche fermée de barbelé. Et le juge « tout stationnement touche la rue »
  regarde de l'autre côté d'une barrière.
- **Juges** : Python — le lot est clos (depuis les cases, on ne sort qu'en passant la barrière, qui
  prend toute l'allée et donne sur la rue), la barrière est du barbelé qui s'ouvre ; banc — ni la
  main par-dessus le barbelé (ouest, nord), ni à pied, ni un char ordinaire ne passent ; une
  auto-patrouille conduite l'ouvre, la tuile ne se libère qu'une fois grande ouverte, elle entre, et
  la barrière se referme ; elle ne se referme pas sur le joueur. Cinq mutations, cinq rouges.
- Capture Chromium avant de livrer : le lot fermé avec ses deux autos-patrouilles, le panneau à
  mi-course, puis ouvert.
