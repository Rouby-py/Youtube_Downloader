from io import BytesIO
from pytube import *
from requests import *
from tkinter import *
import customtkinter
from customtkinter import *
from tkinter import filedialog, ttk
from PIL import ImageTk, Image
from urllib.request import *
from subprocess import *
from os import *
from PIL import *
import requests
import threading
import time
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import ffmpeg
import os
import subprocess

Font = "Helvetica"
customtkinter.set_appearance_mode("system")

# Root config
root = Tk()
root.config(background='#2b2d31')
root.title("Youtube Downloader")
root.geometry("900x500")
root.resizable(width=False, height=False)
root.columnconfigure(0, weight=1)


# Default page
Homepage = Frame(root, bg='#2b2d31')
Homepage.grid(row=0, column=0, sticky="news")

# Download options page
Optionspage = Frame(root, bg='#2b2d31')
Optionspage.grid(row=0, column=0, sticky="news")

# Download Progress page
Progresspage = Frame(root, bg='#2b2d31')
Progresspage.grid(row=0, column=0, sticky="news")
# Download Completed Page
Completedpage = Frame(root, bg='#2b2d31')
Completedpage.grid(row=0, column=0, sticky="news")
# Global initialization for download progress bar
progressbar = CTkProgressBar(Progresspage,height=8,width=500)

# Initializing global variables
yt = None
video_streams = None
audio_stream = None
percentage_of_completion = 0
DownloadingPercent = CTkLabel(Progresspage, text=(f"{percentage_of_completion}%"), font=(Font, 25, "bold"))
videoTitle = None
videoThumbnail = None
destination_path = None
def reset():
    entry.delete(0,END)
    home_page()
def open_location():
    directory = path.dirname(destination_path)
    Popen(['explorer', directory])
def completed_page():
    global videoTitle, videoThumbnail
    Completedpage.tkraise()
    title = CTkLabel(Completedpage, text=videoTitle, font=('Helvetica', 20, 'bold'))
    downloadedLabel = CTkLabel(Completedpage, text="The download is complete!", font=('Helvetica', 32, 'bold'))
    title.place(relx=0.5, y=360, anchor=CENTER)
    downloadedLabel.place(relx=0.5, y=50, anchor=CENTER)
    videoThumbnail = ImageTk.PhotoImage(videoThumbnail)
    thumbnail = Label(Completedpage, image=videoThumbnail, height=240, width=426)
    thumbnail.image = videoThumbnail
    thumbnail.place(relx=0.5, y=220, anchor=CENTER)
    resetButton.place(relx=0.3,y=420, anchor = CENTER)
    openFileButton.place(relx=0.7,y=420, anchor = CENTER)
# Function to check download progress periodically
def schedule_check(t):
    Progresspage.after(500, check_if_done, t)


# Function to check if the download process is done and update the progress bar
def check_if_done(t):
    global percentage_of_completion
    if not t.is_alive():
        completed_page()
    else:
        Progresspage.update_idletasks()
        progressbar.set(percentage_of_completion/100)
        DownloadingPercent.configure (text=f"{round(percentage_of_completion,1)}%")
        schedule_check(t)


# Function to instantiate progress bar
def progress_page():
    global progressbar
    Progresspage.tkraise()
    DownloadingLable = CTkLabel(Progresspage, text="Video is downloading...", font=(Font, 32, "bold"))
    DownloadingPercent.place(relx=0.5,y=220,anchor=CENTER)
    DownloadingLable.place(relx=0.5, y=50, anchor=CENTER)
    progressbar.place(relx=0.5, y=250,anchor=CENTER)


# Function to calculate percentage of download
def progress_update(stream, chunk, bytes_remaining):
    global percentage_of_completion
    bytes_downloaded = stream.filesize - bytes_remaining
    percentage_of_completion = (bytes_downloaded / stream.filesize) * 100
    # print(percentage_of_completion)


# Function to make user select the path for the download
def get_path():
    global destination_path
    destination_path = filedialog.askdirectory(title="Select Destination Folder")
    if destination_path:
        return destination_path
    else:
        invalidPath.place(x=565, y=445)
    return destination_path


# function that downloads the video in another thread
def download_video(stream, path):
    name = stream.title
    stream.download(path, filename="video.webm")
    audio_stream.download(path, filename="audio.mp4")
    video = ffmpeg.input(path+"/video.webm")
    audio = ffmpeg.input(path+"/audio.mp4")
    try:
        subprocess.run(f"ffmpeg -i {path}/video.webm -i {path}/audio.mp4 -c copy {path}/output.mp4 -hide_banner -loglevel error -y")
        title = path+f"/{name}.mp4"
        os.remove(path+"/video.webm")
        os.remove(path+"/audio.mp4")
        name = name.replace("/", " ")
        name = name.replace(":", " ")
        name = name.replace("*", " ")
        name = name.replace("?", " ")
        name = name.replace("<", " ")
        name = name.replace(">", " ")
        name = name.replace("|", " ")
        name = name.replace('"', " ")
        os.rename(path+"/output.mp4", path+f"/{name}.mp4")
    except Exception as e:
        print(e)

# Function to check correct resolution and get stream
def find_stream(req_resolution):
    global video_streams
    path = get_path()
    for stream in video_streams:
        if stream.resolution == req_resolution:
            download_video_thread = threading.Thread(target=download_video, args=(stream, path))
            download_video_thread.start()
            check_if_done(download_video_thread)
            progress_page()
            break


# Function to pass quality choice to find_stream (triggered by button)
def choose_resolution():
    res = cb.get()
    if res != "Quality":
        find_stream(res)
    else:
        invalidRes.place(x=565, y=445)


