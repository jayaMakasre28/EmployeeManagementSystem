from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('employees/', views.employee_list, name='employee_list'),

    path('add/', views.add_employee, name='add_employee'),

    path('update/<int:id>/', views.update_employee, name='update_employee'),

    path('delete/<int:id>/', views.delete_employee, name='delete_employee'),

    path('login/', views.login_user, name='login'),

    path('logout/', views.logout_user, name='logout'),

    path('dashboard/', views.dashboard,name='dashboard'),

    path('export-csv/', views.export_csv, name='export_csv'),

    path('employee/<int:id>/', views.employee_detail, name='employee_detail'),

    path('signup/', views.signup_page, name='signup'),
]