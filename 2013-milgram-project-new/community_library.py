#####################################################
# The purpose of this script is to load the results
# of different community detection algorithms. The 
# following are algorithms used to discover 
# communities in Gowalla and Foursquare networks:
# 1) Inference Algorithm Unweighted
# 2) Inference Algorithm Weighted
# 3) Ganxis Unweighted 
# 4) Ganxis Unweighted with TTL
# 5) Clique Percolation Method 
# 6) Modularity Density
# -------------------------------------------------
####################################################

import multiprocessing
import networkx
import cPickle

gowalla_path = '../2013-communities-detection/gowalla'
foursquare_path = '../2013-communities-detection/foursquare'

# General helper functions
def convert_com_table(communities):
	com_table = {}
	for i in xrange(len(communities)):
		for node in communities[i]:
			if node not in com_table: 
				com_table[node] = set()
			com_table[node].add(i)
	return com_table
	
# Functions for reading the format of communities
def IA_communities(filename):
	communities = []
	temp = set()
	for line in open(filename, 'r'):
		if 'GROUP' in line:
			if len(temp) > 0: communities.append(temp)
			temp = set()
			continue
		if len(line.strip()) > 0: 
			temp.add(line.strip())
	if len(temp) > 0: communities.append(temp)
	return communities
	
def get_communities(filename): 
	communities = [set(line.strip().split(' ')) for line in open(filename, 'r') if len(line.strip()) > 0]
	return communities

# Loading detected communities for Gowalla
def ganxis_gw_communities_overlapping_ttl():
	filename = '%s/SLPA_ORGINAL/SLPAw_gowalla_spatial_network_run1_r0.2_v4_TTL100_T100.icpm' % gowalla_path
	return get_communities(filename)

# Loading detected cgraphs for Gowalla
def ganxis_gw_cgraph_overlapping_ttl():
	filename = '%s/SLPA_ORGINAL/SLPAw_gowalla_spatial_network_run1_r0.2_v4_TTL100_T100_cgraph.pck' % gowalla_path
	return cPickle.load(open(filename, 'rb'))

# Load detected communities from FourSquare
def ganxis_fs_communities_overlapping_unweighted_ttl():
	filename = '%s/SLPA_TTL_UNWEIGHTED/SLPAw_foursquare_network_run1_r0.2_v4_TTL100_T100.icpm' % foursquare_path
	return get_communities(filename)

# Loading detected cgraphs for Foursquare
def ganxis_fs_cgraph_communities_overlapping_unweighted_ttl():
	filename = '%s/SLPA_TTL_UNWEIGHTED/SLPAw_foursquare_network_run1_r0.2_v4_TTL100_T100_cgraph.pck' % foursquare_path
	return cPickle.load(open(filename, 'rb'))
