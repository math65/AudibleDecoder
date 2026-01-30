import wx
import os
import threading
import json
from core.decoder import AudibleDecoder
from core.i18n import LANG # <--- L'import magique

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, current_settings):
        super().__init__(parent, title=LANG.get('btn_prefs'), size=(520, 500))
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
        self.choice_struct = wx.Choice(self.tab_general, choices=[
            LANG.get('struct_none'), 
            LANG.get('struct_auth'), 
            LANG.get('struct_auth_title')
        ])
        self.choice_struct.SetSelection(self.settings.get('struct_index', 2))
        box_struct.Add(self.choice_struct, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(box_struct, 0, wx.EXPAND | wx.ALL, 10)

        box_name = wx.StaticBoxSizer(wx.VERTICAL, self.tab_general, LANG.get('box_name'))
        self.choice_naming = wx.Choice(self.tab_general, choices=[
            LANG.get('name_original'), 
            LANG.get('name_title')
        ])
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

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=LANG.get('app_title'), size=(650, 650))
        self.config_file = os.path.join(os.getcwd(), "settings.json")
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.decoder = AudibleDecoder()
        tools_ok, tools_msg = self.decoder.check_tools()
        self.app_settings = self.load_settings()
        self.current_metadata = None
        self.is_closing = False     
        self.is_converting = False  

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.lbl_status = wx.TextCtrl(self.panel, value=LANG.get('status_sys', tools_msg), style=wx.TE_READONLY|wx.BORDER_NONE)
        self.lbl_status.SetForegroundColour(wx.BLUE if tools_ok else wx.RED)
        self.main_sizer.Add(self.lbl_status, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.ALL, 5)

        self.main_sizer.Add(wx.StaticText(self.panel, label=LANG.get('lbl_file')), 0, wx.LEFT, 15)
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_file = wx.TextCtrl(self.panel)
        file_sizer.Add(self.txt_file, 1, wx.EXPAND | wx.RIGHT, 10)
        self.btn_browse = wx.Button(self.panel, label=LANG.get('btn_browse'))
        self.btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
        file_sizer.Add(self.btn_browse, 0)
        self.main_sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 15)

        self.info_box = wx.StaticBoxSizer(wx.VERTICAL, self.panel, LANG.get('box_info'))
        self.lbl_title = wx.StaticText(self.panel, label=LANG.get('lbl_title') + " -")
        self.lbl_author = wx.StaticText(self.panel, label=LANG.get('lbl_author') + " -")
        font = self.lbl_title.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.lbl_title.SetFont(font)
        self.info_box.Add(self.lbl_title, 0, wx.ALL, 5)
        self.info_box.Add(self.lbl_author, 0, wx.ALL, 5)
        self.main_sizer.Add(self.info_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        self.main_sizer.Add(wx.StaticText(self.panel, label=LANG.get('lbl_format')), 0, wx.LEFT | wx.TOP, 15)
        opts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.choice_fmt = wx.Choice(self.panel, choices=[])
        self.choice_fmt.Bind(wx.EVT_CHOICE, self.on_format_change)
        self.update_format_choices()
        self.choice_fmt.SetSelection(self.app_settings.get('format_index', 0))
        opts_sizer.Add(self.choice_fmt, 1, wx.EXPAND | wx.RIGHT, 10)
        self.btn_prefs = wx.Button(self.panel, label=LANG.get('btn_prefs'))
        self.btn_prefs.Bind(wx.EVT_BUTTON, self.on_prefs)
        opts_sizer.Add(self.btn_prefs, 0)
        self.main_sizer.Add(opts_sizer, 0, wx.EXPAND | wx.ALL, 15)

        self.gauge = wx.Gauge(self.panel, range=100)
        self.main_sizer.Add(self.gauge, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        self.txt_log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.main_sizer.Add(self.txt_log, 1, wx.EXPAND | wx.ALL, 15)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_start = wx.Button(self.panel, label=LANG.get('btn_start'))
        self.btn_start.Enable(False)
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start)
        btn_sizer.Add(self.btn_start, 0, wx.RIGHT, 10)
        btn_quit = wx.Button(self.panel, label=LANG.get('btn_quit'))
        btn_quit.Bind(wx.EVT_BUTTON, self.on_quit)
        btn_sizer.Add(btn_quit, 0)
        self.main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)

        self.panel.SetSizer(self.main_sizer)
        self.Centre()
        if not tools_ok:
            self.btn_browse.Disable()
            self.choice_fmt.Disable()
            self.btn_prefs.Disable()

    def on_format_change(self, event):
        self.save_settings()
        self.update_format_choices()

    def on_quit(self, event): self.Close()

    def on_close(self, event):
        if self.is_converting:
            dlg = wx.MessageDialog(self, LANG.get('confirm_quit_msg'), LANG.get('confirm_quit_title'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result != wx.ID_YES:
                event.Veto()
                return

        self.is_closing = True
        self.decoder.cancel_operation() 
        self.save_settings()
        event.Skip() 

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

    def log(self, msg): 
        if not self.is_closing:
            wx.CallAfter(self.txt_log.AppendText, msg + "\n")

    def update_progress(self, pct):
        if not self.is_closing:
            wx.CallAfter(self.gauge.SetValue, pct)

    def on_browse(self, event):
        with wx.FileDialog(self, LANG.get('lbl_file'), wildcard="AAX|*.aax", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                path = dlg.GetPath()
                self.txt_file.SetValue(path)
                self.log(f"File: {os.path.basename(path)}")
                self.log(LANG.get('reading_meta'))
                def fetch_meta():
                    meta = self.decoder.get_metadata(path)
                    if not self.is_closing:
                        wx.CallAfter(self.update_meta_display, meta)
                threading.Thread(target=fetch_meta).start()

    def update_meta_display(self, meta):
        self.current_metadata = meta
        self.lbl_title.SetLabel(f"{LANG.get('lbl_title')} {meta['title']}")
        self.lbl_author.SetLabel(f"{LANG.get('lbl_author')} {meta['artist']}")
        self.log(LANG.get('detected', meta['title'], meta['artist']))
        self.btn_start.Enable(True)

    def on_prefs(self, event):
        dlg = SettingsDialog(self, self.app_settings)
        if dlg.ShowModal() == wx.ID_OK:
            new_s = dlg.get_settings()
            new_s['format_index'] = self.app_settings.get('format_index', 0)
            self.app_settings = new_s
            self.save_settings()
            self.update_format_choices()
        dlg.Destroy()

    def on_start(self, event):
        self.save_settings()
        self.btn_start.Disable()
        threading.Thread(target=self.run_process).start()

    def run_process(self):
        aax = self.txt_file.GetValue()
        fmt_idx = self.choice_fmt.GetSelection()
        fmt = "mp3" if fmt_idx == 0 else ("m4b" if fmt_idx == 1 else "m4a")
        self.is_converting = True
        
        try:
            self.log(LANG.get('start_msg'))
            if self.app_settings['output_mode'] == 'custom' and self.app_settings['custom_path']:
                base_dir = self.app_settings['custom_path']
            else: base_dir = os.path.dirname(aax)

            struct_idx = self.app_settings['struct_index']
            auth = self.decoder.sanitize_filename(self.current_metadata.get('artist', 'Unknown'))
            tit = self.decoder.sanitize_filename(self.current_metadata.get('title', 'Unknown'))
            
            final_folder = base_dir
            if struct_idx == 1: final_folder = os.path.join(base_dir, auth)
            elif struct_idx == 2: final_folder = os.path.join(base_dir, auth, tit)
            
            naming_idx = self.app_settings['naming_index']
            if naming_idx == 1: final_name = tit + f".{fmt}"
            else: final_name = os.path.splitext(os.path.basename(aax))[0] + f".{fmt}"
                
            do_split = (fmt == "mp3" and self.app_settings['split'])
            chap_prefix = self.app_settings.get('chapter_prefix', False)
            
            if do_split:
                folder_name_chap = os.path.splitext(final_name)[0]
                target_path = os.path.join(final_folder, folder_name_chap)
            else: target_path = os.path.join(final_folder, final_name)

            self.log(f"Dest: {target_path}")

            checksum = self.decoder.get_checksum(aax)
            key = self.decoder.get_activation_bytes(checksum)
            
            out = self.decoder.convert_book(
                aax, key, target_path, 
                output_format=fmt,
                split_chapters=do_split,
                chapter_num_prefix=chap_prefix,
                bitrate_mode=self.app_settings['mp3_mode'],
                bitrate_value=self.app_settings['mp3_value'],
                progress_callback=self.update_progress
            )
            
            self.update_progress(100)
            self.log(LANG.get('success'))
            if not self.is_closing:
                wx.CallAfter(wx.MessageBox, LANG.get('saved_in', out), LANG.get('success'), wx.OK|wx.ICON_INFORMATION)

        except Exception as e:
            if not self.is_closing:
                self.log(LANG.get('error', e))
                wx.CallAfter(wx.MessageBox, str(e), "Status", wx.OK|wx.ICON_ERROR)
        finally: 
            self.is_converting = False
            if not self.is_closing:
                wx.CallAfter(self.btn_start.Enable, True)