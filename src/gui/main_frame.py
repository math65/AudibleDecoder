import wx
import os
import threading
import json
import winsound
from core.decoder import AudibleDecoder
from core.i18n import LANG

# --- GESTION DU GLISSER-DÉPOSER ---
class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        valid_files = [f for f in filenames if f.lower().endswith('.aax')]
        if valid_files:
            self.window.add_files_to_list(valid_files)
        return True

# --- DIALOGUE PRÉFÉRENCES ---
class SettingsDialog(wx.Dialog):
    def __init__(self, parent, current_settings):
        super().__init__(parent, title=LANG.get('menu_prefs'), size=(520, 500))
        self.settings = current_settings
        self.notebook = wx.Notebook(self)

        self.tab_general = wx.Panel(self.notebook)
        self.init_general_tab()
        self.notebook.AddPage(self.tab_general, LANG.get('tab_general'))

        self.tab_mp3 = wx.Panel(self.notebook)
        self.init_mp3_tab()
        self.notebook.AddPage(self.tab_mp3, LANG.get('tab_mp3'))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK, label=LANG.get('btn_ok'))
        btn_cancel = wx.Button(self, wx.ID_CANCEL, label=LANG.get('btn_cancel'))
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.SetSizer(main_sizer)
        self.Centre()

    def init_general_tab(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        box_dest = wx.StaticBoxSizer(wx.VERTICAL, self.tab_general, LANG.get('box_dest'))
        self.rad_dest_same = wx.RadioButton(self.tab_general, label=LANG.get('rad_same'), style=wx.RB_GROUP)
        self.rad_dest_custom = wx.RadioButton(self.tab_general, label=LANG.get('rad_custom'))
        self.dest_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_custom_path = wx.TextCtrl(self.tab_general, value=self.settings.get('custom_path', ''))
        self.btn_dest_browse = wx.Button(self.tab_general, label=LANG.get('btn_choose'))
        self.btn_dest_browse.Bind(wx.EVT_BUTTON, self.on_browse_dest)
        self.dest_sizer.Add(self.txt_custom_path, 1, wx.RIGHT, 5)
        self.dest_sizer.Add(self.btn_dest_browse, 0)
        self.rad_dest_same.Bind(wx.EVT_RADIOBUTTON, self.on_dest_change)
        self.rad_dest_custom.Bind(wx.EVT_RADIOBUTTON, self.on_dest_change)
        box_dest.Add(self.rad_dest_same, 0, wx.ALL, 10)
        box_dest.Add(self.rad_dest_custom, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        box_dest.Add(self.dest_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        if self.settings.get('output_mode') == 'custom': self.rad_dest_custom.SetValue(True)
        else: self.rad_dest_same.SetValue(True)
        sizer.Add(box_dest, 0, wx.EXPAND | wx.ALL, 10)

        box_struct = wx.StaticBoxSizer(wx.VERTICAL, self.tab_general, LANG.get('box_struct'))
        self.choice_struct = wx.Choice(self.tab_general, choices=[LANG.get('struct_none'), LANG.get('struct_auth'), LANG.get('struct_auth_title')])
        self.choice_struct.SetSelection(self.settings.get('struct_index', 2))
        box_struct.Add(self.choice_struct, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(box_struct, 0, wx.EXPAND | wx.ALL, 10)

        box_name = wx.StaticBoxSizer(wx.VERTICAL, self.tab_general, LANG.get('box_name'))
        self.choice_naming = wx.Choice(self.tab_general, choices=[LANG.get('name_original'), LANG.get('name_title')])
        self.choice_naming.SetSelection(self.settings.get('naming_index', 1))
        box_name.Add(self.choice_naming, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(box_name, 0, wx.EXPAND | wx.ALL, 10)
        self.tab_general.SetSizer(sizer)
        self.update_dest_ui()

    def init_mp3_tab(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        box_chap = wx.StaticBoxSizer(wx.VERTICAL, self.tab_mp3, LANG.get('box_split'))
        self.chk_split = wx.CheckBox(self.tab_mp3, label=LANG.get('chk_split'))
        self.chk_split.SetValue(self.settings.get('split', False))
        self.chk_split.Bind(wx.EVT_CHECKBOX, self.on_split_change)
        self.chk_chap_num = wx.CheckBox(self.tab_mp3, label=LANG.get('chk_num'))
        self.chk_chap_num.SetValue(self.settings.get('chapter_prefix', False))
        
        box_chap.Add(self.chk_split, 0, wx.ALL, 5)
        box_chap.Add(self.chk_chap_num, 0, wx.ALL, 5)
        sizer.Add(box_chap, 0, wx.EXPAND | wx.ALL, 10)
        
        box_qual = wx.StaticBoxSizer(wx.VERTICAL, self.tab_mp3, LANG.get('box_qual'))
        modes = [LANG.get('qual_vbr'), LANG.get('qual_cbr')]
        self.radio_mode = wx.RadioBox(self.tab_mp3, label="Mode", choices=modes)
        if self.settings.get('mp3_mode') == 'cbr': self.radio_mode.SetSelection(1)
        else: self.radio_mode.SetSelection(0)
        self.radio_mode.Bind(wx.EVT_RADIOBOX, self.on_mp3_mode_change)
        box_qual.Add(self.radio_mode, 0, wx.EXPAND | wx.ALL, 10)
        self.choice_quality = wx.Choice(self.tab_mp3)
        box_qual.Add(self.choice_quality, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(box_qual, 0, wx.EXPAND | wx.ALL, 10)
        self.update_quality_list()
        self.update_chap_ui()
        self.tab_mp3.SetSizer(sizer)

    def on_dest_change(self, event): self.update_dest_ui()
    def update_dest_ui(self):
        is_custom = self.rad_dest_custom.GetValue()
        self.txt_custom_path.Show(is_custom)
        self.btn_dest_browse.Show(is_custom)
        self.tab_general.Layout()
    def on_split_change(self, event): self.update_chap_ui()
    def update_chap_ui(self):
        is_split = self.chk_split.GetValue()
        self.chk_chap_num.Enable(is_split)
    def on_browse_dest(self, event):
        dlg = wx.DirDialog(self, LANG.get('box_dest'))
        if dlg.ShowModal() == wx.ID_OK: self.txt_custom_path.SetValue(dlg.GetPath())
        dlg.Destroy()
    def on_mp3_mode_change(self, event): self.update_quality_list()
    def update_quality_list(self):
        self.choice_quality.Clear()
        is_cbr = (self.radio_mode.GetSelection() == 1)
        if is_cbr: self.current_data = [("320 kbps", "320k"), ("192 kbps", "192k"), ("128 kbps", "128k"), ("64 kbps", "64k")]
        else: self.current_data = [("V0", "0"), ("V2", "2"), ("V4", "4"), ("V6", "6")]
        for lbl, val in self.current_data: self.choice_quality.Append(lbl)
        saved = self.settings.get('mp3_value', '2')
        found = False
        for i, (l, v) in enumerate(self.current_data):
            if v == saved:
                self.choice_quality.SetSelection(i)
                found = True
        if not found: self.choice_quality.SetSelection(1)
    def get_settings(self):
        is_cbr = (self.radio_mode.GetSelection() == 1)
        q_idx = self.choice_quality.GetSelection()
        if q_idx == wx.NOT_FOUND: q_idx = 1
        return {
            'output_mode': 'custom' if self.rad_dest_custom.GetValue() else 'same',
            'custom_path': self.txt_custom_path.GetValue(),
            'struct_index': self.choice_struct.GetSelection(),
            'naming_index': self.choice_naming.GetSelection(),
            'split': self.chk_split.GetValue(),
            'chapter_prefix': self.chk_chap_num.GetValue(),
            'mp3_mode': 'cbr' if is_cbr else 'vbr',
            'mp3_value': self.current_data[q_idx][1]
        }

# --- FENÊTRE PRINCIPALE ---
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=LANG.get('app_title'), size=(800, 600))
        self.config_file = os.path.join(os.getcwd(), "settings.json")
        self.decoder = AudibleDecoder()
        self.app_settings = self.load_settings()
        
        self.file_list = []
        self.processed_paths = {} 
        self.is_converting = False
        self.stop_requested = False

        self.create_menu_bar()

        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, LANG.get('col_file'), width=450)
        self.list_ctrl.InsertColumn(1, LANG.get('col_status'), width=150)
        
        self.drop_target = FileDropTarget(self)
        self.list_ctrl.SetDropTarget(self.drop_target)
        
        # --- MODIF CLAVIER : On utilise EVT_CONTEXT_MENU au lieu de EVT_LIST_ITEM_RIGHT_CLICK
        # Cela capture le clic droit ET la touche Application du clavier
        self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)

        self.main_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        opt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        opt_sizer.Add(wx.StaticText(self.panel, label=LANG.get('lbl_format')), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.choice_fmt = wx.Choice(self.panel, choices=[])
        self.choice_fmt.Bind(wx.EVT_CHOICE, self.on_format_change)
        self.update_format_choices()
        self.choice_fmt.SetSelection(self.app_settings.get('format_index', 0))
        
        opt_sizer.Add(self.choice_fmt, 0, wx.RIGHT, 20)
        self.main_sizer.Add(opt_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.gauge = wx.Gauge(self.panel, range=100)
        self.main_sizer.Add(self.gauge, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        self.txt_log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(-1, 100))
        self.main_sizer.Add(self.txt_log, 0, wx.EXPAND | wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_start = wx.Button(self.panel, label=LANG.get('btn_start'))
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start_batch)
        self.btn_start.Disable() 
        
        self.btn_stop = wx.Button(self.panel, label=LANG.get('btn_stop'))
        self.btn_stop.Bind(wx.EVT_BUTTON, self.on_stop_batch)
        self.btn_stop.Disable()

        btn_sizer.Add(self.btn_start, 0, wx.RIGHT, 10)
        btn_sizer.Add(self.btn_stop, 0)
        self.main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.panel.SetSizer(self.main_sizer)
        self.Centre()
        
        tools_ok, tools_msg = self.decoder.check_tools()
        self.log(LANG.get('status_sys', tools_msg))
        if not tools_ok:
            self.Enable(False)
            wx.MessageBox(tools_msg, "Erreur", wx.ICON_ERROR)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def create_menu_bar(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        item_add = file_menu.Append(wx.ID_ANY, LANG.get('menu_add') + "\tCtrl+O")
        item_clear = file_menu.Append(wx.ID_ANY, LANG.get('menu_clear'))
        file_menu.AppendSeparator()
        item_quit = file_menu.Append(wx.ID_EXIT, LANG.get('menu_quit') + "\tAlt+F4")
        self.Bind(wx.EVT_MENU, self.on_add_files_menu, item_add)
        self.Bind(wx.EVT_MENU, self.on_clear_list, item_clear)
        self.Bind(wx.EVT_MENU, self.on_quit, item_quit)
        menubar.Append(file_menu, LANG.get('menu_file'))

        edit_menu = wx.Menu()
        item_prefs = edit_menu.Append(wx.ID_PREFERENCES, LANG.get('menu_prefs'))
        self.Bind(wx.EVT_MENU, self.on_prefs, item_prefs)
        menubar.Append(edit_menu, LANG.get('menu_edit'))

        help_menu = wx.Menu()
        item_about = help_menu.Append(wx.ID_ABOUT, LANG.get('menu_about'))
        self.Bind(wx.EVT_MENU, self.on_about, item_about)
        menubar.Append(help_menu, LANG.get('menu_help'))
        self.SetMenuBar(menubar)

    # --- MODIF CLAVIER : Gestionnaire unifié Clavier + Souris ---
    def on_context_menu(self, event):
        # On utilise GetFirstSelected qui marche même sans la souris
        idx = self.list_ctrl.GetFirstSelected()
        
        if idx != -1:
            # On crée le menu
            menu = wx.Menu()
            item_open = menu.Append(wx.ID_ANY, LANG.get('ctx_open_folder'))
            self.Bind(wx.EVT_MENU, self.on_open_folder, item_open)
            
            # PopupMenu s'ouvre à la position de la souris OU du curseur texte si clavier
            self.PopupMenu(menu)
            menu.Destroy()
    # -----------------------------------------------------------

    def on_open_folder(self, event):
        idx = self.list_ctrl.GetFirstSelected()
        if idx != -1 and idx in self.processed_paths:
            path = self.processed_paths[idx]
            if os.path.exists(path):
                os.startfile(path)
            else:
                wx.MessageBox("Le dossier n'existe pas encore (ou a été déplacé).", "Erreur")
        else:
            wx.MessageBox("Convertissez d'abord ce fichier pour voir le dossier.", "Info")

    def add_files_to_list(self, files):
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), os.path.basename(f))
                self.list_ctrl.SetItem(index, 1, LANG.get('status_waiting'))
        
        if self.file_list:
            self.btn_start.Enable(True)

    def on_add_files_menu(self, event):
        with wx.FileDialog(self, LANG.get('menu_add'), wildcard="AAX|*.aax", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                self.add_files_to_list(dlg.GetPaths())

    def on_clear_list(self, event):
        if not self.is_converting:
            self.list_ctrl.DeleteAllItems()
            self.file_list = []
            self.processed_paths = {}
            self.btn_start.Disable()

    def on_start_batch(self, event):
        self.save_settings()
        self.is_converting = True
        self.stop_requested = False
        self.btn_start.Disable()
        self.btn_stop.Enable(True)
        
        mb = self.GetMenuBar()
        for i in range(mb.GetMenuCount()):
            mb.EnableTop(i, False)
        
        threading.Thread(target=self.run_batch_process).start()

    def on_stop_batch(self, event):
        self.stop_requested = True
        self.decoder.cancel_operation()
        self.log("Arrêt demandé...")

    def run_batch_process(self):
        success_count = 0
        
        for i, aax_file in enumerate(self.file_list):
            if self.stop_requested: break
            
            wx.CallAfter(self.list_ctrl.SetItem, i, 1, LANG.get('status_processing'))
            self.log(f"Traitement de : {os.path.basename(aax_file)}")

            try:
                meta = self.decoder.get_metadata(aax_file)
                fmt_idx = self.choice_fmt.GetSelection()
                fmt = "mp3" if fmt_idx == 0 else ("m4b" if fmt_idx == 1 else "m4a")
                
                if self.app_settings['output_mode'] == 'custom' and self.app_settings['custom_path']:
                    base_dir = self.app_settings['custom_path']
                else: base_dir = os.path.dirname(aax_file)

                struct_idx = self.app_settings['struct_index']
                auth = self.decoder.sanitize_filename(meta.get('artist', 'Unknown'))
                tit = self.decoder.sanitize_filename(meta.get('title', 'Unknown'))
                
                final_folder = base_dir
                if struct_idx == 1: final_folder = os.path.join(base_dir, auth)
                elif struct_idx == 2: final_folder = os.path.join(base_dir, auth, tit)
                
                naming_idx = self.app_settings['naming_index']
                if naming_idx == 1: final_name = tit + f".{fmt}"
                else: final_name = os.path.splitext(os.path.basename(aax_file))[0] + f".{fmt}"
                    
                do_split = (fmt == "mp3" and self.app_settings['split'])
                chap_prefix = self.app_settings.get('chapter_prefix', False)
                
                if do_split:
                    if struct_idx == 2:
                        target_path = final_folder
                    else:
                        folder_name_chap = os.path.splitext(final_name)[0]
                        target_path = os.path.join(final_folder, folder_name_chap)
                else:
                    target_path = os.path.join(final_folder, final_name)

                if do_split: self.processed_paths[i] = target_path
                else: self.processed_paths[i] = os.path.dirname(target_path)

                checksum = self.decoder.get_checksum(aax_file)
                key = self.decoder.get_activation_bytes(checksum)
                
                self.decoder.convert_book(
                    aax_file, key, target_path, 
                    output_format=fmt,
                    split_chapters=do_split,
                    chapter_num_prefix=chap_prefix,
                    bitrate_mode=self.app_settings['mp3_mode'],
                    bitrate_value=self.app_settings['mp3_value'],
                    progress_callback=self.update_progress
                )
                
                wx.CallAfter(self.list_ctrl.SetItem, i, 1, LANG.get('status_done'))
                success_count += 1
                
                try: winsound.MessageBeep(winsound.MB_OK)
                except: pass
                
            except Exception as e:
                wx.CallAfter(self.list_ctrl.SetItem, i, 1, LANG.get('status_error'))
                self.log(f"Erreur sur {os.path.basename(aax_file)} : {e}")
                if self.stop_requested: break
        
        self.is_converting = False
        try: winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except: pass
        
        wx.CallAfter(self.finish_batch_ui, success_count)

    def finish_batch_ui(self, count):
        self.btn_start.Enable(True)
        self.btn_stop.Disable()
        
        mb = self.GetMenuBar()
        for i in range(mb.GetMenuCount()):
            mb.EnableTop(i, True)
            
        self.gauge.SetValue(0)
        self.log("---")
        msg = LANG.get('batch_finished') + "\n" + LANG.get('batch_msg', count)
        wx.MessageBox(msg, "Info", wx.OK | wx.ICON_INFORMATION)

    def update_progress(self, pct):
        if not self.stop_requested:
            wx.CallAfter(self.gauge.SetValue, pct)

    def log(self, msg): 
        wx.CallAfter(self.txt_log.AppendText, msg + "\n")

    def on_format_change(self, event):
        self.save_settings()
        self.update_format_choices()

    def update_format_choices(self):
        curr = self.choice_fmt.GetSelection()
        mode = self.app_settings.get('mp3_mode', 'vbr').upper()
        val = self.app_settings.get('mp3_value', '2')
        split = f" ({LANG.get('chapters')})" if self.app_settings.get('split') else ""
        mp3_lbl = f"MP3 ({mode} {val}{split})"
        choices = [mp3_lbl, f"M4B ({LANG.get('flux_copy')})", f"M4A ({LANG.get('flux_copy')})"]
        self.choice_fmt.Clear()
        for c in choices: self.choice_fmt.Append(c)
        if curr != wx.NOT_FOUND: self.choice_fmt.SetSelection(curr)
        else: self.choice_fmt.SetSelection(0)

    def load_settings(self):
        default = { 
            'format_index': 0, 'output_mode': 'same', 'custom_path': '', 
            'struct_index': 2, 'naming_index': 1, 
            'split': False, 'chapter_prefix': False, 
            'mp3_mode': 'vbr', 'mp3_value': '2' 
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f: default.update(json.load(f))
            except: pass
        return default

    def save_settings(self):
        self.app_settings['format_index'] = self.choice_fmt.GetSelection()
        try:
            with open(self.config_file, 'w') as f: json.dump(self.app_settings, f)
        except: pass

    def on_prefs(self, event):
        dlg = SettingsDialog(self, self.app_settings)
        if dlg.ShowModal() == wx.ID_OK:
            new_s = dlg.get_settings()
            new_s['format_index'] = self.app_settings.get('format_index', 0)
            self.app_settings = new_s
            self.save_settings()
            self.update_format_choices()
        dlg.Destroy()

    def on_about(self, event):
        wx.MessageBox("Décodeur Audible V2\n© 2024", LANG.get('menu_about'))

    def on_quit(self, event): self.Close()

    def on_close(self, event):
        if self.is_converting:
            dlg = wx.MessageDialog(self, LANG.get('confirm_quit_msg'), LANG.get('confirm_quit_title'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if dlg.ShowModal() != wx.ID_YES:
                event.Veto()
                return
            self.stop_requested = True
            self.decoder.cancel_operation()
            
        self.save_settings()
        event.Skip()