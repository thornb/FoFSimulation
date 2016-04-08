NetworkCode=$1

for RoutingCode in 1 2 3
do
	python routing_simulation_v2.py $NetworkCode 7 $RoutingCode 2 1 -1 0
done

python routing_simulation_v2.py $NetworkCode 7 4 2 1 -1 8
