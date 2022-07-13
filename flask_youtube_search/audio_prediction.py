from __future__ import unicode_literals
from inaSpeechSegmenter import Segmenter


def audio_pred(audio):
    seg = Segmenter()
    segmentation = seg(audio)
    initial_dict = dict()
    print(segmentation)
    total_time = segmentation[-1][-1]
    voice_list = []
    percent_list = []
    percent = 0
    for voice_type, start_time, end_time in segmentation:
        initial_dict.setdefault(voice_type, []).append(end_time - start_time)
        percent += round(((end_time - start_time) / total_time) * 100)
        percent_list.append(percent)
        voice_list.append(voice_type)

    zipped = zip(voice_list, percent_list)
    voice_percent_lst = list(zipped)
    result_dict1 = dict(zip(initial_dict.keys(), [round(sum(item)) for item in initial_dict.values()]))
    result_dict = {'No Audio' if k == 'noEnergy' else k: v for k, v in result_dict1.items()}
    return result_dict, voice_percent_lst
