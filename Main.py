from io import BytesIO
from pytube import *
from customtkinter import *
from PIL import Image
from urllib.request import *
import threading
import ffmpeg
import os
import subprocess

Font = "Helvetica"
set_appearance_mode("system")

# Root config
root = CTk()
root.iconbitmap("icon.ico")
root.config(background='#2b2d31')
root.title("Youtube Downloader")
root.geometry("900x500")
root.resizable(width=False, height=False)
root.columnconfigure(0, weight=1)



# Default page
Homepage = CTkFrame(root, fg_color='#2b2d31')
Homepage.grid(row=0, column=0, sticky="news")

# Download options page
Optionspage = CTkFrame(root, fg_color='#2b2d31')
Optionspage.grid(row=0, column=0, sticky="news")

# Download Progress page
Progresspage = CTkFrame(root, fg_color='#2b2d31')
Progresspage.grid(row=0, column=0, sticky="news")
# Download Completed Page
Completedpage = CTkFrame(root, fg_color='#2b2d31')
Completedpage.grid(row=0, column=0, sticky="news")
# POPUP Window
# Global initialization for download progress bar
progressbar = CTkProgressBar(Progresspage,height=8,width=500)

# Initializing global variables
yt = None
video_streams = None
audio_stream = None
percentage_of_completion = 0
remaining_text ="Calculating remaining amount..."
title = CTkEntry(Optionspage, font=('Helvetica', 18, 'bold'), width=650)
DownloadingPercent = CTkLabel(Progresspage, text=(f"{percentage_of_completion}%"), font=(Font, 25, "bold"))
RemainingAmount = CTkLabel(Progresspage, text=remaining_text, font=(Font, 22, "bold"))
finalVideoName = CTkLabel(Completedpage, font=('Helvetica', 18, 'bold'))
stream_sizes =[]
videoTitle = None
videoThumbnail = None
destination_path = None
error = False
isPaused = False
illegalCharacters = ["/", ":", "*", "?", "<", ">", "|", '"']
units = ["","Kbs","Mbs","Gbs","Tbs"]
def format(size, unit):
    if size >= 1024:
        return format(size / 1024, unit+1)
    return f"{size:.1f}{units[unit]}"
def reset():
    entry.delete(0, END)
    title.delete(0, END)
    cb.set("Quality")
    progressbar.set(0)
    percentage_of_completion = 0
    isPaused = False
    DownloadingPercent.configure(text="0%")
    invalidPath.place_forget()
    invalidName.place_forget()
    invalidRes.place_forget()
    invalidLink.place_forget()
    progressbar.place_forget()
    DownloadingPercent.place_forget()
    home_page()

def open_location():
    global destination_path
    os.startfile(destination_path)

def completed_page():
    global videoTitle, videoThumbnail
    Completedpage.tkraise()
    downloadedLabel = CTkLabel(Completedpage, text="The download is complete!", font=('Helvetica', 32, 'bold'))
    videoTitle+=".mp4"
    fontsize=int(min(24,1500/len(videoTitle)))
    finalVideoName.configure(font=(Font,fontsize,'bold'))
    finalVideoName.configure(text=videoTitle)
    finalVideoName.place(relx=0.5, y=360, anchor=CENTER)
    downloadedLabel.place(relx=0.5, y=50, anchor=CENTER)
    thumbnail = CTkLabel(Completedpage, image=videoThumbnail, height=240, width=426, text='')
    thumbnail.image = videoThumbnail
    thumbnail.place(relx=0.5, y=220, anchor=CENTER)
    resetButton.place(relx=0.3,y=420, anchor=CENTER)
    openFileButton.place(relx=0.7, y=420, anchor=CENTER)

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
        DownloadingPercent.configure (text=f"{round(percentage_of_completion, 1)}%")
        RemainingAmount.configure (text=remaining_text)
        schedule_check(t)

################vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#################### ROUBY'S JOB
def cancel():
    return
def pause():
    return
def resume():
    return
################^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^################### ROUBY'S JOB
def toggle():
    global isPaused
    isPaused = 1 - isPaused
    if isPaused:
        toggleButton.configure(text = "Resume",fg_color="#2ecc71",hover_color="#16a855")
        pause()
    else:
        toggleButton.configure(text = "Pause",fg_color="#565b5e",hover_color="#3c4042")
        resume()

