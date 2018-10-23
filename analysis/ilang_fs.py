# Print a table of nodes, by in degrees higher than threshold.
def tabulate_in_degrees(graph, in_degree_threshold, first_column_title, second_column_title):
    in_degrees_table = list()
    for n in graph.nodes():
        if graph.in_degree()[n] > in_degree_threshold: 
            in_degrees_table.append((n, graph.in_degree()[n]))
    in_degrees_table.sort()
    from tabulate import tabulate
    print(tabulate(in_degrees_table, headers = [first_column_title, second_column_title], tablefmt="pipe"))

# Print a table of nodes, by out degrees higher than threshold.
def tabulate_out_degrees(graph, out_degree_threshold, first_column_title, second_column_title):
    out_degrees_table = list()
    for n in graph.nodes():
        if graph.out_degree()[n] > out_degree_threshold: 
            out_degrees_table.append((n, graph.out_degree()[n]))
    out_degrees_table.sort()
    from tabulate import tabulate
    print(tabulate(out_degrees_table, headers = [first_column_title, second_column_title], tablefmt="pipe"))

# Print to text file.
def print_to_txt(file_content, project_name, content_description, save_to_project_dir = False):
    import os
    from tabulate import tabulate
    output_file_name = project_name + '_' + content_description + '.txt'
    if save_to_project_dir == False:
        with open(output_file_name, "w") as text_file:
            print(file_content, file=text_file)
    else: 
        os.chdir(project_name)
        with open(output_file_name, "w") as text_file:
            print(file_content, file=text_file)
        os.chdir('..')

# Shorten input string to n characters and ellipsis '...'.
def shorten_string(string, n):
    if len(string) < n: return string
    else: return string[0:n] + '...'

# Add line breaks to long string.
## In: String x and number of characters to add line breaks at.
## Out: String y with a line break every max_chars of x.
def add_line_breaks(x, max_chars):
    import math
    y = str()
    cc = 0
    for i in x.split(): 
        cc = cc + len(i)
        y = y + ' ' + i
        if cc > max_chars:
            cc = 0
            y = y + '\n'
    return y

# Remove line breaks '\n' in a string.
def remove_line_breaks(s):
    s1 = str()
    for w in s.split():
        s1 = s1 + ' ' + w.replace("\n"," ")
    return s1

# Remove punctuation
def return_clean_string(string):
    import unicodedata
    clean_string = str()
    normalized_string = str()
    for w in string.split():
        w = w.replace(".","")
        w = w.replace(",","")
        w = w.replace(":","")
        w = w.replace("\"","")
        w = w.replace("!","")
        w = w.replace("â€œ","")
        w = w.replace("â€˜","")
        w = w.replace("*","")
        w = w.replace("(","")
        w = w.replace(")","")
        w = w.replace("/","")
        w = w.replace("\n"," ")
        clean_string = clean_string + ' ' + w
    normalized_string = unicodedata.normalize("NFKD", clean_string.casefold())
    return normalized_string

# Setup project name and directory.
## Project name is a global variable, and will prefix all output files.
## Project name directory is created within current directory.
def setup_project(name, create_subdirectory = False):
    import os
    if create_subdirectory == True and os.path.isdir(name) == False: 
        os.mkdir(os.path.expanduser(name))
    global project_name
    project_name = name

# Raw Data from CSV
## In: CSV file, with any number of columns, first row must have column names.
## Out: Two dicts, one keyed Attributes, has a list of column names; the other keyed Content has integer keys, each entry is itself a dict of row values, keyed by column names.
def raw_data_from_CSV(csv_file, delimiter_character):
    raw_data = {}
    import csv
    with open(csv_file) as file:
        data = csv.reader(file, delimiter = delimiter_character)
        j = 0
        for i in data: 
            if j == 0: 
                attribute_names = i
            if j > 0:
                raw_data[j-1] = dict()
                for k in range(0,len(attribute_names)):
                    raw_data[j-1][attribute_names[k]] = i[k]
            j = j + 1
    return { 'Attributes': attribute_names, 'Content': raw_data }

