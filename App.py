import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox
import os
from pytube.exceptions import (VideoUnavailable, PytubeError, ExtractError, HTMLParseError,
                                )
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Full, Empty
from download import Download

class GUI(object):
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Youtube Video Downloader")
        self.window.resizable(False, False)
        style = ttk.Style()
        style.theme_use('clam')
        self.canvas = tk.Canvas(self.window, width = 650, height = 77, bg = "grey")
        self.youtubeImage = tk.PhotoImage(file ="youtube.gif")
        self.canvas.create_image(150, 40, image =self.youtubeImage)
        self.canvas.pack()
        self.frame = tk.Frame(self.window, width = 650, height = 200, bg = "black")
        self.frame.grid_propagate(0)
        self.frame.pack(pady=0)
        self.videoLinkLabel = ttk.Label(self.frame, text = "Video Link:", foreground = "red", background = "black").\
            grid(row = 0, column = 0, padx = 5, pady = 40, sticky= tk.W)
        self.url_link = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable = self.url_link, width = 88, foreground = "black", font = 'Times 10')
        self.entry.grid(row = 0, column = 1)
        self.resolutionLabel = ttk.Label(self.frame, text = "Resolution:", foreground = 'red', background = "black").\
            grid(row = 1, column = 0, padx = 5, sticky = tk.W)
        self.resolution = tk.StringVar()
        resolution = ttk.Combobox(self.frame, width = 85, textvariable = self.resolution)
        resolution['values'] = ("1080p", "720p", "480p", "360p", "240p", "144p")
        resolution.grid(row = 1, column = 1, sticky = tk.W)
        resolution.current(1)
        resolution.config(state = 'readonly')
        self.saveFolderLabel = ttk.Label(self.frame, text = "Save to: ", foreground = 'red', background = 'black').\
            grid(row = 2, column = 0, padx = 5, pady = 40, sticky = tk.W)
        self.folder = tk.StringVar()
        self.folderEntry = ttk.Entry(self.frame, textvariable = self.folder, width = 88, foreground = "black", font = "Times 10")
        self.folderEntry.grid(row = 2, column = 1)
        self.folderEntry.insert(0, str(os.path.dirname(os.getcwd())))
        self.folderEntry.config(state = 'readonly')
        self.folderImage = tk.PhotoImage(file = "browserFolder2.gif")
        self.browseFolder = ttk.Button(self.frame, image = self.folderImage, command = lambda: self.folder.set\
            (fd.askdirectory(parent = self.window)))
        self.browseFolder.grid(row = 2, column = 2, padx = 5)
        self.frame2 = tk.Frame(self.window, width=650, height=70, bg="black")
        self.frame2.grid_propagate(0)
        self.frame2.pack()
        self.downloadImage = tk.PhotoImage(file="download2.gif")
        self.downloadButton = ttk.Button(self.frame2, image = self.downloadImage, command = self.scheduleVideoDownload)
        self.downloadButton.grid(row = 3, column = 3, padx = 470, sticky = tk.E)
        self.frame3 = tk.Frame(self.window, width=650, height=20, bg="black")
        self.frame3.grid_propagate(0)
        self.frame3.pack()
        ttk.Label(self.frame3, text="Current Download: ", foreground="red", background="black", font="Times 10").\
            grid(row=4, column = 0, sticky = tk.W)
        self.downloadTitleVar = tk.StringVar()
        self.downloadTitleVar.set('None')
        self.downloadTitleLabel = ttk.Label(self.frame3, textvariable=self.downloadTitleVar, foreground="red",
                                            background="black", font="Times 10")
        self.downloadTitleLabel.grid(row=4, column = 1)

        self.frame4 = tk.Frame(self.window, width=650, height=20, bg="black")
        self.frame4.grid_propagate(0)
        self.frame4.pack()
        ttk.Label(self.frame4, text="Download Progress: ", foreground="red", background="black", font="Times 10"). \
            grid(row=4, column=0, sticky=tk.W)
        self.downloadfSizeLabelVar = tk.StringVar()
        self.downloadfSizeLabelVar.set(f'({0} / {0})mb')
        self.downloadSizeLabel = ttk.Label(self.frame4, textvariable=self.downloadfSizeLabelVar, foreground="red",
                                            background="black", font="Times 10")
        self.downloadSizeLabel.grid(row=4, column=1)


        self.frame5 = tk.Frame(self.window, width=650, height=35, bg="black")
        self.frame5.grid_propagate(0)
        self.frame5.pack()
        self.progressCanvas = tk.Canvas(self.frame5, width = 600, height = 10, bg="grey")
        self.progressCanvas.create_rectangle(0,0,0,10, fill="red", tags="progress")
        self.progressCanvas.grid(row =0, sticky=tk.W, pady=10)
        self.downloadExecutor = ThreadPoolExecutor(max_workers=1)
        self.downloadScheduler = ThreadPoolExecutor(max_workers=1)
        self.urlQueue = Queue(maxsize=3)
        self.resolutionQueue = Queue(maxsize=3)
        self.window.mainloop()

    def scheduleVideoDownload(self):
        try:
            self.urlQueue.put(self.url_link.get(), block=False)
            self.resolutionQueue.put(self.resolution.get(), block=False)
            self.downloadScheduler.submit(self.createDownloadObject)
        except Empty as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except Full:
            tkinter.messagebox.showerror("YoutubeDownloaderError", "ERROR: cannot have more that 2 downloads queued")

    def createDownloadObject(self):
        try:
            self.downloadTitleVar.set('Searching...')
            download = Download()
            future = self.downloadExecutor.submit(download.downloadVideo, self.url_link.get(), self.resolution.get(),
                                                   self.progressCanvas, self.downloadTitleVar, self.downloadfSizeLabelVar,
                                                   self.folder.get())
            for results in as_completed([future]):
                results.result()
            tkinter.messagebox.showinfo("YoutubeDownloader Info", "Download complete")
        except VideoUnavailable as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except ExtractError as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except HTMLParseError as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except PytubeError as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except FileNotFoundError as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except BaseException as error:
            if error == '':
                error = "An unknown error occurred"
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        finally:
            _ = self.urlQueue.get(block=False)
            _ = self.resolutionQueue.get(block=False)
            self.downloadTitleVar.set('None')
            self.downloadfSizeLabelVar.set(f'({0} / {0})mb')

GUI()