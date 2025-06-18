import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("climate_app/static/data")

# --- Fix name mismatches between GeoJSON and OWID data ---
NAME_FIXES = {
    "Unites States": "United States of America",
    "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Cote d'Ivoire": "Côte d'Ivoire"
}

def format_temperature():
    df = pd.read_csv(DATA_DIR / "temperature.csv", skiprows=1)
    df = df[['Year', 'J-D']].dropna()
    df.columns = ['Year', 'Anomaly']
    df.to_csv(DATA_DIR / "formatted_temperature.csv", index=False)
    print("✅ temperature.csv formatted.")

def format_co2():
    df = pd.read_csv(DATA_DIR / "owid-co2-data.csv")
    df.columns = [col.strip().lower() for col in df.columns]
    df = df[['entity', 'year', 'annual co₂ emissions']].dropna()
    df.columns = ['Country', 'Year', 'CO2']
    df.to_csv(DATA_DIR / "formatted_co2.csv", index=False)

    # Build JSON by year
    data = {}
    for _, row in df.iterrows():
        year = str(int(row["Year"]))
        country = NAME_FIXES.get(row["Country"], row["Country"])
        if year not in data:
            data[year] = {}
        data[year][country] = float(row["CO2"])  # preserve decimal

    with open(DATA_DIR / "co2_by_year.json", "w") as f:
        json.dump(data, f, indent=2)

    years = sorted({int(y) for y in data})
    with open(DATA_DIR / "co2_year_range.json", "w") as f:
        json.dump({"min_year": years[0], "max_year": years[-1]}, f, indent=2)

    print("✅ co2_by_year.json and co2_year_range.json created.")

def format_disasters():
    df = pd.read_excel(DATA_DIR / "climate_disaster.xlsx", engine='openpyxl')
    df = df[df['Disaster Type'].isin(['Flood', 'Drought', 'Wildfire'])]
    df_grouped = df.groupby(['Start Year', 'Disaster Type']).size().unstack(fill_value=0)
    df_grouped.reset_index(inplace=True)
    df_grouped.columns.name = None
    df_grouped.columns = ['Year'] + list(df_grouped.columns[1:])
    df_grouped.to_csv(DATA_DIR / "formatted_disasters.csv", index=False)
    print("✅ climate_disaster.xlsx formatted.")

if __name__ == "__main__":
    format_temperature()
    format_co2()
    format_disasters()
    print("🎉 All data formatted and saved.")
