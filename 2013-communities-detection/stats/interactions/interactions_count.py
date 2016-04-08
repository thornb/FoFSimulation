community_filename = 'SLPAw_gowalla_weighted_max_run1_r0.5_v3_statistics.txt'
cover_filename = 'geofriend_nearest.txt'

covers = {}
for line in open(cover_filename, 'r'):
	elements = line.strip().split('\t')
	size = int(elements[0])
	value = elements[15]
	covers[size] = float(value)
	
count = 0
total = 0
for line in open(community_filename, 'r'):
	elements = line.strip().split(' ')
	size = int(elements[5])
	if size > 100 or size < 5: continue
	interactions = float(elements[6])

	if covers[size] < interactions:
		count = count + 1
	total = total + 1

print count, total

