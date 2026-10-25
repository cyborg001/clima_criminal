import uvicorn
import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("Iniciando Clima Criminal en http://127.0.0.1:8090 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8090, reload=True, reload_dirs=[base_dir])
