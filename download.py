from pytube import Playlist, YouTube
from pytube.exceptions import VideoPrivate, VideoUnavailable, PytubeError
from concurrent.futures import ThreadPoolExecutor, as_completed

class Download(object):
    def __init__(self):
        self.downloadOngoing = False
        self.dataEntered: int = 0 #used for monitoring data chunk entered
    def downloadVideo(self, videoUrl, resolution, progressBar, title, folder):
        try:
            self.progressBar = progressBar
            self.title = title
            self.folder = str(folder)
            if 'playlist' in videoUrl or 'list' in videoUrl:
                urlList = Playlist(videoUrl).video_urls
                for url in urlList:
                    youtubeObject = YouTube(url, on_progress_callback=self.showDownloadProgress,
                                            on_complete_callback=self.mergeFiles)
                    self.startDownload(youtubeObject, resolution)
            else:
                #no need for download complete callback since it is already in one file
                youtubeObject = YouTube(videoUrl, on_progress_callback=self.showDownloadProgress)
                # first try and see if a progressive stream is available
                self.startDownload(youtubeObject, resolution)
        except VideoPrivate as error:
            raise error
        except VideoUnavailable as error:
            raise error
        except PytubeError as error:
            raise error
        except BaseException as error:
            raise error

    def startDownload(self, youtubeObject, resolution):
        global downloadOngoing
        try:
            progressiveStream = youtubeObject.streams.filter(progressive=True, file_extension='mp4',
                                                             resolution=resolution)
            #if there is no progressive download available
            if progressiveStream.first() is None:
                adaptiveDownloadList = []
                adaptiveStreamVideo = youtubeObject.streams.filter(adaptive=True, file_extension='mp4',
                                                                   resolution=resolution)
                adaptiveStreamAudio = youtubeObject.streams.filter(adaptive=True, file_extension='mp4',
                                                                   only_audio=True)
                with ThreadPoolExecutor(max_workers=2) as executor:
                    adaptiveDownloadList.append(executor.submit(lambda: adaptiveStreamAudio.first().download(
                        output_path=self.folder
                    )))
                    adaptiveDownloadList.append(executor.submit(lambda: adaptiveStreamVideo.first().download(
                        output_path=self.folder
                    )))
                self.title.set(youtubeObject.title)
                self.downloadOngoing = True
                for future in as_completed(adaptiveDownloadList):
                    future.result()
            else:
                self.title.set(youtubeObject.title)
                self.downloadOngoing = True
                progressiveStream.first().download(output_path=self.folder)
        except VideoPrivate as error:
            self.downloadOngoing = False
            raise error
        except VideoUnavailable as error:
            self.downloadOngoing = False
            raise error
        except PytubeError as error:
            self.downloadOngoing = False
            raise error
        except BaseException as error:
            self.downloadOngoing = False
            raise error

    def showDownloadProgress(self, stream, data_chunk, data_remaining):
        pass
        #self.dataEntered += int(data_chunk)
        #lengthOfProgressBar = (self.dataEntered // int(data_remaining)) * 100
        #self.progressBar["value"] = lengthOfProgressBar
        #self.progressBar.update()

    def mergeFiles(self, stream, folder):
        pass