# spec2spec Notebooks

This folder stores the Jupyter Notebooks that were used to train our spec2spec models or process source data.

The notebooks certainly contains audio output of training results, however we are aware that Visual Studio Code + Jupyter Notebook extension is unable to play them. You may need to set up a proper Jupyter environment to play them; or, you may use a Google account and upload the notebook to Google Colab to be able to play the audio output.

- `preprocess.ipynb`: Converts source MIDI to a pair of audio files with different instruments; may require fluidsynth, please check the notebook for more details
- `spec2spec40000.ipynb`: The notebook to train the first spec2spec model, which is the piano2violin model
- `piano2guitar.ipynb`: The notebook for training a piano2guitar model
- `guitar2eguitar.ipynb`: The notebook for training a guitar2eguitar model
- `piano2flute.ipynb`: The notebook for training a piano2flute model
