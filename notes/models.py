from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    faculty = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    title = models.CharField(max_length=100, default="Title")
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='all_notes/', blank=True, null=True)

    def __str__(self):
        return self.subject
    
class UserInfo(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    notes_count = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    last_uploaded_note = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True)
    recent_activity = models.TextField(default="", blank=True)

    def __str__(self):
        return self.author.username
    

class Bio(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author.first_name}'s Bio"
    

class Feedback(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField()

    

