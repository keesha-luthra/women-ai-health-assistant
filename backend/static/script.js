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
  resultDiv.innerHTML = "<em>Analyzing...</em>";

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
    renderResult(data);

  } catch (error) {
    resultDiv.innerHTML = "Something went wrong. Please try again.";
  }
}

/* ---------------- CONFIDENCE LABEL ---------------- */

function confidenceLabel(confidence) {
  if (confidence >= 0.75) return "High";
  if (confidence >= 0.6) return "Moderate";
  return "Low";
}

/* ---------------- RENDER RESULT ---------------- */

function renderResult(data) {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = "";

  if (!data || !data.ml_result) {
    resultDiv.innerHTML = "Unexpected response from server.";
    return;
  }

  const ml = data.ml_result;

  // ✅ Backend already gives 0–1 confidence
  const confidencePct = (ml.confidence * 100).toFixed(1);
  const confidenceText = confidenceLabel(ml.confidence);

  /* ---------- MODEL ASSESSMENT ---------- */
  resultDiv.innerHTML += `
    <div class="section">
      <div class="section-title">Model Assessment</div>
      <p><strong>Possible condition:</strong> ${ml.prediction}</p>
      <p>
        <strong>Confidence:</strong>
        ${confidenceText} (${confidencePct}%)
      </p>
    </div>
  `;

  /* ---------- IMAGE SIGNAL ---------- */
  if (ml.used_image) {
    resultDiv.innerHTML += `
      <div class="section">
        <div class="section-title">Image Signal</div>
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

  /* ---------- AI SAFE MODE / FOLLOW-UPS ---------- */
  if (data.llm) {
    if (data.llm.type === "safe_mode") {
      resultDiv.innerHTML += `
        <div class="safe-box section">
          <strong>🛡️ AI Safe Mode</strong>
          <p>${data.llm.content}</p>
        </div>
      `;
    }

    if (data.llm.type === "followup") {
      resultDiv.innerHTML += `
        <div class="safe-box section">
          <strong>🤖 Follow-up Questions</strong>
          <p>${data.llm.content}</p>
        </div>
      `;
    }

    if (data.llm.type === "unavailable") {
      resultDiv.innerHTML += `
        <div class="safe-box section">
          <strong>AI Notice</strong>
          <p>${data.llm.content}</p>
        </div>
      `;
    }
  }

  /* ---------- DISCLAIMER ---------- */
  if (data.disclaimer) {
    resultDiv.innerHTML += `
      <div class="disclaimer section">
        ${data.disclaimer}
      </div>
    `;
  }

  resultDiv.classList.remove("hidden");
}
