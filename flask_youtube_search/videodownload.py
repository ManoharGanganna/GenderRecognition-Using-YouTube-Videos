from __future__ import unicode_literals
import yt_dlp
import moviepy.editor as mp


def video_downloader(url, filename):
    ydl_opts = {'outtmpl': filename + '.%(ext)s',
                'format': 'mp4',
                }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            video = filename + '.mp4'
            audio = filename + '.mp3'
            my_clip = mp.VideoFileClip(video)
            my_clip.audio.write_audiofile(audio)
            return 'Download_complete'
        except yt_dlp.DownloadError as e:
            return e
