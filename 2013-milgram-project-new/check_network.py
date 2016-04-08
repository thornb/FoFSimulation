# The purpose of this script is to check the
# validity of the network and make sure that
# everything is consistent.

def failed(network, locations, community, com_table, cgraph):
	f = False
	# Case1: all nodes in network have locations
	count = 0
	for node in network.keys():
		if node not in locations:
			count = count + 1
			f = True
	if f == True:
		print "Network %d. Location %d. Count %d." % (len(network.keys()), len(locations.keys()), count)

	# Case2: all nodes are in commmunity and vice-versa
	nodes_a = set(network.keys())
	nodes_b = set([node for c in community for node in c])
	if nodes_a != nodes_b:
		print "Case2 Failed. Network: %d, Community: %d" % (len(nodes_a), len(nodes_b))
		f = True

	# Case3: all nodes are in com_table and vice-versa
	nodes_a = set(network.keys())
	nodes_b = set(com_table.keys())
	if nodes_a != nodes_b:
		print "Case3 Failed. Network: %d, ComTable: %d" % (len(nodes_a), len(nodes_b))
		f = True
	
	# Case 4: community is consistent with cgraph
	community_nodes = set(range(len(community)))
	cgraph_nodes = set(cgraph.nodes())
	if community_nodes != cgraph_nodes:
		print "Case 4 Failed. Community nodes %d. Cgraph nodes %d. " % (len(community_nodes), len(cgraph_nodes))
		f = True

	return f
