#   Authors: Jacob Kleiman, Tommy Strauser
#   MII
#   July 17, 2019

import numpy as np
import pandas as pd
import sys
import os
import plotly.graph_objects as go
import time
import csv
import json
import discogs_client
from google.cloud import bigquery
from collections import Counter
from plotly.subplots import make_subplots
from ipywidgets import widgets
from anytree import Node, RenderTree, AsciiStyle,search
from anytree.exporter import JsonExporter

#parse_json
#params: name of the json file (string)
#returns: root of the anytree object
def parse_json(file):
    with open(file,'r') as fp:
        obj = json.load(fp)
        root = Node(obj["name"])
        recurse(obj["children"],root)
        return root

#recursively loops the elements of the json file
#recursively adds children to the root pointer
def recurse(obj, node):
    for child in obj:
        curr_node = Node (child["name"],parent=node)
        if "children" in child:
            recurse(child["children"],curr_node)

#parse_label()
#returns the name of the label prompted from the command line
def parse_label():
    label = ""
    for index in enumerate(sys.argv):
        if (index[0] > 0):
            label = label + index[1] + " "
    return label.strip()

#get_sub_labels
#params: name of the label (string)
#returns: a list containing the label and all of its sublabels (if there are any)
def get_sub_labels(label):
    root = parse_json("labels.json")
    try:
        labels = [label]
        node = search.find_by_attr(root, name="name", value=label)
        if not node:
            print(labels)
            return labels
        #node = search.findall(root, filter_= lambda node: label in node.name,maxcount=1)
        labels = recurse_children(labels,node.children)
        print(labels)
        return labels
    except:
        print("Label " + label + " not found.")

#recurse_children
#recursively adds sublabels of a sublabel
def recurse_children(labels, children):
    for child in children:
        labels.append(child.name)
        if not child.is_leaf:
            labels = recurse_children(labels,child.children)
    return labels

#get_from_bq
#params: a list of labels and sublabels
#returns: a pandas DataFrame of creative metadata values and paths
def get_from_bq(labels):
    bqc = bigquery.Client()
    #if there are no labels found in the JSON Tree
    if len(labels) == 1:
        print(labels)
        #Query all names like labels[0]
        query_string = """
                    SELECT DISTINCT t1.r2_label_name
                    FROM `umg-edw.metadata.canopus_resource` AS t1
                    WHERE (t1.r2_label_name LIKE {} OR t1.r2_label_name LIKE {});
                    """.format("'" + labels[0] + "'", "'" + '%' + labels[0] + '%' + "'")
        results = bqc.query(query_string).result()
        for result in results:
            labels.append(result[0])
        print(labels)
        query_string = """
        SELECT t1.path, t1.value
        FROM `umg-edw.metadata.amplify_tem_v3_3`AS t1 INNER JOIN `umg-edw.metadata.canopus_resource` AS t2
        ON t1.isrc = t2.r2_isrc
        WHERE t1.source = \'Manual\'
        AND t2.r2_label_name IN ({});
        """.format(", ".join(repr(e) for e in labels))
    #if there are labels and sublabels found in the JSON Tree
    elif len(labels) > 1:
        print(labels)
        query_string = """
                SELECT t1.path, t1.value
                FROM `umg-edw.metadata.amplify_tem_v3_3`AS t1 INNER JOIN `umg-edw.metadata.canopus_resource` AS t2
                ON t1.isrc = t2.r2_isrc
                WHERE t1.source = \'Manual\'
                AND t2.r2_label_name IN ({});
                """.format(", ".join(repr(e) for e in labels))
    # Wil not be invoked
    else:
        query_string = """
                SELECT t1.path, t1.value
                FROM `umg-edw.metadata.amplify_tem_v3_3`AS t1
                WHERE t1.source = \'Manual\';
                        """
    #initialize DataFrame
    data = []
    #print(query_string)
    results = bqc.query(query_string).result()
    for row in results:
        # if len(labels) == 1:
        #     print(row[2])
        data.append([row[0],row[1]])
    df = pd.DataFrame(data, columns=['Path', 'Value'])
    return df