# Structure raw data.
## In: raw, which is the output of raw_data_from_CSV.
## Out: Dict, where each item is one item from raw, with a series of properties describing that item. 
## Note: In Out, properties are selected so as to preserve the information in the structure of raw. 
## For example, if two items were in the same key in raw (same row in the original CSV), 
## then there must be a relationship over them, in Out.
def structure_raw_data(raw):
    o = dict()
    r = dict()
    id_c = 1
    ats = raw['Attributes']
    for c in raw['Content']:
        for a1 in ats:
            # Unary properties.
            item_id = 'n_' + str(id_c)
            id_c = id_c + 1
            full_name = raw['Content'][c][a1]
            
            # Relationships that d['Content'][c][a1] is involved in.
            d_c_a1 = dict()
            r[raw['Content'][c][a1]] = d_c_a1
            
            for a2 in ats:
                if a1 != a2: d_c_a1[a1,a2] = (full_name, raw['Content'][c][a2])
            
            # Add entry for d['Content'][c][a1] to o.
            o[item_id] = { 'uid': item_id, 
                          'nickname': shorten_string(full_name, 15), 
                          'full_name': full_name, 
                          'instance_of': a1, 
                          'relationships':  d_c_a1 }
    return o

# Make a multi digraph that only has all edges of one relationship type.
## In: d is output of structure_raw_data, rel_from is the name of the type of origin node, and rel_to is the type of destination node.
def make_rel_net(d, rel_from, rel_to):
    global nx
    import networkx as nx
    rel_net = nx.MultiDiGraph()
    for i in d:
        for j in d[i]['relationships']:
            if j == (rel_from, rel_to): 
                rel_net.add_edge(d[i]['relationships'][j][0], d[i]['relationships'][j][1])
    return rel_net

# Return all relationships from strucured data, where the matching_attribute is equal to the matching_value.
def return_matching_relationship_instances(structured_data, matching_attribute, matching_value, rel_from, rel_to, first_column_title, second_column_title):
    output_table = list()
    for n in structured_data:
        if structured_data[n][matching_attribute] == matching_value:
            output_table.append(structured_data[n]['relationships'][rel_from, rel_to])
    from tabulate import tabulate
    print(tabulate(output_table, headers = [first_column_title, second_column_title], tablefmt="pipe"))

# Return all relationships instances from strucured data, of the relationship specified by (rel_from, rel_to).
def tabulate_all_relationship_instances(structured_data, rel_from, rel_to, first_column_title, second_column_title):
    output_table = list()
    for n in structured_data:
        try:
            output_table.append((shorten_string(remove_line_breaks(structured_data[n]['relationships'][rel_from, rel_to][0]), 25), shorten_string(remove_line_breaks(structured_data[n]['relationships'][rel_from, rel_to][1]), 75)))
        except KeyError:
            None
    from tabulate import tabulate
    print(tabulate(output_table, headers = [first_column_title, second_column_title], tablefmt="pipe"))

# Position nodes, with x value function of in_degrees of each node.
# In: Graph whose nodes need positions.
# Out: 
def pos_by_in_degrees(graph):
    import math
    pos_out = dict()
    y = 1
    s = 1 + max(dict(graph.in_degree()).values())
    for e in graph.edges():
        pos_out[e[0]] = [graph.in_degree()[e[0]], y]
        pos_out[e[1]] = [graph.in_degree()[e[1]], y]
        y = y + 10 * s
    return pos_out

# Format node labels.
# Label nodes with full_name, newline every 30 characters, shorten after first 87 characters.
def format_node_labels(graph, sd, original_attribute, line_length, total_length):
    fl = dict()
    for i in sd:
        for n in graph.nodes():
            if n == sd[i][original_attribute]:
                fl[sd[i][original_attribute]] = shorten_string(add_line_breaks(sd[i][original_attribute], line_length), total_length)
    return fl

