# Clean Energy — Canada Renewable Energy Forecasts

This repository contains a reproducible analysis pipeline and forecast artifacts for Canadian renewable energy capacity and generation (2015–2024), using the IRENA dataset. The goal is to provide transparent, reproducible short-term forecasts and visualizations to support planning and stakeholder communication.

## Repository contents (high level)
- `cleaned_capacity_data.csv` — cleaned and pivoted capacity data (years x technologies).
- `cleaned_generation_data.csv` — cleaned and pivoted generation data (years x technologies).
- `Data-Ingestion.ipynb` — notebook used to ingest, clean, and pivot raw IRENA data.
- `arima_forecast.ipynb` — notebook to fit ARIMA/SARIMAX models and produce 5-year forecasts.
- `generate_showcase.py` — script to generate shareable PNGs and combined forecast tables under `showcase/`.
- `linkedin_post.md` — suggested LinkedIn post summarizing technical insights and artifacts.

## Quick start
1. Clone the repository and change directory:

```bash
git clone <your-repo-url>
cd clean-energy
```

2. Create a Python environment and install dependencies (example using pip):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install the minimal set:

```bash
pip install pandas matplotlib seaborn numpy statsmodels pmdarima
```

## Running the notebooks
- Open and run `Data-Ingestion.ipynb` to reproduce the cleaned CSV files (this notebook reads the raw IRENA extract and writes `cleaned_capacity_data.csv` and `cleaned_generation_data.csv`).
- Open and run `arima_forecast.ipynb` to fit ARIMA/SARIMAX models over each technology series and produce `generation_forecasts.csv` and `capacity_forecasts.csv`.

## Generating showcase images and tables
After running the forecast notebook (or if forecast CSVs are already present), create shareable visuals with:

```bash
python generate_showcase.py
```

This will produce a `showcase/` directory with:
- per-technology forecast PNGs in `showcase/forecasts/generation/` and `showcase/forecasts/capacity/` (square images optimized for LinkedIn).
- combined grid images `showcase/forecasts_generation_grid.png` and `showcase/forecasts_capacity_grid.png`.
- summary plots (`capacity_trends.png`, `generation_trends.png`, `top_tech_share.png`) and a combined `forecast_tables.csv` if forecast CSVs exist.

## Notes on reproducibility and environment
- The notebook uses `pmdarima.auto_arima` for automatic order selection when available; a `statsmodels` SARIMAX fallback is included to prevent failures in environments where `pmdarima` binary wheels are incompatible with installed `numpy`.
- For full reproducibility, pin package versions in `requirements.txt` (recommended versions: pandas>=1.4, numpy>=1.24, statsmodels>=0.14, pmdarima>=2.2).

## Suggested workflow
1. Run `Data-Ingestion.ipynb` to produce cleaned CSVs.
2. Run `arima_forecast.ipynb` to produce forecasts.
3. Run `python generate_showcase.py` to create images and tables for sharing.

## Notes on modeling
- The ARIMA approach in `arima_forecast.ipynb` is configured for annual data (one observation per year). It provides a defensible 5-year baseline but doesn't capture intra-year seasonality. Consider monthly/quarterly models and exogenous variables for higher-fidelity forecasts.

## Credits
- Ruchir Attri — time-series modeling and forecasting (ARIMA/SARIMAX notebooks, plotting, showcase generator).
- Kaustubh Pandit — data engineering and exploratory data analysis (data ingestion notebook, pivot tables, EDA visualizations).

## License & contribution
This repository is intended for collaborative research and demonstration. Please open issues or pull requests on GitHub for contributions, improvements, or questions.

## Contact
For questions or follow-up, reach out via the GitHub repo or email (see repository owner profile).
