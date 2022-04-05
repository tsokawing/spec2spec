import os
from flask import Flask, request, send_file
from infer import Spec2spec, load_audio, save_audio, to_melspectrogram, save_melspectrogram

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
spec2spec = Spec2spec()


def is_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
