
import argparse
import os 
from openpyxl import Workbook
import re

def main():
    parser = argparse.ArgumentParser(description='Process some SPLAT')
    parser.add_argument('-i', dest='cf')
    args = parser.parse_args()
    CF = float(args.cf)

    frq_lst = []
    #3561 PUT IN AS MHZ
    step = 0.05 # MHz
    # Header Parsing 
    header = [ "Name", "Tx", "Rx", "Distance" ]

    for x in range(1,10):
        frq_lst.append(CF+(x*step)) # MHz
        header.append(str((CF/1000)+(x*(step/1000))) + " GHz") # GHz


    # Locations 
    name = ["behavioural.qth", "browning.qth", "friendship.qth", "hospital.qth", "meb.qth", "medical.qth", "sagepoint.qth"]

    # Creating excel sheet
    wb = Workbook()
    ws = wb.active
    header.append("Avg Power")
    ws.append(header)

    radio = {
        "behavioural": "bes",
        "browning": "browning",
        "friendship": "fm",
        "hospital": "hospital",
        "meb": "meb",
        "medical":"smt",
        "sagepoint":"sagepoint"
    }

     # filler values
    row = []
    avgPower = 0
    Name = ""
    Tx = ""
    Rx = ""
    Distance = 0
    count = 0
    pwr = 0

    for tx in name:
        for rx in name:
            if tx != rx:
                Tx = tx.split('.')[0]
                Rx = rx.split('.')[0]

                Name = radio[Tx] + "," + radio[Rx]
                row.append(Name)
                row.append(radio[Tx])
                row.append(radio[Rx])
                
                Distance = get_distance(tx, rx)
                row.append(Distance)
                for freq in frq_lst:
                    os.system("sudo splat -metric -t " + tx + " -r " + rx + " -f "+ str(freq))
                    pwr = get_power(tx, rx)
                    avgPower = avgPower + pwr
                    count = count + 1
                    row.append(pwr)
                #
                avgPower = avgPower / count
                row.append(float(avgPower))
                ws.append(row)
                #
                row = []
                avgPower = 0
                Name = ""
                Tx = ""
                Rx = ""
                Distance = 0
                count = 0
                pwr = 0 

    # Finish
    wb.save("temp.xlsx")
                
                


# distance
def get_distance(tx, rx):
    radio = {
        "behavioural.qth": "Behavioral",
        "browning.qth": "Browning",
        "friendship.qth": "Friendship",
        "hospital.qth": "Hospital",
        "meb.qth": "MEB",
        "medical.qth":"Medical_Tower",
        "sagepoint.qth":"Sagepoint"
    }

    t = radio[tx]
    r = radio[rx]
    dist = []
    f = open(t + "-to-" + r + ".txt", 'r')
    for line in f.readlines():
        if re.match(r'^Distance to ',line):
            dist = line.split(' ')
            break 

    if radio[rx] == "Medical_Tower":
        dst = float(dist[4]) * 1000
    else:
        dst = float(dist[3]) * 1000
    f.close()
    return dst

# power     
def get_power(tx, rx):
    radio = {
        "behavioural.qth": "Behavioral",
        "browning.qth": "Browning",
        "friendship.qth": "Friendship",
        "hospital.qth": "Hospital",
        "meb.qth": "MEB",
        "medical.qth":"Medical_Tower",
        "sagepoint.qth":"Sagepoint"
    }

    t = radio[tx]
    r = radio[rx]
    dist = []
    f = open(t + "-to-" + r + ".txt", 'r')
    for line in f.readlines():
        if re.match(r"^Signal power level ",line):
            dist = line.split(' ')
            break

    f.close()

    if radio[rx] == "Medical_Tower":
        return float(dist[6])
    else:
        return float(dist[5])


if __name__ == "__main__":
    main()




##### NON Round Robin Fashion
###
##
#
#import argparse
#import os
#from openpyxl import Workbook
#import re

#def main():
#    parser = argparse.ArgumentParser(description='Process some SPLAT')
#    parser.add_argument('-i', dest='cf')
#    args = parser.parse_args()
#    CF = float(args.cf)

#    frq_lst = []
#    #3561 PUT IN AS MHZ
#    step = 0.05 # MHz
#    # Header Parsing 
#    header = [ "Name", "Tx", "Rx", "Distance" ]

#    for x in range(1,10):
#        frq_lst.append(CF+(x*step)) # MHz
#        header.append(str((CF/1000)+(x*(step/1000))) + " GHz") # GHz


    # Locations 
