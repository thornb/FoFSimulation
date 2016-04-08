import numpy

filename = 'SLPAw_gowalla_weighted_max_run1_r0.5_v3_statistics.txt'

results = {}
for line in open(filename, 'r'):
	iec, bec, sdi, asd, pss, size, loi, iec_space, bec_space = line.strip().split(' ')

	size = int(size)
	if size not in results:
		results[size] = []
	results[size].append((float(iec), float(bec), float(sdi), float(asd)))

output = open(filename.replace('_statistics.txt', '_summary.txt'), 'w')
for size in results.keys():
	elements = results[size]
	avg_iec = str(numpy.mean([e[0] for e in elements]))
	avg_bec = str(numpy.mean([e[1] for e in elements]))
	avg_sdi = str(numpy.mean([e[2] for e in elements]))
	avg_asd = str(numpy.mean([e[3] for e in elements]))
	output.write(avg_iec + '\t' + avg_bec + '\t' + avg_sdi + '\t' + avg_asd + '\t' + str(size) + '\n') 
