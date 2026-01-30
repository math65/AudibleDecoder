import os
import subprocess
import glob
import re
import json
import sys
from core.i18n import LANG

class AudibleDecoder:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        self.bin_path = os.path.join(base_path, 'bin')
        if sys.platform == "win32":
            self.ffmpeg = os.path.join(self.bin_path, 'ffmpeg.exe')
            self.ffprobe = os.path.join(self.bin_path, 'ffprobe.exe')
            self.rcrack = os.path.join(self.bin_path, 'rcrack.exe')
        else:
            self.ffmpeg = "ffmpeg"
            self.ffprobe = "ffprobe"
            self.rcrack = "rcrack"
            
        self.current_process = None

    def check_tools(self):
        missing = []
        if sys.platform == "win32":
            if not os.path.exists(self.ffmpeg): missing.append("ffmpeg.exe")
            if not os.path.exists(self.ffprobe): missing.append("ffprobe.exe")
            if not os.path.exists(self.rcrack): missing.append("rcrack.exe")
            rtc_files = glob.glob(os.path.join(self.bin_path, "*.rtc"))
            if not rtc_files: missing.append("Rainbow Tables (.rtc)")

        if missing: 
            return False, LANG.get('sys_missing', ', '.join(missing))
        return True, LANG.get('sys_ready')

    def _run_cmd(self, cmd, cwd=None):
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW
        return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=creation_flags)

    def get_metadata(self, aax_file):
        cmd = [self.ffprobe, '-v', 'quiet', '-print_format', 'json', '-show_format', aax_file]
        try:
            process = self._run_cmd(cmd)
            data = json.loads(process.stdout)
            tags = data.get('format', {}).get('tags', {})
            return {'title': tags.get('title', 'Unknown_Title'), 'artist': tags.get('artist', 'Unknown_Author')}
        except: return {'title': 'Audiobook', 'artist': 'Unknown'}

    def sanitize_filename(self, name):
        clean = re.sub(r'[\\/*?:"<>|]', "_", name)
        return clean.strip()

    def get_checksum(self, aax_file):
        cmd = [self.ffprobe, aax_file]
        process = self._run_cmd(cmd)
        match = re.search(r"file checksum == ([a-fA-F0-9]+)", process.stderr + process.stdout)
        if match: return match.group(1)
        raise Exception("Checksum not found")

    def get_activation_bytes(self, checksum):
        cmd = [self.rcrack, ".", "-h", checksum]
        process = self._run_cmd(cmd, cwd=self.bin_path)
        match = re.search(r"hex:([a-fA-F0-9]+)", process.stdout)
        if match: return match.group(1)
        raise Exception("Activation key not found")

    def get_chapters(self, aax_file):
        cmd = [self.ffprobe, '-v', 'quiet', '-print_format', 'json', '-show_chapters', aax_file]
        process = self._run_cmd(cmd)
        try: return json.loads(process.stdout).get('chapters', [])
        except: return []

    def _time_to_seconds(self, time_str):
        try:
            # On ignore le signe '-' éventuel pour la barre de progression
            time_str = time_str.replace('-', '')
            parts = time_str.split(':')
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
        except: return 0

    def cancel_operation(self):
        if self.current_process:
            try: self.current_process.kill()
            except: pass
            self.current_process = None

    def convert_book(self, aax_file, activation_bytes, output_path, output_format="mp3", 
                     split_chapters=False, chapter_num_prefix=False, 
                     bitrate_mode="vbr", bitrate_value="2", 
                     progress_callback=None):
        
        if output_format != "mp3": split_chapters = False
        
        tasks = []
        if not split_chapters:
            tasks.append((None, None, output_path))
        else:
            os.makedirs(output_path, exist_ok=True)
            chapters = self.get_chapters(aax_file)
            for i, chap in enumerate(chapters):
                chap_name = "Chapter" if LANG.current_lang == 'en' else "Chapitre"
                if chapter_num_prefix: filename = f"{i+1:02d} - {chap_name} {i+1}.{output_format}"
                else: filename = f"{chap_name}_{i+1:02d}.{output_format}"
                tasks.append((chap['start_time'], chap['end_time'], os.path.join(output_path, filename)))

        # Durée totale pour la barre
        cmd_dur = [self.ffprobe, aax_file]
        proc = self._run_cmd(cmd_dur)
        total_seconds = 0
        match = re.search(r"Duration: (\d{2}:\d{2}:\d{2}\.\d{2})", proc.stderr)
        if match: total_seconds = self._time_to_seconds(match.group(1))
        
        current_processed = 0
        errors_count = 0
        
        for start, end, out in tasks:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            
            cmd = [self.ffmpeg, '-y']
            if start and end: cmd.extend(['-ss', str(start), '-to', str(end)])
            
            cmd.extend(['-threads', '0', '-activation_bytes', activation_bytes, '-i', aax_file])
            
            # --- FORCE NO COVER ---
            # On retire explicitement toute vidéo pour éviter les bugs
            cmd.extend(['-vn']) 

            if output_format == "mp3":
                cmd.extend(['-c:a', 'libmp3lame'])
                if bitrate_mode == "cbr": cmd.extend(['-b:a', str(bitrate_value)])
                else: cmd.extend(['-q:a', str(bitrate_value)])
            else: 
                # M4A / M4B : Copie de flux simple
                cmd.extend(['-c', 'copy'])
            
            cmd.append(out)

            creation_flags = 0
            if sys.platform == "win32": creation_flags = subprocess.CREATE_NO_WINDOW
            
            try:
                self.current_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    encoding='utf-8',
                    errors='replace',
                    creationflags=creation_flags,
                    bufsize=1
                )
                
                while True:
                    if self.current_process is None: raise Exception("Cancelled")
                    
                    line = self.current_process.stderr.readline()
                    if not line:
                        if self.current_process.poll() is not None: break
                        continue
                    
                    # Regex souple qui accepte le signe moins (ex: time=-00:03:00)
                    if "time=" in line and total_seconds > 0 and progress_callback:
                        match = re.search(r"time=[-]?(\d+):(\d+):(\d+)", line)
                        if match:
                            h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
                            seg = h * 3600 + m * 60 + s
                            real = (current_processed + seg) if split_chapters else seg
                            pct = int((real / total_seconds) * 100)
                            if pct > 100: pct = 99
                            if pct < 0: pct = 0
                            progress_callback(pct)
                
                if self.current_process.returncode != 0: 
                    # On note l'erreur mais on continue les autres chapitres
                    errors_count += 1
            
            except Exception:
                errors_count += 1

            if split_chapters and start and end: current_processed += (float(end) - float(start))

        self.current_process = None
        
        # Si tout a échoué
        if errors_count == len(tasks):
             raise Exception("Conversion échouée")

        return output_path