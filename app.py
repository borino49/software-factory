import os
import io
import zipfile
import re
import streamlit as st
from crewai import Agent, Crew, Process, Task

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Software Factory - Multi-Agent (Ultimate)",
    page_icon="🤖",
    layout="wide"
)

st.title("🚀 Software Factory Multi-Agent (v5 - Ultimate & ZIP Export)")
st.markdown("Passez à la vitesse supérieure : vos agents conçoivent, structurent et empaquettent votre application dans une archive ZIP prête à l'emploi.")

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

        with st.spinner(f"🔄 Les agents collaborent et structurent votre code via {llm_provider} ({selected_model})..."):
            try:
                # Définition des Agents avec instructions strictes pour le découpage en fichiers
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
                    goal="Rédiger le code complet, modulaire et structuré en fichiers distincts.",
                    backstory="Tu produis l'intégralité du code source. Pour chaque fichier, tu dois indiquer son nom exact sous le format `### nom_du_fichier.ext` juste au-dessus du bloc de code.",
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
                    description="Écrire tout le code source nécessaire. IMPORTANT: Sépare chaque fichier en utilisant un titre de niveau 3 avec le nom du fichier (ex: `### app.py`) suivi du bloc de code markdown.",
                    expected_output="Le code source complet réparti en fichiers clairs et nommés.",
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
                st.success(f"✅ Application conçue et structurée avec succès via {llm_provider} !")
                st.markdown("### 📋 Rapport & Code de la Brigade :")
                st.markdown(resultat_str)

                # --- MOTEUR D'EXTRACTION DE FICHIERS ET GÉNÉRATION DE ZIP ---
                zip_buffer = io.BytesIO()
                file_count = 0

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    # 1. On sauvegarde d'office le rapport global complet
                    zip_file.writestr("rapport_software_factory.md", resultat_str)

                    # 2. Expression régulière pour détecter les fichiers nommés (ex: ### main.py ou ### `app.py`)
                    pattern = r"###\s+(?:`)?([a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+)(?:`)?\s*\n+```[a-zA-Z]*\n(.*?)```"
                    matches = re.findall(pattern, resultat_str, re.DOTALL)

                    if matches:
                        for filename, code_content in matches:
                            zip_file.writestr(filename.strip(), code_content.strip())
                            file_count += 1
                    else:
                        # Fallback de secours si aucun nom n'est détecté : extraction des blocs de code génériques
                        generic_pattern = r"```[a-zA-Z]*\n(.*?)```"
                        generic_matches = re.findall(generic_pattern, resultat_str, re.DOTALL)
                        if generic_matches:
                            zip_file.writestr("main.py", generic_matches[-1].strip())
                            file_count += 1

                zip_buffer.seek(0)

                # --- BOUTONS DE TÉLÉCHARGEMENT AVANCÉS ---
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Télécharger le rapport complet (.md)",
                        data=resultat_str,
                        file_name=f"software_factory_{llm_provider.lower()}.md",
                        mime="text/markdown"
                    )
                
                with col2:
                    if file_count > 0:
                        st.download_button(
                            label=f"📦 Télécharger l'archive ZIP du projet ({file_count} fichiers)",
                            data=zip_buffer,
                            file_name="software_project_export.zip",
                            mime="application/zip"
                        )
                    else:
                        st.info("💡 Le rapport est disponible, aucun fichier de code isolé n'a été détecté pour le ZIP.")

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    st.error(f"❌ Erreur de quota : Votre compte {llm_provider} est épuisé.")
                elif "authentication" in error_msg.lower() or "api key" in error_msg.lower() or "auth" in error_msg.lower():
                    st.error(f"❌ Erreur d'authentification : Votre clé API {llm_provider} semble invalide.")
                else:
                    st.error(f"Une erreur est survenue lors de l'exécution : {e}")
