import sys
import gowalla
import foursquare
import community_library

#pagerank = gowalla.get_pagerank()
#network = gowalla.get_spatial_friendship_network()
#communities = community_library.ganxis_gw_communities_overlapping_ttl()

pagerank = foursquare.get_pagerank()
network = foursquare.get_spatial_friendship_network()
communities = community_library.ganxis_fs_communities_overlapping_unweighted_ttl()

ctable = community_library.convert_com_table(communities)

sum_bj  = {i : 0 for i in xrange(1, 11)}
sum_boj = {i : 0 for i in xrange(1, 11)}

for i in xrange(len(communities)):
	Ci = communities[i]
	com_i = set([i])
	nodes = sorted(Ci, key=lambda x:float(pagerank[x]), reverse=True)

	if len(Ci) < 15: continue

	used = {}
	prominent = nodes[0]
	for friend in network[prominent]:
		if com_i != set(ctable[friend]):
			used[friend] = 0

	b_counts  = { j: 0 for j in xrange(0, 11)}
	bo_counts = { j: 0 for j in xrange(0, 11)}
	b_counts[0] = len(used.keys())

	for j in xrange(1, 11):
		node = nodes[j]
		bj, boj = 0, 0
		for friend in network[node]:
			if friend in used: 
				bo_counts[j] += 1
				if used[friend] != -1: 
					k = used[friend]
					b_counts[k] -= 1
					bo_counts[k] += 1		
					used[friend] = -1 		
			else:
				b_counts[j] += 1
				used[friend] = j

	for j in xrange(1, 11):
		sum_bj[j]  += b_counts[j]
		sum_boj[j] += bo_counts[j]

for j in xrange(1, 11):
	print j, float(sum_bj[j]) / (sum_bj[j] + sum_boj[j])
	
