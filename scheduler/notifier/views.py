from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

import requests, json, time, pytz, os
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event

from notifier.models import Consultant, Shift, PastShift


def index(request):
    return HttpResponse("Hello, world. You're at the notifier index.")


def download(request, netlink):
    try:
        consultant = Consultant.objects.get(netlink=netlink)
    except ObjectDoesNotExist:
        raise Http404
    # if os.path.exists(file_path):
    with open("notifier/" + str(netlink)+".ics", 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(str(netlink)+".ics")
        return response


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
        print(shift.year, shift.month, shift.day, shift.time_and_location)
    # print(Consultant.objects.using('default').all())
    # print(Shift.objects.using('default').all())
    return HttpResponse("hello")
