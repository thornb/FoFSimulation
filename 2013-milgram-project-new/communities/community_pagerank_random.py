import sys
import numpy
import gowalla
import foursquare
import multiprocessing
import routing_simulation_loader 

from random import choice
from routing_simulation_loader import load_community
from routing_simulation_loader import load_network 
from community_library import convert_com_table
from community_library import ganxis_gw_communities_overlapping_ttl
from community_library import ganxis_fs_communities_overlapping_unweighted_ttl

def split_work(seq, size):
	results = [[] for i in xrange(size)]
	for i in xrange(len(seq)): results[i % size].append(seq[i])
	return results

def generate_cover(size):
	cover = set()
	while len(cover) < size: 
		cover.add(choice(nodes))
	return cover

def random_community(work):
	results = []
	for size in work:
		cover = generate_cover(size)
		values = [pagerank[node] for node in cover]
		avg_pr = numpy.average(values)
		std_pr = numpy.var(values)	
		results.append((avg_pr, std_pr))
	return results

# Input Parameters
network_code = int(sys.argv[1])
community_code = int(sys.argv[2])

# Load data from disk to memory
network, locations, pagerank, states = load_network(network_code)
communities, com_table, cgraph, stationary = load_community(network_code, community_code)

# Parameters
increment = 5
trails    = 1000
largest   = max([len(com) for com in communities])
smallest  = min([len(com) for com in communities])

# Calculations
nodes = network.keys() 
num_cpus = multiprocessing.cpu_count()

for i in xrange(smallest, largest, increment):
	pool = multiprocessing.Pool(num_cpus)
	work_input = split_work([i] * trails, num_cpus)
	results = pool.map(random_community, work_input)
	pool.close()

	averages  = [value[0] for subresults in results for value in subresults]
	variances = [value[1] for subresults in results for value in subresults]	
	print i, numpy.average(averages), numpy.average(variances)

	
	

