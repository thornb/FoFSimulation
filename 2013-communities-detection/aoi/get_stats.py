
def get_cff(filename = 'geofriend_nearest.txt'):
	results = {}
	for line in open(filename, 'r'):
		row = line.strip().split('\t')
		size = int(row[0])
		loi = row[15]
		results[size] = float(loi)
	return results

def get_data(filename):
	results = []
	for line in open(filename, 'r'):
		row = line.strip().split(' ')
		size = int(row[5])
		loi = float(row[6])
		if size <= 100 and size >= 5:
			results.append((size, loi))
	return results

cff = get_cff()
filename = 'SLPA_weighted.txt'
data = get_data(filename)

count = sum([1 for item in data if item[1] > cff[item[0]]])
total = len(data)

print count, total, float(count) / total
