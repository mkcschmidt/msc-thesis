# Description: Configuration file for the project

# Bitquery API Keys
ACCESS_TOKENS = [
    "Put your Bitquery API key here"
]

COINGECKO_API_KEY = "Put your CoinGecko API key here"
ETHERSCAN_API_KEY = "Put your Etherscan API key here"
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"

START_DATE = "2022-01-01"
END_DATE = "2024-06-30"

# Paths
DATA_PATH = "data/"

CHARTS_PATH = "charts/decentralization_metrics/"
CHARTS_PATH_2 = "charts/partcicipation_metrics/"
CHARTS_CUMULATIVE_PROPOSALS = "charts/participation_metrics/cumulative_proposals/"
CHARTS_PARTICIPATION_RATES = "charts/participation_metrics/participation_rates/"
CHARTS_VOTER_TURNOUT = "charts/participation_metrics/voter_turnout/"

RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"
METRICS_PATH = "data/metrics/"
TOKEN_METRICS_PATH = "data/metrics/token_metrics_filtered.csv"
EXCHANGE_ADDRESSES_PATH = "data/raw/exchange_addresses.csv"


TOKENS_PATH = "data/raw/tokens/"
PROPOSALS_PATH = "data/raw/proposals/"
PROPOSALS_PATH_CSV = "data/raw/proposals/proposals.csv"
PROPOSALS_DETAILS_PATH = "data/raw/proposals/proposal_details.csv"
PROPOSALS_VOTES_PATH = "data/raw/proposals/proposal_votes.csv"

COMBINED_TOKENS_PATH = "data/processed/combined_tokens.csv"
CLASSIFIED_TOKENS_PATH = "data/processed/classified_tokens.csv"
PROCESSED_TOKEN_HOLDERS_PATH = "data/processed/token_holders/"
INDEX_DATA_PATH = "data/processed/index_constituents/"
SPACES_CSV_PATH = "data/processed/space_ids.csv"
CONSOLIDATED_INDEX_PATH = "data/processed/consolidated_index.csv"

# Paths for stats calculations
STATISTICS_PATH = "data/statistics/"
PARTICIPATION_RATES_CSV = "data/metrics/participation_rates.csv"
VOTER_TURNOUT_CSV = "data/metrics/voter_turnout_rates.csv"

# Colors
TOKEN_COLORS = {
    'Uniswap': '#1f77b4',
    'Aave': '#ff7f0e',
    'Balancer': '#2ca02c',
    'Yearn Finance': '#d62728',
    'Index Cooperative': '#9467bd',
    'Spectra': '#8c564b'
}

# Define a mapping of normalized token names
TOKEN_NAME_MAPPING = {
    'uniswap': 'Uniswap',
    'aave': 'Aave',
    'balancer': 'Balancer',
    'yearn-finance': 'Yearn Finance',
    'index-cooperative': 'Index Cooperative',
    'apwine': 'Spectra'
}

# Font sizes
FONT_SIZES = {
    'header': 16,
    'legend': 12,
    'axis_labels': 14,
    'ticks': 12
}