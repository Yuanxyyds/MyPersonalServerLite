"""
Instructions (READ THIS FIRST!)
===============================
Read the comments and comment/uncomment specific lines to choose
what part of the program intended to run.

Copyright and Usage Information
===============================

This program is provided solely for the personal and private use of teachers and TAs
checking and grading the CSC110 project at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2020 Alex Lin, Steven Liu, Haitao Zeng, William Zhang.
"""
from typing import Tuple

import pandas as pd
from numpy import mean

intercept_year_to_temp = 0
slope_year_to_temp = 0
intercept_temp_to_sealevel = 0
slope_temp_to_sealevel = 0
# Create Data Frame
df1 = pd.DataFrame(pd.read_csv('landsink/data/temperature.csv'))
df2 = pd.DataFrame(pd.read_csv('landsink/data/sealevel.csv'))


def linear_regression_model(x, y) -> Tuple[float, float]:
    """
    Calculate the best-fit linear line between independent variable x and
    dependent variable y (in form of: Best-fit line = a + Bx). Return a list
    contains the y-intercept a and slope B and length of data lens in [a, B, lens]
    """
    length = len(x)
    x_mean = mean(x)
    y_mean = mean(y)
    x_sum = sum(x)
    xy_sum = sum([x[i] * y[i] for i in range(0, length)])
    x_square_sum = sum([x[i] ** 2 for i in range(0, length)])
    x_slope = (xy_sum - y_mean * x_sum) / (x_square_sum - x_mean * x_sum)
    y_intercept = y_mean - x_slope * x_mean
    return y_intercept, x_slope


def build_models() -> None:
    """
    To draw a graph.
    """
    global intercept_year_to_temp, slope_year_to_temp, intercept_temp_to_sealevel, slope_temp_to_sealevel, df1, df2

    intercept_year_to_temp, slope_year_to_temp = linear_regression_model(df1.Year, df1.Tem)
    # Predict tem of current year
    df2.year = [year_to_tem(line) for line in df2.year]
    # Turn millimeter into meter
    df2.GMSL = [line / 1000 for line in df2.GMSL]
    intercept_temp_to_sealevel, slope_temp_to_sealevel = linear_regression_model(df2.year, df2.GMSL)


def year_to_tem(year: float) -> float:
    """Return the rise in Temperature in given year
    """
    return intercept_year_to_temp + slope_year_to_temp * year


def tem_to_sealevel(tem: float) -> float:
    """Return the rise in Temperature in given year
    """
    return intercept_temp_to_sealevel + slope_temp_to_sealevel * tem
