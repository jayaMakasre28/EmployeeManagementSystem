from django.shortcuts import render
from .models import * 
from django.contrib.auth.models import User
from .models import EmployeeDetail


# Create your views here.

def index(request):
    return render(request, 'index.html') 

def registration(request):
    error = ""
    
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        ecode = request.POST['employeecode']
        email = request.POST['emp_email']
        pswd = request.POST['emp_password']
        
        if User.objects.filter(username=email).exists():
            error = "exists"

        elif EmployeeDetail.objects.filter(empcode=ecode).exists():
            error = "empcode_exists"
    
        else:
            try:
                user = User.objects.create_user(
                    first_name=fname,
                    last_name=lname,
                    username=email,
                    password=pswd
                )
                EmployeeDetail.objects.create(
                    user=user,
                    empcode=ecode
                )
                error = "no"
            except Exception as e:
                print("ERROR:", e)
                error = "yes"

    return render(request, 'registration.html', {'error': error})

def emp_login(request):
    return render(request, 'emp_login.html')             
                
   