from django.shortcuts import render, redirect
from .models import Employee 
from django.contrib.auth import authenticate,login,logout

from django.contrib import messages



def employee_list(request):

    search = request.GET.get('search')
    
    if search:
        
        employees = Employee.objects.filter(name__icontains=search)

    else : 
            
        employees = Employee.objects.all()

    return render(request, 'employee_list.html', {'employees': employees})


def add_employee(request):

    if request.method == 'POST':

        name = request.POST['name']
        email = request.POST['email']
        department = request.POST['department']
        salary = request.POST['salary']

        Employee.objects.create(
            name=name,
            email=email,
            department=department,
            salary=salary

        )

        messages.success(request,'Employee Added Successfully')

        return redirect('employee_list')
    
    return render(request, 'add_employee.html') 


def delete_employee(request, id):

    employee = Employee.objects.get(id=id)

    employee.delete()

    messages.success(request, 'Employee Deleted Successfully!')

    return redirect('employee_list')


def update_employee(request, id):

    employee = Employee.objects.get(id=id)

    if request.method == 'POST':
        employee.name = request.POST['name']
        employee.email = request.POST['email']
        employee.department = request.POST['department']
        employee.salary = request.POST['salary']

        employee.save()

        messages.success(request,'Employee Updated Successfully!')

        return redirect('employee_list')
    
    return render(request, 'update_employee.html', {'employee': employee})


def login_user(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('employee_list')

    return render(request, 'login.html')


def logout_user(request):
    
    logout(request)

    return redirect('login')