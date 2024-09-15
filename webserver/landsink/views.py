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

from django.http import HttpResponse

import json
from pyecharts.charts import Map
from pyecharts import options

from . import models


def predict(request, year: int) -> HttpResponse:
    """
    the main function to accept data form user typing.
    """
    temp = models.year_to_tem(year)
    eve = models.tem_to_sealevel(temp)
    # draw the map.
    return draw_map(eve, year)


def default(request) -> HttpResponse:
    """
    the main function to accept data form user typing.
    """
    temp = models.year_to_tem(2023)
    eve = models.tem_to_sealevel(temp)
    # draw the map.
    return draw_map(eve, 2023)


def translation(sea_level_1: float) -> list:
    """
    translate the information form txt.
    """

    with open("landsink/data/map_data.json", "r") as json_file:
        data = json.load(json_file)

    processed_data = {}

    # change the data format into what pyecharts need to draw.
    for country in data["data"]:
        name = country["name"]
        ele = country["avg_ele"]

        # There are 2 country which ele is 0, we assume whenever time goes,
        # these country will sink immediately.
        if float(ele) != 0:
            processed_data[name] = min(100.0, round(sea_level_1 / float(ele) * 100, 4))
        else:
            processed_data[name] = 100

    #  change the realdata into what pyecharts need.
    return list(processed_data.items())


def draw_map(sea_level_2: float, year: int) -> HttpResponse:
    """
    set the map setting and draw the map.
    """
    element = translation(sea_level_2)
    sunk_map = Map(
        options.InitOpts(bg_color="#87CEFA", page_title="Land sunk percentage map")
    ).add(
        series_name="Estimate Land Sunk Percentage at Year " + str(year),
        data_pair=element,
        is_map_symbol_show=False,
        maptype="world",
        layout_size=150,
    )

    #  set different color to different danger level.
    sunk_map.set_global_opts(
        visualmap_opts=options.VisualMapOpts(
            max_=1100000,
            is_piecewise=True,
            pieces=[
                {"min": 96},
                {"min": 72.9, "max": 95.999},
                {"min": 50.4, "max": 72.899},
                {"min": 27.8, "max": 50.399},
                {"min": 5.001, "max": 27.799},
                {"max": 5},
            ],
        )
    )

    #  set Map data format.
    sunk_map.set_series_opts(
        label_opts=options.LabelOpts(is_show=False)
    )  # set country divisible

    # Render the HTML content and return it as a JSON response
    html_content = sunk_map.render_embed()

    return HttpResponse(html_content)
