###############################################################
# The purpose of this script is to calculate the number of hops 
# for randomly selected pairs of users on LastFM and Flickr 
# social networks. 
###############################################################

import cPickle
import gowalla
import networkx
import foursquare
import multiprocessing

from random import shuffle
from random import randint

def split_work(seq, size):
	newseq = []
	splitsize = 1.0/size*len(seq)
	for i in range(5): shuffle(seq)
	for i in xrange(size): newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
	return newseq

def select_pairs(size):
	pairs = set()

	while len(pairs) < size:
		r1 = users[randint(0, len(users) - 1)]
		r2 = users[randint(0, len(users) - 1)]
		tup1 = (r1, r2)
		tup2 = (r2, r1)
		if r1 != r2 and tup1 not in pairs and tup2 not in pairs:
			pairs.add(tup1)
	return list(pairs)

def calc_paths(pairs):
	results = []
	for starter, target in pairs:
		sp = networkx.shortest_path(G, starter, target)
		results.append((starter, target, len(sp)))
	return results

# Step 1: Load the network into memory. 
network = foursquare.get_spatial_friendship_network()
G = gowalla.convert_network(network)
users = network.keys() 

# Step 2: Pick k randomly select pairs
num_pairs = 10000 # 10^4 pairs
pairs = select_pairs(num_pairs)

# Step 3: Map & Reduce the pair-wise computations
num_processors = 10
work_input = split_work(pairs, num_processors)
results = multiprocessing.Pool(num_processors).map(calc_paths, work_input)

# Step 4: Output the results
for sub_results in results:
	for starter, target, hop in sub_results:
		print starter, target, hop
