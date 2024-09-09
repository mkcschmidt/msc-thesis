# run.py

import os
def install_requirements():
    print("Checking if all required packages are installed...")
    os.system('pip install -r requirements.txt')

def main():
    # First, install dependencies
    install_requirements()
    
    ### Decentralization Metrics
    # Data Collection, Processing of Token Holders (based on data/processed/consolidated_index.csv)
    os.system('python scripts/decentralization/fetch_token_holders.py') # collects data from bitquery, token holders
    os.system('python scripts/decentralization/process_token_holders.py') # processes data, filters exchange addresses
    os.system('python scripts/decentralization/calculate_metrics.py') # analyzes and processes data, calculates metrics

    # Data Visualization
    os.system('python scripts/decentralization/plot_metrics.py') # plots data, saves to file
    os.system('python scripts/decentralization/plot_price.py') # plots price data
    os.system('python scripts/decentralization/plot_mcap.py') # plots market cap data


    ### Participation Metrics
    # Data Collection
    os.system('python scripts/participation/get_proposals.py') # fetches proposals from snapshot
    os.system('python scripts/participation/get_proposal_details.py') # fetches proposal details from snapshot
    os.system('python scripts/participation/get_votes.py') # fetches proposal votes from snapshot

    # Data Processing
    os.system('python scripts/participation/calculate_cumulative_proposals.py') # calculates metrics of tokens
    os.system('python scripts/participation/calculate_participation_rate.py') # calculates participation rate of tokens
    os.system('python scripts/participation/calculate_voter_turnout.py') # calculates voter turnout of tokens

    # Data Visualization
    os.system('python scripts/participation/chart_cumulative_proposals.py') # plots cumulative proposals
    os.system('python scripts/participation/chart_participation_rate.py') # plots participation rate
    os.system('python scripts/participation/chart_voter_turnout.py') # plots voter turnout



    ### Statistics
    os.system('python scripts/statistics/mann_kendall_trend.py') # calculates mann-kendall trend test
    os.system('python scripts/statistics/mann_kendall_trend_participation.py') # calculates mann-kendall trend test for participation
    os.system('python scripts/statistics/spearman_correlation.py') # calculates spearman correlation

if __name__ == "__main__":
    main()