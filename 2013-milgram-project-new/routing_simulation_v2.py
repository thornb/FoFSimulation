import sys
import math
import random
import os.path
import collections
import multiprocessing

import gowalla
import foursquare
#import check_network
import community_index
import community_library 
import routing_simulation_loader
import routing_simulation_parameters

from itertools import product
from pymongo import Connection
from itertools import combinations
from networkx import shortest_path
from gowalla import calc_spatial_dist
from random import random, randint, shuffle, choice, sample

def get_connection(): return Connection('sd-01.cs.rpi.edu', 27017)
def get_database(db, collection): return get_connection()[db][collection]

##############################################################
## General Helper functions
##############################################################
def random_pick(items): 
	if type(items) == type([]): return choice(items)
	if type(items) == type(set()): return sample(items, 1)[0]

def split_work(seq, size):
	results = [[] for i in xrange(size)]
	for i in xrange(len(seq)): results[i % size].append(seq[i])
	return results

def get_pairs(size):
	if selection_code == 0: return pairs_hop_communities(size)
	if selection_code == 1: return pairs_out_communities(size)
	if selection_code == 2: return random_pairs(size)
	if selection_code == 3: return geo_distant_pairs(size)
	if selection_code == 4: return pairs_hop_communities(size)
	if selection_code == 5: return get_states_pairs()
	if selection_code == 6: return all_pairs()
	if selection_code == 7: return fixed_targets()

def is_valid(seed, target, pairs): 
	if seed == target: return False
	return (seed, target) not in pairs and (target, seed) not in pairs 

def calc_dist(seed, target): 
	return calc_spatial_dist(locations[seed], locations[target])

def calc_ndist(seed, target):
	pairs = product(com_table[seed], com_table[target])
	ndistances = [len(shortest_path(cgraph, ci, cj)) for ci, cj in pairs]
	return min(ndistances) - 1

def same_community(seed, target):
	common = com_table[seed].intersection(com_table[target])
	if len(common) > 0: return True
	return False

###############################################################
## Seed/Target selection mechanisms
###############################################################
# Select Seed/Target that are seperated by some number of communities. 
def pairs_hop_communities(size):
	pairs = set()
	choices = com_index[community_hop]
	while len(pairs) < size:
		c_i, c_j = random_pick(choices)
		node_i = random_pick(community[c_i])
		node_j = random_pick(community[c_j])
		if is_valid(node_i, node_j, pairs):
			pairs.add((node_i, node_j))
	return list(pairs)

# Select Seed/Target that are not in the same community. 
def pairs_out_communities(size):
	pairs = set()
	nodes = network.keys()
	while len(pairs) < size:
		seed = random_pick(nodes)
		target = random_pick(nodes)
		common = com_table[seed].intersection(com_table[target])
		if len(common) == 0 and is_valid(seed, target, pairs): 
			pairs.add((seed, target))
	return list(pairs)

# Randomly select seed & target w/ equal probability. 
def random_pairs(size):
	pairs = set()
	users = network.keys()
	while len(pairs) < size:
		seed = random_pick(users)
		target = random_pick(users)
		if is_valid(seed, target, pairs): 
			pairs.add((seed, target))
	return list(pairs)

def all_pairs():
	pairs = set()
	users = network.keys()
	for target in users:
		my_pairs = set()
		while len(my_pairs) < 100:
			seed = random_pick(users)
			if is_valid(seed, target, my_pairs):
				my_pairs.add((seed, target))
		pairs.update(my_pairs)
	return list(pairs)

def fixed_targets(sample_size=1000, trails=1000):
	if network_code == 0: cursor = get_database("gowalla", "com_index")
	if network_code == 1: cursor = get_database("foursquare", "com_index")
	
	table = {}
	for item in cursor.find({'hop': 3}):
		table[item['c_i']] = item['edges']

	cache = {}
	pairs = set()
	communities = table.keys()
	while len(pairs) < sample_size * trails:
		c_t = random_pick(communities)
		target = random_pick(community[c_t])

		if c_t not in cache:
			nodes = list(set([node for c_j in table[c_t] for node in community[c_j]]))
			for i in xrange(3): shuffle(nodes)
			cache[c_t] = nodes
		else:
			nodes = cache[c_t]
		
		if len(nodes) < trails: continue

		temp = set()
		for starter in nodes:
			if len(temp) == trails: break 
			if is_valid(starter, target, temp) == False: continue
			if is_valid(starter, target, pairs) == False: continue
			temp.add((starter, target))

		pairs.update(temp)
		print len(pairs), sample_size, trails, sample_size * trails
	return list(pairs)

