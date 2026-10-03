import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Downloader")
        self.geometry("640x420")
        self.resizable(False, False)

        self.output_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        # URL
        ctk.CTkLabel(self, text="Video URL:", font=("Arial", 14)).pack(pady=(20, 5), anchor="w", padx=20)
        self.url_entry = ctk.CTkEntry(self, width=600, placeholder_text="https://youtube.com/watch?v=...")
        self.url_entry.pack(padx=20)

        # Format
        ctk.CTkLabel(self, text="Format:", font=("Arial", 14)).pack(pady=(15, 5), anchor="w", padx=20)
        self.format_var = ctk.StringVar(value="MP4 (Best)")
        self.format_menu = ctk.CTkOptionMenu(
            self,
            values=["MP4 (Best)", "MP4 (720p)", "MP4 (480p)", "MP3 (Audio only)"],
            variable=self.format_var,
            width=200,
        )
        self.format_menu.pack(anchor="w", padx=20)

        # Output folder
        self.folder_label = ctk.CTkLabel(self, text=f"Save to: {self.output_dir}", font=("Arial", 12))
        self.folder_label.pack(pady=(15, 5), anchor="w", padx=20)
        ctk.CTkButton(self, text="Choose Folder", command=self.choose_folder, width=140).pack(anchor="w", padx=20)

        # Download button
        self.download_btn = ctk.CTkButton(self, text="Download", command=self.start_download, height=45,
                                          font=("Arial", 16, "bold"))
        self.download_btn.pack(pady=25, padx=20, fill="x")

        # Status
        self.status = ctk.CTkLabel(self, text="Ready", font=("Arial", 12))
        self.status.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self, width=600)
        self.progress.set(0)
        self.progress.pack(pady=10, padx=20)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir)
        if folder:
            self.output_dir = folder
            self.folder_label.configure(text=f"Save to: {self.output_dir}")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please paste a video URL.")
            return
        self.download_btn.configure(state="disabled")
        self.progress.set(0)
        threading.Thread(target=self.download, args=(url,), daemon=True).start()

    def download(self, url):
        fmt = self.format_var.get()

        if fmt == "MP3 (Audio only)":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.hook],
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        else:
            height_map = {"MP4 (Best)": None, "MP4 (720p)": 720, "MP4 (480p)": 480}
            h = height_map[fmt]
            if h:
                ydl_opts = {
                    "format": f"bestvideo[height<={h}]+bestaudio/best[height<={h}]",
                    "merge_output_format": "mp4",
                    "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                    "progress_hooks": [self.hook],
                }
            else:
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                    "progress_hooks": [self.hook],
                }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.set_status("✅ Download complete!")
            self.set_progress(1)
        except Exception as e:
            self.set_status(f"❌ Error: {e}")
        finally:
            self.download_btn.configure(state="normal")

    def hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                pct = d["downloaded_bytes"] / total
                self.set_progress(pct)
                self.set_status(f"Downloading... {pct*100:.1f}%")
        elif d["status"] == "finished":
            self.set_status("Processing...")

    def set_status(self, text):
        self.after(0, lambda: self.status.configure(text=text))

    def set_progress(self, val):
        self.after(0, lambda: self.progress.set(val))


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
