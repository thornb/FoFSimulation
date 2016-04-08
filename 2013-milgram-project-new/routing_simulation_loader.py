import gowalla 
import foursquare
import community_library

from community_library import convert_com_table

def load_network(network_code):
	if network_code == 0: return load_gowalla_network()
	if network_code == 1: return load_foursquare_network()

def load_community(network_code, community_code):
	if network_code == 0: return load_gowalla_community(community_code)
	if network_code == 1: return load_foursquare_community(community_code)

def load_stationary(filename):
	results = []
	for line in open(filename, 'r'):
		c_i, lambda_i = line.strip().split(' ')
		element = (int(c_i), float(lambda_i))
		results.append(element)
	return dict(results)

#######################################################
# Loader functions for Gowalla
#######################################################
def load_gowalla_network():
	network = gowalla.get_spatial_friendship_network()
	locations = gowalla.get_users_locations()
	pagerank = gowalla.get_pagerank()
	states = gowalla.get_us_states()
	return network, locations, pagerank, states

def load_gowalla_community(community_code):
	if community_code == 0:
		community = community_library.IA_gw_communities_unweighted()
		cgraph = community_library.IA_gw_cgraph_unweighted()
	if community_code == 2: 
		community = community_library.ganxis_gw_communities_overlapping_ttl()
		cgraph = community_library.ganxis_gw_cgraph_overlapping_ttl()
		stationary = load_stationary('data/gowalla_ganxis_eigenvector.txt')
	return community, convert_com_table(community), cgraph, stationary

#######################################################
# Loader functions for Foursquare
#######################################################
def load_foursquare_network():
	network = foursquare.get_spatial_friendship_network()
	locations = foursquare.get_users_locations()
	pagerank = foursquare.get_pagerank()
	states = foursquare.get_us_states()
	return network, locations, pagerank, states

def load_foursquare_community(community_code):
	if community_code == 0:
		community = community_library.IA_fs_communities_unweighted()
		cgraph = community_library.IA_fs_cgraph_communities_unweighted()
	if community_code == 2: 
		community = community_library.ganxis_fs_communities_overlapping_unweighted_ttl()
		cgraph = community_library.ganxis_fs_cgraph_communities_overlapping_unweighted_ttl()
		stationary = load_stationary('data/foursquare_ganxis_eigenvector.txt')
	return community, convert_com_table(community), cgraph, stationary
