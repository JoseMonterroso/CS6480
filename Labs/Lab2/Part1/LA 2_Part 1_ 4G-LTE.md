# Introduction

In this exercise, we will create an end-to-end LTE network with the following components:

  * An `epc` node with HSS, MME, PGW, and SGW functions provided by NextEPC.
  * An `sim-enb` node with eNodeB and UE functionality over a simulated RAN provided by Open Air Interface.
  * A network link connecting the `epc` and `sim-enb` nodes.

We will configure these services, start them up, and observe the communication between the eNodeB and MME/SGW services over the network link.
For the EPC services, we start with a compute node running a stock Ubuntu 18.04 image with only essential POWDER platform client-side scripts.
The process of adding NextEPC and other tools in this exercise illustrates how you can go from a stock OS image to a custom software setup.

# Steps at a glance

  1. Instantiate the base experiment and open shells on each of the nodes.
  2. Download and compile the OAI RAN software.
  3. Install NextEPC prerequisites.
  4. Download and compile the NextEPC software.
  5. Configure networking on the `epc` host to support NextEPC
  6. Configure NextEPC's HSS, MME, SGW, and PGW components.
  7. Add the simulated UE's subscriber information to the HSS database.
  8. Start NextEPC services.
  9. Start Wireshark, and have it watch the network link.
  10. Start the simulated eNodeB and UE services on the `sim-enb` node.
  11. Verify UE attachment and connectivity, and observe S1-AP and GTP-U (S1-U) activity.

# Detailed Walk-through

This section takes you through the steps listed above in detail.

## Instantiate the base experiment and open shells on each of the nodes.

