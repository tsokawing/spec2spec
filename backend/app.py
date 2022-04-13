import os
from flask import Flask, request, send_file
from infer import Spec2spec, load_audio, save_audio, to_melspectrogram, save_melspectrogram
import datetime

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
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
    pass

@app.route('/predict', methods=['POST'])
def predict():
    # Check if the post request has the file part.
    if 'audio_data' not in request.files:
        return 'No files uploaded'

    file = request.files['audio_data']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return 'No filename'

    if file and is_allowed(file.filename):
        # Write file to the disk then read to predict.
        # May be too slow, better to read file objects directly without disk I/O.
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], 'upload.wav')
        file.save(in_path)

        # Predict.
        audio = load_audio(in_path)
        pred_spec, pred_audio = spec2spec.infer(audio)

        # Save spectrogram of both the input and output audio.
        in_spec = to_melspectrogram(audio)
        in_spec_path = os.path.join(app.config['OUTPUT_FOLDER'], 'input.png')
        save_melspectrogram(in_spec, in_spec_path)
        out_spec_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.png')
        save_melspectrogram(pred_spec, out_spec_path)

        # Save output audio.
        out_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.wav')
        save_audio(out_path, pred_audio)
        return send_file(out_path)

    return 'No file or file not supported'


@app.route('/inspec', methods=['GET'])
def get_input_spectrogram():
    spec_path = os.path.join(app.config['OUTPUT_FOLDER'], 'input.png')
    return send_file(spec_path)


@app.route('/outspec', methods=['GET'])
def get_prediction_spectrogram():
    spec_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.png')
    return send_file(spec_path)


if __name__ == '__main__':
    app.run()
