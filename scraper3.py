#!/usr/bin/env python2

"""
TODO:   Remove schools that already have reports downloaded from schoollist and
        prettylist.
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from schools import schools
from unicodecsv import reader,writer
import getpass, os, time, datetime, threading, argparse, numpy

# import argparse

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

def findSchools():
    print "SCHOOL SEARCH"
    found = False
    schoollist = []
    prettylist = []
    while not found:
        search = raw_input("Search: ")
        # split the search string so that it can search the schools using
        # multiple keywords
        searchStrings = search.split()
        matches = []
        for ss in searchStrings:
            ssmatches = [s for s in schools if ss.lower() in s.lower()]
            matches += ssmatches
        # this eliminates any duplicates from the matches list
        matches = list(set(matches))
        if len(matches) >= 1:
            for i in range(len(matches)):
                print i, matches[i][:-14]
            print '\nType number of option to select school'
            print 'If schools is not available, simply hit enter and you can search again'
            selection = raw_input("Selection number: ")

            if selection == '':
                print "No selection. Search again."
            elif int(selection) in range(len(matches)):
                selection = matches[int(selection)]
                schoollist.append(selection)
                prettylist.append(selection[:-14]) # = selection[:-14]
                found = True
                print "Selected:",prettylist[0]
                return schoollist, prettylist

            elif int(selection) < 0 or int(selection) >= len(matches):
                print "Invalid choice number. Seach again."
            print
        else:
            print 'Did not find any schools related to that search\nPlease try again\n'

def fromReportFile(textfile, folder=None):
    print "READING FROM SCHOOL LIST"
    schoollist = []
    prettylist = []
    filelist = []

    if folder:
        filelist = [f for f in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder,f))]

    with open(textfile) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            include = True
            school = lines[i]
            if folder:
                for f in filelist:
                    if school.strip() + ".csv" in f:
                        include = False
                        break
            if include:
                schoollist.append(lines[i].replace("\n", " - School View"))
                prettylist.append(lines[i].rstrip("\n"))
            include = True

    return schoollist, prettylist

def testLogin():
    loggedIn = False

    while not loggedIn:
        user = raw_input("USERNAME: ")
        password = getpass.getpass("PASSWORD: ")
        # create driver
        driver = webdriver.Chrome()
        driver.get("http://sim.cps.k12.il.us/")

        # LOGIN PAGE
        print "\nAttempting to sign in"
        # username
        elem = driver.find_element_by_name("user")
        elem.clear()
        elem.send_keys(user)
        # password
        elem = driver.find_element_by_name("pass")
        elem.clear()
        elem.send_keys(password)
        # domain
        elem = driver.find_element_by_name("domn")
        elem.clear()
        elem.send_keys("ADMIN")
        elem.send_keys(Keys.RETURN)

        # check for error message
        try:
            driver.find_element_by_id("errmsg")
            # if error message exists, then close window and ask for new login info
            print "Incorrect username or password"
            driver.quit()
        except NoSuchElementException:
            # error message does not exist and the user has logged in
            print "Logged in\n"
            loggedIn = True
            driver.quit()
            return user, password

def login(user, password, threadTemp):
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : os.getcwd() +'\\'+ threadTemp}
    options.add_experimental_option("prefs", prefs)

    # logging in
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("http://sim.cps.k12.il.us/")

    # LOGIN PAGE
    print "\nSigning in"
    # username
    elem = driver.find_element_by_name("user")
    elem.clear()
    elem.send_keys(user)
    # password
    elem = driver.find_element_by_name("pass")
    elem.clear()
    elem.send_keys(password)
    # domain
    elem = driver.find_element_by_name("domn")
    elem.clear()
    elem.send_keys("ADMIN")
    elem.send_keys(Keys.RETURN)

    return driver

def scraperThread(n, user, password, prettylist, schoollist):
    windows = 0
    running = 0
    completed = 0
    failures = []
    threadTemp = tempfolder + str(n)

    driver = login(user, password, threadTemp)

    if not os.path.exists(threadTemp):
        os.makedirs(threadTemp)

    # work through schools and navigate through their respective pages
    for i in range(len(schoollist)):
        pretty = prettylist[i]
        selection = schoollist[i]
        # ROLE SELECTION
        print "Selecting " + pretty
        # navigates to role page
        driver.get("https://sim.cps.k12.il.us/PowerSchoolSMS/User/SwitchRole.aspx?Mode=SwitchRole&reset=true")
        # search schools for selection
        schoolsInputs = driver.find_elements_by_name("SelectedRole")

        if selection in schools:
            running += 1
            schoolIndex = schools.index(selection) - 1
            value = schoolsInputs[schoolIndex].get_attribute("value")
            # selects school
            driver.find_element_by_css_selector("input[type='radio'][value='"+value+"']").click()
            # click OK and submit
            driver.find_element_by_name("TP$QAID_cmd_ok").click()

            # REPORT SELECTION
            print "Selecting report"
            # navigate to report page
            driver.get("https://sim.cps.k12.il.us/PowerSchoolSMS/CustomReports/RunReport.aspx?type=school&reset=true")
            # select CPS_HI 176 report
            driver.find_element_by_id("QAID_RunRpt_5050").click()

            # REPORT OPTIONS
            print "Selecting report options"
            # switch to popout window
            time.sleep(2)
            driver.switch_to_window(driver.window_handles[running])
            try:
                # # select across school option
                driver.find_element_by_css_selector("input[type='radio'][value='Across School']").click()
                # # reveal output options
                driver.find_element_by_id("QAID_OutputSection_IMG").click()
                # select csv output
                selectOps = Select(driver.find_element_by_name("QAID_RadioFormatList"))
                selectOps.select_by_value('CommaSeparatedText')
                # run query
                driver.find_element_by_name("QAID_cmdSubmit").click()

                print "Outputting report\n"

                # Check for any windows that have downloaded reports
                # If the report has been downloaded close the window`
                for j in range(1,running+1):
                    driver.switch_to_window(driver.window_handles[j])
                    if "Completed" in driver.title:
                        time.sleep(2)
                        driver.close()
                        completed += 1
                        running -= 1
                        break

            except NoSuchElementException:
                print "Something is missing"
                driver.close()
                running -= 1
                failures.append(pretty)

            # If there are too many
            while(running >= windowLimit):
                for j in range(1,running+1):
                    driver.switch_to_window(driver.window_handles[j])
                    if "Completed" in driver.title:
                        # print "Too Many Windows => Closing Window"
                        time.sleep(2)
                        driver.close()
                        completed += 1
                        running -= 1
                        break

            # SWITCH BACK TO ORIGINAL WINDOW TO GENERATE MORE REPORTS
            driver.switch_to_window(driver.window_handles[0])
        else:
            print "School not found\n"
            failures.append(pretty)

    path = threadTemp + '\\'
    num_files = 0
    print 'Waiting for file(s)'
    while num_files != (len(schoollist) - len(failures)):
        filelist = [f for f in os.listdir(path)
                        if os.path.isfile(os.path.join(path,f))]
        num_files = len(filelist)

    print "All file(s) in thread " + str(n) + " downloaded"
    time.sleep(1)
    print "Closing windows for thread " + str(n)
    driver.quit()

def clean(folder, downloadTime):

    filelist = [f for f in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder,f))]
    # downloadTime = datetime.datetime.now().strftime('%m-%d-%y--%H-%M')

    for inputFile in filelist:
        # create name for output file
        if 'clean' in inputFile:
            continue

        inputFile = folder +  '\\' + inputFile
        outputFile = inputFile.split('.csv')[0] + '_clean.csv'

        # chop off first 15 lines (header junk)
        with open(inputFile, "r") as f:
            lines = f.readlines()
            total = len(lines)

        with open(inputFile, "r") as f, open(outputFile, "wb") as o:
            guy = reader(f)
            gal = writer(o)

            # header
            gal.writerow(["School", "Teacher", "Course Code", "Course Name", "Period", "Room", "Students", "Capacity"])
            i = 0

            try:
                for row in guy:
                    i+=1
                    # skip short rows
                    if len(row) < 32:
                        continue

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

                    if i == (total - 1):
                        break;
            except UnicodeDecodeError:
                print school

    filelist = [f for f in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder,f))]
    cleanFiles = []

    for files in filelist:
        if 'clean' in files:
            cleanFiles.append(files)


    mergeFile = folder + downloadTime + "mergeFile.csv"


    with open(mergeFile, "wb") as o:
        for cf in cleanFiles:
            gal = writer(o)

            with open(folder + '\\' + cf, "r") as f:
                guy = reader(f)
                for row in guy:
                    gal.writerow(row)


class sThread(threading.Thread):
    def __init__(self, threadID, user, password, prettylist, schoollist):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.user = user
        self.password = password
        self.prettylist = prettylist
        self.schoollist = schoollist

    def run(self):
        print "Starting " + str(self.threadID)
        scraperThread(self.threadID, self.user, self.password, self.prettylist,
                        self.schoollist)
        print "Exiting " + str(self.threadID)

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
