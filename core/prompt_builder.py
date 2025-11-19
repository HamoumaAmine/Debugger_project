# core/prompt_builder.py
# ---------------------------------------------------------------------------
# PROMPT BUILDER — conforme au cahier des charges
# ---------------------------------------------------------------------------

def build_prompt(code: str, error: str) -> str:
    return f"""
Tu es un assistant expert en correction de code Python.

Analyse le code suivant et corrige **toutes les erreurs détectables**, y compris :
- erreurs de syntaxe,
- variables non définies,
- appels de fonctions inexistantes,
- autres erreurs Python.

**IMPORTANT** :
- Le code doit être **directement exécutable** après correction.
- Si une variable n'est pas définie, initialise-la avec une valeur par défaut appropriée.
- Si une fonction est manquante, définis-la avec un corps minimal fonctionnel.
- Corrige toutes les erreurs dans un seul passage, même si elles concernent plusieurs lignes.
- Pour chaque correction, indique exactement quelle(s) ligne(s) supprimer et quelles lignes ajouter.

Code à analyser :
{code}

Sortie d'erreur ou stderr du script :
{error}

Réponds uniquement avec un JSON STRICT au format exact suivant :

{{
  "error_summary": "Résumé court expliquant la cause de toutes les erreurs",
  "modifications": [
    {{
      "line": 1,
      "remove": "ligne exacte à supprimer",
      "add": "nouvelle ligne (ou plusieurs lignes via \\n)"
    }}
  ]
}}

Règles strictes :
- Aucun texte hors JSON.
- Si aucune correction : "modifications": [].
- Les numéros de ligne commencent à 1.
- remove = ligne EXACTE provenant du fichier ou "" si rien à supprimer.
- Ajoute toutes les corrections nécessaires, même si elles concernent plusieurs lignes ou plusieurs erreurs.
- Chaque erreur doit être traitée avec sa propre entrée "modifications".
-le code proposé doit etre strictement executable, pas juste syntaxiquement correct.
"""