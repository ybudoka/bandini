# Le tableau des scores s'en va

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (17 sept. 2026), en réponse à la dette « un score ne s'envoie pas hors
ligne » : « le score pourrait être complètement enlevé ». **Tout** s'en va — le bouton
MEILLEURS SCORES du titre, la ligne ENVOYER MON SCORE du bilan, l'écran du pseudo,
`/api/scores`, `app/scores.py` et son fichier JSON, le pseudo de la partie. La 4e vague de
M14 (« les scores déménagent dans la base ») tombe avec, et la dette aussi.

**Livré** (17 sept. 2026). Sont partis : `app/scores.py` et `tests/test_scores.py`, les deux
routes `/api/scores`, le bouton MEILLEURS SCORES, les deux voiles (le tableau et le nom), leurs
styles, la ligne ENVOYER MON SCORE du bilan, `Hud.montrerScores/envoyerScore/demanderScore/
afficherScores`, le pseudo de la partie, et le `scores.json` du serveur. Un juge le tient :
`/api/scores` rend 404, et le mot « score » n'est plus nulle part dans la page.

- ⚠️ Les **règles du pseudo** (`pseudo_propre`, `PSEUDO_MAX`) vivaient dans `scores.py` et
  servent aux **comptes de M14** : elles ont déménagé chez eux (`comptes.py`), avec leur juge
- ⚠️ **`economie.GAIN_MAX_PAR_SECONDE` reste**, mais change de raison d'être : c'était la
  borne de vraisemblance d'un score envoyé, c'est maintenant un garde d'équilibre — aucun
  boulot ne doit la dépasser (`test_economie`)
- ⚠️ **Deux choses qui menaient au score** se sont trouvé une autre fin : le **générique**
  de M13 mène au BILAN, et la **4e vague de M14** perd son déménagement
- ⚠️ Le `voile()` du HUD ne sert plus qu'au **titre** — c'est lui, et lui seul, qui fait
  sortir du casque Quest (`casque.js`)
