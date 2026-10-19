from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=None):
    """
    Decorator to check if logged-in user belongs to allowed roles (e.g. ['seller']).
    Superusers bypass role restrictions.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "กรุณาเข้าสู่ระบบก่อนทำรายการ")
                return redirect('login')

            # Superusers always have full access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check profile role
            user_profile = getattr(request.user, 'profile', None)
            if user_profile and user_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (เฉพาะผู้ขาย/แอดมินเท่านั้น)")
            return redirect('book_list')
        return _wrapped_view
    return decorator
