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
from django.http import JsonResponse

import json
from pyecharts.charts import Map
from pyecharts import options
from rest_framework.decorators import api_view

from landSink import model


@api_view(['GET'])
def processing(request, year: int) -> JsonResponse:
    """
    the main function to accept data form user typing.
    """
    temp = model.year_to_tem(year)
    eve = model.tem_to_sealevel(temp)
    # draw the map.
    return draw_map(eve, year)


def default(request) -> JsonResponse:
    """
    the main function to accept data form user typing.
    """
    temp = model.year_to_tem(2023)
    eve = model.tem_to_sealevel(temp)
    # draw the map.
    return draw_map(eve, 2023)


def translation(sea_level_1: float) -> list:
    """
    translate the information form txt.
    """
    #  form txt input data.
    f = open('landSink/data/map_data.txt', 'r')
    js = f.read()
    dic = json.loads(js)
    realdata = {}

    # change the data format into what pyecharts need to draw.
    for data in dic['data']:
        name = data['name']
        ele = data['avg_ele']

        #  There are 2 country which has error in translating data,
        #  so this if statement is to fix them.
        for c in name:
            if c == '么':
                name = "Côte d'Ivoire"
            if c == '茅':
                name = "São Tomé and Principe"

        # There are 2 country which ele is 0, we assume whenever time goes,
        # these country will sunk immediately.
        if float(ele) != 0:
            realdata[name] = min(100.0, round(sea_level_1 / float(ele) * 100, 4))
        else:
            realdata[name] = 100

    #  change the realdata into what pyecharts need.
    return list(realdata.items())


def draw_map(sea_level_2: float, year: int) -> JsonResponse:
    """5
    set the map setting and draw the map.
    """
    element = translation(sea_level_2)
    sunk_map = Map(options.InitOpts(bg_color="#87CEFA", page_title='sunk percentage map')). \
        add(series_name="Estimate Sunk Rate at year: " + str(year),
            data_pair=element,
            is_map_symbol_show=False,
            maptype='world',
            layout_size=150
            )

    #  set different color to different danger level.
    sunk_map.set_global_opts(
        visualmap_opts=options.VisualMapOpts(max_=1100000, is_piecewise=True, pieces=[
            {"min": 96},
            {"min": 72.9, "max": 95.999},
            {"min": 50.4, "max": 72.899},
            {"min": 27.8, "max": 50.399},
            {"min": 5.001, "max": 27.799},
            {"max": 5}, ]))

    #  set Map data format.
    sunk_map.set_series_opts(label_opts=options.LabelOpts(is_show=False))  # set country divisible

    # Render the HTML content and return it as a JSON response
    html_content = sunk_map.render_embed()
    response_data = {"html_content": html_content}

    return JsonResponse(response_data)
