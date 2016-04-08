import sys
import random
import gowalla
import foursquare
import networkx as nx
import multiprocessing

def get_pool(size = -1):
    if size == -1: size = multiprocessing.cpu_count()
    return multiprocessing.Pool(size)

def split_work(seq, size=-1):
    if size == -1: size = multiprocessing.cpu_count()
    if type(seq) == type(set()): seq = list(seq)
    results = [[] for i in xrange(size)]
    for i in xrange(len(seq)): results[i % size].append(seq[i])
    return results

def calc_diameter(nodes):
	count = 0
	diameter = 0
	for node in nodes:
		sp = nx.shortest_path(G, source=node)
		for node, path in sp.items():
			if len(path) > diameter:
				diameter = len(path)
		count = count + 1
		print "Current Diameter: %d. Remaining: %d. " % (diameter, len(nodes) - count)
	return diameter

code = int(sys.argv[1])
if code == 0: network = gowalla.get_spatial_friendship_network()
if code == 1: network = foursquare.get_spatial_friendship_network()
G = gowalla.convert_network(network)

nodes = network.keys()
for i in xrange(5): random.shuffle(nodes)
nodes = nodes[0:10000]

pool = get_pool()
work = split_work(nodes)
results = pool.map(calc_diameter, work)

print "Estimated Diamter %d" % max(results)
