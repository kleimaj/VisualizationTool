#Visualization Tool
##Music Informatics Initiative
###A Python project that utilizes the data visualization library Plot.ly to illustrate the creative metadata of record labels

To run this program, one must first clone this repository:
```
git clone https://github.com/kleimaj/VisualizationTool.git
```
After the git repository is cloned, navigate to the repository
```
cd VisualizationTool
```
You may then run the project by invoking the following command
```
python main.py
```
You will then be able to see all of the manually distributed metadata tags applied to all tracks under Universal Music Group

Given a service account to UMG's BigQuery, one may be able to run the program with an extra command line argument (the label name)

```
python main.py Interscope
```
This will visualize all elements of creative metadata under the Interscope label, and all of its sublabels