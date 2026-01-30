import wx
import os
import sys

# On s'assure que Python trouve bien les dossiers 'core' et 'gui'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_frame import MainFrame

if __name__ == '__main__':
    # Création de l'application
    app = wx.App()
    
    # Lancement de la fenêtre principale
    frame = MainFrame()
    frame.Show()
    
    # Boucle infinie qui garde la fenêtre ouverte
    app.MainLoop()