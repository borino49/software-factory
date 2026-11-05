import os
import streamlit as st
from crewai import Agent, Crew, Process, Task

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Software Factory - Multi-Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🚀 Software Factory Multi-Agent")
st.markdown("Concevez vos applications et outils automatisés clés en main grâce à votre brigade d'agents spécialisés.")

# Barre latérale (Sidebar) pour la sécurité (Modèle BYOK)
st.sidebar.header("🔐 Configuration & Sécurité")
st.sidebar.markdown(
    "Entrez votre clé API OpenAI. Elle est utilisée uniquement pour votre session "
    "et garantit que chacun consomme ses propres ressources en toute sécurité."
)
user_api_key = st.sidebar.text_input("Clé API OpenAI (sk-...)", type="password")

# Zone de saisie principale
st.markdown("### 📝 Décrivez votre besoin ou l'outil à créer")
besoin_utilisateur = st.text_area(
    "Exemple : Crée moi un outil de gestion des factures avec calcul automatique des taxes et export CSV.",
    height=120
)

# Bouton de lancement
if st.button("Lancer la Brigade d'Agents", type="primary"):
    if not user_api_key:
        st.error("⚠️ Veuillez entrer votre clé API OpenAI dans la barre latérale pour continuer.")
    elif not besoin_utilisateur:
        st.warning("⚠️ Veuillez décrire l'outil que vous souhaitez concevoir.")
    else:
        # Configuration de la clé API pour CrewAI via les variables d'environnement
        os.environ["OPENAI_API_KEY"] = user_api_key
        os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"

        with st.spinner("🔄 Les agents collaborent (Cadrage -> Architecture -> Développement -> QA)..."):
            try:
                # Définition des Agents de la Software Factory
                orchestrateur = Agent(
                    role="Chef de Projet & Orchestrateur Technique",
                    goal="Analyser les besoins et coordonner l'équipe.",
                    backstory="Tu traduis les besoins en cahier des charges et supervises les échanges.",
                    verbose=False,
                    llm="gpt-4o"
                )

                architecte = Agent(
                    role="Architecte Logiciel Senior",
                    goal="Concevoir l'architecture globale et le schéma de données.",
                    backstory="Tu définis la structure technique, les flux et le modèle des données.",
                    verbose=False,
                    llm="gpt-4o"
                )

                developpeur = Agent(
                    role="Développeur Fullstack Expert",
                    goal="Rédiger le code complet et fonctionnel.",
                    backstory="Tu produis l'intégralité du code source propre, commenté et sans omission.",
                    verbose=False,
                    llm="gpt-4o"
                )

                testeur = Agent(
                    role="Ingénieur Sécurité & QA",
                    goal="Auditer le code et valider la sécurité.",
                    backstory="Tu vérifies l'absence de bugs, les failles de sécurité et la robustesse.",
                    verbose=False,
                    llm="gpt-4o"
                )

                # Définition des Tâches du Workflow
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

                # Affichage du résultat dans l'interface Streamlit
                st.success("✅ Application conçue avec succès par votre brigade d'agents !")
                st.markdown("### 📋 Rapport & Code de la Brigade :")
                st.markdown(str(resultat))

            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'exécution : {e}")
