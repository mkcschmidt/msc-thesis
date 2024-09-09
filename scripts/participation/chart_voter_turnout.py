import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configurations from your scripts.config module
from scripts.config import METRICS_PATH, CHARTS_VOTER_TURNOUT, TOKEN_COLORS, TOKEN_NAME_MAPPING, FONT_SIZES, START_DATE, END_DATE

sns.set_theme(style="whitegrid")

# Load the voter turnout rates data
voter_turnout_rates_file = os.path.join(METRICS_PATH, "voter_turnout_rates.csv")
voter_turnout_rates_df = pd.read_csv(voter_turnout_rates_file)
print(f"Loaded voter turnout rates file with {len(voter_turnout_rates_df)} entries.")

# Convert the 'end_date' column to datetime
voter_turnout_rates_df['end_date'] = pd.to_datetime(voter_turnout_rates_df['end_date'])

# Filter data according to the configured start and end dates
voter_turnout_rates_df = voter_turnout_rates_df[
    (voter_turnout_rates_df['end_date'] >= START_DATE) & 
    (voter_turnout_rates_df['end_date'] <= END_DATE)
]

# Normalize token names
voter_turnout_rates_df['token_name'] = voter_turnout_rates_df['token_id'].apply(lambda x: TOKEN_NAME_MAPPING.get(x, x))

# Ensure the charts directory exists
os.makedirs(CHARTS_VOTER_TURNOUT, exist_ok=True)

# Function to remove outliers using IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Function to calculate a smoother moving average with a larger window
def calculate_moving_average(data, window=180):  # Window increased to 180 days for smoother trend
    return data.rolling(window=window, min_periods=1).mean()

# Plot voter turnout rates for each token with 180-day moving average
for token_id in voter_turnout_rates_df['token_id'].unique():
    token_data = voter_turnout_rates_df[voter_turnout_rates_df['token_id'] == token_id].copy()
    token_name = TOKEN_NAME_MAPPING.get(token_id, token_id)
    
    # Convert dates to numeric for regression
    token_data['date_num'] = mdates.date2num(token_data['end_date'])

    # Calculate the smoother moving average
    token_data['moving_average'] = calculate_moving_average(token_data['voter_turnout_rate'])
    
    plt.figure(figsize=(12, 8))
    
    # Scatter plot with lower alpha for less prominence
    sns.scatterplot(x='end_date', y='voter_turnout_rate', data=token_data, 
                    color=TOKEN_COLORS.get(token_name, '#003366'), s=50, alpha=0.1)
    
    # Plot the 180-day moving average
    plt.plot(token_data['end_date'], token_data['moving_average'], 
             color=TOKEN_COLORS.get(token_name, '#003366'), linewidth=2.5, label='180-day Moving Average')
    
    plt.xlabel('End Date', fontsize=FONT_SIZES['axis_labels'])
    plt.ylabel('Voter Turnout Rate', fontsize=FONT_SIZES['axis_labels'])
    plt.title(f'Voter Turnout Rates for Token {token_name}', fontsize=FONT_SIZES['header'])
    plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
    plt.yticks(fontsize=FONT_SIZES['ticks'])
    
    # Adjust the axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    plt.legend(loc='best', fontsize=FONT_SIZES['legend'])
    
    # Save the plot
    plot_file = os.path.join(CHARTS_VOTER_TURNOUT, f"voter_turnout_rates_{token_id}.png")
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    
    print(f"Saved scatter plot with moving average for token {token_name} to {plot_file}")

# Generate a cumulative scatter plot with all tokens together, applying outlier removal and moving average
plt.figure(figsize=(14, 10))
combined_data = remove_outliers(voter_turnout_rates_df, 'voter_turnout_rate')
for token_id in combined_data['token_id'].unique():
    token_name = TOKEN_NAME_MAPPING.get(token_id, token_id)
    token_data = combined_data[combined_data['token_id'] == token_id].copy()
    
    # Calculate the smoother moving average for cumulative plot
    token_data['moving_average'] = calculate_moving_average(token_data['voter_turnout_rate'])
    
    plt.plot(token_data['end_date'], token_data['moving_average'], 
             label=token_name, color=TOKEN_COLORS.get(token_name, 'grey'), linewidth=2.5)

plt.title('180-day Moving Average of Voter Turnout Rates for All Tokens', fontsize=FONT_SIZES['header'])
plt.xlabel('End Date', fontsize=FONT_SIZES['axis_labels'])
plt.ylabel('Voter Turnout Rate (180-day Moving Average)', fontsize=FONT_SIZES['axis_labels'])
plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
plt.yticks(fontsize=FONT_SIZES['ticks'])

ax = plt.gca()
ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

plt.legend(title='Tokens', loc='upper right', fontsize=FONT_SIZES['legend'])
plt.tight_layout()
scatter_plot_file = os.path.join(CHARTS_VOTER_TURNOUT, "voter_turnout_rates_all_tokens.png")
plt.savefig(scatter_plot_file)
plt.close()

print(f"Saved cumulative moving average plot for all tokens to {scatter_plot_file}")

print("Completed generating and saving all voter turnout rate charts.")