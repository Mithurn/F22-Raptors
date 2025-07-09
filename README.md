# 🌾🚨 F22-Raptors: Saving Farmers with AI — HackOrbit 2025

---

## 💔 Problem Statement

**"One farmer dies by suicide every 41 minutes in India."**

Most of these tragedies are caused by **sudden, unexpected crop failures**.  
Current tools are often too late, unreliable, or require smartphones/literacy — leaving small farmers helpless.

https://timesofindia.indiatimes.com/city/bhubaneswar/farmer-suffers-crop-loss-kills-self-in-jajpur/articleshow/121219672.cms?utm_source=chatgpt.com

---

## 💡 Our Mission

**Build an AI system that stops farmer suicides before they happen**, using an ultra-accessible Telegram bot that works even on 2G networks.  
A single blurry photo or simple message can trigger life-saving help.

---

## 🚀 Our AI-Driven Solution

### 📷 Crop Autopsy AI
Diagnoses pests, soil issues, and drought stress from **low-resolution images** sent by farmers.

- ✔ Works with blurred/poor-quality photos.
- ✔ Uses Roboflow API or TensorFlow (trained on low-res crop samples).
- ✔ Suggests instant, actionable fixes.

### 🧠 Distress Signal AI
Monitors group chats for signs of **suicidal intent**, distress language, or emotional breakdown.

- ✔ Uses `TextBlob` for sentiment + rule-based keyword filtering.
- ✔ Flags high-risk messages.
- ✔ Sends alerts to NGOs or support teams after human review.

### 🔮 Future Vision AI
Predicts crop collapse zones **90 days in advance** using environmental trends.

- ✔ Combines soil data, pesticide usage, and OpenWeatherMap forecasts.
- ✔ Rule-based early warning system.
- ✔ Enables proactive outreach and area-wide prevention.

---

## 💬 How It Works

1. 👨‍🌾 Farmers send a photo or message to our Telegram bot (works over 2G).
2. 🤖 Our AI Engine activates:
    - **Crop Autopsy AI** → Image Diagnosis
    - **Distress Signal AI** → Mental Health Flagging
    - **Future Vision AI** → Forecast Collapse Zones
3. 📩 Farmers receive tailored advice, and high-risk cases alert NGOs instantly.

---
## Demo for our feature 1
video: https://drive.google.com/file/d/1tATjQ9KV7t_7JuyeMmDC2NAQiapl2oGu/view?usp=share_link

ppt: https://drive.google.com/file/d/1b30RHixn48HjuoLmMfwzn3TzkjNOg501/view?usp=share_link
---
## 🛠️ Tech Stack & APIs

### 💻 Backend
- `Python`, `FastAPI` for AI orchestration and endpoints

### 🤖 AI Modules & Tools
| Module | Tools Used |
|--------|------------|
| Image AI | Roboflow API / TensorFlow |
| Sentiment AI | TextBlob, Custom Keyword Engine |
| Forecast AI | Rule-based logic on soil & weather trends |
| Weather | OpenWeatherMap API |
| Chat Interface | Telegram Bot (via `pyTelegramBotAPI`) |
| NLP Helper | Google Gemini API (for future expansion) |

### 🛡️ Security & Environment
- `.env` for secure API token storage (`python-dotenv`)
- API keys protected and ignored from version control

### 🔗 Hosting (Optional Demo Setup)
- Backend: Railway (FastAPI server)
- Frontend: Vercel (demo UI with simulated messages)

---

## ⚡ Impact & Novelty

- ✅ **2G-friendly**: No app, works via WhatsApp/Telegram
- ✅ **Multi-layered AI**: Image + Text + Forecast in one system
- ✅ **Life-Saving Focus**: Not just agri-tech — it's suicide prevention
- ✅ **No literacy or tech barriers**: Designed with empathy, not dashboards

---

## 📦 Sample Inputs & Outputs

### Crop Autopsy (Image)
- **Input**: Low-res photo of diseased tomato plant
- **Output**: `"Pest Detected: Aphids. Recommended: Neem spray + hydration."`

### Distress Signal (Text)
- **Input**: `"I don't see the point of trying anymore. My field is ruined."`
- **Output**: `"ALERT: Distress signal detected. NGO team notified."`

### Forecast AI
- **Input**: `"Soil moisture down, pesticide low, rainfall predicted under 20mm"`
- **Output**: `"⚠ Zone likely to face crop failure in 60–90 days."`

---

## 🔐 Compliance with HackOrbit 2025 Rules

- ✅ All code written after **July 6, 10:00 AM IST**
- ✅ GitHub commits and timestamps are transparent
- ✅ No plagiarized logic/code; only framework/template used where allowed
- ✅ AI tools (TextBlob, Gemini, Roboflow) declared clearly
- ✅ Dataset samples used are either open-source or mock-simulated

---

## 🧠 Use of AI Tools for Debugging & Development

We leveraged the following responsibly:
- **GitHub Copilot** for boilerplate routing & service scaffolding
- **ChatGPT** for architecture decisions and API strategy planning
- **Google Gemini** (test only) for mock Q&A responses (declared, not used in logic)
- **TextBlob** sentiment analysis module was tested via curated inputs during dev
- **Roboflow** used for image model deployment/testing (custom-trained)

All uses were strictly **development aids**, not copied solutions.

---

## 🧠 Future Scope

- 🔁 Fine-tune sentiment classifier with real anonymized data
- 📡 Integrate real-time feedback loop with state helplines
- 🛰️ Add satellite + drone data in Future Vision AI
- 🧭 Rollout via state agricultural departments + NGOs

---

## 💼 Business & Sustainability

| Stakeholder | Value |
|-------------|-------|
| Farmers | 💯 Free forever |
| Govt Agencies | ₹1–5 per alert (via SMS or API) |
| NGOs | Monthly AI dashboard subscription |
| Long-term | Carbon credits + Impact Bonds (social ROI) |

---

## 👨‍👩‍👧‍👦 Team F22-Raptors

- Mithurn Jeromme (Team Lead)
- Mahee Tibrewal  
📞 +91 8056687515  
📞 +91 9731126460  

---

## ⭐ Let’s stop the silent crisis — one message at a time.

