######################################################################
# The purpose of this script is to calculate the statistics of the 
# communities detected by a modified verison of the Clique-Percolation
# Method. 
# -------------------------------------------------------------------
# Author: Tommy Nguyen
# Date: May 31, 2013
######################################################################

import sys
import multiprocessing
import community_statistics

from random import shuffle

def get_communities(filename): return [line.strip().split(' ') for line in open(filename, 'r')]

num_cores = multiprocessing.cpu_count()
filename = 'friendship_communities_results/CPM/communities_results.txt'
output = open(filename.replace('_results.txt', '_statistics.txt'), 'w')
communities = get_communities(filename)

for community in communities:
	# Divide the processing among processors
	indexes = range(len(community))
	for i in range(5): shuffle(indexes)
	work = community_statistics.split_work(indexes, num_cores)
	parameters = [(community, item) for item in work]

	# Map the calculations in parallel. 
	pool = multiprocessing.Pool(num_cores)
	sub_results = pool.map(community_statistics.calc_measurements, parameters)
	pool.close()

	# Combine the calculations
	iec = sum([x[0] for x in sub_results])
	bec = sum([x[1] for x in sub_results])
	sdi = sum([x[2] for x in sub_results])
	asd = sum([x[3] for x in sub_results])
	pss = sum([x[4] for x in sub_results])
	loi = sum([x[5] for x in sub_results])
	iec_space = sum([x[6] for x in sub_results])
	bec_space = sum([x[7] for x in sub_results])

	# Dump the results
	output.write('%d %d %0.4lf %0.4lf %0.4lf %d %lf %d %d \n' % (iec, bec, sdi, asd, pss, len(community), loi, iec_space, bec_space))
	output.flush()
