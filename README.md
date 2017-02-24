# HI-176-scraper
The HI-176-scraper is a python script that downloads HI 176 reports from CPS' SIM

# Running Instructions:
##Single School
To get the report for a single school, you can simply run

    $ python scraper3.py

School options and further instructions will appear on the terminal

##Multiple Schools
To get multiple reports as well as a merged report containing the info from all of the reports, create a textfile with a list of the schools you want reports for (an example textfile has been provided).

To get the reports, run

    $ python scraper.py -t [textfile name] (-wl [window limit]) (-tc [thread count])

The program will open multiple download windows for the reports. The thread count limits the number of instances of the scraper that will be run at once. The default number of threads is 2. The window limit is the maximum number of windows that can be opened per instance of the scraper. The default window limit is 5 windows.

# Additional Info:
If schools.py is different from the list of schools on the SIM portal, use

    $ python calibrateSchools.py

to calibrate schools.py with the current list of schools.

# Future Additions
- Add an option to use the Firefox webdriver instead of Chome webdriver
