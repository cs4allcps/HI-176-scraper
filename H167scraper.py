import scraper3
import argparse, datetime, os

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

if reportFile:
    schoollist, prettylist = fromReportFile(reportFile, folder)
else:
    schoollist, prettylist = findSchools()

if len(schoollist) > 1:
    schoolThreadList = numpy.array_split(numpy.array(schoollist), threadCount)
    prettyThreadList = numpy.array_split(numpy.array(prettylist), threadCount)
else:
    threadCount = 1
    schoolThreadList = [schoollist]
    prettyThreadList = [prettylist]

user, password = testLogin()

threads = []
for i in range(threadCount):
    thread = sThread(i, user, password, prettyThreadList[i], schoolThreadList[i])
    thread.start()
    threads.append(thread)

for i in range(threadCount):
    threads[i].join()

print "All threads done"
print "Converting files"

filelist = []
time.sleep(5)
unknownCount = 0
foundSchools = []

for i in range(threadCount):
    print "thread", i
    path = tempfolder + str(i) + '\\'
    filelist = [f for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))]
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

        if not schoolName:
            os.remove(path + report)
            continue
        else:
            os.rename(path + report, folder + '\\' + downloadTime + " " + schoolName + ".csv")
    os.rmdir(path)

print "Clean raw files"
clean(folder, downloadTime)
# print foundSchools
missing = list(set(prettylist) - set(foundSchools))

print "\nMissing schools:"
for s in missing:
    print s
