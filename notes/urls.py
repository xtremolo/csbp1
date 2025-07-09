from django.urls import path
from . import views

urlpatterns = [
#    path('', views.indexView, name='index'),
    path('', views.addView, name='add'),
    path('add/', views.addView, name='add'),
    path('erase/', views.eraseView, name='erase'),
    ###
    ### - FLAW 5 - Sensitive Data Exposure
    ###
    path('all/', views.allView, name='all'),
]
