import requests
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import igraph as ig
from bidi.algorithm import get_display
from arabic_reshaper import reshape



########## Data Fetching
'''
start_urls = []
for i in range(1, 14):
    start_urls.append(f'https://www.namava.ir/api/v3.0/search/advance?type=movie&count=20&page={i}&CountryProducer=3&ADProductionYear=2016-2021&PersianProductionYear=1395-1400')

filename = 'movies_95.txt'
with open(filename, 'a+') as f:
    for url in start_urls:
        res = requests.get(url, headers={'User-Agent':'test'})
        res = res.json()
        res = res['result']['result_items'][0]['groups']['Media']['items']
        for movie in res:
            f.write(movie['id'] + "\n")
print('Movie ids saved!')

detail_urls = []
with open('movies_95.txt', 'r') as ids_file:
    ids = ids_file.readlines()
    for id in ids:
        detail_urls.append(f'https://www.namava.ir/api/v1.0/medias/{id.strip()}/preview')

ids = []
points = []
casts = []
titles = []
for url in detail_urls:
    res = requests.get(url, headers={'User-Agent':'test'})
    res = res.json()
    res = res['result']
    ids.append('m' + str(res['id']))
    points.append(res['hit'])
    titles.append(res['caption'])
    casts.append(list(map(lambda c: 'c'+str(c['castId']), res['casts'])))

raw_data = {
    'id': ids,
    'title': titles,
    'point': points,
    'cast': casts,
}
df = pd.DataFrame(raw_data, columns = ['id', 'title', 'point',
                                           'cast'])

df.to_csv('movies_95_raw_data_csv.csv')

df = pd.read_csv('movies_95_raw_data_csv.csv')
df['cast'] = df['cast'].apply(lambda x: str(x[1:-1]))
df['id'] = df['id'].apply(lambda x: 'm'+str(x))
df.to_csv('movies_95_raw_data_csv.csv')
'''
######################################################################################
df = pd.read_csv('movies_95_raw_data_csv.csv')
castIds = []
movieIds = []
vertices = []

for ids in df['cast'].tolist():
    if isinstance(ids, str):
        for id in ids.split(','):
            cast = id.strip()[1:-1]
            if cast and cast not in vertices:
                vertices.append(cast)
                castIds.append(cast)

index = 0
casts = df['cast'].tolist();
for id in df['id'].tolist():
    if isinstance(casts[index], str):
        vertices.append(id)
        movieIds.append(id)
    index = index + 1
vertices = list(filter(None, vertices))
movieIds = list(filter(None, movieIds))
castIds = list(filter(None, castIds))

get_type = lambda x: 1 if x[0] == 'm' else 0
types = list(map(get_type, vertices))


mapped_index_to_id = {}
index = 0

for id in castIds:
    mapped_index_to_id[id] = index
    index = index + 1
for id in movieIds:
    mapped_index_to_id[id] = index
    index = index + 1

edges = []
for index, row in df.iterrows():
    if isinstance(row['cast'], str):
        for cast in row['cast'].split(','):
            if cast.strip():
                edges.append((mapped_index_to_id[row['id']], mapped_index_to_id[cast.strip()[1:-1]]))


colors = ['blue', 'red']
vertix_colors = [colors[t] for t in types]

g = ig.Graph()
g.add_vertices(vertices)
g.add_edges(edges)

to_delete_ids = [v.index for v in g.vs if v.degree() == 0]
g.delete_vertices(to_delete_ids)


casts_df = pd.read_csv('casts_95_raw_data_csv.csv')
all_labels = []
all_names = {}
for index, row in casts_df.iterrows():
    all_names[row['id']] = row['name']
for index, row in df.iterrows():
    all_names[row['id']] = row['title']
for id in castIds:
    #print(id)
    all_labels.append(all_names[id])
for id in movieIds:
   # print(id)
    all_labels.append(all_names[id])

g.vs['label'] =  [get_display(reshape(label)) for label in all_labels]
visual_style = {}
visual_style["vertex_color"] = vertix_colors
g.vs['label_size'] = 10
visual_style["vertex_size"]=10
g.vs['vertex_label_angle'] = -45 * (np.pi / 180) #angle is in radians
layout = g.layout_bipartite(types)
ig.plot(g,"twomode.svg", **visual_style, layout=layout, bbox = (25000,500))


print(g)








