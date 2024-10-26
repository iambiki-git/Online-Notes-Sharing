from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Note

# Create your views here.
def index(request):
    return render(request, 'notes/index.html')

def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.email, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')

    return render(request, 'notes/login.html')

def registration(request):
    if request.method == 'POST':
        fullname = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms = request.POST.get('terms')

        if not terms:
            messages.error(request, 'You must agree to the Terms & Conditions.')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        #check if the email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')
        
        #create user
        user = User.objects.create_user(
            username = email,
            email = email, 
            password = password
        )
        user.first_name = fullname  #store the full nane in first_name field
        user.save()
        messages.success(request, 'Registration successful. You can now login.')
        return redirect('login')     

    return render(request, 'notes/registration.html')

def signout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def dashboard(request):
    section = request.GET.get('section', 'dashboard')
    context = {
        'section':section,
    }
    return render(request, 'notes/dashboard.html', context)

def notes(request):
    return render(request, 'notes/notes.html')

def notification(request):
    return render(request, 'notes/notification.html')

def myprofile(request):
    return render(request, 'notes/myprofile.html')

def mynotes(request):
    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        faculty = request.POST.get('faculty').upper()
        subject = request.POST.get('subject').capitalize()
        description = request.POST.get('description')
        file = request.FILES.get('file')

        # Check if we are updating an existing note
        if note_id:
            try:
                # Fetch the specific Note object for editing
                mynote = Note.objects.get(id=note_id, author=request.user)
                mynote.faculty = faculty
                mynote.subject = subject
                mynote.description = description
                if file:
                    mynote.file = file
                mynote.save()  # Save the updated note
                messages.success(request, 'Note updated successfully.')
            except Note.DoesNotExist:
                messages.error(request, 'Note does not exist.')
        else:
            # Create a new note if note_id is not present
            Note.objects.create(
                author=request.user,
                faculty=faculty,
                subject=subject,
                description=description,
                file=file
            )
            messages.success(request, 'File uploaded successfully.')
        
        return redirect('mynotes')
    
    # Retrieve notes for the logged-in user
    mynotes = Note.objects.filter(author=request.user).order_by('-upload_date')

    content = {
        'mynotes': mynotes,
    }

    return render(request, 'notes/mynotes.html', content)


        