import random
import foursquare
import multiprocessing

SAMPLE_SIZE = 10000
from random import shuffle
from bisect import bisect_left
from bisect import bisect_right
from gowalla import calc_spatial_dist

SAMPLE_SIZE = 10000

def get_pool(): return multiprocessing.Pool(multiprocessing.cpu_count())

def split_work(seq):
	size = multiprocessing.cpu_count()
	if type(seq) == type(set()): seq = list(seq)
	results = [[] for i in xrange(size)]
	for i in xrange(len(seq)): results[i % size].append(seq[i])
	return results

def calc_distribution(values, fileh, incr):
	xmin = min(values)
	xmax = max(values)
	total = float(len(values))

	values = sorted(values)
	while xmin < xmax:
		start = bisect_left(values, xmin)
		end   = bisect_right(values, xmin + incr)
		mp 	  = 0.5 * (xmin + xmin + incr)
		val   = (end - start) / total
		if val > 0:
			print mp, val
			fileh.write('%lf %lf\n' % (mp, val))
		xmin = xmin + incr

def bfs_outlinks(item):
	def condiction(node, edges, i):
		for j in xrange(i): 
			if node in edges[j]: return False
		return True

	network, nodes, hop = item
	results = set()

	count = 0
	for a in nodes:
		edges = {0:set()}
		edges[0].add(a)
		for i in xrange(1, hop+1):
			edges[i] = set()
			for node in edges[i-1]:
				for outlink in network[node]:
					if condiction(outlink, edges, i) == True:
						edges[i].add(outlink)
		for u in edges[hop]: 
			if random.randint(1, 100) == 2:
				results.add((a, u))
		count = count + 1
		print "Finished processing %s. Remaining %d." % (a, len(nodes) - count)
	
	return results

def calc_geo_distances(network, locations, fileh, hop):
	work = split_work(network.keys()[0:64000])
	work_input = [(network, w, hop) for w in work]
	
	pool = get_pool()
	results = pool.map(bfs_outlinks, work_input)
	pool.close()
	
	links = results[0]
	for result in results: links.update(result)

	links = list(links)
	for i in xrange(6): shuffle(links)
	links = links[0:SAMPLE_SIZE]

	values = [calc_spatial_dist(locations[s], locations[t]) for s,t in links]
	values = [v for v in values if v < 4000]
	calc_distribution(values, fileh, 160)

def foursquare_geographic_distances():
	network = foursquare.get_spatial_friendship_network()
	locations = foursquare.get_users_locations()

	for hop in xrange(4, 6 + 1):
		print 'Calculating hop %d' % hop
		fileh = open('foursquare_geo_dist_%d.txt' % hop, 'w')
		calc_geo_distances(network, locations, fileh, hop)
		fileh.close()

foursquare_geographic_distances()
