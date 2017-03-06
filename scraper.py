#!/usr/bin/env python2

import argparse, datetime, os, time, numpy
from scraperCore import fromReportFile, findSchools, testLogin, sThread, clean
from unicodecsv import reader,writer

parser = argparse.ArgumentParser(description="This script takes a school's master schedule and spits out something a little more readable.")
parser.add_argument('-t', dest='reportFile', type=str, metavar="<reportfile.txt>",
                    help="This textfile contains the list of schools that the script finds reports for", default=None)
parser.add_argument('-tc', dest='threadCount', type=int, metavar="<max thread count>",
                    help="The number of threads to use", default=2)
parser.add_argument('-wl', dest='windowLimit', type=int, metavar="<max window count>",
                    help="The max number of windows that can open per thread", default=5)
parser.add_argument('-c', dest='chrome', type=bool, metavar="<chrome>",
                    help="Run with chrome", default=False)

args = parser.parse_args()
reportFile = args.reportFile
windowLimit = args.windowLimit
threadCount = args.threadCount

downloadTime = datetime.datetime.now().strftime('%Y-%m-%d')
folder = downloadTime + ' ' + 'HI 176 Reports'
tempfolder = downloadTime + ' tempfolder'
loggedIn = False
schoollist = []
prettylist = []
windows = 0
running = 0
completed = 0
failures = 0

# if folders do not exists, make them
if not os.path.exists(folder):
    os.makedirs(folder)

# if a reportFile is provided then run fromReportFile() to split the file into
# the schoollist and prettylist
if reportFile:
    schoollist, prettylist = fromReportFile(reportFile, folder)
# if no reportFile is provided, use findSchools() to ask the user for a school
else:
    schoollist, prettylist = findSchools()

# if the length of schoollist is greater than 1, then split schoollist and
# prettylist into lists of roughly equal length that will be fed to the threads
if len(schoollist) > 1:
    schoolThreadList = numpy.array_split(numpy.array(schoollist), threadCount)
    prettyThreadList = numpy.array_split(numpy.array(prettylist), threadCount)
else:
    threadCount = 1
    schoolThreadList = [schoollist]
    prettyThreadList = [prettylist]

# ask the user for login information
user, password = testLogin()

# create the threads
threads = []
for i in range(threadCount):
    thread = sThread(i, user, password, prettyThreadList[i], schoolThreadList[i], tempfolder, windowLimit)
    thread.start()
    threads.append(thread)

for i in range(threadCount):
    threads[i].join()

# at this point, all threads will have been completed
print "All threads done"
print "Converting files"

filelist = []
time.sleep(5)
unknownCount = 0
foundSchools = []

# move the files out of the temporary folders into a single folder for reports
for i in range(threadCount):
    print "thread", i
    path = tempfolder + str(i) + '\\'
    filelist = [f for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))]
    # loop through files in temporary folder
    for report in filelist:
        with open(path + report, 'rb') as csv:
            for row in csv:
                schoolName = ""
                try:
                    schoolName = row.split(",")[1].strip('"')
                    if schoolName:
                        foundSchools.append(schoolName)
                        break
                except IndexError:
                    continue
            csv.close()
        # if no school name can be found in the downloaded report or the file
        # already exists => remove the file from the temporary folder
        if not schoolName or os.path.isfile(folder + '\\' + downloadTime + " " + schoolName + ".csv"):
            os.remove(path + report)
            continue
        # change the report's name to include the school name and move it to
        # another folder
        else:
            os.rename(path + report, folder + '\\' + downloadTime + " " + schoolName + ".csv")
    # remove temporary folder once it is empty
    os.rmdir(path)

# clean the files
print "Clean raw files"
clean(folder, downloadTime)

# isolate schools that do not have reports
missing = list(set(prettylist) - set(foundSchools))

print "\nMissing schools:"

missingFile = folder + '\\' + downloadTime + " missing_reports.csv"
with open(missingFile, 'wb') as f:
    toFile = writer(f)
    for s in missing:
        print s
        toFile.writerow([s])