# Select seed & target so they are geographically distant. 
def geo_distant_pairs(size):
	pairs = set()
	users = network.keys()
	while len(pairs) < size:
		seed = random_pick(users)
		target = random_pick(users)
		dist = calc_dist(seed, target)
		if dist > 2500 and is_valid(seed, target, pairs):
			pairs.add((seed, target))
	return list(pairs)

# Select seed & target based on geographical states.
def get_states_pairs():
	pairs = set()
	users = network.keys()
	nodes = [u for s,items in states.items() for u in items]

	for node in nodes:
		if node not in network: continue
		starter = random_pick(users)
		target = node
		if target != starter: pairs.add((starter, target))

	return list(pairs)

# Select seed & target that are always the same. 
def fixed_nodes():
	pairs = set()
	users = network.keys()
	s = users[100]
	t = users[1000]
	pairs.add((s,t))
	return list(pairs)
					
###############################################################
# Routing mechanism
###############################################################
def calc_geo_distances(nodes, target):
	distances = [(node, calc_dist(node, target)) for node in nodes]
	return sorted(distances, key = lambda x: x[1])

def calc_network_distances(nodes, target):
	distances = [(node, calc_ndist(node, target)) for node in nodes]
	return sorted(distances, key = lambda x: x[1])

def calc_alpha(gd, nd):
	if gd < 1 : gd = 1
	return alpha * math.log(gd) + (1 - alpha) * nd

def random_routing(nodes, chain):
	while len(nodes) > 0:
		rindex = randint(0, len(nodes) - 1)
		selected = nodes.pop(rindex)
		if selected not in chain: return selected
	return -1

def geo_only(nodes, target, chain):
	distances = calc_geo_distances(nodes, target)	
	for node, dist in distances:
		if node not in chain: return node
	return -1

def community_only(nodes, target, chain):
	distances = calc_network_distances(nodes, target)	
	for node, dist in distances: 
		if node not in chain: return node
	return -1

def geo_and_community(nodes, target, chain): 
	selected_friends = [node for node in nodes if same_community(node, target)]
	remaining_friends = nodes - set(selected_friends)
	distances = calc_geo_distances(selected_friends, target) + calc_geo_distances(remaining_friends, target)
	for node, dist in distances: 
	    if node not in chain: return node
	return -1
	
def geo_com_interactions(nodes, target, seed, chain):
    weights = []
    for node in nodes:
        if (seed, node) not in interactions:
            score = 0.5
        else:
            score = float(interactions[(seed, node)])
        w = (score ) / max(1.0, calc_dist(node, target))
        weights.append((node, w))
        
    weights = sorted(weights, key=lambda x: x[1], reverse=True)
    for node, w in weights: 
        if node not in chain: return node
    return -1
        
def two_hop_routing(friends, target, chain):
	geo_closest = lambda x: calc_dist(x, target)  
	friends = [f for f in friends if f not in chain]
	temp = [ff for f in friends for ff in network[f] if random() <= two_hop_prob]
	ffriends = set(temp) - set(friends) - chain

	if len(friends) == 0: return -1

	# Case 1: Same community
	candidates = [f for f in friends if same_community(f, target)]
	if len(candidates) > 0: return min(candidates, key=geo_closest)

	# Case 2: friends-of-friends who is in the same community as the target. 
	candidates = [ff for ff in ffriends if same_community(ff, target)]
	if len(candidates) > 0:
		candidate = min(candidates, key=geo_closest)
		parents = [f for f in friends if candidate in network[f]]
		return min(parents, key=geo_closest) 

	# Case 3: Geographically
	return min(friends, key=geo_closest)

def hub_routing(friends, target, chain):
	friends = [f for f in friends if f not in chain]
	if len(friends) == 0: return -1
	high_deg = lambda x: len([f for f in network[x] if same_community(f, target)])
	return max(friends, key=high_deg)
	
def hub_geocom(friends, target, chain):
	high_deg = lambda x: len(network[x])
	friends = [f for f in friends if f not in chain]
	if len(friends) == 0: return -1

	# Same community. Ties are selected based on degree
	candidates = [f for f in friends if same_community(f, target)]
	if len(candidates) > 0: return max(candidates, key=high_deg)

	# Within proximity. Ties are selected based on degree
	candidates = [f for f in friends if calc_dist(f, target) < hub_distance]
	if len(candidates) > 0: return max(candidates, key=high_deg)
	
	# Select a friend based on geographical proximity. 
	return geo_only(friends, target, chain)

