#New simulation of a Friend of Friend network using Gowalla Data
#Coded by Brandon Thorne and Miao Qi

import pprint, pickle
from math import radians, cos, sin, asin, sqrt, floor
import sys
import random

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
    friends_list = list(edge_network[cur_node])

    #check to see if we are directly connected to goal
    if goal in friends_list:
        return goal

    minium = sys.maxint

    #loop through each friend and get thier firends
    closest_f = ""
    closest_fof = "NONE"

    #print "curr:", cur_node, "last:", last_node

    for f in friends_list:

        if f == last_node:
            continue

        #find distance of friend to goal, to check if a friend happens to be closer than a fof
        friend_lat = user_coords[f][0]
        friend_lon = user_coords[f][1]

        goal_lat = user_coords[goal][0]
        goal_lon = user_coords[goal][1]

        friend_dist = haversine(friend_lat, friend_lon, goal_lat, goal_lon)

        if friend_dist < minium:
            closest_f = f
            closest_fof = "NONE"
            minium = friend_dist


        #find the distance to goal for each of these friends

        fof_list = list(edge_network[f])

        for fof in fof_list:
            
            r = random.random()

            #print "random number: ", r
            if r <= knowledge: 

                #print "We know this fof: ", fof

                lat = user_coords[fof][0]
                lon = user_coords[fof][1]

                goal_lat = user_coords[goal][0]
                goal_lon = user_coords[goal][1]

                dist = haversine(lat, lon, goal_lat, goal_lon)
                if dist < minium:
                    closest_f = f
                    closest_fof = fof
                    minium = dist

            else:
                continue

    if closest_f == "":
        print "No route found without backtracking. Ending simulation."
        sys.exit()

    if closest_fof == "NONE":
        #print "closest friend " + closest_f + " is closer than any fof"
        return closest_f

    #print "closest friend: ", closest_f, " closest fof: ", closest_fof

    if closest_fof in friends_list:
        return closest_fof

    return closest_f

#Keeps finding the best FoF to send to until we hit goal state
def find_goal(edge_network, user_coords, cur_node, goal, knowledge, type_sim, max_hops):

    hops = 0 

    #last_node = cur_node

    #list to keep track of visited nodes
    visited_list = []

    while cur_node != goal and hops <= max_hops:

        #find the next node to travel to 
     
        if len(visited_list) < 2:
            last_node = cur_node
        else:
            last_node = visited_list[-2]   

        if type_sim == "distance":
            cur_node = find_next_node(edge_network, user_coords, cur_node, last_node, goal, knowledge)

        elif type_sim == "random":
            cur_node = find_next_node_random(edge_network, user_coords, cur_node, last_node, goal)

        visited_list.append(cur_node)

        #last_node = cur_node

        print "The next node is: " , cur_node

        #print "hops: ", hops

        hops += 1

    
    if hops > max_hops:
            print "The simulation did not find the goal in", max_hops, "hops. Ending Simulation"
            sys.exit()

    return hops

#Function to look at a node's friends, and their friends and returns which node we should travel to next
def find_next_node_random(edge_network, user_coords, cur_node, last_node, goal):

    #get current node's friends
    friends_list = edge_network[cur_node]

    #check to see if we are directly connected to goal
    if goal in friends_list:
        return goal

    
    all_fof = []

    for f in friends_list:

        if f == last_node:
            continue

        #find the distance to goal for each of these friends

        fof_list = list(edge_network[f])

        for fof in fof_list:
            all_fof.append((f, fof))

    rand_fof = random.choice(all_fof)
    closest_f = rand_fof[0]
    closest_fof = rand_fof[1]

    #print "closest friend: ", closest_f, " closest fof: ", closest_fof

    return closest_f

##### START OF MAIN ######

try:
    type_sim = str(sys.argv[1])

    if type_sim == "random":
        start_node = str(sys.argv[2])
        end_node = str(sys.argv[3])
        max_hops = str(sys.argv[4])
        knowledge = 0

    elif type_sim == "distance":
        start_node = str(sys.argv[2])
        end_node = str(sys.argv[3])
        max_hops = int(sys.argv[4])
        knowledge = float(sys.argv[5])

except:
    print "Incorect arguments. Please call program with <type of simulation> <start node> <end node> <max hops> <knowledge>"
    print "type of simulation: distance or random"
    print "start node: number node to start route from. 0 is random"
    print "end node: number node as goal to reach. 0 is random"
    print "max hops: max number of hops before ending simulation"
    sys.exit()



#load the gowalla network and locations
edge_network = load_network()

user_coords = load_loactions()

#Example network of nodes used for testing
# edge_network = {'01':['02','03'],'02':['01','03','07'],'03':['02','01','04','05'],
# '04':['05','03'],'05':['04','03', '06'],'06':['05','08'],'07':['02','12'],
# '08':['06','09','10'],'09':['08','16'],'10':['08','11','12'], '11':['10','13'],'12':['10','07'],'13':['11','14'],
# '14':['13','15','17'],'15':['14','16'],'16':['09','15'],'17':['14','18','19'],
# '18':['17','20'],'19':['17'],'20':['18']}

# user_coords = {'01':(-2,5), '02':(-1.5,5.7),'03':(-0.4,4.5),'04':(-1.9,3.4),'05':(-1.85,3.12),'06':(2.1,4.45),'07':(-0.3,7),'08':(-1.7,1.2),'09':(-2,-0.8),'10':(0,1.9),
# '11':(1,0.8), '12':(2,1.8),'13':(1.2,-1.1),'14':(0,-2.4),'15':(-1.1,-2.6),'16':(-1.7,-1.7),'17':(1.5,-3.4),'18':(1.9,-4.7),'19':(2.6,-3),'20':(0.2,-4.9)}

if start_node == "0":
    start_node = random.choice(edge_network.keys())

if end_node == "0":
    end_node = random.choice(edge_network.keys())

    while end_node == start_node:
        end_node = random.choice(edge_network.keys())




print "Start node is : ", start_node
print "End node is : ", end_node

hops = find_goal(edge_network, user_coords, start_node, end_node, knowledge, type_sim, max_hops)

print "The simulation found the goal in ", hops, " hops."




