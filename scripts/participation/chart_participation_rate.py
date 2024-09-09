import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator

# Append the path to ensure imports from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configurations from your scripts.config module
from scripts.config import METRICS_PATH, CHARTS_PARTICIPATION_RATES, TOKEN_COLORS, TOKEN_NAME_MAPPING, FONT_SIZES, START_DATE, END_DATE

# Set seaborn theme
sns.set_theme(style="whitegrid")

# Load the participation rates data
participation_rates_file = os.path.join(METRICS_PATH, "participation_rates.csv")
participation_rates_df = pd.read_csv(participation_rates_file)
print(f"Loaded participation rates file with {len(participation_rates_df)} entries.")

# Convert the 'date' column to datetime
participation_rates_df['date'] = pd.to_datetime(participation_rates_df['date'])

# Filter data according to the configured start and end dates
participation_rates_df = participation_rates_df[
    (participation_rates_df['date'] >= START_DATE) & 
    (participation_rates_df['date'] <= END_DATE)
]

# Normalize token names for display using the mapping
participation_rates_df['display_name'] = participation_rates_df['id'].apply(lambda x: TOKEN_NAME_MAPPING.get(x.lower(), x))

# Ensure the charts directory exists
os.makedirs(CHARTS_PARTICIPATION_RATES, exist_ok=True)

# Function to calculate a smoother moving average with a larger window
def calculate_moving_average(data, window=180):
    return data.rolling(window=window, min_periods=1).mean()

# Plot participation rates for each token
token_ids = participation_rates_df['id'].unique()  # Use 'id' for the actual storage identifier
for token_id in token_ids:
    token_data = participation_rates_df[participation_rates_df['id'] == token_id].copy()
    token_data = token_data.sort_values('date')
    
    # Calculate the smoother moving average
    token_data['moving_average'] = calculate_moving_average(token_data['participation_rate'])
    
    display_name = TOKEN_NAME_MAPPING.get(token_id.lower(), token_id)  # Map to human-readable name
    
    plt.figure(figsize=(12, 8))
    
    # Scatter plot with lower alpha for less prominence
    sns.scatterplot(x='date', y='participation_rate', data=token_data, 
                    color=TOKEN_COLORS.get(display_name, '#003366'), s=20, alpha=0.2)
    
    # Moving average line with a broader window
    plt.plot(token_data['date'], token_data['moving_average'], 
             color=TOKEN_COLORS.get(display_name, '#003366'), linewidth=2.5, label='180-day Moving Average')

    plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
    plt.ylabel('Participation Rate', fontsize=FONT_SIZES['axis_labels'])
    plt.title(f'Participation Rates for {display_name}', fontsize=FONT_SIZES['header'])
    plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
    plt.yticks(fontsize=FONT_SIZES['ticks'])
    
    # Adjust the axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    
    plt.legend(fontsize=FONT_SIZES['legend'])
    plt.tight_layout()
    
    # Use token_id for saving the file
    plot_file = os.path.join(CHARTS_PARTICIPATION_RATES, f"participation_rates_{token_id.lower().replace(' ', '_').replace('.', '_')}.png")
    plt.savefig(plot_file, dpi=300)
    plt.close()
    
    print(f"Saved improved plot for token {display_name} (ID: {token_id}) to {plot_file}")

# Generate a cumulative plot with all tokens together
plt.figure(figsize=(16, 10))

for token_id in token_ids:
    token_data = participation_rates_df[participation_rates_df['id'] == token_id].copy()
    token_data = token_data.sort_values('date')
    token_data['moving_average'] = calculate_moving_average(token_data['participation_rate'])
    
    display_name = TOKEN_NAME_MAPPING.get(token_id.lower(), token_id)
    
    plt.plot(token_data['date'], token_data['moving_average'], 
             label=display_name, color=TOKEN_COLORS.get(display_name, 'grey'), linewidth=2.5)

plt.title('180-day Moving Average of Participation Rates for All Tokens', fontsize=FONT_SIZES['header'])
plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
plt.ylabel('Participation Rate (180-day Moving Average)', fontsize=FONT_SIZES['axis_labels'])
plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
plt.yticks(fontsize=FONT_SIZES['ticks'])

ax = plt.gca()
ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

plt.legend(title='Token', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=FONT_SIZES['legend'])
plt.tight_layout()

cumulative_plot_file = os.path.join(CHARTS_PARTICIPATION_RATES, "participation_rates_all_tokens_moving_average.png")
plt.savefig(cumulative_plot_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved cumulative plot for all tokens to {cumulative_plot_file}")

print("Completed generating and saving all participation rate charts.")