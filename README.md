## 🩺 HerHealth AI – Intelligent Women’s Health Assistant

HerHealth AI is a safety-aware AI health assistant that combines:
- Machine Learning–based symptom classification
- Confidence-aware decision gating
- AI-powered follow-up questioning (safe mode)

---

## 🔍 Key Features

### 1️⃣ Confidence-Based Gating & Safe Mode
When model confidence is low or the condition is high-risk, the system avoids unsafe predictions and asks follow-up questions instead.

![Low Confidence Follow-up](screenshots/1.png)

---

### 2️⃣ High-Confidence Direct Prediction
When confidence is high and symptoms are specific, the model provides a direct prediction with clear confidence.

![High Confidence Prediction](screenshots/2.png)

---

### 3️⃣ High-Risk Symptom Handling
For potentially dangerous symptoms, the system enforces Safe Mode even if confidence is high.

![High Risk Safe Mode](screenshots/3.png)

---

## 🛡️ Safety Design
- Confidence thresholds
- High-risk condition blocking
- AI fallback when LLM quota is exceeded
- Medical disclaimers by context

---

## 🧠 Tech Stack
- Python, Flask
- Scikit-learn (ML inference)
- OpenAI API (LLM follow-ups)
- HTML/CSS/JS frontend

> ⚠️ This tool is for informational purposes only and not a medical diagnosis.
