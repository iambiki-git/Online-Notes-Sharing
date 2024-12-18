from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .models import Note, Bio, UserInfo, Feedback, NoteDownload
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    testimonials = Feedback.objects.all()
    context = {
        'testimonials':testimonials,
    } 
    return render(request, 'notes/index.html', context)

def signin(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.email, password=password)

            if user is not None:
                login(request, user)

                #set the session to expire when the browser is closed if not "Remember Me"
                if remember_me:
                    request.session.set_expiry(86400) #set the session expiry to 2 weeks
                else:
                    request.session.set_expiry(0) #session expires when the browser is closed

                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')

    return render(request, 'notes/login.html')

def registration(request):
    if request.user.is_authenticated:
        return redirect('index')
    
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

        #create user_info instance for the new user
        UserInfo.objects.create(author=user)

        messages.success(request, 'Welcome to the community! Dive in and start exploring all the resources waiting for you.')
        return redirect('login')     

    return render(request, 'notes/registration.html')

def signout(request):
    logout(request)
    messages.success(request, 'Logout successful. See you next time.')
    return redirect('login')

@login_required
def dashboard(request):
    
    #fetch the user's info
    user_info = UserInfo.objects.get(author=request.user)
    most_downloaded_note = Note.objects.order_by('-downloads').first()
    if most_downloaded_note and most_downloaded_note.downloads > 0:
        title = most_downloaded_note.title
        downloads_count = most_downloaded_note.downloads
    else:
        title = None
        downloads_count = 0 

    #get the latest activity
    latest_activity = user_info.recent_activity if user_info.recent_activity else "None"

    if request.user.is_superuser:
        user_notes = Note.objects.all()
        user_notes_count = user_notes.count()
    else:
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
        'most_downloaded_note_title':title,
        'most_downloaded_note_downloads_count':downloads_count,
    }

    return render(request, 'notes/dashboard.html', context)

# from datetime import timedelta
# def notes(request):
#     notes = Note.objects.all().order_by('-upload_date')
#     faculties = Note.objects.values_list('faculty', flat=True).distinct()  #get unique faculty names

#     # Initialize recommended_notes
#     recommended_notes = Note.objects.none()  # Use an empty QuerySet as the default

#     # Determine the cutoff date (30 days ago)
#     some_cutoff_date = timezone.now() - timedelta(days=30)


#     #if user is new (no downloads yet), show all notes
#     if NoteDownload.objects.filter(user=request.user).exists():
#         recommended_notes = recommended_notes(request.user)
#     else:
#         recommended_notes = Note.objects.all().order_by('-upload_date')


#     paginator = Paginator(notes, 16)  # Show 10 notes per page
#     page_number = request.GET.get('page')
#     notes = paginator.get_page(page_number)

#     content = {
#         'notes':notes,
#         'faculties':faculties,
#         'recommended_notes':recommended_notes,
#         'some_cutoff_date': some_cutoff_date,
#     }
#     return render(request, 'notes/notes.html', content)


# from django.db.models import Count
# def notes_recommended(user):
#     # Get the notes downloaded by the user
#     user_downloads = NoteDownload.objects.filter(user=user).values_list('note', flat=True)
    
#     # Find the most downloaded notes by other users
#     recommended_notes = NoteDownload.objects.exclude(user=user).values('note').annotate(download_count=Count('note')).order_by('-download_count')[:5]  # Adjust the number as needed

#     # Get the corresponding Note objects
#     return Note.objects.filter(id__in=[note['note'] for note in recommended_notes])

from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Note, NoteDownload  # Ensure you import your models
from django.db.models import Count
from .recommendation import recommend_notes


def notes(request):
    notes = Note.objects.all().order_by('-upload_date')
    faculties = Note.objects.values_list('faculty', flat=True).distinct()  # Get unique faculty names

    # Initialize recommended_notes
    recommended_notes_queryset = Note.objects.none()  # Use an empty QuerySet as the default

    # Determine the cutoff date (30 days ago)
    some_cutoff_date = timezone.now() - timedelta(days=1)
    print(some_cutoff_date)

    # Check if the user has downloaded notes
    if request.user.is_authenticated and NoteDownload.objects.filter(user=request.user).exists():
        if request.user.date_joined < some_cutoff_date:  # User is older than 1 day
            recommended_notes_queryset = recommend_notes(request.user)  # Call your recommendation function
            # print(recommended_notes_queryset)
        else:
            recommended_notes_queryset = Note.objects.all().order_by('-upload_date')  # Show all notes for new users

    paginator = Paginator(notes, 16)  # Show 16 notes per page
    page_number = request.GET.get('page')
    notes = paginator.get_page(page_number)

    content = {
        'notes': notes,
        'faculties': faculties,
        'recommended_notes': recommended_notes_queryset,  # Pass the recommended notes QuerySet to the template
        'some_cutoff_date': some_cutoff_date,
    }
    return render(request, 'notes/notes.html', content)

# def notes_recommended(user):
#     # Get the notes downloaded by the user
#     user_downloads = NoteDownload.objects.filter(user=user).values_list('note', flat=True)

#     # Find the most downloaded notes by other users
#     recommended_notes = NoteDownload.objects.exclude(user=user).values('note').annotate(download_count=Count('note')).order_by('-download_count')[:5]  # Adjust the number as needed

#     # Get the corresponding Note objects
#     return Note.objects.filter(id__in=[note['note'] for note in recommended_notes])


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
    note = get_object_or_404(Note, author=request.user, id=note_id)
    user_info = get_object_or_404(UserInfo, author=request.user)

    #update the user info to remove the reference to the note being deleted
    if user_info.last_uploaded_note == note:
        user_info.last_uploaded_note = None
        user_info.save()

    #get the file path to delete
    file_path = note.file.path if note.file else None   

    #delete the note
    note.delete()
    user_info.notes_count -= 1
    user_info.recent_activity = f"Deleted note: '{note.title}' on {timezone.now().strftime('%Y-%m-%d')}"
    user_info.save()

    import os
    if file_path and os.path.isfile(file_path):
        os.remove(file_path)

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
        user_info.recent_activity = f'Downloaded note: "{note.title}" on {timezone.now().strftime("%Y-%m-%d")}' 
        user_info.save()  # Save changes


        NoteDownload.objects.create(user=request.user, note=note)

        note.downloads += 1
        note.save()

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

def feedback(request):
    if request.method == "POST":
        feedback = request.POST.get('feedback')
        suggestion = Feedback.objects.create(
            author = request.user,
            feedback = feedback,
        )

        messages.success(request, 'Feedback sent successfully.')

        return redirect('help_support')
    
def aboutus(request):
    return render(request, 'notes/aboutus.html')

def testimonial(request):
    testimonials = Feedback.objects.all()
    context = {
        'testimonials':testimonials,
    }
    return render(request, 'notes/testimonials.html', context)


def user_downloads(request):
    user_downloads = NoteDownload.objects.filter(user=request.user).order_by('-downloaded_at')
    context = {
        'downloads':user_downloads,
    }
    return render(request, 'notes/userDownloads.html', context)