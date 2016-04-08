import gowalla

from networkx import nx

network = gowalla.get_spatial_friendship_network()
locations = gowalla.get_users_locations()

edges = set()

for user, friends in network.items():
	l_user = locations[user]
	for friend in friends:
		l_friend = locations[friend]
		dist = gowalla.calc_spatial_dist(l_user, l_friend)
		if dist < 160:
			if (user, friend) not in edges and (friend, user) not in edges:
				edges.add((user, friend))

G = nx.Graph()

for a, b in edges:
	G.add_edge(a, b)

print nx.number_connected_components(G)
