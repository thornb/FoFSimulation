import sys

def load_parameters(argv):
	if len(argv) != 9:
		print "./routing_simulation network_code selection_code routing_code community_code prob_p com_hop alpha HubDistance"
		print "Network_code: 0 (Gowalla) 1 (Fourquare)" 
		print "Selection_code: 0 (Pairs in), 1 (Pairs out), 2 (Random), 3 (Geo. Distant), 4 (Community Hop) 5 (States) 6 (All) 7 (fixed)"
		print "Routing_code: 0 (RAND), 1 (GEO), 2 (COM), 3 (GEOCOM) 4 (2Hop) 5 (Hub) 6 (Hub+Geo) 7 (GEO + COM + INTERACTIONS)"
		print "Community_code: 0 (Inference Alg.), 1 (GANXiS TTL Disjoint), 2 (GANXiS TTL Overlapping)" 
		print "Prob_p: Probability of participation"
		print "Com_hop: number of hops seperating communities for selection. (-1 if N/A)"
		print "Probability of selecting a friend-of-friend in 2hop routing. (0 if N/A)"
		print "Hub distance. (-1 if N/A)"
		sys.exit(1)
	else:
		network_code = int(argv[1])
		selection_code = int(argv[2])
		routing_code = int(argv[3])
		community_code = int(argv[4])
		prob = float(argv[5])
		community_hop = int(argv[6])
		two_hop_prob = float(argv[7]) / 100
		hub_distance = float(argv[8])

		if network_code > 1 or network_code < 0:
			print "Network_code out of bound."
			sys.exit(1)
		if selection_code > 7 or selection_code < 0: 
			print "Selection_code out of bound"
			sys.exit(1)
		if routing_code > 7 or routing_code < 0:
			print "Routing_code out of bound"
			sys.exit(1)
		if community_code > 2 or community_code < 0:
			print "Community_code out of bound"
			sys.exit(1)
		if prob > 1 or prob < 0:
			print "Pro_p is out of bound"
			sys.exit(1)
		if community_hop == -1 and selection_code == 4:
			print "Inconsistent selection_code %d and community_hop %d" % (selection_code, community_hop)
			sys.exit(1)
		if selection_code != 4 and community_hop > 0:
			print "Inconsistent selection_code %d and community_hop %d" % (selection_code, community_hop)
			sys.exit(1)
		if (two_hop_prob < 0.0 or two_hop_prob > 1.0) and two_hop_prob != -1: 
			print "two_hop_prob %lf is out of bound. two_hop_prob = [0, 1]" % two_hop_prob
			sys.exit(1)
		if routing_code == 6 and hub_distance < 0:
			print "Hub distance is out of bound %" % routing_code
			sys.exit(1)

		return (network_code, selection_code, routing_code, community_code, prob, community_hop, two_hop_prob, hub_distance)

