import numpy

filename = 'gowalla_weighted_max-fc_test_run.groups'
communities = []
temp = []

for line in open(filename, 'r'):
	if 'GROUP' in line:
		if len(temp) > 0:
			communities.append(len(temp))
		temp = []
	else:
		temp.append(line.strip())

print numpy.average(communities)
print numpy.std(communities)
print min(communities)
print max(communities)
print len(communities)
	
