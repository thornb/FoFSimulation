import sys

def save_results(values, filename):
	fileh = open(filename, 'w')
	for val in values:
		fileh.write('%lf %lf\n' % (val[1], val[2]))
	fileh.close()

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
		x6 = float(points[6])	# PageRank score
		x7 = points[7]			# US State
		x8 = float(points[8])	# prominence score of the starter's community
		x9 = float(points[9])	# prominence score of the target's community
		results.append((x0, x6, x9))

	successes = filter(lambda x: x[0] > -1, results)[0:500]
	failures = filter(lambda x: x[0] == -1, results)[0:500]

	save_results(successes, 'ganxis_geogreedy_successes.txt')
	save_results(failures, 'ganxis_geogreedy_failures.txt')



network_code = 1 		# 0 Gowalla 1 Foursquare
selection_code = 2  	# 0 (in), 1 (out), 2 (rand), 3 (dist), 4 (com-hop), 5 (fixed)
community_code = 2		# 0 IA 1 GanxisD 2 GanxisO
com_hop = -1			# 0-4 (-1 if N/A)

for routing_code in range(1, 4):
	routing_code = 4
	parameters = '%d_%d_%d_%d_1.0_%d_0.080000.txt' % (network_code, selection_code, routing_code, community_code, com_hop)
	filename = 'simulation_results/sr_' + parameters
	get_results(filename)
	sys.exit(1)

