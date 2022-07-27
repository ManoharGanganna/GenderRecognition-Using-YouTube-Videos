from flask import Blueprint, render_template, current_app, request, url_for, redirect, flash
import requests
import re
import os
import ast
# import redis
# from rq import Queue
from isodate import parse_duration
from .videodownload import video_downloader
from .audio_prediction import audio_pred
from extensions import mysql
from .sendemail import send_email


main = Blueprint('main', __name__)

# r = redis.Redis()
# q = Queue(connection=r)

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


def process_results(audio_location, to_mail, file_name):
    result, result1 = audio_pred(audio_location)
    res_dict = {'Voice': 'Duration'}
    res_dict.update(result)
    insert_cur_email = mysql.connection.cursor()
    insert_cur_email.execute("INSERT INTO prediction_data(video_id,prediction_results)VALUES(%s,%s)",
                             (file_name, res_dict))
    mysql.connection.commit()
    insert_cur_email.close()
    send_email(to_mail)


@main.route('/success', methods=['GET', 'POST'])
def success():
    file = request.args.get("file")
    thumbnail = request.args.get("thumbnail")
    cwd = os.getcwd()
    static_file_path = os.path.join(cwd, 'static')
    audio_file_path = os.path.join(static_file_path, 'audios')
    audio_file = file + '.mp3'
    video_file = file + '.mp4'
    vd_file = 'videos/' + video_file
    audio_loc = os.path.join(audio_file_path, audio_file)
    if request.method == 'POST':
        if 'results' in request.form:
            retrieval_cur = mysql.connection.cursor()
            resultvalue = retrieval_cur.execute("SELECT prediction_results FROM prediction_data WHERE video_id = %s ",
                                                (file,))
            if resultvalue > 0:
                calculated_result = retrieval_cur.fetchone()
                for dict1 in calculated_result:
                    voice_dict = dict1
                converteddict = ast.literal_eval(voice_dict)
                return render_template('videoplayer.html', video_id=vd_file, data=converteddict)
                retrieval_cur.close()
            else:
                res, res1 = audio_pred(audio_loc)
                res_dict = {'Voice': 'Duration'}
                res_dict.update(res)
                insert_cur = mysql.connection.cursor()
                insert_cur.execute("INSERT INTO prediction_data(video_id,prediction_results)VALUES(%s,%s)",
                                   (file, res_dict))
                mysql.connection.commit()
                insert_cur.close()
                return render_template('videoplayer.html', video_id=vd_file, data=res_dict)
        elif 'email' in request.form:
            email = request.form.get('email')
            if email is not None:
                print('a')
                retrieval_cur_email = mysql.connection.cursor()
                resultvalue = retrieval_cur_email.execute(
                    "SELECT prediction_results FROM prediction_data WHERE video_id = %s ",
                    (file,))
                if resultvalue > 0:
                    print('b')
                    flash("The Results are already processed, click on view results")
                else:
                    flash("Email will be sent after Results are processed")
                    process_results(audio_loc, email, file)
                    return render_template('success.html')

    return render_template('success.html')
