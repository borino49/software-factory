import hashlib
import io
import re
import zipfile

import httpx
import streamlit as st
from crewai import LLM, Agent, Crew, Process, Task

st.set_page_config(
    page_title="Software Factory - Multi-Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🚀 Software Factory Multi-Agent (v6)")
st.markdown(
    "Décrivez l'outil voulu. Quatre agents rédigent le cahier des charges, "
    "l'architecture, le code et l'audit, puis tout est empaqueté dans un ZIP."
)

# ---------------------------------------------------------------------------
# Barre latérale : fournisseur, modèle et clé API
# ---------------------------------------------------------------------------
st.sidebar.header("🔐 Configuration")

PROVIDERS = {
    "Anthropic": {
        "label_key": "Clé API Anthropic (sk-ant-...)",
        "models": ["anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-5-5"],
    },
    "OpenAI": {
        "label_key": "Clé API OpenAI (sk-...)",
        "models": ["openai/gpt-4o", "openai/gpt-4o-mini"],
    },
    "Google (Gemini)": {
        "label_key": "Clé API Google Gemini",
        "models": ["gemini/gemini-2.5-pro", "gemini/gemini-2.5-flash"],
    },
    "Mistral AI": {
        "label_key": "Clé API Mistral",
        "models": ["mistral/mistral-large-latest", "mistral/mistral-small-latest"],
    },
}

CHECKS = {
    "Anthropic": ("https://api.anthropic.com/v1/models",
                  lambda k: {"x-api-key": k, "anthropic-version": "2023-06-01"}),
    "OpenAI": ("https://api.openai.com/v1/models",
               lambda k: {"Authorization": f"Bearer {k}"}),
    "Google (Gemini)": ("https://generativelanguage.googleapis.com/v1beta/models",
                        lambda k: {"x-goog-api-key": k}),
    "Mistral AI": ("https://api.mistral.ai/v1/models",
                   lambda k: {"Authorization": f"Bearer {k}"}),
}


def verifier_cle(fournisseur: str, cle: str) -> tuple[bool, str]:
    """Appel léger de liste de modèles : valide la clé sans consommer de crédit."""
    url, entetes = CHECKS[fournisseur]
    try:
        r = httpx.get(url, headers=entetes(cle), timeout=15)
    except httpx.HTTPError:
        return False, "Impossible de joindre le fournisseur. Réessayez."
    if r.status_code == 200:
        return True, "Clé valide."
    if r.status_code in (400, 401, 403):
        return False, "Clé refusée. Vérifiez qu'elle est complète et active."
    if r.status_code == 429:
        return True, "Clé reconnue (limite de requêtes atteinte pour l'instant)."
    return False, f"Réponse inattendue du fournisseur (code {r.status_code})."


llm_provider = st.sidebar.selectbox("Fournisseur", list(PROVIDERS.keys()), index=0)
config = PROVIDERS[llm_provider]
user_api_key = st.sidebar.text_input(config["label_key"], type="password")
selected_model = st.sidebar.selectbox("Modèle", config["models"], index=0)

# On retient le résultat pour cette clé précise, pas la clé elle-même
empreinte = hashlib.sha256(f"{llm_provider}:{user_api_key}".encode()).hexdigest()

if st.sidebar.button("✔️ Vérifier la clé", disabled=not user_api_key):
    with st.sidebar:
        with st.spinner("Vérification..."):
            ok, msg = verifier_cle(llm_provider, user_api_key)
    st.session_state["verif"] = {"empreinte": empreinte, "ok": ok, "msg": msg}

verif = st.session_state.get("verif")
if not user_api_key:
    st.sidebar.info("Collez votre clé, puis cliquez sur « Vérifier la clé ».")
elif verif and verif["empreinte"] == empreinte:
    (st.sidebar.success if verif["ok"] else st.sidebar.error)(
        ("✅ " if verif["ok"] else "❌ ") + verif["msg"]
    )
else:
    st.sidebar.warning("Clé saisie, pas encore vérifiée.")

st.sidebar.caption(
    "Votre clé reste dans la session en cours. Elle n'est ni enregistrée "
    "ni partagée avec les autres visiteurs."
)

# ---------------------------------------------------------------------------
# Saisie du besoin
# ---------------------------------------------------------------------------
st.markdown("### 📝 Décrivez l'outil à créer")
besoin_utilisateur = st.text_area(
    "Exemple : un outil de gestion des factures avec calcul des taxes et export CSV.",
    height=120,
)


def nom_fichier_sur(nom: str) -> str | None:
    """Refuse les chemins dangereux avant de les écrire dans le ZIP."""
    nom = nom.strip().replace("\\", "/")
    if not nom or nom.startswith("/") or ".." in nom.split("/"):
        return None
    return nom


