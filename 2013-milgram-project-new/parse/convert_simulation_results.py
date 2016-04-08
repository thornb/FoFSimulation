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
	#print numpy.average(success)
	#print float(len(success)) / len(results)

	return success

network_code 	= 0   # 0 Gowalla 1 Foursquare
selection_code 	= 4   # 0 (in), 1 (out), 2 (rand), 3 (dist), 4 (com-hop), 5 (fixed)
community_code 	= 2   # 0 IA 1 GanxisD 2 GanxisO
com_hop 		= 3   # 0-4 (-1 if N/A)
routing_code 	= 3	  # 0 (Rand), 1 (GEO), 2 (COM), 3(GEO+COM)

parameters = '%d_%d_%d_%d_1.0_%d_-1.000000.txt' % (network_code, selection_code, routing_code, community_code, com_hop)
filename = 'simulation_results/sr_' + parameters

hops = [hop for hop in get_results(filename) if hop <= 13]
limit = 13
for i in xrange(0, limit+2):
	count = hops.count(i)
	print i, count, float(count) / len(hops)

print numpy.average(hops)
print numpy.std(hops)
