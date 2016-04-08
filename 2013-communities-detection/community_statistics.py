######################################################################
# The purpose of this script is to calculate the link-connectivity
# pair-similarity measurements of the detected communities. The 
# following are the six calculated measurements: 
# -------------------------------------------------------------------
#	1) intra-edge count
# 	2) boundary-edge count
# 	3) spatial diameter
#	4) avg. spatial distance
#	5) inter-pair similarity
#	6) commmunity size
# --------------------------------------------------------------------
# Author: Tommy Nguyen
# Date: May 30, 2013
######################################################################

import sys
import gowalla

# Split a list evenly by a given size. Used for multiprocessing.  
def split_work(seq, size):
	newseq = []
	splitsize = 1.0/size*len(seq)
	for i in xrange(size): newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
	return newseq

# Look up physical interactions
def get_interactions(filename = 'friends_loi.txt'):
	results = {}
	for line in open(filename, 'r'):
		user_a, user_b, loi = line.strip().split(' ')
		if user_a not in results:
			results[user_a] = {}
		results[user_a][user_b] = float(loi)
	return results

def calc_interaction(node_i, node_j):
	if node_i in interactions and node_j in interactions[node_i]:
		return interactions[node_i][node_j]
	if node_j in interactions and node_i in interactions[node_j]:
		return interactions[node_j][node_i]
	return 0

# Map-Reduce function to calc. the measurements of a community
def calc_measurements(item):
	def calc_distance(node_i, node_j):
		lat1, lng1 = user_locations[node_i]
		lat2, lng2 = user_locations[node_j]
		return gowalla.calc_haversine(lng1, lat1, lng2, lat2)
	def calc_iec(node_i, node_j): 
		return 1 if node_i in network[node_j] and node_j in network[node_i] else 0
	def calc_iec_with_space(node_i, node_j):
		return 1 if calc_iec(node_i, node_j) == 1 and calc_distance(node_i, node_j) < 80 else 0
	def calc_bec(node_i):
		count = 0
		for friend in network[node_i]:
			if friend not in community_set:
				if friend in network and friend in user_locations:
					count = count + 1
		return count
	def calc_bec_with_space(node_i):
		count = 0
		for friend in network[node_i]:
			if friend not in community_set:
				if friend in network and friend in user_locations and calc_distance(node_i, friend) < 80:
					count = count + 1
		return count
	def calc_ps(node_i, node_j):
		inter = len(network[node_i].intersection(network[node_j]))
		union = len(network[node_i].union(network[node_j]))
		return inter / float(union)
	def calc_diameter(node_i, node_j, diameter):
		dist = calc_distance(node_i, node_j)
		return dist if dist > diameter else diameter

	community, indexes = item
	community_set = set(community)
	iec, iec_space, bec, bec_space, sdi, asd, pss, loi = 0,0,0,0,0,0,0, 0

	for i in indexes:
		node_i = community[i]
		bec = bec + calc_bec(node_i)
		bec_space = bec_space + calc_bec_with_space(node_i)
		for j in xrange(i + 1, len(community)):
			node_j = community[j]
			iec = iec + calc_iec(node_i, node_j)
			pss = pss + calc_ps(node_i, node_j)
			asd = asd + calc_distance(node_i, node_j)
			sdi = calc_diameter(node_i, node_j, sdi)
			loi = loi + calc_interaction(node_i, node_j)
			iec_space = iec_space + calc_iec_with_space(node_i, node_j)

	return (iec, bec, sdi, asd, pss, loi, iec_space, bec_space)

# Step 0: Loading data from DB. 
user_locations = gowalla.get_users_locations()
network = gowalla.get_spatial_friendship_network()
interactions = get_interactions()
