# Software Factory

Une application web où quatre agents IA conçoivent un petit logiciel à partir de votre description, puis vous remettent le tout dans une archive ZIP.

Vous décrivez l'outil voulu, par exemple « un outil de gestion de factures avec calcul des taxes et export CSV ». Les agents travaillent l'un après l'autre :

1. le chef de projet rédige le cahier des charges ;
2. l'architecte propose la structure technique ;
3. le développeur écrit le code, fichier par fichier ;
4. l'ingénieur QA relit, corrige et renvoie la version finale.

Vous pouvez ensuite télécharger le rapport complet (`.md`) et un ZIP contenant un fichier par bloc de code.

## Utiliser l'application

1. Choisissez un fournisseur dans la barre latérale : Anthropic, OpenAI, Google Gemini ou Mistral AI.
2. Collez votre clé API, puis cliquez sur « Vérifier la clé ». Le statut s'affiche juste en dessous.
3. Choisissez un modèle. Les petits modèles (Haiku, mini, flash, small) coûtent moins cher pour un premier essai.
4. Décrivez l'outil, puis cliquez sur « Lancer la brigade d'agents ».

Une génération prend en général quelques minutes. Elle consomme du crédit sur votre compte chez le fournisseur choisi.

### Où obtenir une clé API

| Fournisseur | Adresse |
|---|---|
| Anthropic | https://platform.claude.com/settings/keys |
| OpenAI | https://platform.openai.com/api-keys |
| Google Gemini | https://aistudio.google.com/apikey |
| Mistral AI | https://console.mistral.ai |

L'API est facturée à l'usage, séparément d'un éventuel abonnement au chat du fournisseur.

## À propos de votre clé

La clé que vous saisissez est utilisée uniquement pour votre session. Elle est transmise directement au modèle de langage, sans passer par une variable d'environnement partagée, et n'est enregistrée nulle part. Si elle apparaît dans un message d'erreur, elle est masquée.

Pour limiter les risques, créez une clé réservée à cette application et fixez une limite de dépense dans la console du fournisseur.

## Installer chez soi

Il faut Python 3.10 à 3.13.

```bash
git clone https://github.com/borino49/software-factory.git
cd software-factory
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Publiez ce dépôt sur GitHub.
2. Sur share.streamlit.io, créez une application pointant vers `app.py`.
3. Streamlit installe les dépendances de `requirements.txt` et redéploie à chaque modification du dépôt.

## Contenu du dépôt

- `app.py` : l'application Streamlit (interface, agents, export ZIP).
- `requirements.txt` : les dépendances Python.
- `.devcontainer/` : configuration pour GitHub Codespaces.

## Limites connues

- Le code produit par les agents doit toujours être relu et testé avant usage réel. La relecture par l'agent QA ne remplace pas un vrai test.
- Si le développeur ne respecte pas le format `### nom.ext` suivi d'un bloc de code, le ZIP contient les blocs sous les noms `bloc_1.txt`, `bloc_2.txt`, etc.
- Une description très large peut produire une réponse longue et coûteuse. Mieux vaut décrire un outil précis.
