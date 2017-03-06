# HI-176-scraper
The HI-176-scraper is a python script that downloads HI 176 reports from CPS' SIM

# Running Instructions:
##Single School
To get the report for a single school, you can simply run

    $ python scraper.py

School options and further instructions will appear on the terminal

##Multiple Schools
To get multiple reports as well as a merged report containing the info from all of the reports, create a textfile with a list of the schools you want reports for (an example textfile has been provided).

To get the reports, run

    $ python scraper.py -t [textfile name] (-tc [thread count]) (-wl [window limit])

The program will run multiple threads with multiple download windows for the reports. The default number of threads is 2 but more can be run by using the -tc tag when calling scraper.py. The default number of windows is 5 windows per thread, but this can also be changed by using the -wl tag.

# Additional Info:
If schools.py is different from the list of schools on the SIM portal, use

    $ python calibrateSchools.py

to calibrate schools.py with the current list of schools.

The HI-176 reports will originally be downloaded in a non-readable format. If you have a folder of these unedited reports, use this command

    $ python cleanReports.py [folder name]

to clean and merge the files.

If you would like to gather reports for (nearly) all of the CPS high schools, use allCPSHS.txt as the text file for scraper.py. If you just want the CPS high schools with CS4All programs, use the file cs4allHS.txt with scraper.py.

scraperCore.py contains many of the basic functions used to interface with the CPS SIM via Selenium. These functions can be used for other future scrapers.

# Future Additions
- Add an option to use the Firefox webdriver instead of Chome webdriver
