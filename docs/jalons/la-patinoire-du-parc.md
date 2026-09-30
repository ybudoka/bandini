# La patinoire du parc

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demandé par Martin le 30 sept. 2026 : « l'hiver, mets une patinoire dans un parc avec des
gens qui patinent ». Tranché par Martin : une patinoire à bandes dans le parc du Faubourg,
de vrais passants qui patinent, des patins à louer — « patin, mais on doit glisser aussi ».
Le parc n'a nulle part la place (6 × 6 tuiles libres au plus entre 29 arbres) : une
CLAIRIÈRE d'environ 14 × 7 tuiles se taille à la toute fin de la génération, sans dé, le
décor dessus DÉPLACÉ à sa place dans la liste (la recette de `devants.py`), jamais retiré ;
aucune tuile, aucune porte. Vague 1 — la glace et la glisse : l'été une clairière de gazon ;
l'hiver, tant que la neige tient, la glace, des bandes blanches à liseré rouge, deux filets,
des lampadaires le soir, une cabane chauffée ; les bandes arrêtent les chars, on entre à
pied par deux portes ; la glace glisse pour tout le monde — à pied de l'élan, une chute si
on court ; un char y dérape (le modèle du lot 6a des saisons). Tout est peint. Vague 2 — les
patineurs, de vrais passants : ils naissent hors de l'écran à la cabane quand le joueur
approche (la recette des enfants de l'Halloween), et repartent quand il s'éloigne ; six à
dix l'après-midi et le soir, personne tard la nuit ; habillés d'hiver, des patins aux
pieds ; ils tournent en rond à contre-sens des aiguilles, avec l'élan de la glace ; un
enfant tombe parfois ; frappés, ils fuient et la police s'en mêle, comme les autres. Vague 3
— les patins à louer, et le son : à la cabane, 2 $, on chausse ; plus vite, MAIS on glisse
toujours — on démarre doucement, on tourne large, on met du temps à s'arrêter ; rendus en
quittant la glace ; le raclement des lames et une valse au haut-parleur le soir
(ElevenLabs). Juges : la ville identique hors de la clairière (JSON clé par clé), les bandes
arrêtent un char, personne ne patine l'été, l'élan mesuré sur la glace, 2 $ et les patins
rendus hors de la glace ; une capture Chromium avant de livrer.

## Notes

### ✅ Vague 1 — la glace et la glisse (30 sept. 2026)

- **La place** (`app/patinoire.py`) : 13 × 5 tuiles en bas du parc du Faubourg, entre l'allée verticale et le
  kiosque de Madame Thibodeau ; ses portes au nord (l'allée de la statue y débouche) et à l'ouest (l'allée
  verticale). Le parc n'avait nulle part plus de 6 × 6 tuiles libres : cinq décors (arbres, buissons, bancs)
  sont DÉPLACÉS sur la pelouse voisine, à leur place dans la liste. Le choix se fait au moindre coût, sans un
  dé ; une fenêtre dont un décor ne trouve pas de place est défaite et la suivante essayée — une autre graine
  ne fait jamais planter la ville.
- ⚠️ **Le marché aux puces s'installait sur la glace** : il prend le terrain vague libre le plus proche de la
  planque, et la clairière en était un. La patinoire et le tour de ses bandes sont maintenant des tuiles prises
  (`frenesies._prises`, que lisent aussi les icônes, les cartes et les sauts). La ville du jeu, bande nord
  comprise, est la même clé par clé avec et sans la patinoire, hors du décor déplacé (`test_patinoire.py`).
- **La peinture** (`static/js/patinoire.js`) : l'hiver (`Saisons.enHiver`), la glace et ses rayures, la ligne
  rouge du centre, deux filets, les bandes blanches à liseret rouge, quatre lampadaires qui éclairent le soir ;
  l'été, rien — la clairière est du gazon.
- **Les bandes sont solides** l'hiver : aucun char sur la glace (`Monde.barriereBloque`) ; à pied, on entre par
  les portes (`Entites.bloquerParDecor`). Un char déjà dessus en sort librement.
- **La glisse** : sur la glace, la vitesse voulue se rejoint peu à peu (`elan` quand on pousse, `freinage` quand
  on lâche) — pour le joueur et pour tout passant. Mesuré au banc : sur une demi-seconde de poussée on part
  moins vite qu'au sec, puis on file une soixantaine de pixels sur son élan (au sec : zéro).
- **La chute** : courir sans patins (ESQUIVE tenue) près d'une seconde, ou virer de plus de 110° lancé, et on
  tombe (`auSol`, comme projeté) — sans un dé. Un premier jet repartait de la vitesse voulue quand la suite des
  images se rompait : on démarrait sur la glace aussi vite qu'au sec ; le juge de l'élan l'a pris.
- **Pas encore** : les chars ne dérapent pas sur la glace — ils n'y entrent jamais, les bandes les arrêtent.

### ✅ Vague 2 — les patineurs (30 sept. 2026)

- **De vrais passants** (`Entites.creerPieton`, marqués `patineur`) : ils naissent SUR la glace pendant qu'elle
  est hors de l'écran et que le joueur est à moins de 480 px — on arrive, elle est pleine ; personne n'apparaît
  sous nos yeux. Trois le matin (9 h), sept l'après-midi, neuf le soir, personne après 22 h ni l'été. Ils
  repartent hors de l'écran à la fermeture ou quand on s'éloigne.
- **Ils tournent** à contre-sens des aiguilles d'une montre, chacun sur son couloir (trois anneaux), par `cap`,
  avec l'élan de la glace ; des lames claires sous leurs pieds.
- **Un enfant sur trois** (par le rang d'arrivée) ; un enfant lancé tombe parfois (une chance sur 25 à chaque
  seconde, à l'empreinte de son numéro et de la seconde), couché le temps de se relever.
- **Bousculé, il n'est plus mené** : un patineur qui fuit, assommé ou témoin, redevient un passant comme un autre
  — et il glisse en se sauvant.
- ⚠️ **`hash2` répartit mal ses petites entrées** : un seuil « 35 % d'enfants » sur `hash2(rang, sel)` n'en
  donnait AUCUN de 0 à 9. Le rang décide (`un_enfant_sur`).

### ✅ Vague 3 — les patins à louer, et le son (30 sept. 2026)

- **Au guichet du kiosque de Madame Thibodeau**, et pas une cabane de plus : son kiosque touche la bande est, le
  guichet est la tuile de glace collée à son mur (`p.guichet`, la plus proche de sa porte). ⚠️ On ne loue pas en
  lui parlant : ACTION près d'elle, c'est sa conversation de mission, qui passe avant tout le reste. ⚠️ La
  tuile se départage à la distance VRAIE : au max des écarts, le coin nord-est l'emportait, et la bande nord y
  repoussait le joueur hors de la glace (vu sur la capture, pas par les juges — ils le disent maintenant).
  ⚠️ La porte d'un lieu se nomme par `lieu`, pas `slug` : sans ça, le guichet retombait sans bruit sur une porte
  des bandes.
- **ACTION, deux piastres** : on chausse (`j.patins`), elle dit un mot à elle (« Tiens, mon p'tit… »). Sans le
  sou, on reste en bottes. On les rend en quittant la glace.
- **En patins, plus vite MAIS on glisse toujours** (Martin : « patin, mais on doit glisser aussi ») : ×1,6 sur la
  vitesse voulue, un élan plus franc, un arrêt encore plus long ; on ne tombe plus en courant, seulement en
  virant sec lancé.
- **Le son** (ElevenLabs) : la rumeur de la glace (`patinoire-1.mp3`, 6 s en boucle : les lames, une rondelle
  contre la bande, des enfants) tant qu'on y patine, et la valse du haut-parleur le soir de 17 h à 22 h
  (`musique-patinoire_valse.mp3`, 30 s, par `Son.Rue` comme l'orgue de la foire ; son filet en notes :
  `musique.VALSE`) — dosées à la distance du centre de la glace, en fondu. ⚠️ Le plafond des sons de lieu
  (1,95 Mo, `test_audio`) n'avait plus que 25 Ko : la rumeur est une boucle de 6 s (pas 10 : une boucle ne se
  coupe pas), mono 44,1 kHz à 32 kbit/s, 24 Ko — on compresse avant de relever ; la version à 64 kbit/s attend
  une décision de Martin.
- **Pas encore** : les chars ne dérapent pas sur la glace (les bandes les arrêtent) ; les mots de location ne
  sont pas dits à voix haute.
