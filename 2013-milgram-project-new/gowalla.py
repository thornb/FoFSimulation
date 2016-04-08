########################################################
# The purpose of this script is to interact with the
# MongoDB database. This script currently supports
# launching data from MongoDB directly to the code 
# and loading the data from the disk to the code
# ---------------------------------------------------
# Author: Tommy Nguyen
# Last Modified: May 9, 2013
########################################################

import os.path
import cPickle
import math

from math import *
from networkx import nx
from random import shuffle
from pymongo import Connection
from itertools import combinations
from numpy import average

def get_connection(): return Connection('ganxis.nest.rpi.edu', 27017)
def get_database(db, collection): return get_connection()[db][collection]

##############################################################
# Get Friendship Network from DB or Disk
def get_friendship_network(filename='data/friendship_network.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		network = get_network_friends_from_db()
		cPickle.dump(network, open(filename, 'wb'))
	return network	

def get_pagerank(filename = 'data/gowalla_pagerank.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		network = get_network_friends_from_db()
		pagerank = nx.pagerank(convert_network(network))
		cPickle.dump(pagerank, open(filename, 'wb'))
	return pagerank	

# Get Spatially-Aware Friendship Network
def get_spatial_friendship_network(filename = 'data/gowalla_spatial_network.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		network = get_spatial_network_friends_from_db()
		cPickle.dump(network, open(filename, 'wb'))
	return network

# Get Location of Users from DB or Disk
def get_users_locations(filename = 'data/gowalla_users_locations.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		locations = get_users_locations_from_db()
		cPickle.dump(locations, open(filename, 'wb'))
	return locations

# Get Checkins of Users from DB or Disk
def get_users_checkins(filename = 'data/gowalla_users_checkins.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		checkins = get_users_checkins_from_db()
		cPickle.dump(checkins, open(filename, 'wb'))
	return checkins

# Get users ids
def get_ids(filename = 'data/user_keys.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		userids = get_users_ids_from_db()
		cPickle.dump(userids, open(filename, 'wb'))
	return userids

# Get user hashed ids
def get_hashed_ids(filename = 'data/gowalla_keys.txt'):
	return dict([tuple(line.strip().split(' '))[::-1] for line in open(filename, 'r')])

def calc_spatial_dist(user_a, user_b):
	lat1, lng1 = user_a
	lat2, lng2 = user_b
	return calc_haversine(lng1, lat1, lng2, lat2)
	
# Calc. the spatial distance betweena a and b. 
def calc_haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km 

# Uses max-flow to calc. physical interaction btw. users
def calc_physical_interaction(a_checkins, b_checkins):
	count = 0
	matches = {}

	for a_lat, a_lng, a_time in a_checkins:
		key = (a_lat, a_lng, a_time)
		matches[key] = []
		for b_lat, b_lng, b_time in b_checkins:
			t_diff = math.fabs(a_time - b_time)
			if t_diff < 30 * 60: 
				dist = calc_haversine(a_lng, a_lat, b_lng, b_lat)
				if dist < 1: matches[key].append((b_lat, b_lng, b_time))

	G = nx.DiGraph()
	G.add_edge('supersource', 'supersink', capacity = 0.0)
	for key, matched in matches.items():
		if len(matched) == 0: continue
		G.add_edge('supersource', key, capacity = 1.0)
		for node in matched: 
			G.add_edge(key, node, capacity = 1.0)
			G.add_edge(node, 'supersink', capacity = 1.0)

	max_flow = nx.max_flow(G, 'supersource', 'supersink')	
	return float(max_flow) / min(len(a_checkins), len(b_checkins))

# Return the network with nx representation
def convert_network(network):
	G = nx.Graph()
	for user, friends in network.items():
		for friend in friends:
			G.add_edge(user, friend)
	return G

###############################################################
# Loading the entire network from server. 
def get_network_friends_from_db():
	network = {}
	cursor = get_database("gowalla", "network")
	for item in cursor.find({}, {'friends': 1, 'user_id': 1}): 
		network[item['user_id']] = set(item['friends'])
	return network

def get_spatial_network_friends_from_db():
	cursor = get_database("gowalla", "network")

	network = {}
	squery = {'checkins_count': {'$gt': 0}}
	rquery = {'freq_loc': 1, 'user_id': 1, 'friends': 1}
	for item in cursor.find(squery, rquery):
		user_id = item['user_id']
		lat = float(item['freq_loc']['lat'])
		lng = float(item['freq_loc']['lng'])
		if lat != -1 and lng != -1: 
			network[user_id] = set(item['friends'])

	for user in network.keys():
		friends = [f for f in network[user] if f in network and f != user]
		network[user] = set(friends)

	G = nx.Graph()
	for node, friends in network.items():
		edges = [(node, f) for f in friends]
		G.add_edges_from(edges)

	lcc = set(nx.connected_components(G)[0])
	lcc_network = {}

	for user in lcc:
		friends = [f for f in network[user] if f in lcc] 
		lcc_network[user] = set(friends)
		
	return lcc_network

def load_network(filename):
	network = {}
	for line in open(filename, 'r'):
		a,b = line.strip().split(' ')
		if a not in network: network[a] = set()
		if b not in network: network[b] = set()
		network[a].add(b)
		network[b].add(a)
	return network

# Loading the entire network from server. 
def get_users_locations_from_db():
	locations = {}
	cursor = get_database("gowalla", "network")
	for item in cursor.find({'checkins_count': {'$gt': 0}}, {'freq_loc': 1, 'user_id': 1}):
		user_id = item['user_id']
		lat = float(item['freq_loc']['lat'])
		lng = float(item['freq_loc']['lng'])
		if lat != -1 and lng != -1: 
			locations[user_id] = (lat, lng)
	return locations

# Loading the userids
def get_users_ids_from_db():
	user_ids = {}
	cursor = get_database("gowalla", "hashed_ids")
	for item in cursor.find({}): 
		user_ids[item['value']] = item['user_id']
	return user_ids

# Loading checkins
def get_users_checkins_from_db():
	checkins = {}
	cursor = get_database("gowalla", "network")
	for item in cursor.find({}, {'checkins' : 1, 'user_id': 1}):
		user_id = item['user_id']
		checkins[user_id] = item['checkins']
	return checkins

def get_weighted_network():
	edges = [line.strip().split(' ') for line in open('spatial_network.txt', 'r')]
	user_locations = get_users_locations()
	output = open('spatial_network_weighted.txt', 'w')

	for a, b in edges:
		lat1, lng1 = user_locations[a]
		lat2, lng2 = user_locations[b]
		d = calc_haversine(lng1, lat1, lng2, lat2)
		if d <= 0.0152115030237: d = 0.001
		dist = 1.0 / d
		if a == 'therealadam':
			a = '1139110'
		if b == 'therealadam': 
			b = '1139110'
		output.write('%s %s %s \n' % (str(a), str(b), str(dist)))	

def get_location_map():
	locations = get_users_locations()
	unique_locations = set([loc for node, loc in locations.items()])
	cursor_locations = get_database('gowalla', 'locations')

	count = 0
	loc_map = {}
	for lat, lng in unique_locations:
		query = {'$and': [{'lat': lat}, {'lng': lng}, {'processed': 1}]}
		res = cursor_locations.find(query)	
		if res.count() == 0: continue
		if res[0]['Country'].find('|') == -1: continue		
		country = res[0]['Country'].split('|')[1]
		if country != 'US': continue
		state = res[0]['State'].split('|')[1]
		if len(state) > 2 or state == 'DC': continue
	        loc_map[(lat,lng)] = state
		count = count + 1
		if count % 100 == 0: print count, len(unique_locations) - count
	return loc_map

def get_us_states(filename='data/gowalla_us_states.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		locations = get_users_locations()
		loc_map = get_location_map()
		states = set([state for loc, state in loc_map.items()])

		pop_map = dict([(state, set()) for state in states])
		for node, loc in locations.items():
			if loc not in loc_map: continue
			state = loc_map[loc]
			pop_map[state].add(node)

		cPickle.dump(pop_map, open(filename, 'wb'))
		return pop_map

def gowalla_dump():
	network = get_spatial_friendship_network()
	locations = get_users_locations()
	G = convert_network(network)

	network_file  = open('gowalla_network_private.txt', 'w')
	for u, t in G.edges_iter():
		network_file.write('%s %s\n' % (u, t))

	location_file = open('gowalla_locations_private.txt', 'w')	
	for u, cord in locations.items():
		lat, lng = cord
		if u in G: location_file.write('%s %lf %lf\n' % (u, lat, lng))

def transitivity():
	network = get_spatial_friendship_network()
	G = convert_network(network)
	print "Gowalla Transitivity %lf" % nx.transitivity(G)


def l_clustering_coef():
	network = get_spatial_friendship_network()

	nodes = network.keys()
	for i in xrange(5): shuffle(nodes)

	values = []
	for node in nodes[0:10000]:
		count = 0
		friends = network[node]
		
		for s, t in combinations(friends, 2):	
			if s in network[t] and t in network[s]:
				count += 1
		
		k = len(friends)
		if k == 1: continue
		val = count / (0.5 * k * (k - 1))
		values.append(val)

		print node, val

	print "Avg. local clustering coef is %lf" % average(values)		
	

