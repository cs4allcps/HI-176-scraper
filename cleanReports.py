import argparse, datetime
from scraperCore import clean

parser = argparse.ArgumentParser(description="This script applies the masterScheduleParse.py script to a folder of HI 176 reports")
parser.add_argument('folder', help="folder of HI 176 reports", type=str, metavar="<schedule.csv>")

# select folder to clean reports from
args = parser.parse_args()
folder = args.folder
downloadTime = "2017-02-27"# datetime.datetime.now().strftime('%Y-%m-%d')
#
# import re, os, datetime
# from unicodecsv import reader,writer
#
# # select all files from the provided folder
# filelist = [f for f in os.listdir(folder)
#                 if os.path.isfile(os.path.join(folder,f))]
# downloadTime = datetime.datetime.now().strftime('%m-%d-%y--%H-%M')
#
# # iterate through the files in the folder
# for inputFile in filelist:
#     # create name for output file
#     if 'clean' in inputFile:
#         continue
#
#     inputFile = folder + inputFile
#     outputFile = inputFile.split('.csv')[0] + '_clean.csv'
#
#     # chop off first 15 lines (header junk)
#     with open(inputFile, "r") as f:
#         lines = f.readlines()
#         total = len(lines)
#
#     with open(inputFile, "r") as f, open(outputFile, "wb") as o:
#         guy = reader(f)
#         gal = writer(o)
#
#         # header
#         gal.writerow(["School", "Teacher", "Course Code", "Course Name", "Period", "Room", "Students", "Capacity"])
#         i = 0
#
#         try:
#             for row in guy:
#                 i+=1
#                 # skip short rows
#                 if len(row) < 32:
#                     continue
#
#                 # relevant rows include hour, teacher, seats remaining
#                 if row[1] != "" and row[19] != "" and row[-1] != "":
#
#                     school = row[1]
#                     teacher = row[22]
#                     ccode = row[18]
#                     cname = row[21]
#                     hour = row[16]
#                     room = row[17]
#                     students = row[23]
#                     capacity = row[24]
#
#                     gal.writerow([school, teacher, ccode, cname, hour, room, students, capacity])
#
#                 if i == (total - 1):
#                     break;
#         except UnicodeDecodeError:
#             print school
#
# filelist = [f for f in os.listdir(folder)
#                 if os.path.isfile(os.path.join(folder,f))]
# cleanFiles = []
#
# for files in filelist:
#     if 'clean' in files:
#         cleanFiles.append(files)
#
#
# mergeFile = folder + '\\' + downloadTime + "mergeFile.csv"
#
#
# with open(mergeFile, "wb") as o:
#     for cf in cleanFiles:
#         gal = writer(o)
#
#         with open(folder + cf, "r") as f:
#             guy = reader(f)
#             for row in guy:
#                 gal.writerow(row)
clean(folder, downloadTime)
