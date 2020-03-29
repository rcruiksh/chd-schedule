from celery import task
from celery import shared_task
# We can have either registered task
@task(name='scrape_and_notify')
def scrapeAndNotify():
    print("YOOOOO")
     # Magic happens here ...
