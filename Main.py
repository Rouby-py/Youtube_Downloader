from io import BytesIO
from pytube import *
from requests import *
from tkinter import *
from PIL import ImageTk, Image
from urllib.request import *
from tkinter import ttk
from PIL import *
import requests


# Root config
root = Tk()
root.config(background='gray')
root.title("Youtube Downloader")
root.geometry("900x500")
root.resizable(width=False, height=False)
root.columnconfigure(0, weight=1)


# Default page
f1 = Frame(root, bg='gray')
f1.grid(row=0, column=0, sticky="news")


# Download options page
f2 = Frame(root, bg='gray')
f2.grid(row=0, column=0, sticky="news")


def f2load(video_title=None, thumbnail_url=None, download_options=None):
    # video title
    title = ttk.Label(f2, text=video_title, background='gray', font=('Helvetica', 24, 'bold'))
    title.pack()

    # showing thumbnail
    u = urlopen(thumbnail_url)
    raw = u.read()
    u.close()
    img = Image.open(BytesIO(raw))
    img = img.resize((500, 300))
    img = ImageTk.PhotoImage(img)
    thumbnail = Label(f2, image=img, height=300, width=500)
    thumbnail.image = img
    thumbnail.pack()

    # drop down menu for quality selection

    cb = ttk.Combobox(f2, values=download_options, width=40, state='readonly')
    cb.pack()



def get_data(link):
    try:
        yt = YouTube(link)
        yt.check_availability()
        invalid.place_forget()  # remove warning message
        f2.tkraise()

        title = yt.title
        thumbnail = yt.thumbnail_url
        try:
            streams = yt.streams
            print(streams)
            res_names = set()
            for stream in streams:
                if stream.resolution:
                    res_names.add(stream.resolution)
            res_values = list()
            for res in res_names:
                res_values.append(int(res.split('p')[0]))
            f2load(title, thumbnail, sorted(res_values))
        except Exception as e:
            print(e)
            f2load(title, thumbnail)

    except:  # put warning message
        invalid.place(x=70, y=235)


def click(event=None):
    link = entry.get()
    get_data(link)
    # entry.delete(0, END)


# Warning message for invalid links
invalid = Label(f1, text="Please enter a valid link", font="Raavi", foreground="darkred", background='gray')


# Just a header
label = Label(f1, text="Youtube Downloader", font=("Raavi", 26, "bold"), background="gray")
label.pack(side=TOP, pady=60)


# Entry box for link
entry = Entry(f1, width=50, font=("Raavi", 20, "bold"))
entry.place(relx=0.5, rely=0.5, anchor=CENTER)
entry.bind("<Return>", click)

# Submit button for entry box
button = Button(f1, text="Download", font=("Raavi", 26, "bold"), background="green", command=click)
button.pack(side=BOTTOM, pady=100)

f1.tkraise()
f1.mainloop()
