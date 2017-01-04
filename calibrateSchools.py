from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import getpass

loggedIn = False
options = webdriver.ChromeOptions()

# ATTEMT TO LOGIN
while not loggedIn:
    # collect username and password
    user = raw_input("USERNAME: ")
    password = getpass.getpass("PASSWORD: ")
    # create driver
    driver = webdriver.Chrome(chrome_options=options)
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

# navigate to role page
driver.get("https://sim.cps.k12.il.us/PowerSchoolSMS/User/SwitchRole.aspx?Mode=SwitchRole&reset=true")
#select schools
schools = driver.find_elements_by_class_name("last-col")
print "Reading schools"
for i in range(1,len(schools)):
    element = schools[i]
    schools[i] = element.text

del schools[0]
print "Closing window"
driver.quit()
print "Updating schools.py"
with open("schools.py", "w") as f:
    f.write("schools = " + str(schools))
    f.close()
