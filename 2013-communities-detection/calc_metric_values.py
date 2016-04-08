from itertools import product
from itertools import combinations

def delta(communities, i, j):
	for community in communities:
		if i in community and j in community:
			return True
	return False

def is_connected(network, i, j):
	if i in network[j] and j in network[i]:
		return 1
	return 0

def calc_num_edges(network):
	m = 0
	for i, j in product(network.keys(), repeat=2):
		m = m + is_connected(network, i, j)
	return 0.5 * m

def calc_modularity(network, communities):
	total = 0
	nodes = network.keys()
	m = calc_num_edges(network)

	for i, j in product(nodes, repeat=2):
		a_ij = is_connected(network, i, j)
		expected = (len(network[i]) * len(network[j])) / (2*m)
		val = a_ij - expected
		if delta(communities, i, j):
			total = total + val

	return total / (2*m)

def calc_split_penalty(network, communities):
	m = 2 * calc_num_edges(network)

	total = 0
	for i, j in product(network.keys(), repeat = 2):
		if delta(communities, i, j) == False:
			total = total + is_connected(network, i, j)

	return total / m

def calc_modularity_with_penalty(network, communities):
	m = calc_num_edges(network)

	total = 0
	for i, j in product(network.keys(), repeat = 2):
		a_ij = 2 * is_connected(network, i, j)
		expected = (len(network[i]) * len(network[j])) / (2*m) 
		if delta(communities, i, j) == True:
			val = a_ij - expected
		else:
			val = 0
		total += (val - is_connected(network, i, j))
	return total / (2*m)

def get_community(node, communities):
	for com in communities:
		if node in com: 
			return com

def calc_community_density(network, community):
	edge_count = 0
	k = len(community)
	for node_i, node_j in combinations(community, 2):
		edge_count = edge_count + is_connected(network, node_i, node_j)
	return edge_count / (0.5 * k * (k - 1)) 

def calc_communities_density(network, c_i, c_j):
	edge_count = 0
	for i in c_i:
		for j in c_j:
			edge_count = is_connected(network, i, j) 
	return edge_count / (len(c_i) * len(c_j))

def calc_modularity_with_density(network, communities):
	m = calc_num_edges(network)
	
	total = 0
	for i, j in product(network.keys(), repeat = 2):
		c_i = get_community(i, communities)
		d_c_i = calc_community_density(network, c_i)
		a_ii = is_connected(network, i, j) 
		expected = (len(network[i]) * len(network[j])) / (2*m) 
		if delta(communities, i, j) == True:
			val = (a_ii * d_c_i) - (expected * (d_c_i * d_c_i))
			total += val
	LHS = total / (2*m)

	total = 0
	for i, j in product(network.keys(), repeat = 2):
		if delta(communities, i, j) == False:
			a_ii = is_connected(network, i, j)
			c_i = get_community(i, communities)
			c_j = get_community(j, communities)
			d_ij = calc_communities_density(network, c_i, c_j)
			total += (a_ii*d_ij)
	RHS = total / (2*m)

	return LHS - RHS

def calc_edge_count(network, community):
	count = 0
	for i, j in combinations(network, community):
		count = count + is_connected(network, i, j)
	return count

def calc_edge_out(network, community):
	count = 0
	for i in community:
		for node in network[i]:
			if node not in community:
				count = count + 1
	return count

def calc_modularity_with_density_two(network, communities):
	total = 0
	for community in communities:
		ci_edge_count = calc_edge_count(network, community)
		d_c_i = calc_community_density(network, community)
		num_edges = calc_num_edges(network)

		ci_edge_out = calc_edge_out(network, community)
	
		for community_j in communities:
			if community_j != community_i:
				summation = 


def calc_values(network):
	c1 = [[1,2,3,4,5,6,7,8]]
	c2 = [[1, 2, 3, 4], [5, 6, 7, 8]]

	print "Modularity of Two Communities: %lf " % calc_modularity(network, c2)
	print "Modularity of One Community  : %lf " % calc_modularity(network, c1)
	print "Split Penalty of Two communities: %lf " % calc_split_penalty(network, c2)
	print "Split Penalty of One Community: %lf " % calc_split_penalty(network, c1)
	print "Qs Two Communities: %lf " % calc_modularity_with_penalty(network, c2)
	print "Qs One Community: %lf " % calc_modularity_with_penalty(network, c1)
	print "Qds Two Communities: %lf " % calc_modularity_with_density(network, c2)
	print "Qds One Community: %lf " % calc_modularity_with_density(network, c1)

# Example Fig. 1 (a)
network_1 = {1: [2, 3, 4], 
			 2: [1, 3, 4],
			 3: [1, 2, 4],
			 4: [1, 2, 3], 
			 5: [6, 7, 8],
			 6: [5, 7, 8], 
			 7: [5, 6, 8],
			 8: [5, 6, 7]}

# Example Fig. 1 (b)
network_2 = {1: [2, 3, 4], 
			 2: [1, 3, 4, 5],
			 3: [1, 2, 4],
			 4: [1, 2, 3, 7], 
			 5: [6, 7, 8, 2],
			 6: [5, 7, 8], 
			 7: [5, 6, 8, 4],
			 8: [5, 6, 7]}

# Example Fig. 1 (c)
network_3 = {1: [2, 3, 4], 
		 	 2: [1, 3, 4, 5, 7],
		 	 3: [1, 2, 4],
		 	 4: [1, 2, 3, 7], 
			 5: [6, 7, 8, 2],
			 6: [5, 7, 8], 
			 7: [5, 6, 8, 4, 2],
			 8: [5, 6, 7]}

calc_values(network_1)
