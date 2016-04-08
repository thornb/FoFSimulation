#!/bin/bash

NetworkCode=1
# Simulating pairs based on multiple selection strategies
for CommunityCode in 0 2
do 
	for SelectionCode in 1 3
	do
        	for RoutingCode in 1 2 3
        	do
			echo "Running simulations with parameters: $NetworkCode $SelectionCode $RoutingCode $CommunityCode 1 -1 -1"
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
			echo "Running simulations with parameters: $NetworkCode 4 $RoutingCode $CommunityCode 1 $CommunityHop"
			python routing_simulation_v2.py $NetworkCode 4 $RoutingCode $CommunityCode 1 $CommunityHop -1
		done
	done
done

