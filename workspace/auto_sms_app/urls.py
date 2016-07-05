from django.conf.urls import patterns, include, url
from . import views


urlpatterns =[
    
    url(r'^$', views.auto_sms, name="sms_app")
    
    ]