import uvicorn
import os

if __name__ == "__main__":
    print("🚀 Iniciando Servidor del Gemelo Digital...")
    
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run("server:app", host="0.0.0.0", port=port)