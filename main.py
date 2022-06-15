from __future__ import unicode_literals
import youtube_dl
import os
from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter.export_funcs import seg2csv, seg2textgrid
import subprocess

name = 'audio'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': name + '.%(ext)s',
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=znePvsR-Nvs'])

media = 'audio.wav'

seg = Segmenter()

segmentation = seg(media)

print(segmentation)
# speech_segment_index = 0

# for segment in segmentation:
# segment_label = segment[0]
# print(segment_label)
# os.remove('audio.wav')
# seg2csv(segmentation, 'test.csv')
