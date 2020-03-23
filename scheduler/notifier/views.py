from django.shortcuts import render
from django.http import HttpResponse

import requests, json
from selenium import webdriver
from bs4 import BeautifulSoup

def index(request):
    return HttpResponse("Hello, world. You're at the notifier index.")

def scrape(request):
    # data = requests.get("https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php")
    # print(str(data.text), file=open("data.html", "w"))

    url = 'https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php'
    driver = webdriver.PhantomJS()#executable_path='~/Library/phantomjs-2.1.1-macosx/bin/phantomjs')
    driver.get(url)
    # print(driver.page_source)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    a = soup.find_all("table", class_="dailySchedule")
    print(a)
    # print(soup.prettify())

    return HttpResponse("hello")

scrape(None)
