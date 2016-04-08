import gowalla
import multiprocessing

# Split a list evenly by a given size. Used for multiprocessing.  
def split_work(seq, size):
	newseq = []
	splitsize = 1.0/size*len(seq)
	for i in xrange(size): newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
	return newseq

def process_users(users):
	results = {}
	count = 0
	for user in users:
		results[user] = {}
		for friend in network[user]:
			if friend in results[user]: continue
			loi = gowalla.calc_physical_interaction(checkins[user], checkins[friend])
			results[user][friend] = loi
		count = count + 1
		print "Finished processing user %s. Remaining: %d " % (user, len(users) - count)
	return results

checkins = gowalla.get_users_checkins()
print "Finished loading checkins"
network = gowalla.get_spatial_friendship_network()

num_cores = multiprocessing.cpu_count()
pool = multiprocessing.Pool(num_cores)
results = pool.map(process_users, split_work(network.keys(), num_cores))
pool.close()

edges = set()
output = open('friends_loi.txt', 'w')
for sub_results in results:
	for user, table in sub_results.items():
		for friend, loi in table.items():
			if (user, friend) in edges or (friend, user) in edges: continue
			output.write('%s %s %lf \n' % (user, friend, loi))
			edges.add((user, friend))
