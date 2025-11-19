import os
import shutil

def apply_corrections(file_path: str, corrections: dict, backup: bool = True) -> dict:
    if not os.path.exists(file_path):
        return {"ok": False, "msg": f"Fichier introuvable : {file_path}"}

    if backup:
        try:
            shutil.copy(file_path, file_path + ".bak")
        except Exception as e:
            return {"ok": False, "msg": f"Impossible de créer la sauvegarde : {e}"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        mods = corrections.get("modifications", [])
        mods_sorted = sorted(mods, key=lambda m: m["line"], reverse=True)

        for mod in mods_sorted:
            original_idx = mod["line"] - 1
            remove_text = mod.get("remove") or ""
            add_texts = mod.get("add", "").split("\n") if mod.get("add") else []
            remove_lines = remove_text.split("\n") if remove_text else []

            #====== NOUVEAU : fonction skip lignes vides + commentaires ======#
            def skip_non_code(idx):
                while 0 <= idx < len(lines) and (
                    lines[idx].strip() == "" or     # vide
                    lines[idx].strip().startswith("#")  # commentaire
                ):
                    idx += 1
                return idx
            #================================================================#

            # --- Suppression multi-lignes avec tolérance améliorée ---
            if remove_lines:
                found = False

                # on balaye autour de la ligne, mais en sautant les lignes non code
                for shift in range(-5, 6):
                    idx = original_idx + shift
                    idx = skip_non_code(idx)

                    if idx < 0 or idx + len(remove_lines) > len(lines):
                        continue

                    match = True
                    for i in range(len(remove_lines)):
                        if lines[idx + i].strip() != remove_lines[i].strip():
                            match = False
                            break

                    if match:
                        line_idx = idx
                        found = True
                        break

                if not found:
                    return {
                        "ok": False,
                        "msg": (
                            f"Suppression impossible à partir de la ligne {mod['line']}.\n"
                            f"Attendu : {remove_text!r}\n"
                            f"Lignes actuelles autour : {lines[original_idx:original_idx+5]!r}"
                        )
                    }

                # Suppression du bloc
                for _ in range(len(remove_lines)):
                    lines.pop(line_idx)

            # --- Ajout des lignes ---
            if add_texts:
                insert_idx = original_idx
                insert_idx = skip_non_code(insert_idx)
                for offset, newl in enumerate(add_texts):
                    lines.insert(insert_idx + offset, newl)

        # Écriture finale
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return {"ok": True, "msg": "Corrections appliquées avec succès (backup créé)."}

    except Exception as e:
        return {"ok": False, "msg": f"Erreur lors de l'application des corrections : {e}"}
