import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import zipfile
import time
from threading import Thread
from io import BytesIO
from ttkbootstrap import Style
from PIL import Image, ImageTk

# 📌 Liens des fichiers
CSS_PACK_URL = "https://tkx.fr/css-content-leroleplay.zip"
LOGO_URL = "https://le-roleplay.fr/img/logo.png"

# 📌 Recherche automatique du dossier addons de Garry's Mod
def find_gmod_path():
    possible_paths = [
        "C:\\Program Files (x86)\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\addons",
        "C:\\Program Files\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\addons",
        os.path.expanduser("~") + "\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\addons",
        "D:\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\addons",
        "E:\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\addons"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return ""

# 📌 Fonction pour charger une image depuis un lien Web
def load_web_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si l'image est accessible
        image_data = BytesIO(response.content)  # Convertir en image exploitable
        return Image.open(image_data).resize((120, 120), Image.LANCZOS)
    except Exception as e:
        print(f"⚠ Erreur lors du chargement du logo : {e}")
        return None

# 📌 Création de la fenêtre principale
root = tk.Tk()
root.title("Le Roleplay - CS:S Installer")
root.geometry("600x450")  # Fenêtre plus large
root.resizable(False, False)
style = Style("darkly")  # Thème sombre
root.configure(bg="#212121")

# 📌 Charger le logo depuis le Web
logo_image = load_web_image(LOGO_URL)
if logo_image:
    logo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo, bg="#212121")
    logo_label.pack(pady=10)
else:
    tk.Label(root, text="⚠ Logo non chargé", fg="red", bg="#212121").pack(pady=10)

# 📌 Titre principal
title_label = tk.Label(root, text="Le Roleplay - CS:S Installer", font=("Arial", 16, "bold"), fg="white", bg="#212121")
title_label.pack(pady=5)

# 📌 Variable pour stocker le chemin
install_path = tk.StringVar()
install_path.set(find_gmod_path())

# ✅ Sélection manuelle du dossier (si détecté incorrectement)
def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        install_path.set(folder_selected)

# ✅ Fonction pour télécharger et installer le pack CS:S
def download_and_install():
    if not install_path.get():
        messagebox.showerror("Erreur", "Impossible de trouver le dossier GMod. Sélectionnez-le manuellement.")
        return
    
    download_button.config(state=tk.DISABLED)
    progress_label.config(text="Téléchargement en cours...")
    speed_label.config(text="")
    time_label.config(text="")
    eta_label.config(text="")

    def download():
        try:
            file_path = os.path.join(install_path.get(), "css_pack.zip")
            
            # 📥 Téléchargement du fichier
            response = requests.get(CSS_PACK_URL, stream=True)
            if response.status_code != 200:
                messagebox.showerror("Erreur", "Le fichier n'a pas pu être téléchargé.")
                download_button.config(state=tk.NORMAL)
                return

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.time()

            with open(file_path, "wb") as file:
                for data in response.iter_content(1024):
                    file.write(data)
                    downloaded_size += len(data)
                    
                    # 🔄 Mise à jour de la barre de progression
                    progress_bar["value"] = (downloaded_size / total_size) * 100
                    
                    # 📊 Calcul de la vitesse et du temps restant
                    elapsed_time = time.time() - start_time
                    speed = (downloaded_size / elapsed_time) / (1024 * 1024)  # Vitesse en MB/s
                    remaining_time = (total_size - downloaded_size) / (speed * 1024 * 1024) if speed > 0 else 0
                    eta = time.strftime("%M min %S sec", time.gmtime(remaining_time))
                    
                    # 🔹 Mise à jour des labels
                    speed_label.config(text=f"Vitesse : {speed:.2f} MB/s")
                    time_label.config(text=f"Temps écoulé : {elapsed_time:.2f} sec")
                    eta_label.config(text=f"Temps restant estimé : {eta}")
                    
                    root.update_idletasks()

            progress_label.config(text="Extraction en cours...")

            # 📦 Extraction du pack dans "addons"
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(install_path.get())

            os.remove(file_path)  # Suppression du fichier ZIP après extraction
            
            progress_label.config(text="✅ Installation terminée !")
            messagebox.showinfo("Succès", "Le pack CS:S a été installé avec succès dans addons !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        finally:
            download_button.config(state=tk.NORMAL)

    # Lancer le téléchargement et l'installation dans un thread séparé
    Thread(target=download).start()

# 📌 Interface graphique stylisée
frame = tk.Frame(root, bg="#212121")
frame.pack(pady=5)

tk.Label(frame, text="Dossier d'installation de Garry's Mod :", fg="white", bg="#212121").pack(pady=5)
entry = tk.Entry(frame, textvariable=install_path, width=50, font=("Arial", 10), bg="#333", fg="white", bd=2)
entry.pack(pady=5)
browse_button = tk.Button(frame, text="📂 Parcourir", command=select_folder, font=("Arial", 10, "bold"), bg="#fbbf15", fg="black", relief="flat")
browse_button.pack(pady=5)

download_button = tk.Button(root, text="⚡ Installer le pack CS:S", command=download_and_install, font=("Arial", 12, "bold"), bg="#fbbf15", fg="black", relief="flat")
download_button.pack(pady=10)

progress_label = tk.Label(root, text="", fg="white", bg="#212121")
progress_label.pack()

# ✅ Barre de progression horizontale
progress_bar = ttk.Progressbar(root, length=500, mode="determinate", style="info.Horizontal.TProgressbar")
progress_bar.pack(pady=10)

# ✅ Ajout des infos sur la vitesse et le temps restant
speed_label = tk.Label(root, text="", fg="white", bg="#212121", font=("Arial", 10))
speed_label.pack()
time_label = tk.Label(root, text="", fg="white", bg="#212121", font=("Arial", 10))
time_label.pack()
eta_label = tk.Label(root, text="", fg="white", bg="#212121", font=("Arial", 10, "bold"))
eta_label.pack()

# 📌 Lancer l'application
root.mainloop()
