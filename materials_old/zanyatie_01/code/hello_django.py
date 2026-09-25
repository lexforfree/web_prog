"""
Django Hello World Example
Basic view and URL configuration
"""

from django.http import HttpResponse
from django.urls import path
from datetime import datetime


def hello(request):
    """Simple hello world endpoint"""
    return HttpResponse("Hello, World!")


def about(request):
    """About page with student info"""
    html = """
    <h1>About Me</h1>
    <p>Name: [Your Name]</p>
    <p>Course: Web Programming</p>
    <p>University: BFU</p>
    """
    return HttpResponse(html)


def current_time(request):
    """Current time endpoint"""
    now = datetime.now()
    html = f"""
    <h1>Current Time</h1>
    <p>{now.strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    return HttpResponse(html)


# URL patterns
urlpatterns = [
    path('', hello, name='hello'),
    path('about/', about, name='about'),
    path('time/', current_time, name='time'),
]
