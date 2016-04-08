############################################################################
# The purpose of this script is to detect spatial communities by using 
# a modification of the Clique-Percolation Method (CPM). The algorithm
# works as follows. First, it detects cliques of the size k by permuting
# friendship pairs (k=2) and then friendship triangles (k=3). Second,
# each triangle becomes a vertex, and there is an edge from this vertex to
# the vertex that together has the highest intra-edge count or link density.
# The algorithm uses spatial information between the two vertices
# triangles to break ties by taking the spatially-closest one. Finally, 
# each connected component in the clique-graph consisting of cliques a
# s nodes and edges between cliques is a community. 
# -------------------------------------------------------------------------
#  Author: Tommy Nguyen
#  Date: May 31, 2013
###########################################################################

import sys
import gowalla
import cPickle
import networkx as nx
import multiprocessing

from random import shuffle
from itertools import combinations
from multiprocessing import Pool
from multiprocessing import Process

# Definition of friendship. 
def is_friend(node_i, node_j):
	if node_i in network[node_j]:
		if node_j in network[node_i]:
			if node_j != node_i:
				return True
	return False

# Calc. the number of edges between two cliques. 
def calc_edge_count(clique_i, clique_j):
	count = 0
	for node_i in clique_i:
		for node_j in clique_j:
			if node_i in network[node_j]:
				count = count + 1
	return count

# Split a list evenly by a given size.
def split_work(seq, size):
	newseq = []
	splitsize = 1.0/size*len(seq)
	for i in xrange(size): newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
	return newseq

# The purpose of this function is to evenly divide the workload
# among nodes by using the degree of the node to estimate runtime. 
def divide_task(nodes, num_processors):
	def get_weight(node): return len(network[node]) * len(network[node]) * 0.5

	work = dict([(i, [0, []]) for i in xrange(num_processors)])
	items = sorted([(node, get_weight(node)) for node in nodes], key=lambda x: x[1], reverse=True)
 
	for node, weight in items:
		process, score = sorted([(proc, work[proc][0]) for proc in work.keys()], key=lambda x:x[1])[0]
		work[process][0] = work[process][0] + weight
		work[process][1].append(node)

	return [work[p][1] for p in work.keys()]

# Calc. the average spatial distance between members. 
def calc_avg_distance(nodes):
	def calc_distance(node_i, node_j): 
		lat1, lng1 = user_locations[node_i]
		lat2, lng2 = user_locations[node_j]
		return gowalla.calc_haversine(lng1, lat1, lng2, lat2)
	distances = [calc_distance(node_i, node_j) for node_i, node_j in combinations(nodes, 2)]
	return sum(distances) / len(distances) 

# Permute all possible triangles from the given input. 
def get_triangles(work_input):
	triangles = set()
	for node in work_input:
		for node_i, node_j in combinations(network[node], 2):
			if is_friend(node_i, node_j):
				triangle = tuple(sorted([node, node_i, node_j]))
				triangles.add(triangle)
	return triangles

# Permute all possible cliques of size k from the triangles. 
def get_cliques(work_input):
	results = set()
	for index in work_input:
		triangle = triangles[index]
		common_neighbors = network[triangle[0]].copy()
		for node in triangle: common_neighbors.intersection(network[node])
		for node in common_neighbors:
			element = tuple(sorted(triangle + (node,)))
			results.add(element)
	return results

# Find all possible edges in the clique-vertex in the modifed CPM. 
def get_clique_edges_modified(indexes):
	edge_counts = dict([(i, (-1, -1)) for i in indexes])
	for i in indexes:
		clique_i = cliques[i]
		for j in xrange(len(cliques)):
			if j == i: continue
			clique_j = cliques[j]
			current_ecount = calc_edge_count(clique_i, clique_j)
			clique_j, last_ecount = edge_counts[i]
			if current_ecount > last_ecount:
				edge_counts[i] = (j, current_ecount)
	return [(i, item[0]) for i, item in edge_counts.items()]

# Assign remaining nodes to cliques using spatial and social information. 
def assign_nodes_to_cliques(indexes):
	results = []
	for i in indexes:
		node_i = remaining_nodes[i]
		clique_j, clique_count, clique_dist = -1,-1,-1
		for j in xrange(len(cliques)):
			current_count = calc_edge_count(cliques[j], [node_i])
			if current_count > clique_count:
				avg_dist = calc_avg_distance(cliques[j] + [node_i])
				if clique_dist == -1 or avg_dist < clique_dist:
					clique_j = j
					clique_count = current_count
					clique_dist = avg_dist
		results.append((node_i, clique_j))
	return results

# Code starts here
if len(sys.argv) != 2:
	print "./cpm_parallel output-filename"
	sys.exit(1)
else:
	file_handle = open(sys.argv[1], 'w')
	num_processors = multiprocessing.cpu_count()

print "Step 1: Loading the network from DB/disk to memory."
user_locations = gowalla.get_users_locations()
network = gowalla.get_spatial_friendship_network()

print "Step 2a: Processing triangles with multiprocessors."
triangles = set()
work_input  = divide_task(network.keys(), num_processors)
work_output = Pool(num_processors).map(get_triangles, work_input)
for sub_output in work_output: triangles.update(sub_output)
print "Number of triangles found: %d " % len(triangles)

print "Step 2b: Finding disjoint triangles."
cliques = list(triangles)
cliques_sorted = sorted(cliques, key = lambda x: calc_avg_distance(x))

disjoint_cliques = set()
processed_nodes = set()
for clique in cliques_sorted:
	overlapping = False
	for node in clique:
		if node in processed_nodes:
			overlapping = True
			break
	if overlapping == False:
		for node in clique: processed_nodes.add(node)
		disjoint_cliques.add(clique)
print "Number of disjoint triangles: %d " % len(disjoint_cliques)

cliques = [list(clique) for clique in disjoint_cliques]
remaining_nodes = list(set(network.keys()) - processed_nodes)
indexes = range(len(remaining_nodes))
work_input = split_work(indexes, num_processors)
work_output = Pool(num_processors).map(assign_nodes_to_cliques, work_input)
for sub_result in work_output: 
	for node, clique_id in sub_result:
		cliques[clique_id].append(node)

print "Step 3: Connecting cliques by edges"
indexes = range(len(cliques))
work_input = split_work(indexes, num_processors)
work_output = Pool(num_processors).map(get_clique_edges_modified, work_input)

print "Step 4: Generate clique-graph based on the edges"
G = nx.Graph()
for sub_result in work_output: G.add_edges_from(sub_result)
communities = nx.connected_components(G)
print "Number of communities found %d" % len(communities)
for community in communities:
	nodes = set([node for index in community for node in cliques[index]])
	file_handle.write('%s \n' % ' '.join(map(str, list(nodes))))
