import cPickle


locdata = cPickle.load(open('data/gowalla_users_locationmap.pck','rb'))

udata = cPickle.load(open('data/gowalla_users_locations.pck','rb'))

states_data = {}
mapcount = 0

for uid,latlong in udata.items():
	if latlong not in locdata.keys():
		continue
	mapcount = mapcount+1
	state = locdata[latlong]
	if state not in states_data.keys():
		states_data[state] = set()
	states_data[state].add(uid)

cPickle.dump(states_data,open('data/gowalla_us_states.pck','wb'))
print "Succesfully added",mapcount,"of",len(udata),"users"
