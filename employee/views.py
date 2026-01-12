from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
import datetime

from .models import Profile, Task, Attendance


# =========================
# HOME
# =========================
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('emp_dashboard')
    return render(request, 'employee/home.html')


# =========================
# EMPLOYEE AUTHENTICATION
# =========================
def emp_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('emp_dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and not user.is_staff:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('emp_dashboard')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'employee/emp_login.html')


def emp_signup(request):
    if request.user.is_authenticated:
        return redirect('emp_dashboard')

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect('emp_signup')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        Profile.objects.create(user=user)
        login(request, user)
        return redirect('emp_dashboard')

    return render(request, 'employee/emp_signup.html')


def emp_logout(request):
    logout(request)
    return redirect('home')


# =========================
# ADMIN AUTHENTICATION
# =========================
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            messages.success(request, "Admin login successful")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, 'employee/admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# =========================
# ADMIN DASHBOARD
# =========================
def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    today = datetime.date.today()

    # ---------------- Employees ----------------
    employees = User.objects.filter(is_staff=False)

    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # ---------------- Assign Task ----------------
    if request.method == "POST":
        emp_ids = request.POST.getlist('employee')
        title = request.POST.get('title')

        if emp_ids and title:
            for emp_id in emp_ids:  
                user = get_object_or_404(User, id=emp_id)
                Task.objects.create(
                    user=user,
                    title=title,
                    status='Pending'
                )
            messages.success(request, "Task assigned successfully")

    total_employees = User.objects.filter(is_staff=False).count()        

    # ---------------- Tasks ----------------
    pending_tasks = Task.objects.filter(status='Pending')
    completed_tasks = Task.objects.filter(status='Completed')

    # total_tasks = task_list.count()

    # ---------------- Attendance ----------------
    attendance_today = Attendance.objects.filter(date=today)

    present_list = attendance_today.filter(status='Present')
    present_today = present_list.count()

    # absent users (important logic)
    # present_users = present_list.values_list('user_id', flat=True)
    absent_list = attendance_today.filter(status='Absent')
    absent_today = absent_list.count()

    marked_users = attendance_today.values_list('user_id', flat=True)
    not_marked = employees.exclude(id__in=marked_users)

    # ---------------- Context ----------------
    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,

        'employees': employees,
        'total_employees': total_employees,

        # 'task_list': task_list,
        # 'total_tasks': total_tasks,

        'present_today': present_today,
        'present_list': present_list,

        'absent_today': absent_today,
        'absent_list': absent_list,
    }

    return render(request, 'employee/admin_dashboard.html', context)

# =========================
# EMPLOYEE DASHBOARD
# =========================
@login_required(login_url='emp_login')
def emp_dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.status = "Completed"
        task.save()

    # Profile completion
    filled = 0
    total = 5
    for field in [profile.job_title, profile.education, profile.gender, profile.experience, profile.profile_photo]:
        if field:
            filled += 1
    completion = int((filled / total) * 100)

    # Today's attendance
    today = datetime.date.today()
    attendance = Attendance.objects.filter(user=request.user, date=today).first()

    # Employee tasks
    tasks = Task.objects.filter(user=request.user)

    return render(request, 'employee/emp_dashboard.html', {
        'profile': profile,
        'completion': completion,
        'attendance': attendance,
        'tasks': tasks
    })


# =========================
# PROFILE
# =========================
@login_required(login_url='emp_login')
def emp_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'employee/emp_profile.html', {
        'user': request.user,
        'profile': profile
    })


@login_required(login_url='emp_login')
def edit_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        profile.job_title = request.POST.get('job_title')
        profile.education = request.POST.get('education')
        profile.gender = request.POST.get('gender')
        profile.experience = request.POST.get('experience')

        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']

        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect('emp_profile')

    return render(request, 'employee/edit_profile.html', {
        'user': user,
        'profile': profile
    })


# =========================
# ATTENDANCE
# =========================
@login_required(login_url='emp_login')
@require_POST
def mark_attendance(request):
    if request.method == "POST":
        status = request.POST.get('status')
        today = datetime.date.today()

    
    Attendance.objects.get_or_create(
    user=request.user, 
    date=today, 
    status=status
    )
    messages.success(request, "Attendance marked")
    return redirect('emp_dashboard')


# =========================
# SEARCH & VIEW EMPLOYEE
# =========================
@login_required(login_url='emp_login')
def search_employees(request):
    query = request.GET.get('q')
    employees = []
    if query:
        employees = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)
    return render(request, 'employee/search_employees.html', {
        'employees': employees,
        'query': query
    })


@login_required(login_url='emp_login')
def view_employee_profile(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user_profile)
    return render(request, 'employee/view_employee_profile.html', {
        'user_profile': user_profile,
        'profile': profile
    })


# =========================
# DELETE EMPLOYEE
# =========================
@user_passes_test(is_admin, login_url='admin_login')
def delete_employee(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete superuser")
        return redirect('admin_dashboard')
    user.delete()
    messages.success(request, "Employee deleted successfully")
    return redirect('admin_dashboard')



@user_passes_test(is_admin)
def delete_task(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    messages.success(request, "Task deleted")
    return redirect('admin_dashboard')



@user_passes_test(is_admin)
def delete_employee(request, id):
    employee = get_object_or_404(User, id=id, is_staff=False)
    employee.delete()
    messages.success(request, "Employee deleted successfully")
    return redirect('admin_dashboard')
