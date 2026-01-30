import sys
import os
import wx

# --- LIGNES MAGIQUES POUR RÉGLER L'ERREUR ---
# Cela dit à Python : "Regarde dans le dossier où je suis pour trouver les autres fichiers"
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
# --------------------------------------------

from gui.main_frame import MainFrame

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()