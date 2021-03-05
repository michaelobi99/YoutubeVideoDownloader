from pytube import Playlist, YouTube
from pytube.exceptions import VideoPrivate, VideoUnavailable, PytubeError
from concurrent.futures import ThreadPoolExecutor, as_completed
import ffmpeg
import subprocess
import os
from contextlib import suppress

class Download(object):
    def __init__(self):
        self.progressBar: int = 0
        self.dataEntered: int = 0
        self.isAdaptiveStream = False
    def downloadVideo(self, videoUrl, resolution, progressCanvas, title, folder):
        try:
            if videoUrl == '':
                raise BaseException("No url provided")
            self.progressCanvas = progressCanvas
            self.title = title
            self.folder = str(folder)
            if 'playlist' in videoUrl or 'list' in videoUrl and 'index' not in videoUrl:
                urlList = Playlist(videoUrl).video_urls
                for url in urlList:
                    youtubeObject = YouTube(url, on_progress_callback=self.showDownloadProgress)
                    self.startDownload(youtubeObject, resolution)
                    self.resetValues()
            else:
                #no need for download complete callback since it is already in one file
                youtubeObject = YouTube(videoUrl, on_progress_callback=self.showDownloadProgress)
                # first try and see if a progressive stream is available
                self.startDownload(youtubeObject, resolution)
                self.resetValues()

        except VideoPrivate as error:
            raise error
        except VideoUnavailable as error:
            raise error
        except PytubeError as error:
            raise error
        except BaseException as error:
            raise error

    def resetValues(self):
        self.title.set('None')
        self.progressCanvas.delete("progress")
        self.progressCanvas.update()
        self.progressBar = 0
        self.dataEntered = 0

    def startDownload(self, youtubeObject, resolution):
        global downloadOngoing
        try:
            progressiveStream = youtubeObject.streams.filter(progressive=True, file_extension='mp4',
                                                             resolution=resolution)
            #if there is no progressive download available
            if progressiveStream.first() is None:
                self.isAdaptiveStream = True
                adaptiveDownloadList = []
                adaptiveStreamVideo = youtubeObject.streams.filter(adaptive=True, file_extension='mp4',
                                                                   resolution=resolution)
                adaptiveStreamAudio = youtubeObject.streams.filter(adaptive=True, file_extension='mp4',
                                                                   only_audio=True)
                if adaptiveStreamVideo.first() is None:
                    raise BaseException("Selected resolution not found")
                else:
                    self.title.set(f'{youtubeObject.title}')
                    self.videoTitle = str(self.title.get()) + '_video' + '.mp4'
                    self.audioTitle = str(self.title.get()) + '_audio' + '.mp4'
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        adaptiveDownloadList.append(executor.submit(lambda: adaptiveStreamVideo.first().download(
                            output_path=self.folder, filename= self.videoTitle.replace('.mp4', '')
                        )))
                        adaptiveDownloadList.append(executor.submit(lambda: adaptiveStreamAudio.first().download(
                            output_path=self.folder, filename= self.audioTitle.replace('.mp4', '')
                        )))
                    for future in as_completed(adaptiveDownloadList):
                        future.result()

                    self.mergeFiles()
                    self.deleteFiles()
            else:
                self.title.set(youtubeObject.title)
                progressiveStream.first().download(output_path=self.folder)
        except VideoPrivate as error:
            raise error
        except VideoUnavailable as error:
            raise error
        except PytubeError as error:
            raise error
        except FileNotFoundError as error:
            raise error
        except BaseException as error:
            raise error

    def showDownloadProgress(self, stream, data_chunk, data_remaining):
        with suppress(ZeroDivisionError):
            self.dataEntered += len(data_chunk)
            self.progressBar = int((self.dataEntered / data_remaining) * 600)
            self.progressCanvas.delete("progress")
            self.progressCanvas.update()
            self.progressCanvas.create_rectangle(0, 0, self.progressBar, 15, fill="cyan", tags="progress")
            self.progressCanvas.update()


    def mergeFiles(self):
        self.title.set(f'Merging files...please wait')
        self.paths = []
        files = os.listdir(self.folder)
        for file in files:
            if file.endswith('_video.mp4'):
                self.paths.append(file)
        for file in files:
            if file.endswith('_audio.mp4'):
                self.paths.append(file)
        videoFilePath = ffmpeg.input(os.path.join(self.folder, self.paths[0]))
        audioFilePAth = ffmpeg.input(os.path.join(self.folder, self.paths[1]))
        filePath = os.path.join(self.folder, self.paths[0].replace('_video', ''))
        if os.path.basename(filePath) in files:
            os.unlink(os.path.join(self.folder, filePath))
        vcodec = "copy"
        acodec = "aac"
        out = ffmpeg.output(videoFilePath, audioFilePAth, filePath, vcodec=vcodec, acodec=acodec, strict='experimental')
        out.run()

    def deleteFiles(self):
        with suppress(BaseException):
            os.unlink(os.path.join(self.folder, self.paths[0]))
            os.unlink(os.path.join(self.folder, self.paths[1]))



