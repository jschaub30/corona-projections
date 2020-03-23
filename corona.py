"""
Curve fitting for Corona virus USA
https://www.worldometers.info/coronavirus/country/us/
"""

import csv
from datetime import datetime, timedelta

import numpy
import plotly.graph_objects as go


def main():
    """ Read and fit raw data, then generate plot """

    with open("data.csv", "r") as fid:
        csv_reader = csv.reader(fid)
        dates = []
        num_cases = []
        header = True
        for date_str, cases in csv_reader:
            if header:
                header = False
                continue
            dates.append(datetime.strptime(date_str + "-2020", "%d-%b-%Y"))
            num_cases.append(int(cases))
    x = numpy.array(range(len(num_cases)))
    y = numpy.array(num_cases)
    last_day = datetime(2020, 4, 30)
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=dates, y=y, mode="markers", name="All data"))

    population = 330000000
    for num_points in [21, 7]:
        x_arr = x[-num_points:]
        y_arr = y[-num_points:]
        p = numpy.polyfit(x_arr, numpy.log10(y_arr), 1)

        # project into the future
        projected_x = numpy.array(list(range(int(min(x_arr)), 60)))
        projected_y = 10 ** (p[0] * projected_x + p[1])
        projected_y = numpy.minimum(projected_y, population)

        first_day = dates[-num_points]
        projected_dates = numpy.arange(first_day, last_day, timedelta(days=1))
        fig.add_trace(
            go.Scatter(
                x=projected_dates,
                y=projected_y[: len(projected_dates)],
                mode="lines",
                name=f"Last {num_points} days",
            )
        )
    title = f"Total coronavirus cases in the USA"
    fig.update_layout(title=title, yaxis_type="log")
    fig.add_annotation(
        x=dates[-1],
        y=2,
        text=f"Last updated {dates[-1].strftime('%b-%d')}",
        showarrow=False,
    )
    fig.add_annotation(
        x=dates[5],
        y=8.8,
        text=f"Source: https://www.worldometers.info/coronavirus/country/us/",
        showarrow=False,
    )
    fig.show()
    fig.write_html("index.html", include_plotlyjs="cdn")


if __name__ == "__main__":
    main()
