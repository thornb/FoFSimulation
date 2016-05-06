#New simulation of a Friend of Friend network using Gowalla Data
#Coded by Brandon Thorne and Miao Qi

import pprint, pickle
from math import radians, cos, sin, asin, sqrt, floor
import sys
from random import shuffle, choice

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


#Function to calculate the Havsersine distance between two points
#taken from stack overflow
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

#Function to look at a node's friends, and their friends and returns which node we should travel to next
def find_next_node(edge_network, user_coords, cur_node, last_node, goal, knowledge):

    #get current node's friends
    friends_list = edge_network[cur_node]


    #check to see if we are directly connected to goal
    if goal in friends_list:
        return goal

    minium = sys.maxint

    #loop through each friend and get thier firends
    closest_f = ""

    for f in friends_list:

        if f == last_node:
            continue

        #find the distance to goal for each of these friends

        fof_list = list(edge_network[f])

        shuffle(fof_list)

        number_known = len(fof_list) * knowledge


        for i in range(0, int(floor(number_known))):
            

            #@TODO I don't think this works if the first node is only connected to one node
            if len(fof_list) == 1:
                continue

            fof = fof_list[i]

            lat = user_coords[fof][0]
            lon = user_coords[fof][1]

            goal_lat = user_coords[goal][0]
            goal_lon = user_coords[goal][1]

            dist = haversine(lat, lon, goal_lat, goal_lon)
            if dist < minium:
                closest_f = f
                closest_fof = fof
                minium = dist


    print "closest friend: ", closest_f, " closest fof: ", closest_fof

    return closest_f

#Keeps finding the best FoF to send to until we hit goal state
def find_goal(edge_network, user_coords, cur_node, goal, knowledge):

    hops = 0 

    while cur_node != goal and hops < 20:

        #find the next node to travel to 
        last_node = cur_node
        cur_node = find_next_node(edge_network, user_coords, cur_node, last_node, goal, knowledge)

        print cur_node

        hops += 1

    return hops



##### START OF MAIN ######
knowledge = float(sys.argv[1])
start_node = str(sys.argv[2])
end_node = str(sys.argv[3])


#load the network and locations
edge_network = load_network()
user_coords = load_loactions()

if start_node == "0":
    start_node = choice(edge_network.keys())

if end_node == "0":
    end_node = choice(edge_network.keys())

    while end_node == start_node:
        end_node = choice(edge_network.keys())




print "Start node is : ", start_node
print "End node is : ", end_node

hops = find_goal(edge_network, user_coords, start_node, end_node, knowledge)

print "The simulation found the goal in ", hops, " hops."


#user_locations = load_loactions()