# Offset positions of node labels, relative to node positions.
# In: Node positions, offset_x and offset_y to add to x and y of each node's position.
# Out: Offset positions dict.
def offset_node_labels(node_pos, offset_x, offset_y):
    offset_pos = dict()
    for i in node_pos:
        offset_pos[i] = [node_pos[i][0] + offset_x, node_pos[i][1] + offset_y]
    return offset_pos

# Make a list of randomly made HTML color codes.
# Returns list with as many random colors as number_of_colors.
def make_color_list(number_of_colors):
    import random
    color_list = list()
    color_list = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]
    return color_list

# Color nodes with random colors, roots are of same color (#DDDDDD by default).
def color_nodes(graph, color_list, root_color = '#DDDDDD'):
    node_colors = dict()
    c = 1
    for n in graph.nodes():
        if graph.in_degree()[n] == 0: 
            node_colors[n] = root_color
        else:
            if c <= len(color_list) - 1: 
                node_colors[n] = color_list[c]
                c = c + 1
            else:
                node_colors[n] = color_list[0]
                c = 1
    return node_colors

# Color edge with target node color.
def color_edge_by_target_node(graph, node_colors_dict):
    edge_colors = list()
    for o, d in graph.edges():
        edge_colors.append(node_colors_dict[d])
    return edge_colors

# Draw a Relationship Network.
def draw_rel_net(graph, node_positions, node_labels, node_label_positions, node_colors, edge_labels, edge_colors, fig_w = 10, fig_h = 10, dpi_val = 90, fig_margin = 0.15, save_to_project_dir = False, image_description = 'figure'):
    import networkx as nx
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure
    plt.figure(num=None, figsize=(fig_w, fig_h), dpi=dpi_val, facecolor='w')
    plt.margins(fig_margin)
    plt.axis('off')
    nx.draw_networkx_nodes(graph, node_positions, node_color = list(node_colors.values()), node_shape = 'o', node_size = 20)
    nx.draw_networkx_labels(graph, pos = node_label_positions, labels = node_labels, font_size = 8)
    nx.draw_networkx_edges(graph, node_positions, edge_color = edge_colors)
    nx.draw_networkx_edge_labels(graph, node_positions, edge_labels = edge_labels, font_size = 8)
    # Save figure as PNG file.
    image_file_name = project_name + '_' + image_description + '_' + 'w' + str(fig_w) + '_' + 'h' + str(fig_h) + '_' + str(dpi_val) + 'dpi' + '.png'
    if save_to_project_dir == False:
        plt.savefig(image_file_name)
    else: 
        import os
        os.chdir(project_name)
        plt.savefig(image_file_name)
        os.chdir('..')
    return

# Given attribute attribute_to_searh_in and (part of) value in string_to_find, return values of attribute_to_return, of the matching item.
def return_matching_case_sensitive(structured_data, attribute_to_searh_in, string_to_find, attribute_to_return):
    o = list()
    for i in structured_data:
        if string_to_find in structured_data[i][attribute_to_searh_in]:
            o.append(structured_data[i][attribute_to_return])
    return o


#############################################
### INTERNAL DEPENDENCY NETWORK functions.
#############################################

# Structure data that can be used to make a Dependency Network.
# In: Output of structure_raw_data
# Out: Dict with uid, definiendum, definiens, and cleaned up definiendum and definiens (used to find Internal and External Dependency relationship instances)
def structure_dependency_network_data(structured_data):
    dn_structured_data = dict()
    for i in structured_data:
        if structured_data[i]['instance_of'] == 'Definiendum':
            dn_structured_data[i] = { 'uid': structured_data[i]['uid'], 
                                    'definiendum': structured_data[i]['full_name'], 
                                    'clean_definiendum': return_clean_string(structured_data[i]['full_name']), 
                                    'definiens': structured_data[i]['relationships']['Definiendum', 'Definiens'][1],
                                    'clean_definiens': return_clean_string(structured_data[i]['relationships']['Definiendum', 'Definiens'][1])
                                }
    return dn_structured_data

