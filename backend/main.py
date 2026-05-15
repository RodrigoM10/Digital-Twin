import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando Servidor del Gemelo Digital...")
    
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)