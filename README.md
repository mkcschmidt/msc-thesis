# DeFi Governance Metrics Analysis

## Overview

This project is a comprehensive analysis of decentralization, participation, and governance metrics for various DeFi protocols, including Uniswap, Aave, Yearn Finance, Balancer, Index Cooperative, and Spectra. The analysis utilizes various metrics to evaluate the governance structures of these protocols, including token distribution, voting power, and participation trends over time.

The project is divided into three major components:
1. **Decentralization Metrics**: Analysis of token holder distribution and concentration.
2. **Participation Metrics**: Analysis of governance participation rates, voter turnout, and proposal activity.
3. **Statistical Analysis**: Trends and correlations across decentralization and participation metrics using tests such as the Mann-Kendall trend and Spearman's rank correlation.

## Setup

### Prerequisites
Ensure you have Python 3.10.9 installed on your system. 

### Install Dependencies

Before running the analysis, you'll need to install the required Python packages. All dependencies are listed in the `requirements.txt` file. To install them, run the following command in the terminal:

pip install -r requirements.txt

### API Keys

This project requires access to several APIs (e.g., Bitquery and Snapshot). Before running the scripts, make sure to insert your API keys into the `scripts/config.py` file or relevant scripts that fetch data. 


### Running the Project

Once the dependencies are installed and API keys are configured, you can execute the entire project using the main `scripts/run.py` script.

python scripts/run.py

The `scripts/run.py` script performs the following tasks in sequence:

1. **Decentralization Metrics**:
   - Fetches token holder data from Bitquery.
   - Processes and filters the token holder data.
   - Calculates decentralization metrics such as Gini coefficient, Shannon entropy, and Herfindahl-Hirschman Index (HHI).
   - Generates visualizations of the decentralization metrics.

2. **Participation Metrics**:
   - Fetches governance proposal and voting data from Snapshot.
   - Calculates cumulative proposals, participation rates, and voter turnout rates.
   - Generates visualizations of participation and voter turnout over time.

3. **Statistical Analysis**:
   - Conducts the Mann-Kendall trend test on decentralization and participation metrics.
   - Performs Spearman's rank correlation on participation and voter turnout data.

### Results

The results, including visualizations and statistical outputs, will be saved in the appropriate directories inside `data/processed/`, `data/metrics/`, `data/statistics/`, as well as in the charts folder.