# Find Internal Dependency relationship instances.
# In: Output of structure_dependency_network_data
# Out: Dict of Internal Dependency relationship instances
def find_internal_dependencies(x_dependency_data):
    x_dependency_relationships = dict()
    c = 0
    for i in x_dependency_data:
        for j in x_dependency_data:
            if i != j and x_dependency_data[i]['clean_definiendum'] in x_dependency_data[j]['clean_definiens']:
                x_dependency_relationships[c] = { 'definiendum': x_dependency_data[j]['definiendum'],
                                            'depends_on': x_dependency_data[i]['definiendum'] }
                c = c + 1
    return x_dependency_relationships

# Create a graph to hold the Internal Dependency Network.
# In: Output of find_internal_dependencies
# Out: Networkx MultiDiGraph with only all intenrnal Dependency Relationships.
def make_internal_dependency_network(x_dependency_relationships):
    import networkx as nx
    dpn = nx.MultiDiGraph()
    for i in x_dependency_relationships:
        dpn.add_edge(x_dependency_relationships[i]['definiendum'], x_dependency_relationships[i]['depends_on'])
    return dpn

# Compute stats of an Internal Dependency Network
# In: Output of make_internal_dependency_network
# Out: internal_dependency_stats, where:
# - depended_by is the count of terms that depend on term X
# - depends_on is the count of terms that X depends on
# - depended_by_weight is the proportion of other terms' dependence on X, in the total number of internal dependencies
# - depends_on_weight is the proportion of X's dependencies on other terms, in the total number of internal dependencies
# - depended_by_list is the list of terms which depend on X
# - depends_on_list is the list of terms which X depends on
def compute_internal_dependency_stats(internal_dependency_network):
    internal_dependency_stats = dict()
    internal_dependency_count = len(internal_dependency_network.edges())
    for i in internal_dependency_network.nodes():
        depended_by_list = list()
        depends_on_list = list()
        for o,d in internal_dependency_network.edges():
            if o == i:
                depends_on_list.append(d)
            if d == i:
                depended_by_list.append(o)
        depended_by_weight = round(internal_dependency_network.in_degree()[i] / internal_dependency_count, 3)
        depends_on_weight = round(internal_dependency_network.out_degree()[i] / internal_dependency_count, 3)
        internal_dependency_balance = round(depended_by_weight - depends_on_weight, 4)
        internal_dependency_stats[i] = { 
        'depended_by': internal_dependency_network.in_degree()[i],
        'depends_on': internal_dependency_network.out_degree()[i],
        'depended_by_weight': depended_by_weight,
        'depends_on_weight': depends_on_weight,
        'total_weight': round(depended_by_weight + depends_on_weight, 4),
        'internal_dependency_balance': internal_dependency_balance,
        'depended_by_list': depended_by_list,
        'depends_on_list': depends_on_list
        }
        del(depended_by_list)
        del(depends_on_list)
    return internal_dependency_stats

# Show data content in readable format.
def show_data(data):
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)

# Display internal dependency stats.
def show_internal_dependency_stats(internal_dependency_stats, sort_by_item):
    internal_dependency_stats_print = list()
    for i in internal_dependency_stats:
        internal_dependency_stats_print.append((shorten_string(i,25), internal_dependency_stats[i]['depended_by'], internal_dependency_stats[i]['depended_by_weight'], internal_dependency_stats[i]['depends_on'], internal_dependency_stats[i]['depends_on_weight'], internal_dependency_stats[i]['total_weight'], internal_dependency_stats[i]['internal_dependency_balance']))
    # sort by total_weight descending
    from operator import itemgetter
    internal_dependency_stats_print.sort(key = itemgetter(sort_by_item), reverse = True)
    # show on screen
    from tabulate import tabulate
    print(tabulate(internal_dependency_stats_print, headers = ['Term', 'In Count', 'In Share', 'Out Count', 'Out Share', 'Total Share', 'Balance'], tablefmt="pipe"))


