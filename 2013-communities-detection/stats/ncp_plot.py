filename = 'SLPAw_gowalla_weighted_max_run1_r0.5_v3_statistics.txt'

results = {}
for line in open(filename, 'r'):
	iec, bec, sdi, asd, pss, k, loi, iec_space, bec_space = line.strip().split(' ')
	if k not in results:
		results[k] = []
	results[k].append((iec, bec, sdi, asd, pss, k, loi, iec_space, bec_space))

for size in results.keys():
	values = results[size]
	m_iec = max([e[0] for e in values])
	m_bec = min([e[1] for e in values])
	m_sdi = min([e[2] for e in values])
	m_asd = min([e[3] for e in values])
	m_pss = max([e[4] for e in values])
	m_k = max([e[5] for e in values])
	m_loi = max([e[6] for e in values])
	m_iec_space = max([e[7] for e in values])
	m_bec_space = min([e[8] for e in values])
	
	print m_iec, m_bec, m_sdi, m_asd, m_pss, m_k, m_loi, m_iec_space, m_bec_space
