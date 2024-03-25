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

# Download options page
Progresspage = Frame(root, bg='#2b2d31')
Progresspage.grid(row=0, column=0, sticky="news")

percentage_of_completion = 0
progressbar = CTkProgressBar(Progresspage)


def schedule_check(t):
    Progresspage.after(500, check_if_done, t)


def check_if_done(t):
    global percentage_of_completion
    if not t.is_alive():
        progressbar.destroy()
    else:
        Progresspage.update_idletasks()
        progressbar.set(percentage_of_completion/100)
        schedule_check(t)


def progress_page():
    global progressbar
    Progresspage.tkraise()
    progressbar.pack(padx=20, pady=10)


def progress_update(stream, chunk, bytes_remaining):
    global percentage_of_completion
    bytes_downloaded = stream.filesize - bytes_remaining
    percentage_of_completion = (bytes_downloaded / stream.filesize) * 100
    #print(percentage_of_completion)


def get_path():
    destination_path = filedialog.askdirectory(title="Select Destination Folder")
    if destination_path:
        return destination_path
    else:
        invalidPath.place(x=70, y=235)


def download_video(stream, path):
    stream.download(path)


def download(req_resolution):
    global streams
    path = get_path()
    for stream in streams:
        print(stream)
        if stream.resolution == req_resolution:
            download_video_thread = threading.Thread(target=download_video, args=(stream, path))
            download_video_thread.start()
            check_if_done(download_video_thread)
            progress_page()
            break

def get_value():
    res = cb.get()
    #print(res)
    download(res)


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
    cb.configure(values = download_options)
    cb.place(relx=0.5, y=400, anchor=CENTER)

    #download button
    download_button = CTkButton(Optionspage, text="Download", font=(Font, 25, "bold"), command=get_value, fg_color="#2ecc71", width=220, height=45, corner_radius=70)
    download_button.place(relx=0.5, y=450, anchor=CENTER)


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
            res_values=sorted(res_values)
            res_values = [str(res) + 'p' for res in res_values]
            options_page(title, thumbnail, res_values)
        except Exception as e:
            print(e)
            options_page(title, thumbnail)

    except:  # put warning message
        invalidLink.place(x=70, y=235)


def click(event=None):
    link = entry.get()
    get_data(link)
    # entry.delete(0, END)

yt=None
streams=None

# Warning message for invalid links
invalidLink = Label(Homepage, text="Please enter a valid link", font=Font, foreground="darkred", background='#2b2d31')
invalidPath = Label(Homepage, text="Please select a valid path", font=Font, foreground="darkred", background='#2b2d31')
link = str()
# Just a header
empty = CTkLabel(Homepage, text="", font=(Font, 32, "bold"))
empty.pack(pady=500)
label = CTkLabel(Homepage, text="YouTube Downloader", font=(Font, 32, "bold"))
label.place(relx=0.5, y=40, anchor=CENTER)

#combobox for quality selection
cb = CTkComboBox(Optionspage, width=500, state='readonly', dropdown_font=(Font, 32, "bold"), corner_radius=50, hover=True)
cb.set('Quality')
cb.configure(state='readonly', font=(Font, 25, 'bold'), dropdown_font=(Font, 20, 'bold'), justify='center')

# Entry box for link
entry = CTkEntry(Homepage, width=500, font=(Font, 20, "bold"))
entry.place(relx=0.5, y=300, anchor=CENTER)
entry.bind("<Return>", click)


# Submit button for entry box
button = CTkButton(Homepage, text="Confirm", font=(Font, 25, "bold"), fg_color="#2ecc71", command=click, width=220, height=45, corner_radius=70)
button.place(relx=0.5, rely=0.35, anchor=CENTER)

Homepage.tkraise()
Homepage.mainloop()
