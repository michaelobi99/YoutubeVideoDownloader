from pytube import Playlist, YouTube
from pytube.exceptions import VideoPrivate, VideoUnavailable, PytubeError
from concurrent.futures import ThreadPoolExecutor, as_completed
import ffmpeg
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
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        self.getFileSize(adaptiveStreamVideo.first().filesize)
                        adaptiveDownloadList.append(executor.submit(lambda: adaptiveStreamVideo.first().download(
                            output_path=self.folder, filename= self.videoTitle.replace('.mp4', '')
                        )))
                        adaptiveDownloadList.append(executor.submit(lambda: adaptiveStreamAudio.first().download(
                            output_path=self.folder, filename= self.audioTitle.replace('.mp4', '')
                        )))
                    for future in as_completed(adaptiveDownloadList):
                        future.result()

                    self.mergeFiles()
            else:
                self.title.set(youtubeObject.title)
                self.getFileSize(progressiveStream.first().filesize)
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
        videoFilePath = os.path.join(self.folder, self.videoTitle)
        audioFilePAth = os.path.join(self.folder, self.audioTitle)
        destinationPath = videoFilePath.replace("_video", '')
        print(os.path.join(self.folder, destinationPath))
        if self.isAdaptiveStream:
            self.title.set('merging downloaded files, please wait...')
            inputVideo = ffmpeg.input(videoFilePath)
            inputAudio = ffmpeg.input(audioFilePAth)
            joinFile = ffmpeg.concat(
                inputVideo, inputAudio, v=1, a=1
            )
            joinFile.output(destinationPath).run()
        os.unlink(videoFilePath)
        os.unlink(audioFilePAth)



