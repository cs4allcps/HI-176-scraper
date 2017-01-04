from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from schools import schools
import getpass, os, sys, time, datetime, shutil

reportFile = None
downloadTime = datetime.datetime.now().strftime('%m-%d-%y--%H-%M')
folder = 'sim_downloads'
windowLimit = 5
tempfolder = 'temp_folder' + downloadTime
windowLimit = 5

# if folders do not exists, make them
if not os.path.exists(folder):
    os.makedirs(folder)

if not os.path.exists(tempfolder):
    os.makedirs(tempfolder)

# will be replaced with argparse soon
# -t : allows you to use a list of schools from a text file
# -wl: limit of windows that selenium can open
for i in range(len(sys.argv)):
    if sys.argv[i] == '-t':
        i+=1
        reportFile = sys.argv[i]

    elif sys.argv[i] == '-wl':
        i+=1
        windowLimit = int(sys.argv[i])

# set options for the webdriver
options = webdriver.ChromeOptions()
print  os.getcwd() + '\\' + tempfolder
prefs = {"download.default_directory" : os.getcwd() +'\\'+ tempfolder}
options.add_experimental_option("prefs", prefs)

# collect username and password
user = raw_input("USERNAME: ")
password = getpass.getpass("PASSWORD: ")
schoollist = []
prettylist = []
notfound = []
windows = 0
running = 0
completed = 0

# if no text file was provided, let the user select the schools they want
if not reportFile:
    print
    found = 0
    print "SCHOOL SEARCH"
    while not found:
        search = raw_input("Search: ")
        matches = [s for s in schools if search.lower() in s.lower()]
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
            found = 1
            print "Selected:",prettylist[0]
        elif int(selection) < 0 or int(selection) >= len(matches):
            print "Invalid choice number. Seach again."
        print

else:
    print "READING FROM SCHOOL LIST"
    with open(reportFile) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            school = lines[i]
            schoollist.append(lines[i].replace("\n", " - School View"))
            prettylist.append(lines[i].rstrip("\n"))

# create driver
driver = webdriver.Chrome(chrome_options=options)
driver.get("http://sim.cps.k12.il.us/")

# LOGIN PAGE
print "Signing in"
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
        # selects lane tech
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
        # select across school option
        driver.find_element_by_css_selector("input[type='radio'][value='Across School']").click()
        # reveal output options
        driver.find_element_by_id("QAID_OutputSection_IMG").click()
        # select csv output
        selectOps = Select(driver.find_element_by_name("QAID_RadioFormatList"))
        selectOps.select_by_value('TabSeparatedText')
        # run query
        driver.find_element_by_name("QAID_cmdSubmit").click()

        print "Outputting Report\n"

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
        notfound.append(selection)


path = 'temp_folder\\'
newpath = 'sim_downloads\\'
num_files = 0
filelist = []

print 'Waiting for file(s)'

while num_files != len(schoollist):
    filelist = [f for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path,f))]
    num_files = len(filelist)

print "All file(s) downloaded"
time.sleep(1)
filelist = [f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path,f))]
downloadTime = datetime.datetime.now().strftime('%m-%d-%y--%H-%M')
if reportFile:
    newfile = path + "merge_file "+downloadTime+".tsv"
    with open(newfile, 'wb') as newtsv:
        for oldfile in filelist:
            f = open(path + oldfile)
            for line in f:
                newtsv.write(line)
            f.close()
        newtsv.close()

    os.rename(newfile, newpath + "merge_file--"+downloadTime+".tsv")

for report in filelist:
    count = 0
    with open(path + report, 'rb') as tsvfile:
        for row in tsvfile:
            count += 1
            if count == 3:
                schoolName = row.rstrip().replace('"', '')
        tsvfile.close()
        if not schoolName:
            schoolName = "unknown"
    os.rename(path + report, newpath+schoolName+'--'+downloadTime+".tsv")




shutil.rmtree(path)
print "Files merged"
print "Closing Windows"
while len(driver.window_handles) > 1:
    driver.switch_to_window(driver.window_handles[1])
    driver.close()

driver.switch_to_window(driver.window_handles[0])
driver.close()
