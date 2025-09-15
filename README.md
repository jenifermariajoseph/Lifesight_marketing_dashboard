# 📊 Lifesight Marketing Dashboard  

🚀 A powerful, data-driven analytics tool that transforms raw marketing data into **actionable insights**.  
This dashboard helps **marketing and business leaders** visualize 📈, analyze 🔍, and optimize 💡 their performance across **Facebook, Google, TikTok, and Business Data** — all in one place.  

---

## 🚀 Live Demo  

🔗 [View the Dashboard Here](https://jenifermariajoseph-lifesight-marketing-dashboard-app-uhdu2l.streamlit.app/An_Overview)  

---

## 🌟 Project Overview  

The **Lifesight Marketing Dashboard** brings together data from multiple channels to provide a **holistic view** of marketing effectiveness and ROI 💰.  
It empowers decision-makers with **real-time insights** and clear visual storytelling 🎨.  

---

## ⚙️ How It Was Created  

### 🔗 Data Integration & Processing  
- 📥 **Data Collection**:  
  - Facebook Ads → `Facebook.csv`  
  - Google Ads → `Google.csv`  
  - TikTok Ads → `TikTok.csv`  
  - Business Performance (orders & revenue) → `business.csv`  

- 🧹 **Data Cleaning & Preparation**:  
  - Standardized date formats 📅  
  - Added source labels 🔖  
  - Merged marketing & business data 🔗  
  - Calculated KPIs (ROAS, CPC, CTR, Conversion Rate) 📊  

- 💻 **Tech Implementation**:  
  - Python + Streamlit 🐍✨  
  - Plotly for interactive charts 📉  
  - Flexible date filters 📅  
  - Period-over-period comparisons 📊🔁  

---

## 🗂️ Dashboard Structure  

1. **🏠 Overview** – High-level marketing summary  
2. **📊 Comparison** – Side-by-side performance across periods  
3. **🔍 Individual Assessment** – Deep dive into each channel  

---

## 🔥 Key Features  

### 1️⃣ Overview Dashboard  
- **KPI Cards**: Revenue 💰, Orders 📦, Spend 💸, ROAS 🔄  
- **Revenue & Spend Trends**: Interactive lines with hover insights 📈  
- **Orders vs New Customers**: Track acquisition & retention 👥  
- **Sales Tactics Performance**: Lollipop chart 🍭 with growth indicators ✅❌  

### 2️⃣ Comparison Dashboard  
- Compare time periods ⏳ side-by-side  
- See **channel & campaign performance shifts** 🔄  

### 3️⃣ Individual Assessment  
- **Channel-specific ROI** 🎯  
- **Campaign-level breakdowns** 📊  
- Deep **performance analysis** 🔍  

---

## 🎮 How to Use  

1. **Launch**: Open the hosted Streamlit app 🌐  
2. **Filter**: Select your desired date range 📅  
3. **Explore**: Hover on charts for deep insights 👆  
4. **Navigate**: Use sidebar to switch between pages 📑  

---

## 💻 Tech Stack  

- Python 3.9+ 🐍  
- Streamlit 🌐  
- Plotly 📊  
- Pandas 🐼  

---

## 🛠️ Installation & Local Development  

```bash
# Clone the repository
git clone [repository-url]

cd lifesight

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