###############################################################
# Simulate Milgram's Experiment
###############################################################
def simulate_routing(seed, target):	
	num_hops = 1
	chain = [seed] 
	visited_com = []
	
	while seed != -1:
		if target in network[seed]: 
			return (num_hops, visited_com)		
		friends = network[seed].copy()

		chc = com_table[seed]
		if routing_code == 0: seed = random_routing(list(friends), set(chain))
		if routing_code == 1: seed = geo_only(friends, target, set(chain))
		if routing_code == 2: seed = community_only(list(friends), target, set(chain))
		if routing_code == 3: seed = geo_and_community(friends, target, set(chain))
		if routing_code == 4: seed = two_hop_routing(friends, target, set(chain))
		if routing_code == 5: seed = hub_routing(friends, target, set(chain))
		if routing_code == 6: seed = hub_geocom(friends, target, set(chain))
		if routing_code == 7: seed = geo_com_interactions(friends, target, seed, set(chain))

		if seed != -1: 
			nhc = com_table[seed]
			for e in product(chc, nhc):
				visited_com.append(e)

		if seed != -1:
			num_hops = num_hops + 1
			chain.append(seed)

	return (-1, visited_com)

def get_prominence(node):
	vals = [(c, stationary[c]) for c in com_table[node]]
	c_i, lambda_i = max(vals, key = lambda x: x[1])
	return lambda_i

def map_simulate_routing(pairs):
	results = []
	us_map = dict([(node, state) for state, nodes in states.items() for node in nodes])

	count = 0
	for seed, target in pairs:
		print "Simulating seed %s and target %s. Remaining %d." % (seed, target, len(pairs) - count)
		sp, nd = [], -1
		gd = calc_dist(seed, target)
		hops, coms = simulate_routing(seed, target)
		uniq_coms = len(set(coms))	
		change_coms = sum([1 for i in range(1, len(coms)) if coms[i-1] != coms[i]])
		pr_score = pagerank[target]
		#state = us_map[target]
		state = -1		
		lambda_st = (get_prominence(seed), get_prominence(target))
		pair = (str(seed), str(target))
		results.append((hops, len(sp), gd, nd, uniq_coms, change_coms, pr_score, state, coms, lambda_st, pair))
		#except:
		#	print "ERROR"
		#	continue
		count = count + 1
	return results

# Loading simulation parameters
parameters 		= routing_simulation_parameters.load_parameters(sys.argv)
network_code 	= parameters[0]
selection_code 	= parameters[1]
routing_code 	= parameters[2]
community_code 	= parameters[3]
prob 			= parameters[4]
community_hop 	= parameters[5]
two_hop_prob	= parameters[6]
hub_distance 	= parameters[7]

interactions = {}
for line in open('data/gowalla_interactions.txt', 'r'):
    s, t, w = line.strip().split(' ')
    interactions[(s, t)] = int(w)
    interactions[(t, s)] = int(w)
    
output_parameters = 'sr_%d_%d_%d_%d_%0.1lf_%d_%lf' % (network_code, selection_code, routing_code, community_code, prob, community_hop, two_hop_prob)
filename='simulation_results/%s.txt' % output_parameters

if os.path.exists(filename):
	print "Already ran the simulation"
	print filename
	sys.exit(1)

# Loading the data into memory
network, locations, pagerank, states = routing_simulation_loader.load_network(network_code)
community, com_table, cgraph, stationary = routing_simulation_loader.load_community(network_code, community_code)

G = gowalla.convert_network(network)
users = network.keys()

if selection_code == 4: 
	com_index = community_index.get_community_index(network_code, community_code)

check = check_network.failed(network, locations, community, com_table, cgraph)
if check == True: 
	print "Something is wrong with input parameters"
	sys.exit(1)

# Simulation starts here
num_pairs = 10000
pairs = get_pairs(num_pairs)

num_cores = multiprocessing.cpu_count()
pool = multiprocessing.Pool(num_cores)
work_input = split_work(pairs, num_cores)
results = pool.map(map_simulate_routing, work_input)

parameters = (network_code, selection_code, routing_code, community_code, prob, community_hop, two_hop_prob, hub_distance)
output_parameters = 'sr_%d_%d_%d_%d_%0.1lf_%d_%lf_%lf' % parameters
filename='simulation_results/%s.txt' % output_parameters

fileh = open(filename, 'w')
for subresults in results:
	for e in subresults:
		line = '%d %d %0.15lf %d %d %d %0.15lf %s %0.15lf %0.15lf %s %s\n' % (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[9][0], e[9][1], e[10][0], e[10][1])
		fileh.write(line)
fileh.close()

#filename='foursquare_pij_simulations.txt'
#fileh=open(filename, 'w')
#for subresults in results:
#	for e in subresults:
#		for ci, cj in e[8]:
#			fileh.write('%d %d %d\n' % (ci, cj, e[0]))
#fileh.close()

