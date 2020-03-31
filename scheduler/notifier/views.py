from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.core.mail import send_mail

import requests, json, time, pytz, os
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event

from notifier.models import Consultant, Shift, PastShift


def index(request):
    return HttpResponse("Hello, world. You're at the notifier index.")


def generateCalendar(request):
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
            # event.add('priority', 5)

            cal.add_component(event)

    f = open('example.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

    return HttpResponse("hello")


# These are test functions
def dbTestDataCurrent(request):
    names = ["Alexandra", "Amanda", "Andrew", "Blake", "Cassidy", "Catherine", "Chandula", "Christopher", "Claire", "Denzel", "Erin", "Ethan", "Gavin", "Georgia", "Gillian", "Hanna", "Jamie", "Kathy", "Katy", "Keanu", "Kendra", "Kutay", "Maggie", "Marcela", "Richard", "Sarah", "Scott", "Shaelyn", "Shannon", "Sophie", "Taryn", "Will"]

    count = 0
    for name in names:
        c = Consultant(netlink="rcruiksh{}".format(count), email="rcruiksh{}@uvic.ca".format(count), first_name=name, last_name=name)
        c.save()
        count += 1

    print(Consultant.objects.using('default').all())

    return HttpResponse("hello")


def clearDB(request):
    for item in Consultant.objects.all():
        item.delete()
    # due to on delete cascade this should also empty out the shift table
    print(Consultant.objects.all())
    print(Shift.objects.all())
    print(PastShift.objects.all())
    return HttpResponse("hello")


def queryDB(request):
    c = Consultant.objects.get(first_name="Richard")
    s = Shift.objects.filter(consultant=c)
    for shift in s:
        print(shift.date)
        print(shift.start)
        print()
    # print(Consultant.objects.using('default').all())
    # print(Shift.objects.using('default').all())
    return HttpResponse("hello")
