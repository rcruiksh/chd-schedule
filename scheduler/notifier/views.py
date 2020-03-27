from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import IntegrityError

import requests, json, time, calendar
from selenium import webdriver
from bs4 import BeautifulSoup

from notifier.models import Consultant, Shift
# from sqlite3 import IntegrityError

def index(request):
    return HttpResponse("Hello, world. You're at the notifier index.")

# def scrape(request):
#     # data = requests.get("https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php")
#     # print(str(data.text), file=open("data.html", "w"))
#
#     url = 'https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php'
#     driver = webdriver.PhantomJS()#executable_path='~/Library/phantomjs-2.1.1-macosx/bin/phantomjs')
#     driver.get(url)
#     # print(driver.page_source)
#
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     a = soup.find_all("table", class_="dailySchedule")
#     print(a)
#     # print(soup.prettify())
#
#     return HttpResponse("hello")
#
# scrape(None)

def parseShift(shift):
    shift = shift.split()
    start_time = shift[0]
    end_time = shift[2]
    location = shift[-1].strip('(').strip(')')
    return start_time, end_time, location

def compare(request):



    return HttpResponse("hello")

def scrape(request):

    # TODO: fix var names
    # TODO: compare past sched with current
    # TODO: database tinkering. Use db1 for past schedule, db2 for current schedule. Compare db2 to db1, notify consultants if different, overwrite db1 values with db2 values, repeat.
    # this function should only write to db2 - current schedule
    # TODO: API for adding/removing consultants. Verify by email?
    # TODO: superuser and admin app setup
    # TODO: test scripts
    # TODO: handle crash due to long page load -- return a value and retry x times?
    # TODO: general error handling. Don't email people if something breaks


    # This is being used as a headless browser, since the schedule html is built by a JS Function
    # Just performing a get will return the page source, but does not contain the schedule html.
    # using a headless browser executes that JS and allows us to retrieve the final rendered html.
    driver = webdriver.PhantomJS() # TODO: phontomJS is deprecated, replace with headless
    url = 'https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php'
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    first_time = True
    next_url = ""

    months = {
        "Jan.": "01",
        "Feb.": "02",
        "Mar.": "03",
        "Apr.": "04",
        "May.": "05",
        "Jun.": "06",
        "Jul.": "07",
        "Aug.": "08",
        "Sep.": "09",
        "Oct.": "10",
        "Nov.": "11",
        "Dec.": "12"
    }

    days = 14
    for i in range(days):
        if not first_time:
            driver.get(next_url)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

        # For each shift, we need to get the date, time, location, and consultant
        # Get the date from the header above the schedule table
        sched_header = soup.find("table", class_="schedule_control")
        date = sched_header.find_next("b")
        date = date.text
        date = date.split()[1:]
        date = '-'.join([date[2], months[date[0]], date[1][:-1]])

        next_url = soup.select("a#forward_arrow")
        next_url = next_url[0]["href"]

        sched = soup.find("table", class_="dailySchedule")

        # This variable maps each consultant to their column index in the format {index: "consultant"}
        col_mappings = dict()
        col_index = 0
        num_rows = 0

        count = 0
        # There are 32 relevant rows in the schedule table
        while(num_rows < 32):
            count += 1
            # print(count)
            # use BeautifulSoup to iterate through HTML elements. This steps through table rows and cells
            try:
                sched = sched.find_next()
            # if the page takes too long to load, sched will be NoneType, in which case we need to retry
            except AttributeError:
                return HttpResponse("timed out. please retry")
            # all th entries are the names of consultants as column headings
            if sched.name == "th":
                col_mappings[col_index] = ''.join(sched.text.split()) #removes all whitespace
                col_index += 1

            # this is a new row in the table, so reset the cell index
            elif sched.name == "tr":
                col_index = 0
                num_rows += 1

            # this is a new table cell
            elif sched.name == "td":
                try:
                    if sched['title'] != "" and "Preference" not in sched['title'] and "Unavailable" not in sched['title'] and "Class" not in sched['title']:
                        # consultants[col_index]["schedule"][date].add(sched['title'])
                        start_time, end_time, location = parseShift(sched['title'])
                        consultant = col_mappings[col_index]
                        consultant = Consultant.objects.using('current').get(first_name=consultant)#[0]
                        s = Shift(date=date, start_time=start_time, end_time=end_time, location=location, time_and_location=sched['title'], consultant=consultant)
                        s.save(using='current')
                except KeyError:
                    pass
                except IntegrityError:
                    pass
                col_index += 1

        first_time = False
    return HttpResponse("hello")

def dbTestData(request):

    names = ["Alexandra", "Amanda", "Andrew", "Blake", "Cassidy", "Catherine", "Chandula", "Christopher", "Claire", "Denzel", "Erin", "Ethan", "Gavin", "Georgia", "Gillian", "Hanna", "Jamie", "Kathy", "Katy", "Keanu", "Kendra", "Kutay", "Maggie", "Marcela", "Richard", "Sarah", "Scott", "Shaelyn", "Shannon", "Sophie", "Taryn", "Will"]

    count = 0
    for name in names:
        c = Consultant(netlink="rcruiksh{}".format(count), email="rcruiksh{}@uvic.ca".format(count), first_name=name, last_name=name)
        c.save(using='current')
        count += 1

    print(Consultant.objects.using('current').all())

    return HttpResponse("hello")

def clearDB(request):
    for item in Consultant.objects.using('current').all():
        item.delete(using='current')
    # due to on delete cascade this should also empty out the shift table
    print(Consultant.objects.using('current').all())
    print(Shift.objects.using('current').all())
    return HttpResponse("hello")

def queryDB(request):
    c = Consultant.objects.using('current').get(first_name="Richard")
    s = Shift.objects.using('current').filter(consultant=c)
    for shift in s:
        print(shift.date)
        print(shift.start_time)
        print()
    # print(Consultant.objects.using('current').all())
    # print(Shift.objects.using('current').all())
    return HttpResponse("hello")
