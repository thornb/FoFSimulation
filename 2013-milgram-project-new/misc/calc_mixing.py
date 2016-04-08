import numpy
import gowalla
import foursquare
import networkx as nx

def get_degrees(): return [len(network[node]) for node in network.keys()]
def max_degree():  return max(get_degrees())

def calc_pk():
	degrees = get_degrees()
	total = float(len(degrees))
	return { k : degrees.count(k) / total for k in xrange(0, max(degrees) + 1)}

def calc_qk():
	avg_degree = sum([k * val for k, val in pk.items()]) 
	return { k : k * pk[k] / avg_degree for k in xrange(max_degree() + 1)}

def calc_eij():
	count = {}
	total = 2 * len(G.edges())

	for u, v in G.edges_iter():
		deg_u = min(len(network[u]), len(network[v]))
		deg_v = max(len(network[u]), len(network[v]))
		
		key1 = (deg_u, deg_v)
		key2 = (deg_v, deg_u)
	
		if key1 not in count: count[key1] = 0
		if key2 not in count: count[key2] = 0
	
		count[key1] += (1.0 / total)
		count[key2] += (1.0 / total)

	return count

def get_eij(i, j):
	if (i,j) not in eij: return 0
	return eij[(i,j)]

def calc_qk_var():
	avg_qk = sum([k * val for k, val in qk.items()])
	return sum([qk[i] * pow(i - avg_qk, 2) for i in xrange(max_degree() + 1)])

def calc_coeff():
	total = 0.0
	N = max_degree()

	for i in xrange(N):
		for j in xrange(N):
			total += (i * j) * (get_eij(i,j) - qk[i] * qk[j])

	return total / qk_var

network = {}
G = nx.read_gml('power.gml')
for s, t in G.edges():
	if s not in network: network[s] = []
	if t not in network: network[t] = []
	network[s].append(t)
	network[t].append(s)

network = gowalla.get_spatial_friendship_network()
G = gowalla.convert_network(network)

pk = calc_pk()
qk = calc_qk()
eij = calc_eij()
qk_var = calc_qk_var()
r = calc_coeff()

print r