#initialize lists of creative metadata from BigQuery
def get_lists():
    return [],[],[],[],[],[],[]

def add_fig_traces(figs,keys,values,visiblity,title):
    figs.add_trace(go.Pie(labels=keys, values=values, visible = visiblity,name=title, hole=0.3,
                          title=title)) #textfont=dict(size=1000)))

def calc_metadata(df,label):
    genre_data,emotion_data,intensity_data,instrument_data,lyric_theme_data,\
    sound_color_data,ensemble_timbre_data = get_lists()
    for row_index,row in df.iterrows():
        if "Genre" in row[0]:
            genre_data.append(row[1])
        elif "Emotion" in row[0]:
            if not "Attitude" in row[1]:
                emotion_data.append(row[1])
        elif "Intensity" in row[0]:
            intensity_data.append(row[1])
        elif "Instrument" in row[0]:
            if not "Instrument Technique" in row[0]:
                if not "Instrument Effect" in row[0]:
                    instrument_data.append(row[1])
        elif "Lyric Theme" in row[0]:
            lyric_theme_data.append(row[1])
        elif "Sound Color" in row[0]:
            sound_color_data.append(row[1])
        elif "Ensemble Timbre" in row[0]:
            ensemble_timbre_data.append(row[1])
    genre_fig, genre_keys, genre_values = calc_averages(genre_data)
    #genre_fig.show()
    emotion_fig, emotion_keys, emotion_values= calc_averages(emotion_data)
    #emotion_fig.show()
    intensity_fig, intensity_keys, intensity_values= calc_averages_intensity(intensity_data)
    instrument_fig, instrument_keys,instrument_values = calc_averages_instrument(instrument_data)
    lyric_fig,lyric_keys,lyric_values = calc_averages_lyrics(lyric_theme_data)
    sound_fig,sound_keys,sound_values = calc_averages(sound_color_data)
    ensemble_fig,ensemble_keys,ensemble_values = calc_averages(ensemble_timbre_data)

    figs = go.Figure()
    add_fig_traces(figs,genre_keys,genre_values,True,"Genre")
    add_fig_traces(figs,emotion_keys,emotion_values,False,"Emotion")
    add_fig_traces(figs,intensity_keys,intensity_values,False,"Intensity")
    add_fig_traces(figs,instrument_keys,instrument_values,False,"Instruments")
    add_fig_traces(figs,lyric_keys,lyric_values,False,"Lyric Themes")
    add_fig_traces(figs,ensemble_keys,ensemble_values,False,"Ensemble Timbre")

    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
                             '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
                             '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
                             '#000075', '#808080', '#ffffff', '#000000']
    figs.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=15,
                                         marker=dict( line=dict(color='#000000', width=2)))
    make_layout(figs,label)

    figs.show()

