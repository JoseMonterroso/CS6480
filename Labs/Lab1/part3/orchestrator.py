#!/usr/bin/python
# Jose Monterroso - CS 6480 Adv Computer Networking
# Orchestrator 

import os
import sys
from optparse import OptionParser

# Start a Docker container 
def start_container(containers):
    print("Starting topology")
    cts = 'docker-compose up -d'
    for c in containers:
        cts += ' ' + c

    print('CMD: ' + cts)
    os.system(cts)

# Start OSPF, and Zebra on the containers provided
def start_OSPF(containers):
    print("Starting OSPF on Topology")

    # zebra, daemons, and ospf conf files added, also starting up zebra and ospfd
    for c in containers:
        os.system("docker cp ./cfiles/shared/daemons part3_"+ c + "_1:/etc/quagga")
        os.system("docker cp ./cfiles/shared/zebra.conf part3_"+ c + "_1:/etc/quagga")
        os.system("docker cp ./cfiles/"+ c +"/ospfd.conf part3_"+ c +"_1:/etc/quagga")
        os.system("docker exec -it part3_"+ c +"_1 service zebra start")
        os.system("docker exec -it part3_"+ c +"_1 service ospfd start")

# Install route at endpoint
def endpoint_routes(route):
    print("Adding route to endpoint")
    r = "docker exec -it part3_" + route[0] + "_1 route add -net " + route[1] + " gw " + route[2]
    print('CMD: ' + r)
    os.system(r)

# Move traffic on the "north" path (R1, R2, R3)
def north_path():
    print("North Path (r1, r2, r3)")

    #R1
    os.system("docker exec -it part3_r1_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 5'"'")
    os.system("docker exec -it part3_r1_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth2'"' -c '"'ip ospf cost 10'"'")

    #R2
    os.system("docker exec -it part3_r2_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth0'"' -c '"'ip ospf cost 5'"'")
    os.system("docker exec -it part3_r2_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 5'"'")

    #R3
    os.system("docker exec -it part3_r3_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth0'"' -c '"'ip ospf cost 5'"'")
    os.system("docker exec -it part3_r3_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 10'"'")

    #R4
    os.system("docker exec -it part3_r4_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth0'"' -c '"'ip ospf cost 10'"'")
    os.system("docker exec -it part3_r4_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 10'"'")

# Move traffic on the "south" path (R1, R4, R3)
def south_path():
    print("South Path (r1, r4, r3)")

    #R1
    os.system("docker exec -it part3_r1_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 10'"'")
    os.system("docker exec -it part3_r1_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth2'"' -c '"'ip ospf cost 5'"'")

    #R2
    os.system("docker exec -it part3_r2_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth0'"' -c '"'ip ospf cost 10'"'")
    os.system("docker exec -it part3_r2_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 10'"'")

    #R3
    os.system("docker exec -it part3_r3_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth0'"' -c '"'ip ospf cost 10'"'")
    os.system("docker exec -it part3_r3_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 5'"'")

    #R4
    os.system("docker exec -it part3_r4_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth0'"' -c '"'ip ospf cost 5'"'")
    os.system("docker exec -it part3_r4_1 vtysh -c '"'configure terminal'"' -c '"'router ospf'"' -c '"'interface eth1'"' -c '"'ip ospf cost 5'"'")

# Remove Container 
def remove_container(containers):
    r = "docker-compose rm -fsv"
    for c in containers:
        r += ' ' +  c

    print('CMD: ' + r)
    os.system(r)

# Main Function 
def main():
    # Establishing Commandline Args
    parser = OptionParser()
    parser.add_option('-u', '--start_container', action='store_true',
            dest='start', default=False, help='Start Container. Provide names as args')
    parser.add_option('-o', '--ospf', action='store_true',
            dest='ospf', default=False, help='Start OSPF. Provide names as args')
    parser.add_option('-p', '--add_routes', action='store_true',
            dest='routes', default=False, help='Install routes on host. <Host dest GW> as args')
    parser.add_option('-n', '--north', action='store_true',
            dest='north', default=False, help='Move traffic to north path')
    parser.add_option('-s', '--south', action='store_true',
            dest='south', default=False, help='Move traffic to south path')
    parser.add_option('-r', '--remove_container', action='store_true',
            dest='stop', default=False, help='Remove container. Provde name as args')
    (options, args) = parser.parse_args()

    # Choosing which option to follow through
    if options.start:
        start_container(args)
    elif options.ospf:
        start_OSPF(args)
    elif options.routes:
        endpoint_routes(args)
    elif options.north:
        north_path()
    elif options.south:
        south_path()
    elif options.stop:
        remove_container(args)
    else:
        print("Use -h for assistance")

if __name__ == "__main__":
    main()
