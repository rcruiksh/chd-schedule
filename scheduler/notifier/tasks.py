from celery import task
from celery import shared_task

from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.forms.models import model_to_dict

import json, time, os, pytz
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from bs4 import BeautifulSoup
from datetime import datetime

from notifier.models import Consultant, Shift, PastShift


'''SHIFT CHANGE NOTIFICATION'''
def parseShift(shift):
    # 8:30 - 10:30 (Working at HSD lab)
    shift = shift.split()
    location = (' ').join(shift[3:]).strip('(').strip(')')
    start_time = shift[0].split(":")
    start_hour = int(start_time[0])
    start_min = int(start_time[1])
    end_time = shift[2].split(":")
    end_hour = int(end_time[0])
    end_min = int(end_time[1])
    return start_hour, start_min, end_hour, end_min, location


def scrape():
    # start with a clean slate in the database
    for item in Shift.objects.all():
        item.delete()

    # This is being used as a headless browser, since the schedule html is built by a JS Function
    # Just performing a get will return the page source, but does not contain the schedule html.
    # using a headless browser executes that JS and allows us to retrieve the final rendered html.
    # driver = webdriver.PhantomJS() # TODO: phontomJS is deprecated, replace with headless
    options = FirefoxOptions()
    options.add_argument('--headless')
    binary = FirefoxBinary('/usr/bin/firefox')
    driver = webdriver.Firefox(firefox_binary=binary, firefox_options=options)

    url = 'https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php'
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    first_time = True
    next_url = ""

    months = {
        "Jan.": "1",
        "Feb.": "2",
        "Mar.": "3",
        "Apr.": "4",
        "May.": "5",
        "Jun.": "6",
        "Jul.": "7",
        "Aug.": "8",
        "Sep.": "9",
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
        year = int(date[2])
        month = int(months[date[0]])
        day = int(date[1][:-1])

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
                    if sched['title'] != "" and "Preference" not in sched['title'] and "Unavailable" not in sched['title'] and "Class" not in sched['title'] and "Exam" not in sched['title']:
                        # consultants[col_index]["schedule"][date].add(sched['title'])
                        start_hour, start_min, end_hour, end_min, location = parseShift(sched['title'])
                        consultant = col_mappings[col_index]
                        consultant = Consultant.objects.get(first_name=consultant)#[0]
                        s = Shift(year=year, month=month, day=day, start_hour=start_hour, start_min=start_min, end_hour=end_hour, end_min=end_min, location=location, time_and_location=sched['title'], consultant=consultant)
                        s.save()
                except KeyError: # if the sched doesn't have a 'title' attribute
                    pass
                except IntegrityError: # if the shift already exists in db, don't add it again
                    pass
                except ObjectDoesNotExist: # if the consultant hasn't been added to the db yet, don't build their schedule
                    pass
                col_index += 1

        first_time = False
    return 1


# return True if shifts are same, false otherwise
def compareShifts(shift1, shift2):
    shift1 = model_to_dict(shift1)
    shift2 = model_to_dict(shift2)
    match = True
    for key in shift1.keys():
        if shift1[key] != shift2[key] and key != 'id':
            match = False
    return match


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
@task(name='scrape_and_notify')
def scrapeAndNotify():
    print("scrape and notify")
    # start with a clean slate in the past database
    for item in PastShift.objects.all():
        item.delete()

    # overwrite past data with what's in current
    for item in Shift.objects.all():
        duplicate = PastShift(
            year=item.year,
            month=item.month,
            day=item.day,
            start_hour=item.start_hour,
            start_min=item.start_min,
            end_hour=item.end_hour,
            end_min=item.end_min,
            location=item.location,
            time_and_location=item.time_and_location,
            consultant=Consultant.objects.get(netlink=item.consultant.netlink)
        )
        duplicate.save()

    # refresh current data
    attempts = 0
    result = 0
    while (result != 1 and attempts < 10):
        result = scrape()
        attempts += 1

    # if scrape did not succeed after 10 attempts, raise an alert?
    if result == 0:
        pass #TODO implement this

    consultants = Consultant.objects.all()

    for consultant in consultants:
        current_shifts = Shift.objects.filter(consultant=consultant)
        current_shifts = list(current_shifts)

        past_shifts = PastShift.objects.filter(consultant=consultant)
        past_shifts = list(past_shifts)

        removed, added = findDifferences(past_shifts, current_shifts)
        removed = [str(entry) for entry in removed]
        added = [str(entry) for entry in added]

        if len(removed) != 0 or len(added) != 0:
            print('''Hi {},\nYour schedule has been updated.\n\nRemoved shifts:\n{}\n\nAdded shifts:\n{}\n\nPlease email chdsuper if you have any questions.\n\nRegards,\nSchedule Notification Bot'''.format(consultant.first_name, '\n'.join(removed), '\n'.join(added)))
            # send_mail(
            #     'Your Computer Help Desk schedule has been changed',
            #     '''Hi {},\nYour schedule has been updated.\n\nRemoved shifts:\n{}\n\nAdded shifts:\n{}\n\nPlease email chdsuper if you have any questions.\n\nRegards,\nSchedule Notification Bot'''.format(consultant.first_name, '\n'.join(removed), '\n'.join(added)),
            #     'chdschdedule@uvic.ca',
            #     ['{}'.format(consultant.email)],
            #     fail_silently=False,
            # )
    return

'''ICAL GENERATION'''
@task(name='ical_generation')
def generateCalendar(request):
    print("ical generation")
    tz = pytz.timezone(os.environ['TZ'])

    for consultant in Consultant.objects.all():

        cal = Calendar()
        # required to be compliant
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        shifts = Shift.objects.filter(consultant=consultant)
        for shift in shifts:
            event = Event()
            event.add('summary', str(shift.location))
            dtstart = datetime(shift.year,shift.month,shift.day,shift.start_hour,shift.start_min,0,tzinfo=tz)
            event.add('dtstart', dtstart)
            event.add('dtend', datetime(shift.year,shift.month,shift.day,shift.end_hour,shift.end_min,0,tzinfo=tz))
            event.add('dtstamp', datetime(shift.year,shift.month,shift.day,0,0,0,tzinfo=tz))
            event['uid'] = dtstart.isoformat() + shift.location + shift.consultant.netlink
            cal.add_component(event)

        f = open('notifier/{}.ics'.format(consultant.netlink), 'wb')
        f.write(cal.to_ical())
        f.close()

    return HttpResponse("hello")
