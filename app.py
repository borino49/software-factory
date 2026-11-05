import os
import streamlit as st
from crewai import Agent, Crew, Process, Task

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Software Factory - Multi-Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🚀 Software Factory Multi-Agent (v4 - Multi-Fournisseurs)")
st.markdown("Concevez, auditez et téléchargez vos applications avec le fournisseur d'IA de votre choix (OpenAI, Anthropic, Google, Mistral).")

# Barre latérale (Sidebar) pour le choix du fournisseur et la sécurité
st.sidebar.header("🔐 Configuration & Sécurité")

# Choix élargi du fournisseur LLM
llm_provider = st.sidebar.selectbox(
    "Choisissez le fournisseur",
    ["OpenAI", "Anthropic", "Google (Gemini)", "Mistral AI"],
    index=0
)

# Configuration dynamique selon le fournisseur choisi
if llm_provider == "OpenAI":
    user_api_key = st.sidebar.text_input("Clé API OpenAI (sk-...)", type="password")
    selected_model = st.sidebar.selectbox("Modèle OpenAI", ["gpt-4o", "gpt-4o-mini"], index=0)
    env_key_name = "OPENAI_API_KEY"
elif llm_provider == "Anthropic":
    user_api_key = st.sidebar.text_input("Clé API Anthropic (sk-ant-...)", type="password")
    selected_model = st.sidebar.selectbox(
        "Modèle Anthropic", 
        ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"], 
        index=0
    )
    env_key_name = "ANTHROPIC_API_KEY"
elif llm_provider == "Google (Gemini)":
    user_api_key = st.sidebar.text_input("Clé API Google Gemini", type="password")
    selected_model = st.sidebar.selectbox(
        "Modèle Gemini", 
        ["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash"], 
        index=0
    )
    env_key_name = "GEMINI_API_KEY"
else:  # Mistral AI
    user_api_key = st.sidebar.text_input("Clé API Mistral", type="password")
    selected_model = st.sidebar.selectbox(
        "Modèle Mistral", 
        ["mistral/mistral-large-latest", "mistral/mistral-small-latest"], 
        index=0
    )
    env_key_name = "MISTRAL_API_KEY"

# Zone de saisie principale
st.markdown("### 📝 Décrivez votre besoin ou l'outil à créer")
besoin_utilisateur = st.text_area(
    "Exemple : Crée-moi un outil de gestion des factures avec calcul automatique des taxes et export CSV.",
    height=120
)

# Bouton de lancement
if st.button("Lancer la Brigade d'Agents", type="primary"):
    if not user_api_key:
        st.error(f"⚠️ Veuillez entrer votre clé API {llm_provider} dans la barre latérale pour continuer.")
    elif not besoin_utilisateur.strip():
        st.warning("⚠️ Veuillez décrire l'outil que vous souhaitez concevoir.")
    else:
        # Nettoyage complet de toutes les clés pour éviter les interférences
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "MISTRAL_API_KEY"]:
            os.environ.pop(key, None)
        
        # Injection de la clé active et du modèle
        os.environ[env_key_name] = user_api_key
        os.environ["OPENAI_MODEL_NAME"] = selected_model

        with st.spinner(f"🔄 Les agents collaborent via {llm_provider} ({selected_model})..."):
            try:
                # Définition des Agents
                orchestrateur = Agent(
                    role="Chef de Projet & Orchestrateur Technique",
                    goal="Analyser les besoins et coordonner l'équipe.",
                    backstory="Tu traduis les besoins en cahier des charges et supervises les échanges.",
                    verbose=False,
                    llm=selected_model
                )

                architecte = Agent(
                    role="Architecte Logiciel Senior",
                    goal="Concevoir l'architecture globale et le schéma de données.",
                    backstory="Tu définis la structure technique, les flux et le modèle des données.",
                    verbose=False,
                    llm=selected_model
                )

                developpeur = Agent(
                    role="Développeur Fullstack Expert",
                    goal="Rédiger le code complet et fonctionnel.",
                    backstory="Tu produis l'intégralité du code source propre, commenté et sans omission.",
                    verbose=False,
                    llm=selected_model
                )

                testeur = Agent(
                    role="Ingénieur Sécurité & QA",
                    goal="Auditer le code et valider la sécurité.",
                    backstory="Tu vérifies l'absence de bugs, les failles de sécurité et la robustesse.",
                    verbose=False,
                    llm=selected_model
                )

                # Définition des Tâches
                t1 = Task(
                    description=f"Analyser ce besoin et rédiger un cahier des charges : {besoin_utilisateur}",
                    expected_output="Un cahier des charges fonctionnel détaillé.",
                    agent=orchestrateur
                )
                t2 = Task(
                    description="Élaborer le plan d'architecture technique et le modèle des composants.",
                    expected_output="Un plan d'architecture clair.",
                    agent=architecte
                )
                t3 = Task(
                    description="Écrire tout le code source nécessaire pour rendre l'outil 100% opérationnel.",
                    expected_output="Le code source complet de l'application.",
                    agent=developpeur
                )
                t4 = Task(
                    description="Vérifier le code, détecter d'éventuels bugs et valider sa conformité.",
                    expected_output="Le code final audité et validé.",
                    agent=testeur
                )

                # Création et exécution de la Crew
                software_factory = Crew(
                    agents=[orchestrateur, architecte, developpeur, testeur],
                    tasks=[t1, t2, t3, t4],
                    process=Process.sequential,
                    verbose=False
                )

                resultat = software_factory.kickoff()
                resultat_str = str(resultat)

                # Affichage du succès
                st.success(f"✅ Application conçue avec succès via {llm_provider} !")
                st.markdown("### 📋 Rapport & Code de la Brigade :")
                st.markdown(resultat_str)

                # Persistance via téléchargement
                provider_slug = llm_provider.lower().replace(" ", "_").replace("(", "").replace(")", "")
                st.download_button(
                    label="📥 Télécharger le rapport et le code généré (.md)",
                    data=resultat_str,
                    file_name=f"software_factory_{provider_slug}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    st.error(f"❌ Erreur de quota : Votre compte {llm_provider} est épuisé.")
                elif "authentication" in error_msg.lower() or "api key" in error_msg.lower() or "auth" in error_msg.lower():
                    st.error(f"❌ Erreur d'authentification : Votre clé API {llm_provider} semble invalide.")
                else:
                    st.error(f"Une erreur est survenue lors de l'exécution : {e}")
