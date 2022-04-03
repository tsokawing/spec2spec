const inputAudio = document.getElementsByTagName("audio")[0];
const predAudio = document.getElementsByTagName("audio")[1];

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

  const predictURL = "http://127.0.0.1:5000/predict";
  const formData = new FormData();
  formData.append("audio_data", file);

  fetch(predictURL, {
    method: "POST",
    body: formData,
  })
    .then((res) => {
      console.log(res.body);
      return res.body;
    })
    .then((stream) => new Response(stream))
    .then((response) => response.blob())
    .then((blob) => URL.createObjectURL(blob))
    .then((url) => {
      console.log((predAudio.src = url));
      stopLoadingAnimation();
    })
    .catch((err) => console.error(err));
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
