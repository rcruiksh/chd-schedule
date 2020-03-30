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


def addConsultant(request):
    pass


# These are test functions
def dbTestDataCurrent(request):
    names = ["Alexandra", "Amanda", "Andrew", "Blake", "Cassidy", "Catherine", "Chandula", "Christopher", "Claire", "Denzel", "Erin", "Ethan", "Gavin", "Georgia", "Gillian", "Hanna", "Jamie", "Kathy", "Katy", "Keanu", "Kendra", "Kutay", "Maggie", "Marcela", "Richard", "Sarah", "Scott", "Shaelyn", "Shannon", "Sophie", "Taryn", "Will"]

    count = 0
    for name in names:
        c = Consultant(netlink="rcruiksh{}".format(count), email="rcruiksh{}@uvic.ca".format(count), first_name=name, last_name=name)
        c.save(using='default')
        count += 1

    print(Consultant.objects.using('default').all())

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
    for item in Consultant.objects.using('default').all():
        item.delete(using='default')
    # due to on delete cascade this should also empty out the shift table
    print(Consultant.objects.using('default').all())
    print(Shift.objects.using('default').all())
    return HttpResponse("hello")


def queryDB(request):
    c = Consultant.objects.using('default').get(first_name="Richard")
    s = Shift.objects.using('default').filter(consultant=c)
    for shift in s:
        print(shift.date)
        print(shift.start_time)
        print()
    # print(Consultant.objects.using('default').all())
    # print(Shift.objects.using('default').all())
    return HttpResponse("hello")
