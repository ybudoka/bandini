# Le tour du propriétaire montre ses quatre contacts

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (20 sept. 2026) : « améliore l'animation de la mission tour du propriétaire
pour voir toutes les cibles, pas juste la première ».

- ⚠️ **Mesuré avant**, au banc : l'intro de m6 (Josée, dedans) ne filme que le dépanneur —
  une seule `coupe`, 159 images à l'écran — alors que Josée nomme quatre portes (dépanneur,
  cantine, usine, phare) : les trois autres ne se voient jamais. Et sa première réplique
  (6,0 s de voix, 360 images) est coupée à l'image 229 par la deuxième, parce que la coupe qui
  la porte ne tient que 230 : « ma sœur Lulu à la cantine » ne s'entendait pas.
- **Une `coupe` visite plusieurs lieux.** `vers` accepte une liste (`["chez:tipaul",
  "chez:lulu"]`) : chaque lieu a son noir (`ferme`, `ouvre`) et tient `tient` images, dans
  l'ordre, et la pièce ne revient qu'à la fin — jamais entre deux lieux, sans quoi le bar
  clignoterait entre deux plans. Un lieu seul joue exactement l'aller-retour d'avant (34 images
  pour `ferme` 6, `ouvre` 6, `tient` 10, comme avant). Un lieu qui ne se trouve pas est sauté et
  compté (`sautes`), les autres se jouent. Le vocabulaire ne change pas d'une clé : `TYPES_PLANS`
  et le paquet sont les mêmes ; seuls `vers` (une liste, pour la coupe seule) et la validation
  (`_lieux_du_plan`) le savent.
- **L'intro de m6 : deux coupes de deux portes, calées sur les voix.** Les pauses des mp3
  (`ffmpeg silencedetect`) donnent où chaque contact est nommé : Ti-Paul à l'image 141 de la
  réplique 1, Lulu à la 242 ; Raymonde d'entrée dans la 2, Ovila à la 164. Josée dit d'abord
  « quatre coins » dans le bar (100 images), puis Ti-Paul et Lulu défilent sous la réplique 1,
  Raymonde et Ovila sous la 2, et Josée montre la sortie sur la 3. Chaque coupe survit à sa
  réplique (deux `attendre` de marge : 70 et 60 images) : c'est la coupe qui retient la scène, et
  une voix plus longue qu'elle serait coupée par la suivante. 1 071 images (17,9 s) contre 969.
- **Vu en vrai** : capture Chromium des quatre plans — l'enseigne, la porte au centre, la
  boîte de Josée en dessous : « Chez Ti-Paul », « Cantine », « Usine Prévost » (Raymonde devant)
  et « Le Phare ».
- **Trois juges** (`test_scenes_js.py`, `test_missions_en_scene_js.py`, `test_mise_en_scene.py`).
  La coupe en liste : trois lieux vus dans l'ordre, un noir plein par lieu et un pour le retour,
  78 images. Le tour : chaque contact à l'écran au moins une seconde, dans l'ordre, sous la
  réplique qui le nomme, et le bar rendu. Et la voix : la réplique suivante part après la fin du
  **fichier** (`ffprobe`) plus une demi-seconde. ⚠️ Rouges avant sur l'ancienne scène (Lulu à
  0 image ; 229 images pour 360 de voix) et sur l'ancien moteur. Le juge des lieux lit aussi
  les listes (`_lieux_du_plan`) : sans elle, `chez:personne` dans une liste passait.
- ⚠️ **Pas fait, à savoir** : les intros de m2, m3, m4, m5 et m97 ont le même défaut que m6
  avait — leur première réplique est coupée par la deuxième (de 0,6 s à 1,9 s de voix perdues,
  mesuré avec les durées des mp3). Le remède général serait qu'une `dire` attende son tour au
  lieu de remplacer celle qui parle ; il touche toutes les scènes, donc il n'est pas dans ce
  correctif.