# Function to load the quality selection page components
def options_page(video_title=None, thumbnail_url=None, download_options=None):
    global videoTitle, videoThumbnail
    videoTitle = video_title
    title = CTkLabel(Optionspage, text=video_title, font=('Helvetica', 24, 'bold'))
    title.place(relx=0.5, y=40, anchor=CENTER)

    # showing thumbnail
    u = urlopen(thumbnail_url)
    raw = u.read()
    u.close()
    img = Image.open(BytesIO(raw))
    img = img.resize((533, 300))
    videoThumbnail = img.resize((426, 240))
    img = ImageTk.PhotoImage(img)
    thumbnail = Label(Optionspage, image=img, height=300, width=533)
    thumbnail.image = img
    thumbnail.place(relx=0.5, y=220, anchor=CENTER)

    # drop down menu for quality selection
    cb.configure(values=download_options)
    cb.place(relx=0.5, y=400, anchor=CENTER)

    # download button to confirm download quality
    download_button = CTkButton(Optionspage, text="Download", font=(Font, 25, "bold"), command=choose_resolution, fg_color="#2ecc71", width=220, height=45, corner_radius=70)
    download_button.place(relx=0.5, y=450, anchor=CENTER)
    backButton.place(x=100,y=90,anchor=CENTER)

# Function to filter all streams and pass them to quality selection page
def get_data(link):
    global yt
    global video_streams
    global audio_stream
    try:
        yt = YouTube(link, on_progress_callback=progress_update)
        yt.check_availability()
        invalidLink.place_forget()  # remove warning message
        Optionspage.tkraise()

        title = yt.title
        thumbnail = yt.thumbnail_url
        try:
            video_streams = yt.streams.filter(file_extension="webm", type="video")
            audio_stream = yt.streams.filter(file_extension="mp4", type="audio").last()
            res_values = []
            for stream in video_streams:
                res_values.append(stream.resolution)
            options_page(title, thumbnail, res_values)
        except Exception as e:
            print(e)
            options_page(title, thumbnail)

    except Exception as e:  # put warning message
        invalidLink.place(x=200, y=260)


# Function to pass link to get_data function (triggered by button)
def click(event=None):
    global link
    link = entry.get()
    get_data(link)
    # entry.delete(0, END)

def home_page():
    Homepage.tkraise()
    label.place(relx=0.5, y=50, anchor=CENTER)
    tube.place(y=51,anchor=CENTER,x=383)
    entry.place(relx=0.5, y=300, anchor=CENTER)
    button.place(relx=0.5, rely=0.35, anchor=CENTER)
def watermark():
    HPWatermark  = CTkLabel(Homepage, text="Made by Rouby and Bigo", font=(Font,14))
    OPWatermark  = CTkLabel(Optionspage, text="Made by Rouby and Bigo", font=(Font,14))
    PPWatermark  = CTkLabel(Progresspage, text="Made by Rouby and Bigo", font=(Font,14))
    CPWatermark  = CTkLabel(Completedpage, text="Made by Rouby and Bigo", font=(Font,14))
    HPWatermark.place(x=10,y=470)
    OPWatermark.place(x=10,y=470)
    PPWatermark.place(x=10,y=470)
    CPWatermark.place(x=10,y=470)

# Main Code -----------

# Warning message for invalid links
invalidLink = CTkLabel(Homepage, text="Please enter a valid link...", font=(Font,16), text_color="#f23f42")
invalidPath = CTkLabel(Optionspage, text="Please select a valid path...", font=(Font,16), text_color="#f23f42")
invalidRes  = CTkLabel(Optionspage, text="Please select a resolution...", font=(Font,16), text_color="#f23f42")
link = str()

# Just a header
empty = CTkLabel(Homepage, text="", font=(Font, 32, "bold"))
empty.pack(pady=500)
label = CTkLabel(Homepage, text="YouTube Downloader", font=(Font, 32, "bold"))
tube = CTkLabel(Homepage, text="Tube", font=(Font, 32, "bold"), text_color="#fd011b")
# combobox for quality selection
cb = CTkComboBox(Optionspage, width=500, state='readonly', dropdown_font=(Font, 32, "bold"), corner_radius=50, hover=True)
cb.set('Quality')
cb.configure(state='readonly', font=(Font, 25, 'bold'), dropdown_font=(Font, 20, 'bold'), justify='center')

# Entry box for link
entry = CTkEntry(Homepage, width=500, font=(Font, 20, "bold"))
entry.place(relx=0.5, y=250, anchor=CENTER)

# Binding enter button to entry box
entry.bind("<Return>", click)


# Submit button for entry box
button = CTkButton(Homepage, text="Confirm", font=(Font, 25, "bold"), fg_color="#2ecc71", command=click, width=220, height=45, corner_radius=70)
resetButton = CTkButton(Completedpage, text="Download New Video", font=(Font, 25, "bold"), fg_color="#2ecc71", command=reset, width=220, height=45, corner_radius=70)
openFileButton = CTkButton(Completedpage, text="Open File Location", font=(Font, 25, "bold"), fg_color="#2ecc71", command=open_location, width=220, height=45, corner_radius=70)
backButton = CTkButton(Optionspage, text="<< Back", font=(Font, 22, "bold"), fg_color="#2b2d31",border_color="#565b5e", border_width=2, command=reset, width=140, height=40, corner_radius=70,hover_color="#565b5e")
watermark()
home_page()

# Run main loop
Homepage.tkraise()
Homepage.mainloop()
