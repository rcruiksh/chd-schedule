from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scrape', views.scrape, name='scrape'),
    path('populate', views.dbTestData, name='populate'),
    path('clear', views.clearDB, name='clear'),
    path('query', views.queryDB, name='query'),
]