#############################################
### DEFINITION TREE functions.
#############################################

# Find definition trees For each node in an internal dependency network.
# In: internal_dependency_network.
# Out: definition_trees, which is a dict, in which each item is a NetworkX graph, of a tree rooted in a given node of internal_dependency_network and obtained via depth first search. 
def find_definition_trees(internal_dependency_network):
    import networkx as nx
    definition_trees = dict()
    for i in internal_dependency_network:
        l = str()
        definition_trees[i] = nx.dfs_tree(internal_dependency_network, source=i)
        for j in definition_trees[i].nodes():
            if l is '': l = j
            else: l = l + ', ' + j
        if len(l) == len(i): l = j
        print(l)
        del(l)
    return(definition_trees)

# Compute definition trees stats.
def compute_defintion_trees_stats(definition_trees):
    definition_trees_stats = dict()
    term_count = len(definition_trees)
    for i in definition_trees:
        definition_trees_stats[i] = { 
        'size': len(definition_trees[i].nodes()),
        'coverage': round(len(definition_trees[i].nodes()) / term_count, 3)
        }
    return definition_trees_stats

# Display definition trees stats.
def show_definition_trees_stats(definition_trees_stats, sort_by_item):
    definition_trees_stats_print = list()
    for i in definition_trees_stats:
        definition_trees_stats_print.append((shorten_string(i,25), definition_trees_stats[i]['size'], definition_trees_stats[i]['coverage']))
    # sort by total_weight descending
    from operator import itemgetter
    definition_trees_stats_print.sort(key = itemgetter(sort_by_item), reverse = True)
    # show on screen
    from tabulate import tabulate
    print(tabulate(definition_trees_stats_print, headers = ['Term', 'Size', 'Coverage'], tablefmt="pipe"))


#############################################
### DEFINITION TREE SIMILARITY functions.
#############################################

# Take a list of lists of strings, and return a flat list of strings. Note recursion.
# Before calling, define an empty list to pass as l (second parameter) to flatten_lls.
def flatten_lls(d, l):
    for v in d:
        try:
            iter(d[v])
        except TypeError:
            l.append(v)
        else:
            if isinstance(d[v], str):
                l.append(d[v])
            else:
                flatten_lls(d[v], l)

# For each pair of terms, compute number of terms which appear in both of their definition trees.
def compute_successor_similarity(internal_dependency_network):
    import networkx as nx
    term_successors = dict()
    for i in internal_dependency_network.nodes():
        term_successors[i] = nx.dfs_successors(internal_dependency_network, i)
    sml = dict()
    for i in internal_dependency_network.nodes():
        for j in internal_dependency_network.nodes():
            if i != j:
                sml[i,j] = 0
    for i,j in sml:
        if i != j:
            for k in term_successors[i]:
                for l in term_successors[j]:
                    if l in k:
                        sml[i,j] = sml[i,j] + 1
    return sml

# Show list of top (if top = True) or bottom (otherwise) term pairs, by successor similarity.
def compute_successor_similarity_stats(internal_dependency_network, successor_similarity, show = 50, top = True):
    lss = list()
    for t1,t2 in successor_similarity:
        lss.append((t1,t2,successor_similarity[t1,t2]))
    from operator import itemgetter
    if top == True:
        lss.sort(key = itemgetter(2), reverse = True)
    if top == False:
        lss.sort(key = itemgetter(2), reverse = False)
    total = len(internal_dependency_network.nodes())
    terms_to_show = list()
    c = 1
    for i in lss:
        if c < show:
            terms_to_show.append((shorten_string(i[0], 30), shorten_string(i[1], 30), i[2], round(i[2] / total, 2)))
        c = c + 1
    return terms_to_show

