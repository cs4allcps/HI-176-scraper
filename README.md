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

    $ python scraper.py -t [textfile name] (-wl [window limit])

The program will open multiple download windows for the reports, and the window limit is the number of download windows that can be open at once. The default is 5 windows.

# Future Additions
- Threading: threading will hopefully increase the efficiency of the downloading/scraping process
- Add an option to use the Firefox webdriver instead of Chome webdriver
- Add functionality to update schools.py
