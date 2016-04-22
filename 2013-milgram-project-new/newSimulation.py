#New simulation of a Friend of Friend network using Gowalla Data
#Coded by Brandon Thorne and Miao Qi

import pprint, pickle


#Functions to load the .pck data

def load_network():
	pkl_file = open('data/gowalla_spatial_network.pck', 'rb')
	return pickle.load(pkl_file) 

def load_loactions():
	pkl_file = open('data/gowalla_users_locations.pck', 'rb')
	return pickle.load(pkl_file)

def load_location_map():
	pkl_file = open('data/gowalla_users_locationmap.pck', 'rb')
	return pickle.load(pkl_file)	





##### START OF MAIN ######




