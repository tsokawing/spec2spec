import os
from flask import Flask, request, send_file
from infer import Spec2spec, load_audio, save_audio

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'wav'}

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

        audio = load_audio(in_path)
        pred_spec, pred_audio = spec2spec.infer(audio)
        out_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.wav')
        save_audio(out_path, pred_audio)
        return send_file(out_path)

    return 'No file or file not supported'


if __name__ == '__main__':
    app.run()
