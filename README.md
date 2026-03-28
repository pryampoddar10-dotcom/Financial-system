# FinSentinel — AI Market Intelligence Dashboard

**Financial Systems and Market — Group Assignment | March 2026**

An institutional-grade AI-driven market sentiment analysis and portfolio risk management dashboard built with Streamlit and Plotly.

---

## 🚀 How to Run on Streamlit Cloud (Recommended)

1. **Fork or upload this repo to your GitHub account**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your GitHub repo, branch `main`, and file `app.py`
5. Click **Deploy** — it will be live in ~2 minutes with a shareable link

---

## 💻 How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/finsentinel.git
cd finsentinel

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## 📊 Dashboard Features

| Page | Features |
|------|----------|
| **Market Overview** | Live ticker tape, 5 KPI cards, AI insight panel, sentiment chart, VaR chart, sector heatmap, factor attribution, macro monitor |
| **Sentiment Engine** | NLP trend chart, sentiment distribution donut, data source breakdown, daily news volume |
| **Risk Monitor** | VaR 95%/99% history, implied volatility term structure, cross-asset correlation heatmap |
| **Earnings Intel** | **3 working tabs** — Recent Calls (NLP-scored), Upcoming Earnings (AI outlook), Anomaly Alerts (AI-detected) |
| **AI Copilot** | Interactive Q&A, suggested questions, AI insight library |

---

## 🗂️ File Structure

```
finsentinel/
├── app.py              ← Main Streamlit application
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🛠️ Built With

- **Streamlit** — Web app framework
- **Plotly** — Interactive charts
- **Pandas** — Data manipulation
- **FinBERT** — NLP sentiment (simulated for demo)
- **Claude AI** — Analytical copilot responses

---

## 👥 Group 4

- Aditya Maheshwari
- Pryam Poddar
- Sriju Singh
- Rudra Tiwari

---

*Financial Systems and Market Subject — March 2026*
