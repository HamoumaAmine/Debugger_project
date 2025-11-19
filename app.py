# app.py
import os
import json
import streamlit as st
from core.executor import run_script
from utils.file_loader import read_file
from core.ai_agent import get_correction_from_ia
from core.prompt_builder import build_prompt

from core.json_validator import validate_correction_json
from core.patcher import apply_corrections

st.set_page_config(page_title="Mini Débuggeur Universel", layout="wide")
st.title("Mini Débuggeur Universel")

st.header("Configuration")

project_path = st.text_input("Chemin du projet", value=os.getcwd())
venv_name = st.text_input("Nom du dossier venv", value=".venv")

scripts = []
if os.path.isdir(project_path):
    scripts = [f for f in os.listdir(project_path) if f.endswith(".py")]

script_choice = st.selectbox("Script à analyser :", ["-- Aucun --"] + scripts)

run_button = st.button("Exécuter & Analyser")
st.markdown("---")

# ---- Exécution et analyse ----
if run_button:
    if script_choice == "-- Aucun --":
        st.error("Aucun script sélectionné.")
    else:
        script_path = os.path.join(project_path, script_choice)
        st.session_state["script_path"] = script_path

        # Détection du python dans le venv
        if os.name == "nt":
            venv_python = os.path.join(project_path, venv_name, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(project_path, venv_name, "bin", "python")

        if not os.path.exists(script_path):
            st.error(f"Script introuvable : {script_path}")
        elif not os.path.exists(venv_python):
            st.error(f"Python introuvable dans l'environnement virtuel : {venv_python}")
        else:
            st.subheader("Exécution du script dans le venv")

            # ---- EXÉCUTION AVEC CAPTURE stdout/stderr ----
            stdout, stderr, returncode = run_script(script_path, venv_python)

            st.write(f"Code de retour : {returncode}")

            st.subheader("Sortie standard (stdout)")
            st.text_area("", stdout if stdout else "Aucune sortie.", height=150)

            st.subheader("Erreur standard (stderr)")
            st.text_area("", stderr if stderr else "Aucune erreur.", height=200)

            if returncode == 0 and not stderr:
                st.success("Exécution terminée sans erreurs (code 0).")

            # Lecture du code source
            code = read_file(script_path)

            # Prompt IA basé sur le code + erreurs
            prompt = build_prompt(code, stderr or "")

            st.subheader("Analyse IA")
            correction_json = get_correction_from_ia(prompt)

            st.session_state["corrections"] = correction_json

            if isinstance(correction_json, dict) and correction_json.get("error"):
                st.error(f"Erreur API : {correction_json.get('error')}")
            else:
                valid, errors = validate_correction_json(correction_json)
                if not valid:
                    st.error("Le JSON renvoyé par l'IA n'est pas conforme au schema.")
                    st.text_area("Détails validation JSON", json.dumps(errors, indent=2), height=120)
                    st.write("Réponse brute de l'IA :")
                    st.json(correction_json)
                else:
                    st.success("JSON de corrections valide.")
                    st.subheader("JSON de correction proposé par l'IA")
                    st.json(correction_json)

# ---- Bouton pour appliquer les corrections ----
if "corrections" in st.session_state and "script_path" in st.session_state:
    if st.button("Appliquer les corrections au fichier"):
        result = apply_corrections(st.session_state["script_path"], st.session_state["corrections"], backup=True)
        if result.get("ok"):
            st.success(result["msg"])
            updated_code = read_file(st.session_state["script_path"])
            st.subheader("Code après application")
            st.code(updated_code, language="python")
        else:
            st.error(result.get("msg"))
