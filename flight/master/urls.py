from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    #login Account
    path("register/", views.registerPage, name="register"),
    path("", views.loginPage, name="login"),
    path("logout/", views.logoutPage, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    #Table CLass
    path('Create/', views.Cclass, name='Cclass'),

    #Class Edit and Delete
    path('class/edit/<int:id>/', views.EditClass, name='EditClass'),
    path('class/delete/<int:id>/', views.DeleteClass, name='DeleteClass'),
    # urls.py

    #Create
    path('Createclass/', views.CreateClass, name='CreateClass'),

    path('Createsection/', views.Create_Section, name='Create_Section'),

    #Excel Import
    path("sections/<int:pk>/import_excel/", views.import_students_excel, name="import_students_excel"),
    
    # Delete Excel row
    path("excel_row/<int:pk>/delete/", views.delete_excel_row, name="delete_excel_row"),

    #edit excel row
        path("excel-row/<int:pk>/edit/", views.edit_student, name="Edit_Excel_Row"),

    #Section List
    path('Sectionlist/', views.Section_List, name='Section_List'),

    path("sections/<int:pk>/", views.section_detail, name="Section_Detail"),

    # Section Update and Delete
    path("sections/<int:pk>/update/", views.Update_section, name="Update_section"),
    path('sections/<int:id>/delete/', views.Delete_section, name='Delete_Section'),

    #Instructions
    # master/urls.py

    path("book-flight/<int:section_id>/", views.book_flight, name="book_flight"),






    # STUDENTS
    path("sections/<int:pk>/add-students/", views.create_students, name="create_students"),




]