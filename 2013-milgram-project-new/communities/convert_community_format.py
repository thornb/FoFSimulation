#######################################################
# The purpose of this script is to convert network and 
# community format into networkx graph representation
#######################################################

import cPickle
import gowalla
import networkx
import foursquare
import multiprocessing
import community_library

from community_library import convert_com_table

# Save results here
output_file = 'foursquare_network_largest_cgraph.pck'

# General helper functions
def split_work(seq, size):
	newseq = [[] for i in xrange(size)]
	for i in xrange(len(seq)):
		newseq[i%size].append(seq[i])
	return newseq

def is_connected(i, j):
	com_i = community[i]
	com_j = community[j]
	
	# Case 1: Existence of an overlapping node
	overlapping = com_i.intersection(com_j)
	if len(overlapping) > 0:
		print "community %d is connected to community %d " % (i, j) 
		return True

	# Case 2: Existence of an overlapping bridge
	for node in com_i:
		for friend in network[node]:
			if friend in com_j: 
				print "community %d is connected community %d " % (i, j) 
				return True

	return False

def calc_edges(work_input):
	results = []
	for i in work_input:
		edges = [(i, j) for j in xrange(i+1, len(community)) if is_connected(i, j)]
		results += edges
	return results

# Step 1: load the network and community 
network = foursquare.get_spatial_friendship_network('/data/foursquare_network_largest.pck')
foursquare_path = '../2013-communities-detection/foursquare/SLPA_TTL_UNWEIGHTED/'
filename = "SLPAw_foursquare_network_largest_Nov18_2013_run1_r0.2_v4_TTL100_T100_NL1953189_LP0.0_GP0.0.icpm"
community = community_library.get_communities(foursquare_path + filename)

# Step 2: divide the work among processors
num_procs = multiprocessing.cpu_count()
work = range(len(community))
work_input = split_work(work, num_procs)

# Step 3: map the calculation to processors
pool = multiprocessing.Pool(num_procs)
results = pool.map(calc_edges, work_input)

# Step 4: dump the results
G = networkx.Graph()
for sub_results in results: G.add_edges_from(sub_results)
cPickle.dump(G, open(output_file, 'wb'))

print "Total number of nodes in cgraph %d" % len(G.nodes())
print "Total number of edges in cgraph %d" % len(G.edges())

