from core.executor import run_script

venv_python = ".venv\\Scripts\\python.exe"  # Windows
script_path = "script_test.py"

stdout, stderr, code = run_script(script_path, venv_python)

print("STDOUT:", stdout)
print("STDERR:", stderr)
print("Return code:", code)
