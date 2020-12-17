#!/bin/bash
# Docker container setup with OSPF and Zebra running 

# Compose docker container topology
docker-compose up -d

# Array of container names
declare -a arr=("r1" "r2" "r3" "r4")

# zebra, daemons, and ospf conf files added, also starting up zebra and ospfd 
for i in "${arr[@]}"
	do
		docker cp ./cfiles/shared/daemons part2_"$i"_1:/etc/quagga
		docker cp ./cfiles/shared/zebra.conf part2_"$i"_1:/etc/quagga
		docker cp ./cfiles/"$i"/ospfd.conf part2_"$i"_1:/etc/quagga
		docker exec -it part2_"$i"_1 service zebra start
		docker exec -it part2_"$i"_1 service ospfd start
	done

# Add Routes to ha and hb
docker exec -it part2_ha_1 route add -net 10.0.19.0/24 gw 10.0.14.4
docker exec -it part2_hb_1 route add -net 10.0.14.0/24 gw 10.0.19.3
