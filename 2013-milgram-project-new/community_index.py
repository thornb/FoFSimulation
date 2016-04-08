import os
import cPickle
import multiprocessing
import routing_simulation_loader

from networkx import shortest_path

num_procs = multiprocessing.cpu_count()	

def split_work(seq, size):
	results = [[] for i in xrange(size)]
	for i in xrange(len(seq)): results[i % size].append(seq[i])
	return results

def calc_chops(item):
	indexes, cgraph = item
	results = []
	for ci in indexes:
		paths = shortest_path(cgraph, ci)
		for cj, path in paths.items():
			hop = len(path) - 1
			if hop < 4: results.append((ci, cj, hop))
	return results

def get_community_index(network_code, community_code):
	filename = 'data/com_index_%d_%d.pck' % (network_code, community_code)
	if os.path.isfile(filename): return cPickle.load(open(filename, 'rb'))

	community, com_table, cgraph = routing_simulation_loader.load_community(network_code, community_code)
	
	work_input = split_work(range(len(community)), num_procs)
	pool = multiprocessing.Pool(num_procs)
	results = pool.map(calc_chops, [(indexes, cgraph) for indexes in work_input])
	pool.close()

	com_index = {}
	for sub_results in results:
		for ci, cj, hop in sub_results:
			if hop not in com_index: com_index[hop] = []
			com_index[hop].append((ci, cj))

	cPickle.dump(com_index, open(filename, 'wb'))
	return com_index

