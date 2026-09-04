import sys
import os
import subprocess
import webbrowser
import urllib.request
import tkinter as tk
from tkinter import messagebox

# Redireciona saídas de terminal ocultas no modo executável (--windowed)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# --- MODO SERVIDOR STREAMLIT (EXECUTADO EM SEGUNDO PLANO DENTRO DO .EXE) ---
if len(sys.argv) > 1 and sys.argv[1] == "run_streamlit":
    import streamlit.web.cli as stcli
    
    # Busca o app.py dentro da pasta temporária do PyInstaller
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        caminho_app = os.path.join(base_dir, "app.py")
    else:
        caminho_app = os.path.join(os.path.dirname(__file__), "app.py")
        
    sys.argv = [
        "streamlit", "run", caminho_app,
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.headless=true",
        "--global.developmentMode=false"
    ]
    sys.exit(stcli.main())

# --- MODO INTERFACE TKINTER ---
processo_streamlit = None
tentativas = 0

def verificar_servidor():
    global tentativas
    try:
        # Tenta bater na porta do servidor
        urllib.request.urlopen("http://localhost:8501", timeout=1)
        
        # Se responder, o servidor está pronto!
        lbl_status.config(text="Status: RODANDO ONLINE", fg="green")
        btn_ligar.config(state=tk.DISABLED)
        btn_desligar.config(state=tk.NORMAL)
        webbrowser.open("http://localhost:8501")
        
    except Exception:
        tentativas += 1
        if tentativas < 20: # Tenta por até 10 segundos
            # Pede para o Tkinter tentar de novo daqui a meio segundo (sem travar a tela)
            root.after(500, verificar_servidor)
        else:
            lbl_status.config(text="Status: ERRO AO INICIAR", fg="red")
            messagebox.showerror("Erro", "O servidor demorou muito para responder.\nTente desligar e ligar novamente.")
            desligar_servidor()

def ligar_servidor():
    global processo_streamlit, tentativas
    if processo_streamlit is None:
        try:
            if getattr(sys, 'frozen', False):
                cmd = [sys.executable, "run_streamlit"]
            else:
                caminho_app = os.path.join(os.path.dirname(__file__), "app.py")
                cmd = [
                    sys.executable, "-m", "streamlit", "run", caminho_app,
                    "--server.enableCORS=false",
                    "--server.enableXsrfProtection=false",
                    "--server.headless=true"
                ]
            
            # Oculta janelas extras do terminal no Windows
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            processo_streamlit = subprocess.Popen(
                cmd, 
                creationflags=creation_flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            
            lbl_status.config(text="Status: CONECTANDO...", fg="orange")
            btn_ligar.config(state=tk.DISABLED)
            
            # Inicia o loop de verificação inteligente
            tentativas = 0
            root.after(1000, verificar_servidor)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível iniciar o servidor:\n{e}")
            btn_ligar.config(state=tk.NORMAL)

def desligar_servidor():
    global processo_streamlit
    if processo_streamlit is not None:
        processo_streamlit.terminate()
        processo_streamlit = None
    lbl_status.config(text="Status: DESLIGADO", fg="red")
    btn_ligar.config(state=tk.NORMAL)
    btn_desligar.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Painel Conciliador Pix")
root.geometry("350x200")
root.eval('tk::PlaceWindow . center')

tk.Label(root, text="Controle do Servidor Pix", font=("Arial", 14, "bold")).pack(pady=15)

lbl_status = tk.Label(root, text="Status: DESLIGADO", font=("Arial", 12, "bold"), fg="red")
lbl_status.pack(pady=5)

btn_ligar = tk.Button(root, text="▶ LIGAR SISTEMA", font=("Arial", 12, "bold"), command=ligar_servidor)
btn_ligar.pack(pady=5, ipadx=10)

btn_desligar = tk.Button(root, text="⏹ DESLIGAR", font=("Arial", 12, "bold"), bg="red", fg="white", command=desligar_servidor, state=tk.DISABLED)
btn_desligar.pack(pady=5, ipadx=10)

def on_closing():
    desligar_servidor()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
