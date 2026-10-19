from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="ชื่อจริง", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ระบุชื่อจริง'}))
    last_name = forms.CharField(max_length=30, required=True, label="นามสกุล", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ระบุนามสกุล'}))
    email = forms.EmailField(required=True, label="อีเมล", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'รหัสผ่านอย่างน้อย 6 ตัวอักษร'}), label="รหัสผ่าน")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ยืนยันรหัสผ่าน'}), label="ยืนยันรหัสผ่าน")
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="ประเภทผู้ใช้งาน",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อผู้ใช้งาน (ตัวอักษรภาษาอังกฤษหรือตัวเลข)'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้งานแล้วในระบบ กรุณาใช้อีเมลอื่น")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("รหัสผ่านทั้งสองช่องไม่ตรงกัน")
            if len(password) < 6:
                raise forms.ValidationError("รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            role = self.cleaned_data.get('role', UserProfile.ROLE_CUSTOMER)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.role = role
            user_profile.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อผู้ใช้'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'รหัสผ่าน'}))


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="ชื่อจริง", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, label="นามสกุล", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label="อีเมล", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0812345678'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'แนะนำตัวสั้นๆ'}),
        }
