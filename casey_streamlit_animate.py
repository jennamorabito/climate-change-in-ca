def animate():
    import pandas as pd
    import streamlit as st
    import altair as alt
    import time
    import numpy as np


    ##overriding the dataset size limit from altair
    alt.data_transformers.disable_max_rows()

    def create_temp_data():

        ca_temp_dirty = pd.read_csv("/Users/cmcgonigle/Downloads/Avg_Temp_Historic_CA.csv")

        ## Dictionary for new names of our columns
        name_dict = {"California": "Date", " Average Temperature": "Avg Temp", " May-October": "Anomaly"}

        ## rename columns and drop extra columns
        ca_temp = ca_temp_dirty.rename(columns=name_dict).drop([0, 1, 2, 3]).reset_index().drop(columns={"index"})
        ## get Date into a proper Year format, then drop Date
        ca_temp["Year"] = ca_temp["Date"].str[:-2]
        ca_temp = ca_temp.drop(columns={"Date"})

        ## Turn Avg. Temp and Anomaly into ints, Year into a datetime object

        ca_temp["Avg Temp"] = ca_temp["Avg Temp"].astype(float)
        ca_temp["Anomaly"] = ca_temp["Anomaly"].astype(float)
        ca_temp["Year"] = pd.to_datetime(ca_temp["Year"])

        first_temp_avg = float(ca_temp[["Avg Temp"]].iloc[range(101)].mean(axis=0)[0])

        ca_temp["100yr_avg"] = first_temp_avg

        return ca_temp

    def create_precip_data():
        ca_prec_dirty = pd.read_csv("/Users/cmcgonigle/Downloads/Precip_CA_Historic.csv")
        ca_prec_dirty.head(8)

        ## Dictionary for new names of our columns
        name_dict2 = {"California": "Date", " May-October": "Anomaly"}

        ## rename columns and drop extra columns
        ca_prec = ca_prec_dirty.rename(columns=name_dict2).drop([0, 1, 2, 3]).reset_index().drop(columns={"index"})
        ## get Date into a proper Year format, then drop Date
        ca_prec["Year"] = ca_prec["Date"].str[:-2]
        ca_prec = ca_prec.drop(columns={"Date"})

        ## Turn Avg. Temp and Anomaly into ints, Year into a datetime object

        ca_prec["Precipitation"] = ca_prec[" Precipitation"].astype(float)
        ca_prec["Anomaly"] = ca_prec["Anomaly"].astype(float)
        ca_prec["Year"] = pd.to_datetime(ca_prec["Year"])
        ca_prec = ca_prec.drop(columns={" Precipitation"})

        ca_prec = ca_prec[['Year', 'Precipitation', 'Anomaly']]

        first_precip_avg = float(ca_prec[["Precipitation"]].iloc[range(101)].mean(axis=0)[0])

        ca_prec["100yr_avg"] = first_precip_avg
        return ca_prec

    ca_temp = create_temp_data()
    ca_prec = create_precip_data()

    climate = pd.merge(ca_temp, ca_prec, how='inner', on="Year").rename(
        columns={"Anomaly_x": "Temp Anomaly", "100yr_avg_x": "Temp_100_yr_avg", "Anomaly_y": "Precip Anomaly",
                 "100yr_avg_y": "Precip_100_yr_avg"})

    climate = climate[
        ["Year", "Avg Temp", "Temp Anomaly", "Temp_100_yr_avg", "Precipitation", "Precip Anomaly", "Precip_100_yr_avg"]]

    climate["decade"] = climate.Year.apply(lambda x: str(x)[:3] + '0')

    climate["streamlit_year"] = climate["Year"]  + pd.offsets.DateOffset(years=1)


    ##########################################################################
    ##### END DATA CLEANING ##################################################
    ##########################################################################


    # This creates the temp and precip avg. lines
    def avg_lines():
        lines_color = '#c33cb8'
        y_rule = alt.Chart(climate).mark_rule(size=1, color=lines_color, fillOpacity=0.1).encode(
            y=alt.Y('Precip_100_yr_avg:Q', scale=alt.Scale(domain=[0, 7])),
            tooltip=[alt.Tooltip("Precip_100_yr_avg:Q", title="Average Precip 1895-1995 (in)", format=",.2f")]
        )

        x_rule = alt.Chart(climate).mark_rule(size=1, color=lines_color).encode(
            x= alt.X('Temp_100_yr_avg:Q', scale = alt.Scale(domain=[64, 72])),
            tooltip=[alt.Tooltip("Temp_100_yr_avg:Q", title="Average Temp 1895-1995 (°F)", format=",.2f")]
        )

        y_1 = alt.Chart(climate).mark_text(dx=720, dy=5, fontSize=15, color=lines_color, text='Avg. Precip (1895 - 1995)'
                                           ).encode()

        x_1 = alt.Chart(climate).mark_text(dx=-250, dy=-120, fontSize=15, angle=270, color=lines_color,
                                           text='Avg. Temp (1895 - 1995)'
                                           ).encode()

        reg = x_1.transform_regression("Avg Temp:Q", "Precipiation:Q").mark_line

        return (y_rule + x_rule +y_1 + x_1 )


    def scatterpoints():
        base = alt.Chart(climate).mark_point(size=150, filled=True, opacity=0.7).encode(
            x=alt.X("Avg Temp:Q", axis=alt.Axis(title="Average Summer Temperature Statewide (°F)"),
                    scale=alt.Scale(domain=[64, 72])),
            y=alt.Y("Precipitation:Q", axis=alt.Axis(title="Average Precipitation Statewide (in)")))


        scatter = base.encode(color=alt.Color('decade:O', scale = alt.Scale(domain=[1890, 1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020], scheme='plasma'),
                            legend=alt.Legend(title="Decades", tickCount=10, titleFontSize=25, labelFontSize=20)),
            tooltip=[alt.Tooltip("year(streamlit_year):T" , title="Year"), alt.Tooltip("Avg Temp", title="Temperature (°F)"),
                     alt.Tooltip("Precipitation", title="Precip (in)"), alt.Tooltip("Temp Anomaly"),
                     alt.Tooltip("Precip Anomaly")])
        line = base.transform_regression("Avg Temp", "Precipitation").mark_line(size = 2, color = 'grey')

        line_label = alt.Chart(climate).mark_text(dx=690, dy=17, fontSize=15, angle = 6, color="grey", text='Line of Best Fit (Precipitation ~ Temp)'
                                           ).encode()



        return scatter + line + line_label




    def make_empty_chart():
        return avg_lines().properties(title="California's Average Climate 1895 - 2020", width=1800, height=800
                ).configure_axis(labelFontSize=25, titleFontSize=25, grid=False
                ).configure_title(fontSize=35
                )

    # This plots the scatters and gives them their color
    def make_chart():
        return (scatterpoints() + avg_lines()).properties(title="California's Average Climate 1895 - 2020", width=1800, height=800
                ).configure_axis(labelFontSize=25, titleFontSize=25, grid=False
                ).configure_title(fontSize=35
                )


    def make_animation(df):


        climateChart3 = alt.Chart(df).mark_point(size=150, filled=True, opacity=0.7).encode(
            x=alt.X("Avg Temp:Q", axis=alt.Axis(title="Average Summer Temperature Statewide (°F)"),
                    scale=alt.Scale(domain=[64, 72])),
            y=alt.Y("Precipitation:Q", axis=alt.Axis(title="Average Precipitation Statewide (in)"), scale=alt.Scale(domain=[0,7])),
            color=alt.Color('decade:O', scale=alt.Scale(domain=[1890, 1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020], scheme='plasma'),
                            legend=alt.Legend(title="Decades", tickCount=10, titleFontSize=25, labelFontSize=20)),
            tooltip=[alt.Tooltip("year(streamlit_year):T", title="Year"), alt.Tooltip("Avg Temp", title="Temperature (°F)"),
                     alt.Tooltip("Precipitation", title="Precip (in)"), alt.Tooltip("Temp Anomaly"),
                     alt.Tooltip("Precip Anomaly")],
            )

        return (climateChart3 + avg_lines()).properties(title="California's Average Climate 1895 - 2020", width=1800, height=800
                ).configure_axis(labelFontSize=25, titleFontSize=25, grid=False
                ).configure_title(fontSize=35
                )

    N = climate.shape[0] + 1  # number of elements in the dataframe
    burst = 10 # number of elements (Years) to add to the plot
    size = 5  # size of the current dataset

    scatter_plot = st.altair_chart(make_chart())
    start_btn = st.button('Start Animation! -- 10 years at a time')

    if start_btn:
        while size < N:
            step_df = climate.iloc[0:size]
            scatter = make_animation(step_df)
            animation = scatter_plot.altair_chart(scatter)
            size = size + burst
            if size >= N:
                scatter = make_animation(climate)
                animation = scatter_plot.altair_chart(scatter)

                break
            time.sleep(0.1)

    viz1 = make_chart()

    #viz1.save("casey_caClimate1.html")

    st.write("""
    # Press the Start Button!
    ## Todo:

    1. Fire Data! (Add Fire Data / Identify those years (dots))
    2. Dot size by fire acres burned
    3. --- Make sure the years are correct! (Right now they're 1 year early) ---
    4. --- Get colors on animation to be consistent ---
    5. --- Line of best fit through the data ... maybe have it post-animation too? Or labeled? ---
    6. --- Make it Faster? ---
    7. --- Include Current Decade count in top right? ---
    8. Line of best fit arrows?
    9. Line of best fit in the animation? Sloping down as we move through time?
    10. Upper Right Hand w/ Decades during animation
    11. Label "Hot & Dry" v. "Cold & Wet"

    """)

    #st.altair_chart(viz1)

    return #viz1.save("casey_caClimate1.html")


if __name__ == '__main__':
    animate()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
