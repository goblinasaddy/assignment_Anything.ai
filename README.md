# Trader Performance vs Market Sentiment Analysis 📈

Analyze how macroeconomic Bitcoin sentiment (Fear vs. Greed Index) uniquely impacts retail trader behavior and net profitability on the Hyperliquid exchange.

## Key Features

*   **Robust Data Engineering:** Synchronized IST to UTC timestamps against global sentiment indices to completely eliminate data leakage and boundary misalignment.
*   **Net Fee Profiles:** Employs precise PnL measurement (factoring out exchange fees) rather than gross metrics to map true retail extraction edges.
*   **Behavioral Execution Proxies:** Engineered Maker/Taker ratios directly off Trade Order books to identify aggregate retail _panic_ levels. 
*   **K-Means Trader Segregation:** Evaluated trader habits into 4 distinct Archetypes ('Aggressive Whales', 'Retail', 'Passive Makers', 'High-Frequency Scalpers') using unsupervised machine learning.
*   **Streamlit Web Visualizer:** Includes a beautifully-structured, reactive local web dashboard to review granular data changes across Market Regimes inline.

## Project Structure

```
├── data/
│   ├── fear_greed_index.csv     # Historical Market Sentiment (0-100 values)
│   └── historical_data.csv      # Raw transaction records across users
├── notebooks/
│   └── assignment.ipynb         # Complete data science pipeline & insights logging
├── dashboard.py                 # Interactive Streamlit Web App source
├── requirements.txt             # Python dependencies
└── README.md
```

## Installation & Setup

Ensure you have Python 3.9+ installed.

1. Clone the repository 
   ```bash
   git clone https://github.com/goblinasaddy/assignment_Anything.ai.git
   cd assignment_Anything.ai
   ```
2. Setup the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Analysis Pipeline

You can directly explore the compiled interactive notebook via Jupyter:
```bash
jupyter notebook notebooks/assignment.ipynb
```
The notebook is completely documented with statistical evaluations and 3 key actionable strategy implementations.

## Launching the Dashboard

This project includes a fully robust web application designed with Streamlit. To spin up this dashboard to view interactive trendline plots, Win Rate box distributions, and Execution Urgency charts:

Run:
```bash
streamlit run dashboard.py
```
> The dashboard will become available instantly at `http://localhost:8501`.

## Key Findings
* **Emotion spikes Taker Constraints:** When extreme 'Fear' descends on the index, retail accounts flip largely to market 'Takers', drastically accumulating unrecoverable fee losses attempting to rapidly exit drawdowns.
* **Greed maintains Win Rates:** While 'Greed' invites complacency, structural ecosystem Win Rates dramatically outpace 'Fear' events which predominantly force retail account liquidations/stop-triggers.