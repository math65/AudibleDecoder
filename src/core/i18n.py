import locale

# Dictionnaire complet Français / Anglais
TRANSLATIONS = {
    # --- UI GÉNÉRAL ---
    'app_title': {
        'fr': "Décodeur Audible",
        'en': "Audible Decoder"
    },
    'tab_general': {
        'fr': "Général et Sortie",
        'en': "General & Output"
    },
    'tab_mp3': {
        'fr': "Encodage MP3",
        'en': "MP3 Encoding"
    },
    'btn_start': {
        'fr': "Démarrer",
        'en': "Start"
    },
    'btn_quit': {
        'fr': "Quitter",
        'en': "Quit"
    },
    'btn_browse': {
        'fr': "Parcourir...",
        'en': "Browse..."
    },
    'btn_choose': {
        'fr': "Choisir...",
        'en': "Choose..."
    },
    'btn_prefs': {
        'fr': "Préférences...",
        'en': "Settings..."
    },
    'btn_ok': {
        'fr': "OK",
        'en': "OK"
    },
    'btn_cancel': {
        'fr': "Annuler",
        'en': "Cancel"
    },

    # --- SECTION FICHIER ---
    'lbl_file': {
        'fr': "Livre Audio (.aax) :",
        'en': "Audiobook file (.aax):"
    },
    'box_info': {
        'fr': "Informations détectées",
        'en': "Detected Info"
    },
    'lbl_title': {
        'fr': "Titre :",
        'en': "Title:"
    },
    'lbl_author': {
        'fr': "Auteur :",
        'en': "Author:"
    },
    'detected': {
        'fr': "-> Détecté : {} par {}",
        'en': "-> Detected: {} by {}"
    },
    'reading_meta': {
        'fr': "Lecture des infos...",
        'en': "Reading metadata..."
    },

    # --- SECTION FORMAT & LOGS ---
    'lbl_format': {
        'fr': "Format de sortie :",
        'en': "Output Format:"
    },
    'status_sys': {
        'fr': "Système : {}",
        'en': "System: {}"
    },
    'sys_ready': {
        'fr': "Système complet et prêt.",
        'en': "System ready."
    },
    'sys_missing': {
        'fr': "Manquant : {}",
        'en': "Missing: {}"
    },

    # --- ONGLET GÉNÉRAL ---
    'box_dest': {
        'fr': "Dossier de destination",
        'en': "Destination Folder"
    },
    'rad_same': {
        'fr': "Même dossier que le fichier original",
        'en': "Same folder as original file"
    },
    'rad_custom': {
        'fr': "Dossier spécifique :",
        'en': "Custom folder:"
    },
    'box_struct': {
        'fr': "Organisation des dossiers",
        'en': "Folder Structure"
    },
    'struct_none': {
        'fr': "Aucun sous-dossier (En vrac)",
        'en': "No subfolder (Flat)"
    },
    'struct_auth': {
        'fr': "Créer dossier : Auteur",
        'en': "Create folder: Author"
    },
    'struct_auth_title': {
        'fr': "Créer dossier : Auteur / Titre (Recommandé)",
        'en': "Create folder: Author / Title (Recommended)"
    },
    'box_name': {
        'fr': "Nom du fichier final",
        'en': "Final Filename"
    },
    'name_original': {
        'fr': "Garder le nom du fichier original",
        'en': "Keep original filename"
    },
    'name_title': {
        'fr': "Utiliser le Titre du livre",
        'en': "Use Book Title"
    },

    # --- ONGLET MP3 ---
    'box_split': {
        'fr': "Découpage",
        'en': "Splitting"
    },
    'chk_split': {
        'fr': "Diviser le livre par chapitres",
        'en': "Split book by chapters"
    },
    'chk_num': {
        'fr': "Numéroter les fichiers (01 - Chapitre 1)",
        'en': "Number files (01 - Chapter 1)"
    },
    'box_qual': {
        'fr': "Qualité Audio",
        'en': "Audio Quality"
    },
    'qual_vbr': {
        'fr': "Débit Variable (VBR)",
        'en': "Variable Bitrate (VBR)"
    },
    'qual_cbr': {
        'fr': "Débit Constant (CBR)",
        'en': "Constant Bitrate (CBR)"
    },
    
    # --- MESSAGES / ERREURS ---
    'start_msg': {
        'fr': "--- Démarrage ---",
        'en': "--- Starting ---"
    },
    'success': {
        'fr': "SUCCÈS !",
        'en': "SUCCESS!"
    },
    'saved_in': {
        'fr': "Sauvegardé dans :\n{}",
        'en': "Saved in:\n{}"
    },
    'error': {
        'fr': "ERREUR : {}",
        'en': "ERROR: {}"
    },
    'confirm_quit_title': {
        'fr': "Conversion en cours",
        'en': "Conversion in progress"
    },
    'confirm_quit_msg': {
        'fr': "Une conversion est en cours.\nSi vous quittez, elle sera annulée.\nVoulez-vous vraiment quitter ?",
        'en': "Conversion is running.\nIf you quit now, it will be cancelled.\nAre you sure?"
    },
    'flux_copy': {
        'fr': "Flux copié",
        'en': "Stream copy"
    },
    'chapters': {
        'fr': "Chapitres",
        'en': "Chapters"
    }
}

class LanguageManager:
    def __init__(self):
        # Détection automatique de la langue système
        # Si ça commence par 'fr', on met 'fr', sinon 'en'
        try:
            sys_lang = locale.getdefaultlocale()[0]
            if sys_lang and sys_lang.lower().startswith('fr'):
                self.current_lang = 'fr'
            else:
                self.current_lang = 'en'
        except:
            self.current_lang = 'en'

    def get(self, key, *args):
        """Récupère le texte traduit. Si args est fourni, formate le texte."""
        # On cherche la clé, si on trouve pas, on renvoie la clé elle-même (sécurité)
        entry = TRANSLATIONS.get(key, {})
        text = entry.get(self.current_lang, key)
        
        # Si on a des arguments (ex: pour remplir les {}), on formate
        if args:
            try:
                return text.format(*args)
            except:
                return text
        return text

# Instance unique qu'on importera ailleurs
LANG = LanguageManager()