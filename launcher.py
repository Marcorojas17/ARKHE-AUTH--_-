import uvicorn
import webbrowser
import threading
import time
import sys

def open_browser():
    time.sleep(2)
    print("\n" + "="*50)
    print(" 🚀 ARKHE SENTINEL INICIADO")
    print(" 🌐 Abriendo la consola forense en el navegador...")
    print(" (Si no se abre, ve a: http://127.0.0.1:8000)")
    print("="*50 + "\n")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="info")