def construire_zip(resultat_str: str) -> tuple[io.BytesIO, int]:
    """Crée le ZIP : rapport complet + un fichier par bloc de code nommé."""
    buffer = io.BytesIO()
    nb_fichiers = 0

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("rapport_software_factory.md", resultat_str)

        # Format attendu : "### nom.ext" suivi d'un bloc de code
        motif_nomme = (
            r"###\s+`?([a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+)`?\s*\n+"
            r"```[a-zA-Z]*\n(.*?)```"
        )
        blocs_nommes = re.findall(motif_nomme, resultat_str, re.DOTALL)

        for nom, contenu in blocs_nommes:
            nom_sur = nom_fichier_sur(nom)
            if nom_sur:
                zf.writestr(nom_sur, contenu.strip())
                nb_fichiers += 1

        # Secours : aucun nom détecté, on garde tous les blocs de code
        if nb_fichiers == 0:
            blocs = re.findall(r"```[a-zA-Z]*\n(.*?)```", resultat_str, re.DOTALL)
            for i, contenu in enumerate(blocs, start=1):
                zf.writestr(f"bloc_{i}.txt", contenu.strip())
                nb_fichiers += 1

    buffer.seek(0)
    return buffer, nb_fichiers


# ---------------------------------------------------------------------------
# Lancement des agents
# ---------------------------------------------------------------------------
if st.button("Lancer la brigade d'agents", type="primary"):
    if not user_api_key:
        st.error(f"⚠️ Entrez votre clé API {llm_provider} dans la barre latérale.")
    elif not besoin_utilisateur.strip():
        st.warning("⚠️ Décrivez d'abord l'outil que vous voulez concevoir.")
    else:
        with st.spinner(f"Les agents travaillent avec {llm_provider} ({selected_model})..."):
            try:
                # La clé est transmise directement à l'objet LLM, sans passer
                # par os.environ, qui est partagé entre tous les visiteurs.
                llm = LLM(model=selected_model, api_key=user_api_key)

                orchestrateur = Agent(
                    role="Chef de projet et orchestrateur technique",
                    goal="Analyser le besoin et coordonner l'équipe.",
                    backstory="Tu traduis les besoins en cahier des charges clair.",
                    llm=llm,
                    verbose=False,
                )
                architecte = Agent(
                    role="Architecte logiciel senior",
                    goal="Concevoir l'architecture globale et le schéma de données.",
                    backstory="Tu définis la structure technique, les flux et le modèle de données.",
                    llm=llm,
                    verbose=False,
                )
                developpeur = Agent(
                    role="Développeur fullstack expert",
                    goal="Écrire un code complet, modulaire et réparti en fichiers distincts.",
                    backstory=(
                        "Tu produis tout le code source. Pour chaque fichier, tu écris "
                        "son nom exact sous la forme `### nom_du_fichier.ext` juste "
                        "au-dessus du bloc de code."
                    ),
                    llm=llm,
                    verbose=False,
                )
                testeur = Agent(
                    role="Ingénieur sécurité et QA",
                    goal="Auditer le code et corriger les défauts.",
                    backstory="Tu cherches les bugs, les failles de sécurité et les fragilités.",
                    llm=llm,
                    verbose=False,
                )

                t1 = Task(
                    description=f"Analyse ce besoin et rédige un cahier des charges : {besoin_utilisateur}",
                    expected_output="Un cahier des charges fonctionnel détaillé.",
                    agent=orchestrateur,
                )
                t2 = Task(
                    description="Élabore le plan d'architecture technique et le modèle des composants.",
                    expected_output="Un plan d'architecture clair.",
                    agent=architecte,
                )
                t3 = Task(
                    description=(
                        "Écris tout le code source nécessaire. Sépare chaque fichier avec "
                        "un titre de niveau 3 portant son nom (ex : `### app.py`), suivi "
                        "du bloc de code markdown."
                    ),
                    expected_output="Le code source complet, réparti en fichiers nommés.",
                    agent=developpeur,
                )
                t4 = Task(
                    description=(
                        "Relis le code, corrige les bugs et failles éventuels, puis "
                        "renvoie la version finale en gardant le format `### nom.ext` "
                        "suivi du bloc de code pour chaque fichier."
                    ),
                    expected_output="Le code final audité, réparti en fichiers nommés.",
                    agent=testeur,
                )

                equipe = Crew(
                    agents=[orchestrateur, architecte, developpeur, testeur],
                    tasks=[t1, t2, t3, t4],
                    process=Process.sequential,
                    verbose=False,
                )

                resultat_str = str(equipe.kickoff())

                st.success(f"✅ Projet conçu avec {llm_provider}.")
                st.markdown("### 📋 Rapport et code")
                st.markdown(resultat_str)

                zip_buffer, nb_fichiers = construire_zip(resultat_str)

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Télécharger le rapport (.md)",
                        data=resultat_str,
                        file_name=f"software_factory_{llm_provider.lower().split()[0]}.md",
                        mime="text/markdown",
                    )
                with col2:
                    if nb_fichiers > 0:
                        st.download_button(
                            label=f"📦 Télécharger le ZIP ({nb_fichiers} fichiers)",
                            data=zip_buffer,
                            file_name="software_project_export.zip",
                            mime="application/zip",
                        )
                    else:
                        st.info("Aucun bloc de code détecté pour le ZIP.")

            except Exception as e:
                message = str(e)
                # On masque la clé si elle apparaît dans un message d'erreur
                if user_api_key:
                    message = message.replace(user_api_key, "***")
                bas = message.lower()
                if "429" in message or "quota" in bas or "credit" in bas:
                    st.error(f"❌ Quota ou crédit épuisé sur votre compte {llm_provider}.")
                elif "authentication" in bas or "api key" in bas or "401" in message:
                    st.error(f"❌ Clé API {llm_provider} refusée. Vérifiez-la.")
                else:
                    st.error(f"Une erreur est survenue : {message}")
