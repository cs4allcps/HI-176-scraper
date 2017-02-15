#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="This script takes a school's master schedule and spits out something a little more readable.")
parser.add_argument('inputFile', help="master schedule file to be parsed (CSV)", type=str, metavar="<schedule.csv>")

args = parser.parse_args()
inputFile = args.inputFile

import re
from unicodecsv import reader,writer

# create name for output file
outputFile = inputFile.split('.csv')[0] + '_clean.csv'

# chop off first 15 lines (header junk)
with open(inputFile, "r") as f:
    lines = f.readlines()
    school = lines[3].split(',')[0]
with open(inputFile, "w") as o:
    o.writelines([l for l in lines[15:]])

with open(inputFile, "r") as f, open(outputFile, "w") as o:
    guy = reader(f)
    gal = writer(o)

    # header
    gal.writerow(["School", "Teacher", "Course Code", "Course Name", "Period", "Room", "Students", "Capacity"])

    for row in guy:
        # skip short rows
        if len(row) < 32:
            continue

        # relevant rows include hour, teacher, seats remaining
        if row[1] != "" and row[19] != "" and row[-1] != "":
            hour = row[1]
            room = row[3]
            ccode = row[7]
            cname = row[14]
            teacher = row[19]
            students = int(float(row[23]))
            capacity = int(float(row[26]))

            gal.writerow([school, teacher, ccode, cname, hour, room, students, capacity])
