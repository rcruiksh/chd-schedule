from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.core.mail import send_mail

import requests, json, time, calendar
from selenium import webdriver
from bs4 import BeautifulSoup

from notifier.models import Consultant, Shift


def index(request):
    return HttpResponse("Hello, world. You're at the notifier index.")


def parseShift(shift):
    shift = shift.split()
    start_time = shift[0]
    end_time = shift[2]
    location = shift[-1].strip('(').strip(')')
    return start_time, end_time, location


def scrape():

    # TODO: fix var names
    # TODO: API for adding/removing consultants. Verify by email?
    # TODO: superuser and admin app setup
    # TODO: test scripts
    # TODO: handle crash due to long page load -- return a value and retry x times?
    # TODO: general error handling. Don't email people if something breaks
    # TODO: scheduling (with celery?)
    # TODO: email notifications
    # TODO: testing with actual changed schedule - do emails get sent?
    # TODO: dockerize it?

    # start with a clean slate in the database
    for item in Shift.objects.using('current').all():
        item.delete(using='current')

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

        # There are 32 relevant rows in the schedule table (one for every 30 mins from 8am-11pm plus one for the header)
        while (num_rows < 32):
            # use BeautifulSoup to iterate through HTML elements. This steps through table rows and cells
            try:
                sched = sched.find_next()
            # if the page takes too long to load, sched will be NoneType, in which case we need to retry
            except AttributeError:
                return 0

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
    return 1


# return True if shifts are same, false otherwise
def compareShifts(shift1, shift2):
    if shift1.date == shift2.date and shift1.time_and_location == shift2.time_and_location:
        return True
    return False


def findDifferences(past_shifts, current_shifts):
    i = 0
    j = 0
    while i < len(past_shifts):
        # match_flag = False
        while j < len(current_shifts):
            if compareShifts(past_shifts[i], current_shifts[j]):
                past_shifts.remove(past_shifts[i])
                current_shifts.remove(current_shifts[j])
                i -= 1
                break
            j += 1
        i += 1

    return past_shifts, current_shifts


# overwrite past data with current data, then refresh current data, then compare
def compare(request):
    # start with a clean slate in the past database
    for item in Shift.objects.using('past').all():
        item.delete(using='past')

    # overwrite past data with what's in current
    for item in Shift.objects.using('current').all():
        duplicate = Shift(
            date=item.date,
            start_time=item.start_time,
            end_time=item.end_time,
            location=item.location,
            time_and_location=item.time_and_location,
            consultant=Consultant.objects.using('past').get(netlink=item.consultant.netlink)
        )
        duplicate.save(using='past')

    # refresh current data
    attempts = 0
    result = 0
    while (result != 1 and attempts < 10):
        result = scrape()
        attempts += 1

    # if scrape did not succeed after 10 attempts, raise an alert?
    if result == 0:
        pass #TODO implement this

    current_consultants = Consultant.objects.using('current').all()

    for consultant in current_consultants:
        current_shifts = Shift.objects.using('current').filter(consultant=consultant)
        current_shifts = list(current_shifts)

        past_consultant = Consultant.objects.using('past').get(netlink=consultant.netlink)
        past_shifts = Shift.objects.using('past').filter(consultant=past_consultant)
        past_shifts = list(past_shifts)

        removed, added = findDifferences(past_shifts, current_shifts)
        # print('\n'.join(removed))

        # print('''Hi {},\nYour schedule has been updated.\n\nRemoved shifts: {}\n\nAdded shifts: {}\n\nPlease email chdsuper if you have any questions.\n\nRegards\nSchedule Notification Bot'''.format(consultant.first_name, '\n'.join(removed), '\n'.join(added)))

        if len(removed) != 0 or len(added) != 0:
            send_mail(
                'Your Computer Help Desk schedule has been changed',
                '''Hi {},\nYour schedule has been updated.\n\nRemoved shifts:\n{}\n\nAdded shifts:\n{}\n\nPlease email chdsuper if you have any questions.\n\nRegards\nSchedule Notification Bot'''.format(consultant.first_name, '\n'.join(removed), '\n'.join(added)),
                'chdschdedule@uvic.ca',
                ['{}'.format(consultant.email)],
                fail_silently=False,
            )

    return HttpResponse("hello")


def dbTestDataCurrent(request):
    names = ["Alexandra", "Amanda", "Andrew", "Blake", "Cassidy", "Catherine", "Chandula", "Christopher", "Claire", "Denzel", "Erin", "Ethan", "Gavin", "Georgia", "Gillian", "Hanna", "Jamie", "Kathy", "Katy", "Keanu", "Kendra", "Kutay", "Maggie", "Marcela", "Richard", "Sarah", "Scott", "Shaelyn", "Shannon", "Sophie", "Taryn", "Will"]

    count = 0
    for name in names:
        c = Consultant(netlink="rcruiksh{}".format(count), email="rcruiksh{}@uvic.ca".format(count), first_name=name, last_name=name)
        c.save(using='current')
        count += 1

    print(Consultant.objects.using('current').all())

    return HttpResponse("hello")

def dbTestDataPast(request):
    names = ["Alexandra", "Amanda", "Andrew", "Blake", "Cassidy", "Catherine", "Chandula", "Christopher", "Claire", "Denzel", "Erin", "Ethan", "Gavin", "Georgia", "Gillian", "Hanna", "Jamie", "Kathy", "Katy", "Keanu", "Kendra", "Kutay", "Maggie", "Marcela", "Richard", "Sarah", "Scott", "Shaelyn", "Shannon", "Sophie", "Taryn", "Will"]

    count = 0
    for name in names:
        c = Consultant(netlink="rcruiksh{}".format(count), email="rcruiksh{}@uvic.ca".format(count), first_name=name, last_name=name)
        c.save(using='past')
        count += 1

    print(Consultant.objects.using('past').all())

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
