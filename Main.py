from io import BytesIO
import base64
from pytube import *
from requests import *
from tkinter import *
from PIL import ImageTk, Image
import urllib.request
import requests
# Root config

root = Tk()
root.config(background='gray')
root.title("Youtube Downloader")
root.geometry("900x400")
root.resizable(width=False, height=False)
root.columnconfigure(0, weight=1)

# Default page
f1 = Frame(root, bg='gray')
f1.grid(row=0, column=0, sticky="news")


# Download options page
f2 = Frame(root, bg='gray')
f2.grid(row=0, column=0, sticky="news")


def f2load(video_title=None, thumbnail="https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png", download_options=None):
    # video title
    title = Label(f2, text=video_title, background='gray')
    title.pack()

    # showing thumbnail
    u = requests.get(thumbnail)
    image = ImageTk.PhotoImage(Image.open(BytesIO(u.content)))
    l = Label(f2, image=image)
    l.pack()
    #canvas = Canvas(f2, width=400, height=400)
    #canvas.pack()
    #canvas.create_image(20, 20, anchor=NW,  image=img)


def download(link):
    try:
        yt = YouTube(link)
        yt.check_availability()
        invalid.place_forget()  # remove warning message
        f2.tkraise()

        title = yt.title
        thumbnail = yt.thumbnail_url
        f2load(title)


    except:  # put warning message
        invalid.place(x=70, y=235)


def click(event=None):
    link = entry.get()
    download(link)
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