#    name = ["behavioural.qth", "browning.qth", "friendship.qth", "honors.qth", "sagepoint.qth", "ustar.qth"]
#    name2 = ["bookstore.qth", "ebc.qth", "garage.qth", "guesthouse.qth", "humanities.qth", "law73.qth", "madsen.qth", "moran.qth", "web.qth"]

    # Creating excel sheet
#    wb = Workbook()
#    ws = wb.active
#    header.append("Avg Power")
#    ws.append(header)

#    radio = {
#        "behavioural": "bes",
#        "browning": "browning",
#        "friendship": "fm",
#        "hospital": "hospital",
#        "meb": "meb",
#        "medical":"smt",
#        "sagepoint":"sagepoint",
#        "honors":"honors",
#        "ustar":"ustar",
#        "bookstore":"bookstore",
#        "ebc":"ebc",
#        "garage":"garage",
#        "guesthouse":"guesthouse",
#        "humanities":"humanities",
#        "law73":"law73",
#        "madsen":"madsen",
#        "moran":"moran",
#        "web":"web"
#    }

     # filler values
#    row = []
#    avgPower = 0
#    Name = ""
#    Tx = ""
#    Rx = ""
#    Distance = 0
#    count = 0
#    pwr = 0

#    for tx in name:
#        for rx in name2:
#            if tx != rx:
#                Tx = tx.split('.')[0]
#                Rx = rx.split('.')[0]

#                Name = radio[Tx] + "," + radio[Rx]
#                row.append(Name)
#                row.append(radio[Tx])
#                row.append(radio[Rx])

#                Distance = get_distance(tx, rx)
#                row.append(Distance)
#                for freq in frq_lst:
#                    os.system("sudo splat -metric -t " + tx + " -r " + rx + " -f "+ str(freq))
#                    pwr = get_power(tx, rx)
#                    avgPower = avgPower + pwr
#                    count = count + 1
#                    row.append(pwr)
#                #
#                avgPower = avgPower / count
#                row.append(float(avgPower))
#                ws.append(row)
#                #
#                row = []
#                avgPower = 0
#                Name = ""
#                Tx = ""
#                Rx = ""
#                Distance = 0
#                count = 0
#                pwr = 0

#    # Finish
#    wb.save("temp.xlsx")

# distance
#def get_distance(tx, rx):
#    radio = {
#        "behavioural.qth": "Behavioral",
#        "browning.qth": "Browning",
#        "friendship.qth": "Friendship",
#        "hospital.qth": "Hospital",
#        "meb.qth": "MEB",
#        "medical.qth":"Medical_Tower",
#        "sagepoint.qth":"Sagepoint",
#        "honors.qth":"Honors",
#        "ustar.qth":"USTAR",
#        "bookstore.qth":"Bookstore",
#        "ebc.qth":"EBC",
#        "garage.qth":"Garage",
#        "guesthouse.qth":"Guesthouse",
#        "humanities.qth":"Humanities",
#        "law73.qth":"Law73",
#        "madsen.qth":"Madsen",
#        "moran.qth":"Moran",
#        "web.qth":"WEB"
#    }

#    t = radio[tx]
#    r = radio[rx]
#    dist = []
#    f = open(t + "-to-" + r + ".txt", 'r')
#    for line in f.readlines():
#        if re.match(r'^Distance to ',line):
#            dist = line.split(' ')
#            break

#    if radio[rx] == "Medical_Tower":
#        dst = float(dist[4]) * 1000
#    else:
#        dst = float(dist[3]) * 1000
#    f.close()
#    return dst

# power     
#def get_power(tx, rx):
#    radio = {
#        "behavioural.qth": "Behavioral",
#        "browning.qth": "Browning",
#        "friendship.qth": "Friendship",
#        "hospital.qth": "Hospital",
#        "meb.qth": "MEB",
#        "medical.qth":"Medical_Tower",
#        "sagepoint.qth":"Sagepoint",
#        "honors.qth":"Honors",
#        "ustar.qth":"USTAR",
#        "bookstore.qth":"Bookstore",
#        "ebc.qth":"EBC",
#        "garage.qth":"Garage",
#        "guesthouse.qth":"Guesthouse",
#        "humanities.qth":"Humanities",
#        "law73.qth":"Law73",
#        "madsen.qth":"Madsen",
#        "moran.qth":"Moran",
#        "web.qth":"WEB"
#    }

#    t = radio[tx]
#    r = radio[rx]
#    dist = []
#    f = open(t + "-to-" + r + ".txt", 'r')
#    for line in f.readlines():
#        if re.match(r"^Signal power level ",line):
#            dist = line.split(' ')
#            break

#    f.close()

#    if radio[rx] == "Medical_Tower":
#        return float(dist[6])
#    else:
#        return float(dist[5])


#if __name__ == "__main__":
#    main()
