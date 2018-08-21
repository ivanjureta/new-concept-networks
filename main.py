# test
import csv
from igraph import *

terms = []
descriptions = []
# initialize graph 
g = Graph(directed=True)

# in, one pass - read from file, build terms index and add edges to graph 
with open('data.csv') as f:
    r = csv.reader(f)
    for i, row in enumerate(r):
        # we read each line, and place values in two arrays - terms and descriptions
        terms.append(row[0])
        descriptions.append(row[1])
        # adding to graph, first allocating vertices, and then throw an edge between
        g.add_vertex(name=row[0] + ' desc', label=row[1], type='description')
        g.add_vertex(name=row[0], label=row[0], type='term')
        g.add_edge(2*i, 2*i + 1, type='defines')

# naive search through descriptions to establish connections with depeneding terms
size = len(terms)
for x, d in enumerate(descriptions):
    for y, t in enumerate(terms):
        # super naive check, as it will pick any match 
        if t.lower() in d.lower():
            g.add_edge(2*x, 2*y + 1, type='depends')

print(g)
layout = g.layout("kk")
plot(g, layout = layout)
