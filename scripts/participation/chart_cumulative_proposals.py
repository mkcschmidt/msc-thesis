import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
import seaborn as sns

# Append the path to ensure imports from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configurations from your scripts.config module
from scripts.config import TOKEN_COLORS, TOKEN_NAME_MAPPING, FONT_SIZES, METRICS_PATH, CHARTS_CUMULATIVE_PROPOSALS, START_DATE, END_DATE

sns.set_theme(style="whitegrid")

# Load and preprocess the data
cumulative_proposals_file = os.path.join(METRICS_PATH, "cumulative_proposals.csv")
cumulative_proposals_df = pd.read_csv(cumulative_proposals_file)
cumulative_proposals_df['date'] = pd.to_datetime(cumulative_proposals_df['date'])
cumulative_proposals_df['token_name'] = cumulative_proposals_df['id'].map(TOKEN_NAME_MAPPING)

# Filter the data based on START_DATE and END_DATE from config
start_date = pd.to_datetime(START_DATE)
end_date = pd.to_datetime(END_DATE)
cumulative_proposals_df = cumulative_proposals_df[(cumulative_proposals_df['date'] >= start_date) & (cumulative_proposals_df['date'] <= end_date)]

# Rebase the cumulative proposals to start at 0 for each token
cumulative_proposals_df = cumulative_proposals_df.sort_values(['id', 'date'])
initial_values = cumulative_proposals_df.groupby('id')['cumulative_proposals'].first()
cumulative_proposals_df['rebased_proposals'] = cumulative_proposals_df.apply(lambda row: row['cumulative_proposals'] - initial_values[row['id']], axis=1)

# Ensure the output directory exists
os.makedirs(CHARTS_CUMULATIVE_PROPOSALS, exist_ok=True)

# Plot individual charts for each token
for token_id, token_group in cumulative_proposals_df.groupby('id'):
    token_name = TOKEN_NAME_MAPPING.get(token_id, 'Unknown')
    plt.figure(figsize=(12, 8))
    plt.plot(token_group['date'], token_group['rebased_proposals'], label=token_name, linewidth=2, color=TOKEN_COLORS.get(token_name, '#000000'))
    plt.title(f'Cumulative Proposals for {token_name} (Rebased)', fontsize=FONT_SIZES['header'])
    plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
    plt.ylabel('Cumulative Proposals (Rebased)', fontsize=FONT_SIZES['axis_labels'])
    plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
    plt.yticks(fontsize=FONT_SIZES['ticks'])
    plt.legend(loc='best', fontsize=FONT_SIZES['legend'], frameon=True)
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_CUMULATIVE_PROPOSALS, f"cumulative_proposals_{token_id}.png"))
    plt.close()

# Plot for all tokens together
plt.figure(figsize=(14, 10))
for token_id, token_group in cumulative_proposals_df.groupby('id'):
    token_name = TOKEN_NAME_MAPPING.get(token_id, 'Unknown')
    plt.plot(token_group['date'], token_group['rebased_proposals'], label=token_name, linewidth=2, color=TOKEN_COLORS.get(token_name, '#000000'))

plt.title('Cumulative Proposals for All Tokens (Rebased)', fontsize=FONT_SIZES['header'])
plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
plt.ylabel('Cumulative Proposals (Rebased)', fontsize=FONT_SIZES['axis_labels'])
plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
plt.yticks(fontsize=FONT_SIZES['ticks'])
plt.legend(loc='best', fontsize=FONT_SIZES['legend'], frameon=True)
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_CUMULATIVE_PROPOSALS, "cumulative_proposals_all_tokens.png"))
plt.close()

print("Completed generating and saving all rebased cumulative proposal charts.")