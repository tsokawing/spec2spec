# spec2spec demo Backend

This is the folder containing the backend code for spec2spec demo. It is built using Python with the Flask library along with other python libraries.

This requires Python 3. Further requirements are specified in `requirements.txt`.

## The Virtual Environment

The backend utilizes the Python virtual environment. Refer to the official tutorial for more details: https://docs.python.org/3/tutorial/venv.html

It is optional to use the virtual environment, but we recommend using it to maintain maximum compatibility with other Python projects on your local machine.

it was noticed that on Windows 11 PowerShell, the system may refuse to activate the virtual environment due to a strict safety mechanism on script execution. In that case, you may execute the following before activating the virtual environment in the PowerShell command line:

```
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

This allows the current PowerShell session to execute foreign scripts such as the one used to activate the virtual environment. 

## Installing the requirements

After activating the virtual environment, continue by installing the required Python libraries written at `requirements.txt`:

```
pip install -r requirements.txt
```

## Launching the backend

Launch the backend using:

```
python3 app.py
```

When the backend starts, it will download 3 files to the `/model` directory. These files are the pix2pix model files for the backend to generate music. Their large size meant that it was not possible to commit them to GitHub, and deployment was difficult. It was later settled to host them somewhere else but download them on demand when the backend starts.

After downloading the files, the backend should bind to `127.0.0.1:5000`.

Verify its status by sending a request to `127.0.0.1:5000`, and you should get this simple response:

```
OK
```

Then your backend is ready to listen to requests from the frontend.