# Function to instantiate progress bar
def progress_page():
    global progressbar
    Progresspage.tkraise()
    DownloadingLable = CTkLabel(Progresspage, text="Video is downloading...", font=(Font, 32, "bold"))
    DownloadingPercent.place(relx=0.5, y=220,anchor=CENTER)
    DownloadingLable.place(relx=0.5, y=50, anchor=CENTER)
    progressbar.set(0)
    progressbar.place(relx=0.5, y=250, anchor=CENTER)
    RemainingAmount.place(relx=0.5, y=275, anchor=CENTER)
    toggleButton.place(relx=0.3, y=400, anchor=CENTER)
    cancelButton.place(relx=0.7, y=400, anchor=CENTER)

# Function to calculate percentage of download
def progress_update(stream, chunk, bytes_remaining):
    global percentage_of_completion, remaining_text
    bytes_downloaded = stream.filesize - bytes_remaining
    remaining_text = f"{format(bytes_remaining,0)} remaining out of {format(stream.filesize,0)}"
    percentage_of_completion = (bytes_downloaded / stream.filesize) * 100
    # print(percentage_of_completion)

# Function to make user select the path for the download
def get_path():
    global destination_path
    destination_path = filedialog.askdirectory(title="Select Destination Folder")
    return destination_path

# function that downloads the video in another thread
def fix_name(oldName):
    newName = oldName
    for char in illegalCharacters:
        newName = newName.replace(char, " ")
    return newName

def download_video(stream, name, path):
    global videoTitle
    videoTitle = name
    if check_duplicate(name,path):
        os.remove(path+f"/{name}.mp4")
    stream.download(filename="video.webm")
    audio_stream.download(filename="audio.mp4")
    video = ffmpeg.input("video.webm")
    audio = ffmpeg.input("audio.mp4")
    try:
        subprocess.run(f"ffmpeg -i video.webm -i audio.mp4 -c copy {path}/output.mp4 -hide_banner -loglevel error -y")
        title = path+f"/{name}.mp4"
        os.remove("video.webm")
        os.remove("audio.mp4")
        os.rename(path+"/output.mp4", path+f"/{name}.mp4")
    except Exception as e:
        print(e)

# Function to check correct resolution and get stream
def find_stream(req_resolution, name, path):
    global video_streams
    for stream in video_streams:
        if stream.resolution == req_resolution:
            download_video_thread = threading.Thread(target=download_video, args=(stream, name, path))
            download_video_thread.start()
            check_if_done(download_video_thread)
            progress_page()
            break

#Function to check if there exists a file with this name in path
def check_duplicate(filename, path):    ##################  ROUBY'S JOB  ###########################
    full_path = path + f"/{filename}.mp4"
    return os.path.exists(full_path)

#PopUp Page function
def popup_page(res, name, path):#  Should be working, for some reason isn't. I'm going to bed.
    global error
    Popuppage = CTkToplevel(root)
    root.bell()
    Popuppage.after(100, Popuppage.lift)
    Popuppage.title = "A file already exists with this name"
    Popuppage.geometry("400x150")
    Popuppage.resizable(False,False)
    label = CTkLabel(Popuppage, text ="A file already exists with this name", font = (Font,20,'bold'))
    label.place(relx=0.5, y=40, anchor=CENTER)
    def rename():
        error = True
        Popuppage.destroy()
    def replace():
        error = False
        Popuppage.destroy()
        find_stream(res, name, path)
    renameButton = CTkButton(Popuppage, text="Rename", font=(Font, 22, "bold"), fg_color="#2ecc71", command=rename, width=140, height=45, corner_radius=70)
    replaceButton = CTkButton(Popuppage, text="Replace", font=(Font, 22, "bold"), fg_color="#2ecc71", command=replace, width=140, height=45, corner_radius=70)
    renameButton.place(relx=0.3,y=110,anchor = CENTER)
    replaceButton.place(relx=0.7,y=110, anchor= CENTER)
def check_errors():
    global error
    res=cb.get()
    res = res.split(" ")[0]
    name=title.get()
    invalidRes.place_forget()
    invalidName.place_forget()
    error = False
    if res == "Quality":
        invalidRes.place(x=710, y=385)
        error = True
    for char in illegalCharacters:
        if name.find(char) != -1:
            error = True
            invalidName.place(x=725,y=290)
            break
    if error:
        return
    path = get_path()
    if not path:
        invalidPath.place(x=565, y=445)
        return
    if check_duplicate(name, path):
        popup_page(res, name, path)
        return
    if not error:
        find_stream(res, name, path)

