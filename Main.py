from io import BytesIO
from pytube import *
from requests import *
from tkinter import *
from tkinter import filedialog, ttk
from PIL import ImageTk, Image
from urllib.request import *
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

def get_path():
    destination_path = filedialog.askdirectory(title="Select Destination Folder")
    if destination_path:
        return destination_path
    else:
        invalidPath.place(x=70, y=235);

def download(req_resolution):
    path=get_path()
    print(path)
    yt = YouTube(link)
    streams = yt.streams
    for stream in streams:
        if stream.resolution == req_resolution:
            stream.download(path)
            break

def get_value():
    res = cb.get()
    download(res)
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

    cb.config(values = download_options)
    cb.pack()
    download_button = Button(f2, text="Download", font=("Raavi", 26, "bold"), background="green", command = get_value)
    download_button.pack()


def get_data(link):
    try:
        yt = YouTube(link)
        yt.check_availability()
        invalidLink.place_forget()  # remove warning message
        f2.tkraise()

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
            f2load(title, thumbnail, res_values)
        except Exception as e:
            print("ERRORRR")
            # f2load(title, thumbnail)

    except:  # put warning message
        invalidLink.place(x=70, y=235)


def click(event=None):
    link = entry.get()
    get_data(link)
    # entry.delete(0, END)




# Warning message for invalid links
invalidLink = Label(f1, text="Please enter a valid link", font="Raavi", foreground="darkred", background='gray')
invalidPath = Label(f1, text="Please select a valid path", font="Raavi", foreground="darkred", background='gray')
link = str()
# Just a header
label = Label(f1, text="Youtube Downloader", font=("Raavi", 26, "bold"), background="gray")
label.pack(side=TOP, pady=60)
cb = ttk.Combobox(f2, width=40, state='readonly')

# Entry box for link
entry = Entry(f1, width=50, font=("Raavi", 20, "bold"))
entry.place(relx=0.5, rely=0.5, anchor=CENTER)
entry.bind("<Return>", click)

# Submit button for entry box
button = Button(f1, text="Download", font=("Raavi", 26, "bold"), background="green", command=click)
button.pack(side=BOTTOM, pady=100)

f1.tkraise()
f1.mainloop()
