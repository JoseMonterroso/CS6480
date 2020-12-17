# RAN softwarization - Using OAI, XRAN and the ONOS framework

#### Setup

1.  We will re-use the experiment you created in the [Part 1: 4G - LTE](https://gitlab.flux.utah.edu/teach-studentview/cs6480-2020/-/blob/master/LA%202/Part%201:%204G-LTE.md) session.

#### ONOS control framework and the XRAN control application 

1.  Open a shell on the `epc` node. Install the ONOS dependencies:
	```
	sudo apt update
	sudo apt install -y openjdk-8-jdk
	sudo apt install -y openjfx=8u161-b12-1ubuntu2 libopenjfx-jni=8u161-b12-1ubuntu2 libopenjfx-java=8u161-b12-1ubuntu2
	sudo apt-get install libcommons-math-java
	```

2.  Download and build the ONOS environment:
	```
	sudo bash
	cd /opt
	git clone https://gitlab.flux.utah.edu/jczhu/xransim
	export ONOS_ROOT=/opt/xransim
	cd /opt/xransim
	source $ONOS_ROOT/tools/dev/bash_profile
	onos-buck build onos --show-output
	```
	
3.  Run the ONOS environment:
	```
	onos-buck run onos-local
	```
	
3.  Once the ONOS controller started up, open another shell on the `epc` noded and start the ONOS console:

	(a) Set up the ONOS environment:
	
	```
	sudo bash
	export ONOS_ROOT=/opt/xransim
	cd /opt/xransim
	source $ONOS_ROOT/tools/dev/bash_profile
		
	```

	(b) Register the eNodeB agent with XRAN:
	
	```
	onos-netcfg 127.0.0.1 apps/xran/xran-cfg.json
	```
	
	(c) Start up the ONOS console:
	
	```
	onos 127.0.0.1 -l onos
	```
	The password is: rocks

5.  Within the ONOS console activate the XRAN component:

	```
	app activate org.onosproject.xran
	```
	
6.  Verify that XRAN has no UEs associated with it. Within the ONOS console run:

	```
	hosts
	```
	
	At this point this should *not* show any output.

7. Restart the EPC and RAN components.

	(a) Open a shell on the `epc` node and start up the NextEPC services:

	```
	sudo /opt/nextepc/install/bin/nextepc-epcd
	```

	(b) Open a shell on the `sim-enb` node and start up the simulated OAI eNodeB:

	```
    cd /opt/oaisim-xran/cmake_targets/lte_build_oai/build
    sudo RFSIMULATOR=enb   ./lte-softmodem -O /opt/oaisim-xran/enb1.conf --rfsim
    ```

	If you want to restart the eNodeB: Type "Control-C" to kill the process, then execute the last command again to restart.

	(c) Open another shell on the `sim-enb` node and start up the simulated OAI UE:

	```
	cd /opt/oaisim-xran/cmake_targets/lte_build_oai/build
	sudo RFSIMULATOR=127.0.0.1 ./lte-uesoftmodem -C 2125000000 -r 25 --rfsim

	```

	If you want to restart the UE: Type "Control-C" to kill the process, then execute the last command again to restart.
	
	
8.  Verify that the OAI components interact with XRAN. In the ONOS console run:

	```
	hosts
	```

	This time you should see information associated with the simulated OAI UE.

9.  Start up an `iperf` server on the simulated UE. Open another shell on the `sim-enb` node and run:

	```
	iperf -s -u -i 1
	```
	
10. Start up an `iperf` client on the EPC. Open another shell on the `epc` node and run:

	```
	iperf -c 192.168.0.2 -u -i 1 -b 5M -t 5
	```
	
11. Note the throughput reported in the iperf *server* node. (I.e., the output for iperf on the simulated UE on the `sim-enb` node.)

12.  Change the number of physical resource blocks (PRBs) in the downlink direction via the XRAN API. On the `epc` node execute: 

```
curl -H "Content-Type: application/json" --request PATCH -d '{"RRMConf":{"start_prb_dl":0,"end_prb_dl":10}}' -u onos:rocks "http://localhost:8181/onos/xran/links/{00001000},{0}"
```

13. Rerun the `iperf` test and note the change in throughput. On the `epc` node, rerun:

	```
	iperf -c 192.168.0.2 -u -i 1 -b 5M -t 5
	```
	
14. Note the throughput reported in the iperf *server* node. (I.e., the output for iperf on the simulated UE on the `sim-enb` node.)

	You should observe a lower downlink throughput than before.

15.  When you are finished, return to the experiment page and press the `Terminate` button.
