# Rosa habille l'hiver : bottes, tuques, ceintures et parapluies

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demandé par Martin le 30 sept. 2026 : « ajoute l'achat de bottes d'hiver, de bottes de loup
marin et des tuques, des ceintures et ceintures fléchées, des parapluies » — à la Boutique
Rosa. Tranché par Martin : trois places neuves où tout se cumule, cinq tuques de plus, et des
effets pour vrai (le froid, la neige, le parapluie qui frappe, la ceinture fléchée qui fait
sourire les vieux).

Vague 1 — la boutique et le linge. Trois emplacements neufs à côté de `corps` et `tete` :
`pieds` (les bottes), `taille` (les ceintures), `main` (le parapluie) ; on porte les cinq à la
fois, et chacun s'enlève en le rechoisissant, comme un chapeau. Chez Rosa : bottes d'hiver,
bottes de loup marin, ceinture de cuir, ceinture fléchée, parapluie, et cinq tuques à côté
de la rouge — à pompon, bleu-blanc-rouge rayée (sans logo), de laine grise de chantier, en
Phentex tricotée par matante, à oreilles. Le menu a une section par place (LE LINGE, LES
CHAPEAUX, LES BOTTES, LES CEINTURES, LE PARAPLUIE) ; changer n'importe quelle pièce fait
oublier ta tête à la police, comme le reste. Le dessin : les bottes à leur couleur (le loup
marin gris tacheté), la ceinture sur la taille, la fléchée avec ses franges, le parapluie
fermé à la main au sec, ouvert tout seul sous la pluie (celui des passants, lot 4a des
saisons). ⚠️ Le joueur n'est plus habillé d'hiver par la saison : ce qu'il porte, c'est ce
qu'on voit — sinon le froid punirait un joueur qui a l'air botté. Rocco te donne une vieille
tuque au départ (une partie commence le 1er janvier) ; les bottes, tu les achètes.

Vague 2 — les effets. Le froid : dehors, à pied, en grand froid (`froid` de la palette ≥ le
seuil des habits d'hiver), sans ce qu'il faut — une tuque ET des bottes d'hiver, ou les
bottes de loup marin qui suffisent seules — après une minute dehors, la vie baisse doucement
et s'arrête à 25 % : jamais mortel. Un char, une porte, un café réchauffent ; le joueur
grelotte (bulle, souffle) avant que ça morde, et le premier coup de froid le dit (« une tuque
pis des bottes, ça se vend chez Rosa »). La neige : sur la neige au sol (pas un trottoir
déneigé), sans bottes on marche et on court moins vite ; en souliers, un sprint sur le
verglas glisse un peu. Avec des bottes : normal. ⚠️ La glisse de la patinoire est à la
patinoire : les bottes ne l'enlèvent pas. Le parapluie : une arme de mêlée tant qu'il est à
la main — un coup faible qui repousse ; au bout d'une dizaine de coups il se revire à
l'envers et il faut en racheter un ; un son neuf (ElevenLabs), pas vendu chez Gus. La
ceinture fléchée : un vieux passant qui te croise sourit et te le dit, une fois chacun, tiré
à l'empreinte (la recette des saluts du boss).

Juges : chaque place s'enfile et s'enlève sans toucher aux autres, trois oublis de police de
plus ; chaque pièce neuve change le dessin sur les six corps ; le joueur de janvier n'est plus
habillé par la saison ; le froid mord dehors sans protection, jamais sous 25 %, jamais dedans
ni en char, jamais en juillet ; loup marin seul protège ; ralenti mesuré dans la neige, pas
sur le déneigé ; le parapluie frappe, s'use, et disparaît de la garde-robe revirée ; la
ceinture fléchée fait sourire un vieux, pas un jeune, une seule fois. Le poids du paquet
relu ; une capture Chromium du joueur habillé avant de livrer.

## Notes

**Vague 1 — la boutique et le linge (30 sept. 2026).** `magasins.PLACES` (et `PLACES_DE_TENUE`,
`champDeTenue` dans `base.js`) : `corps` → `partie.tenue`, `tete` → `chapeau`, `pieds`, `taille`, `main`.
`porterTenue` enfile par la place ; tout sauf le linge s'enlève en le rechoisissant. Les pièces :
`pieds` porte `{souliers}` (`bottes_hiver`, `loup_marin`, deux valeurs neuves de `garderobe.SOULIERS`),
`taille` `{accessoires}` (`ceinture`, `ceinture_flechee`, au BOUT de `garderobe.ACCESSOIRES`), `main`
`{objet: "parapluie"}`. Les cinq tuques sont des chapeaux neufs de `garderobe.CHAPEAUX`, jamais dans une
garde-robe tirée ; leurs rayures prennent des couleurs FIXES (`W`, `F`, `G`, `y`) parce que `a`,
l'accent du joueur, teint déjà sa cravate. ⚠️ La vieille tuque de Rocco (`tuque_rocco`, `prime: "rocco"`)
se porte au départ et arrive dans la garde-robe d'une vieille partie sans être mise. ⚠️ La saison ne
chausse ni ne coiffe plus le joueur (`Saisons.habiller`, `joueur`) : elle lui met encore son manteau et
son foulard au grand froid, pas les bottes ni la tuque — celles-là le gardent du froid. ⚠️ La copie des
tenues dans `magasins.CATALOGUE` (que rien ne lisait) est sortie du paquet : `magasins` 795 → 310 gzip,
`tenues` 542 → 872. Capture Chromium : la tuque à oreilles, brune, se lisait comme des cheveux et
cachait un œil — elle est violette, les oreilles pendent à côté du visage.

**Vague 2 — les effets (30 sept. 2026).** Les réglages : `saisons.JOUEUR` (au paquet sous
`saisons.joueur`). Le froid : `Entites.majFroid`, à chaque image au début de `majJoueur` (même en char,
pour s'y réchauffer) ; `j.froid` compte les secondes à geler, la vie ne descend jamais sous le plancher,
la tempête mord deux fois plus vite ; la caféine réchauffe. Il grelotte en bulle (pas de souffle
dessiné). La neige : `Entites.hiverAPied` lit `Son.solDuPas` (`pas_neige`, déneigé compris) ; le verglas
(l'option d'essai) fait garder l'élan d'un sprint en souliers. Le parapluie : une arme `armes.py` à prix
0, `usures` 10 ; `Combat.suivreLaMain` le met au sac quand il est à la main (au départ, à chaque change,
à la sortie de prison : la police rend le linge) ; au dernier coup, `revirer` l'enlève de la main, du
sac et de la garde-robe. ⚠️ `semerDesArmesDeFortune` l'exclut par son nom. Ouvert sous la pluie, il n'est
plus dessiné roulé dans la main. Deux sons ElevenLabs au lieu `parapluie` (le coup, le revirement).
La ceinture fléchée : `Entites.majFlechee`, la recette de `majSaluts`, un vieux (`squelette: 'vieux'`)
sur 0,6 à l'empreinte de son numéro.
