# PythonProject
This project is a real-time financial analytics platform developed in Python using Streamlit, designed to support quantitative analysis and portfolio management in an asset management context.
The application simulates a professional quantitative research workflow, combining:
- real-time and dynamic data retrieval,
- quantitative strategies and backtesting,
- interactive dashboards,
- automated daily reporting,
- and deployment on a Linux environment.
The project is organized into two main quantitative modules:
Quant A — Single Asset Analysis
Quant B — Multi-Asset Portfolio Analysis
Collaboration and integration are handled through GitHub, with separate development branches and a final integrated platform.

Project Objectives :
- Retrieve and display financial and macroeconomic data dynamically
- Implement quantitative investment strategies and performance metrics
- Provide interactive dashboards for single-asset and portfolio analysis
- Automate daily reporting via cron jobs
- Deploy and maintain a continuously running application on Linux
- Follow professional software engineering and Git workflows

Repository Structure : 
PythonProject/
│
├── app/
│   ├── pages/
│   │   ├── single_asset.py        # Quant A Streamlit dashboard
│   │   ├── portfolio.py           # Quant B Streamlit dashboard
│   │
│   ├── reports/
│   │   ├── daily_report.py         # Single asset daily report (cron)
│   │   ├── daily_report_portfolio.py # Portfolio daily report (cron)
│   │   └── output/                # Generated CSV reports
│
├── src/
│   ├── data/
│   │   ├── single_asset_data.py    # Market data loaders
│   │   ├── fred.py                 # FRED multi-series fetch
│   │   ├── fred_search.py          # FRED series search
│   │
│   ├── metrics/
│   │   ├── single_asset_metrics.py # Single asset metrics & strategies
│   │   ├── portfolio_metrics.py    # Portfolio metrics
│   │
│   ├── strategies/
│   │   ├── portfolio_construction.py # Portfolio construction logic
│
├── cron/
│   ├── daily_report.cron           # Cron configuration
│
├── requirements.txt
├── README.md
└── .gitignore

Quant A — Single Asset Analysis :
The Single Asset module focuses on the quantitative analysis of one financial instrument at a time.
Key Features :
- Dynamic price retrieval (Stooq)
- Auto-refresh every 5 minutes
- Interactive strategy parameters
- Multiple performance metrics
- Strategy vs Buy & Hold comparison
- Predictive modeling with confidence intervals

Implemented Strategies :
1-Buy & Hold
- Total return
- Annualized return
- Volatility
- Sharpe ratio
- Maximum drawdown

2- Moving Average Crossover Strategy
- Configurable short and long windows
- Trading signal generation
- Equity curve computation
- RSI indicator
- Strategy performance metrics

3- Predictive Model :
A linear regression model on log-prices is implemented to forecast future prices:
1- Configurable forecast horizon
2- Confidence intervals
3- Visualized alongside historical prices

Quant B — Multi-Asset Portfolio Analysis : 

The Portfolio module extends the analysis to multiple assets simultaneously, using macroeconomic and financial time series from FRED.
Key Features:

1- Selection of at least 3 assets
2- Dynamic asset search via FRED API
3- Customizable portfolio weights
4- Weekly / Monthly / No rebalancing
5- Robust data handling (app does not crash on API failure)

Portfolio Analytics:
- Portfolio returns and value
- Annualized return
- Annualized volatility
- Maximum drawdown
- Correlation matrix
- Comparison between individual assets and portfolio performance

Automated Daily Reports (Cron):
The project includes automated daily reporting, generated at a fixed time via cron on a Linux machine.

Reports Generated:
- Single Asset Daily Report
- Portfolio Daily Report

Each report includes:
- Date
- Asset(s)
- Open & close prices
- Annualized volatility
- Maximum drawdown

Reports are saved locally as CSV files in: app/reports/output/
Cron jobs are defined in the cron/ directory and execute the reporting scripts daily (e.g. at 8:00 PM).

Deployment & Reliability:
- Designed to run 24/7 on a Linux virtual machine
- Streamlit application kept running continuously
- Auto-refresh ensures near real-time updates
- Errors in data retrieval are handled gracefully
- Cloud cost minimization by lightweight architecture

Git Workflow:
Separate branches for each module:
- single-asset
- portfolio
Final integration in the integration branch
Clear and incremental commit history
Pull requests used for integration
Single unified README for the full project
