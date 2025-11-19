# core/ai_agent.py
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_KEY = os.getenv("GROQ_KEY")

# Client Groq officiel, comme dans la documentation
client = Groq(api_key=GROQ_KEY)


# # ---------------------------------------------------------------------------
# # PROMPT BUILDER — conforme au cahier des charges
# # ---------------------------------------------------------------------------

# def build_prompt(code: str, error: str) -> str:
#     return f"""
# Tu es un assistant expert en correction de code Python.

# Analyse le code suivant et corrige **toutes les erreurs détectables**, y compris :
# - erreurs de syntaxe,
# - variables non définies,
# - appels de fonctions inexistantes,
# - autres erreurs Python.

# **IMPORTANT** :
# - Le code doit être **directement exécutable** après correction.
# - Si une variable n'est pas définie, initialise-la avec une valeur par défaut appropriée.
# - Si une fonction est manquante, définis-la avec un corps minimal fonctionnel.
# - Corrige toutes les erreurs dans un seul passage, même si elles concernent plusieurs lignes.
# - Pour chaque correction, indique exactement quelle(s) ligne(s) supprimer et quelles lignes ajouter.

# Code à analyser :
# {code}

# Sortie d'erreur ou stderr du script :
# {error}

# Réponds uniquement avec un JSON STRICT au format exact suivant :

# {{
#   "error_summary": "Résumé court expliquant la cause de toutes les erreurs",
#   "modifications": [
#     {{
#       "line": 1,
#       "remove": "ligne exacte à supprimer",
#       "add": "nouvelle ligne (ou plusieurs lignes via \\n)"
#     }}
#   ]
# }}

# Règles strictes :
# - Aucun texte hors JSON.
# - Si aucune correction : "modifications": [].
# - Les numéros de ligne commencent à 1.
# - remove = ligne EXACTE provenant du fichier ou "" si rien à supprimer.
# - Ajoute toutes les corrections nécessaires, même si elles concernent plusieurs lignes ou plusieurs erreurs.
# - Chaque erreur doit être traitée avec sa propre entrée "modifications".
# -le code proposé doit etre strictement executable, pas juste syntaxiquement correct.
# """

# ---------------------------------------------------------------------------
# EXTRACTION JSON depuis la réponse texte
# ---------------------------------------------------------------------------
def _extract_json_from_text(text: str):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception:
        raise ValueError("Impossible d'extraire un JSON valide depuis la réponse IA.")


# ---------------------------------------------------------------------------
# APPEL À L’API GROQ
# ---------------------------------------------------------------------------
def get_correction_from_ia(prompt: str) -> dict:
    if not GROQ_KEY:
        return {"error": "Variable d'environnement GROQ_KEY introuvable dans .env"}

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",    # modèle correct provenant de la doc Groq
            messages=[
                {"role": "system", "content": "Tu renvoies uniquement un JSON strict conforme au schema."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,                 # zéro température pour garantir JSON strict
            max_completion_tokens=2048
        )
    except Exception as e:
        return {"error": f"Erreur API Groq : {e}"}

    try:
        content = completion.choices[0].message.content
    except Exception:
        return {"error": f"Réponse invalide retournée par l'API : {completion}"}

    try:
        return _extract_json_from_text(content)
    except Exception as e:
        return {"error": f"Impossible d'extraire le JSON : {e}. Réponse brute : {content}"}
