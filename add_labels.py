#   Jacob Kleiman, Tommy Strauser
#   MII Team
#   July 29, 2019

from anytree import Node, RenderTree,search
from anytree.exporter import JsonExporter
import csv
import json
import pandas as pd
import numpy as np

def parse_json(file):
    with open(file,'r') as fp:
        obj = json.load(fp)
        root = Node(obj["name"])
        recurse(obj["children"],root)
        return root

def recurse(obj, node):
    for child in obj:
        curr_node = Node (child["name"],parent=node)
        if "children" in child:
            recurse(child["children"],curr_node)

root = parse_json("labels.json")
df = pd.read_csv('labels.csv',squeeze=True)
#add df elements to root where appropriate
list = []
for idx, label in df.items():
    node = search.find_by_attr(root, name="name", value=label)
    if not node:
        list.append(label)

# with open('labels.csv','w', newline='') as csvfile:
#     spamwriter = csv.writer(csvfile, delimiter=' ',
#                             escapechar = ' ', quoting=csv.QUOTE_NONE)
#     for label in list:
#         # print(label)
#         spamwriter.writerow([label])
#Exporting to JSON
exporter = JsonExporter(indent = 2, sort_keys = False)
#exports to tree.json file
fh = open("tree.json","w")
exporter.write(root,fh)