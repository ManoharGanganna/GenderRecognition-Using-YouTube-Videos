from __future__ import unicode_literals
import youtube_dl
import moviepy.editor as mp


def video_downloader(url, filename):
    ydl_opts = {'outtmpl': filename + '.%(ext)s',
                'format': 'mp4'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    video = filename + '.mp4'
    audio = filename + '.mp3'
    my_clip = mp.VideoFileClip(video)
    my_clip.audio.write_audiofile(audio)
