from __future__ import unicode_literals
import yt_dlp
import moviepy.editor as mp
import os


def video_downloader(url, filename):
    cwd = os.getcwd()
    static_file_path = os.path.join(cwd, 'static')
    audio_file_path = os.path.join(static_file_path, 'audios')
    video_file_path = os.path.join(static_file_path, 'videos')
    ydl_opts = {'outtmpl': os.path.join(video_file_path, filename + '.%(ext)s'),
                'format': 'mp4',
                }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            video = filename + '.mp4'
            audio = filename + '.mp3'
            video_loc = os.path.join(video_file_path, video)
            audio_loc = os.path.join(audio_file_path, audio)
            my_clip = mp.VideoFileClip(video_loc)
            my_clip.audio.write_audiofile(audio_loc)
            return 'Download_complete'
        except yt_dlp.DownloadError as e:
            return e
