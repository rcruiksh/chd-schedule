import requests, json
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape(request):
    # data = requests.get("https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php")
    # print(str(data.text), file=open("data.html", "w"))

    # This is being used as a headless browser, since the schedule html is built by a JS Function
    # Just performing a get will return the page source, but does not contain the schedule html.
    # using a headless browser executes that JS and allows us to retrieve the final rendered html.
    driver = webdriver.PhantomJS()#executable_path='~/Library/phantomjs-2.1.1-macosx/bin/phantomjs')
    url = 'https://helpdesk.uvic.ca/tools/index.php?next_page=schedule/viewAll.php'
    driver.get(url)
    # print(driver.page_source)

    # BeautifulSoup is a library built for parsing html
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    a = soup.find("table", class_="dailySchedule")
    # print(a)
    num_consultants = 0
    schedule = []
    consultants = []
    # count is how we keep track of which consultant a specific <td> belongs to
    count = 0
    # ignore_states = []

    while(1):
        a = a.find_next()
        # print(a.name)
        # all th entries are the names of consultants as column headings
        if a.name == "th":
            num_consultants += 1
            consultants.append(''.join(a.text.split())) # this line removes whitespace formatting
            # print(consultants)
            # print(len(consultants))

        elif a.name == "tr":
            count = 0

        elif a.name == "td":
            count += 1
            # print(a.attrs)
            try:
                if a['title'] != "" and "Preference" not in a['title'] and "Unavailable" not in a['title'] and "Class" not in a['title']:
                    print(consultants[count-2], a['title'])
                    # print(a['title'])
            except KeyError:
                pass


    # print(soup.prettify())

    # return HttpResponse("hello")

scrape(None)
