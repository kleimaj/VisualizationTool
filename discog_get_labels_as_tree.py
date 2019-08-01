#   Authors: Jacob Kleiman, Tommy Strauser
#   MII
#   July 17, 2019
#   The purpose of this program is to collect all of the sublabels under UMG and format it into a JSON tree
#   This program is run without commandline arguments, simply $python3 discog_get_labels_as_tree.py

import time
import discogs_client
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter

#Parameters:
# 1 - list of labels to 'open'
# 2 - root node
#Returns:
# 1 - nothing, but node will be a full tree once it returns
def get_label_tree(label_list_to_do, node):
    if len(label_list_to_do) == 0:
        return
    else:
        for label in label_list_to_do:
            try:
                time.sleep(1)
                #label_names.append(str(label.id) + " " + label.name)
                #print(str(label.id) +" "+ label.name)
                curr_node = Node(label.name,parent = node)
                get_label_tree(label.sublabels,curr_node)
            except:
                return
        return

#Discogs Client Initialization
d = discogs_client.Client('getalluniversallabels/0.1',
                          user_token='NMEOClFdbylQxiIwvtLKvwIJioGlKIdzQFxDlVzQ')

boss_label = d.label(38404) # 38404 is the Discogs ID for UMG
root = Node("Universal Music Group")
get_label_tree(boss_label.sublabels,root)

#Exporting to JSON
exporter = JsonExporter(indent = 2, sort_keys = False)
#exports to tree.json file
fh = open("tree.json","w")
exporter.write(root,fh)