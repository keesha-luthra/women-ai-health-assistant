async function submitSymptoms() {
    const input = document.getElementById("symptomsInput");
    const resultDiv = document.getElementById("result");
  
    const symptoms = input.value.trim();
    if (!symptoms) {
      alert("Please describe your symptoms.");
      return;
    }
  
    resultDiv.classList.add("hidden");
    resultDiv.innerHTML = "Loading...";
  
    try {
      const response = await fetch("http://127.0.0.1:5000/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ symptoms }),
      });
  
      const data = await response.json();
      displayResult(data);
    } catch (error) {
      resultDiv.innerHTML = "Something went wrong. Please try again.";
      resultDiv.classList.remove("hidden");
    }
  }
  
  function displayResult(data) {
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "";
  
    const ml = data.ml_result;
  
    resultDiv.innerHTML += `
      <div class="label">Possible condition:</div>
      <div>${ml.prediction}</div>
  
      <div class="label">Confidence:</div>
      <div>${ml.confidence}</div>
    `;
  
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
  