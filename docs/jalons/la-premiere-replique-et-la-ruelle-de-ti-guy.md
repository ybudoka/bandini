# La première réplique, et la ruelle de Ti-Guy

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026), « oui corrige tout », après « Quatre trous dans les
missions » : les deux restes de la vérification au bouton. L'appui d'ACTION qui lance une
conversation saute sa première réplique, chez les cinq donneurs, au clavier comme à la
manette : `Combat.maj` ouvre le dialogue, puis `Histoire.maj` relit le même appui dans la
même image et passe à la deuxième — on ne lit jamais « Heille! Le cousin de Rocco! », ni la
phrase qui explique la mission. Et Ti-Guy dit encore « la ruelle derrière le garage » alors
que le char dort à vingt-quatre tuiles : la réplique change, et sa voix (`ti_guy-m1-3`) se
régénère.

**Livré.** `Histoire.majCinema` n'écoute plus les boutons à la première image d'une ligne :
l'appui qui ouvre la conversation ne la saute plus. Le compte est celui de la ligne (`c.t`),
pas `B.t`, qui s'arrête pendant une scène — on passe toujours une réplique au bouton dès
l'image suivante. Ti-Guy dit « Y a un char qui traîne dans une ruelle, un peu plus loin.
Personne va s'en ennuyer. » (`missions.py` et son jeu dans `interpretation.py`), et
`histoire-ti_guy-m1-3.mp3` est régénéré en v3 (99 crédits, 4,98 s, −19,3 LUFS comme
l'ancienne, master gardé dans `~/elevenlabs-audio/bandini-voix-v3-masters-2026-09-16/`).
Juge : `test_la_premiere_replique_se_dit_quand_on_parle_au_bouton` (`test_histoire_js.py`) —
les cinq donneurs au clavier, Ti-Guy à la manette, l'intro jouée scène comprise ; rouge sans
la garde (« `ti_guy-m1-2`, pas `ti_guy-m1-1` »).

- ⚠️ Personne d'autre que Martin ne peut juger la nouvelle voix : elle a le niveau et le
  temps mort de l'ancienne, pas forcément le même ton.
