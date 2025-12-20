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

  /* ---------- ML RESULT ---------- */
  resultDiv.innerHTML += `
    <div class="section">
      <div class="section-title">ML Prediction</div>
      <p><strong>Possible condition:</strong> ${ml.prediction}</p>
      <p><strong>Confidence:</strong> ${ml.confidence.toFixed(1)}%</p>
    </div>
  `;

  /* ---------- IMAGE SIGNAL ---------- */
  if (ml.used_image) {
    resultDiv.innerHTML += `
      <div class="section">
        <div class="section-title">Image Used</div>
        <p>The uploaded image was used as a supporting signal.</p>
      </div>
    `;
  }

  if (data.decision_note) {
    resultDiv.innerHTML += `
      <div class="section">
        <div class="section-title">Image Insight</div>
        <p>${data.decision_note}</p>
      </div>
    `;
  }

  /* ---------- LLM / FOLLOW-UP LOGIC ---------- */
  if (data.llm) {
    if (data.llm.type === "followup") {
      resultDiv.innerHTML += `
        <div class="section followup-box">
          <div class="section-title">We need a bit more information 💬</div>
          <p>${data.llm.content}</p>
        </div>
      `;
    }

    else if (data.llm.type === "safe_mode") {
      resultDiv.innerHTML += `
        <div class="section warning">
          <div class="section-title">AI Safe Mode</div>
          <p>${data.llm.content}</p>
        </div>
      `;
    }

    else if (data.llm.type === "unavailable") {
      resultDiv.innerHTML += `
        <div class="section warning">
          <div class="section-title">AI Safe Mode</div>
          <p>AI follow-up questions are currently unavailable.</p>
        </div>
      `;
    }
  }

  /* ---------- DISCLAIMER ---------- */
  if (data.disclaimer) {
    resultDiv.innerHTML += `
      <div class="disclaimer">
        ${data.disclaimer}
      </div>
    `;
  }

  resultDiv.classList.remove("hidden");
}
