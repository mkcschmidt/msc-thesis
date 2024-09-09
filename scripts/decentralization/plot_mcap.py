import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pycoingecko import CoinGeckoAPI
from datetime import datetime

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import CHARTS_PATH, TOKEN_COLORS, FONT_SIZES, COINGECKO_API_KEY, END_DATE, TOKEN_NAME_MAPPING

sns.set_theme(style="whitegrid")

# Initialize the CoinGecko API client
cg = CoinGeckoAPI(api_key=COINGECKO_API_KEY)

# List of token IDs
token_ids = ['uniswap', 'aave', 'balancer', 'yearn-finance', 'index-cooperative', 'apwine']

# Convert END_DATE to the required format: dd-mm-yyyy
end_date = datetime.strptime(END_DATE, "%Y-%m-%d").strftime("%d-%m-%Y")

# Fetch market cap data
market_caps = []
for token_id in token_ids:
    try:
        data = cg.get_coin_history_by_id(id=token_id, date=end_date)
        
        # Handle potential missing market data
        if 'market_data' in data and 'market_cap' in data['market_data']:
            market_cap = data['market_data']['market_cap']['usd']
        else:
            market_cap = None
        
        token_name = TOKEN_NAME_MAPPING.get(token_id, token_id.capitalize())
        if market_cap:
            market_caps.append((token_name, market_cap))
        else:
            print(f"Market cap data not available for {token_name} on {END_DATE}")
    except Exception as e:
        print(f"Error fetching data for {token_id} on {END_DATE}: {e}")

# Create DataFrame
df = pd.DataFrame(market_caps, columns=['Token', 'Market Capitalization (USD)'])

# Sort the DataFrame by Market Cap
df = df.sort_values(by='Market Capitalization (USD)', ascending=False)

# Create the bar plot with custom colors
plt.figure(figsize=(14, 8))
bar_colors = [TOKEN_COLORS.get(token, '#333333') for token in df['Token']]  # Map token names to their specific colors
ax = sns.barplot(data=df, x='Market Capitalization (USD)', y='Token', palette=bar_colors, dodge=False)

plt.xscale('log')

# Add labels in millions on the bars with two decimal places
for container in ax.containers:
    ax.bar_label(container, labels=[f'{v / 1_000_000:,.2f}M' for v in container.datavalues], fontsize=FONT_SIZES['ticks'], padding=5)

# Add title and labels using font sizes from the config
plt.title(f'Market Capitalization of Selected Tokens as of {END_DATE}', fontsize=FONT_SIZES['header'])
plt.xlabel('Market Capitalization (USD)', fontsize=FONT_SIZES['axis_labels'])
plt.ylabel('Token', fontsize=FONT_SIZES['axis_labels'])
plt.xticks(fontsize=FONT_SIZES['ticks'])
plt.yticks(fontsize=FONT_SIZES['ticks'])

# Remove the legend as there are no categories to display
plt.legend().set_visible(False)

# Adjust layout to make room for potential legend or axis labels
plt.tight_layout()

# Ensure the charts directory exists
os.makedirs(CHARTS_PATH, exist_ok=True)

# Save the plot
file_path = os.path.join(CHARTS_PATH, "market_capitalization.png")
plt.savefig(file_path)
print(f"Saved plot to {file_path}")
plt.close()