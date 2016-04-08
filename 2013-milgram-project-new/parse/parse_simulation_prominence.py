import sys
import numpy

from math import log
from numpy import arange,array,ones#,random,linalg
from pylab import plot,show
from scipy import stats

def get_results(filename):
	results = []
	for line in open(filename, 'r'):
		points = line.strip().split(' ')
		x0 = int(points[0]) 		# Successful or Unsuccesful routes
		x1 = int(points[1])  		# Shortest path between nodes
		x2 = float(points[2]) 		# Geo. distance between them
		x3 = float(points[3]) 		# shortest path between communities
		x4 = int(points[4])			# Number of unique communities
		x5 = int(points[5])			# Number of times it changed communities
		x6 = float(points[6])		# PageRank score
		x7 = points[7]				# US State
		x8 = float(points[8])		# prominence score of the starter's community
		x9 = log(float(points[9]))	# prominence score of the target's community
		results.append((x0,x9,x9))

	results = sorted(results, key=lambda x: x[1])

	num_points = 150
	min_val = min([val[1] for val in results])
	max_val = max([val[1] for val in results])
	ran_val = (max_val - min_val) / num_points

	for i in xrange(0, num_points):
		x_start = min_val + ran_val * i
		x_end = min_val + ran_val * (i + 1)

		values = []
		for hop, x6, x9 in results: 
			if x6 >= x_start and x6 < x_end: values.append(hop)
			if x6 > x_end: break

		successes = [value for value in values if value != -1]

		if len(values) == 0: continue
		if len(successes) == 0: continue 

		print 0.5*(x_start + x_end), numpy.average(successes), len(successes)
		
network_code = 1 	# 0 Gowalla 1 Foursquare
selection_code = 7  # 0 (in), 1 (out), 2 (rand), 3 (dist), 4 (com-hop), 5 (fixed), 6 (all)
community_code = 2	# 0 IA 1 GanxisD 2 GanxisO
com_hop = -1		# 0-4 (-1 if N/A)

routing_code = 4
parameters = '%d_%d_%d_%d_1.0_%d_0.080000.txt' % (network_code, selection_code, routing_code, community_code, com_hop)
filename = 'simulation_results/sr_' + parameters
get_results(filename)
