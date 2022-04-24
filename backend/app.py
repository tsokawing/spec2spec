import os
import shutil

from flask import Flask, request, send_file
from infer import Spec2spec, load_audio, save_audio, to_melspectrogram, save_melspectrogram
import datetime
import gdown

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def init():
    remake_models_folder()
    # init the stuff: download from google drive
    download_from_gdrive('1fIwwUHbalNsY4pXwiZbBzN7frrU5VfEC', 'model/variables/variables.data-00000-of-00001')
    download_from_gdrive('1WI1eyYKCjk1duE3XFOai1uOVls-VNGxL', 'model/variables/variables.index')
    download_from_gdrive('1eASWc81Xpf_S_wjc3qsCIDH44keg9bAr', 'model/saved_model.pb')


def remake_models_folder():
    proj_root_dir = os.path.dirname(__file__)
    for path in [f'{proj_root_dir}/model', f'{proj_root_dir}/model/variables']:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)


def download_from_gdrive(gdrive_id: str, output: str):
    proj_root_dir = os.path.dirname(__file__)
    url_path = f'https://drive.google.com/uc?id={gdrive_id}'
    gdown.download(url_path, proj_root_dir + '/' + output)
    pass


init()
spec2spec = Spec2spec()

# files are allowed max 15 minutes of existence in our server
app.config['FILE_TIMEOUT_SECONDS'] = 15 * 60


def is_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_old_files():
    proj_root_dir = os.path.dirname(__file__)
    now_time = datetime.datetime.now()
    # deletes old files that are too old; both uploads and outputs
    for dir_name in ['uploads', 'output']:
        full_dir_name = proj_root_dir + '/' + dir_name
        for file_name in os.listdir(full_dir_name):
            if not os.path.isfile(full_dir_name + '/' + file_name):
                # not a file
                continue
            # is a file, check whether it matches
            base_name = os.path.split(file_name)[1]
            need_delete = False
            # it is always eg upload_2022_04_01_12_34_56.wav
            # in general, [type]_[timestamp].[filetype]
            try:
                components = [int(x) for x in base_name.split('.')[0].split('_')[1:7]]
                file_stamp = datetime.datetime(components[0], components[1], components[2], components[3],
                                               components[4], components[5])
                age = now_time - file_stamp
                if age.total_seconds() <= app.config['FILE_TIMEOUT_SECONDS']:
                    # not old enough
                    continue
                # delete the file!
                os.remove(full_dir_name + '/' + file_name)
            except Exception:
                # does not match
                continue


@app.route('/', methods=['GET'])
def basic_reply():
    # to show that it works without loading any fancy
    return 'OK'


@app.route('/predict', methods=['POST'])
def predict():
    # Check if the post request has the file part.
    remove_old_files()
    if 'audio_data' not in request.files:
        return 'No files uploaded'

    file = request.files['audio_data']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return 'No filename'

    if file and is_allowed(file.filename):
        proj_root_dir = os.path.dirname(__file__)
        now_time = datetime.datetime.now()
        # hopefully this is sufficient
        time_string_comp = f'{now_time.year}_{str(now_time.month).zfill(2)}_{str(now_time.day).zfill(2)}' \
                           f'_{str(now_time.hour).zfill(2)}_{str(now_time.minute).zfill(2)}_{str(now_time.second).zfill(2)}'

        # Write file to the disk then read to predict.
        # May be too slow, better to read file objects directly without disk I/O.
        in_path = os.path.join(proj_root_dir, app.config['UPLOAD_FOLDER'], f'upload_{time_string_comp}.wav')
        file.save(in_path)

        # Predict.
        audio = load_audio(in_path)
        pred_spec, pred_audio = spec2spec.infer(audio)

        # Save spectrogram of both the input and output audio.
        in_spec = to_melspectrogram(audio)
        in_spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], f'input_{time_string_comp}.png')
        save_melspectrogram(in_spec, in_spec_path)
        out_spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], f'output_{time_string_comp}.png')
        save_melspectrogram(pred_spec, out_spec_path)

        # Save output audio.
        out_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], f'output_{time_string_comp}.wav')
        save_audio(out_path, pred_audio)
        return time_string_comp

    return 'No file or file not supported'


@app.route('/outwav', methods=['GET'])
def get_output_audio():
    remove_old_files()
    proj_root_dir = os.path.dirname(__file__)
    spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], 'output.wav')
    if 'time_code' in request.args:
        # load the specific file
        file_name = f'output_{request.args.get("time_code")}.wav'
        spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], file_name)
    return send_file(spec_path)


@app.route('/inspec', methods=['GET'])
def get_input_spectrogram():
    remove_old_files()
    proj_root_dir = os.path.dirname(__file__)
    spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], 'input.png')
    if 'time_code' in request.args:
        # load the specific file
        file_name = f'input_{request.args.get("time_code")}.png'
        spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], file_name)
    return send_file(spec_path)


@app.route('/outspec', methods=['GET'])
def get_prediction_spectrogram():
    remove_old_files()
    proj_root_dir = os.path.dirname(__file__)
    spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], 'output.png')
    if 'time_code' in request.args:
        # load the specific file
        file_name = f'output_{request.args.get("time_code")}.png'
        spec_path = os.path.join(proj_root_dir, app.config['OUTPUT_FOLDER'], file_name)
    return send_file(spec_path)


if __name__ == '__main__':
    app.run()
