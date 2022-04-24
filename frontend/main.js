const SERVER_URL =
  "http://ec2-18-191-140-64.us-east-2.compute.amazonaws.com:5000/";

const inputAudio = document.getElementsByTagName("audio")[0];
const predAudio = document.getElementsByTagName("audio")[1];

const inputSpec = document.getElementById("input-spec");
const outputSpec = document.getElementById("output-spec");

const input = document.getElementById("upload");

// To fire onchange event even if the chosen file name does not change.
input.onclick = function () {
  this.value = "";
};

input.addEventListener("change", (e) => {
  // Change audio player source to the chosen file.
  const file = e.target.files[0];
  inputAudio.src = URL.createObjectURL(file);

  // Send POST request to server for prediction.
  sendPredictRequest(file);
});

function sendPredictRequest(file) {
  startLoadingAnimation();

  const predictURL = SERVER_URL + "predict";
  const formData = new FormData();
  formData.append("audio_data", file);

  fetch(predictURL, {
    method: "POST",
    body: formData,
  })
    .then((res) => {
      // The POST response will be the magic timecode to get subsequent stuff
      return res.body;
    })
    .then((stream) => new Response(stream))
    .then((response) => response.text())
    .then((time_code) => {
      const regexTimeCode = new RegExp("[0-9]{4}_[0-9]{2}_[0-9]{2}");
      if (regexTimeCode.test(time_code)) {
        // regex match it, it should at least look like a time code
        // whether it actually exists, we can leave to backend
        getSpectrograms(time_code);
        getPredictionResult(time_code);
      }
    })
    .catch((err) => console.error(err));
}

function getPredictionResult(time_code) {
  const obtainURL = SERVER_URL + "outwav";
  fetch(obtainURL + "?time_code=" + time_code)
    .then((res) => {
      // The GET response will be the prediction wav
      return res.body;
    })
    .then((stream) => new Response(stream))
    .then((response) => response.blob())
    .then((blob) => URL.createObjectURL(blob))
    .then((url) => {
      predAudio.src = url;
    })
    .catch((err) => console.error(err));
}

function getSpectrograms(time_code) {
  Promise.all([
    fetch(SERVER_URL + "inspec?time_code=" + time_code),
    fetch(SERVER_URL + "/outspec?time_code=" + time_code),
  ])
    .then((responses) =>
      Promise.all(responses.map((response) => response.body))
    )
    .then((streams) => {
      new Response(streams[0]).blob().then((blob) => {
        const inputSpecUrl = URL.createObjectURL(blob);
        inputSpec.src = inputSpecUrl;
      });
      new Response(streams[1]).blob().then((blob) => {
        const outputSpecUrl = URL.createObjectURL(blob);
        outputSpec.src = outputSpecUrl;
      });
      stopLoadingAnimation();
    })
    .catch((err) => console.log(err));
}

function startLoadingAnimation() {
  document.getElementsByClassName("loader")[0].style.display = "block";
  document.getElementsByClassName("fa-arrow-right-long")[0].style.display =
    "none";
}

function stopLoadingAnimation() {
  document.getElementsByClassName("loader")[0].style.display = "none";
  document.getElementsByClassName("fa-arrow-right-long")[0].style.display =
    "block";
}
