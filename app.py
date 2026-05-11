import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import traceback

print("Loading data...")

# =============================================
# DATA LOADING
# =============================================
df = pd.read_csv("data/cleaned_data.csv")
df["date"] = pd.to_datetime(df["date"])
df["continent"] = df["continent"].astype(object)

scatter = pd.read_csv("data/scatter.csv")
scatter["date"] = pd.to_datetime(scatter["date"])
scatter["continent"] = scatter["continent"].astype(object)

bubble = pd.read_csv("data/bubble.csv")
bubble["date"] = pd.to_datetime(bubble["date"])
bubble["continent"] = bubble["continent"].astype(object)

hist_df = pd.read_csv("data/hist_data.csv")
box_df = pd.read_csv("data/box_data.csv")
box_df["continent"] = box_df["continent"].astype(object)


def normalize_continent_column(frame):
    if "continent" in frame.columns:
        frame["continent"] = frame["continent"].astype(str).str.strip()
        frame.loc[frame["continent"].isin(["", "nan", "None"]), "continent"] = pd.NA

# Safe defaults
if "vaccination_rate" not in df.columns:
    df["vaccination_rate"] = 0
if "new_cases" not in df.columns:
    df["new_cases"] = 0

normalize_continent_column(df)
normalize_continent_column(scatter)
normalize_continent_column(bubble)
normalize_continent_column(box_df)

countries = sorted(df["location"].unique())
continents = ["All"] + sorted(df["continent"].dropna().unique())
dates = sorted(df["date"].dropna().unique())

print("Data loaded successfully")

# =============================================
# DASH APP
# =============================================
app = Dash(__name__)
app.title = "COVID-19 Dashboard"

app.layout = html.Div(
    style={
        "backgroundColor": "#0f172a",
        "color": "white",
        "padding": "20px",
        "fontFamily": "Arial, sans-serif",
    },
    children=[
        html.H1("COVID-19 Global Analysis Dashboard", style={"textAlign": "center"}),
        html.P(
            "Explore pandemic metrics across countries and continents",
            style={"textAlign": "center", "color": "#cbd5e1"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Country", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="country",
                            options=[{"label": i, "value": i} for i in countries],
                            value=countries[0],
                            clearable=False,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "200px", "marginRight": "10px"},
                ),
                html.Div(
                    [
                        html.Label("Continent", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="continent",
                            options=[{"label": i, "value": i} for i in continents],
                            value="All",
                            clearable=False,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "200px", "marginRight": "10px"},
                ),
                html.Div(
                    [
                        html.Label("Metric", style={"fontWeight": "bold"}),
                        dcc.RadioItems(
                            id="metric",
                            options=[
                                {"label": "Cases", "value": "total_cases"},
                                {"label": "Deaths", "value": "total_deaths"},
                                {"label": "Vaccination %", "value": "vaccination_rate"},
                            ],
                            value="total_cases",
                            inline=True,
                            style={"display": "flex", "gap": "15px"},
                        ),
                    ],
                    style={"flex": "1", "minWidth": "250px"},
                ),
            ],
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "15px",
                "marginBottom": "20px",
                "padding": "15px",
                "backgroundColor": "#1e293b",
                "borderRadius": "10px",
            },
        ),
        html.Div(
            [
                html.Label(
                    "Select Date Range (for Scatter/Bubble)",
                    style={"fontWeight": "bold"},
                ),
                dcc.RangeSlider(
                    id="date_range",
                    min=0,
                    max=len(dates) - 1,
                    value=[max(0, len(dates) - 30), len(dates) - 1],
                    step=1,
                    marks={
                        0: dates[0].strftime("%Y"),
                        len(dates) - 1: dates[-1].strftime("%Y"),
                    },
                ),
            ],
            style={
                "padding": "15px",
                "backgroundColor": "#1e293b",
                "borderRadius": "10px",
                "marginBottom": "20px",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Cases"),
                        html.H2(id="k1"),
                    ],
                    style={
                        "flex": "1",
                        "padding": "15px",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "10px",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    [
                        html.H4("Deaths"),
                        html.H2(id="k2"),
                    ],
                    style={
                        "flex": "1",
                        "padding": "15px",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "10px",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    [
                        html.H4("Death Rate"),
                        html.H2(id="k3"),
                    ],
                    style={
                        "flex": "1",
                        "padding": "15px",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "10px",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    [
                        html.H4("Vaccination %"),
                        html.H2(id="k4"),
                    ],
                    style={
                        "flex": "1",
                        "padding": "15px",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "10px",
                        "textAlign": "center",
                    },
                ),
            ],
            style={"display": "flex", "gap": "15px", "marginBottom": "20px", "flexWrap": "wrap"},
        ),
        html.Div(
            id="charts-container",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(500px, 1fr))",
                "gap": "15px",
            },
        ),
    ],
)


