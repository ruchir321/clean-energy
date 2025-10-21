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

# 4. Example ARIMA forecast plot if forecasts exist
fc_gen_path = 'generation_forecasts.csv'
fc_cap_path = 'capacity_forecasts.csv'

if os.path.exists(fc_gen_path) and gen is not None:
    try:
        fc_gen = pd.read_csv(fc_gen_path, parse_dates=['Year'], index_col='Year')
        # pick a sample technology column that exists in both
        common = [c for c in fc_gen.columns if c in gen.columns]
        if common:
            tech = common[0]
            fig, ax = plt.subplots(figsize=(10,5))
            # historical
            ax.plot(gen.index.year, gen[tech], marker='o', label='Historical', color='#1f77b4')
            # forecast
            ax.plot(fc_gen.index.year, fc_gen[tech], marker='o', linestyle='--', label='Forecast', color='#ff7f0e')
            ax.set_title(f'Historical and 5-year Forecast: {tech}')
            ax.set_xlabel('Year')
            ax.set_ylabel('Value')
            ax.legend()
            save_fig(fig, 'arima_forecast_example.png')
            plt.close(fig)
    except Exception as e:
        print('Could not create forecast example plot:', e)

# 5. Combine available forecasts into a table
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
