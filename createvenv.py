import os
import subprocess
import sys

def create_virtualenv():
    venv_name = "venv"

    # Crear el entorno virtual
    print(f"Creando el entorno virtual '{venv_name}'...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_name])

    # Instalar dependencias desde requirements.txt
    pip_path = os.path.join(venv_name, "Scripts", "pip") if os.name == "nt" else os.path.join(venv_name, "bin", "pip")
    print("Instalando dependencias desde requirements.txt...")
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])

    print("¡Entorno virtual configurado con éxito!")

if __name__ == "__main__":
    create_virtualenv()
