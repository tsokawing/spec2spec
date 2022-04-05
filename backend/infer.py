import librosa
import librosa.display
import numpy as np
import tensorflow as tf
import soundfile as sf
import matplotlib.pyplot as plt

SPEC2SPEC_MODEL_PATH = 'model'

# To obtain the best results, we use a sampling rate and a duration
# identical to those used in training.
SAMPLING_RATE = 22050
DURATION = 5.94


class Spec2spec:
    def __init__(self):
        self.saved_path = SPEC2SPEC_MODEL_PATH
        self.model = tf.saved_model.load(self.saved_path)

    def infer(self, audio=None):
        tensor_image = self.preprocess(audio)

        # Input images are 3 dimensional (256, 256, 1), but model expects 4 (None, 256, 256, 1).
        # Therefore we reshape the tensor image to match.
        shape = tensor_image.shape
        tensor_image = tf.reshape(tensor_image, [1, shape[0], shape[1], shape[2]])

        # Our model, which is pix2pix based, requires training=True even for prediction.
        pred_image = self.model(tensor_image, training=True)

        # Only the 256x256 dimensions contain our prediction data, the spectrogram.
        # We remove the first and last dimensions from (None, 256, 256, 1) here.
        squeezed = tf.squeeze(pred_image[0, ...])

        # Convert to numpy array as librosa does not work with tf arrays.
        pred_spec = np.array(self.denormalize(squeezed))
        pred_audio = recover_audio(pred_spec)
        return pred_spec, pred_audio

    def preprocess(self, audio):
        spec = to_melspectrogram(audio)
        normalized = self.normalize(spec)
        expanded = tf.expand_dims(normalized, axis=2)
        return expanded

    @staticmethod
    def normalize(spec):
        spec = (spec - 127.5) / 127.5
        return spec

    @staticmethod
    def denormalize(spec):
        spec = spec * 127.5 + 127.5
        return spec


def load_audio(path):
    audio, _ = librosa.load(path, duration=DURATION, sr=SAMPLING_RATE)
    return audio


def save_audio(path, audio, sampling_rate=SAMPLING_RATE):
    sf.write(path, audio, sampling_rate, 'PCM_24')


def to_melspectrogram(audio):
    spec = librosa.feature.melspectrogram(y=audio, sr=SAMPLING_RATE, n_mels=256)
    return spec


def save_melspectrogram(spec, path):
    fig, ax = plt.subplots(frameon=False)
    ax.set_axis_off()
    audio_db = librosa.power_to_db(spec, ref=np.max)
    librosa.display.specshow(audio_db, sr=SAMPLING_RATE, fmax=8000, ax=ax, cmap='magma')
    fig.savefig(path, bbox_inches='tight', pad_inches=0)


def recover_audio(melspectrogram):
    stft = librosa.feature.inverse.mel_to_stft(melspectrogram, sr=SAMPLING_RATE)
    audio = librosa.griffinlim(stft)
    return audio


def test():
    audio = load_audio('uploads/test.wav')
    # pred_spec, pred_audio = Spec2spec().infer(audio)
    # save_audio('output/test.wav', pred_audio)
    save_melspectrogram(to_melspectrogram(audio), 'output/test.png')


if __name__ == '__main__':
    test()
