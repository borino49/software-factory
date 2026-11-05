# Software Factory

Décrivez l'outil dont vous avez besoin. Quatre agents IA le conçoivent pour vous et vous remettent le résultat dans une archive ZIP.

**Essayer l'application :** https://software-factory-cifkvias365hkgrcexacwm.streamlit.app/

## Ce que vous obtenez

Vous écrivez une demande simple, par exemple « un outil de gestion de factures avec calcul des taxes et export CSV ». Les agents travaillent l'un après l'autre :

1. le chef de projet rédige le cahier des charges ;
2. l'architecte propose la structure technique ;
3. le développeur écrit le code, fichier par fichier ;
4. l'ingénieur qualité relit le code, le corrige et renvoie la version finale.

Vous téléchargez ensuite le rapport complet (`.md`) et un ZIP avec un fichier par bloc de code.

## Comment l'utiliser

1. Dans la barre latérale, choisissez un fournisseur : Anthropic, OpenAI, Google Gemini ou Mistral AI.
2. Collez votre clé API, puis cliquez sur « Vérifier la clé ». Le résultat s'affiche juste en dessous.
3. Choisissez un modèle. Pour un premier essai, prenez un petit modèle (Haiku, mini, flash ou small), il coûte moins cher.
4. Décrivez l'outil voulu, puis cliquez sur « Lancer la brigade d'agents ».

Comptez quelques minutes par génération.

## Votre clé API

L'application n'a pas de clé à elle : vous utilisez la vôtre, et c'est votre compte chez le fournisseur qui paie les appels. L'API est facturée à l'usage, séparément d'un éventuel abonnement au chat.

| Fournisseur | Où créer une clé |
|---|---|
| Anthropic | https://platform.claude.com/settings/keys |
| OpenAI | https://platform.openai.com/api-keys |
| Google Gemini | https://aistudio.google.com/apikey |
| Mistral AI | https://console.mistral.ai |

Quelques conseils :

- Créez une clé réservée à cet usage, et fixez une limite de dépense dans la console du fournisseur.
- Ne partagez jamais votre clé, ni par message ni par capture d'écran.
- Votre clé sert uniquement le temps de votre session. L'application ne l'enregistre pas.

## Bon à savoir

- Relisez et testez toujours le code reçu avant de l'utiliser pour de vrai. La relecture par l'agent qualité ne remplace pas un test.
- Une demande précise donne un meilleur résultat qu'une demande vague, et coûte moins cher.
- Chaque projet du ZIP se lance à sa façon, selon ce que les agents ont écrit. Lisez d'abord le rapport `.md`, ou demandez aux agents d'ajouter un fichier d'instructions dans votre demande.
- Si le ZIP contient des fichiers nommés `bloc_1.txt`, `bloc_2.txt`, c'est que les agents n'ont pas indiqué les noms de fichiers. Le rapport `.md` contient alors tout le code.
- Un problème ou une question : ouvrez une demande dans l'onglet « Issues » de ce dépôt.
