import gowalla
import cPickle
import foursquare
import multiprocessing
import routing_simulation_loader 

from math import log
from random import random
from numpy import average, std
from gowalla import convert_network, calc_spatial_dist
from itertools import combinations, product
from community_library import convert_com_table
from community_library import ganxis_gw_communities_overlapping_ttl
from community_library import ganxis_fs_communities_overlapping_unweighted_ttl

def get_community_pagerank(communities):
	results = {}
	for i in xrange(len(communities)):
		val = [pagerank[node] for node in communities[i]]
		results[i] = average(val)
	return results

network_code = 1
community_code = 2

network, locations, pagerank, states = routing_simulation_loader.load_network(network_code)
communities, com_table, cgraph, stationary = routing_simulation_loader.load_community(network_code, community_code)

com_table = convert_com_table(communities)
com_pagerank = get_community_pagerank(communities)
G = convert_network(network)

for node, com in com_table.items():
	for ci, cj in combinations(com, 2):
		val = com_pagerank[ci] - com_pagerank[cj]
		print ci, cj, val, abs(val)

for u,v in G.edges_iter():
	com_u = com_table[u]
	com_v = com_table[v]
	for ci, cj in product(com_u, com_v):
		if ci == cj: continue
		val = com_pagerank[ci] - com_pagerank[cj]
		#print ci, cj, val, abs(val)