def calc_metadata_static(df,label):
    genre_data, emotion_data, intensity_data, instrument_data, lyric_theme_data, \
    sound_color_data, ensemble_timbre_data = get_lists()
    for row_index,row in df.iterrows():
        if "Genre" in row[1]:
            genre_data.append(row[2])
        elif "Emotion" in row[1]:
            if not "Attitude" in row[2]:
                emotion_data.append(row[2])
        elif "Intensity" in row[1]:
            intensity_data.append(row[2])
        elif "Instrument" in row[1]:
            if not "Instrument Technique" in row[1]:
                if not "Instrument Effect" in row[1]:
                    instrument_data.append(row[2])
        elif "Lyric Theme" in row[1]:
            lyric_theme_data.append(row[2])
        elif "Sound Color" in row[1]:
            sound_color_data.append(row[2])
        elif "Ensemble Timbre" in row[1]:
            ensemble_timbre_data.append(row[2])
    print("Data Parsed...")
    genre_fig, genre_keys, genre_values = calc_averages(genre_data)
    #genre_fig.show()
    emotion_fig, emotion_keys, emotion_values= calc_averages(emotion_data)
    #emotion_fig.show()
    intensity_fig, intensity_keys, intensity_values= calc_averages_intensity(intensity_data)
    instrument_fig, instrument_keys,instrument_values = calc_averages_instrument(instrument_data)
    lyric_fig,lyric_keys,lyric_values = calc_averages_lyrics(lyric_theme_data)
    sound_fig,sound_keys,sound_values = calc_averages(sound_color_data)
    ensemble_fig,ensemble_keys,ensemble_values = calc_averages(ensemble_timbre_data)

    figs = go.Figure()
    add_fig_traces(figs, genre_keys, genre_values, True, "Genre")
    add_fig_traces(figs, emotion_keys, emotion_values, False, "Emotion")
    add_fig_traces(figs, intensity_keys, intensity_values, False, "Intensity")
    add_fig_traces(figs, instrument_keys, instrument_values, False, "Instruments")
    add_fig_traces(figs, lyric_keys, lyric_values, False, "Lyric Themes")
    add_fig_traces(figs, ensemble_keys, ensemble_values, False, "Ensemble Timbre")

    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
                             '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
                             '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
                             '#000075', '#808080', '#ffffff', '#000000']
    figs.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=20,
                                         marker=dict( line=dict(color='#000000', width=2)))
    make_layout(figs,label)

    figs.show()

