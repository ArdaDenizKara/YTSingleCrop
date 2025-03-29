import yt_dlp
import tkinter as tk
from tkinter import  messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageTk
import threading
import re
import os
import webbrowser

def open_github():
    webbrowser.open("https://github.com/ArdaDenizKara")

def ProgressHook(d):
    if d['status'] == 'downloading':
        percent = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_percent_str', '0.0%')).strip()
        eta = d.get('eta', 'N/A')
        speed = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_speed_str', 'N/A')).strip()
        
        progressLabel.config(text=f"📥 Progress: {percent} |⏳ ETA: {eta}s | ⚡Speed: {speed}")
        root.update_idletasks()
    elif d['status'] == 'finished':
        downloadButton.config(text="Processing...")
        progressLabel.config(text="🔄 Processing video...", fg="orange")
        root.update_idletasks()
        
def ValidateTimeInterval(startTime, endTime):
    try:
        startTimeObj = datetime.strptime(startTime, "%H:%M:%S")
        endTimeObj = datetime.strptime(endTime, "%H:%M:%S")
        
        if endTimeObj <= startTimeObj:
            messagebox.showerror("Error", "End time must be greater than start time!")
            return False
        return True
    except ValueError:
        messagebox.showerror("Error", "Invalid time format! Please use hh:mm:ss.")
        return False

def ValidateURL(url):
    if not url.startswith("https://www.youtube.com/watch?v="):
        messagebox.showerror("Error", "Please enter a valid YouTube URL (must start with https://www.youtube.com/watch?v=).")
        return False
    return True

def IsVideoAvailable(url):
    if not ValidateURL(url):
        return False 
    video_id_match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    if not video_id_match:
        messagebox.showerror("Error", "Invalid YouTube URL. No video ID found.")
        return False
    try:
        with yt_dlp.YoutubeDL() as ydl:
         result = ydl.extract_info(url, download=False)
        if result.get('restricted', False):
         messagebox.showerror("Error", "Video cannot be downloaded. It may be private or region-restricted.")
         return False
        return True
    except Exception as e:
        messagebox.showerror("Error","Invalid YouTube URL. No video ID found.")
        return False

        

def DownloadVideo():
    url = urlEntry.get()
    startTime = startTimeEntry.get()
    endTime = endTimeEntry.get()
    
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return
    if not startTime:
        messagebox.showerror("Error", "Please enter a start time in hh:mm:ss format!")
        return
    if not endTime:
        messagebox.showerror("Error", "Please enter an end time in hh:mm:ss format!")
        return
    if not ValidateTimeInterval(startTime, endTime):
        return
    if not IsVideoAvailable(url):
      return
   
    
    saveLocation = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    if not saveLocation:
        return  
    downloadButton.config(state=tk.DISABLED, text="Downloading...")
    ydl_opts = {
        'format': 'bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': saveLocation,
        'postprocessor_args': [
            '-ss', startTime,
            '-to', endTime,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', '-2'
        ],
        'noplaylist': True,
        'progress_hooks': [ProgressHook],
        
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Video downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        downloadButton.config(state=tk.NORMAL, text="Download Video")
        progressLabel.config(text="Progress: 0% | ETA: N/A | Speed: N/A")
        ClearInputs()

def DownloadVideoThread():
    threading.Thread(target=DownloadVideo, daemon=True).start()

def ClearInputs():
  urlEntry.delete(0, tk.END)
  startTimeEntry.delete(0, tk.END)
  endTimeEntry.delete(0, tk.END)

root = tk.Tk()
root.title("YouTube Video Cropper")
#root.geometry("600x300")
root.geometry("650x375")
root.resizable(False, False)
root.configure(bg="#1e1e2e")
font_title = ("Arial", 14, "bold")
font_text = ("Arial", 11)
text_color = "#ffffff"  
button_color = "#ffcc00"
entry_bg = "#2e2e3e" 

base_dir = os.path.dirname(os.path.abspath(__file__))

image_folder = os.path.join(base_dir, "assets")

try:
    img = Image.open(os.path.join(image_folder, "ytvideocutter.png")) 
    img = img.resize((64, 64))
    icon = ImageTk.PhotoImage(img)
    root.iconphoto(False, icon)
except:
    print("Warning: Icon file not found.")


githubLogo = Image.open(os.path.join(image_folder, "githubLogo.png")) 
githubLogo = githubLogo.resize((20, 20)) 
githubLogo = ImageTk.PhotoImage(githubLogo)
creditsButton = tk.Button(root, text="GitHub", font=("Arial", 10), bg="#5555ff", fg="white", command=open_github,compound="left", image=githubLogo)
creditsButton.place(x=0, y=350)

tableFrame = tk.Frame(root, bg="#1e1e2e")
tableFrame.pack(pady=25)
tk.Label(root, text="YouTube URL:", font=font_title, fg=text_color, bg="#1e1e2e").pack(pady=15)
urlEntry = tk.Entry(root, width=50, font=font_text, bg=entry_bg, fg=text_color, insertbackground=text_color)
urlEntry.pack()

tk.Label(root, text="Start Time (hh:mm:ss):", font=font_title, fg=text_color, bg="#1e1e2e").pack(pady=5)
startTimeEntry = tk.Entry(root, width=20, font=font_text, bg=entry_bg, fg=text_color, insertbackground=text_color)
startTimeEntry.pack()

tk.Label(root, text="End Time (hh:mm:ss):", font=font_title, fg=text_color, bg="#1e1e2e").pack(pady=5)
endTimeEntry = tk.Entry(root, width=20, font=font_text, bg=entry_bg, fg=text_color, insertbackground=text_color)
endTimeEntry.pack()

progressLabel = tk.Label(root, text="Progress: 0% | ETA: N/A | Speed: N/A", font=font_text, fg="yellow", bg="#1e1e2e")
progressLabel.pack(pady=5)

downloadButton = tk.Button(root, text="Download Video", font=font_title, bg=button_color, command=DownloadVideoThread)
downloadButton.pack(pady=10)



root.mainloop() 