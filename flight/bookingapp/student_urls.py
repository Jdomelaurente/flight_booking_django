from django.urls import path
from . import views

app_name = "bookingapp"

urlpatterns = [
    path('h/', views.student_home, name="student_home"),
    path('h/act', views.student_lab, name="student_lab"),

]