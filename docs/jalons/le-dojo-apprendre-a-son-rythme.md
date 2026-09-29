# Le dojo : apprendre à son rythme

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026, devant LES COURS (trois techniques « PAYÉ — À REPRENDRE ») : « change comment on
apprend ces techniques, c'est trop dur ». Troisième retour sur la leçon du [dojo du
quartier](le-dojo-du-quartier.md#fiche), après [des leçons qu'on comprend](le-dojo-des-lecons-qu-on-comprend.md#fiche)
(fenêtre de 0,6 s, la carte des boutons) et [Bandini revient sur sa marque](le-dojo-bandini-revient-sur-sa-marque.md#fiche).
Ce n'est plus un réglage : c'est le principe — trois réussites dans la fenêtre du « et » — qui ne tient pas.
Tranché avec Martin : **à son rythme**, trois réussites, aucun échec.

- **Plus de métronome** : ni compte « UN DEUX ET », ni barre, ni claquements, ni fenêtre. Le tatami, Kevin,
  Mireille, l'annonce et la carte des boutons restent.
- **Une réussite** = la technique enseignée qui **porte sur Kevin** (`Techniques.quandPorte`), n'importe
  quand. **Trois** : apprise.
- **Aucun échec** : les cinq ratés disparaissent, on reste sur le tatami tant qu'on veut. Un geste enseigné
  qui ne porte pas : Mireille glisse « Tu danses tout seul », sans pénalité. « Trop tôt » est retirée.
- **Kevin se remet en place** ≈ 1 s après chaque essai (et Bandini sur sa marque) : de dos pour
  l'étranglement ; pour la **parade**, il arme un coup **lent**, bien télégraphié, toutes les ≈ 2 s ; pour le
  **balayage**, il attaque lentement — on roule, puis on balaie.
- **Sortir** (la porte, ABANDONNER) : le cours reste payé, on reprend sans repayer.
- **Juges au banc, au bouton** : trois réussites espacées au hasard apprennent ; vingt coups dans le vide
  n'annulent rien ; la parade et le balayage s'apprennent contre le Kevin lent ; sortir laisse le cours payé.
  Chaque règle mutée une fois.

## Notes

**Livré le 29 sept. 2026.**

- **Un essai** (`B.cours.essai`) : du geste qui part — un coup, une prise, une roulade et sa sortie — jusqu'à ce
  qu'il retombe, et que Kevin, s'il vole, soit retombé aussi. Jugé à ce moment-là : la technique enseignée a
  porté sur Kevin (`quandPorte`, retenu même avant que l'essai soit vu : le retournement porte à son étape 0),
  c'est **OUI !** ; elle est partie sans porter, **PRESQUE** et « Tu danses tout seul » ; autre chose, rien.
  Trois OUI, apprise. Rien ne compte contre toi.
- **La remise en place** : 45 images après un essai (`dojo.REMISE_IMAGES`), Kevin et Bandini reprennent leur
  marque — le compte repart tant que Bandini marche : personne n'est téléporté en pleine course.
- ⚠️ **Le vrai mur de la parade** : le coup de rue que Kevin armait n'arme que **5 images** (0,08 s). En leçon,
  il arme toutes les 2 s (`CADENCE_ARME`), TIENT l'élan 45 images (`ANTICIPATION_KEVIN`) et crie « HA ! » dans
  une bulle. Pour le balayage, il reste menaçant (`attaque_joueur`) tout le long : la roulade a sa raison.
- **La chaîne** reste au maillon d'avant tant qu'on ne frappe pas : une tape fait partir l'uppercut, pas un
  direct du gauche.
- **Retirés** : le compte « UN DEUX ET » et sa barre, le métronome (`Son.SFX.claquement`), `TEMPS_IMAGES`,
  `FENETRE_IMAGES`, `RATES_MAX`, et deux voix de Mireille (« Trop tôt », et « On reprendra… », qui ne se disait
  qu'après cinq ratés) ; « Tu danses tout seul » devient `mireille-dojo-dans_le_vide`. La carte du pied de côté
  dit « TIENS [X] … PUIS LÂCHE ».
- **Juges** (`test_dojo_js.py`) : trois uppercuts espacés au hasard, trois réussites ; vingt coups dans le vide,
  vingt PRESQUE et la leçon toujours là ; chaque mise en place s'apprend au bouton à son rythme ; le pied sauté
  après un essai qui laisse Bandini derrière Kevin ; la remise, et personne ramené en marchant ; Kevin arme
  lentement et crie. Huit mutations (la réussite, un échec remis, la course, la remise, l'anticipation, le cri,
  la menace, la chaîne), chacune a fait rougir son juge. Capture Chromium de la parade : lisible.