def make_layout(figs,label):
    format = "pie"
    figs.update_layout(
        width=800,
        height=900,
        autosize=False,
        margin=dict(t=0, b=0, l=0, r=0),
        template="plotly_white",
    )

    figs.update_layout(
        title={"text": label + "<br>" + "Manually Distributed Tags"},
        width=1800,
        height=1000,
        margin=go.layout.Margin(
            l=350,
            pad = 5
        ),
        updatemenus=[
            go.layout.Updatemenu(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        # args=[{"values":genre_values, "labels":genre_keys}],
                        args=[{
                               "type": "pie"}],
                        label="Pie",
                        method="restyle",
                    ),
                    dict(
                        args=[{
                               "type": "bar"}],
                        # args=[{"values":emotion_values,"labels":emotion_keys}],
                        label="Bar",
                        method="restyle",
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=1,
                y=1
            ),

            go.layout.Updatemenu(
                type="buttons",
                direction="down",
                buttons=list([
                    dict(
                        # args=[{"values":genre_values, "labels":genre_keys}],
                        args=[{"visible": [True, False, False, False, False, False]}],
                        label="Genre",
                        method="restyle",
                    ),
                    dict(
                        args=[{"visible": [False, True, False, False, False, False]}],
                        label="Emotion",
                        method="restyle",
                    ),
                    dict(
                        args=[{"visible": [False, False, True, False, False, False]}],
                        label="Intensity",
                        method="restyle",
                    ),
                    dict(
                        args=[{"visible": [False, False, False, True, False, False]}],
                        label="Instrument",
                        method="restyle",
                    ),
                    dict(
                        args=[{"visible": [False, False, False, False, True, False]}],
                        label="Lyric Theme",
                        method="restyle",
                    ),
                    dict(
                        args=[{"visible": [False, False, False, False, False, True]}],
                        label="Ensemble Timbre",
                        method="restyle",
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=-0.05,
                # xanchor="left",
                y=1
                # yanchor="top"
            )
        ]
    )

def calc_averages(data):
    keys = list(Counter(data).keys())
    values = list(Counter(data).values())
    values, keys = (list(t) for t in zip(*sorted(zip(values, keys))))
    values.reverse()
    keys.reverse()
    ave_values = []
    Sum = sum(values)
    for value in values:
        norm_val = round(((value/Sum) * 100),1)
        if norm_val >= 1:
            ave_values.append(norm_val)
    return createFigure(keys, ave_values), keys, ave_values

def calc_averages_intensity(data):
    keys = list(Counter(data).keys())
    values = list(Counter(data).values())
    values, keys = (list(t) for t in zip(*sorted(zip(values, keys))))
    values.reverse()
    keys.reverse()
    if "High" in keys:
        idx = keys.index("High")
        del values[idx]
        del keys[idx]
    if "Medium" in keys:
        idx = keys.index("Medium")
        del values[idx]
        del keys[idx]
    if "Low" in keys:
        idx = keys.index("Low")
        del values[idx]
        del keys[idx]
    if "Calm" in keys:
        idx = keys.index("Calm")
        del values[idx]
        del keys[idx]
    if "Driving" in keys:
        idx = keys.index("Driving")
        del values[idx]
        del keys[idx]
    if "Striding" in keys:
        idx = keys.index("Striding")
        del values[idx]
        del keys[idx]
    if "Moderate" in keys:
        idx = keys.index("Moderate")
        del values[idx]
        del keys[idx]
    if "Excessive" in keys:
        idx = keys.index("Excessive")
        del values[idx]
        del keys[idx]
    if "Passive" in keys:
        idx = keys.index("Passive")
        del values[idx]
        del keys[idx]
    if "Reserved" in keys:
        idx = keys.index("Reserved")
        del values[idx]
        del keys[idx]
    if "Light" in keys:
        idx = keys.index("Light")
        del values[idx]
        del keys[idx]
    if "Heavy" in keys:
        idx = keys.index("Heavy")
        del values[idx]
        del keys[idx]
    ave_values = []
    Sum = sum(values)
    for value in values:
        norm_val = round(((value / Sum) * 100), 1)
        if norm_val >= 1:
            ave_values.append(norm_val)
    return createFigure(keys, ave_values), keys, ave_values

def calc_averages_instrument(data):
    keys = list(Counter(data).keys())
    values = list(Counter(data).values())
    values, keys = (list(t) for t in zip(*sorted(zip(values, keys))))
    values.reverse()
    keys.reverse()
    if "Pitched" in keys:
        idx = keys.index("Pitched")
        del values[idx]
        del keys[idx]
    if "Unpitched" in keys:
        idx = keys.index("Unpitched")
        del values[idx]
        del keys[idx]
    if "Music" in keys:
        idx = keys.index("Music")
        del values[idx]
        del keys[idx]
    if "Instrument Effect" in keys:
        idx = keys.index("Instrument Effect")
        del values[idx]
        del keys[idx]
    ave_values = []
    Sum = sum(values)
    for value in values:
        norm_val = round(((value / Sum) * 100), 1)
        if norm_val >= 1:
            ave_values.append(norm_val)
    return createFigure(keys, ave_values), keys, ave_values

def calc_averages_lyrics(data):
    keys = list(Counter(data).keys())
    values = list(Counter(data).values())
    values, keys = (list(t) for t in zip(*sorted(zip(values, keys))))
    values.reverse()
    keys.reverse()
    if "Objects" in keys:
        idx = keys.index("Objects")
        del values[idx]
        del keys[idx]
    if "Motion" in keys:
        idx = keys.index("Motion")
        del values[idx]
        del keys[idx]
    if "Place" in keys:
        idx = keys.index("Place")
        del values[idx]
        del keys[idx]
    ave_values = []
    Sum = sum(values)
    for value in values:
        norm_val = round(((value / Sum) * 100), 1)
        if norm_val >= 1:
            ave_values.append(norm_val)
    return createFigure(keys, ave_values), keys, ave_values

def createFigure(keys, values):
    fig = go.Pie(labels=keys,values = values, hole =.3)
    return fig

if len(sys.argv) == 1:
    # df = get_from_bq([])
    # df.to_csv('all_manual.csv')
    df = pd.DataFrame(pd.read_csv("all_manual.csv"))
    print("Generating Visualization ...")
    calc_metadata_static(df,"All")
else :
    if "@" in sys.argv:
        print("EMAIL\n")

    else:
        label = parse_label()
        labels = get_sub_labels(label)
        df = get_from_bq(labels)
        if df.empty:
            print("No results found in Big Query")
            sys.exit(1)
        print("Generating Visualization ...")
        calc_metadata(df,label)


#print(RenderTree(root, style=AsciiStyle()).by_attr())