# =============================================
# CALLBACK
# =============================================
@app.callback(
    Output("k1", "children"),
    Output("k2", "children"),
    Output("k3", "children"),
    Output("k4", "children"),
    Output("charts-container", "children"),
    Input("country", "value"),
    Input("metric", "value"),
    Input("date_range", "value"),
    Input("continent", "value"),
)
def update_dashboard(country, metric, date_indices, selected_continent):
    try:
        valid_continents = set(df["continent"].dropna().unique())
        if selected_continent not in valid_continents and selected_continent != "All":
            selected_continent = "All"

        start_idx = max(0, date_indices[0]) if isinstance(date_indices, (list, tuple)) else 0
        end_idx = (
            min(len(dates) - 1, date_indices[1])
            if isinstance(date_indices, (list, tuple))
            else len(dates) - 1
        )
        start_date = dates[start_idx]
        end_date = dates[end_idx]

        # Keep country KPIs independent from continent dropdown.
        # A user can compare any country while filtering regional charts separately.
        country_data = df[df["location"] == country]
        date_filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        if selected_continent != "All":
            date_filtered = date_filtered[date_filtered["continent"] == selected_continent]

        cases = int(country_data["total_cases"].max()) if not country_data.empty else 0
        deaths = int(country_data["total_deaths"].max()) if not country_data.empty else 0
        death_rate = (deaths / (cases + 1) * 100) if cases > 0 else 0
        vacc_rate = country_data["vaccination_rate"].max() if not country_data.empty else 0

        continent_data = (
            date_filtered.groupby("continent", as_index=False).agg(
                {
                    "total_cases": "sum",
                    "total_deaths": "sum",
                    "total_vaccinations": "sum",
                    "people_vaccinated": "sum",
                    "population": "sum",
                }
            )
            if not date_filtered.empty
            else pd.DataFrame()
        )

        # Bar charts (G1, G2): always by country (top 10 in selected scope)
        top_countries_cases = (
            date_filtered.groupby("location", as_index=False)["total_cases"]
            .sum()
            .sort_values("total_cases", ascending=False)
            .head(10)
            if not date_filtered.empty
            else pd.DataFrame()
        )
        bar_scope = (
            "Worldwide"
            if selected_continent == "All"
            else f"in {selected_continent}"
        )

        charts = []

        if not top_countries_cases.empty:
            g1 = px.bar(
                top_countries_cases,
                x="location",
                y="total_cases",
                title=f"Top 10 Countries by Total Cases ({bar_scope})",
                labels={"location": "Country", "total_cases": "Total Cases"},
            )
        else:
            g1 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            )

        g1.update_layout(
            xaxis_title="Country",
            yaxis_title="Total Cases",
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g1))

        if not top_countries_cases.empty:
            g2 = px.bar(
                top_countries_cases.sort_values("total_cases"),
                x="total_cases",
                y="location",
                orientation="h",
                title=f"Top 10 Countries by Total Cases ({bar_scope}) — Horizontal",
                labels={"location": "Country", "total_cases": "Total Cases"},
            )
        else:
            g2 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            )

        g2.update_layout(
            xaxis_title="Total Cases",
            yaxis_title="Country",
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g2))

        if not continent_data.empty:
            g3 = go.Figure(
                data=[
                    go.Bar(
                        name="Cases",
                        x=continent_data["continent"],
                        y=continent_data["total_cases"],
                    ),
                    go.Bar(
                        name="Vaccinations",
                        x=continent_data["continent"],
                        y=continent_data["total_vaccinations"],
                    ),
                ]
            )
            g3.update_layout(
                barmode="stack",
                title="Cases and Vaccinations (Stacked)",
                xaxis_title="Continent",
                yaxis_title="Count",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        else:
            g3 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(
                title="Cases and Vaccinations (Stacked)",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        charts.append(dcc.Graph(figure=g3))

        if not continent_data.empty:
            g4 = go.Figure(
                data=[
                    go.Bar(
                        name="Deaths",
                        x=continent_data["total_deaths"],
                        y=continent_data["continent"],
                        orientation="h",
                    ),
                    go.Bar(
                        name="Vaccinated",
                        x=continent_data["people_vaccinated"],
                        y=continent_data["continent"],
                        orientation="h",
                    ),
                ]
            )
            g4.update_layout(
                barmode="stack",
                title="Deaths and Vaccinated (Stacked)",
                xaxis_title="Count",
                yaxis_title="Continent",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        else:
            g4 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(
                title="Deaths and Vaccinated (Stacked)",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        charts.append(dcc.Graph(figure=g4))

        if not continent_data.empty:
            g5 = go.Figure(
                data=[
                    go.Bar(
                        name="Cases",
                        x=continent_data["continent"],
                        y=continent_data["total_cases"],
                    ),
                    go.Bar(
                        name="Deaths",
                        x=continent_data["continent"],
                        y=continent_data["total_deaths"],
                    ),
                ]
            )
            g5.update_layout(
                barmode="group",
                title="Cases vs Deaths (Clustered)",
                xaxis_title="Continent",
                yaxis_title="Count",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        else:
            g5 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(
                title="Cases vs Deaths (Clustered)",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        charts.append(dcc.Graph(figure=g5))

        if not continent_data.empty:
            g6 = go.Figure(
                data=[
                    go.Bar(
                        name="Cases",
                        x=continent_data["total_cases"],
                        y=continent_data["continent"],
                        orientation="h",
                    ),
                    go.Bar(
                        name="Population",
                        x=continent_data["population"],
                        y=continent_data["continent"],
                        orientation="h",
                    ),
                ]
            )
            g6.update_layout(
                barmode="group",
                title="Cases and Population (Clustered)",
                xaxis_title="Count",
                yaxis_title="Continent",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        else:
            g6 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(
                title="Cases and Population (Clustered)",
                template="plotly_dark",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font_color="white",
            )
        charts.append(dcc.Graph(figure=g6))

        scatter_data = scatter[
            (scatter["date"] >= start_date) & (scatter["date"] <= end_date)
        ]
        if (
            selected_continent != "All"
            and "continent" in scatter_data.columns
            and selected_continent in set(scatter_data["continent"].dropna().unique())
        ):
            scatter_data = scatter_data[scatter_data["continent"] == selected_continent]

        if not scatter_data.empty:
            g7 = px.scatter(
                scatter_data,
                x="gdp_per_capita",
                y="total_cases",
                color="continent",
                title="GDP per Capita vs Total Cases",
                labels={
                    "gdp_per_capita": "GDP per Capita (USD)",
                    "total_cases": "Total Cases",
                },
            )
        else:
            g7 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title="GDP per Capita vs Total Cases")

        g7.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
            xaxis_title="GDP per Capita (USD)",
            yaxis_title="Total Cases",
        )
        charts.append(dcc.Graph(figure=g7))

        bubble_data = bubble[
            (bubble["date"] >= start_date) & (bubble["date"] <= end_date)
        ]
        if (
            selected_continent != "All"
            and "continent" in bubble_data.columns
            and selected_continent in set(bubble_data["continent"].dropna().unique())
        ):
            bubble_data = bubble_data[bubble_data["continent"] == selected_continent]

        if not bubble_data.empty:
            g8 = px.scatter(
                bubble_data,
                x="population_density",
                y="total_cases",
                size="population",
                color="continent",
                title="Population Density vs Total Cases (Bubble)",
                labels={
                    "population_density": "Population Density (per km²)",
                    "total_cases": "Total Cases",
                    "population": "Population",
                },
            )
        else:
            g8 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title="Population Density vs Total Cases (Bubble)")

        g8.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
            xaxis_title="Population Density (per km²)",
            yaxis_title="Total Cases",
        )
        charts.append(dcc.Graph(figure=g8))

        hist_data = hist_df[hist_df["location"] == country] if "location" in hist_df.columns else hist_df
        if not hist_data.empty:
            g9 = px.histogram(
                hist_data,
                x="death_rate",
                nbins=20,
                title=f"Death Rate Distribution - {country}",
                labels={"death_rate": "Death Rate"},
            )
        else:
            g9 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title=f"Death Rate Distribution - {country}")

        g9.update_layout(
            xaxis_title="Death Rate",
            yaxis_title="Frequency",
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g9))

        box_data_plot = box_df.copy()
        if (
            selected_continent != "All"
            and "continent" in box_data_plot.columns
            and selected_continent in set(box_data_plot["continent"].dropna().unique())
        ):
            box_data_plot = box_data_plot[box_data_plot["continent"] == selected_continent]

        if not box_data_plot.empty and "vaccination_rate" in box_data_plot.columns:
            g10 = px.box(
                box_data_plot,
                x="continent",
                y="vaccination_rate",
                title="Vaccination Rate Distribution",
                labels={"continent": "Continent", "vaccination_rate": "Vaccination Rate"},
            )
        else:
            g10 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title="Vaccination Rate Distribution")

        g10.update_layout(
            xaxis_title="Continent",
            yaxis_title="Vaccination Rate",
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g10))

        if not box_data_plot.empty and "cases_per_million" in box_data_plot.columns:
            g11 = px.violin(
                box_data_plot,
                x="continent",
                y="cases_per_million",
                box=True,
                title="Cases per Million Distribution",
                labels={"continent": "Continent", "cases_per_million": "Cases per Million"},
            )
        else:
            g11 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title="Cases per Million Distribution")

        g11.update_layout(
            xaxis_title="Continent",
            yaxis_title="Cases per Million",
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g11))

        line_data = df[df["location"] == country].sort_values("date")
        if not line_data.empty and metric in line_data.columns:
            g12 = px.line(
                line_data,
                x="date",
                y=metric,
                title=f'{metric.replace("_", " ").title()} Trend - {country}',
                labels={
                    "date": "Date",
                    metric: metric.replace("_", " ").title(),
                },
            )
        else:
            g12 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title=f'{metric.replace("_", " ").title()} Trend - {country}')

        g12.update_layout(
            xaxis_title="Date",
            yaxis_title=metric.replace("_", " ").title(),
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g12))

        if not line_data.empty and "new_cases" in line_data.columns:
            g13 = px.area(
                line_data,
                x="date",
                y="new_cases",
                title=f"New Cases Daily - {country}",
                labels={"date": "Date", "new_cases": "New Cases"},
            )
        else:
            g13 = go.Figure().add_annotation(
                text="No Data", x=0.5, y=0.5, showarrow=False
            ).update_layout(title=f"New Cases Daily - {country}")

        g13.update_layout(
            xaxis_title="Date",
            yaxis_title="New Cases",
            template="plotly_dark",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font_color="white",
        )
        charts.append(dcc.Graph(figure=g13))

        return (
            f"{cases:,}",
            f"{deaths:,}",
            f"{death_rate:.2f}%",
            f"{vacc_rate:.1f}%",
            charts,
        )

    except Exception as e:
        print("Callback failed with traceback:")
        print(traceback.format_exc())
        return (
            "Error",
            "Error",
            "Error",
            "Error",
            [
                html.Div(
                    f"Dashboard Error: {str(e)}",
                    style={"color": "red", "padding": "20px"},
                )
            ],
        )


if __name__ == "__main__":
    app.run(debug=False, port=8053, use_reloader=False)
