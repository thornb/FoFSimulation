import community_library

community = community_library.ganxis_fs_communities_overlapping_unweighted_ttl()

N = set([node for com in community for node in com])
val = sum([len(com)*len(com) for com in community])

print float(val) / len(N)




