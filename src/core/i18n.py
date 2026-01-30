import locale

TRANSLATIONS = {
    # --- MENUS ---
    'menu_file': { 'fr': "Fichier", 'en': "File" },
    'menu_add': { 'fr': "Ajouter des fichiers...", 'en': "Add Files..." },
    'menu_clear': { 'fr': "Vider la liste", 'en': "Clear List" },
    'menu_quit': { 'fr': "Quitter", 'en': "Quit" },
    'menu_edit': { 'fr': "Édition", 'en': "Edit" },
    'menu_prefs': { 'fr': "Préférences...", 'en': "Preferences..." },
    'menu_help': { 'fr': "Aide", 'en': "Help" },
    'menu_about': { 'fr': "À propos", 'en': "About" },
    'ctx_open_folder': { 'fr': "Ouvrir le dossier de destination", 'en': "Open Destination Folder" },

    # --- LISTE DES FICHIERS ---
    'col_file': { 'fr': "Fichier", 'en': "File" },
    'col_status': { 'fr': "État", 'en': "Status" },
    'status_waiting': { 'fr': "En attente", 'en': "Waiting" },
    'status_processing': { 'fr': "En cours...", 'en': "Processing..." },
    'status_done': { 'fr': "Terminé", 'en': "Done" },
    'status_error': { 'fr': "Erreur", 'en': "Error" },

    # --- UI GÉNÉRAL ---
    'app_title': { 'fr': "Décodeur Audible V2", 'en': "Audible Decoder V2" },
    'tab_general': { 'fr': "Général et Sortie", 'en': "General & Output" },
    'tab_mp3': { 'fr': "Encodage MP3", 'en': "MP3 Encoding" },
    'btn_start': { 'fr': "Lancer la conversion", 'en': "Start Conversion" },
    'btn_stop': { 'fr': "Arrêter", 'en': "Stop" },
    'btn_ok': { 'fr': "OK", 'en': "OK" },
    'btn_cancel': { 'fr': "Annuler", 'en': "Cancel" },
    'btn_choose': { 'fr': "Choisir...", 'en': "Choose..." },

    # --- INFO & LOGS ---
    'lbl_format': { 'fr': "Format de sortie :", 'en': "Output Format:" },
    'status_sys': { 'fr': "Système : {}", 'en': "System: {}" },
    'sys_ready': { 'fr': "Prêt", 'en': "Ready" },
    'sys_missing': { 'fr': "Manquant : {}", 'en': "Missing: {}" },
    'batch_finished': { 'fr': "Traitement terminé !", 'en': "Batch finished!" },
    'batch_msg': { 'fr': "{} fichiers traités avec succès.", 'en': "{} files processed successfully." },

    # --- PRÉFÉRENCES ---
    'box_dest': { 'fr': "Dossier de destination", 'en': "Destination Folder" },
    'rad_same': { 'fr': "Même dossier que le fichier original", 'en': "Same folder as original file" },
    'rad_custom': { 'fr': "Dossier spécifique :", 'en': "Custom folder:" },
    'box_struct': { 'fr': "Organisation", 'en': "Organization" },
    'struct_none': { 'fr': "Aucun (En vrac)", 'en': "None (Flat)" },
    'struct_auth': { 'fr': "Dossier Auteur", 'en': "Author Folder" },
    'struct_auth_title': { 'fr': "Auteur / Titre", 'en': "Author / Title" },
    'box_name': { 'fr': "Nommage", 'en': "Naming" },
    'name_original': { 'fr': "Nom original", 'en': "Original Name" },
    'name_title': { 'fr': "Titre du livre", 'en': "Book Title" },

    # --- MP3 ---
    'box_split': { 'fr': "Découpage", 'en': "Splitting" },
    'chk_split': { 'fr': "Diviser par chapitres", 'en': "Split by chapters" },
    'chk_num': { 'fr': "Numéroter (01 - ...)", 'en': "Numbering (01 - ...)" },
    'box_qual': { 'fr': "Qualité", 'en': "Quality" },
    'qual_vbr': { 'fr': "VBR (Variable)", 'en': "VBR (Variable)" },
    'qual_cbr': { 'fr': "CBR (Constant)", 'en': "CBR (Constant)" },
    
    # --- CONFIRMATIONS ---
    'confirm_quit_title': { 'fr': "Conversion en cours", 'en': "Conversion running" },
    'confirm_quit_msg': { 'fr': "Voulez-vous arrêter le traitement et quitter ?", 'en': "Stop processing and quit?" },
    'flux_copy': { 'fr': "Copie", 'en': "Copy" },
    'chapters': { 'fr': "Chapitres", 'en': "Chapters" }
}

class LanguageManager:
    def __init__(self):
        try:
            sys_lang = locale.getdefaultlocale()[0]
            if sys_lang and sys_lang.lower().startswith('fr'):
                self.current_lang = 'fr'
            else:
                self.current_lang = 'en'
        except:
            self.current_lang = 'en'

    def get(self, key, *args):
        entry = TRANSLATIONS.get(key, {})
        text = entry.get(self.current_lang, key)
        if args:
            try: return text.format(*args)
            except: return text
        return text

LANG = LanguageManager()