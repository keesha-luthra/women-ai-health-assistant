async function submitSymptoms() {
  const input = document.getElementById("symptomsInput");
  const imageInput = document.getElementById("imageInput");
  const resultDiv = document.getElementById("result");

  const symptoms = input.value.trim();
  if (!symptoms) {
    alert("Please describe your symptoms.");
    return;
  }

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<em>Loading...</em>";

  const formData = new FormData();
  formData.append("symptoms", symptoms);

  if (imageInput && imageInput.files.length > 0) {
    formData.append("image", imageInput.files[0]);
  }

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Request failed");
    }

    const data = await response.json();
    displayResult(data);
  } catch (error) {
    resultDiv.innerHTML = "Something went wrong. Please try again.";
  }
}

function displayResult(data) {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = "";

  if (!data || !data.ml_result) {
    resultDiv.innerHTML = "Unexpected response from server.";
    return;
  }

  const ml = data.ml_result;

  resultDiv.innerHTML += `
    <div class="label">Possible condition:</div>
    <div>${ml.prediction}</div>

    <div class="label">Confidence:</div>
    <div>${ml.confidence}</div>
  `;

  if (ml.used_image) {
    resultDiv.innerHTML += `
      <div class="label">Image used:</div>
      <div>Yes (as a supporting signal)</div>
    `;
  }

  if (data.decision_note) {
    resultDiv.innerHTML += `
      <div class="label">Image insight:</div>
      <div>${data.decision_note}</div>
    `;
  }

  if (data.llm && data.llm.type !== "unavailable") {
    resultDiv.innerHTML += `
      <div class="label">Additional guidance:</div>
      <div>${data.llm.content}</div>
    `;
  }

  if (data.disclaimer) {
    resultDiv.innerHTML += `
      <div class="disclaimer">${data.disclaimer}</div>
    `;
  }

  resultDiv.classList.remove("hidden");
}
