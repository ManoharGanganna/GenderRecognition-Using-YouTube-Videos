from threading import Thread
from flask import Blueprint, render_template, current_app, request, url_for, redirect, flash
import requests
import re
import ast
from extensions import mysql
from isodate import parse_duration
from .videodownload import video_downloader
from .audio_prediction import audio_pred
from .sendemail import send_email
import json
import boto3
import os

s3 = boto3.client('s3',
                  aws_access_key_id='secretaccesskeyid',
                  aws_secret_access_key='secretaccesskey'
                  )

BUCKET_NAME = 'flaskappvideos-genderprediction'

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
                download_cur = mysql.connection.cursor()
                download_value = download_cur.execute(
                    "SELECT prediction_results,js_results FROM prediction_data WHERE video_id = %s ",
                    (file_name,))
                if download_value > 0:
                    return redirect(url_for('.success', file=file_name, thumbnail=thumbnail))
                else:
                    video_file = file_name + '.mp4'
                    download_status = video_downloader(download_url, file_name)
                    if download_status == 'Download_complete':
                        s3.upload_file(
                            Bucket=BUCKET_NAME,
                            Filename=video_file,
                            Key=video_file
                        )
                        return redirect(url_for('.success', file=file_name, thumbnail=thumbnail))
                    else:
                        message = f"The Video Download was unsuccessful due to {download_status}"
                        flash(message)
                        return render_template('index.html')

        return render_template('index.html', videos=videos)

    else:

        return render_template('index.html')


def process_results(app, audio_location, to_mail, file_name):
    result, result1, result2 = audio_pred(audio_location)
    res_dict = {'Voice': 'Duration'}
    res_dict.update(result)
    jsr = json.dumps(result2)
    ad_file = file_name + '.mp3'
    with app.app_context():
        insert_cur = mysql.connection.cursor()
        insert_cur.execute("INSERT INTO prediction_data(video_id,prediction_results,js_results)VALUES(%s,%s,%s)",
                           (file_name, res_dict, jsr))
        mysql.connection.commit()
        insert_cur.close()
        send_email(to_mail)
        file_exists = os.path.exists(ad_file)
        if file_exists:
            os.remove(ad_file)


def show_video(bucket, videokey):
    try:
        presigned_url = s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': bucket, 'Key': videokey},
                                                  ExpiresIn=3600)
    except Exception as e:
        pass
    return presigned_url


@main.route('/success', methods=['GET', 'POST'])
def success():
    file = request.args.get("file")
    thumbnail = request.args.get("thumbnail")
    audio_file = file + '.mp3'
    video_file = file + '.mp4'
    if request.method == 'POST':
        if 'results' in request.form:
            file_exists = os.path.exists(video_file)
            if file_exists:
                os.remove(video_file)
            retrieval_cur = mysql.connection.cursor()
            resultvalue = retrieval_cur.execute(
                "SELECT prediction_results,js_results FROM prediction_data WHERE video_id = %s ",
                (file,))
            if resultvalue > 0:
                calculated_result = retrieval_cur.fetchone()
                voice_dict = calculated_result[0]
                converteddict = ast.literal_eval(voice_dict)
                jr = calculated_result[1]
                contents = show_video(BUCKET_NAME, video_file)
                return render_template('videoplayer.html', video_id=contents, data=converteddict, js_ip=jr)
                retrieval_cur.close()
            else:
                res, res1, res2 = audio_pred(audio_file)
                jsr = json.dumps(res2)
                res_dict = {'Voice': 'Duration'}
                print(res)
                res_dict.update(res)
                insert_cur = mysql.connection.cursor()
                insert_cur.execute(
                    "INSERT INTO prediction_data(video_id,prediction_results,js_results)VALUES(%s,%s,%s)",
                    (file, res_dict, jsr))
                mysql.connection.commit()
                insert_cur.close()
                file_exists = os.path.exists(audio_file)
                if file_exists:
                    os.remove(audio_file)
                contents = show_video(BUCKET_NAME, video_file)
                return render_template('videoplayer.html', video_id=contents, data=res_dict, js_ip=json.dumps(res2))
        elif 'email' in request.form:
            email = request.form.get('email')
            file_exists = os.path.exists(video_file)
            if file_exists:
                os.remove(video_file)
            if email is not None:
                retrieval_cur_email = mysql.connection.cursor()
                resultvalue = retrieval_cur_email.execute(
                    "SELECT prediction_results FROM prediction_data WHERE video_id = %s ",
                    (file,))
                if resultvalue > 0:
                    flash("The Results are already processed, click on view results")
                else:
                    flash("Email will be sent after Results are processed")
                    app = current_app._get_current_object()
                    Thread(target=process_results, args=(app, audio_file, email, file,)).start()
                    return render_template('success.html')

    return render_template('success.html')
