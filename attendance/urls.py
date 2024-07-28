# attendance/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload_employee/', views.upload_employee, name='upload_employee'),
    path('start_attendance/', views.start_attendance, name='start_attendance'),
    path('stop_attendance/', views.stop_attendance, name='stop_attendance'),
    path('mark_latecomers/', views.mark_latecomers, name='mark_latecomers'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('video_stream/', views.video_stream, name='video_stream'),
    path('get_current_attendees/', views.get_current_attendees, name='get_current_attendees'),
]
