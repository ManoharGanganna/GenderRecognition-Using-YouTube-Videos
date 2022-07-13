from flask import Blueprint, render_template, current_app, request, url_for, redirect, flash
import requests
from isodate import parse_duration
from .videodownload import video_downloader
from .audio_prediction import audio_pred
import re
import os

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    videos = []

    if request.method == 'POST':
        if request.form.get('query') != '':
            search_params = {
                'key': current_app.config['YOUTUBE_API_KEY'],
                'q': request.form.get('query'),
                'part': 'snippet',
                'maxResults': 9,
                'type': 'video'
            }

            r = requests.get(search_url, params=search_params)

            results = r.json()['items']

            video_ids = []
            for result in results:
                video_ids.append(result['id']['videoId'])

            video_params = {
                'key': current_app.config['YOUTUBE_API_KEY'],
                'id': ','.join(video_ids),
                'part': 'snippet,contentDetails',
                'maxResults': 9
            }

            r = requests.get(video_url, params=video_params)

            results = r.json()['items']

            for result in results:
                video_data = {
                    'id': result['id'],
                    'url': f'https://www.youtube.com/watch?v={result["id"]}',
                    'thumbnail': result['snippet']['thumbnails']['high']['url'],
                    'duration': parse_duration(result['contentDetails']['duration']).total_seconds() // 60,
                    'title': result['snippet']['title'],

                }
                videos.append(video_data)

            if 'download' in request.form:
                download_url = request.form.get('download')
                thumbnail = request.form.get('thumbnail')
                file_name_url = re.search(r"[^v=]*$", download_url)
                file_name = file_name_url.group()
                download_status = video_downloader(download_url, file_name)
                if download_status == 'Download_complete':
                    return redirect(url_for('.success', file=file_name, thumbnail=thumbnail))
                else:
                    message = f"The Video Download was unsuccessful due to {download_status}"
                    flash(message)
                    return render_template('index.html')

        return render_template('index.html', videos=videos)

    else:

        return render_template('index.html')


@main.route('/success', methods=['GET', 'POST'])
def success():
    file = request.args.get("file")
    thumbnail = request.args.get("thumbnail")
    cwd = os.getcwd()
    static_file_path = os.path.join(cwd, 'static')
    audio_file_path = os.path.join(static_file_path, 'audios')
    audio_file = file + '.mp3'
    video_file = file + '.mp4'
    audio_loc = os.path.join(audio_file_path, audio_file)
    if request.method == 'POST':
        res, res1 = audio_pred(audio_loc)
        vd_file = 'videos/' + video_file
        print('routes',res1)
        res_dict = {'Voice': 'Duration'}
        res_dict.update(res)
        print('b', res_dict)
        return render_template('piechart.html', data=res_dict)
    return render_template('success.html')
