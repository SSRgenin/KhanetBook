from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import UserProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            role_name = user.profile.get_role_display()
            messages.success(request, f"ยินดีต้อนรับคุณ {user.username}! สมัครสมาชิกสำเร็จในบทบาท '{role_name}'")
            return redirect('book_list')
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อความแจ้งเตือนด้านล่าง")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                role_name = user.profile.get_role_display() if hasattr(user, 'profile') else 'ผู้ใช้งาน'
                messages.success(request, f"เข้าสู่ระบบสำเร็จ! สวัสดีคุณ {user.get_full_name() or user.username} ({role_name})")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('book_list')
        messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "คุณได้ออกจากระบบเรียบร้อยแล้ว")
    return redirect('book_list')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            form.save()
            messages.success(request, "อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว")
            return redirect('profile')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = ProfileUpdateForm(instance=profile, initial=initial_data)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile
    })
