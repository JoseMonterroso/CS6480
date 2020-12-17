import argparse
import re
from openpyxl import Workbook


def main():
    # Args to filename
    parser = argparse.ArgumentParser(description="Read in file")
    parser.add_argument('-f', dest="filename", help="Filename as .txt file")
    args = parser.parse_args()
    filename = args.filename
    
    # Creating excel sheet
    wb = Workbook()
    ws = wb.active

    # Header Parsing 
    header = [ "Name", "Tx", "Rx", "Distance" ]
    CF = 2.620

    for x in range(1,10):
        header.append(str(CF+(x*0.00005)) + " GHz")

    header.append("Avg Power")
    ws.append(header)

    # Read in parse data
    f = open(filename + ".txt")
    lines = f.readlines()

    # filler values
    row = []
    avgPower = 0
    Name = ""
    Tx = ""
    Rx = ""
    Distance = 0
    count = 0

    # Every third line is one data set 
    for l in range(0, len(lines)-1, 3):
        # 
        line1 = re.split(' |, |\n', lines[l])
        Distance = int(line1[5])
        Tx = line1[1]
        Rx = line1[3]
        Name = Tx + "," + Rx
        row.append(Name)
        row.append(Tx)
        row.append(Rx)
        row.append(Distance)

        #
        line2 = re.findall("-[0-9]*.[0-9]*",lines[l+1])
        for x in range(0, len(line2)):
            row.append(float(line2[x]))
            avgPower += float(line2[x])
            count = count + 1

        # 
        line3 = re.findall("-[0-9]*.[0-9]*",lines[l+2])
        for x in range(0, len(line3)):
            row.append(float(line3[x]))
            avgPower += float(line3[x])
            count = count + 1
        
        # Append Row 
        row.append(float(avgPower/count))
        ws.append(row)

        # Reset
        row = []
        avgPower = 0
        Name = ""
        Tx = ""
        Rx = ""
        Distance = 0
        count = 0

     
    # Finish
    f.close()
    wb.save(filename + ".xlsx")


if __name__ == "__main__":
    main()