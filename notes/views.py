from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'notes/index.html')

def login(request):
    return render(request, 'notes/login.html')

def registration(request):
    return render(request, 'notes/registration.html')