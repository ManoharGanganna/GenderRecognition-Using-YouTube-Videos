# GenderRecognition-Using-YouTube-Videos

Gender, age, language, accent, and emotional state all contribute to the voice of human speech, which is an efficient communication method containing distinct semantic linguistic and para-linguistic aspects.The project aims to use speech to recognize gender in YouTube videos. The project's design continues with the creation of a web application that takes a YouTube link and uses an audio segmentation tool to calculate the proportion of the length of Male and Female speakers in the given YouTube link.

Youtube_dl library is used to get the audio file from the YouTube link and download it in mp3 format. Then, the mp3 format audio file is converted to a Wav format file with the help of FFmpeg. The Wav format audio file is then fed into the inaspeechsegmenter API, which divides the audio file into three categories: voice, music, and noise. The voice file is used in the gender identification process.
