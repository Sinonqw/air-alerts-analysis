Interactive production-ready MVP application for geospatial and time-series analysis of air raid alerts in Ukraine during 2026. This project processes historical data down to the district (raion) level, normalizes strict military timestamps, and visualizes tactical patterns via a high-performance analytical dashboard.

## 📊 Key Analytical Insights Uncovered

* **Tactical Peak Activity:** Identified a nation-wide statistical surge in alerts consistently at 19:00, correlating with evening UAV wave deployments.
* **Geospatial Hotspots:** While frontline regions experience the highest frequency of triggers, Donetsk Oblast remains the absolute leader in total duration spent in shelters (35k+ hours).
* **Anomalous Spikes:** Successfully isolated massive combined attack waves (outliers reaching 900+ alerts daily) predominantly concentrated on Tuesdays and Fridays.
* **Predictive Risk Modeling:** Integrated 24-hour ahead probability curves to map threat escalation using statistical intensity markers.

## 🛠️ Tech Stack & Engineering Highlights

* **Core Data Engine:** Pandas & NumPy for heavy tabular cleaning, feature engineering, and processing over 50,000+ localized rows.
* **Geospatial Intelligence:** Dynamic multi-level Choropleth maps rendered with Plotly Express mapped directly to post-decentralization Ukrainian district borders (136 raions via Admin 2 GeoJSON boundaries).
* **Timezone Normalization:** Solved critical mixed-timezone edge cases, transforming timestamps from native formats seamlessly into standard Europe/Kyiv zone with automatic DST handling.
* **AI-Driven Forecasting:** Integrated an LLM predictive engine via **OpenRouter API** (`google/gemini-2.5-flash`) that parses live metrics on-the-fly and generates structured math-based JSON vectors to plot future threat probabilities.
* **Modern Interface:** Rapidly prototyped responsive UX/UI utilizing Streamlit with state-preserving data caching (`@st.cache_data`).

## 📁 Repository Structure

```text
├── data/
│   ├── raw/            # Raw datasets (official_data_uk.csv & GeoJSON maps)
│   └── processed/      # Cleaned data ready for consumption
├── notebooks/          # Exploratory Data Analysis (Jupyter Notebooks)
├── src/                # Modular codebase containing pipeline logic
│   ├── data_loader.py  # Loading, validation & initial pre-filtering
│   ├── processing.py   # Advanced feature engineering (Time-series components)
│   └── ai_analyst.py   # OpenRouter API integration & JSON predictive module
├── app.py              # Main Streamlit Frontend Dashboard application
├── main.py             # CLI production entry point
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
🚀 Getting Started & Installation
1. Clone the repository

git clone https://github.com/Sinonqw/air-alerts-analysis.git
cd air-alerts-analysis
2. Set up Virtual Environment

python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

3. Run the Data Pipeline
Execute the main entry point to download, clean, and pre-process the initial dataset slice:

python3 main.py

4. Launch the Strategic Dashboard
Fire up the responsive local web server:


streamlit run app.py
The app will automatically open in your default browser at http://localhost:8501.

🔮 AI Forecast Setup (Zero-Leak Security)
To use the Mathematical AI-Predictive Model feature without risking credential leaks:

Obtain an API key from OpenRouter.

Run the application locally via Streamlit.

Paste your key directly into the secure "🔑 Налаштування AI" input field located in the sidebar interface.

Your key is processed completely in-memory, ensuring zero exposure in public commits or repository history.

🗺️ Dashboard Preview
The application features a built-in switch to toggle monitoring focus between high-level Oblasts (Admin 1) and newly reformed Raions (Admin 2) for maximum granularity control during situational updates, alongside an isolated area chart displaying predicted threat percentages for the next 24 hours.
