from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import sys, json, logging
import os

os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
import generate_story
from moviepy.config import change_settings
from logging.config import dictConfig

change_settings({"FFMPEG_BINARY": "/opt/homebrew/bin/ffmpeg"})
# change_settings({"FFMPEG_BINARY": "/usr/bin/ffmpeg"})

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/storage/"


@app.route('/health')
def say_hello():
    return 'OK'


@app.route('/api/v1/generate', methods=['POST'])
def generate():
    print(request.json)
    logging.info('got generate story request: {}'.format(request.json))

    output_file = generate_story.generate_story_video_from_config(request.json)
    if output_file is None:
        return jsonify({'error': {'id': '1', 'message': 'cannot generate video'}}), 500

    return jsonify({'video': {'type': 'file', 'file_name': output_file}})

@app.route('/videos/<path:path>')
def send_report(path):
    return send_from_directory('storage/video/generated/8c3de4dd', path)