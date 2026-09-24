# Des commerces, du monde qui habite, des vrais intérieurs

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« beaucoup plus de variété de commerce ou bien enlever certaines
devantures pour remplacer par des résidences ; ajouter des appartements à étage ; améliorer
les intérieurs, car présentement il n'y a jamais rien, seulement des comptoirs vides ;
ajoute aussi des intérieurs pour plusieurs types ; valide les missions qui doivent avoir des
choses à l'intérieur ») : **142 noms d'enseigne** au lieu de 56 (14 à 48 par quartier) et
**trois familles de plus** (santé, mode, savoir) ; `choisir_enseigne` refuse le même nom à
moins de **40 tuiles** — La Shop affichait sept fois « FERRAILLE ». **74 immeubles à
logements** remplacent 20 devantures et habillent les quartiers d'habitation : une couche
peinte comme les enseignes (zéro solidité touchée), **1 à 3 étages** de fenêtres, balcon,
**escalier de fer** sur le trottoir, et une fenêtre sur trois allumée la nuit. Les **29
intérieurs** sont maintenant **dessinés à la main** (un plan par pièce, l'espace = le
plancher) avec **onze meubles** (comptoir, étagère, table, chaise, lit, frigo, machine,
plante, classeur, poêle, escalier) et **trois planchers** (bois, céramique, tapis) — et du
**monde dedans** : un commis à son poste, des clients tirés dans les passants du quartier.
**Un commerce ordinaire sur cinq s'ouvre pour de vrai** (42 portes au lieu de 16) : dix
pièces génériques, une par famille de devanture, et le **nom de l'enseigne voyage sur la
porte** — on entre chez « TABAGIE DUBOIS », pas dans « Boutique ». Nouveaux comptoirs :
`emplettes` (`magasins.COMPTOIRS`, data), `salon` (le barbier change tes cheveux **et fait
oublier ta tête à la police**), `escalier` (l'étage du plex et la chambre de l'hôtel),
`fouiller` (les tiroirs d'un logement, une fois par adresse), `casier` (le carnet du poste).

- ⚠️ **Trois comptoirs étaient morts** (`guichet`, `sortie_prison`, `casier` : un libellé,
  aucun menu, « PLUS TARD ») — un juge du banc compare maintenant ce que `carte.INTERIEURS`
  dessine à ce que `missions.js` sert, et seul le comptoir de la fourrière reste en chantier
  (il appartient à M9).
- ⚠️ **Un meuble ne remplit pas sa tuile** : sans plancher peint dessous, chaque table était
  un trou **noir** — `plancher` voyage donc avec la pièce. **125 juges de plus**
  (`test_interieurs.py`, `test_interieurs_js.py`, et les logements dans
  `test_devantures.py`)
