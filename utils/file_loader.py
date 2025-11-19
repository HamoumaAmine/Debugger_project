def read_file(file_path: str) -> str:
    """Lit un fichier et retourne son contenu en texte."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"
