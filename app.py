import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd


from src.app_utility.dates import get_most_recent_august_start
from src.app_utility.create_output_tables import (
    get_team_and_league_data,
    get_team_and_league_data_filtered_summarised,
)
from src.data_prep.load_data import get_league_data

external_stylesheets = [dbc.themes.BOOTSTRAP]
style_cell_tables = {
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "paddingLeft": "10px",
    "paddingRight": "10px",
}
style_header_tables = {"fontWeight": "bold"}
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Pre Processing
latest_season_start = get_most_recent_august_start()


intro = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    width=10, children=[html.H3(children=["FPL Tool | League History"])]
                ),
                dbc.Col(
                    width=2,
                    children=[
                        html.Div(
                            children=[
                                html.Img(
                                    src="assets/pwt.png", style={"max-height": "100%"}
                                )
                            ],
                            style={
                                "height": "50px",
                                "overflow": "hidden",
                                "text-align": "right",
                            },
                        )
                    ],
                ),
            ]
        )
    ]
)

select_inputs = html.Div(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    width=6,
                    children=[
                        html.H6("Enter League ID"),
                        dcc.Input(
                            id="league-id",
                            type="number",
                            min=0,
                            max=999999999,
                            step=1,
                            style={"width": "90%"},
                        ),
                        html.Div(
                            "This can be obtained from the league URL:",
                            style={"font-style": "italic"},
                        ),
                        html.Div(
                            "https://fantasy.premierleague.com/leagues/XXXXXX/standings/c",
                            style={"font-style": "italic"},
                        ),
                    ],
                ),
                dbc.Col(
                    width=6,
                    children=[
                        html.H6("Select League Starting Season"),
                        dcc.RangeSlider(
                            id="year-select",
                            count=1,
                            min=2002,
                            max=latest_season_start,
                            step=1,
                            value=[2002],
                            marks={
                                year: str(year) if year % 5 == 0 else ""
                                for year in range(2002, latest_season_start + 1)
                            },
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                ),
            ]
        ),
    ]
)

league_summary_table = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(children=[html.H3(id="league-name")]),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    width=4,
                    children=[
                        dcc.Loading(
                            type="circle",
                            children=[html.Div(id="summary-kpis", children=[""])],
                        )
                    ],
                ),
            ]
        ),
        dbc.Row(html.Hr()),
        dbc.Row(
            [
                dbc.Col(children=[html.H3(id="winner-data-header")]),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    width=4,
                    children=[
                        dcc.Loading(
                            type="circle",
                            children=[html.Div(id="winner-data", children=[""])],
                        )
                    ],
                ),
            ]
        ),
    ]
)


# Enclosing both intro and select_inputs within a grey box
container = dbc.Card(
    [
        dbc.CardBody([intro, select_inputs]),
    ],
    style={"background-color": "#f8f9fa", "padding": "20px", "margin": "20px"},
)

app.title = "FPL - League History"
app.layout = dbc.Container([container, league_summary_table])


@app.callback(
    [
        Output(component_id="league-name", component_property="children"),
        Output(component_id="summary-kpis", component_property="children"),
        Output(component_id="winner-data-header", component_property="children"),
        Output(component_id="winner-data", component_property="children"),
    ],
    Input(component_id="league-id", component_property="value"),
    Input(component_id="year-select", component_property="value"),
)
def dash_get_team_and_league_data(league_id, season_start_year):
    """
    This takes the league_id as the dashboard input and returns the data for the league
    """

    (
        league_data,
        manager_information,
        team_ids,
        final_gw_finished,
        season_history,
        season_current_df,
        season_history_df,
    ) = get_team_and_league_data(league_id=league_id)

    (
        league_name,
        league_summary_kpis,
        seasons_top_three_output,
        titles_won_summary_output,
        season_current_df_output,
        season_history_df_output,
        all_time_table_output,
    ) = get_team_and_league_data_filtered_summarised(
        league_data=league_data,
        manager_information=manager_information,
        team_ids=team_ids,
        season_current_df=season_current_df,
        season_history_df=season_history_df,
        season_start_year=season_start_year[0],
    )

    league_summary_kpis.reset_index(inplace=True)
    league_summary_kpis.columns = ["", league_name]
    league_summary_kpis_dash = dash_table.DataTable(
        id="df",
        columns=[{"name": i, "id": i} for i in league_summary_kpis.columns],
        data=league_summary_kpis.to_dict(orient="records"),
        style_cell=style_cell_tables,
        style_header=style_header_tables,
    )

    # league_summary_kpis.reset_index(inplace=True)
    league_summary_kpis.columns = ["", league_name]
    league_summary_kpis_dash = dash_table.DataTable(
        id="df",
        columns=[{"name": i, "id": i} for i in league_summary_kpis.columns],
        data=league_summary_kpis.to_dict(orient="records"),
        style_cell=style_cell_tables,
        style_header=style_header_tables,
    )
    titles_won_summary_output_dash_header = "Champions"
    titles_won_summary_output_dash = dash_table.DataTable(
        id="df",
        columns=[{"name": i, "id": i} for i in titles_won_summary_output.columns],
        data=titles_won_summary_output.to_dict(orient="records"),
        style_cell=style_cell_tables,
        style_header=style_header_tables,
    )

    titles_won_summary_output

    return (
        league_name,
        league_summary_kpis_dash,
        titles_won_summary_output_dash_header,
        titles_won_summary_output_dash,
    )


if __name__ == "__main__":
    app.run_server(debug=False)
