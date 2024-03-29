import requests, json, time
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape(consultants, days=1):
    # data = requests.get("https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php")
    # print(str(data.text), file=open("data.html", "w"))

    # TODO: fix var names
    # TODO: use django model to replace data structures
    # TODO: build schedule over multiple days
    # TODO: compare past sched with current
    # TODO: function for building sched first time vs not?

    # This is being used as a headless browser, since the schedule html is built by a JS Function
    # Just performing a get will return the page source, but does not contain the schedule html.
    # using a headless browser executes that JS and allows us to retrieve the final rendered html.
    driver = webdriver.PhantomJS() # TODO: phontomJS is deprecated, replace with headless
    url = 'https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php'
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    first_time = True
    next_url = ""

    for i in range(days):
        if not first_time:
            driver.get(next_url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

        sched_header = soup.find("table", class_="schedule_control")
        date = sched_header.find_next("b")
        date = date.text
        if not first_time:
            for index in consultants.keys():
                consultants[index]["schedule"][date] = set()

        next_url = soup.select("a#forward_arrow")
        next_url = next_url[0]["href"]

        sched = soup.find("table", class_="dailySchedule")

        num_rows = 0
        col_index = 0

        # There are 32 relevant rows in the schedule table
        while(num_rows < 32):
            # use BeautifulSoup to iterate through HTML elements. This steps through table rows and cells
            sched = sched.find_next()

            # all th entries are the names of consultants as column headings
            if sched.name == "th" and first_time:
                consultants[col_index] = dict()
                consultants[col_index]["name"] = ''.join(sched.text.split()) # this removes whitespace formatting
                consultants[col_index]["schedule"] = dict()
                consultants[col_index]["schedule"][date] = set()
                col_index += 1

            # this is a new row in the table, so reset the cell index
            elif sched.name == "tr":
                col_index = 0
                num_rows += 1

            # this is a new table cell
            elif sched.name == "td":
                try:
                    if sched['title'] != "" and "Preference" not in sched['title'] and "Unavailable" not in sched['title'] and "Class" not in sched['title']:
                        consultants[col_index]["schedule"][date].add(sched['title'])
                except KeyError:
                    pass
                col_index += 1

        first_time = False

    return consultants

consultants = dict()

consultants = scrape(consultants, days=14)
print(consultants[25])
