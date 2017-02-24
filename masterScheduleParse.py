#!/usr/bin/env python2

import argparse

parser = argparse.ArgumentParser(description="This script takes a school's master schedule and spits out something a little more readable.")
parser.add_argument('inputFile', help="master schedule file to be parsed (CSV)", type=str, metavar="<schedule.csv>")
parser.add_argument('-t', dest='reportFile', type=str, metavar="<reportfile.txt>")

args = parser.parse_args()
inputFile = args.inputFile
outputFolder = args.outputFolder

import re
from unicodecsv import reader,writer

# create name for output file
outputFile = inputFile.split('.csv')[0] + '_clean.csv'

# chop off first 15 lines (header junk)
with open(inputFile, "r") as f:
    lines = f.readlines()
    total = len(lines)
    school = lines[3].split(',')[0]
with open(inputFile, "w") as o:
    o.writelines([l for l in lines[15:]])

with open(inputFile, "r") as f, open(outputFile, "wb") as o:
    guy = reader(f)
    gal = writer(o)

    # header
    gal.writerow(["School", "Teacher", "Course Code", "Course Name", "Period", "Room", "Students", "Capacity"])
    i = 0

    print total
    print total - 15 -1

    for row in guy:
        # print row
        # print row
        i+=1
        # skip short rows
        if len(row) < 32:
            # print "short row"
            continue
        # print "bypassed continue"

        # relevant rows include hour, teacher, seats remaining
        if row[1] != "" and row[19] != "" and row[-1] != "":

            school = row[1]
            teacher = row[22]
            ccode = row[18]
            cname = row[21]
            hour = row[16]
            room = row[17]
            students = row[23]
            capacity = row[24]

            gal.writerow([school, teacher, ccode, cname, hour, room, students, capacity])

        if i == (total - 16):
            break;
