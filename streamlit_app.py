import streamlit as st
import base64
import altair as alt
import pandas as pd

st.set_page_config(
    page_title="FPL League History",
    page_icon=":soccer:",
)

# Import functions
from src.app_utility.app_tools import (
    get_most_recent_august_start,
    remove_starting_the,
)
from src.app_utility.create_output_tables import (
    get_team_and_league_data,
    get_team_and_league_data_filtered_summarised,
)

# Hide deploy button
st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Pre Processing
latest_season_start = get_most_recent_august_start()


def main():
    try:
        st.title("FPL League History")

        # Add github link and logo
        LOGO_IMAGE = "assets//pwt.png"

        st.markdown(
            """
            <style>
            .container {
                display: flex;
            }
            .logo-text {
                font-weight: 0 !important;
                font-size: 15px !important;
                padding-top: 0px !important;
                margin-left: 0px;
                font-style: italic; 
            }
            .logo-img {
                float:right;
                width: 28px;
                height: 28px;
                margin-right: 8px; 
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="container">
                <img class="logo-img" src="data:assets//pwt.png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
                <p class="logo-text"><a href="https://github.com/edward-farragher/fpl-league-history">GitHub Repo</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Dashboard Information"):
            st.markdown("""
                This dashboard displays summary statistics and historic league tables for a selected mini league.

                Data comes solely from the _Previous Seasons_ section of each team's _Gameweek History_.  
                - All current league teams are included.  
                - Teams that were previously in the league but are no longer are not included.  
                - Teams not previously in this league but with FPL history will be displayed in past seasons.  
                - The starting season year can be adjusted to choose how far back the history goes. 
                """)

        # Input number
        league_id = st.number_input(
            "Enter League ID",
            step=1,
            format="%d",
            value=None,
            help="This is located in the league URL: `https://fantasy.premierleague.com/leagues/XXXXXX/standings/c`",
        )

        # Slider for another number
        season_start_year = st.slider(
            "Select League Starting Season",
            min_value=2000,
            max_value=latest_season_start,
            value=2002,
            step=1,
            help="Select the season start year to only select data after. For example if the league has only been running since a specific season, or there is a specific season where all teams were participation from",
        )

        # Button to trigger function execution
        if st.button("Generate League Data :soccer:"):
            # Call your function with the input numbers

            # Get data

            with st.spinner(text="Getting league data..."):
                (
                    league_data,
                    manager_information,
                    team_ids,
                    final_gw_finished,
                    season_history,
                    season_current_df,
                    season_history_df,
                    current_gamekweek,
                    team_data,
                ) = get_team_and_league_data(league_id=int(league_id))

                (
                    league_name,
                    league_summary_kpis,
                    seasons_top_three_output,
                    titles_won_summary_output,
                    season_overview_output,
                    season_current_df_output,
                    season_history_df_output,
                    all_time_table_output,
                ) = get_team_and_league_data_filtered_summarised(
                    league_data=league_data,
                    manager_information=manager_information,
                    team_ids=team_ids,
                    season_current_df=season_current_df,
                    season_history_df=season_history_df,
                    season_start_year=season_start_year,
                    team_data=team_data,
                )

            league_summary_kpis.reset_index(inplace=True)
            league_summary_kpis.columns = ["", league_name]

            # Display the output tables
            st.header(league_name, divider="grey")

            # Summary KPIs
            st.dataframe(data=league_summary_kpis, hide_index=True)

            # Champions total
            st.subheader("Champions", divider="grey")
            data_champions, chart_champions = st.tabs(["📃Data", "📈 Chart"])

            with data_champions:
                st.dataframe(titles_won_summary_output, hide_index=True)

            with chart_champions:
                title = alt.TitleParams("Seasons Won", anchor="middle")
                chart = (
                    alt.Chart(titles_won_summary_output, title=title)
                    .mark_bar()
                    .encode(
                        x=alt.X("Winners", title=""),
                        y=alt.Y("Team", title="").sort("-x"),
                    )
                )

                chart = chart.configure_axis(labelLimit=1000)
                st.altair_chart(chart)

            # List of Champions
            st.subheader("List of Champions", divider="grey")
            st.markdown("*(number of titles)*")

            # Add medal icon
            prefix = "🥇 "
            seasons_top_three_output["Champions: Manager"] = seasons_top_three_output[
                "Champions: Manager"
            ].apply(lambda x: prefix + x if x else x)

            prefix = "🥈 "
            seasons_top_three_output["Runners-up: Manager"] = seasons_top_three_output[
                "Runners-up: Manager"
            ].apply(lambda x: prefix + x if x else x)

            prefix = "🥉 "
            seasons_top_three_output["Third Place: Manager"] = seasons_top_three_output[
                "Third Place: Manager"
            ].apply(lambda x: prefix + x if x else x)

            st.dataframe(seasons_top_three_output, hide_index=True)

            league_name_starting_the_removed = remove_starting_the(text=league_name)

            # All time table
            st.subheader(f"All time {league_name_starting_the_removed}", divider="grey")
            st.dataframe(all_time_table_output, hide_index=True)

            # Team summary statistics
            st.subheader("Team Summary Statistics", divider="grey")
            st.dataframe(season_overview_output.T, hide_index=True)

            # Current season
            if final_gw_finished:
                season_current_df_output_dash_header = f"Current Season (Completed)"
            else:
                season_current_df_output_dash_header = (
                    f"Current Season (GW {current_gamekweek})"
                )

            if current_gamekweek != "Season Not Started":
                st.subheader(season_current_df_output_dash_header, divider="grey")
                st.dataframe(season_current_df_output, hide_index=True)

            # Season history
            season_history_df_output_dash_header = (
                f"Previous {league_name_starting_the_removed} Seasons"
            )
            st.subheader(f"{season_history_df_output_dash_header}", divider="grey")
            data_history, chart_history = st.tabs(["📃Data", "📈 Chart"])
            with data_history:
                # Convert DataFrame to CSV
                csv = season_history_df_output.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download League Standings by Season as CSV",
                    data=csv,
                    file_name="FPL Leage History.csv",
                    mime="text/csv",
                )
                # Get past league seasons, with a seperate table for each season
                filtered_df_00 = season_history_df_output[
                    season_history_df_output["Season"] == "2000/01"
                ]
                if not filtered_df_00.empty:
                    st.markdown("**2000/01:**")
                    st.dataframe(filtered_df_00, hide_index=True)

                filtered_df_01 = season_history_df_output[
                    season_history_df_output["Season"] == "2001/02"
                ]
                if not filtered_df_01.empty:
                    st.markdown("**2001/02:**")
                    st.dataframe(filtered_df_01, hide_index=True)

                filtered_df_02 = season_history_df_output[
                    season_history_df_output["Season"] == "2002/03"
                ]
                if not filtered_df_02.empty:
                    st.markdown("**2002/03:**")
                    st.dataframe(filtered_df_02, hide_index=True)

                filtered_df_03 = season_history_df_output[
                    season_history_df_output["Season"] == "2003/04"
                ]
                if not filtered_df_03.empty:
                    st.markdown("**2003/04:**")
                    st.dataframe(filtered_df_03, hide_index=True)

                filtered_df_04 = season_history_df_output[
                    season_history_df_output["Season"] == "2004/05"
                ]
                if not filtered_df_04.empty:
                    st.markdown("**2004/05:**")
                    st.dataframe(filtered_df_04, hide_index=True)

                filtered_df_05 = season_history_df_output[
                    season_history_df_output["Season"] == "2005/06"
                ]
                if not filtered_df_05.empty:
                    st.markdown("**2005/06:**")
                    st.dataframe(filtered_df_05, hide_index=True)

                filtered_df_06 = season_history_df_output[
                    season_history_df_output["Season"] == "2006/07"
                ]
                if not filtered_df_06.empty:
                    st.markdown("**2006/07:**")
                    st.dataframe(filtered_df_06, hide_index=True)

                filtered_df_07 = season_history_df_output[
                    season_history_df_output["Season"] == "2007/08"
                ]
                if not filtered_df_07.empty:
                    st.markdown("**2007/08:**")
                    st.dataframe(filtered_df_07, hide_index=True)

                filtered_df_08 = season_history_df_output[
                    season_history_df_output["Season"] == "2008/09"
                ]
                if not filtered_df_08.empty:
                    st.markdown("**2008/09:**")
                    st.dataframe(filtered_df_08, hide_index=True)

                filtered_df_09 = season_history_df_output[
                    season_history_df_output["Season"] == "2009/10"
                ]
                if not filtered_df_09.empty:
                    st.markdown("**2009/10:**")
                    st.dataframe(filtered_df_09, hide_index=True)

                filtered_df_10 = season_history_df_output[
                    season_history_df_output["Season"] == "2010/11"
                ]
                if not filtered_df_10.empty:
                    st.markdown("**2010/11:**")
                    st.dataframe(filtered_df_10, hide_index=True)

                filtered_df_11 = season_history_df_output[
                    season_history_df_output["Season"] == "2011/12"
                ]
                if not filtered_df_11.empty:
                    st.markdown("**2011/12:**")
                    st.dataframe(filtered_df_11, hide_index=True)

                filtered_df_12 = season_history_df_output[
                    season_history_df_output["Season"] == "2012/13"
                ]
                if not filtered_df_12.empty:
                    st.markdown("**2012/13:**")
                    st.dataframe(filtered_df_12, hide_index=True)

                filtered_df_13 = season_history_df_output[
                    season_history_df_output["Season"] == "2013/14"
                ]
                if not filtered_df_13.empty:
                    st.markdown("**2013/14:**")
                    st.dataframe(filtered_df_13, hide_index=True)

                filtered_df_14 = season_history_df_output[
                    season_history_df_output["Season"] == "2014/15"
                ]
                if not filtered_df_14.empty:
                    st.markdown("**2014/15:**")
                    st.dataframe(filtered_df_14, hide_index=True)

                filtered_df_15 = season_history_df_output[
                    season_history_df_output["Season"] == "2015/16"
                ]
                if not filtered_df_15.empty:
                    st.markdown("**2015/16:**")
                    st.dataframe(filtered_df_15, hide_index=True)

                filtered_df_16 = season_history_df_output[
                    season_history_df_output["Season"] == "2016/17"
                ]
                if not filtered_df_16.empty:
                    st.markdown("**2016/17:**")
                    st.dataframe(filtered_df_16, hide_index=True)

                filtered_df_17 = season_history_df_output[
                    season_history_df_output["Season"] == "2017/18"
                ]
                if not filtered_df_17.empty:
                    st.markdown("**2017/18:**")
                    st.dataframe(filtered_df_17, hide_index=True)

                filtered_df_18 = season_history_df_output[
                    season_history_df_output["Season"] == "2018/19"
                ]
                if not filtered_df_18.empty:
                    st.markdown("**2018/19:**")
                    st.dataframe(filtered_df_18, hide_index=True)

                filtered_df_19 = season_history_df_output[
                    season_history_df_output["Season"] == "2019/20"
                ]
                if not filtered_df_19.empty:
                    st.markdown("**2019/20:**")
                    st.dataframe(filtered_df_19, hide_index=True)

                filtered_df_20 = season_history_df_output[
                    season_history_df_output["Season"] == "2020/21"
                ]
                if not filtered_df_20.empty:
                    st.markdown("**2020/21:**")
                    st.dataframe(filtered_df_20, hide_index=True)

                filtered_df_21 = season_history_df_output[
                    season_history_df_output["Season"] == "2021/22"
                ]
                if not filtered_df_21.empty:
                    st.markdown("**2021/22:**")
                    st.dataframe(filtered_df_21, hide_index=True)

                filtered_df_22 = season_history_df_output[
                    season_history_df_output["Season"] == "2022/23"
                ]
                if not filtered_df_22.empty:
                    st.markdown("**2022/23:**")
                    st.dataframe(filtered_df_22, hide_index=True)

                filtered_df_23 = season_history_df_output[
                    season_history_df_output["Season"] == "2023/24"
                ]
                if not filtered_df_23.empty:
                    st.markdown("**2023/24:**")
                    st.dataframe(filtered_df_23, hide_index=True)

                filtered_df_24 = season_history_df_output[
                    season_history_df_output["Season"] == "2024/25"
                ]
                if not filtered_df_24.empty:
                    st.markdown("**2024/25:**")
                    st.dataframe(filtered_df_24, hide_index=True)

                filtered_df_25 = season_history_df_output[
                    season_history_df_output["Season"] == "2025/26"
                ]
                if not filtered_df_25.empty:
                    st.markdown("**2025/26:**")
                    st.dataframe(filtered_df_25, hide_index=True)

                filtered_df_26 = season_history_df_output[
                    season_history_df_output["Season"] == "2026/27"
                ]
                if not filtered_df_26.empty:
                    st.markdown("**2026/27:**")
                    st.dataframe(filtered_df_26, hide_index=True)

                filtered_df_27 = season_history_df_output[
                    season_history_df_output["Season"] == "2027/28"
                ]
                if not filtered_df_27.empty:
                    st.markdown("**2027/28:**")
                    st.dataframe(filtered_df_27, hide_index=True)

                filtered_df_28 = season_history_df_output[
                    season_history_df_output["Season"] == "2028/29"
                ]
                if not filtered_df_28.empty:
                    st.markdown("**2028/29:**")
                    st.dataframe(filtered_df_28, hide_index=True)

                filtered_df_29 = season_history_df_output[
                    season_history_df_output["Season"] == "2029/30"
                ]
                if not filtered_df_29.empty:
                    st.markdown("**2029/30:**")
                    st.dataframe(filtered_df_29, hide_index=True)

                filtered_df_30 = season_history_df_output[
                    season_history_df_output["Season"] == "2030/31"
                ]
                if not filtered_df_30.empty:
                    st.markdown("**2030/31:**")
                    st.dataframe(filtered_df_30, hide_index=True)

                filtered_df_31 = season_history_df_output[
                    season_history_df_output["Season"] == "2031/32"
                ]
                if not filtered_df_31.empty:
                    st.markdown("**2031/32:**")
                    st.dataframe(filtered_df_31, hide_index=True)

                filtered_df_32 = season_history_df_output[
                    season_history_df_output["Season"] == "2032/33"
                ]
                if not filtered_df_32.empty:
                    st.markdown("**2032/33:**")
                    st.dataframe(filtered_df_32, hide_index=True)

                filtered_df_33 = season_history_df_output[
                    season_history_df_output["Season"] == "2033/34"
                ]
                if not filtered_df_33.empty:
                    st.markdown("**2033/34:**")
                    st.dataframe(filtered_df_33, hide_index=True)

                filtered_df_34 = season_history_df_output[
                    season_history_df_output["Season"] == "2034/35"
                ]
                if not filtered_df_34.empty:
                    st.markdown("**2034/35:**")
                    st.dataframe(filtered_df_34, hide_index=True)

                filtered_df_35 = season_history_df_output[
                    season_history_df_output["Season"] == "2035/36"
                ]
                if not filtered_df_35.empty:
                    st.markdown("**2035/36:**")
                    st.dataframe(filtered_df_35, hide_index=True)

                filtered_df_36 = season_history_df_output[
                    season_history_df_output["Season"] == "2036/37"
                ]
                if not filtered_df_36.empty:
                    st.markdown("**2036/37:**")
                    st.dataframe(filtered_df_36, hide_index=True)

                filtered_df_37 = season_history_df_output[
                    season_history_df_output["Season"] == "2037/38"
                ]
                if not filtered_df_37.empty:
                    st.markdown("**2037/38:**")
                    st.dataframe(filtered_df_37, hide_index=True)

                filtered_df_38 = season_history_df_output[
                    season_history_df_output["Season"] == "2038/39"
                ]
                if not filtered_df_38.empty:
                    st.markdown("**2038/39:**")
                    st.dataframe(filtered_df_38, hide_index=True)

                filtered_df_39 = season_history_df_output[
                    season_history_df_output["Season"] == "2039/40"
                ]
                if not filtered_df_39.empty:
                    st.markdown("**2039/40:**")
                    st.dataframe(filtered_df_39, hide_index=True)
            with chart_history:
                # Select top 10 teams from most recent season
                max_season = season_history_df_output["Season"].max()
                filtered_df = season_history_df_output[
                    season_history_df_output["Season"] == max_season
                ]

                sorted_df = filtered_df.sort_values(by="Pos", ascending=True)

                top_10_df = sorted_df.head(10)

                teams = top_10_df["Team"].tolist()

                plot_data = season_history_df_output[
                    season_history_df_output["Team"].isin(teams)
                ]

                # Plot Team Positions by Season
                max_position = plot_data["Pos"].max()

                title = alt.TitleParams("Team Positions by Season", anchor="middle")
                chart_position = (
                    alt.Chart(plot_data, title=title)
                    .mark_line()
                    .encode(
                        x=alt.X("Season", title="Season"),
                        y=alt.Y(
                            "Pos:Q",
                            title="Position",
                            scale=alt.Scale(domain=[1, max_position]),
                            sort=alt.SortOrder("descending"),
                        ),
                        color="Team:N",
                    )
                    .properties(
                        width=700,
                        height=400,
                    )
                    .configure(numberFormat="d")
                )

                st.altair_chart(chart_position)

                # Plot Team Overall Rank by Season
                max_rank = plot_data["Overall Rank"].max()

                title = alt.TitleParams("Team Overall Rank by Season", anchor="middle")
                chart_rank = (
                    alt.Chart(plot_data, title=title)
                    .mark_line()
                    .encode(
                        x=alt.X("Season", title="Season"),
                        y=alt.Y(
                            "Overall Rank",
                            title="Overall Rank",
                            scale=alt.Scale(domain=[1, max_rank]),
                            sort=alt.SortOrder("descending"),
                        ),
                        color="Team:N",
                    )
                    .properties(
                        width=700,
                        height=400,
                    )
                    .configure(numberFormat="d")
                )

                st.altair_chart(chart_rank)

    except Exception as e:
        st.error(
            """:lion_face: Unable to get league data. League ID is a number located in the league URL: `https://fantasy.premierleague.com/leagues/XXXXXX/standings/c`"""
        )


if __name__ == "__main__":
    main()
