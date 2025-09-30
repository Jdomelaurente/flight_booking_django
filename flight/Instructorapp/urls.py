from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    # ✅ Public routes - No login required
    path("register/", views.registerPage, name="register"),
    path("", views.loginPage, name="login"),
    
    # ✅ Logout - Login required
    path("logout/", login_required(views.logoutPage), name="logout"),

    # ✅ Dashboards - Login required (role checking done in views)
    path("dashboard/", login_required(views.dashboard), name="dashboard"),
    path('student-dashboard/', login_required(views.student_dashboard), name='student_dashboard'),
    path('admin-dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),

    # ✅ Table Class - Login required
    path('Create/', login_required(views.Cclass), name='Cclass'),

    # ✅ Class Edit and Delete - Login required
    path('class/edit/<int:id>/', login_required(views.EditClass), name='EditClass'),
    path('class/delete/<int:id>/', login_required(views.DeleteClass), name='DeleteClass'),

    # ✅ Create - Login required
    path('Createclass/', login_required(views.CreateClass), name='CreateClass'),
    path('Createsection/', login_required(views.Create_Section), name='Create_Section'),

    # ✅ Delete Excel row - Login required
    path("excel_row/<int:pk>/delete/", login_required(views.delete_excel_row), name="delete_excel_row"),

    # ✅ Edit excel row - Login required
    path("excel-row/<int:pk>/edit/", login_required(views.edit_student), name="Edit_Excel_Row"),

    # ✅ Section List - Login required
    path('Sectionlist/', login_required(views.Section_List), name='Section_List'),
    path("sections/<int:pk>/", login_required(views.section_detail), name="Section_Detail"),

    # ✅ Section Update and Delete - Login required
    path("sections/<int:pk>/update/", login_required(views.Update_section), name="Update_section"),
    path('sections/<int:id>/delete/', login_required(views.Delete_section), name='Delete_Section'),

    # ✅ Instructions/Book Flight - Login required
    path("book-flight/<int:section_id>/", login_required(views.book_flight), name="book_flight"),

    # ✅ Students - Login required
    path("sections/<int:pk>/add-students/", login_required(views.create_students), name="create_students"),
]