# Take two terms, find their definition trees, and count shared nodes and edges of these trees.
def compute_definition_tree_similarity(internal_dependency_network, term1, term2):
    import networkx as nx
    g1 = nx.dfs_tree(internal_dependency_network, source = term1)
    g2 = nx.dfs_tree(internal_dependency_network, source = term2)
    shared_nodes = 0
    for n1 in g1.nodes():
        for n2 in g2.nodes():
            if n1 == n2:
                shared_nodes = shared_nodes + 1
    shared_edges = 0
    for o1,d1 in g1.edges():
        for o2,d2 in g2.edges():
            if o1 == o2 and d1 == d2:
                shared_edges = shared_edges + 1
    say = term1 + ' and ' + term2 + ' share ' + str(shared_nodes) + ' shared nodes, and ' + str(shared_edges) + ' shared edges.'
    return say

# For each pair of terms in an internal dependency network, compute the number of nodes and edges that their definition trees share.
def compute_defintion_tree_similarity_all_pairs(internal_dependency_network):
    import networkx as nx
    dfs_stats = list()
    for i in internal_dependency_network.nodes():
        for j in internal_dependency_network.nodes():
            if i != j:
                g1 = nx.dfs_tree(internal_dependency_network, source = i)
                g2 = nx.dfs_tree(internal_dependency_network, source = j)
                shared_nodes = 0
                for n1 in g1.nodes():
                    for n2 in g2.nodes():
                        if n1 == n2:
                            shared_nodes = shared_nodes + 1
                shared_edges = 0
                for o1,d1 in g1.edges():
                    for o2,d2 in g2.edges():
                        if o1 == o2 and d1 == d2:
                            shared_edges = shared_edges + 1
                dfs_stats.append((shorten_string(i, 30), shorten_string(j, 30), shared_nodes, shared_edges))
    return dfs_stats

# Show list of top (if top = True) or bottom (otherwise) term pairs, by number of shared nodes (if sort_by_shared_nodes = True) or shared edges (if sort_by_shared_nodes = False).
def show_definition_tree_similarity_stats(dfs_stats, internal_dependency_network, show = 50, top = True, sort_by_shared_nodes = True):
    out = list()
    for i in dfs_stats:
        out.append((i[0], i[1], i[2], i[3]))
    from operator import itemgetter
    if top == True:
        if sort_by_shared_nodes == True:
            out.sort(key = itemgetter(3), reverse = True)
        if sort_by_shared_nodes == False:
            out.sort(key = itemgetter(4), reverse = True)
    if top == False:
        if sort_by_shared_nodes == True:
            out.sort(key = itemgetter(3), reverse = False)
        if sort_by_shared_nodes == False:
            out.sort(key = itemgetter(4), reverse = False)
    stats_to_show = list()
    total_nodes = len(internal_dependency_network.nodes())
    total_edges = len(internal_dependency_network.edges())
    c = 1
    for i in out:
        if c < show:
            stats_to_show.append((shorten_string(i[0], 30), shorten_string(i[1], 30), i[2], round(i[2] / total_nodes, 2), i[3], round(i[3] / total_edges, 2)))
        c = c + 1
    return stats_to_show

#############################################
### EXTERNAL DEPENDENCY NETWORK functions.
#############################################

