from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .models import Note, Bio, UserInfo
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator

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
                messages.success(request, "You are now logged in.")
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
    messages.success(request, 'Logout successful. See you next time.')
    return redirect('login')

def dashboard(request):
    #fetch the user's info
    user_info = UserInfo.objects.get(author=request.user)

    #get the latest activity
    latest_activity = user_info.recent_activity if user_info.recent_activity else "No recent activity."

    #get the notes uploaded by the user
    user_notes = Note.objects.filter(author=request.user)
    user_notes_count = user_notes.count()

    #fetch the last uploaded note
    last_uploaded_note = user_info.last_uploaded_note

    #prepare context data

    context = {
        'notes_count':user_notes_count,
        'total_downloads':user_info.total_downloads,
        'last_uploaded_note':user_info.last_uploaded_note,
        'recent_activity':latest_activity,
        'user_notes':user_notes,  #pass the user's notes for any additional usage
    }

    return render(request, 'notes/dashboard.html', context)

# def dashboard(request):
#     return render(request, 'notes/dashboard.html', )


def notes(request):
    notes = Note.objects.all().order_by('-upload_date')

    paginator = Paginator(notes, 16)  # Show 10 notes per page
    page_number = request.GET.get('page')
    notes = paginator.get_page(page_number)

    content = {
        'notes':notes,
    }
    return render(request, 'notes/notes.html', content)


def notification(request):
    return render(request, 'notes/notification.html')

@login_required
def myprofile(request):
    bio = Bio.objects.filter(author=request.user)

   
    if request.method == 'POST':
        first_name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        #update user's data
        user = request.user
        user.first_name = first_name
        user.email = email

        #update the password only if a new one is provided
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user) #keep the user logged in after the passsword change

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('myprofile')
    

    context = {
        'bios':bio,
    }
    
    return render(request, 'notes/myprofile.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
def update_bio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bio_text = data.get('bio')

            # Assuming you have a model to save the bio
            user_bio, created = Bio.objects.get_or_create(author=request.user)
            user_bio.bio = bio_text
            user_bio.save()

            return JsonResponse({'status': 'success', 'bio': bio_text})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

from django.utils import timezone
def mynotes(request):
    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        faculty = request.POST.get('faculty').upper()
        subject = request.POST.get('subject').capitalize()
        title = request.POST.get('title')
        file = request.FILES.get('file')
        

        # Check if we are updating an existing note
        if note_id:
            try:
                # Fetch the specific Note object for editing
                mynote = Note.objects.get(id=note_id, author=request.user)
                
                
                mynote.faculty = faculty
                mynote.subject = subject
                mynote.title = title

                if file:
                    mynote.file = file
                mynote.save()  # Save the updated note

                 # Update recent activity for edit
                user_info, created = UserInfo.objects.get_or_create(author=request.user)
                user_info.recent_activity = f"Edited note: '{mynote.title}' on {timezone.now().strftime('%Y-%m-%d')}"
                user_info.save()

                messages.success(request, 'Note updated successfully.')
            except Note.DoesNotExist:
                messages.error(request, 'Note does not exist.')
        else:
            # Create a new note if note_id is not present
            new_note = Note.objects.create(
                author=request.user,
                faculty=faculty,
                subject=subject,
                title=title,
                file=file
            )
            
            #update user info
            user_info, created = UserInfo.objects.get_or_create(author=request.user)
            user_info.notes_count += 1  #increament the notes count
            user_info.last_uploaded_note = new_note #set the last uploaded note
            user_info.recent_activity = f"Added note: '{new_note.title}' on '{timezone.now().strftime('%Y-%m-%d')}'"

            user_info.save()

            messages.success(request, 'File uploaded successfully.')
            return redirect('mynotes')
    
    # Retrieve notes for the logged-in user
    mynotes = Note.objects.filter(author=request.user).order_by('-upload_date')

    # Pagination
    paginator = Paginator(mynotes, 9)  # Show 10 notes per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    mynotes = paginator.get_page(page_number)  # Get the notes for the current page

    context = {
        'mynotes': mynotes,
    }

    return render(request, 'notes/mynotes.html', context)


def delete_note(request, note_id):
    note = Note.objects.get(author=request.user, id=note_id)
    user_info = UserInfo.objects.get(author=request.user)

    note.delete()
    user_info.recent_activity = f"Deleted note: '{note.title}' on {timezone.now().strftime('%Y-%m-%d')}"
    user_info.save()

    messages.success(request, 'Note deleted successfully.')
    return redirect('mynotes')


from django.utils import timezone
def download_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

     # Check if the note has a file before attempting to download
    if note.file:
        # Update UserInfo for download
        user_info, created = UserInfo.objects.get_or_create(author=request.user)
        user_info.total_downloads += 1  # Increment download count
        user_info.recent_activity = f'Downloaded note: "{note.title}" on {timezone.now().strftime('%Y-%m-%d')}'        
        user_info.save()  # Save changes

        response = HttpResponse(note.file, content_type='application/pdf')  # Adjust content type if needed
        response['Content-Disposition'] = f'attachment; filename="{note.file.name}"'
        return response
     
    else:
        return HttpResponse("File not found.", status=404)  # Handle the case where the file does not exist

from django.http import FileResponse
def note_preview(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    
    if note.file:
        response = FileResponse(note.file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="preview.pdf"'
        return response
    
    return redirect('notes')

    
def help_support(request):
    return render(request, 'notes/helpSupport.html')