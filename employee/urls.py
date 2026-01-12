from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Employee Authentication
    path('login/', views.emp_login, name='emp_login'),
    path('signup/', views.emp_signup, name='emp_signup'),
    path('logout/', views.emp_logout, name='emp_logout'),

    # Employee Dashboard
    path('dashboard/', views.emp_dashboard, name='emp_dashboard'),

    # Employee Profile
    path('profile/', views.emp_profile, name='emp_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Attendance
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),

    # Admin Authentication
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Search & View Employee
    path('search-employees/', views.search_employees, name='search_employees'),
    path('employee/<int:user_id>/', views.view_employee_profile, name='view_employee_profile'),

    # Delete Employee
    path('admin/delete-employee/<int:user_id>/', views.delete_employee, name='delete_employee'),

    # admin dashboard
    path('delete-task/<int:id>/', views.delete_task, name='delete_task'),
    path(
    'delete-employee/<int:id>/',
    views.delete_employee,
    name='delete_employee'
),

]
