"""
Curve fitting for Corona virus USA
https://www.worldometers.info/coronavirus/country/us/
"""

import csv
from datetime import datetime, timedelta

import numpy
import plotly.graph_objects as go

POPULATION = 330000000
LAST_DAY = datetime(2020, 5, 2)


def read_data():
    """ Read CSV data """
    with open("data.csv", "r") as fid:
        csv_reader = csv.reader(fid)
        dates = []
        cases = []
        header = True
        for date_str, num_cases in csv_reader:
            if header:
                header = False
                continue
            dates.append(datetime.strptime(date_str + "-2020", "%d-%b-%Y"))
            cases.append(int(num_cases))
    return dates, cases


def fit_and_project(x, y, first_day, linear=False):
    """
    Fit data for the past number of days
    Project fit until LAST_DAY
    """
    # project into the future
    projected_dates = numpy.arange(first_day, LAST_DAY, timedelta(days=1))
    projected_x = numpy.arange(x[0], x[0] + len(projected_dates))

    if linear:
        pfit = numpy.polyfit(x, y, 1)
        projected_y = pfit[0] * projected_x + pfit[1]
    else:
        pfit = numpy.polyfit(x, numpy.log10(y), 1)
        projected_y = 10 ** (pfit[0] * projected_x + pfit[1])

    projected_y = numpy.minimum(projected_y, POPULATION)

    return projected_dates, projected_y, projected_y / POPULATION * 100


def main():
    """ Read and fit raw data, then generate plot """
    dates0, cases = read_data()

    x0 = numpy.array(range(len(cases)))
    y0 = numpy.array(cases)
    y0norm = numpy.array(cases) / POPULATION * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates0, y=y0, mode="markers", name="All data"))

    # March 1 - March 26
    days = (datetime(2020, 3, 26) - datetime(2020, 3, 1)).days
    dates1, y1, y1norm = fit_and_project(x0[7:34], y0[7:34], dates0[7])
    fig.add_trace(
        go.Scatter(x=dates1, y=y1, mode="lines", name="March 1 - 26 (exponential)")
    )
    # Last 7 days
    days = 7
    dates2, y2, y2norm = fit_and_project(
        x0[-days:], y0[-days:], dates0[-days], linear=True
    )
    fig.add_trace(
        go.Scatter(x=dates2, y=y2, mode="lines", name=f"Last {days} days (linear)")
    )
    subtitle = (
        f"<br><sub><a href='https://www.worldometers.info/coronavirus/country/us/'>"
    )
    subtitle += "Source</a>"
    subtitle += ", Also see: <br>"
    subtitle += "<a href='https://aatishb.com/covidtrends/'>covidtrends</a> and "
    subtitle += (
        "<a href='https://www.youtube.com/watch?v=54XLXg4fYsc'>explanation</a> <br>"
    )
    subtitle += "<a href='http://covid19.healthdata.org/projections'>Projections</a>"
    subtitle += f"<br>Updated through {dates0[-1].strftime('%b-%d')}</sub>"
    title = "<b>Projected coronavirus cases in the USA</b>" + subtitle

    fig.update_layout(title=title, yaxis_type="log")
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.5,
                y=1.05,
                buttons=list(
                    [
                        dict(
                            label="Number",
                            method="update",
                            args=[
                                {"y": [y0, y1, y2]},
                                {"title": title, "yaxis": {"type": "log", "title": ""}},
                            ],
                        ),
                        dict(
                            label="Percent",
                            method="update",
                            args=[
                                {"y": [y0norm, y1norm, y2norm]},
                                {
                                    "title": title,
                                    "yaxis": {
                                        "type": "log",
                                        "tickformat": "0.1r",
                                        "title": "% of population",
                                    },
                                },
                            ],
                        ),
                    ]
                ),
            )
        ]
    )
    fig.show()
    fig.write_html("index.html", include_plotlyjs="cdn")


if __name__ == "__main__":
    main()
