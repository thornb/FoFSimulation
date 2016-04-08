import sys
import math

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

	results = [(s, float(success.count(s))) for s in range(1, max(success) + 1)] 
	return dict(results)

def calc_pi(ei_values):
	pi_values = {}
	for i, ei in ei_values.items():
		val = N - sum([ei_values[j] for j in xrange(1, i-1)])
		pi_values[i] = ei/val
	return pi_values

def calc_ci(pi_values, ei_values):
	ci_values = {1:N}
	for i in range(2, len(pi_values.keys())):
		val1 = math.pow(1-drop, i-1)
		val2 = N - sum([ei_values[j] for j in xrange(1, i-1)])
		ci_values[i] =val1*val2
	return ci_values
	
def calc_di(ci_values, pi_values):
	di_values = {}
	for i in ci_values.keys():
		di = pi_values[i] * ci_values[i]
		di_values[i] = di
	return di_values

def calc_average(di_values):
	weight = sum([i * di_values[i] for i in di_values.keys()])
	return float(weight) / sum([val for i, val in di_values.items()])
	
network_code = 0 	# 0 Gowalla 1 Foursquare
selection_code = 4  # 0 (in), 1 (out), 2 (rand), 3 (dist), 4 (com-hop), 5 (fixed)
community_code = 0	# 0 IA 1 GanxisD 2 GanxisO
routing_code = 2	# 1 (Geogreedy) 1 (Comgreedy) 2 (Geocom)
com_hop = 2			# 0-4 (-1 if N/A)

parameters = '%d_%d_%d_%d_1.0_%d_-1.000000.txt' % (network_code, selection_code, routing_code, community_code, com_hop)
filename = 'simulation_results/sr_' + parameters
ei_values = get_results(filename)

N = 10000
drop = 0.00
while drop <= 1:
	pi_values = calc_pi(ei_values)
	ci_values = calc_ci(pi_values, ei_values)
	di_values = calc_di(ci_values, pi_values)
	calc_avg  = calc_average(di_values)
	drop = drop + 0.01
	print drop, calc_avg


