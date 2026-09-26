# La Saint-Jean sur la baie

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ une soirée de fête nationale — des feux d'artifice au-dessus de la baie, un défilé qui
ferme des rues, et la ville entière dehors.

- **Quand** : un soir fixe de la partie, calculé, jamais tiré.
- **Le défilé** : un cortège de chars allégoriques qui suit un trajet fixe dans le Faubourg ; les rues du
  trajet ferment (les barrières de `carte.BARRIERES` savent fermer une rue avec sa raison affichée).
- **Les feux** : tirés du phare de La Pointe, vus de partout ; des éclats de couleur par-dessus le ciel de
  nuit (les lampes et la nuit existent).
- **Une mission** (M16) : quelqu'un vole la caisse du comité des fêtes pendant les feux — un fuyard dans la
  foule.

⚠️ **Ce qui guette** : une foule dense coûte au rendu (la dette du rythme sur le vrai téléphone) ; une rue
fermée ne doit enfermer ni la planque ni un lieu de mission (le juge des barrières) ; les feux sont une
musique et des bruitages à payer (à trancher par Martin).

**Juges** : le défilé suit son trajet et libère les rues après ; les feux ne tirent aucun `B.rng()` ; aucun
lieu de mission n'est enfermé ce soir-là.

## Notes

_Livré le 26 sept. 2026._ Pas d'option : c'est un soir par année du jeu, le 24 juin (le jour 20 de
chaque année de quarante jours, `calendrier.py`).

- **Le soir** (`app/saint_jean.py`, `static/js/saintjean.js`) : le défilé de 19 h à 21 h 30, les feux de
  22 h à 22 h 36. Tout est une fonction du jour et de l'heure (le défilé) ou de l'image (les fusées).
- **La rue du défilé** : pas une rue neuve à juger, une de celles que la carte sait DÉJÀ fermer sans
  couper la ville — la plus longue des `fermetures` du Faubourg (le juge de connexité les a toutes
  vues, `devants.py` n'en a écarté aucune devant une porte). Le soir de la fête, elle PREND LA PLACE de
  l'entrave du jour (`Monde.entraveDuJour` la demande à `SaintJean.fermeture`) : une seule rue fermée à
  la fois, la règle qui évite de juger des combinaisons — et c'est elle qui garantit qu'aucun lieu de
  mission ni la planque ne se retrouvent enfermés. Une barricade, « RUE FERMÉE — DÉFILÉ DE LA SAINT-JEAN »,
  le trafic tourne au croisement ; elle se rouvre à la fin du défilé.
- **Le défilé** : quatre chars allégoriques PEINTS (ni entité ni dé) — la fleur de lys, le drapeau au
  mât, le violoneux sur sa balle de foin, le feu de joie — qui remontent la rue à la file, cinq tuiles
  d'écart, d'un bout à l'autre.
- **Les feux** : une fusée toutes les 18 images, du phare de La Pointe ; au-dessus du phare s'il est à
  l'écran, au bord du ciel de son côté sinon (on les voit de partout). La fusée monte, flashe, éclate en
  couronne de sa couleur (à l'empreinte de son numéro : bleu, blanc, rouge, or, vert ; une sur trois a un
  cœur d'une autre couleur) avec sa traînée, et retombe en s'éteignant ; chaque éclat est une LAMPE pour
  la nuit (la ville s'allume de couleurs). ⚠️ Peints PAR-DESSUS la nuit (`Base.ecran()`, comme le HUD) :
  sous elle, ils s'y éteignaient — vu à la capture, une lueur rouge et pas un éclat. Le bruit est synthétisé
  (`Son.SFX.artifice`) : pas d'échantillon à payer pour un soir par année.
- **Le Clairon** : la veille, « DEMAIN SOIR, LA SAINT-JEAN… » ; le matin, « BONNE SAINT-JEAN!… ».
- **Juges** : `test_saint_jean.py` (la rue est une fermeture validée du Faubourg, assez longue ; le soir
  tient dans la journée) et `test_saint_jean_js.py` (la rue fermée le soir de la fête seulement, à la
  place de l'entrave du jour, rendue après, revenant l'année suivante ; les chars dans leur rue, dans
  l'ordre, sans reculer ni se doubler ; les feux à 22 h, leurs lampes, sans un dé ; le Clairon). Chaque
  juge a été vu rougir sous sa mutation.
- **Pas fait, à dire** : **la mission du vol de la caisse du comité** pendant les feux (M16) ; la foule
  (« la ville entière dehors ») — les passants restent ceux d'un soir ordinaire, la dette du rythme sur le
  vrai téléphone le demande ; une musique de fête (à payer, à trancher par Martin).
