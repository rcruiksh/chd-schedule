from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('scrape', views.scrape, name='scrape'),
    path('populateCurrent', views.dbTestDataCurrent, name='populateCurrent'),
    # path('populatePast', views.dbTestDataPast, name='populatePast'),
    path('clear', views.clearDB, name='clear'),
    path('query', views.queryDB, name='query'),
    # path('compare', views.compare, name='compare'),
    # path('cal', views.generateCalendar, name='cal'),
    path('schedule/<str:netlink>', views.download, name='download'),
]
