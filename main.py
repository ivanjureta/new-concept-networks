# test
import csv
from igraph import *

terms = []
descriptions = []

# just opneing file
with open('data.csv') as f:
    r = csv.reader(f)
    for row in r:
        # we read each line, and place values in two arrays - terms and descriptions
        terms.append(row[0])
        descriptions.append(row[1])

# this size of dataset
size = len(terms)
# creating edges - description are pointing to terms
edges = [(size + i, i) for i in xrange(size)]
print(edges)

g = Graph(edges, directed=True)
g.vs['text'] = descriptions + terms
g.es['type'] = 'defines'

# naive search through descriptions to establish connections with dpeneding terms
for x, d in enumerate(descriptions):
    for y, t in enumerate(terms):
        # super naive check, as it will pick any match 
        if t in d:
            g.add_edge(size + x, y, type='depends')

print(g)
layout = g.layout("kk")
plot(g, layout = layout)
