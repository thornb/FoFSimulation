filename = 'cpm_summary.txt'
def get_data(lower_bound, upper_bound):
	data = []
	for line in open(filename, 'r'):
		avg_iec, avg_bec, avg_asd, avg_sdi, size = line.strip().split('\t')
		size = int(size)
		##### CHANGE HERE
		val = float(avg_bec) / (2*float(avg_iec) + float(avg_bec))
		if size >= lower_bound and size < upper_bound:		
			data.append((size, val))
	return data

def get_cover():
	fff = {}
	for line in open('geofriend_nearest_avg.txt', 'r'):
		elements = line.strip().split('\t')
		size = int(elements[0])
		avg_iec = float(elements[1])
		avg_bec = float(elements[3])
		sdi = float(elements[7])
		###### CHANGE HERE
		fff[size] = avg_bec / (2*avg_iec + avg_bec)
	return fff

def get_percentage_diff(lower_bound, upper_bound):
	data = get_data(lower_bound, upper_bound)
	fff = get_cover()

	total = 0 
	for size, avg_iec in data:
		avg = (avg_iec + fff[size]) * 0.5
		diff = (fff[size] - avg_iec)
		total += (diff / avg)
	
	return total / len(data)

print get_percentage_diff(5, 25)
print get_percentage_diff(25, 50)
print get_percentage_diff(50, 75)
print get_percentage_diff(75, 100)
