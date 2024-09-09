import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import CHARTS_PATH, TOKEN_COLORS, FONT_SIZES, COINGECKO_API_KEY, START_DATE, END_DATE, TOKEN_NAME_MAPPING

# Initialize CoinGecko API client
cg = CoinGeckoAPI(api_key=COINGECKO_API_KEY)

# Set up Seaborn style
sns.set_theme(style="whitegrid")

# Convert dates to Unix timestamps
start_timestamp = int(datetime.strptime(START_DATE, "%Y-%m-%d").timestamp())
end_timestamp = int(datetime.strptime(END_DATE, "%Y-%m-%d").timestamp())

# Function to fetch price data
def fetch_price_data(token_id):
    try:
        data = cg.get_coin_market_chart_range_by_id(
            id=token_id,
            vs_currency='usd',
            from_timestamp=start_timestamp,
            to_timestamp=end_timestamp
        )
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df.set_index('date')['price']
    except Exception as e:
        print(f"Error fetching data for {token_id}: {e}")
        return pd.Series()

# Fetch data for each token
tokens = ['uniswap', 'aave', 'balancer', 'yearn-finance', 'index-cooperative', 'apwine']
price_data = {}

for token in tokens:
    price_data[token] = fetch_price_data(token)

# Normalize price data and calculate cumulative returns
normalized_price_data = {}
cumulative_returns_data = {}

for token, prices in price_data.items():
    if not prices.empty:
        normalized_price_data[token] = (prices / prices.iloc[0]) * 100
        returns = prices.pct_change()
        cumulative_returns_data[token] = (1 + returns).cumprod() * 100 - 100

# Create the normalized price plot
plt.figure(figsize=(14, 8))

for token, prices in normalized_price_data.items():
    if not prices.empty:
        plt.plot(prices.index, prices.values, label=TOKEN_NAME_MAPPING.get(token, token), color=TOKEN_COLORS.get(TOKEN_NAME_MAPPING.get(token, token)))

plt.title('Normalized Token Prices Over Time (Starting at 100)', fontsize=FONT_SIZES['header'])
plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
plt.ylabel('Normalized Price', fontsize=FONT_SIZES['axis_labels'])
plt.xticks(fontsize=FONT_SIZES['ticks'])
plt.yticks(fontsize=FONT_SIZES['ticks'])
plt.legend(fontsize=FONT_SIZES['legend'])
plt.axhline(y=100, color='gray', linestyle='--', alpha=0.7)
plt.gcf().autofmt_xdate()
plt.tight_layout()

# Save the normalized price plot
normalized_file_path = os.path.join(CHARTS_PATH, "normalized_token_prices_over_time.png")
plt.savefig(normalized_file_path)
print(f"Saved normalized price plot to {normalized_file_path}")
plt.close()

# Create the cumulative returns plot
plt.figure(figsize=(14, 8))

for token, returns in cumulative_returns_data.items():
    if not returns.empty:
        plt.plot(returns.index, returns.values, label=TOKEN_NAME_MAPPING.get(token, token), color=TOKEN_COLORS.get(TOKEN_NAME_MAPPING.get(token, token)))

plt.title('Cumulative Returns of Tokens Over Time', fontsize=FONT_SIZES['header'])
plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
plt.ylabel('Cumulative Return (%)', fontsize=FONT_SIZES['axis_labels'])
plt.xticks(fontsize=FONT_SIZES['ticks'])
plt.yticks(fontsize=FONT_SIZES['ticks'])
plt.legend(fontsize=FONT_SIZES['legend'])
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
plt.gcf().autofmt_xdate()
plt.tight_layout()

# Save the cumulative returns plot
cumulative_file_path = os.path.join(CHARTS_PATH, "cumulative_returns_over_time.png")
plt.savefig(cumulative_file_path)
print(f"Saved cumulative returns plot to {cumulative_file_path}")
plt.close()