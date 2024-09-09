import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

# Append the path to ensure imports from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import METRICS_PATH, CHARTS_PATH, TOKEN_COLORS, TOKEN_NAME_MAPPING, FONT_SIZES

sns.set_theme(style="whitegrid")

# Read the metrics CSV files
metrics_filtered_df = pd.read_csv(os.path.join(METRICS_PATH, 'token_metrics_filtered.csv'))
metrics_unfiltered_df = pd.read_csv(os.path.join(METRICS_PATH, 'token_metrics_unfiltered.csv'))

# Convert the date column to datetime
metrics_filtered_df['date'] = pd.to_datetime(metrics_filtered_df['date'])
metrics_unfiltered_df['date'] = pd.to_datetime(metrics_unfiltered_df['date'])

# Replace token IDs with names in the dataframes
metrics_filtered_df['token_id'] = metrics_filtered_df['token_id'].map(TOKEN_NAME_MAPPING)
metrics_unfiltered_df['token_id'] = metrics_unfiltered_df['token_id'].map(TOKEN_NAME_MAPPING)

# List of metrics to plot
metrics = ['gini_coefficient', 'nakamoto_coefficient', 'shannon_entropy', 'hhi', 'theil_index', 'unique_holders']

# Ensure the charts directory exists
if not os.path.exists(CHARTS_PATH):
    os.makedirs(CHARTS_PATH)

# Define a function to create plots for each metric
def plot_metric(metric, df, title_suffix):
    plt.figure(figsize=(14, 8))
    sns.lineplot(data=df, x='date', y=metric, hue='token_id', palette=TOKEN_COLORS)
    plt.title(f'Time Series of {metric.replace("_", " ").title()} ({title_suffix})', fontsize=FONT_SIZES['header'])
    plt.xlabel('Date', fontsize=FONT_SIZES['axis_labels'])
    plt.ylabel(metric.replace("_", " ").title(), fontsize=FONT_SIZES['axis_labels'])
    plt.xticks(rotation=45, fontsize=FONT_SIZES['ticks'])
    plt.yticks(fontsize=FONT_SIZES['ticks'])

    # Set y-axis to a log scale for unique_holders
    ax = plt.gca()
    if metric == 'unique_holders':
        ax.set_yscale('log')
    
    max_y = df[metric].max()

    if metric == 'gini_coefficient':
        min_y = df[metric].min()
        ax.set_ylim(min_y - (0.01 * min_y), max_y + (0.01 * max_y))  # Zoom in for Gini coefficient
    elif metric != 'unique_holders':  # Don't set limits if using a log scale
        ax.set_ylim(0, max_y * 1.1)  # Add 10% room above the max value
    
    # Set x-axis label format to show only a limited number of date labels
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    # Add legend inside the plot area
    plt.legend(title='Token', loc='upper right', fontsize=FONT_SIZES['legend'])
    plt.tight_layout()
    file_path = os.path.join(CHARTS_PATH, f"{metric}_time_series_{title_suffix.lower()}.png")
    plt.savefig(file_path)
    plt.close()
    print(f"Saved plot to {file_path}")

# Plot each metric for filtered and unfiltered data
for metric in metrics:
    plot_metric(metric, metrics_filtered_df, 'Filtered')
    plot_metric(metric, metrics_unfiltered_df, 'Unfiltered')