# Produce the list of most frequent words (showcount sets number of returned words) in all definientia in structured_dependency_network_data.
def external_term_candidates(structured_dependency_network_data, conservative = True, descending = True, showcount = 20):
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
    stopterms = list()
    if conservative == True:
        for i in structured_dependency_network_data:
            stopterms.append(structured_dependency_network_data[i]['clean_definiendum'])
    if conservative == False:
        for i in structured_dependency_network_data:
            for w in structured_dependency_network_data[i]['clean_definiendum'].split():
                if w not in stopwords:
                    stopterms.append(w)
    wordcount = dict()
    for i in structured_dependency_network_data:
        for word in structured_dependency_network_data[i]['clean_definiens'].lower().split():
            if word not in stopwords:
                if word not in stopterms:
                    if word not in wordcount:
                        wordcount[word] = 1
                    else:
                        wordcount[word] = wordcount[word] + 1
    wordlist = list()
    for i in wordcount:
        wordlist.append((i, wordcount[i]))
    from operator import itemgetter
    if descending == True:
        wordlist.sort(key = itemgetter(1), reverse = True)
    if descending == False:
        wordlist.sort(key = itemgetter(1), reverse = False)
    
    shortwordlist = list()
    for i in range(0,showcount):
        shortwordlist.append(wordlist[i])

    from tabulate import tabulate
    print(tabulate(shortwordlist, headers = ['Word', 'Mentions'], tablefmt="pipe"))
    return wordlist

# For each External Term x, find the number of Internal Terms which use x in its definiendum.
def internal_to_external_dependencies(structured_dependency_network_data, external_term_candidates, descending = True, showcount = 20):
    used_in = dict()
    for i in external_term_candidates:
        w = i[0]
        l = list()
        for j in structured_dependency_network_data:
            if w in structured_dependency_network_data[j]['clean_definiens']:
                l.append(structured_dependency_network_data[j]['definiendum'])
        used_in[w] = { 'used_in_internal_terms_count': len(l), 'used_in_internal_terms': l }
    # return used_in

    count_list = list()
    for i in used_in:
        count_list.append((i, used_in[i]['used_in_internal_terms_count']))
    
    from operator import itemgetter
    if descending == True:
        count_list.sort(key = itemgetter(1), reverse = True)
    if descending == False:
        count_list.sort(key = itemgetter(1), reverse = False)

    shortcountlist = list()
    for i in range(0,showcount):
        shortcountlist.append(count_list[i])

    out = { 'count_list': shortcountlist, 'in_ex_data': used_in }

    return out



def internal_term_candidates(structured_dependency_network_data, conservative = True, descending = True, showcount = 20):
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
    stopterms = list()
 
    if conservative == True:
        for i in structured_dependency_network_data:
            stopterms.append(structured_dependency_network_data[i]['clean_definiendum'])
    if conservative == False:
        for i in structured_dependency_network_data:
            for w in structured_dependency_network_data[i]['clean_definiendum'].split():
                if w not in stopwords:
                    stopterms.append(w)
 
    wordcount = dict()
    for i in structured_dependency_network_data:
        for word in structured_dependency_network_data[i]['clean_definiens'].lower().split():
            if word not in stopwords:
                if word not in stopterms:
                    if word not in wordcount:
                        wordcount[word] = 1
                    else:
                        wordcount[word] = wordcount[word] + 1

    used_in = dict()
    for i in wordcount:
        w = i[0]
        l = list()
        for j in structured_dependency_network_data:
            if w in structured_dependency_network_data[j]['clean_definiens']:
                l.append(structured_dependency_network_data[j]['definiendum'])
        used_in[w] = { 'used_in_internal_terms_count': len(l), 'used_in_internal_terms': l }

    wordlist = list()
    for i in wordcount:
        wordlist.append((i, wordcount[i], used_in[i]['used_in_internal_terms_count']))
    from operator import itemgetter
    if descending == True:
        wordlist.sort(key = itemgetter(1), reverse = True)
    if descending == False:
        wordlist.sort(key = itemgetter(1), reverse = False)
    
    shortwordlist = list()
    for i in range(0,showcount):
        shortwordlist.append(wordlist[i])

    from tabulate import tabulate
    print(tabulate(shortwordlist, headers = ['Word', 'Mentions'], tablefmt="pipe"))
    
    out = { 'wordcount': wordcount, 'used_in': used_in }
    
    return out