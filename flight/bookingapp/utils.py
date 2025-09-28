from django.shortcuts import redirect
from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('student_id'):  # check if logged in
            return redirect('bookingapp:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def redirect_if_logged_in(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('student_id'):  # already logged in
            return redirect('bookingapp:main')  # send them to home
        return view_func(request, *args, **kwargs)
    return wrapper
