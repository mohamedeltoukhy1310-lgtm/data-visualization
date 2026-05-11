# 🦠 COVID-19 Global Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14%2B-lightblue)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-orange)](https://plotly.com/python/)

**Interactive web dashboard** for exploring COVID-19 metrics (cases, deaths, vaccinations) across **countries and continents**. Powered by [Our World in Data](https://ourworldindata.org/coronavirus) dataset, featuring **13+ dynamic Plotly charts**, real-time KPIs, and intuitive filters.

## ✨ Features
- **Interactive Controls**: Filter by country, continent, metric (cases/deaths/vaccination), date range.
- **Live KPIs**: Total cases, deaths, death rate, vaccination % for selected country.
- **Rich Visualizations**:
  | Chart Type | Description |
  |------------|-------------|
  | Bar (vertical/horizontal) | Top 10 countries by cases |
  | Stacked/Clustered Bars | Cases vs vaccinations/deaths/population by continent |
  | Scatter | GDP per capita vs cases |
  | Bubble | Population density vs cases (size = population) |
  | Histogram | Death rate distribution |
  | Box/Violin | Vaccination rates, cases per million by continent |
  | Line/Area | Trends (e.g., new cases over time) |
- **Dark Theme**: Professional Plotly dark mode UI.
- **Responsive**: Grid layout adapts to screen size.

## 🚀 Quick Start
1. **Setup Virtual Environment** (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Download Data**:
   - Get latest [OWID COVID data CSV](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv)
   - Place as `data/owid-covid-data.csv`

4. **Preprocess Data**:
   ```
   python preprocess.py
   ```
   Generates: `cleaned_data.csv`, `scatter.csv`, `bubble.csv`, `hist_data.csv`, `box_data.csv`.

5. **Run Dashboard**:
   ```
   python app.py
   ```
   Open [http://localhost:8053](http://localhost:8053) 🎉

## 📁 Project Structure
```
d:/Team03_COVID19Analysis/
├── app.py                 # Dash app + charts
├── preprocess.py          # Data pipeline
├── requirements.txt       # Dependencies
├── README.md              # This file
├── data/                  # Input/output CSVs
│   ├── owid-covid-data.csv  # Raw (download)
│   ├── cleaned_data.csv     # Main dataset
│   └── scatter.csv          # etc.
├── notebooks/             # EDA
│   └── preprocessing.ipynb
└── assets/                # Static files
```

## 📊 Dataset Description
**Our World in Data (OWID) COVID-19 Dataset**  
- **Source**: [OWID COVID-19](https://ourworldindata.org/coronavirus-source-data) ([raw CSV](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv))
- **Coverage**: Daily time-series for 200+ countries/territories (2020–present).
- **Key Columns Used**:
  | Column | Description |
  |--------|-------------|
  | `date` | Observation date |
  | `location` | Country name |
  | `continent` | Continent |
  | `total_cases` | Cumulative confirmed cases |
  | `total_deaths` | Cumulative deaths |
  | `people_vaccinated` | People received at least 1 dose |
  | `population` | Country population |
  | `gdp_per_capita` | Economic indicator |
  | `population_density` | People per km² |
- **Derived Metrics** (`preprocess.py`):
  - `death_rate = (total_deaths / total_cases) * 100`
  - `vaccination_rate = (people_vaccinated / population) * 100`
  - `cases_per_million = (total_cases / population) * 1e6`
- **Processing Steps**:
  1. Load raw CSV.
  2. Filter countries (exclude aggregates like 'World').
  3. Compute metrics, handle missing values.
  4. Export: `cleaned_data.csv` (main), `scatter.csv`, `bubble.csv`, etc.

**Update**: Download latest CSV to `data/owid-covid-data.csv` and run `python preprocess.py`.

## 🛠️ Tech Stack
- **Backend**: Python 3.8+, Pandas
- **Frontend**: Dash, Plotly Express/Graph Objects
- **Port**: 8053 (configurable)

## 📸 Screenshots
*(Run the app for live demo; charts update dynamically!)*

## 👥 Team Member Roles (Team 03)
| Member | Role |
|--------|------|
| [Your Name] | Project Lead / Dashboard UI |
| [Your Name] | Data Preprocessing |
| [Your Name] | Visualizations & Charts |
| [Your Name] | Deployment & Documentation |

*(Update with actual team names)*

## 🤝 Contributing
1. Fork & clone.
2. Create feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add some feature'`).
4. Push & PR.

Issues? [Open a ticket](https://github.com/user/repo/issues/new)!

## 📄 License
MIT License © 2024 Team 03.

---

⭐ **Star this repo if useful!** Built by **Team 03**.

