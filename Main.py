from io import BytesIO
from pytube import *
from requests import *
from tkinter import *
import customtkinter
from customtkinter import *
from tkinter import filedialog, ttk
from PIL import ImageTk, Image
from urllib.request import *
from PIL import *
import requests
import threading
import time

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

# Global initialization for download progress bar
progressbar = CTkProgressBar(Progresspage)

# Initializing global variables
yt = None
streams = None
percentage_of_completion = 0


# Function to check download progress periodically
def schedule_check(t):
    Progresspage.after(500, check_if_done, t)


# Function to check if the download process is done and update the progress bar
def check_if_done(t):
    global percentage_of_completion
    if not t.is_alive():
        progressbar.destroy()
    else:
        Progresspage.update_idletasks()
        progressbar.set(percentage_of_completion/100)
        schedule_check(t)


# Function to instantiate progress bar
def progress_page():
    global progressbar
    Progresspage.tkraise()
    progressbar.pack(padx=20, pady=10)


# Function to calculate percentage of download
def progress_update(stream, chunk, bytes_remaining):
    global percentage_of_completion
    bytes_downloaded = stream.filesize - bytes_remaining
    percentage_of_completion = (bytes_downloaded / stream.filesize) * 100
    # print(percentage_of_completion)


# Function to make user select the path for the download
def get_path():
    destination_path = filedialog.askdirectory(title="Select Destination Folder")
    if destination_path:
        return destination_path
    else:
        invalidPath.place(x=70, y=235)


# function that downloads the video in another thread
def download_video(stream, path):
    stream.download(path)


# Function to check correct resolution and get stream
def find_stream(req_resolution):
    global streams
    path = get_path()
    for stream in streams:
        if stream.resolution == req_resolution:
            download_video_thread = threading.Thread(target=download_video, args=(stream, path))
            download_video_thread.start()
            check_if_done(download_video_thread)
            progress_page()
            break


# Function to pass quality choice to find_stream (triggered by button)
def choose_resolution():
    res = cb.get()
    find_stream(res)


# Function to load the quality selection page components
def options_page(video_title=None, thumbnail_url=None, download_options=None):
    # video title
    title = CTkLabel(Optionspage, text=video_title, font=('Helvetica', 24, 'bold'))
    title.place(relx=0.5, y=40, anchor=CENTER)

    # showing thumbnail
    u = urlopen(thumbnail_url)
    raw = u.read()
    u.close()
    img = Image.open(BytesIO(raw))
    img = img.resize((500, 300))
    img = ImageTk.PhotoImage(img)
    thumbnail = Label(Optionspage, image=img, height=300, width=500)
    thumbnail.image = img
    thumbnail.place(relx=0.5, y=220, anchor=CENTER)

    # drop down menu for quality selection
    cb.configure(values=download_options)
    cb.place(relx=0.5, y=400, anchor=CENTER)

    # download button to confirm download quality
    download_button = CTkButton(Optionspage, text="Download", font=(Font, 25, "bold"), command=choose_resolution, fg_color="#2ecc71", width=220, height=45, corner_radius=70)
    download_button.place(relx=0.5, y=450, anchor=CENTER)


# Function to filter all streams and pass them to quality selection page
def get_data(link):
    global yt
    global streams
    try:
        yt = YouTube(link, on_progress_callback=progress_update)
        yt.check_availability()
        invalidLink.place_forget()  # remove warning message
        Optionspage.tkraise()

        title = yt.title
        thumbnail = yt.thumbnail_url
        try:
            streams = yt.streams
            res_names = set()
            for stream in streams:
                if stream.resolution:
                    res_names.add(stream.resolution)
            res_values = list()
            for res in res_names:
                res_values.append(int(res.split('p')[0]))
            res_values = sorted(res_values)
            res_values = [str(res) + 'p' for res in res_values]
            options_page(title, thumbnail, res_values)
        except Exception as e:
            print(e)
            options_page(title, thumbnail)

    except Exception as e:  # put warning message
        invalidLink.place(x=200, y=270)


# Function to pass link to get_data function (triggered by button)
def click(event=None):
    global link
    link = entry.get()
    get_data(link)
    # entry.delete(0, END)


# Main Code -----------

# Warning message for invalid links
invalidLink = Label(Homepage, text="Please enter a valid link", font=Font, foreground="darkred", background='#2b2d31')
invalidPath = Label(Homepage, text="Please select a valid path", font=Font, foreground="darkred", background='#2b2d31')
link = str()
# Just a header
empty = CTkLabel(Homepage, text="", font=(Font, 32, "bold"))
empty.pack(pady=500)
label = CTkLabel(Homepage, text="YouTube Downloader", font=(Font, 32, "bold"))
label.place(relx=0.5, y=40, anchor=CENTER)

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
button.place(relx=0.5, rely=0.35, anchor=CENTER)

# Run main loop
Homepage.tkraise()
Homepage.mainloop()
