import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.messagebox
import os
from pytube import Playlist, YouTube
from pytube.exceptions import VideoPrivate, VideoUnavailable, PytubeError
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Full, Empty
class GUI(object):
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Youtube Video Downloader")
        self.window.resizable(False, False)
        self.canvas = tk.Canvas(self.window, width = 650, height = 77, bg = "grey")
        self.youtubeImage = tk.PhotoImage(file ="youtube.gif")
        self.canvas.create_image(150, 40, image =self.youtubeImage)
        self.canvas.pack()
        self.frame = tk.Frame(self.window, width = 650, height = 200, bg = "black")
        self.frame.grid_propagate(0)
        self.frame.pack()
        self.videoLinkLabel = ttk.Label(self.frame, text = "Video Link:", foreground = "cyan", background = "black").\
            grid(row = 0, column = 0, padx = 5, pady = 40, sticky= tk.W)
        self.url_link = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable = self.url_link, width = 88, foreground = "black", font = 'Times 10')
        self.entry.grid(row = 0, column = 1)
        self.resolutionLabel = ttk.Label(self.frame, text = "Resolution:", foreground = 'cyan', background = "black").\
            grid(row = 1, column = 0, padx = 5, sticky = tk.W)
        self.resolution = tk.StringVar()
        resolution = ttk.Combobox(self.frame, width = 85, textvariable = self.resolution)
        resolution['values'] = ("1080p", "720p", "480p", "360p", "240p", "144p")
        resolution.grid(row = 1, column = 1, sticky = tk.W)
        resolution.current(1)
        resolution.config(state = 'readonly')
        self.saveFolderLabel = ttk.Label(self.frame, text = "Save to: ", foreground = 'cyan', background = 'black').\
            grid(row = 2, column = 0, padx = 5, pady = 40, sticky = tk.W)
        self.folder = tk.StringVar()
        self.folderEntry = ttk.Entry(self.frame, textvariable = self.folder, width = 88, foreground = "black", font = "Times 10")
        self.folderEntry.grid(row = 2, column = 1)
        self.folderEntry.insert(0, str(os.path.dirname(os.getcwd())))
        self.folderEntry.config(state = 'readonly')
        self.folderImage = tk.PhotoImage(file = "browserFolder.gif")
        self.browseFolder = ttk.Button(self.frame, image = self.folderImage, command = lambda: self.folder.set\
            (fd.askdirectory(parent = self.window)))
        self.browseFolder.grid(row = 2, column = 2, padx = 5)
        self.frame2 = tk.Frame(self.window, width=650, height=173, bg="black")
        self.frame2.grid_propagate(0)
        self.frame2.pack()
        self.downloadImage = tk.PhotoImage(file="download.gif")
        self.downloadButton = ttk.Button(self.frame2, image = self.downloadImage, command = self.scheduleVideoDownload)
        self.downloadButton.grid(row = 3, column = 3, padx = 470, sticky = tk.E)
        self.downloadScheduler = ThreadPoolExecutor(max_workers=3)
        self.urlQueue = Queue(maxsize=3)
        self.resolutionQueue = Queue(maxsize=3)
        self.window.mainloop()

    def scheduleVideoDownload(self):
        try:
            self.urlQueue.put(self.url_link.get(), block=False)
            self.resolutionQueue.put(self.resolution.get(), block=True)
            self.downloadScheduler.submit()
            self.youtubeObject = YouTube(self.url_link.get())
            #first try and see if a progressive stream is available
            for elem in self.youtubeObject.streams:
                print(elem)
            progressiveStream = self.youtubeObject.streams.filter(progressive=True, file_extension='mp4',
                                                                  resolution=self.resolution.get())
            if progressiveStream.first() is None:
                adaptiveStreamVideo = self.youtubeObject.streams.filter(adaptive=True, file_extension='mp4',
                                                                        resolution=self.resolution.get())
                adaptiveStreamAudio = self.youtubeObject.streams.filter(adaptive=True, file_extension='mp4',
                                                                        only_audio=True)
        except VideoPrivate as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except VideoUnavailable as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except PytubeError as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")
        except BaseException as error:
            tkinter.messagebox.showerror("YoutubeDownloaderError", f"ERROR: {error}")




GUI()