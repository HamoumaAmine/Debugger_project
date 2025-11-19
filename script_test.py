
# core/executor.py
a = 'Hello, world!'
print(a)
x = 0
z = 1
y = x + z
import subprocess
from typing import Tuple

def run_script(script_path: str, venv_python: str) -> Tuple[str, str, int]:
    """
    Exécute un script Python avec l'interpréteur venv_python.
    Retourne stdout, stderr, returncode.
    """
    try:
        proc = subprocess.Popen(
            [venv_python, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=60)
        return stdout, stderr, proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        return "", "Erreur : exécution timeout.", -1
    except Exception as e:
        return "", f"Erreur lors de l'exécution : {e}", -1