Be sure you are logged in to [POWDER](https://powderwireless.net).

* Navigate to profile and instantiate it.

Click the following link to open the profile for this exercise: [OAISIM-NEXTEPC Profile](https://www.powderwireless.net/p/PowderTeam/OAISIM-NEXTEPC).

Next, find and click the `Instantiate` button. This will take you to the experiment instantiation wizard with the above profile selected.  Click `Next` to proceed to the "Finalize" step (this profile has no user-selectable parameters). Click `Next` on the "Finalize" step, and then click `Finish` on the "Schedule" page.  Your experiment should now begin instantiating.

* Open shells on the two nodes

Once the experiment is up and running (green), use the SSH client on your computer to open *three* shells to *each* of the `epc` and `sim-enb` nodes. 
You can find the SSH commands to use in the `List View` tab of the experiment.

## Download and compile the OAI RAN software.

In a `sim-enb` node shell:

```
sudo apt-get remove -y --purge man-db
sudo bash
cd /opt
git clone https://gitlab.flux.utah.edu/jczhu/oaisim-xran/
cd oaisim-xran
git checkout develop
cd cmake_targets
sudo ./build_oai -I -c -C --eNB --UE -w SIMU
```

*Note:* Answer `yes` in the dialog that pops up asking about restarting services.

Leave the compilation running in this `sim-enb` shell window (it will take a while), and continue on through the NextEPC installation and configuration steps below.

## Install NextEPC prerequisites

NextEPC has a handful of prerequisites for building and running.  Most important of these is MongoDB, which it uses as its database backend for the HSS.  Run any commands specified in an `epc` shell window.

* Install MongoDB

```
sudo apt-get remove -y --purge man-db
sudo apt-get update
sudo apt-get -y install mongodb
sudo systemctl start mongodb

```

* Install other prerequisite build and library packages

```
sudo apt-get -y install autoconf libtool gcc pkg-config \
         git flex bison libsctp-dev libgnutls28-dev libgcrypt-dev \
         libssl-dev libidn11-dev libmongoc-dev libbson-dev libyaml-dev

```

*Note:* Answer `yes` in the dialog that pops up asking about restarting services.

* Install nodeJS (needed by NextEPC HSS database interface)

```
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get -y install nodejs

```

* Install Wireshark

```
sudo apt-get -y install wireshark
```

*Note:* Answer `no` when asked whether to enable dumping for non-root users.

## Download and compile NextEPC on the `epc` node

This step has you download and build NextEPC.  It will be installed into `/opt/nextepc/install` as well.  Run any commands specified in an `epc` node shell session.

* Download and compile NextEPC

```
sudo bash

cd /opt
git clone https://github.com/nextepc/nextepc
cd nextepc
autoreconf -iv
./configure --prefix=`pwd`/install
make -j `nproc`
make install

exit

```

* Install nodeJS library prerequisites and build the NextEPC HSS Web UI

```
cd /opt/nextepc/webui
sudo npm install
```

## Configure networking on the `epc` node to support NextEPC

NextEPC requires a tunnel device to be setup, and IP masquerading (NAT) for UE internet connectivity.  Run any commands specified in an `epc` node shell session.

* Create tunnel device

```
sudo bash

cat << EOF > /etc/systemd/network/98-nextepc.netdev
[NetDev]
Name=pgwtun
Kind=tun
EOF

exit

```

Next, restart systemd's networking handler:

```
sudo systemctl restart systemd-networkd

```

Now set the IP address on the `pgwtun` tunnel device:

```
sudo ip addr add 192.168.0.1/24 dev pgwtun
sudo ip link set up dev pgwtun
```

*Note:* These `ip` commands to set the address of the `pgwtun` interface and bring it online need to be executed again if the `epc` node is rebooted.

* Setup NAT (IP Masquerade) 

We need to configure NAT to allow UEs connected to the NextEPC PGW to access the Internet.  The file `/var/emulab/boot/controlif` contains the name of the internet-facing "control network" device.

```
sudo iptables -t nat -A POSTROUTING -o `cat /var/emulab/boot/controlif` -j MASQUERADE

```

## Configure NextEPC services (HSS, MME, PGW, SGW)

Before starting NextEPC services, we need to edit its configuration file.

* Get IP address of the `epc` <-> `sim-enb` network link

We'll need to gather some interface configuration information befor making any edits.  Run the `ip` or `ifconfig` command at the shell prompt and look for the interface with a `10.10.x.x` IP address.  Write down or save off this interface name and IP address.  We refer to these as `EPC_IFACE` and `EPC_IP` below.

```
ip addr show to 10.10.0.0/16

```

* Change directory to where this configuration file is kept

```
cd /opt/nextepc/install/etc/nextepc

```

* Open `nextepc.conf` for editing 

You can use your favorite editor (emacs, vi, nano, etc.).  **Be careful with spacing!**  This is a YAML configuration file, and it is sensitive to exact indentation levels using spaces (not tabs).  Be sure to use `sudo` to open the file since it is owned by the root user.

```
sudo nano nextepc.conf

```

- In the `mme:` configuration section, find the `s1ap:` entry.  Add an `addr:` entry that has your `EPC_IP` address listed (recorded in previous step.).  E.g.,

```
    s1ap:
      addr: 10.10.1.2

```

- In the `mme:` configuration section, find the `gtpc:` entry. Add an `addr:` entry with the `127.0.0.1` localhost address specified.

```
    gtpc:
      addr: 127.0.0.1
```

- In the `mme:` configuration section, find the `gummei:` portion.  Edit the `mcc:` to be `998` and the `mnc:` to be `98`.  These will match what is configured on the OAI simulated UE.

```
    gummei:
      plmn_id:
        mcc: 998
        mnc: 98
      mme_gid: 2
      mme_code: 1

```

- In the `mme:` configuration section, find the `tai:` entry. Change the `mcc:` to `998` and the `mnc:` to `98`. Also change the `tac:` entry to `1`:

```
    tai:
      plmn_id:
        mcc: 998
        mnc: 98
      tac: 1

```

- In the `sgw:` configuration section, find the `gtpu:` entry and set the address to be that of your `EPC_IP`. E.g.,

```
    gtpu:
      addr: 10.10.1.2

```

- In the `pgw:` configuration section, find the `ue_pool:` entry. Remove the two address ranges listed, and add `- addr: 192.168.0.1/24`:

```
    ue_pool:
      - addr: 192.168.0.1/24

```

* Close and save the configuration file.

# Add the simulated UE subscriber information to the HSS database

NextEPC provides a UI written in nodeJS for interacting with the HSS database.  We set it up and run it here.

* Start the Web UI

```
cd /opt/nextepc/webui
sudo npm run dev
```

* Browse to Web UI interface and log in

Now open the Web UI from a browser tab on your machine.  Note the hostname of your `epc` host from the `List View` tab in the POWDER Portal interface view of your experiment.  Use that hostname, along with port `3000` to access the NextEPC Web UI:

```
http://pcXXX.emulab.net:3000
```

It takes a few seconds for the page to load.  Log in with username `admin` and password `1423`.

* Add subscriber to the HSS using the Web UI

Click the `Add A Subscriber` link on the page.  In the dialog box that follows, use the following values:

```
IMSI: 998981234560308
Subscriber Key (K): 00112233445566778899aabbccddeeff
Authentication Management Field (AMF): 8000
USIM Type: OPc
Operator Key (OPc/OP): 0ED47545168EAFE2C39C075829A7B61F
```

<!---
```
IMSI: 99898000001234
Subscriber Key (K): 8BAF473F2F8FD09487CCCBD7097C6862
Authentication Management Field (AMF): 8000
USIM Type: OP
Operator Key (OPc/OP): 01020304050607080910111213141516
```
--->

Now click `Save` in the lower right of the dialog.  Lastly, type `CTRL-C` to stop the web service in your `epc` shell and close the browser tab you opened.

# Start NextEPC services

We will start NextEPC HSS, MME, SGW, and PGW services by invoking its unified binary.  This binary will fork and run each of these individual services, reading the configuration file we modified in the last step (`nextepc.conf`).

* Start NextEPC services

In an `epc` shell, execute:

```
sudo /opt/nextepc/install/bin/nextepc-epcd
```

Once this command is run, the current `epc` shell will perpetually run the EPC services until you press the `CTRL-C` key sequence.  Log messages from NextEPC will appear in the shell.  Other interactions with the `epc` node will now need to be performed from the other shell you have opened.

# Start Wireshark

In your other `epc` shell, assuming you have X11 forwarding setup properly, run Wireshark to watch the network link between the `sim-enb` and `epc` node.  Use the network interface identified previously when editing the NextEPC configuration file as the interface to listen on.

```
sudo -E wireshark -i EPC_IFACE
```

You must replace `EPC_IFACE` with the actual name of the interface that you wrote down earlier.  Once Wireshark is running, verify that the correct interface is selected, and click the "start" button (looks like a shark fin).  You should not see anything aside from a few stray LLDP packets (from the attached Ethernet switch) until we start the eNodeB and UE on the `sim-enb` node.  Minimize this window for now.  We will come back to it later.

# Start the simulated eNodeB and UE on the `sim-enb` node

In a `sim-enb` shell, start the eNodeB:

```
cd /opt/oaisim-xran/cmake_targets/lte_build_oai/build
sudo RFSIMULATOR=enb   ./lte-softmodem -O /opt/oaisim-xran/enb1.conf --rfsim
```

In a `sim-enb` shell, start the UE:

```
cd /opt/oaisim-xran/cmake_targets/lte_build_oai/build
sudo RFSIMULATOR=127.0.0.1 ./lte-uesoftmodem -C 2125000000 -r 25 --rfsim
```

Open another `sim-enb` shell to verify that the UE successfully connected:

```
ping -I oaitun_ue1 8.8.8.8
```

<!---
```
sudo /local/repository/bin/sim_enb.start.sh && sudo screen -r
```

You will now be viewing the OAI eNodeB console output, which is running inside of a `screen` session as root.  You should see a bunch of initialization, connection, and attachment messages go by as the eNodeB starts and the UE (running in a another process) attaches over the simulated RAN.

# Verify attachment and connectivity of UE and observe S1AP and S1-U traffic

* Run ping test from simulated UE to Internet

In your other `sim-enb` shell, run a quick ping test to validate that the UE connection is active.  The OAI code brings up an interface that carries traffic over the simulated RAN.

```
ping -I oip1 8.8.8.8
```

The `-I oip` flag tells `ping` to use the simulated UE/RAN interface to send its packets.  You should see successful ping replies come back.  As the pings packets are sent and received, you should see activity in the OAI eNodeB console output similar to the following:

```
[RLC][I][FRAME 00612][ UE][MOD 00][RNTI b0a0][DRB AM 01] RLC_AM_DATA_REQ size 86 Bytes,  NB SDU 1 current_sdu_index=6 next_sdu_index=7 conf 0 mui 0
[PHY][I][UE  0][PDSCH b0a0] frame 613, subframe 7: Po_PUCCH 34 dBm : Po_NOMINAL_PUCCH -104 dBm, PL 89 dB, g_pucch 46 dB
[RLC][I][FRAME 00000][eNB][MOD 00][RNTI b0a0][DRB AM 01] RLC_AM_DATA_REQ size 86 Bytes,  NB SDU 1 current_sdu_index=6 next_sdu_index=7 conf 0 mui 0
[PHY][I][UE  0][PDSCH b0a0] frame 614, subframe 4: Po_PUCCH 34 dBm : Po_NOMINAL_PUCCH -104 dBm, PL 89 dB, g_pucch 46 dB
...
```
--->

* Look at captured wireshark traffic

Bring your Wireshark window up now and see what packets have been captured on the link between the `sim-enb` and the `epc` nodes.  Click the "stop" button to stop capturing packets. You should see SCTP packets (for the S1AP connection), along with S1AP/NAS messages where the UE authenticated with the HSS.  You should also see GTP tunneled ping packets from the ping command you ran above.  This confirms connectivity.  You can drill down into the S1AP NAS packets to see the LTE authentication elements in detail.

![Wireshark window showing S1AP/GTP traffic](/LA 2/images/wireshark-nextepc.png "Wireshark capture")