# Function to load the quality selection page components
def options_page(video_title=None, thumbnail_url=None, download_options=None):
    global videoTitle, videoThumbnail
    videoTitle = fix_name(video_title)
    title.insert(0,videoTitle)
    title.place(x=160, y=350, anchor = "w")
    filename = CTkLabel(Optionspage,text="Name:",font=('Helvetica',24,'bold'))
    filename.place(y=347,x=115,anchor =CENTER)
    # showing thumbnail
    u = urlopen(thumbnail_url)
    raw = u.read()
    u.close()
    img = Image.open(BytesIO(raw))
    videoThumbnail = CTkImage(img, size=(426, 240))
    img = CTkImage(img, size=(533, 300))
    thumbnail = CTkLabel(Optionspage, image=img, height=300, width=533, text='')
    thumbnail.place(relx=0.5, y=170, anchor=CENTER)

    # drop down menu for quality selection
    values = [download_options[i] +"  -  "+ stream_sizes[i] for i in range(len(stream_sizes))]
    cb.configure(values=values)
    cb.place(relx=0.5, y=400, anchor=CENTER)

    # download button to confirm download quality
    download_button = CTkButton(Optionspage, text="Download", font=(Font, 25, "bold"), command=check_errors, fg_color="#2ecc71", width=220, height=45, corner_radius=70)
    download_button.place(relx=0.5, y=450, anchor=CENTER)
    backButton.place(x=100,y=50,anchor=CENTER)

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
                stream_sizes.append(format(stream.filesize,0))
            options_page(title, thumbnail, res_values)
        except Exception as e:
            print(e)
            options_page(title, thumbnail)

    except Exception as e:  # put warning message
        invalidLink.place(x=520, y=251)

# Function to pass link to get_data function (triggered by button)
def click(event=None):
    global link
    link = entry.get()
    get_data(link)

def home_page():
    Homepage.tkraise()
    label.place(relx=0.5, y=90, anchor=CENTER)
    tube.place(y=91, anchor=CENTER, x=372)
    entry.place(relx=0.5, y=300, anchor=CENTER)
    button.place(relx=0.5, rely=0.35, anchor=CENTER)

def watermark():
    HPWatermark = CTkLabel(Homepage, text="Made by Bigo and Rouby", font=(Font,14))
    OPWatermark = CTkLabel(Optionspage, text="Made by Bigo and Rouby", font=(Font,14))
    PPWatermark = CTkLabel(Progresspage, text="Made by Bigo and Rouby", font=(Font,14))
    CPWatermark = CTkLabel(Completedpage, text="Made by Bigo and Rouby", font=(Font,14))
    HPWatermark.place(x=10,y=470)
    OPWatermark.place(x=10,y=470)
    PPWatermark.place(x=10,y=470)
    CPWatermark.place(x=10,y=470)

# Main Code -----------


# Warning message for invalid links
invalidLink = CTkLabel(Homepage, text="Please enter a valid link...", font=(Font,16), text_color="#f23f42")
invalidPath = CTkLabel(Optionspage, text="Please select a valid path...", font=(Font,16), text_color="#f23f42")
invalidRes  = CTkLabel(Optionspage, text="Please select a resolution...", font=(Font,16), text_color="#f23f42")
invalidName = CTkLabel(Optionspage, text="File name can't contain \n"+r"\ / : * ? \" < > |", font=(Font,16), text_color="#f23f42")
link = str()

# message header
please_insert = CTkLabel(Homepage, text="Insert video link...", font=(Font, 24))
please_insert.place(x=200, y=250)


# Just a header
empty = CTkLabel(Homepage, text="", font=(Font, 32, "bold"))
empty.pack(pady=500)
label = CTkLabel(Homepage, text="YouTube Downloader", font=(Font, 38, "bold"))
tube = CTkLabel(Homepage, text="Tube", font=(Font, 38, "bold"), text_color="#fd011b")

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
toggleButton = CTkButton(Progresspage, text="Pause", font=(Font, 25, "bold"), fg_color="#565b5e", command=toggle, width=220, height=45, corner_radius=70,hover_color="#3d4042")
cancelButton = CTkButton(Progresspage, text="Cancel", font=(Font, 25, "bold"), fg_color="#b32227", command=cancel, width=220, height=45, corner_radius=70,hover_color="#87171b")
watermark()
home_page()

# Run main loop
root.mainloop()
Homepage.tkraise()
Homepage.mainloop()

