#!/usr/bin/env python3
"""
Beautiful YouTube Video Downloader GUI for Linux
Requirements: pip install yt-dlp tkinter (tkinter usually comes with Python)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
from pathlib import Path
import re

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.format_var = tk.StringVar(value="mp4")
        self.is_downloading = False
        
        self.setup_ui()
        self.check_dependencies()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="YouTube Video Downloader", 
            font=('Arial', 24, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # URL Input Section
        url_frame = tk.Frame(main_frame, bg='#2c3e50')
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        url_label = tk.Label(
            url_frame,
            text="YouTube URL:",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        url_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.url_entry = tk.Entry(
            url_frame,
            textvariable=self.url_var,
            font=('Arial', 11),
            relief=tk.FLAT,
            bg='#34495e',
            fg='#ecf0f1',
            insertbackground='#ecf0f1'
        )
        self.url_entry.pack(fill=tk.X, ipady=8)
        
        # Options Frame
        options_frame = tk.Frame(main_frame, bg='#2c3e50')
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Download Path
        path_frame = tk.Frame(options_frame, bg='#2c3e50')
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        path_label = tk.Label(
            path_frame,
            text="Download Path:",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        path_label.pack(anchor=tk.W, pady=(0, 5))
        
        path_input_frame = tk.Frame(path_frame, bg='#2c3e50')
        path_input_frame.pack(fill=tk.X)
        
        self.path_entry = tk.Entry(
            path_input_frame,
            textvariable=self.download_path,
            font=('Arial', 11),
            relief=tk.FLAT,
            bg='#34495e',
            fg='#ecf0f1',
            insertbackground='#ecf0f1'
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        self.browse_btn = tk.Button(
            path_input_frame,
            text="Browse",
            command=self.browse_folder,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            font=('Arial', 10, 'bold'),
            padx=20,
            cursor='hand2'
        )
        self.browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Quality and Format Selection
        selection_frame = tk.Frame(options_frame, bg='#2c3e50')
        selection_frame.pack(fill=tk.X)
        
        # Quality Selection
        quality_frame = tk.Frame(selection_frame, bg='#2c3e50')
        quality_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        quality_label = tk.Label(
            quality_frame,
            text="Quality:",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        quality_label.pack(anchor=tk.W, pady=(0, 5))
        
        quality_options = ["best", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p", "240p", "144p", "worst"]
        self.quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality_var,
            values=quality_options,
            state="readonly",
            font=('Arial', 11)
        )
        self.quality_combo.pack(fill=tk.X, ipady=4)
        
        # Format Selection
        format_frame = tk.Frame(selection_frame, bg='#2c3e50')
        format_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        format_label = tk.Label(
            format_frame,
            text="Format:",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        format_label.pack(anchor=tk.W, pady=(0, 5))
        
        format_options = ["mp4", "mkv", "webm", "avi", "mp3", "m4a", "wav", "flac"]
        self.format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=format_options,
            state="readonly",
            font=('Arial', 11)
        )
        self.format_combo.pack(fill=tk.X, ipady=4)
        
        # Download Button
        self.download_btn = tk.Button(
            main_frame,
            text="Download Video",
            command=self.start_download,
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            font=('Arial', 14, 'bold'),
            pady=12,
            cursor='hand2'
        )
        self.download_btn.pack(fill=tk.X, pady=(20, 0))
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=(20, 0))
        
        # Status Label
        self.status_label = tk.Label(
            main_frame,
            text="Ready to download",
            font=('Arial', 11),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        self.status_label.pack(pady=(10, 0))
        
        # Log Area
        log_frame = tk.Frame(main_frame, bg='#2c3e50')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        log_label = tk.Label(
            log_frame,
            text="Download Log:",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=('Consolas', 10),
            bg='#1a252f',
            fg='#ecf0f1',
            relief=tk.FLAT,
            insertbackground='#ecf0f1'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar', background='#e74c3c')
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
            
    def check_dependencies(self):
        """Check if yt-dlp is installed"""
        try:
            subprocess.run(['yt-dlp', '--version'], 
                         capture_output=True, check=True)
            self.log("✓ yt-dlp is installed and ready")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠ yt-dlp not found. Installing...")
            self.install_ytdlp()
            
    def install_ytdlp(self):
        """Install yt-dlp using pip"""
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], 
                         check=True)
            self.log("✓ yt-dlp installed successfully")
        except subprocess.CalledProcessError:
            self.log("✗ Failed to install yt-dlp. Please install manually: pip install yt-dlp")
            messagebox.showerror("Dependency Error", 
                               "Could not install yt-dlp. Please install it manually:\npip install yt-dlp")
            
    def log(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def validate_url(self, url):
        """Basic YouTube URL validation"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
        
    def start_download(self):
        if self.is_downloading:
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if not self.validate_url(url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
            
        if not os.path.exists(self.download_path.get()):
            messagebox.showerror("Error", "Download path does not exist")
            return
        
        # Check available formats first
        self.log("Checking available formats...")
        self.check_available_formats(url)
            
        # Start download in separate thread
        self.is_downloading = True
        self.download_btn.config(text="Downloading...", state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Starting download...")
        
        download_thread = threading.Thread(target=self.download_video, args=(url,))
        download_thread.daemon = True
        download_thread.start()
    
    def check_available_formats(self, url):
        """Check and log available formats for the video"""
        try:
            cmd = ['yt-dlp', '--list-formats', url]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if process.returncode == 0:
                lines = process.stdout.split('\n')
                quality_found = False
                target_height = self.quality_var.get().replace('p', '').replace(' (4K)', '').replace(' (2K)', '').split()[0] if 'p' in self.quality_var.get() else None
                
                for line in lines:
                    if target_height and f"{target_height}p" in line:
                        quality_found = True
                        self.log(f"✓ Found {self.quality_var.get()}: {line.strip()}")
                        break
                
                if not quality_found and target_height:
                    self.log(f"⚠ Exact quality {self.quality_var.get()} not available, will use best alternative")
                
                # Also show what format string will be used
                format_string = self.get_format_string()
                self.log(f"Will use format string: {format_string}")
                
        except Exception as e:
            self.log(f"Could not check formats: {str(e)}")
        
    def download_video(self, url):
        try:
            self.log(f"Starting download: {url}")
            self.log(f"Selected quality: {self.quality_var.get()}")
            self.log(f"Selected format: {self.format_var.get()}")
            self.log(f"Format string: {self.get_format_string()}")
            
            # Prepare yt-dlp command
            output_template = os.path.join(
                self.download_path.get(), 
                '%(title)s.%(ext)s'
            )
            
            format_ext = self.format_var.get()
            
            cmd = [
                'yt-dlp',
                '--output', output_template,
                '--format', self.get_format_string(),
                '--no-playlist',
                '--embed-metadata',
                '--cookies-from-browser', 'firefox',
                '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                url
            ]
            
            # Add format-specific options
            if format_ext in ['mp3', 'm4a', 'wav', 'flac']:
                cmd.extend(['--extract-audio', '--audio-format', format_ext])
                if format_ext == 'mp3':
                    cmd.extend(['--audio-quality', '192K'])
                else:
                    cmd.extend(['--audio-quality', '0'])
            elif format_ext != 'mp4':
                cmd.extend(['--recode-video', format_ext])
            
            # Execute download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output line by line
            for line in process.stdout:
                if line.strip():
                    self.log(line.strip())
                    
            process.wait()
            
            if process.returncode == 0:
                self.log("✓ Download completed successfully!")
                self.root.after(0, lambda: self.status_label.config(
                    text="Download completed successfully!"
                ))
                messagebox.showinfo("Success", "Video downloaded successfully!")
            else:
                self.log("✗ Download failed!")
                self.root.after(0, lambda: self.status_label.config(
                    text="Download failed!"
                ))
                messagebox.showerror("Error", "Download failed. Check the log for details.")
                
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            self.root.after(0, lambda: self.status_label.config(
                text="Download failed!"
            ))
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        finally:
            # Reset UI
            self.is_downloading = False
            self.root.after(0, self.reset_download_button)
            
    def get_format_string(self):
        """Get format string for yt-dlp based on user selection"""
        quality = self.quality_var.get()
        format_ext = self.format_var.get()
        
        # For audio formats
        if format_ext in ['mp3', 'm4a', 'wav', 'flac']:
            return 'bestaudio/best'
        
        # For video formats - simplified and more reliable approach
        if quality == "best":
            # Use simpler format that's more likely to work
            return 'best[ext=mp4]/best[height<=2160]/best'
        elif quality == "worst":
            return 'worst/worstvideo+worstaudio'
        else:
            # Extract exact height from quality string
            height_map = {
                "2160p (4K)": "2160",
                "1440p (2K)": "1440", 
                "1080p": "1080",
                "720p": "720",
                "480p": "480",
                "360p": "360",
                "240p": "240",
                "144p": "144"
            }
            
            target_height = height_map.get(quality, quality.replace('p', '').split()[0])
            
            # Simplified format selection that's more reliable
            return f'best[height<={target_height}]/best'
            
    def reset_download_button(self):
        self.download_btn.config(text="Download Video", state=tk.NORMAL)
        self.progress.stop()
        self.status_label.config(text="Ready to download")

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()