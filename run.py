import uvicorn
import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Iniciando Clima Criminal en http://127.0.0.1:8070 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8070, reload=True)
