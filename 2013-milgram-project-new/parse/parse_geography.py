import numpy

from random import shuffle
from bisect import bisect_left
from bisect import bisect_right

def calc_distribution(values, fileh, incr):
	xmin = min([val[0] for val in values])
	xmax = max([val[0] for val in values])
	total = float(len(values))

	while xmin < xmax:
		start = xmin
		end = xmin + incr
		temp = [v[1] for v in values if v[0] >= start and v[0] < end]
		mp = 0.5 * (start + end)
		if len(temp) > 0: 
			fileh.write('%lf %lf %d\n' % (mp, numpy.average(temp), len(temp)))
		xmin = xmin + incr
		print xmin, xmax
	
values = []
filename = 'gowalla_interactions.txt'

for line in open(filename, 'r'):
	val = line.split(' ')
	dij = float(val[2])
	tij = float(val[3])
	values.append((dij, tij))

fileh = open('interactions_parsed.txt', 'w')
calc_distribution(values, fileh, 160)
	
