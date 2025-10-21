"""
generate_showcase.py

Generates showcase plots and a combined forecast table from cleaned CSVs and forecast CSVs.
Creates a `showcase/` directory with PNGs and CSVs suitable for sharing on LinkedIn.

Usage:
    python generate_showcase.py

Dependencies:
    pandas, matplotlib, seaborn, numpy
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='whitegrid')

OUT_DIR = 'showcase'
os.makedirs(OUT_DIR, exist_ok=True)

# Load cleaned data
cap_path = 'cleaned_capacity_data.csv'
gen_path = 'cleaned_generation_data.csv'

cap = pd.read_csv(cap_path, parse_dates=['Year']) if os.path.exists(cap_path) else None
if cap is not None:
    cap = cap.set_index('Year')

gen = pd.read_csv(gen_path, parse_dates=['Year']) if os.path.exists(gen_path) else None
if gen is not None:
    gen = gen.set_index('Year')

# Helper to save figure
def save_fig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    print('Saved', path)

# 1. Capacity trends: total renewable vs non-renewable
if cap is not None and 'Total renewable' in cap.columns and 'Total non-renewable' in cap.columns:
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(cap.index.year, cap['Total renewable'], marker='o', label='Total renewable')
    ax.plot(cap.index.year, cap['Total non-renewable'], marker='o', label='Total non-renewable')
    ax.set_title('Total Capacity: Renewable vs Non-renewable')
    ax.set_xlabel('Year')
    ax.set_ylabel('Capacity')
    ax.legend()
    save_fig(fig, 'capacity_trends.png')
    plt.close(fig)

# 2. Generation trends for major techs (if present)
if gen is not None:
    majors = []
    for c in ['Solar photovoltaic', 'Onshore wind energy', 'Renewable hydropower']:
        if c in gen.columns:
            majors.append(c)
    if majors:
        fig, ax = plt.subplots(figsize=(10,6))
        for c in majors:
            ax.plot(gen.index.year, gen[c], marker='o', label=c)
        ax.set_title('Generation Trends by Technology')
        ax.set_xlabel('Year')
        ax.set_ylabel('Generation')
        ax.legend()
        save_fig(fig, 'generation_trends.png')
        plt.close(fig)

# 3. Stacked bar for renewable tech share (latest year)
if cap is not None:
    renewable_techs = [t for t in ['Solar photovoltaic', 'Onshore wind energy', 'Renewable hydropower', 'Marine energy', 'Solid biofuels', 'Biogas'] if t in cap.columns]
    if renewable_techs:
        latest = cap.loc[cap.index.max(), renewable_techs]
        fig, ax = plt.subplots(figsize=(8,6))
        latest.plot(kind='bar', ax=ax)
        ax.set_title(f'Renewable Technology Contribution ({cap.index.max().year})')
        ax.set_ylabel('Capacity')
        save_fig(fig, 'top_tech_share.png')
        plt.close(fig)

# 4. Forecast plots: save individual per-technology forecasts and combined grids
fc_gen_path = 'generation_forecasts.csv'
fc_cap_path = 'capacity_forecasts.csv'

def sanitize_filename(name: str) -> str:
    return name.strip().replace(' ', '_').replace('/', '_')

def plot_and_save_forecast(tech, hist, fc_df, out_file, square=True, dpi=200):
    """Plot historical series and forecast (with conf int if available) and save a square image suitable for LinkedIn."""
    if hist is None or hist.empty:
        print('No historical data for', tech)
        return
    fig_size = (6,6) if square else (10,5)
    fig, ax = plt.subplots(figsize=fig_size)

    hist_index = pd.to_datetime(hist.index)
    ax.plot(hist_index.year, hist.values, marker='o', color='#1f77b4', label='Historical', linewidth=2)

    if fc_df is not None and not fc_df.empty:
        try:
            fc_index = pd.to_datetime(fc_df.index)
            ax.plot(fc_index.year, fc_df['forecast'].values, marker='o', linestyle='--', color='#ff7f0e', label='Forecast', linewidth=2)
            if 'lower' in fc_df.columns and 'upper' in fc_df.columns:
                ax.fill_between(fc_index.year, fc_df['lower'], fc_df['upper'], color='#ff7f0e', alpha=0.2)
        except Exception:
            # If fc_df is a Series
            ax.plot(fc_df.index, fc_df.values, marker='o', linestyle='--', color='#ff7f0e', label='Forecast', linewidth=2)

    ax.set_title(tech)
    ax.set_xlabel('Year')
    ax.set_ylabel('Value')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(out_file, dpi=dpi)
    plt.close(fig)
    print('Saved', out_file)

def save_all_forecasts(fc_path, hist_df, out_subdir):
    if not os.path.exists(fc_path):
        print('Forecast file not found:', fc_path)
        return
    fc = pd.read_csv(fc_path, parse_dates=['Year'], index_col='Year')
    # create directories
    indi_dir = os.path.join(OUT_DIR, 'forecasts', out_subdir)
    grid_path = os.path.join(OUT_DIR, f'forecasts_{out_subdir}_grid.png')
    os.makedirs(indi_dir, exist_ok=True)

    techs = list(fc.columns)
    saved = []
    for tech in techs:
        hist = hist_df[tech] if (hist_df is not None and tech in hist_df.columns) else None
        filename = sanitize_filename(tech) + '.png'
        out_file = os.path.join(indi_dir, filename)
        plot_and_save_forecast(tech, hist, fc[[tech]] if tech in fc.columns else None, out_file, square=True)
        saved.append(out_file)

    # create combined grid
    if saved:
        n = len(saved)
        ncols = 3
        nrows = (n + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*4, nrows*3), squeeze=False)
        axes_flat = axes.flatten()
        for i, tech in enumerate(techs):
            ax = axes_flat[i]
            hist = hist_df[tech] if (hist_df is not None and tech in hist_df.columns) else None
            if hist is not None:
                ax.plot(pd.to_datetime(hist.index).year, hist.values, marker='o', color='#1f77b4', linewidth=1.5)
            if tech in fc.columns:
                fc_df = fc[[tech]]
                ax.plot(fc_df.index.year, fc_df[tech].values, marker='o', linestyle='--', color='#ff7f0e', linewidth=1.5)
            ax.set_title(tech, fontsize=8)
            ax.tick_params(axis='x', labelrotation=45, labelsize=7)
            ax.tick_params(axis='y', labelsize=7)
        # hide extra axes
        for j in range(i+1, len(axes_flat)):
            axes_flat[j].axis('off')
        plt.tight_layout()
        fig.savefig(grid_path, dpi=200)
        plt.close(fig)
        print('Saved combined grid:', grid_path)

# Save generation forecasts (all techs)
if os.path.exists(fc_gen_path) and gen is not None:
    save_all_forecasts(fc_gen_path, gen, 'generation')

# Save capacity forecasts (all techs)
if os.path.exists(fc_cap_path) and cap is not None:
    save_all_forecasts(fc_cap_path, cap, 'capacity')

# 5. Combine available forecasts into a table (unchanged)
frames = []
if os.path.exists(fc_gen_path):
    try:
        f = pd.read_csv(fc_gen_path)
        frames.append(f.assign(type='generation'))
    except Exception:
        pass
if os.path.exists(fc_cap_path):
    try:
        f = pd.read_csv(fc_cap_path)
        frames.append(f.assign(type='capacity'))
    except Exception:
        pass

if frames:
    out = pd.concat(frames, axis=0, ignore_index=True)
    out_path = os.path.join(OUT_DIR, 'forecast_tables.csv')
    out.to_csv(out_path, index=False)
    print('Saved', out_path)

print('Showcase generation complete.')
