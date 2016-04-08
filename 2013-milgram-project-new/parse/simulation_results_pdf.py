import sys
import numpy

def get_results(filename):
	results = []
	for line in open(filename, 'r'):
		points = line.strip().split(' ')
		x0 = int(points[0]) 	# Successful or Unsuccesful routes
		x1 = int(points[1])  	# Shortest path between nodes
		x2 = float(points[2]) 	# Geo. distance between them
		x3 = float(points[3]) 	# shortest path between communities
		x4 = int(points[4])		# Number of unique communities
		x5 = int(points[5])		# Number of times it changed communities
		results.append(x0)

	success = filter(lambda x: x > -1, results)
	for i in xrange(1, max(success)):
		rate = success.count(i) / float(len(success))
		if i > 20 and rate < 0.01: break
		print i, success.count(i), success.count(i) / float(len(success))



network_code = 1   		# 0 Gowalla 1 Foursquare
selection_code = 4  	# 0 (in), 1 (out), 2 (rand), 3 (dist), 4 (com-hop), 5 (fixed)
community_code = 2		# 0 IA 1 GanxisD 2 GanxisO
com_hop = 3				# 0-4 (-1 if N/A)

for routing_code in range(3,4):
	parameters = '%d_%d_%d_%d_1.0_%d_-1.000000.txt' % (network_code, selection_code, routing_code, community_code, com_hop)
	filename = 'simulation_results/sr_' + parameters
	get_results(filename)
