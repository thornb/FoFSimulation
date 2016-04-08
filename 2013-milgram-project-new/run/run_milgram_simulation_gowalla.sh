#!/bin/bash

# The purpose of this script is to simulate all possible
# configurations of the Milgram's experiments using ONLY
# the Gowalla network. 

NetworkCode=0
# Simulating pairs based on multiple selection strategies
for CommunityCode in 0 2
do 
	for SelectionCode in 1 3
	do
        	for RoutingCode in 1 2 3
        	do
			python routing_simulation_v2.py $NetworkCode $SelectionCode $RoutingCode $CommunityCode 1 -1 -1
        	done
	done
done

# Simulating pairs that are seperated by fix distances
for CommunityCode in 0 2
do 
	for RoutingCode in 1 2 3
	do
		for CommunityHop in 0 1 2 3
		do
			python routing_simulation_v2.py $NetworkCode 4 $RoutingCode $CommunityCode 1 $CommunityHop -1
		done
	done
done

