#   Authors: Jacob Kleiman, Tommy Strauser
#   MII
#   July 17, 2019
#
#   The purpose of this file is to update labels.csv
#   API calls to Discogs will collect all label and sublabel information { id , label name }
#   This program will run without any command line arguments, simply $python3 discog_get_labels.py
#   At the time this program was written, it processed 4730 total labels under UMG

import time
import csv
import discogs_client

#Parameters:
# 1 - list of labels to 'open'
# 2 - list of labels
#Returns:
# list of sublabels

def get_labels(label_list_to_do, label_names):
    if len(label_list_to_do) == 0:
        return label_names
    else:
        for label in label_list_to_do:
            time.sleep(1)
            label_names.append(label.name)
            print(label.id)
            label_names = label_names + get_labels(label.sublabels,[])
        return label_names

#Parameters:
# 1 - list of labels to 'open'
# 2 - list of labels
#Returns:
# 1 - list of ids with label names
def get_label_ids_and_names(label_list_to_do, label_names):
    if len(label_list_to_do) == 0:
        return label_names
    else:
        for label in label_list_to_do:
            try:
                time.sleep(1)
                label_names.append(str(label.id) + " " + label.name)
                print(str(label.id) +" "+ label.name)
                label_names = label_names + get_label_ids_and_names(label.sublabels,[])
            except:
                return label_names
        return label_names

#Discogs Client Initialization
d = discogs_client.Client('getalluniversallabels/0.1', user_token='NMEOClFdbylQxiIwvtLKvwIJioGlKIdzQFxDlVzQ')

boss_label = d.label(38404) # 38404 is the Discogs ID for UMG
labels = get_label_ids_and_names(boss_label.sublabels,[])

with open('labels.csv','w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            escapechar = ' ', quoting=csv.QUOTE_NONE)
    for label in labels:
        # print(label)
        spamwriter.writerow([label])