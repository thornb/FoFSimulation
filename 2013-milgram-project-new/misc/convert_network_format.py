###################################################
# The purpose of this script is to convert the 
# network text-file format into network dictionary
# and networkx format. 
###################################################

import cPickle
import networkx
 
def load_network(filename):
	count = 0
	network = {}
	G = networkx.Graph()
	for line in open(filename, 'r'):
		a, b = line.strip().split(' ')

		if a == b: 
			print "Error: Self-loops"
			sys.exit()
		if a in network and b in network[a]:
			print "Error: duplicate edges"
			sys.exit(1)
		if b in network and a in network[b]:
			print "Error: duplicate edges"
			sys.exit(1)
		
		if a not in network: network[a] = set()
		if b not in network: network[b] = set()
		if b in network and a in network[b]: continue
		

		network[a].add(b)
		G.add_edge(a,b)
		count = count + 1	
		if count % 50000 == 0: print "Proccessed %d edges." % count
	return network, G

network, G = load_network('foursquare_network_llc_Nov18_2013.txt')
cPickle.dump(network, open('foursquare_network.p', 'wb'))
cPickle.dump(G, open('foursquare_graph.g', 'wb'))
