from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.core.paginator import Paginator

from django.db.models import Avg, Max, Count

from django.http import HttpResponse

from .models import Employee

import csv


# =========================
# HOME PAGE
# =========================

def home(request):

    return render(request, 'home.html')


# =========================
# EMPLOYEE LIST
# =========================

@login_required
def employee_list(request):

    search = request.GET.get('search')

    # Search Logic

    if search:

        employees = Employee.objects.filter(
            name__icontains=search
        ).order_by('id')

    else:

        employees = Employee.objects.all().order_by('id')

    # Pagination

    paginator = Paginator(employees, 5)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {

        'page_obj': page_obj,

        'search': search

    }

    return render(
        request,
        'employee_list.html',
        context
    )


# =========================
# ADD EMPLOYEE
# =========================

@login_required
def add_employee(request):

    # Only admin/staff can add employees

    if not request.user.is_staff:

        messages.error(
            request,
            'You are not allowed to add employees.'
        )

        return redirect('employee_list')

    if request.method == 'POST':

        name = request.POST.get('name')

        email = request.POST.get('email')

        department = request.POST.get('department')

        salary = request.POST.get('salary') or 0

        image = request.FILES.get('image')

        Employee.objects.create(

            name=name,

            email=email,

            department=department,

            salary=salary,

            image=image

        )

        messages.success(
            request,
            'Employee Added Successfully!'
        )

        return redirect('employee_list')

    return render(request, 'add_employee.html')


# =========================
# UPDATE EMPLOYEE
# =========================

@login_required
def update_employee(request, id):

    # Only admin/staff can update employees

    if not request.user.is_staff:

        messages.error(
            request,
            'You are not allowed to update employees.'
        )

        return redirect('employee_list')

    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':

        employee.name = request.POST.get('name')

        employee.email = request.POST.get('email')

        employee.department = request.POST.get('department')

        employee.salary = request.POST.get('salary') or 0

        # Optional image update

        image = request.FILES.get('image')

        if image:

            employee.image = image

        employee.save()

        messages.success(
            request,
            'Employee Updated Successfully!'
        )

        return redirect('employee_list')

    context = {

        'employee': employee

    }

    return render(
        request,
        'update_employee.html',
        context
    )


# =========================
# DELETE EMPLOYEE
# =========================

@login_required
def delete_employee(request, id):

    # Only admin/staff can delete employees

    if not request.user.is_staff:

        messages.error(
            request,
            'You are not allowed to delete employees.'
        )

        return redirect('employee_list')

    employee = get_object_or_404(Employee, id=id)

    employee.delete()

    messages.success(
        request,
        'Employee Deleted Successfully!'
    )

    return redirect('employee_list')


# =========================
# EMPLOYEE DETAIL PAGE
# =========================

@login_required
def employee_detail(request, id):

    employee = get_object_or_404(Employee, id=id)

    context = {

        'employee': employee

    }

    return render(
        request,
        'employee_detail.html',
        context
    )


# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):

    # Dashboard Cards

    total_employees = Employee.objects.count()

    total_departments = Employee.objects.values(
        'department'
    ).distinct().count()

    highest_salary = Employee.objects.aggregate(
        highest=Max('salary')
    )

    average_salary = Employee.objects.aggregate(
        average=Avg('salary')
    )

    # Chart Data

    department_data = Employee.objects.values(
        'department'
    ).annotate(
        total=Count('department')
    )

    context = {

        'total_employees': total_employees,

        'total_departments': total_departments,

        'highest_salary': highest_salary['highest'],

        'average_salary': average_salary['average'],

        'department_names': [

            x['department']

            for x in department_data

        ],

        'department_counts': [

            x['total']

            for x in department_data

        ]

    }

    return render(
        request,
        'dashboard.html',
        context
    )


# =========================
# EXPORT CSV
# =========================

@login_required
def export_csv(request):

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="employees.csv"'

    writer = csv.writer(response)

    # Column Names

    writer.writerow([

        'ID',
        'Name',
        'Email',
        'Department',
        'Salary'

    ])

    employees = Employee.objects.all()

    # Employee Data

    for emp in employees:

        writer.writerow([

            emp.id,

            emp.name,

            emp.email,

            emp.department,

            emp.salary

        ])

    return response


# =========================
# LOGIN
# =========================

def login_user(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(

            request,

            username=username,

            password=password

        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                'Login Successful!'
            )

            return redirect('employee_list')

        else:

            messages.error(
                request,
                'Invalid Username or Password'
            )

    return render(request, 'login.html')


# =========================
# LOGOUT
# =========================

def logout_user(request):

    logout(request)

    messages.success(
        request,
        'Logout Successful!'
    )

    return redirect('/login/')


# =========================
# SIGNUP
# =========================

def signup_page(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        confirm_password = request.POST.get(
            'confirm_password'
        )

        # Password Match Validation

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match'
            )

            return redirect('/signup/')

        # Username Already Exists

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists'
            )

            return redirect('/signup/')

        # Create User

        User.objects.create_user(

            username=username,

            email=email,

            password=password

        )

        messages.success(
            request,
            'Account Created Successfully!'
        )

        return redirect('/login/')

    return render(request, 'signup.html')