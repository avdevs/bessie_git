from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def user_type_required(allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.user_type in allowed_types:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator