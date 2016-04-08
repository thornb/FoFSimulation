###################################################################
# The purpose of this script is to calculate the statistics of 
# sizes and link-connectivity of communities detected by GANXiS. 
# The network has to be undirected and no self-loops. 
# ----------------------------------------------------------------
# General Statistics: 
# 	1) Avg. Size of a Community
#	2) Smallest Size of a Community
#	3) Largest Size of a Community
#	4) Total Num. of Communities
# Link-Connectivity Statistics:
#	1) Intra-Edge-Count
#	2) Boundary-Edge-Count
#	3) Edge Bridges
#	4) Node Bridges
#	5) Avg. Shortest Path
#	6) Diameter
###################################################################

import sys
import numpy
import cPickle
import gowalla
import networkx 
import foursquare
import multiprocessing
import community_library

from random import shuffle

# Load the network from textfile to memory.  
def load_network():
	network = foursquare.get_spatial_friendship_network()
	#network = gowalla.get_spatial_friendship_network()
	G = gowalla.convert_network(network)
	return network, G

# Divide tasks among processors. 
def split_work(seq, size):
	newseq = [[] for i in xrange(size)]
	for i in xrange(len(seq)):
		newseq[i % size].append(seq[i])
	return newseq

# Check if a & b are friends. 
def is_friend(a, b):
	if b not in network[a]: return False
	if a not in network[b]: return False
	return True

# Calculate the shorthest path between pairs.
def calc_shortest_path(indexes, community):
	count = 0
	results = []
	for i in indexes:
		node_i = community[i]
		for j in xrange(i + 1, len(community)):
			node_j = community[j]
			sp = []
			results.append(len(sp) - 1)
			if is_friend(node_i, node_j):
				count = count + 1
	return results, count

# Map the calculations among processors.
def map_calc_statistics(work_input):
	indexes, community = work_input
	paths, iec = calc_shortest_path(indexes, community)
	dia = max(paths + [0])
	return iec, sum(paths), dia

# Step 1: Load the data into memory
network, G = load_network()
print "Finished loading network"
communities = community_library.IA_fs_communities_unweighted()
com_table = community_library.convert_com_table(communities)

final = []
# Step 2: Divide the tasks among processors
num_cpus = multiprocessing.cpu_count()
for community in communities:
	pool = multiprocessing.Pool(num_cpus)
	indexes = range(len(community))
	shuffle(indexes)
	work = split_work(indexes, num_cpus)
	work_input = [(element, list(community)) for element in work]
	results = pool.map(map_calc_statistics, work_input)
	pool.close()
	
	size = len(community)
	density = sum([subresults[0] for subresults in results]) / (0.5*size*(size-1))
	asp = sum([subresults[1] for subresults in results]) / (0.5*size*(size-1))
	dia = max([subresults[2] for subresults in results])
	
	print "Size: %d, Den: %lf, ASP: %lf, Dia: %lf" % (size, density, asp, dia)
	final.append((size, density, asp, dia))

# Count the number of node and edge-bridges.
edge_bridge = 0
for u,t in G.edges_iter():
	c_u = com_table[u]
	c_t = com_table[t]
	if len(c_u.union(c_t)) > 1:
		edge_bridge += 1

node_bridge = 0
for u in G.nodes_iter():
	c_u = com_table[u]
	if len(c_u) > 1:
		node_bridge += 1

print "Smallest Community Size: %d" % min([e[0] for e in final])
print "Average Community Size: %lf" % numpy.average([e[0] for e in final])
print "Largest Community Size: %d" % max([e[0] for e in final])
print "Total number of communities: %lf" % len(final)
print "Avg. Link density: %lf" % numpy.average([e[1] for e in final])
print "Number of edge-bridges: %d" % edge_bridge
print "Number of node-bridges: %d" % node_bridge
	




