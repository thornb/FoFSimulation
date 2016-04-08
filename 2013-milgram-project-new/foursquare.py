###############################################
# The purpose of this script is to interact
# with the MongoDB database. This script
# currently supports launching data from
# MongoDB directly to the code and loading 
# the data from the disk to the code. 
# --------------------------------------------
# Author: Tommy Nguyen
# Last Modified: July 22, 2013
##############################################

import os.path
import cPickle
import gowalla
import math
import sys

from math import *
from networkx import nx
from pymongo import Connection
from gowalla import convert_network
from itertools import combinations
from numpy import average
from random import shuffle

def get_connection(): return Connection('sd-01.cs.rpi.edu', 27017)
def get_database(db, collection): return get_connection()[db][collection]

# Get a particular instance of the evolving network
def get_snapshot(timestamp):
	network  = {}
	filename = '/home/nguyet11/Dropbox/Virtual/crawlers/foursquare/snapshots/foursquare_network_%d.txt' % timestamp
	for line in open(filename, 'r'):
		s, t = line.strip().split(' ')
		if s not in network: network[s] = set()
		if t not in network: network[t] = set()
		network[s].add(t)
		network[t].add(s)
	return network

def get_pagerank(filename = 'data/fs_pagerank.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		network = get_spatial_friendship_network()
		pagerank = nx.pagerank(convert_network(network))
		cPickle.dump(pagerank, open(filename, 'wb'))
	return pagerank	

# Get Spatially-Aware Friendship Network
def get_spatial_friendship_network(filename = 'data/fs_spatial_friendship_network.pck'):
	if os.path.isfile(filename):
		network = cPickle.load(open(filename, 'rb'))
		for user, friends in network.items():
			for friend in friends:
				if user not in network[friend]:
					network[friend].add(user)
	else:
		network = get_snapshot(1377304430)		
		cPickle.dump(network, open(filename, 'wb'))
	return network
	
# Get Location of Users from DB or Disk
def get_users_locations(filename = 'data/fs_users_locations.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		locations = get_users_locations_from_db()
		cPickle.dump(locations, open(filename, 'wb'))
	return locations

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

def get_spatial_network_friends_from_db():
	cursor = get_database("foursquare", "network")

	network = {}
	for item in cursor.find({}):
		user_id = item['user_id']
		lat = float(item['lat'])
		lng = float(item['lng'])
		if lat != -1 and lng != -1:
			network[user_id] = set(item['friends'])

	for user, friends in network.items():
		selected_friends = [f for f in friends if f in network and f != user]
		network[user] = set(selected_friends)

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

def get_users_locations_from_db():
	locations = {}
	location_cursor = get_database("foursquare", "locations")
	
	# Step 1: Get all processed locations
	for record in location_cursor.find({'processed': 1}):
		lat = record['lat']
		lng = record['lng']
		if lat != -1 and lng != -1:
			loc = record['location'].strip().lower()
			locations[loc] = (lat, lng)	
		
	users = {}
	network_cursor = get_database("foursquare", "network")

	# Step 2: Get all users and their homeCities	
	squery = {'friends_processed': 1}
	rquery = {'user_id' : 1, 'homeCity': 1}
	for record in network_cursor.find(squery, rquery):
		homeCity = record['homeCity'].strip().lower()
		if homeCity in locations:
			user_id = record['user_id']
			users[user_id] = locations[homeCity]

	return users

def get_state_country(address_components):
	state = country = ''
	for record in address_components:
		if 'administrative_area_level_1' in record['types']:
			state = record['short_name']
		if 'country' in record['types']:
			country = record['short_name']
	return state, country

def get_location_map():
	locations = get_users_locations()
	network = get_spatial_friendship_network()
	unique_locations = set([loc for node, loc in locations.items() if node in network])
	cursor_locations = get_database('foursquare', 'locations')

	print "Number of unique locations %d" % len(unique_locations)

	count = 0
	loc_map = {}
	for lat, lng in unique_locations:
		query = {'$and': [{'lat': lat}, {'lng': lng}, {'processed': 1}]}
		res = cursor_locations.find(query)	
		if res.count() == 0: continue
		response = res[0]['response']
		location = res[0]['location']
		if type(response) == type([]):
			response = response[0]
		ac = response['address_components']
		state, country = get_state_country(ac)
		count = count + 1
		if country != 'US': continue
		if len(state) != 2 or state == 'DC': continue
		loc_map[(lat,lng)] = state

	return loc_map

def get_us_states(filename='data/foursquare_us_states.pck'):
	if os.path.isfile(filename):
		return cPickle.load(open(filename, 'rb'))
	else:
		network = get_spatial_friendship_network()
		locations = get_users_locations()
		loc_map = get_location_map()
		states = set([state for loc, state in loc_map.items()])

		pop_map = dict([(state, set()) for state in states])
		for node, loc in locations.items():
			if node not in network: continue
			if loc not in loc_map: continue
			state = loc_map[loc]
			pop_map[state].add(node)

		cPickle.dump(pop_map, open(filename, 'wb'))
		return pop_map

def dump_network():
	network = get_spatial_friendship_network()
	locations = get_users_locations()
	G = convert_network(network)

	network_file  = open('foursquare_network_private.txt', 'w')
	for u, t in G.edges_iter():
		network_file.write('%s %s\n' % (u, t))

	location_file = open('foursquare_locations_private.txt', 'w')	
	for u, cord in locations.items():
		lat, lng = cord
		if u in G: location_file.write('%s %lf %lf\n' % (u, lat, lng))

def network_size():
	network = get_spatial_friendship_network()
	G = convert_network(network)
	print "Number of nodes: %d" % len(G.nodes())
	print "Number of edges: %d" % len(G.edges())

def get_network_from_file(filename):
	network = {}
	for line in open(filename):
		a, b = line.strip().split(' ')
		if a not in network: network[a] = set()
		if b not in network: network[b] = set()
		network[a].add(b)
		network[b].add(a)
	return network
	
def text_to_pck(input_filename, output_filename):
	network = get_network_from_file(input_filename)
	cPickle.dump(network, open(output_filename, 'wb'))
	
def calc_pagerank(network, output_file):
	G = convert_network(network)
	pr = nx.pagerank(G, alpha=0.9)
	cPickle.dump(network, open(output_file, 'wb'))

def transitivity():
	network = get_spatial_friendship_network()
	G = convert_network(network)
	print "Foursquare Transitivity %lf" % nx.transitivity(G)

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

